"""
FasalDrishti - AWS Infrastructure Setup Script
================================================
Creates all required AWS resources for the project:
  1. S3 bucket for image and voice storage
  2. DynamoDB tables for scans and users
  3. Tests connectivity to Bedrock, Rekognition, Translate, Polly

Run this once after configuring your .env with AWS credentials:
  cd backend
  python -m scripts.setup_aws

AWS Services Created:
  - Amazon S3: fasaldrishti-images bucket
  - Amazon DynamoDB: fasaldrishti-scans + fasaldrishti-users tables
  
AWS Services Tested:
  - Amazon Bedrock (Claude 3.5 Sonnet v2)
  - Amazon Rekognition
  - Amazon Translate  
  - Amazon Polly
  - Amazon S3
  - Amazon DynamoDB
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
import json
from dotenv import load_dotenv

# Load environment
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env")
if not os.path.exists(env_path):
    # Fallback: try parent directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path)

REGION = os.getenv("AWS_REGION", "ap-south-1")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "fasaldrishti-images")
SCANS_TABLE = os.getenv("DYNAMODB_TABLE_SCANS", "fasaldrishti-scans")
USERS_TABLE = os.getenv("DYNAMODB_TABLE_USERS", "fasaldrishti-users")


def get_client(service):
    kwargs = {"region_name": REGION}
    if ACCESS_KEY:
        kwargs["aws_access_key_id"] = ACCESS_KEY
    if SECRET_KEY:
        kwargs["aws_secret_access_key"] = SECRET_KEY
    return boto3.client(service, **kwargs)


def get_resource(service):
    kwargs = {"region_name": REGION}
    if ACCESS_KEY:
        kwargs["aws_access_key_id"] = ACCESS_KEY
    if SECRET_KEY:
        kwargs["aws_secret_access_key"] = SECRET_KEY
    return boto3.resource(service, **kwargs)


def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def success(msg):
    print(f"  ✅ {msg}")


def fail(msg):
    print(f"  ❌ {msg}")


def info(msg):
    print(f"  ℹ️  {msg}")


# ============================================================
# 1. S3 BUCKET SETUP
# ============================================================
def setup_s3():
    separator("1. Amazon S3 — Image & Voice Storage")
    s3 = get_client("s3")
    
    try:
        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=S3_BUCKET)
            success(f"Bucket '{S3_BUCKET}' already exists")
            return True
        except s3.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                info(f"Bucket '{S3_BUCKET}' not found — creating...")
            elif error_code == "403":
                fail(f"Bucket '{S3_BUCKET}' exists but access denied")
                return False
        
        # Create bucket
        if REGION == "us-east-1":
            s3.create_bucket(Bucket=S3_BUCKET)
        else:
            s3.create_bucket(
                Bucket=S3_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": REGION},
            )
        success(f"Created S3 bucket: {S3_BUCKET}")
        
        # Configure CORS for web uploads
        s3.put_bucket_cors(
            Bucket=S3_BUCKET,
            CORSConfiguration={
                "CORSRules": [
                    {
                        "AllowedHeaders": ["*"],
                        "AllowedMethods": ["GET", "PUT", "POST"],
                        "AllowedOrigins": ["*"],
                        "MaxAgeSeconds": 3600,
                    }
                ]
            },
        )
        success("CORS configured for web access")
        
        # Set lifecycle rule (auto-delete after 90 days)
        s3.put_bucket_lifecycle_configuration(
            Bucket=S3_BUCKET,
            LifecycleConfiguration={
                "Rules": [
                    {
                        "ID": "AutoDeleteOldScans",
                        "Status": "Enabled",
                        "Filter": {"Prefix": "scans/"},
                        "Expiration": {"Days": 90},
                    },
                    {
                        "ID": "AutoDeleteOldVoice",
                        "Status": "Enabled",
                        "Filter": {"Prefix": "voice/"},
                        "Expiration": {"Days": 30},
                    },
                ]
            },
        )
        success("Lifecycle rules set (scans: 90 days, voice: 30 days)")
        
        return True
    except Exception as e:
        fail(f"S3 setup failed: {e}")
        return False


# ============================================================
# 2. DYNAMODB TABLE SETUP
# ============================================================
def setup_dynamodb():
    separator("2. Amazon DynamoDB — Data Storage")
    client = get_client("dynamodb")
    
    existing = []
    try:
        existing = client.list_tables()["TableNames"]
    except Exception as e:
        fail(f"Cannot list tables: {e}")
        return False
    
    results = {}
    
    # --- Scans Table ---
    if SCANS_TABLE in existing:
        success(f"Table '{SCANS_TABLE}' already exists")
        results["scans"] = True
    else:
        try:
            client.create_table(
                TableName=SCANS_TABLE,
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
            # Wait for table
            waiter = client.get_waiter("table_exists")
            waiter.wait(TableName=SCANS_TABLE, WaiterConfig={"Delay": 2, "MaxAttempts": 30})
            
            # Enable TTL
            client.update_time_to_live(
                TableName=SCANS_TABLE,
                TimeToLiveSpecification={
                    "Enabled": True,
                    "AttributeName": "ttl",
                },
            )
            success(f"Created table '{SCANS_TABLE}' with GSI + TTL")
            results["scans"] = True
        except Exception as e:
            fail(f"Failed to create {SCANS_TABLE}: {e}")
            results["scans"] = False
    
    # --- Users Table ---
    if USERS_TABLE in existing:
        success(f"Table '{USERS_TABLE}' already exists")
        results["users"] = True
    else:
        try:
            client.create_table(
                TableName=USERS_TABLE,
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
            waiter = client.get_waiter("table_exists")
            waiter.wait(TableName=USERS_TABLE, WaiterConfig={"Delay": 2, "MaxAttempts": 30})
            success(f"Created table '{USERS_TABLE}'")
            results["users"] = True
        except Exception as e:
            fail(f"Failed to create {USERS_TABLE}: {e}")
            results["users"] = False
    
    return all(results.values())


# ============================================================
# 3. TEST ALL AWS SERVICES
# ============================================================
def test_bedrock():
    separator("3. Amazon Bedrock — AI Analysis Engine")
    try:
        client = get_client("bedrock-runtime")
        model_id = os.getenv("BEDROCK_MODEL_ID", "apac.anthropic.claude-3-5-sonnet-20241022-v2:0")
        
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "messages": [{"role": "user", "content": "Say 'Namaste farmer' in Hindi"}],
            }),
        )
        result = json.loads(response["body"].read())
        text = result["content"][0]["text"]
        success(f"Bedrock working! Response: {text[:80]}")
        return True
    except Exception as e:
        fail(f"Bedrock: {e}")
        info("If INVALID_PAYMENT_INSTRUMENT — Visa card still verifying")
        return False


def test_rekognition():
    separator("4. Amazon Rekognition — Image Label Detection")
    try:
        client = get_client("rekognition")
        
        # Generate a minimal valid JPEG in-memory using Pillow if available, else raw bytes
        try:
            from PIL import Image as PILImage
            from io import BytesIO
            img = PILImage.new("RGB", (10, 10), color=(0, 128, 0))  # green pixel
            buf = BytesIO()
            img.save(buf, format="JPEG")
            test_jpg = buf.getvalue()
        except ImportError:
            # Minimal valid JPEG bytes (hand-crafted smallest valid JPEG)
            import struct
            # Use a simpler approach: just send some bytes and catch InvalidImageFormatException
            test_jpg = bytes([
                0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
                0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
                0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
                0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
                0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
                0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
                0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
                0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
                0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
                0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
                0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
                0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0x7B, 0x40,
                0xFF, 0xD9
            ])
        
        response = client.detect_labels(
            Image={"Bytes": test_jpg},
            MaxLabels=5,
            MinConfidence=10.0,
        )
        labels = [l["Name"] for l in response.get("Labels", [])]
        success(f"Rekognition working! Labels: {labels}")
        return True
    except Exception as e:
        err_str = str(e)
        if "InvalidImageFormatException" in err_str:
            # Service is reachable — the test image just wasn't valid enough
            success("Rekognition reachable! (test image format not ideal, but API connected)")
            return True
        fail(f"Rekognition: {e}")
        return False


def test_translate():
    separator("5. Amazon Translate — Multilingual Support")
    try:
        client = get_client("translate")
        
        response = client.translate_text(
            Text="Your tomato crop has early blight disease. Apply fungicide immediately.",
            SourceLanguageCode="en",
            TargetLanguageCode="hi",
        )
        translated = response["TranslatedText"]
        success(f"Translate working! Hindi: {translated[:80]}")
        return True
    except Exception as e:
        fail(f"Translate: {e}")
        return False


def test_polly():
    separator("6. Amazon Polly — Voice Advisory Generation")
    try:
        client = get_client("polly")
        
        response = client.synthesize_speech(
            Text="नमस्ते किसान भाई। आपकी फसल स्वस्थ है।",
            OutputFormat="mp3",
            VoiceId="Kajal",
            LanguageCode="hi-IN",
            Engine="neural",
        )
        
        audio_bytes = response["AudioStream"].read()
        success(f"Polly working! Generated {len(audio_bytes)} bytes of Hindi audio")
        
        # Save test audio file
        test_path = os.path.join(os.path.dirname(__file__), "test_polly_output.mp3")
        with open(test_path, "wb") as f:
            f.write(audio_bytes)
        info(f"Test audio saved: {test_path}")
        return True
    except Exception as e:
        fail(f"Polly: {e}")
        return False


def test_s3():
    separator("7. Amazon S3 — Storage Test")
    try:
        s3 = get_client("s3")
        
        # Write a test file
        test_key = "test/health-check.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=test_key,
            Body=json.dumps({"status": "ok", "service": "FasalDrishti"}),
            ContentType="application/json",
        )
        success(f"S3 write test passed: s3://{S3_BUCKET}/{test_key}")
        
        # Read it back
        response = s3.get_object(Bucket=S3_BUCKET, Key=test_key)
        data = json.loads(response["Body"].read())
        success(f"S3 read test passed: {data}")
        
        # Clean up
        s3.delete_object(Bucket=S3_BUCKET, Key=test_key)
        success("S3 cleanup done")
        return True
    except Exception as e:
        fail(f"S3: {e}")
        return False


def test_dynamodb():
    separator("8. Amazon DynamoDB — Database Test")
    try:
        dynamo = get_resource("dynamodb")
        
        # Test scans table
        scans = dynamo.Table(SCANS_TABLE)
        scans.put_item(Item={
            "scan_id": "test-setup-001",
            "phone_number": "test",
            "timestamp": "2026-01-01T00:00:00Z",
            "crop": "tomato",
            "disease_key": "healthy",
            "disease_name": "Healthy Plant",
            "severity": "none",
            "confidence": 95,
        })
        success(f"DynamoDB write test passed: {SCANS_TABLE}")
        
        # Read it back
        response = scans.get_item(Key={"scan_id": "test-setup-001"})
        item = response.get("Item")
        success(f"DynamoDB read test passed: {item.get('crop')}/{item.get('disease_name')}")
        
        # Clean up
        scans.delete_item(Key={"scan_id": "test-setup-001"})
        success("DynamoDB cleanup done")
        return True
    except Exception as e:
        fail(f"DynamoDB: {e}")
        return False


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "🌱" * 30)
    print("  FasalDrishti — AWS Infrastructure Setup")
    print("🌱" * 30)
    print(f"\n  Region: {REGION}")
    print(f"  Bucket: {S3_BUCKET}")
    print(f"  Tables: {SCANS_TABLE}, {USERS_TABLE}")
    print(f"  Access Key: {ACCESS_KEY[:8]}..." if ACCESS_KEY else "  Access Key: NOT SET")
    
    results = {}
    
    # Setup
    results["s3"] = setup_s3()
    results["dynamodb"] = setup_dynamodb()
    
    # Test all services
    results["bedrock"] = test_bedrock()
    results["rekognition"] = test_rekognition()
    results["translate"] = test_translate()
    results["polly"] = test_polly()
    results["s3_test"] = test_s3()
    results["dynamodb_test"] = test_dynamodb()
    
    # Summary
    separator("SUMMARY")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for service, ok in results.items():
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}  {service}")
    
    print(f"\n  Result: {passed}/{total} services operational")
    
    if passed == total:
        print("\n  🎉 All AWS services are ready! FasalDrishti is fully operational.")
    elif passed >= 6:
        print("\n  ⚠️  Most services working. Check failed items above.")
    else:
        print("\n  🚨 Multiple services failing. Check AWS credentials and permissions.")
    
    print()
    return 0 if passed >= 6 else 1


if __name__ == "__main__":
    sys.exit(main())
