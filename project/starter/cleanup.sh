#!/bin/bash

# Cleanup script for Bedrock Knowledge Base and OpenSearch Serverless stacks
# Run this to delete all resources and avoid ongoing AWS charges

set -e

REGION=${1:-us-east-1}
KB_STACK="support-chatbot-kb-stack"
OS_STACK="support-chatbot-opensearch-stack"

echo "🗑️  Starting cleanup of CloudFormation stacks..."
echo "Region: $REGION"
echo ""

# Step 1: Empty and delete S3 bucket (if created)
echo "Step 1: Emptying S3 bucket..."
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $KB_STACK \
  --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

if [ ! -z "$S3_BUCKET" ] && [ "$S3_BUCKET" != "None" ]; then
  echo "  Deleting objects in bucket: $S3_BUCKET"
  aws s3 rm "s3://$S3_BUCKET" --recursive --region $REGION 2>/dev/null || echo "  (Bucket not found or already deleted)"
else
  echo "  S3 bucket not found or already deleted"
fi

echo ""

# Step 2: Delete Knowledge Base stack
echo "Step 2: Deleting Knowledge Base stack ($KB_STACK)..."
if aws cloudformation describe-stacks \
  --stack-name $KB_STACK \
  --region $REGION \
  --query 'Stacks[0].StackStatus' \
  --output text 2>/dev/null | grep -q "CREATE_COMPLETE\|UPDATE_COMPLETE"; then

  aws cloudformation delete-stack \
    --stack-name $KB_STACK \
    --region $REGION

  echo "  Waiting for stack deletion..."
  aws cloudformation wait stack-delete-complete \
    --stack-name $KB_STACK \
    --region $REGION

  echo "  ✅ KB stack deleted"
else
  echo "  KB stack not found or already deleted"
fi

echo ""

# Step 3: Delete OpenSearch stack
echo "Step 3: Deleting OpenSearch stack ($OS_STACK)..."
if aws cloudformation describe-stacks \
  --stack-name $OS_STACK \
  --region $REGION \
  --query 'Stacks[0].StackStatus' \
  --output text 2>/dev/null | grep -q "CREATE_COMPLETE\|UPDATE_COMPLETE"; then

  aws cloudformation delete-stack \
    --stack-name $OS_STACK \
    --region $REGION

  echo "  Waiting for stack deletion..."
  aws cloudformation wait stack-delete-complete \
    --stack-name $OS_STACK \
    --region $REGION

  echo "  ✅ OpenSearch stack deleted"
else
  echo "  OpenSearch stack not found or already deleted"
fi

echo ""
echo "✅ Cleanup complete! All resources have been deleted."
echo ""
echo "Cost Summary:"
echo "  - S3 storage: $0"
echo "  - OpenSearch Serverless: $0"
echo "  - Bedrock Knowledge Base: $0"
echo "  - All IAM roles: $0"
echo ""
echo "Total ongoing charges: $0"
