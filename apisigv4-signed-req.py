import datetime
import hashlib
import hmac
import requests
import json

SERVICE = "execute-api"
HOST = "kxm63nv0uk.execute-api.us-east-2.amazonaws.com"
ENDPOINT = "https://kxm63nv0uk.execute-api.us-east-2.amazonaws.com/Test/generate-accessibility-report"
REQUEST_PAYLOAD = json.dumps({
    "html": [
        '<!DOCTYPE html><html lang="en"><head><title>Test Document 1</title></head><body><h1>Test Page 1</h1><a href="#">Link with no description to test</a></body></html>',
        '<!DOCTYPE html><html lang="en"><head><title>Test Document 2</title></head><body><h2>Test Page 2</h2><img src="image.jpg" alt=""></body></html>',
        '<!DOCTYPE html><html lang="en"><head><title>Test Document 3</title></head><body><h3>Test Page 3</h3><button>Click me</button></body></html>',
        '<!DOCTYPE html><html lang="en"><head><title>Test Document 3</title></head><body><h3>Test Page 4</h3><button>Click me</button></body></html>'
    ]
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

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

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

print("Headers for the request:")
for k, v in headers.items():
    print(f"key: {k}, value: {v}")

try:
    response = requests.post(ENDPOINT, headers=headers, data=REQUEST_PAYLOAD)
    
    print("Full Response Details:")
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for header, value in response.headers.items():
        print(f"  {header}: {value}")
    print("Body:")
    print(response.text)
    
    print("Raw Content:")
    print(response.content)
    
    try:
        json_response = response.json()
        print("JSON Response (formatted):")
        print(json.dumps(json_response, indent=2))
    except json.JSONDecodeError:
        print("Response is not JSON decodable")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    if hasattr(e, 'response'):
        print("Error Response Details:")
        print(f"Status Code: {e.response.status_code}")
        print("Headers:")
        for header, value in e.response.headers.items():
            print(f"  {header}: {value}")
        print("Body:")
        print(e.response.text)
    else:
        print("No response available (likely a connection error)")
