import requests

ORTHANC = "http://127.0.0.1:8042"
AUTH = ("orthanc", "orthanc")

def main():
    dest_id = "pynetscp"
    body = {"AET": "PYNETSCP", "Host": "host.docker.internal", "Port": 11112}
    r = requests.put(f"{ORTHANC}/modalities/{dest_id}", auth=AUTH, json=body, timeout=5)
    r.raise_for_status()
    print(f"Registered destination '{dest_id}'. HTTP {r.status_code}")

if __name__=="__main__":
    main()