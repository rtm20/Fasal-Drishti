"""
FasalDrishti — Amazon CloudWatch Integration
=============================================
Structured logging + custom metrics for monitoring the app.

AWS Service: Amazon CloudWatch
- CloudWatch Logs: Structured JSON logs from FastAPI
- CloudWatch Metrics: Custom metrics (scan count, latency, errors, diseases detected)
- Namespace: FasalDrishti

Usage:
    from app.services.cloudwatch_service import cloudwatch_logger, publish_scan_metric

    cloudwatch_logger.log_scan(scan_id="abc", crop="tomato", disease="blight")
    await publish_scan_metric(crop="tomato", disease="early_blight", latency_ms=1200)
"""

import os
import json
import time
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.config import get_settings

logger = logging.getLogger("fasaldrishti.cloudwatch")

# ============================================================
# CONFIGURATION
# ============================================================
_settings = get_settings()
REGION = _settings.aws_region or "ap-south-1"
METRIC_NAMESPACE = "FasalDrishti"
LOG_GROUP = "/fasaldrishti/application"
ENVIRONMENT = _settings.app_env if hasattr(_settings, 'app_env') else "development"


def _get_cw_client():
    """Create CloudWatch client."""
    kwargs = {"region_name": REGION}
    if _settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = _settings.aws_access_key_id
    if _settings.aws_secret_access_key:
        kwargs["aws_secret_access_key"] = _settings.aws_secret_access_key
    return boto3.client("cloudwatch", **kwargs)


def _get_logs_client():
    """Create CloudWatch Logs client."""
    kwargs = {"region_name": REGION}
    if _settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = _settings.aws_access_key_id
    if _settings.aws_secret_access_key:
        kwargs["aws_secret_access_key"] = _settings.aws_secret_access_key
    return boto3.client("logs", **kwargs)


# ============================================================
# STRUCTURED LOGGING TO CLOUDWATCH LOGS
# ============================================================
class CloudWatchLogger:
    """
    Structured logger that sends JSON events to CloudWatch Logs.
    Falls back to local Python logging if CloudWatch is unavailable.
    """

    def __init__(self):
        self._client = None
        self._log_group = LOG_GROUP
        self._log_stream = None
        self._sequence_token = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy init — connect to CloudWatch Logs and create group/stream."""
        if self._initialized:
            return
        try:
            self._client = _get_logs_client()
            
            # Create log group if it doesn't exist
            try:
                self._client.create_log_group(logGroupName=self._log_group)
                logger.info(f"Created CloudWatch log group: {self._log_group}")
                
                # Set retention to 30 days
                self._client.put_retention_policy(
                    logGroupName=self._log_group,
                    retentionInDays=30,
                )
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
                    raise
            
            # Create a log stream for this instance
            today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
            instance_id = os.getenv("HOSTNAME", "local")[:12]
            self._log_stream = f"{today}/{instance_id}/{int(time.time())}"
            
            try:
                self._client.create_log_stream(
                    logGroupName=self._log_group,
                    logStreamName=self._log_stream,
                )
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
                    raise
            
            self._initialized = True
            logger.info(f"CloudWatch Logs connected: {self._log_group}/{self._log_stream}")
            
        except (NoCredentialsError, ClientError) as e:
            logger.warning(f"CloudWatch Logs unavailable, using local logging: {e}")
            self._initialized = False

    def _send_log_event(self, message: dict):
        """Send a structured log event to CloudWatch Logs."""
        self._ensure_initialized()
        
        # Always log locally
        log_str = json.dumps(message, default=str, ensure_ascii=False)
        logger.info(log_str)
        
        if not self._initialized or not self._client:
            return
        
        try:
            kwargs = {
                "logGroupName": self._log_group,
                "logStreamName": self._log_stream,
                "logEvents": [
                    {
                        "timestamp": int(time.time() * 1000),
                        "message": log_str,
                    }
                ],
            }
            if self._sequence_token:
                kwargs["sequenceToken"] = self._sequence_token
            
            response = self._client.put_log_events(**kwargs)
            self._sequence_token = response.get("nextSequenceToken")
            
        except ClientError as e:
            # If invalid sequence token, retry once
            if e.response["Error"]["Code"] == "InvalidSequenceTokenException":
                try:
                    token = e.response["Error"]["Message"].split(":")[-1].strip()
                    kwargs["sequenceToken"] = token
                    response = self._client.put_log_events(**kwargs)
                    self._sequence_token = response.get("nextSequenceToken")
                except Exception:
                    pass
            else:
                logger.debug(f"CloudWatch log send failed: {e}")

    # --- Convenience log methods ---
    
    def log_scan(
        self,
        scan_id: str,
        phone_number: str = "unknown",
        crop: str = "unknown",
        disease: str = "unknown",
        severity: str = "unknown",
        confidence: float = 0.0,
        analysis_method: str = "unknown",
        latency_ms: float = 0.0,
        language: str = "en",
    ):
        """Log a completed crop scan analysis."""
        self._send_log_event({
            "event": "SCAN_COMPLETED",
            "scan_id": scan_id,
            "phone_number": phone_number[-4:] if len(phone_number) > 4 else "****",
            "crop": crop,
            "disease": disease,
            "severity": severity,
            "confidence": round(confidence, 2),
            "analysis_method": analysis_method,
            "latency_ms": round(latency_ms, 1),
            "language": language,
            "environment": ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def log_error(
        self,
        error_type: str,
        message: str,
        scan_id: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        """Log an error event."""
        self._send_log_event({
            "event": "ERROR",
            "error_type": error_type,
            "message": message,
            "scan_id": scan_id,
            "details": details or {},
            "traceback": traceback.format_exc() if "NoneType" not in traceback.format_exc() else None,
            "environment": ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def log_whatsapp_message(
        self,
        phone_number: str,
        direction: str,  # "inbound" or "outbound"
        message_type: str,  # "text", "image", "voice"
        language: str = "en",
    ):
        """Log WhatsApp message flow."""
        self._send_log_event({
            "event": "WHATSAPP_MESSAGE",
            "phone_number": phone_number[-4:] if len(phone_number) > 4 else "****",
            "direction": direction,
            "message_type": message_type,
            "language": language,
            "environment": ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def log_service_health(self, service: str, status: str, latency_ms: float = 0):
        """Log a service health check result."""
        self._send_log_event({
            "event": "HEALTH_CHECK",
            "service": service,
            "status": status,
            "latency_ms": round(latency_ms, 1),
            "environment": ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def log_startup(self, services: dict):
        """Log application startup event with service status."""
        self._send_log_event({
            "event": "APP_STARTUP",
            "services": services,
            "environment": ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


# ============================================================
# CUSTOM CLOUDWATCH METRICS
# ============================================================
def publish_scan_metric(
    crop: str = "unknown",
    disease: str = "unknown",
    severity: str = "unknown",
    latency_ms: float = 0.0,
    analysis_method: str = "unknown",
    success: bool = True,
):
    """
    Publish custom metrics to CloudWatch for monitoring.
    
    Metrics published:
      - ScanCount (count of scans)
      - ScanLatency (analysis time in ms)
      - ScanErrors (error count, if success=False)
      - DiseaseDetections (count per disease)
    """
    try:
        cw = _get_cw_client()
        
        timestamp = datetime.now(timezone.utc)
        
        metric_data = [
            # Total scan count
            {
                "MetricName": "ScanCount",
                "Timestamp": timestamp,
                "Value": 1,
                "Unit": "Count",
                "Dimensions": [
                    {"Name": "Environment", "Value": ENVIRONMENT},
                    {"Name": "AnalysisMethod", "Value": analysis_method},
                ],
            },
            # Latency
            {
                "MetricName": "ScanLatency",
                "Timestamp": timestamp,
                "Value": latency_ms,
                "Unit": "Milliseconds",
                "Dimensions": [
                    {"Name": "Environment", "Value": ENVIRONMENT},
                    {"Name": "AnalysisMethod", "Value": analysis_method},
                ],
            },
        ]
        
        if success:
            # Disease detection metric
            metric_data.append({
                "MetricName": "DiseaseDetections",
                "Timestamp": timestamp,
                "Value": 1,
                "Unit": "Count",
                "Dimensions": [
                    {"Name": "Crop", "Value": crop},
                    {"Name": "Disease", "Value": disease},
                    {"Name": "Severity", "Value": severity},
                ],
            })
        else:
            # Error metric
            metric_data.append({
                "MetricName": "ScanErrors",
                "Timestamp": timestamp,
                "Value": 1,
                "Unit": "Count",
                "Dimensions": [
                    {"Name": "Environment", "Value": ENVIRONMENT},
                    {"Name": "AnalysisMethod", "Value": analysis_method},
                ],
            })
        
        cw.put_metric_data(
            Namespace=METRIC_NAMESPACE,
            MetricData=metric_data,
        )
        logger.debug(f"Published CloudWatch metrics for scan ({crop}/{disease})")
        
    except (NoCredentialsError, ClientError) as e:
        logger.debug(f"CloudWatch metrics unavailable: {e}")
    except Exception as e:
        logger.debug(f"CloudWatch metric publish failed: {e}")


def publish_whatsapp_metric(direction: str = "inbound", message_type: str = "text"):
    """Publish WhatsApp usage metric."""
    try:
        cw = _get_cw_client()
        cw.put_metric_data(
            Namespace=METRIC_NAMESPACE,
            MetricData=[
                {
                    "MetricName": "WhatsAppMessages",
                    "Timestamp": datetime.now(timezone.utc),
                    "Value": 1,
                    "Unit": "Count",
                    "Dimensions": [
                        {"Name": "Direction", "Value": direction},
                        {"Name": "MessageType", "Value": message_type},
                        {"Name": "Environment", "Value": ENVIRONMENT},
                    ],
                }
            ],
        )
    except Exception:
        pass


# ============================================================
# SERVICE STATUS
# ============================================================
def get_cloudwatch_status() -> dict:
    """Get CloudWatch service status."""
    status = {
        "service": "Amazon CloudWatch",
        "operational": False,
        "metrics_namespace": METRIC_NAMESPACE,
        "log_group": LOG_GROUP,
    }
    try:
        cw = _get_cw_client()
        # Quick check — list metrics in our namespace
        response = cw.list_metrics(
            Namespace=METRIC_NAMESPACE,
        )
        status["operational"] = True
        status["metric_count"] = len(response.get("Metrics", []))
    except Exception as e:
        status["error"] = str(e)
    
    return status


# ============================================================
# SINGLETON INSTANCE
# ============================================================
cloudwatch_logger = CloudWatchLogger()
