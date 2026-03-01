"""
FasalDrishti - AWS Lambda Handler
==================================
Wraps the FastAPI application for deployment on AWS Lambda behind
Amazon API Gateway.

AWS Service: AWS Lambda + Amazon API Gateway
Why: Serverless compute — no servers to manage, pay only for what you use.
     API Gateway provides HTTPS endpoints, throttling, and request routing.
     Lambda scales automatically from 0 to thousands of concurrent requests.

How it works:
  1. API Gateway receives HTTP request (from WhatsApp webhook, web UI, etc.)
  2. API Gateway invokes this Lambda function with the request event
  3. Mangum adapter converts API Gateway event → ASGI request for FastAPI
  4. FastAPI processes the request (AI analysis, DynamoDB, etc.)
  5. Response flows back: FastAPI → Mangum → Lambda → API Gateway → Client

Deployment:
  sam build && sam deploy --guided
  OR
  Upload as a ZIP to Lambda console with handler = "lambda_handler.handler"

Environment Variables (set in SAM template or Lambda console):
  AWS_REGION, BEDROCK_MODEL_ID, S3_BUCKET_NAME,
  DYNAMODB_TABLE_USERS, DYNAMODB_TABLE_SCANS,
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
"""

from mangum import Mangum
from app.main import app

# Mangum wraps the FastAPI ASGI app for Lambda
# It translates between API Gateway events and ASGI
handler = Mangum(app, lifespan="off")
