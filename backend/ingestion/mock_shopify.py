from schema import ProductContext



def fetch_product(product_id: str) -> ProductContext:
    products = {
        "001": ProductContext(
            product_id="001",
            title="Classic Running Shoes",
            description="Lightweight shoes great for running. Comfortable fit.",
            variants=["Size 8", "Size 9", "Size 10", "Size 11"],
            return_policy="",  # blank — will expose gap
            shipping_policy="Standard shipping. Arrives in 5-7 days.",
            faqs=[],
            reviews_summary="Customers love the comfort but say sizing runs small."
        ),
        "002": ProductContext(
            product_id="002",
            title="Cotton Polo T-Shirt",
            description="A nice t-shirt. Available in colors.",
            variants=["Blue", "Red"],
            return_policy="No returns on sale items.",
            shipping_policy="Free shipping on orders above 500 rupees.",
            faqs=["Q: Is this machine washable? A: Yes."],
            reviews_summary="Good quality. Some say color fades after washing."
        ),
        "003": ProductContext(
            product_id="003",
            title="Wireless Bluetooth Headphones",
            description="Premium sound quality headphones. Long battery life. Fits most head sizes.",
            variants=["Black", "White"],
            return_policy="Returns accepted within 7 days if unopened.",
            shipping_policy="Express shipping available. Standard takes 3-5 days.",
            faqs=[
                "Q: Is it compatible with iPhone? A: Yes.",
                "Q: What is battery life? A: Around 20 hours."
            ],
            reviews_summary="Great sound. Some users report connectivity issues after 6 months."
        ),
    }
    return products.get(product_id, products["001"])

def fetch_all_product_ids() -> list[str]:
    return ["001", "002", "003"]