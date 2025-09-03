import argparse
from pydicom.dataset import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelMove

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--study", required=True, help="StudyInstanceUID to move")
    p.add_argument("--dest", default="PYNETSCP")
    p.add_argument("--peer", default="127.0.0.1")
    p.add_argument("--port", type=int, default=4242)
    p.add_argument("--called-aet", default="ORTHANC")
    p.add_argument("--calling-aet", default="PYNETMOVE")
    args = p.parse_args()

    ae = AE(ae_title=args.calling_aet)
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelMove)
    assoc = ae.associate(args.peer, args.port, ae_title=args.called_aet)
    if not assoc.is_established:
        raise SystemExit("Association failed")

    ds = Dataset()
    ds.QueryRetrieveLevel = "STUDY"
    ds.StudyInstanceUID = args.study

    for status, identifier in assoc.send_c_move(ds, args.dest, StudyRootQueryRetrieveInformationModelMove):
        code = getattr(status, "Status", None)
        if code is not None:
            print(f"Status: 0x{code:04X}")
    assoc.release()

if __name__=="__main__":
    main()