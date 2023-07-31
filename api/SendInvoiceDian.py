from .translator import Translator
from datetime import date
from invoice.models import Invoice,Payment_Form_Invoice
from company.models import Company
from django.shortcuts import render
t = Translator()

class send_invoice_dian:
  def __init__(self,number,nit):
    self.number = number
    self.company = Company.objects.get(documentIdentification = t.codificar(str(nit)))
    self.invoice_ = Invoice.objects
    self.invf = self.invoice_.filter(number = t.codificar(str(number)),company= self.company)
    self.invu = self.invf.last()
    self.fp = Payment_Form_Invoice.objects.get(invoice = self.invu)

  def Customer(self):
    c = self.invu.client
    data = {
      "identification_number": 900541566,
      "dv": 1,
      "name": t.decodificar(str(c.name)),
      "phone": t.decodificar(str(c.phone)),
      "address": t.decodificar(str(c.address)),
      "email": t.decodificar(str(c.email)),
      "merchant_registration": t.decodificar(str(c.merchant_registration)),
      "type_document_identification_id": c.type_documentI.id,
      "type_organization_id": c.type_organization.id,
      "type_liability_id": 7,
      "municipality_id": c.municipality.id,
      "type_regime_id": c.type_regime.id
    }
    return data

  def Invoice_Lines(self):
    data = [
      {
        "unit_measure_id": 70,
        "invoiced_quantity": t.decodificar(str(i.quanty)),
        "line_extension_amount": str(i.Base_Product_WithOut_Discount()),
        "free_of_charge_indicator": False,
        "tax_totals": [
          {
            "tax_id": 1,
            "tax_amount": str(i.Tax_Value()),
            "taxable_amount": str(i.Base_Product_WithOut_Discount()),
            "percent": '19'
          }
        ],
        "description": t.decodificar(str(i.description)),
        "notes": t.decodificar(str(i.notes)),
        "code": t.decodificar(str(i.code)),
        "type_item_identification_id": 4,
        "price_amount": str(i.Neto()),
        "base_quantity": t.decodificar(str(i.quanty))
      }
      for i in self.invf
    ]
    return data

  def Taxs(self):
    list_tax = []
    for i in self.invf:
      if t.decodificar(str(i.tax)) not in list_tax:
        list_tax.append(t.decodificar(str(i.tax)))
    data = []
    values = []
    for j in list_tax:
      _i = self.invoice_.filter(company = self.company,number = t.codificar(str(self.number)),tax = t.codificar(str(j)))
      value_tax = 0
      value_base_product = 0
      for i in _i:
        value_tax += i.Tax_Value()
        value_base_product += i.Base_Product_WithOut_Discount()
      data.append(
        {
          "tax_id": 1,
          "tax_amount": str(value_tax),
          "percent": str(j),
          "taxable_amount": str(value_base_product)
        }
      )
    return data

  def Payment_Form(self):
    data = {
      "payment_form_id": self.fp.payment_form_id.id,
      "payment_method_id": self.fp.payment_method_id.id,
      "payment_due_date": self.fp.payment_due_date,
      "duration_measure": self.fp.duration_measure
    }
    return data

  def Legal_Monetary_Totals(self):
    subtotal = 0
    tax = 0
    total = 0 
    ico = 0
    for i in self.invf:
      subtotal += i.Base_Product_WithOut_Discount()
      tax += i.Tax_Value()
      total += i.Neto()
      ico += float(t.decodificar(str(i.ipo))) * float(t.decodificar(str(i.quanty)))
    data = {
      "line_extension_amount": subtotal,
      "tax_exclusive_amount": subtotal,
      "tax_inclusive_amount": total - ico,
      "charge_total_amount": str(ico),
      "payable_amount": total
    }

    return data

  def AllowanceCharges(self):
    ico = 0
    subtotal = 0
    for i in self.invf:
      ico += float(t.decodificar(str(i.ipo))) * float(t.decodificar(str(i.quanty)))
      subtotal += i.Base_Product_WithOut_Discount()
    data = [{
      "discount_id": 1,
      "charge_indicator": True,
      "allowance_charge_reason": "VALOR DEL IMPUESTO AL CONSUMO",
      "amount": ico,
      "base_amount": subtotal
    }]
    return data

  def Send_Electronic_Invoice(self):
    company = self.invu.company
    data = {
      "number": 2468,#t.decodificar(str(self.invu.number)),
      "type_document_id": 1,
      "date": str(date.today()),
      "Generation_Date":t.decodificar(str(self.invu.date)),
      "time": "04:08:12",
      "resolution_number": str(company.resolution_number),
      "prefix": str(company.prefix),
      "notes": "ESTA ES UNA NOTA DE PRUEBA",
      "disable_confirmation_text": True,
      "establishment_name":  t.decodificar(str(company.business_name)),
      "establishment_address":  t.decodificar(str(company.address)),
      "establishment_phone":  t.decodificar(str(company.phone)),
      "establishment_municipality": company.municipality.id,
      "foot_note": "Factura elaborada por Evansoft - 3004609548"
    }
    import json,requests
    data['customer'] = self.Customer()
    data['allowance_charges'] = self.AllowanceCharges()
    data['payment_form'] = self.Payment_Form()
    data['legal_monetary_totals'] = self.Legal_Monetary_Totals()
    data['tax_totals'] = self.Taxs()
    data['invoice_lines'] = self.Invoice_Lines()
    _data = json.dumps(data)
    url = "http://localhost/api_solo_pdf/public/api/ubl2.1/invoice"
    token = "654bcc733f62fa7a5e9548b16057712ed4e30166a7c11f86e76eae9224faf5c0"
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'host': 'apidian2022.oo',
      'Authorization': 'Bearer '+str(token)
    }
    response = requests.request("POST", url, headers=headers, data=_data)
    print(response.text)
    resp = json.loads(response.text)
    response_dian = ""
    for i in self.invf:
      if 'errors' in resp:        
        for j,k in resp['errors'].items():
          if len(resp['errors']) == 1:
            response_dian = k
          else:
            response_dian += k+", "
        i.state = t.codificar(str(response_dian))
      elif "Documento procesado anteriormente" in response.text:
        i.state = t.codificar(str("Documento procesado anteriormente"))
      else:
        i.state = t.codificar(str("Documento procesado correctamente."))
      i.save()
    
    print(response_dian)
    return _data



