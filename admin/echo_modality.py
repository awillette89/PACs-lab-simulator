import requests
ORTHANC="http://127.0.0.1:8042"; AUTH=("orthanc","orthanc")
r=requests.post(f"{ORTHANC}/modalities/pynetscp/echo", auth=AUTH, timeout=10)
print(r.status_code, r.text)
