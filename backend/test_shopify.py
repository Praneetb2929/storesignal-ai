import httpx
import os
from dotenv import load_dotenv

load_dotenv()

store_url = os.getenv("SHOPIFY_STORE_URL")
token     = os.getenv("SHOPIFY_ACCESS_TOKEN")

url = f"https://{store_url}/admin/api/2024-01/products.json"

response = httpx.get(
    url,
    headers={"X-Shopify-Access-Token": token}
)

print("Status:", response.status_code)
print("First product title:", response.json()["products"][0]["title"])