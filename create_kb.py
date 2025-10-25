import boto3

bedrock = boto3.client("bedrock", region_name="us-east-1")

response = bedrock.create_knowledge_base(
    name="customer-support",
    description="bedrock-allow",
    roleArn="arn:aws:iam::552995353289:role/AmazonBedrockExecutionRoleForKnowledgeBase_b860",
    knowledgeBaseConfiguration={
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0",
            "s3BucketArn": "arn:aws:s3vectors:us-east-1:552995353289:bucket/customer-support-vectors-b860",
            "s3IndexId": "customer-support-index-b860"
        }
    }
)

print("✅ KB Created:", response["knowledgeBase"]["knowledgeBaseId"])