import streamlit as st
from launch_agent_runtime import query_agent
import json

# Load config
with open("config/agent_config.json") as f:
    config = json.load(f)

KB_ID = config["knowledge_base_id"]
REGION = config.get("region", "us-east-1")

st.set_page_config(page_title="Customer Support Assistant", layout="centered")

st.title("📦 Customer Support Assistant")
st.markdown("Ask me anything about your product, warranty, or troubleshooting.")

query = st.text_input("🔍 Your question:", placeholder="e.g., How do I reset my Elite headphones?")
submit = st.button("Ask")

if submit and query:
    with st.spinner("Thinking..."):
        results = query_agent(KB_ID, query, region=REGION)
        if results:
            top_answer = results[0]["content"]["text"]
            st.success(top_answer)
            with st.expander("📁 Source document"):
                source = results[0]["location"]["s3Location"]["uri"]
                st.write(source)
        else:
            st.warning("🤖 Sorry, I couldn't find an answer.")