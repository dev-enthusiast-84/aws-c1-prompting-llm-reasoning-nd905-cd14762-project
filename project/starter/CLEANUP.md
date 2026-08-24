# Cleanup Guide - Remove All Resources

Complete guide to delete all Bedrock Knowledge Base and OpenSearch resources to avoid AWS charges.

---

## Quick Cleanup (Recommended)

Run the automated cleanup script:

```bash
chmod +x cleanup.sh
./cleanup.sh us-east-1
```

This will:
1. ✅ Empty S3 bucket (if created)
2. ✅ Delete Knowledge Base stack
3. ✅ Delete OpenSearch stack
4. ✅ Show final cost: $0

---

## Manual Cleanup (Step by Step)

### Step 1: Delete Knowledge Base Stack

```bash
# Delete the KB stack
aws cloudformation delete-stack \
  --stack-name support-chatbot-kb-stack \
  --region us-east-1

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name support-chatbot-kb-stack \
  --region us-east-1

echo "✅ KB stack deleted"
```

**Expected time:** 2-3 minutes

---

### Step 2: Delete OpenSearch Stack

```bash
# Delete the OpenSearch stack
aws cloudformation delete-stack \
  --stack-name support-chatbot-opensearch-stack \
  --region us-east-1

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name support-chatbot-opensearch-stack \
  --region us-east-1

echo "✅ OpenSearch stack deleted"
```

**Expected time:** 1-2 minutes

---

### Step 3: Verify Deletion

```bash
# Verify both stacks are deleted
aws cloudformation list-stacks \
  --stack-status-filter DELETE_COMPLETE \
  --query 'StackSummaries[?StackName==`support-chatbot-kb-stack` || StackName==`support-chatbot-opensearch-stack`]' \
  --region us-east-1

# Check S3 buckets
aws s3 ls | grep bedrock-kb-bucket || echo "No Bedrock S3 buckets found"
```

---

## Resource Deletion Order

**Important:** Always delete in this order:

1. **Knowledge Base Stack** (uses the collection)
   - Removes: KB, Data Source, IAM roles, S3 bucket
2. **OpenSearch Stack** (used by KB)
   - Removes: Collection, Network policy, Encryption policy

If you delete OpenSearch first, the KB stack deletion may fail.

---

## What Gets Deleted

### Knowledge Base Stack
- ✅ Bedrock Knowledge Base
- ✅ S3 bucket + all documents
- ✅ S3 bucket policy
- ✅ IAM role (BedrockKnowledgeBaseRole)
- ✅ Data Source configuration

### OpenSearch Stack
- ✅ OpenSearch Serverless Collection
- ✅ Network security policy
- ✅ Encryption security policy

### What's NOT Deleted
- ❌ CloudWatch logs (small cost, can delete manually)
- ❌ API call history (no charge)
- ❌ VPC endpoints (if created manually)

---

## Cost After Cleanup

| Service | Cost |
|---------|------|
| S3 bucket | $0 (deleted) |
| OpenSearch Serverless | $0 (deleted) |
| Bedrock KB | $0 (deleted) |
| IAM roles | $0 (no charge) |
| **Total** | **$0** |

---

## Troubleshooting Cleanup

### Stack Won't Delete

```bash
# Check for errors
aws cloudformation describe-stack-events \
  --stack-name support-chatbot-kb-stack \
  --query 'StackEvents[?ResourceStatus==`DELETE_FAILED`]' \
  --region us-east-1

# Common issue: S3 bucket not empty
# Solution: Empty it first
aws s3 rm s3://bedrock-kb-bucket-<account-id> --recursive --region us-east-1

# Then retry deletion
aws cloudformation delete-stack --stack-name support-chatbot-kb-stack --region us-east-1
```

### Stuck Collection

```bash
# List collections
aws opensearchserverless list-collections --region us-east-1

# If collection still exists after stack delete, delete manually
aws opensearchserverless delete-collection \
  --id <collection-id> \
  --region us-east-1
```

### Orphaned S3 Bucket

```bash
# List all Bedrock-related buckets
aws s3 ls | grep bedrock

# Force delete (WARNING: permanent!)
aws s3 rb s3://bedrock-kb-bucket-<account-id> --force --region us-east-1
```

---

## Backup Before Cleanup (Optional)

Save your documents before deleting:

```bash
# Download all documents
mkdir -p ./documents-backup
aws s3 sync s3://bedrock-kb-bucket-<account-id>/documents/ ./documents-backup/

# Save KB metadata
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id <KB-ID> \
  > kb-metadata.json

echo "✅ Backup complete in ./documents-backup/"
```

---

## Cleanup Automation

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
cleanup:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    - name: Run cleanup
      run: |
        chmod +x cleanup.sh
        ./cleanup.sh us-east-1
```

---

## Frequently Asked Questions

**Q: Will cleanup delete my documents?**  
A: Yes. Download them first if you need to keep them (see backup section above).

**Q: How long does cleanup take?**  
A: 3-5 minutes total. CloudFormation may take time to cascade deletions.

**Q: What if cleanup fails?**  
A: Check the troubleshooting section above, or manually delete stacks via AWS Console.

**Q: Can I keep OpenSearch and delete only the KB?**  
A: Yes! Just run `aws cloudformation delete-stack --stack-name support-chatbot-kb-stack`. OpenSearch can be reused.

**Q: How do I know everything is deleted?**  
A: Run `aws cloudformation list-stacks --region us-east-1` and verify both stacks show `DELETE_COMPLETE` status.

---

## Next Steps

After cleanup:
- ✅ Resources deleted
- ✅ No ongoing charges
- ✅ AWS account clean

To redeploy later, follow the deployment guide in `OPENSEARCH_SETUP.md`.
