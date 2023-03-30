import requests
import json

url = "https://google.serper.dev/search"

payload = json.dumps({
  "q": "fudan university",
})
headers = {
  'X-API-KEY': 'b08bef7cb98fbe5f48428d20dbd8d23a0de74f53',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

response_dict = json.loads(response.text)

print(response_dict)

ssss


