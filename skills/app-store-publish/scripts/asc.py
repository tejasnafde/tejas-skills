# asc.py METHOD PATH [json]: one App Store Connect API call. The ES256 key is read from
# Secret Manager (APPLE_ASC_API_KEY, gcloud --configuration=personal) at run time, so this
# file holds no secret. Needs PyJWT with cryptography.
import json, subprocess, sys, time, urllib.request, urllib.error, jwt
k = json.loads(subprocess.run(["/opt/homebrew/share/google-cloud-sdk/bin/gcloud", "--configuration=personal", "secrets",
                               "versions", "access", "latest", "--secret=APPLE_ASC_API_KEY"], capture_output=True, text=True, check=True).stdout)
tok = jwt.encode({"iss": k["issuer_id"], "iat": int(time.time()), "exp": int(time.time()) + 900, "aud": "appstoreconnect-v1"},
                 k["p8"], algorithm="ES256", headers={"kid": k["key_id"], "typ": "JWT"})
method, path = sys.argv[1], sys.argv[2]
data = sys.argv[3].encode() if len(sys.argv) > 3 else None
req = urllib.request.Request("https://api.appstoreconnect.apple.com" + path, data=data, method=method,
                             headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read(); print(body.decode() if body else "{}")
except urllib.error.HTTPError as e:
    print(json.dumps({"http_error": e.code, "body": json.loads(e.read() or b"{}")})); sys.exit(1)
