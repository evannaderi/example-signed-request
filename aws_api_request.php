<?php

// Load environment variables
$dotenv = parse_ini_file('.env');
$AWS_ACCESS_KEY_ID = $dotenv['AWS_ACCESS_KEY_ID'];
$AWS_SECRET_ACCESS_KEY = $dotenv['AWS_SECRET_ACCESS_KEY'];

$AWS_REGION = "us-east-2";
$SERVICE = "execute-api";
$HOST = "kxm63nv0uk.execute-api.us-east-2.amazonaws.com";
$ENDPOINT = "https://kxm63nv0uk.execute-api.us-east-2.amazonaws.com/Test/generate-accessibility-report";

// Read HTML content
$html_content = file_get_contents('test.html');

$REQUEST_PAYLOAD = json_encode([
    "html" => [$html_content]
]);

$amz_date = gmdate('Ymd\THis\Z');
$date_stamp = gmdate('Ymd');

$canonical_uri = "/Test/generate-accessibility-report";
$canonical_querystring = "";
$canonical_headers = "content-type:application/json\nhost:{$HOST}\nx-amz-date:{$amz_date}\n";
$signed_headers = "content-type;host;x-amz-date";
$payload_hash = hash('sha256', $REQUEST_PAYLOAD);

$canonical_request = "POST\n{$canonical_uri}\n{$canonical_querystring}\n{$canonical_headers}\n{$signed_headers}\n{$payload_hash}";

$algorithm = "AWS4-HMAC-SHA256";
$credential_scope = "{$date_stamp}/{$AWS_REGION}/{$SERVICE}/aws4_request";
$canonical_request_hash = hash('sha256', $canonical_request);
$string_to_sign = "{$algorithm}\n{$amz_date}\n{$credential_scope}\n{$canonical_request_hash}";

function sign($key, $msg) {
    return hash_hmac('sha256', $msg, $key, true);
}

$k_date = sign("AWS4" . $AWS_SECRET_ACCESS_KEY, $date_stamp);
$k_region = sign($k_date, $AWS_REGION);
$k_service = sign($k_region, $SERVICE);
$k_signing = sign($k_service, "aws4_request");

$signature = hash_hmac('sha256', $string_to_sign, $k_signing);

$authorization_header = 
    "{$algorithm} Credential={$AWS_ACCESS_KEY_ID}/{$credential_scope}, " .
    "SignedHeaders={$signed_headers}, Signature={$signature}";

$headers = [
    'Content-Type: application/json',
    "x-amz-date: {$amz_date}",
    "Authorization: {$authorization_header}"
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $ENDPOINT);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $REQUEST_PAYLOAD);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

try {
    $response = curl_exec($ch);
    
    if ($response === false) {
        throw new Exception(curl_error($ch), curl_errno($ch));
    }
    
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    if ($http_code >= 400) {
        throw new Exception("HTTP Error: " . $http_code);
    }
    
    echo $response;
    
    // Attempt to decode JSON response
    $json_response = json_decode($response, true);
    if (json_last_error() === JSON_ERROR_NONE) {
        // If you want to print formatted JSON, uncomment the next line
        // echo json_encode($json_response, JSON_PRETTY_PRINT);
    }
} catch (Exception $e) {
    echo "An error occurred: " . $e->getMessage();
}

curl_close($ch);
