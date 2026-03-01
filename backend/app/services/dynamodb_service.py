"""
FasalDrishti - Amazon DynamoDB Service
=======================================
Stores scan history and user session data in DynamoDB tables.

Tables:
  fasaldrishti-scans  — every crop scan (image analysis results)
  fasaldrishti-users  — user preferences (language, phone, scan count)

AWS Service: Amazon DynamoDB
Why: Serverless NoSQL database that scales automatically. Perfect for
     storing scan records with variable schemas and providing fast
     lookups by phone number or scan ID. Zero server management.

How it works:
  1. On first WhatsApp message → create/update user record
  2. On every scan → store analysis result with scan_id as primary key
  3. Dashboard reads aggregated stats from scan table
  4. Tables are auto-created if they don't exist (for hackathon ease)
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("fasaldrishti.dynamodb")
settings = get_settings()

_dynamodb_resource = None
_dynamodb_client = None


def _get_dynamodb_resource():
    """Get or create a cached boto3 DynamoDB resource."""
    global _dynamodb_resource
    if _dynamodb_resource is None:
        try:
            import boto3
            kwargs = {"region_name": settings.aws_region}
            if settings.aws_access_key_id:
                kwargs["aws_access_key_id"] = settings.aws_access_key_id
            if settings.aws_secret_access_key:
                kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            _dynamodb_resource = boto3.resource("dynamodb", **kwargs)
        except Exception as e:
            logger.warning(f"Could not create DynamoDB resource: {e}")
    return _dynamodb_resource


def _get_dynamodb_client():
    """Get or create a cached boto3 DynamoDB client."""
    global _dynamodb_client
    if _dynamodb_client is None:
        try:
            import boto3
            kwargs = {"region_name": settings.aws_region}
            if settings.aws_access_key_id:
                kwargs["aws_access_key_id"] = settings.aws_access_key_id
            if settings.aws_secret_access_key:
                kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            _dynamodb_client = boto3.client("dynamodb", **kwargs)
        except Exception as e:
            logger.warning(f"Could not create DynamoDB client: {e}")
    return _dynamodb_client


# ============================================================
# TABLE CREATION (auto-create for hackathon)
# ============================================================

def ensure_tables_exist():
    """
    Create DynamoDB tables if they don't already exist.
    Called once at application startup.
    
    Table: fasaldrishti-scans
      PK: scan_id (String)
      GSI: phone-index on phone_number + timestamp
    
    Table: fasaldrishti-users
      PK: phone_number (String)
    """
    client = _get_dynamodb_client()
    if not client:
        logger.warning("DynamoDB client unavailable — skipping table creation")
        return False

    existing = []
    try:
        existing = client.list_tables()["TableNames"]
    except Exception as e:
        logger.error(f"Cannot list DynamoDB tables: {e}")
        return False

    created = []

    # --- Scans table ---
    scans_table = settings.dynamodb_table_scans
    if scans_table not in existing:
        try:
            client.create_table(
                TableName=scans_table,
                KeySchema=[
                    {"AttributeName": "scan_id", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "scan_id", "AttributeType": "S"},
                    {"AttributeName": "phone_number", "AttributeType": "S"},
                    {"AttributeName": "timestamp", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "phone-index",
                        "KeySchema": [
                            {"AttributeName": "phone_number", "KeyType": "HASH"},
                            {"AttributeName": "timestamp", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {
                            "ReadCapacityUnits": 5,
                            "WriteCapacityUnits": 5,
                        },
                    }
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            )
            logger.info(f"Created DynamoDB table: {scans_table}")
            created.append(scans_table)
        except client.exceptions.ResourceInUseException:
            logger.info(f"Table {scans_table} already exists (race condition)")
        except Exception as e:
            logger.error(f"Failed to create {scans_table}: {e}")

    # --- Users table ---
    users_table = settings.dynamodb_table_users
    if users_table not in existing:
        try:
            client.create_table(
                TableName=users_table,
                KeySchema=[
                    {"AttributeName": "phone_number", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "phone_number", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            )
            logger.info(f"Created DynamoDB table: {users_table}")
            created.append(users_table)
        except client.exceptions.ResourceInUseException:
            logger.info(f"Table {users_table} already exists (race condition)")
        except Exception as e:
            logger.error(f"Failed to create {users_table}: {e}")

    # Wait for tables to become active
    if created:
        try:
            for table_name in created:
                waiter = client.get_waiter("table_exists")
                waiter.wait(
                    TableName=table_name,
                    WaiterConfig={"Delay": 2, "MaxAttempts": 30},
                )
                logger.info(f"Table {table_name} is now ACTIVE")
        except Exception as e:
            logger.warning(f"Waiter error (tables may still be creating): {e}")

    return True


# ============================================================
# SCAN OPERATIONS
# ============================================================

def _convert_floats(obj):
    """Convert floats to Decimal for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(round(obj, 6)))
    elif isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_floats(i) for i in obj]
    return obj


async def save_scan(
    scan_id: str,
    phone_number: str,
    analysis_result: dict,
) -> bool:
    """
    Save a scan record to DynamoDB fasaldrishti-scans table.
    
    Item schema:
      scan_id (PK)     — unique scan identifier
      phone_number     — user's WhatsApp number (GSI hash key)
      timestamp        — ISO 8601 UTC (GSI range key)
      crop             — detected crop name
      disease_key      — disease identifier
      disease_name     — human-readable disease name
      severity         — none/mild/moderate/severe
      confidence       — AI confidence score (0-100)
      analysis_engine  — bedrock/rekognition/fallback_demo
      language         — user's language preference
      full_result      — complete analysis result JSON
      ttl              — auto-expire after 90 days (optional)
    """
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return False

        table = dynamo.Table(settings.dynamodb_table_scans)
        
        analysis = analysis_result.get("analysis", {})
        metadata = analysis_result.get("metadata", {})
        
        now = datetime.now(timezone.utc)
        
        item = {
            "scan_id": scan_id,
            "phone_number": phone_number or "web",
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "crop": analysis.get("crop", "unknown"),
            "disease_key": analysis.get("disease_key", "unknown"),
            "disease_name": analysis.get("disease_name", "Unknown"),
            "severity": analysis.get("severity", "unknown"),
            "confidence": int(analysis.get("confidence", 0)),
            "is_healthy": analysis.get("is_healthy", False),
            "analysis_engine": metadata.get("analysis_engine", "unknown"),
            "pipeline_latency_ms": int(metadata.get("pipeline_latency_ms", 0)),
            "full_result": _convert_floats(analysis_result),
            # TTL: auto-delete after 90 days (DynamoDB TTL feature)
            "ttl": int(time.time()) + (90 * 24 * 60 * 60),
        }
        
        table.put_item(Item=item)
        logger.info(f"Scan {scan_id} saved to DynamoDB")
        return True
        
    except Exception as e:
        logger.warning(f"DynamoDB save_scan failed (non-blocking): {e}")
        return False


async def get_scan(scan_id: str) -> Optional[dict]:
    """Retrieve a single scan by scan_id."""
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return None

        table = dynamo.Table(settings.dynamodb_table_scans)
        response = table.get_item(Key={"scan_id": scan_id})
        item = response.get("Item")
        if item:
            # Convert Decimals back to floats for JSON serialization
            return _decimal_to_float(item)
        return None
    except Exception as e:
        logger.warning(f"DynamoDB get_scan failed: {e}")
        return None


async def get_scans_by_phone(phone_number: str, limit: int = 20) -> list:
    """Get recent scans for a phone number using the GSI."""
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return []

        table = dynamo.Table(settings.dynamodb_table_scans)
        from boto3.dynamodb.conditions import Key
        
        response = table.query(
            IndexName="phone-index",
            KeyConditionExpression=Key("phone_number").eq(phone_number),
            ScanIndexForward=False,  # newest first
            Limit=limit,
        )
        items = response.get("Items", [])
        return [_decimal_to_float(item) for item in items]
    except Exception as e:
        logger.warning(f"DynamoDB get_scans_by_phone failed: {e}")
        return []


async def get_recent_scans(limit: int = 50) -> list:
    """Get most recent scans across all users (table scan — use sparingly)."""
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return []

        table = dynamo.Table(settings.dynamodb_table_scans)
        response = table.scan(Limit=limit)
        items = response.get("Items", [])
        # Sort by timestamp descending
        items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return [_decimal_to_float(item) for item in items[:limit]]
    except Exception as e:
        logger.warning(f"DynamoDB get_recent_scans failed: {e}")
        return []


async def get_scan_stats() -> dict:
    """Get aggregate stats from the scans table for the dashboard."""
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return _empty_stats()

        table = dynamo.Table(settings.dynamodb_table_scans)
        
        # Scan the full table (fine for hackathon scale)
        response = table.scan()
        items = response.get("Items", [])
        
        # Handle pagination
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
        
        if not items:
            return _empty_stats()

        total = len(items)
        from collections import Counter
        
        disease_counter = Counter(
            item["disease_name"] for item in items 
            if item.get("disease_key") != "healthy"
        )
        crop_counter = Counter(item.get("crop", "unknown") for item in items)
        severity_counter = Counter(item.get("severity", "unknown") for item in items)
        engine_counter = Counter(item.get("analysis_engine", "unknown") for item in items)
        
        confidences = [
            float(item.get("confidence", 0)) for item in items 
            if item.get("confidence")
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Recent scans (sorted by timestamp)
        items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "total_scans": total,
            "diseases_detected": len(disease_counter),
            "crops_analyzed": len(crop_counter),
            "average_confidence": round(avg_confidence, 1),
            "top_diseases": [
                {"name": name, "count": count}
                for name, count in disease_counter.most_common(5)
            ],
            "severity_distribution": {
                "none": severity_counter.get("none", 0),
                "mild": severity_counter.get("mild", 0),
                "moderate": severity_counter.get("moderate", 0),
                "severe": severity_counter.get("severe", 0),
            },
            "crop_distribution": dict(crop_counter),
            "engine_distribution": dict(engine_counter),
            "recent_scans": [
                _decimal_to_float(item) for item in items[:10]
            ],
        }
    except Exception as e:
        logger.warning(f"DynamoDB get_scan_stats failed: {e}")
        return _empty_stats()


def _empty_stats() -> dict:
    return {
        "total_scans": 0,
        "diseases_detected": 0,
        "crops_analyzed": 0,
        "average_confidence": 0,
        "top_diseases": [],
        "severity_distribution": {"none": 0, "mild": 0, "moderate": 0, "severe": 0},
        "crop_distribution": {},
        "engine_distribution": {},
        "recent_scans": [],
    }


# ============================================================
# USER OPERATIONS
# ============================================================

async def save_user(
    phone_number: str,
    language: str = "en",
    name: str = "",
) -> bool:
    """
    Create or update a user record in DynamoDB.
    Uses phone_number as the primary key.
    Tracks: language preference, scan count, first/last seen timestamps.
    """
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return False

        table = dynamo.Table(settings.dynamodb_table_users)
        now = datetime.now(timezone.utc).isoformat()
        
        # Use update_item for upsert behavior
        table.update_item(
            Key={"phone_number": phone_number},
            UpdateExpression=(
                "SET #lang = :lang, "
                "last_seen = :now, "
                "updated_at = :now, "
                "scan_count = if_not_exists(scan_count, :zero) + :zero, "
                "created_at = if_not_exists(created_at, :now)"
            ),
            ExpressionAttributeNames={"#lang": "language"},
            ExpressionAttributeValues={
                ":lang": language,
                ":now": now,
                ":zero": 0,
            },
        )
        logger.info(f"User {phone_number} saved/updated in DynamoDB")
        return True
    except Exception as e:
        logger.warning(f"DynamoDB save_user failed: {e}")
        return False


async def increment_user_scan_count(phone_number: str) -> bool:
    """Increment the scan_count for a user after each analysis."""
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return False

        table = dynamo.Table(settings.dynamodb_table_users)
        now = datetime.now(timezone.utc).isoformat()
        
        table.update_item(
            Key={"phone_number": phone_number},
            UpdateExpression=(
                "SET scan_count = if_not_exists(scan_count, :zero) + :one, "
                "last_scan_at = :now"
            ),
            ExpressionAttributeValues={
                ":zero": 0,
                ":one": 1,
                ":now": now,
            },
        )
        return True
    except Exception as e:
        logger.warning(f"DynamoDB increment scan count failed: {e}")
        return False


async def get_user(phone_number: str) -> Optional[dict]:
    """Get user record by phone number."""
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return None

        table = dynamo.Table(settings.dynamodb_table_users)
        response = table.get_item(Key={"phone_number": phone_number})
        item = response.get("Item")
        return _decimal_to_float(item) if item else None
    except Exception as e:
        logger.warning(f"DynamoDB get_user failed: {e}")
        return None


async def get_user_language(phone_number: str) -> Optional[str]:
    """Get just the language preference for a user."""
    user = await get_user(phone_number)
    return user.get("language") if user else None


async def get_all_users(limit: int = 100) -> list:
    """Get all users (for admin dashboard)."""
    try:
        dynamo = _get_dynamodb_resource()
        if not dynamo:
            return []

        table = dynamo.Table(settings.dynamodb_table_users)
        response = table.scan(Limit=limit)
        items = response.get("Items", [])
        return [_decimal_to_float(item) for item in items]
    except Exception as e:
        logger.warning(f"DynamoDB get_all_users failed: {e}")
        return []


# ============================================================
# UTILITY
# ============================================================

def _decimal_to_float(obj):
    """Convert Decimal values back to int/float for JSON serialization."""
    if isinstance(obj, Decimal):
        if obj == int(obj):
            return int(obj)
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_decimal_to_float(i) for i in obj]
    return obj


def get_dynamodb_status() -> dict:
    """Check DynamoDB connectivity for health endpoint."""
    client = _get_dynamodb_client()
    if not client:
        return {"available": False, "error": "Client not created"}
    try:
        tables = client.list_tables()["TableNames"]
        scans_exists = settings.dynamodb_table_scans in tables
        users_exists = settings.dynamodb_table_users in tables
        return {
            "available": True,
            "tables": {
                settings.dynamodb_table_scans: "active" if scans_exists else "missing",
                settings.dynamodb_table_users: "active" if users_exists else "missing",
            },
        }
    except Exception as e:
        return {"available": False, "error": str(e)}
