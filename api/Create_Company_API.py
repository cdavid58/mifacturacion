import requests
import json

class RegisterCompanyAPI:
  def __init__(self,data):
    self.data = data

  def Register(self):
    url = "http://localhost:8000:8787/apidian/server.php/api/ubl2.1/config/"+str(self.data['document_identification'])+"/"+str(self.data['dv'])
    payload = json.dumps({
      "type_document_identification_id": self.data['type_document_identification_id'],
      "type_organization_id": self.data['type_organization_id'],
      "type_regime_id": self.data['type_regime_id'],
      "type_liability_id": self.data['type_liability_id'],
      "business_name": self.data['business_name'],
      "merchant_registration": self.data['merchant_registration'],
      "municipality_id": self.data['municipality_id'],
      "address": self.data['address'],
      "phone": self.data['phone'],
      "email": self.data['email'],
      "mail_host": "smtp.gmail.com",
      "mail_port": "587",
      "mail_username": "evansoftmd@gmail.com",
      "mail_password": "ccsdfjruqddyxcsjgfggqlqvttt",
      "mail_encryption": "tls"
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    _response = json.loads(response.text)
    print(_response['token'])
    return _response['token']
