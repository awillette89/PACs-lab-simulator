from pydicom.dataset import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import ModalityWorklistInformationFind

def main():
    ae = AE(ae_title="PYMOD1")  # must match ScheduledStationAETitle to be realistic
    ae.add_requested_context(ModalityWorklistInformationFind)
    assoc = ae.associate("127.0.0.1", 4242, ae_title="ORTHANC")
    if not assoc.is_established:
        raise SystemExit("Association failed")

    ds = Dataset()
    # Return keys
    ds.PatientName = ""
    ds.PatientID = ""
    ds.AccessionNumber = ""
    ds.RequestedProcedureID = ""
    ds.RequestedProcedureDescription = ""

    # MWL requires SPS sequence; include an item (empty = wildcard)
    sps = Dataset()
    sps.ScheduledStationAETitle = "PYMOD1"
    sps.Modality = ""
    sps.ScheduledProcedureStepStartDate = ""
    sps.ScheduledProcedureStepStartTime = ""
    sps.ScheduledProcedureStepDescription = ""
    sps.ScheduledProcedureStepID = ""
    ds.ScheduledProcedureStepSequence = [sps]

    for status, rsp in assoc.send_c_find(ds, ModalityWorklistInformationFind):
        code = getattr(status, "Status", None)
        if code in (0xFF00, 0xFF01) and rsp:
            sseq = rsp.get("ScheduledProcedureStepSequence", [])
            item = sseq[0] if sseq else Dataset()
            print(
                f"{rsp.get('PatientName','?')} | {rsp.get('PatientID','?')} | "
                f"ACC={rsp.get('AccessionNumber','?')} | "
                f"RPID={rsp.get('RequestedProcedureID','?')} | "
                f"SPS='{item.get('ScheduledProcedureStepDescription','?')}' "
                f"{item.get('ScheduledProcedureStepStartDate','????')} "
                f"{item.get('ScheduledProcedureStepStartTime','??????')} "
                f"MOD={item.get('Modality','?')}"
            )
    assoc.release()

if __name__ == "__main__":
    main()