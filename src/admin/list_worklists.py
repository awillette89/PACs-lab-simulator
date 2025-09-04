from pathlib import Path
from pydicom import dcmread

def main():
    wl_dir = Path("worklists")
    for p in sorted(wl_dir.glob("*.wl")):
        ds = dcmread(str(p), force=True)
        sps = (ds.get("ScheduledProcedureStepSequence") or [None])[0] or {}
        print(f"{p.name} | PID={ds.get('PatientID','?')} | "
              f"PN={ds.get('PatientName','?')} | ACC={ds.get('AccessionNumber','?')} | "
              f"RPID={ds.get('RequestedProcedureID','?')} | "
              f"DATE={sps.get('ScheduledProcedureStepStartDate','????')} "
              f"TIME={sps.get('ScheduledProcedureStepStartTime','????')} | "
              f"MOD={sps.get('Modality','?')} | AET={sps.get('ScheduledStationAETitle','?')}")
if __name__ == "__main__":
    main()