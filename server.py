from flask import Flask, request, jsonify
import datetime
import hashlib
import hmac
import requests
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
load_dotenv(dotenv_path='.env')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = "us-east-2"
SERVICE = "execute-api"
HOST = "kxm63nv0uk.execute-api.us-east-2.amazonaws.com"
ENDPOINT = "https://kxm63nv0uk.execute-api.us-east-2.amazonaws.com/Test/generate-accessibility-report"

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def process_html(html_content):
    if isinstance(html_content, str):
        html_content = [html_content]

    REQUEST_PAYLOAD = json.dumps({
        "html": html_content
    })

    amz_date = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    date_stamp = datetime.datetime.utcnow().strftime('%Y%m%d')
    canonical_uri = "/Test/generate-accessibility-report"
    canonical_querystring = ""
    canonical_headers = f"content-type:application/json\nhost:{HOST}\nx-amz-date:{amz_date}\n"
    signed_headers = "content-type;host;x-amz-date"
    payload_hash = hashlib.sha256(REQUEST_PAYLOAD.encode('utf-8')).hexdigest()
    canonical_request = f"POST\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{AWS_REGION}/{SERVICE}/aws4_request"
    canonical_request_hash = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{canonical_request_hash}"

    k_date = sign(("AWS4" + AWS_SECRET_ACCESS_KEY).encode('utf-8'), date_stamp)
    k_region = sign(k_date, AWS_REGION)
    k_service = sign(k_region, SERVICE)
    k_signing = sign(k_service, "aws4_request")
    signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization_header = (
        f"{algorithm} Credential={AWS_ACCESS_KEY_ID}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers = {
        'Content-Type': 'application/json',
        'x-amz-date': amz_date,
        'Authorization': authorization_header
    }

    try:
        response = requests.post(ENDPOINT, headers=headers, data=REQUEST_PAYLOAD)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"

@app.route('/check', methods=['POST'])
def check_accessibility():
    if request.headers['Content-Type'] == 'application/json':
        data = request.get_json()
        if 'html' not in data:
            return "Missing 'html' key in request body", 400
        
        html_content = data['html']

        result = process_html(html_content)
        return result, 200
    else:
        print(f"Unsupported Media Type: {request.headers['Content-Type']}")
        return "Unsupported Media Type", 415

if __name__ == '__main__':
    app.run(port=3001)
