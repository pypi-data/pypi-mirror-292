def get_headers(tkn: str) -> dict:
    return {"Token": tkn}

def get_headers_app_json(tkn: str) -> dict:
    headers = get_headers(tkn=tkn)
    headers["Content-Type"] = "application/json"
    return headers