from ingestion.shopify import fetch_all_product_ids, fetch_product

ids = fetch_all_product_ids()
print(f"Found {len(ids)} products: {ids}")

# Fetch the first one
product = fetch_product(ids[0])
print("\n--- ProductContext ---")
print("Title:", product.title)
print("Description:", product.description[:200])
print("Variants:", product.variants)
print("Return policy:", product.return_policy[:100] if product.return_policy else "EMPTY ⚠️")
print("Shipping policy:", product.shipping_policy[:100] if product.shipping_policy else "EMPTY ⚠️")