from datetime import datetime
from pathlib import Path

def main():
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    pid = "P12345"; pname = "DOE^JANE"; dob = "19800101"; sex = "F"
    acc = "ACC1001"; rp_id = "RP1001"; proc_text = "CT CHEST W CONTRAST"

    adt = "\r".join([
        f"MSH|^~\\&|SIM|RAD|PACS|ORTHANC|{now}||ADT^A08|MSG0001|P|2.5",
        f"PID|1||{pid}||{pname}||{dob}|{sex}",
        "PV1|1|O"
    ]) + "\r"

    orm = "\r".join([
        f"MSH|^~\\&|SIM|RAD|PACS|ORTHANC|{now}||ORM^O01|MSG0002|P|2.5",
        f"PID|1||{pid}||{pname}||{dob}|{sex}",
        f"ORC|NW|{rp_id}|{acc}",
        f"OBR|1|{acc}|{acc}|CTCHEST^{proc_text}"
    ]) + "\r"

    out = Path("data/samples"); out.mkdir(parents=True, exist_ok=True)
    (out/"adt_a08.hl7").write_text(adt)
    (out/"orm_o01.hl7").write_text(orm)
    print("Wrote:", out/"adt_a08.hl7", "and", out/"orm_o01.hl7")

if __name__ == "__main__":
    main()
