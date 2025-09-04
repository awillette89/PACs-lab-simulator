from pathlib import Path
from datetime import datetime, timedelta
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ImplicitVRLittleEndian, UID, generate_uid

def main():
    # Minimal demo values
    pid = "P12345"; pname = "DOE^JANE"; dob = "19800101"; sex = "F"
    acc = "ACC1001"; rp_id = "RP1001"; proc_text = "CT CHEST W CONTRAST"
    modality = "CT"; station_aet = "PYMOD1"
    when = datetime.now() + timedelta(minutes=10)
    sps_date = when.strftime("%Y%m%d"); sps_time = when.strftime("%H%M%S")

    # File meta (use MWL FIND SOP Class UID for clarity)
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = UID("1.2.840.10008.5.1.4.31")
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ImplicitVRLittleEndian  # <= implicit

    # Dataset with only the key attributes
    ds = Dataset()
    ds.file_meta = meta
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # Patient/Order (flat)
    ds.AccessionNumber = acc                       # (0008,0050)
    ds.PatientName = pname                         # (0010,0010) "DOE^JANE"
    ds.PatientID = pid                             # (0010,0020)
    ds.PatientBirthDate = dob                      # (0010,0030)
    ds.PatientSex = sex                            # (0010,0040)
    ds.RequestedProcedureID = rp_id                # (0040,1001)
    ds.RequestedProcedureDescription = proc_text   # (0032,1060)

    # Scheduled Procedure Step Sequence (one item, minimal)
    sps = Dataset()
    sps.ScheduledStationAETitle = station_aet                  # (0040,0001)
    sps.ScheduledProcedureStepStartDate = sps_date             # (0040,0002)
    sps.ScheduledProcedureStepStartTime = sps_time             # (0040,0003)
    sps.Modality = modality                                    # (0008,0060)
    ds.ScheduledProcedureStepSequence = [sps]                  # (0040,0100)

    out_dir = Path("worklists"); out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{acc}.wl"
    ds.save_as(str(out_path), write_like_original=False)
    print("Wrote minimal worklist:", out_path.resolve())

if __name__ == "__main__":
    main()
