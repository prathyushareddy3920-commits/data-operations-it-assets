from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os

# === CONFIGURATION ===
ES_ENDPOINT = "https://my-elasticsearch-project-a42a97.es.us-central1.gcp.elastic.cloud:443"
ES_API_KEY = "QWVPVE9ab0I3OVh1cUlFeFQ3TFI6eUxHa0Z5aVFURXZSZUw4ak1na0J6Zw=="
CSV_FILE = "C:/Users/PrathyushaChilkamari/Documents/GitHub/data-operations-it-assets/it_asset_inventory_cleaned.csv"
TARGET_INDEX = "it_asset2"

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

# === READ CSV FILE ===
if not os.path.exists(CSV_FILE):
    print(f"❌ CSV file not found: {CSV_FILE}")
    exit()

df = pd.read_csv(CSV_FILE)
print(f"📄 Loaded {len(df)} records from {CSV_FILE}")

# === PREPARE BULK DATA ===
actions = [
    {
        "_index": TARGET_INDEX,
        "_source": row.to_dict()
    }
    for _, row in df.iterrows()
]

# === BULK UPLOAD ===
try:
    helpers.bulk(es, actions)
    print(f"✅ Successfully uploaded {len(actions)} documents to index '{TARGET_INDEX}'")
except Exception as e:
    print(f"❌ Bulk upload failed: {e}")