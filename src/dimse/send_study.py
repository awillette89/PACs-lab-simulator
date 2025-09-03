import argparse
from pynetdicom import AE, StoragePresentationContexts
from pynetdicom.sop_class import Verification
from pydicom import dcmread

def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", help="Path to DICOM file")
    p.add_argument("--peer", default="127.0.0.1")
    p.add_argument("--port", type=int, default=4242)
    p.add_argument("--called-aet", default="ORTHANC")
    p.add_argument("--calling-aet", default="PYNETDICOM")
    args =  p.parse_args()

    ae = AE(ae_title=args.calling_aet)
    ae.requested_contexts = StoragePresentationContexts
    ae.add_requested_context(Verification)

    assoc = ae.associate(args.peer, args.port, ae_title=args.called_aet)
    if not assoc.is_established:
        raise SystemExit("Association failed")
    
    status = assoc.send_c_echo()
    if not getattr(status, "Status", None) == 0x0000:
        raise SystemExit(f"C-ECHO failed: {getattr(status,'Status',None)}")
    
    ds = dcmread(args.path)
    st = assoc.send_c_store(ds)
    print(f"C-STORE status: 0x{getattr(st,'Status',0):04X}")

    assoc.release()

if __name__=="__main__":
    main()