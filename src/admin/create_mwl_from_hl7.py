from pathlib import Path
from datetime import datetime, timedelta
import requests
from hl7apy.parser import parse_message

ORTHANC = "http://127.0.0.1:8042"
AUTH = ("orthanc","orthanc")

def first_or_blank(val): return val if val else ""

def get_pid_fields(msg):
    # Works for both strict and tolerant parses
    try:
        pid = msg.PID
    except AttributeError:
        pid = msg.segment('PID')[0]
    pid3 = first_or_blank(getattr(pid, "pid_3", None).to_er7() if hasattr(pid,"pid_3") else "")
    pid5 = first_or_blank(getattr(pid, "pid_5", None).to_er7() if hasattr(pid,"pid_5") else "")
    pid7 = first_or_blank(getattr(pid, "pid_7", None).to_er7() if hasattr(pid,"pid_7") else "")
    pid8 = first_or_blank(getattr(pid, "pid_8", None).to_er7() if hasattr(pid,"pid_8") else "")
    return pid3, pid5, pid7, pid8

def main():
    adt = parse_message(Path("data/samples/adt_a08.hl7").read_text(), find_groups=False)
    orm = parse_message(Path("data/samples/orm_o01.hl7").read_text(), find_groups=False)

    pid_adt = get_pid_fields(adt)
    pid_orm = get_pid_fields(orm)
    pid = pid_orm[0] or pid_adt[0]
    pname = pid_orm[1] or pid_adt[1]
    dob = pid_orm[2] or pid_adt[2]
    sex = pid_orm[3] or pid_adt[3]

    # Accession and procedure text from ORM
    try:
        acc = getattr(orm.OBR, "obr_3", None).to_er7() if hasattr(orm,"OBR") else ""
    except Exception:
        acc = ""
    try:
        proc_text = getattr(orm.OBR.obr_4, "ce_2", None) or "CT CHEST"
    except Exception:
        proc_text = "CT CHEST"
    try:
        rp_id = getattr(orm.ORC, "orc_2", None).to_er7() if hasattr(orm,"ORC") else "RP1001"
    except Exception:
        rp_id = "RP1001"

    modality = "CT"
    for m in ("CT","MR","US","XA","MG","DX","NM","PT","CR"):
        if proc_text.upper().startswith(m):
            modality = m; break

    when = datetime.now() + timedelta(minutes=10)
    sps_date = when.strftime("%Y%m%d"); sps_time = when.strftime("%H%M%S")
    station_aet = "PYMOD1"

    mwl = {
        "00080050": acc,                 # AccessionNumber
        "00100010": pname,               # PatientName (DOE^JANE)
        "00100020": pid,                 # PatientID
        "00100030": dob,                 # PatientBirthDate
        "00100040": sex,                 # PatientSex
        "00400100": [ {
            "00400001": station_aet,     # ScheduledStationAETitle
            "00400002": sps_date,        # StartDate
            "00400003": sps_time,        # StartTime
            "00080060": modality,        # Modality
            "00400006": "DR.SMITH",
            "00400007": proc_text,       # SPS Description
            "00400009": rp_id            # SPS ID
        } ],
        "00401001": rp_id,               # RequestedProcedureID
        "00321060": proc_text            # RequestedProcedureDescription
    }

    r = requests.post(f"{ORTHANC}/worklists", auth=AUTH, json=mwl, timeout=10)
    r.raise_for_status()
    print("MWL created:", r.json())

if __name__ == "__main__":
    main()
