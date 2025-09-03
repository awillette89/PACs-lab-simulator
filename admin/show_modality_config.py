# show_destination.py
import requests
ORTHANC="http://127.0.0.1:8042"; AUTH=("orthanc","orthanc")
r = requests.get(f"{ORTHANC}/modalities/pynetscp/configuration", auth=AUTH, timeout=5)
r.raise_for_status()
print(r.json())

