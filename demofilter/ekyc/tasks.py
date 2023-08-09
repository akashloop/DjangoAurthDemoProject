from celery import shared_task
import requests
from .models import *

@shared_task
def ocr_process(id):
    api_url = 'https://api.ocr.space/parse/image'
    print("id",id)
    kyc_kyb = KYCKYBEntry.objects.get(id=id)
    apikey = {
    'apikey': 'K89562154588957'
    }
    payload = {
        'url': kyc_kyb.doc_image,
    }
    response = requests.post(api_url, data=apikey, files=payload)
    if response.status_code == 200:
        responce = response.json()
        kyc_kyb_list = []
        kyc_kyb_data= KYCKYBEntry.objects.filter(id=id)
        for data in kyc_kyb_data :
            kyc_kyb_list.append(data.doc_number)
            kyc_kyb_list.append(data.dob)
        parsed_text_value = responce["ParsedResults"][0]['ParsedText']
        parsed_lines = parsed_text_value.split('\r\n')
        parsed_lines = [line.replace(' ', '').replace('-', '') for line in parsed_lines]
        for item in kyc_kyb_list:
            for data in kyc_kyb_data:
                if data.doc_number in parsed_lines:
                    data.verification_status = "approved"
                    data.save()
                    print(f"Found: {item}")
                else:
                    data.verification_status = "rejected"
                    data.save()
                    print(f"Not Found: {item}")
        return response.json()
    else:
        return None