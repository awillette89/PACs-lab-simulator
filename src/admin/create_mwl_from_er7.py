from pathlib import Path
from datetime import datetime, timedelta
import requests

ORTHANC = "http://127.0.0.1:8042"
AUTH = ("orthanc","orthanc")

def parse_er7(lines):
    fields = {"PID": {}, "ORC": {}, "OBR": {}}
    for raw in lines:
        seg = raw.strip()
        if not seg: continue
        parts = seg.split("|")
        t = parts[0]
        if t == "PID":
            # PID|1||PID-3||PID-5||PID-7|PID-8
            fields["PID"]["3"] = parts[3] if len(parts) > 3 else ""
            fields["PID"]["5"] = parts[5] if len(parts) > 5 else ""
            fields["PID"]["7"] = parts[7] if len(parts) > 7 else ""
            fields["PID"]["8"] = parts[8] if len(parts) > 8 else ""
        elif t == "ORC":
            # ORC|NW|RP_ID|ACC
            fields["ORC"]["2"] = parts[2] if len(parts) > 2 else ""
            fields["ORC"]["3"] = parts[3] if len(parts) > 3 else ""
        elif t == "OBR":
            # OBR|1|ACC|ACC|CTCHEST^PROC_TEXT
            fields["OBR"]["3"] = parts[3] if len(parts) > 3 else ""
            fields["OBR"]["4"] = parts[4] if len(parts) > 4 else ""
    return fields

def main():
    adt_text = Path("data/samples/adt_a08.hl7").read_text()
    orm_text = Path("data/samples/orm_o01.hl7").read_text()

    f_adt = parse_er7(adt_text.split("\r"))
    f_orm = parse_er7(orm_text.split("\r"))

    pid = f_orm["PID"].get("3") or f_adt["PID"].get("3") or "P0001"
    pname = f_orm["PID"].get("5") or f_adt["PID"].get("5") or "DOE^JANE"
    dob = f_orm["PID"].get("7") or f_adt["PID"].get("7") or "19800101"
    sex = f_orm["PID"].get("8") or f_adt["PID"].get("8") or "F"

    acc = f_orm["OBR"].get("3") or f_orm["ORC"].get("3") or "ACC1001"
    rp_id = f_orm["ORC"].get("2") or "RP1001"
    proc_comp = f_orm["OBR"].get("4") or "CTCHEST^CT CHEST"
    proc_text = (proc_comp.split("^", 1)[1] if "^" in proc_comp else proc_comp) or "CT CHEST"

    modality = "CT"
    for m in ("CT","MR","US","XA","MG","DX","NM","PT","CR"):
        if proc_text.upper().startswith(m):
            modality = m; break

    when = datetime.now() + timedelta(minutes=10)
    sps_date = when.strftime("%Y%m%d")
    sps_time = when.strftime("%H%M%S")
    station_aet = "PYMOD1"

    mwl = {
        "00080050": acc,
        "00100010": pname,
        "00100020": pid,
        "00100030": dob,
        "00100040": sex,
        "00400100": [ {
            "00400001": station_aet,
            "00400002": sps_date,
            "00400003": sps_time,
            "00080060": modality,
            "00400006": "DR.SMITH",
            "00400007": proc_text,
            "00400009": rp_id
        } ],
        "00401001": rp_id,
        "00321060": proc_text
    }

    r = requests.post(f"{ORTHANC}/worklists", auth=AUTH, json=mwl, timeout=10)
    r.raise_for_status()
    print("MWL created:", r.json())

if __name__ == "__main__":
    main()