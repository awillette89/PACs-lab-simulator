import argparse, logging
from pathlib import Path
from pynetdicom import AE, evt, AllStoragePresentationContexts, debug_logger
from pynetdicom.sop_class import Verification

def on_c_store(event):
    ds = event.dataset
    ds.file_meta = event.file_meta
    out = Path("inbox")
    if not out.exists():
        out.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created folder: {out.resolve()}")
    fname = out / f"{ds.SOPInstanceUID}.dcm"
    ds.save_as(str(fname), write_like_original=False)
    logging.info(f"Saved: {fname.name}")
    return 0x0000

def on_accepted(event):
    a = event.assoc
    import logging
    logging.info(
        f"Association accepted from {a.requestor.address}:{a.requestor.port} "
        f"CallingAET={a.requestor.ae_title} CalledAET={a.ae.ae_title}"
    )

def on_released(event):
    logging.info("Association released")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--aet", default="PYNETSCP")
    p.add_argument("--port", type=int, default=11112)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    if args.verbose:
        debug_logger()

    ae = AE(ae_title=args.aet)
    # Accept all common Storage SOP Classes
    for cx in AllStoragePresentationContexts:
        ae.add_supported_context(cx.abstract_syntax)
    # ALSO accept Verification (C-ECHO)
    ae.add_supported_context(Verification)

    logging.info(f"Starting SCP AET={args.aet} on 0.0.0.0:{args.port}")
    ae.start_server(("0.0.0.0", args.port), block=True,
                    evt_handlers=[(evt.EVT_C_STORE, on_c_store),
                                  (evt.EVT_ACCEPTED, on_accepted),
                                  (evt.EVT_RELEASED, on_released)])

if __name__ == "__main__":
    main()
