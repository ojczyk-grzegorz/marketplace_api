import sys
import json
import requests


filepath = sys.argv[1]
with open(filepath, "r") as file:
    req_data: dict = json.load(file)

method: str = req_data.get("method", "GET")
url: str = req_data.get("url", "http://127.0.0.1:8000/")
route: str = req_data.get("route", "")
body: dict = req_data.get("body", {})

response = requests.request(
    method,
    url=url + route,
    json=body
)

print(
    json.dumps(
        [
            response.status_code,
            response.json()
        ],
        indent=4
    )
)