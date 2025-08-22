import requests

BASE_URL = "http://localhost:8000"
response = requests.get(f"{BASE_URL}/")
print(response.json())

payload = {
    "name": "Grocery Shopping",
    "amount": 50.75,
    "date": "2023-10-01"
}
response = requests.post(
    url=f"{BASE_URL}/add-transaction",
    json=payload
)
print(response.json())