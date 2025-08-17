import requests

def get_iam_token_from_metadata() -> str:
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    r = requests.get(url, headers=headers, timeout=3)
    r.raise_for_status()
    return r.json()["access_token"]