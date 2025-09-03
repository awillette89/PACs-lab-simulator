import requests, sys, json
ORTHANC="http://127.0.0.1:8042"; AUTH=("orthanc","orthanc")

def main(uid):
    q={"Level":"Study","Query":{"StudyInstanceUID":uid},"Expand":True}
    r=requests.post(f"{ORTHANC}/tools/find", auth=AUTH, json=q, timeout=10)
    r.raise_for_status()
    hits=r.json()
    if not hits:
        print("NO MATCH"); return 1
    study=hits[0]
    print("MATCH:", json.dumps({"OrthancID":study["ID"],
                                "Instances":len(study.get("Instances",[])),
                                "PatientID":study.get("PatientMainDicomTags",{}).get("PatientID","")}))
    return 0

if __name__=="__main__":
    sys.exit(main(sys.argv[1]))
