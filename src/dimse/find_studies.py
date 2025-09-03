from pydicom.dataset import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind

def main():
    ae = AE(ae_title="PYNETDICOM")
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
    assoc = ae.associate("127.0.0.1", 4242, ae_title="ORTHANC")
    if not assoc.is_established:
        raise SystemExit("Association failed")
    
    ds = Dataset()
    ds.QueryRetrieveLevel = "STUDY"
    ds.PatientName = ""
    ds.PatientID = ""
    ds.StudyDate = ""
    ds.StudyInstanceUID = ""
    ds.ModalitiesInStudy = ""
    ds.NumberOfStudyRelatedInstances = ""

    for status, ident in assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind):
        if status and getattr(status, "Status", None) in (0xFF00, 0xFF01) and ident:
            print(f"{ident.get('PatientName','?')} | {ident.get('PatientID','?')} | "
                  f"{ident.get('StudyDate','????')} | {ident.get('StudyInstanceUID','?')} | "
                  f"{ident.get('ModalitiesInStudy','?')} | "
                  f"{ident.get('NumberOfStudyRelatedInstances','?')}")
    assoc.release()

    if __name__=="__main__":
        main()