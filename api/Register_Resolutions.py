import requests
import json



def Register(token):
  url = "http://localhost:8000:8787/apidian/server.php/api/ubl2.1/config/resolution"

  payload = json.dumps({
    "type_document_id": 1,
    "prefix": "SETP",
    "resolution": "18760000001",
    "resolution_date": "2019-01-19",
    "technical_key": "fc8eac422eba16e22ffd8c6f94b3f40a6e38162c",
    "from": 990000000,
    "to": 995000000,
    "generated_to_date": 0,
    "date_from": "2019-01-19",
    "date_to": "2030-01-19"
  })
  headers = {
    'Content-Type': 'application/json',
    'accept': 'application/json',
    'Authorization': 'Bearer '+str(token)
  }
  print(token)

  response = requests.request("PUT", url, headers=headers, data=payload)
  print(response.text)
