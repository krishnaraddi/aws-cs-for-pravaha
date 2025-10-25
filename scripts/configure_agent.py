import boto3
import json
import os

# SSM parameter paths
KB_PARAM = "/agentcore/knowledge-base/customer-support"
DS_PARAM = "/agentcore/data-source/customer-support"

# Output config path
CONFIG_DIR = "config"
CONFIG_FILE = "agent_config.json"

def get_ssm_parameter(name, region="us-east-1"):
    ssm = boto3.client("ssm", region_name=region)
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=False)
        return response["Parameter"]["Value"]
    except Exception as e:
        print(f"❌ Failed to retrieve {name}: {e}")
        return None

def write_config(kb_id, ds_id):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config = {
        "knowledge_base_id": kb_id,
        "data_source_id": ds_id,
        "region": "us-east-1"
    }
    with open(os.path.join(CONFIG_DIR, CONFIG_FILE), "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Agent config written to {CONFIG_DIR}/{CONFIG_FILE}")

def main():
    print("🔍 Retrieving KB and DS IDs from SSM...")
    kb_id = get_ssm_parameter(KB_PARAM)
    ds_id = get_ssm_parameter(DS_PARAM)

    if not kb_id or not ds_id:
        print("❌ Missing KB or DS ID. Aborting.")
        return

    print(f"📦 KB ID: {kb_id}")
    print(f"📦 DS ID: {ds_id}")
    write_config(kb_id, ds_id)

if __name__ == "__main__":
    main()