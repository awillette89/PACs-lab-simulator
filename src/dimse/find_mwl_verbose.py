# src/dimse/find_mwl_verbose.py
from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import ModalityWorklistInformationFind

def main():
    debug_logger()
    ae = AE(ae_title="PYMOD1")
    ae.add_requested_context(ModalityWorklistInformationFind)
    assoc = ae.associate("127.0.0.1", 4242, ae_title="ORTHANC")
    print("Assoc:", assoc.is_established)
    if not assoc.is_established: return
    ds = Dataset()
    ds.PatientName = ""; ds.PatientID = ""; ds.AccessionNumber = ""
    ds.RequestedProcedureID = ""; ds.RequestedProcedureDescription = ""
    sps = Dataset(); sps.ScheduledStationAETitle = "PYMOD1"; sps.Modality = ""
    sps.ScheduledProcedureStepStartDate = ""; sps.ScheduledProcedureStepStartTime = ""
    sps.ScheduledProcedureStepDescription = ""; sps.ScheduledProcedureStepID = ""
    ds.ScheduledProcedureStepSequence = [sps]
    got = 0
    for status, rsp in assoc.send_c_find(ds, ModalityWorklistInformationFind):
        print("Status:", hex(getattr(status,"Status",0)))
        if rsp: got += 1
    print("Matches:", got)
    assoc.release()
if __name__ == "__main__": main()
