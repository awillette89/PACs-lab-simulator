import requests, sys
ORTH="http://127.0.0.1:8042"; AUTH=("orthanc","orthanc")
uid=sys.argv[1]

q={"Level":"Study","Query":{"StudyInstanceUID":uid}}
r=requests.post(f"{ORTH}/tools/find", auth=AUTH, json=q, timeout=10)
r.raise_for_status()
hits=r.json()
if not hits:
    raise SystemExit("Study UID not found")

study_id=hits[0]
print("Orthanc study ID:", study_id)

r=requests.post(f"{ORTH}/modalities/pynetscp/store", auth=AUTH, json=study_id, timeout=30)
r.raise_for_status()
print("STORE job submitted:", r.json())