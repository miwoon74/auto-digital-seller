def create_gumroad_product_with_file(title, description, price, pdf_path):
    url = "https://api.gumroad.com/v2/products"
    
    data = {
        "access_token": GUMROAD_TOKEN,
        "name": title,
        "price": price,
        "description": f"{description}\n\n----------\n📄 Access Link Included: Download the attached PDF guide to access your digital assets immediately.",
    }

    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path, f, "application/pdf")}
        res = requests.post(url, data=data, files=files)

    if res.status_code in [200, 201]:
        p_data = res.json().get("product", {})
        # url 및 short_url을 순차적으로 확인하여 링크 추출
        return p_data.get("url") or p_data.get("short_url") or "https://gumroad.com/products"
    else:
        raise Exception(f"Gumroad API Error: {res.status_code} - {res.text}")
