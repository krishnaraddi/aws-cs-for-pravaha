import boto3
import json
import os

CONFIG_PATH = "config/agent_config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Missing config file: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def query_agent(kb_id, query, region="us-east-1"):
    bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=region)
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query}
        )
        return response.get("retrievalResults", [])
    except Exception as e:
        print(f"❌ Error querying agent: {e}")
        return []

def main():
    print("🚀 Launching agent runtime...")
    config = load_config()
    kb_id = config.get("knowledge_base_id")
    query = "Do refurbished products have the same warranty?"

    print(f"📡 Sending query to KB: {kb_id}")
    results = query_agent(kb_id, query)

    if not results:
        print("⚠️ No results returned.")
        return

    print("✅ Response:")
    for i, result in enumerate(results, 1):
        doc = result.get("content", {}).get("text", "")
        source = result.get("location", {}).get("s3Location", {}).get("uri", "")
        print(f"\n🔹 Result {i}:\n{doc}\n📁 Source: {source}")

if __name__ == "__main__":
    main()