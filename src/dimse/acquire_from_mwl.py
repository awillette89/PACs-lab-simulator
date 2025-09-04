from pathlib import Path
from datetime import datetime
import numpy as np
from pydicom import dcmread
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import (ExplicitVRLittleEndian, generate_uid,
                         CTImageStorage, PYDICOM_IMPLEMENTATION_UID)

WL_DIR = Path("worklists")
OUT_DIR = Path("data/samples"); OUT_DIR.mkdir(parents=True, exist_ok=True)

def first_wl():
    wl = sorted(WL_DIR.glob("*.wl"))
    if not wl:
        raise SystemExit("No .wl files in ./worklists")
    return dcmread(str(wl[0]), force=True)

def build_ct(ds_wl):
    sps = (ds_wl.get("ScheduledProcedureStepSequence") or [None])[0] or Dataset()
    now = datetime.now()
    # ---- File Meta
    meta = FileMetaDataset()
    meta.FileMetaInformationVersion = b"\x00\x01"
    meta.MediaStorageSOPClassUID = CTImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID
    # ---- Main dataset
    ds = Dataset()
    ds.file_meta = meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Patient / order (from MWL)
    ds.PatientID   = ds_wl.get("PatientID","P0001")
    ds.PatientName = ds_wl.get("PatientName","DOE^JANE")
    ds.PatientBirthDate = ds_wl.get("PatientBirthDate","19800101")
    ds.PatientSex  = ds_wl.get("PatientSex","O")
    ds.AccessionNumber = ds_wl.get("AccessionNumber","ACC0001")

    # Study/series + minimal study context
    ds.StudyInstanceUID  = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID    = meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID       = CTImageStorage
    ds.StudyID = "1"
    ds.StudyDate = now.strftime("%Y%m%d")
    ds.StudyTime = now.strftime("%H%M%S")
    ds.Modality = "CT"
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.StudyDescription  = ds_wl.get("RequestedProcedureDescription","CT CHEST")
    ds.RequestedProcedureID = ds_wl.get("RequestedProcedureID","RP1")
    ds.ReferringPhysicianName = "DR.SMITH"
    # Optional: echo some SPS fields into plain tags
    ds.BodyPartExamined = "CHEST"

    # Minimal pixel data (64x64 int16 gradient)
    arr = np.linspace(-1000, 3000, 64*64, dtype=np.int16).reshape(64,64)
    ds.Rows, ds.Columns = arr.shape
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1  # signed
    ds.PixelData = arr.tobytes()

    # Geometry (minimal but nice to have)
    ds.KVP = "120"
    ds.SliceThickness = "5"
    ds.PixelSpacing = ["0.8","0.8"]
    ds.ImagePositionPatient = ["0","0","0"]
    ds.ImageOrientationPatient = ["1","0","0","0","1","0"]

    return ds

def main():
    wl = first_wl()
    ds = build_ct(wl)
    out = OUT_DIR / f"CT_{ds.PatientID}_{ds.AccessionNumber}.dcm"
    ds.save_as(str(out), write_like_original=False)
    print(f"Wrote DICOM: {out.resolve()}")

if __name__ == "__main__":
    main()