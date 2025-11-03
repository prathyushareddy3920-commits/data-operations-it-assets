from datetime import datetime
from elasticsearch import Elasticsearch
 
# === CONFIGURATION ===
ES_ENDPOINT = "https://my-elasticsearch-project-a42a97.es.us-central1.gcp.elastic.cloud:443"
ES_API_KEY = "ay1OcVJab0I3OVh1cUlFeGM3VEQ6YkZ1amNoZ0FwM0dhQ0pxcnNDLW1Wdw=="
SOURCE_INDEX = "it_asset2"
TARGET_INDEX = "it_assets5_transformed"
 
# === CONNECT TO ELASTIC ===
es = Elasticsearch(
    ES_ENDPOINT,
    api_key=ES_API_KEY,
    verify_certs=True
)
 
# === CHECK CONNECTION ===
if not es.ping():
    print("❌ Connection failed! Please check endpoint or API key.")
    exit()
else:
    print("✅ Connected to Elasticsearch!")
 
# === 1️⃣ DELETE AND RECREATE TARGET INDEX ===
try:
    es.indices.delete(index=TARGET_INDEX)
    print(f"🗑️ Deleted existing index '{TARGET_INDEX}'")
except:
    print(f"ℹ️ Index '{TARGET_INDEX}' doesn't exist, creating new one")
 
# === 2️⃣ REINDEX DATA TO ANOTHER INDEX ===
print("📦 Reindexing data ...")
 
# Check source data first
source_count = es.count(index=SOURCE_INDEX)["count"]
print(f"   Source index '{SOURCE_INDEX}' has {source_count} records")
 
reindex_body = {
    "source": {"index": SOURCE_INDEX},
    "dest": {"index": TARGET_INDEX}
}
 
reindex_result = es.reindex(body=reindex_body, wait_for_completion=True)
print(f"✅ Reindex completed. Copied: {reindex_result.get('total', 0)} records")
 
# Force refresh and wait a moment
es.indices.refresh(index=TARGET_INDEX)
import time
time.sleep(2)
 
# Verify target data
target_count = es.count(index=TARGET_INDEX)["count"]
print(f"   Target index '{TARGET_INDEX}' now has {target_count} records")
 
# === 3️⃣ ADD DERIVED FIELDS (risk_level + system_age_years) ===
# Painless script to calculate risk_level and system_age_years
update_script = """
// Add risk_level based on lifecycle status
if (ctx._source.containsKey('operating_system_lifecycle_status')) {
    def status = ctx._source.operating_system_lifecycle_status.toLowerCase();
    if (status == 'eol' || status == 'eos') {
        ctx._source.risk_level = 'High';
    } else {
        ctx._source.risk_level = 'Low';
    }
}
 
// Add system_age_years based on installation date
if (ctx._source.containsKey('operating_system_installation_date')) {
    try {
        def date_str = ctx._source.operating_system_installation_date;
        if (date_str != null && date_str.length() >= 4) {
            def install_year = Integer.parseInt(date_str.substring(0, 4));
            def current_year = 2025;
            ctx._source.system_age_years = current_year - install_year;
        }
    } catch (Exception e) {
        // ignore invalid dates
    }
}
"""
 
print("⚙️  Adding derived fields (risk_level, system_age_years) ...")
update_query = {
    "script": {"source": update_script, "lang": "painless"},
    "query": {"match_all": {}}
}
 
es.update_by_query(index=TARGET_INDEX, body=update_query, refresh=True)
print("✅ Added derived fields successfully!")
 
# === 4️⃣ DELETE RECORDS WITH UNKNOWN HOSTNAMES ONLY ===
print("🧹 Deleting records with Unknown hostnames only...")
 
# First, let's check what we have before deleting
count_before = es.count(index=TARGET_INDEX)["count"]
print(f"   Records before deletion: {count_before}")
 
# Delete records where hostname equals "Unknown" 
delete_query = {
    "query": {
        "term": {"hostname.keyword": "unknown"}
    }
}
 
result = es.delete_by_query(index=TARGET_INDEX, body=delete_query, refresh=True)
print(f"✅ Deleted {result['deleted']} records with Unknown hostnames")
print("ℹ️ Keeping records with Unknown providers (as requested)")
 
# === 5️⃣ FINAL UPDATE CONFIRMATION ===
count = es.count(index=TARGET_INDEX)["count"]
print(f"📊 Transformation complete! Final record count in '{TARGET_INDEX}': {count}")
 
# === SHOW SAMPLE RECORD ===
sample = es.search(index=TARGET_INDEX, body={"size": 1})
if sample['hits']['hits']:
    record = sample['hits']['hits'][0]['_source']
    print(f"\n📋 Sample transformed record:")
    print(f"   • Hostname: {record.get('hostname')}")
    print(f"   • Provider: {record.get('operating_system_provider')}")
    print(f"   • Lifecycle Status: {record.get('operating_system_lifecycle_status')}")
    print(f"   • Risk Level: {record.get('risk_level')}")
    print(f"   • System Age: {record.get('system_age_years')} years")
else:
    print("⚠️ No records found in transformed index!")