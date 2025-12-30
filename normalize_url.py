from urllib.parse import urlparse

def normalize_url(url: str) -> str:
    url = url.strip().lower()
    
    url_tuple = urlparse(url)
    
    netloc = url_tuple.netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]

    normalized = f"{url_tuple.scheme}://{netloc}{url_tuple.path}"
    return normalized.rstrip('/')