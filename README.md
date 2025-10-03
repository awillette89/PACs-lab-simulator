# PACS Lab Simulator (MVP)

A minimal, Windows-friendly PACS sandbox that simulates a radiology workflow:

**HL7-ish order → Modality Worklist (.wl) → “Acquisition” → C-STORE to PACS → Web viewer**

Built for radiologic technologists transitioning into data/PACS analytics. Uses **Orthanc** (Docker) + **Python** (pydicom, pynetdicom).

---

## Features (MVP)

- **Orthanc PACS** in Docker (DICOM 4242, REST 8042), DICOMweb enabled  
- **Worklists plugin** (DIMSE-only) serving **`.wl`** files from a host folder  
- **Modality Worklist C-FIND** client (AET `PYMOD1`)  
- **Acquisition generator** → valid **CT Image Storage** from MWL data  
- **C-STORE** sender to PACS  
- **Admin helpers** (echo/register/list, push-store, list worklists)  
- **No PHI** (synthetic demographics; runtime artifacts gitignored)

---

## Quick Demo

```powershell
# 0) Requirements: Docker Desktop + Python 3.10+ (tested on 3.13)
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1) Start Orthanc (creates local volume + worklists bind)
docker compose up -d

# 2) End-to-end demo (creates WL → queries MWL → acquires → sends)
python src/demo.py

# 3) Open PACS UI (login: orthanc / orthanc)
# http://localhost:8042/
```

You’ll see a study for **PID `P12345`** with **Accession `ACC1001`**, modality **CT**, description **CT CHEST W CONTRAST**.

---

## Architecture (MVP)

```
+------------------+          (.wl files)          +------------------+
|  "RIS-ish" gen   | --writes--> ./worklists  -->  |   Orthanc PACS   |
| (Python ER7→WL)  |                                |  + Worklists     |
+------------------+                                |  + DICOMweb      |
           ^                                        +---------+--------+
           |                                                     ^
           | MWL C-FIND (DIMSE 4242)                             | C-STORE
+----------+-----------+                                         |
|   Modality Sim      | --creates CT .dcm --> ./data/samples --> |
| (find_mwl + acquire)|                                         |
+---------------------+------------------------------------------+
```

---

## Repository Layout

```
docker-compose.yml
requirements.txt
src/
  admin/
    create_wl_file.py           # generate minimal .wl for Worklists plugin
    list_worklists.py           # local viewer for .wl files (for demos)
    register_modality.py        # register a DICOM destination in Orthanc
    echo_modality.py            # C-ECHO test from Orthanc
    show_modality_config.py     # show a modality's config
    list_modalities.py
    push_store.py               # PACS -> SCP push (C-STORE)
    verify_uid.py               # verify study UID in Orthanc
  dimse/
    find_mwl.py                 # MWL C-FIND (modality side)
    find_mwl_verbose.py         # verbose variant
    acquire_from_mwl.py         # synthesize CT image from MWL data
    send_study.py               # C-STORE to Orthanc
    recv_scp.py                 # simple C-STORE SCP -> ./data/inbox
  demo.py                       # one-command demo runner
data/
  samples/                      # generated demo DICOM(s)
  inbox/                        # runtime receiving folder (gitignored)
worklists/                      # MWL .wl files served by Orthanc
```

---

## Docker Compose (Orthanc)

- **Ports:** 8042 (REST/UI), 4242 (DICOM)
- **Worklists:** host `./worklists` mounted to `/var/lib/orthanc/worklists`
- **AET whitelist:** accepts DIMSE from **`PYMOD1`** (host `*`, port `11112`)

> Orthanc Explorer UI does **not** list MWL. The Worklists plugin is **DIMSE-only**.

---

## Scripts — What they do

### Worklists
- `src/admin/create_wl_file.py`  
  Creates `worklists/ACC1001.wl` with:
  - Patient: `P12345`, `DOE^JANE`, DOB `19800101`, Sex `F`  
  - Requested Proc ID: `RP1001`, Accession: `ACC1001`  
  - SPS: `ScheduledStationAETitle=PYMOD1`, `Modality=CT`, start date/time (now+10m)

- `src/dimse/find_mwl.py` / `find_mwl_verbose.py`  
  Associates as `PYMOD1` and performs **C-FIND** on MWL.  
  Filter: `ScheduledStationAETitle=PYMOD1`. Prints matches (ACC/PID/SPS time).

- `src/admin/list_worklists.py`  
  Local reader for `.wl` files (handy for screenshots/demos).

### Acquisition & Send
- `src/dimse/acquire_from_mwl.py`  
  Reads first `.wl`, populates demographics/proc fields, builds valid **CT Image Storage** (64×64 synthetic pixels).  
  Saves to `data/samples/CT_<PID>_<ACC>.dcm`.

- `src/dimse/send_study.py`  
  Sends a DICOM file to Orthanc via **C-STORE**.

### Admin / Troubleshooting
- `src/dimse/recv_scp.py` — simple **C-STORE SCP** writing to `data/inbox/`  
- `src/admin/push_store.py` — Orthanc-initiated push to your SCP  
- `src/admin/register_modality.py`, `echo_modality.py`, `show_modality_config.py`, `list_modalities.py`, `verify_uid.py`

---

## Install (Python)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt`
```
pydicom
numpy
pynetdicom
requests
```

---

## Troubleshooting

**Orthanc exits with** `A TCP port number must be in range ... found: 0`  
→ Fix `ORTHANC__DICOM_MODALITIES` JSON to use a real port, e.g. `11112`.

**MWL C-FIND “authorization rejected”**  
→ Add AET to Orthanc env and restart:  
`ORTHANC__DICOM_MODALITIES: '{"PYMOD1":["PYMOD1","*",11112]}'`

**MWL returns 0 matches**  
→ Ensure a `.wl` exists in `./worklists` and includes an SPS item with `ScheduledStationAETitle=PYMOD1`.  
Recreate: `python src/admin/create_wl_file.py`  
Re-run: `python src/dimse/find_mwl_verbose.py` (expect `Status: 0xff00` then `Matches: 1`).

**Docker → Windows networking**  
- From container to host, use `host.docker.internal`.  
- Open firewall if you run a local SCP on 11112:  
  `netsh advfirewall firewall add rule name="DICOM-11112" dir=in action=allow protocol=TCP localport=11112`

**Why MWL isn’t visible in the web UI**  
→ The Worklists plugin is **DIMSE-only** (no web listing). Use `src/admin/list_worklists.py` to print `.wl` contents locally.

---

## Security / PHI

- All sample data is synthetic.  
- Runtime paths (`data/inbox/`, generated `.dcm`) are gitignored.  
- Default creds are **orthanc/orthanc** on `http://localhost:8042` (local only).

---

## What this demonstrates (resume bullets)

- Containerized **PACS** with **DICOMweb** + **Worklists**  
- DIMSE clients/servers: **C-FIND (MWL)**, **C-STORE**, echo/register admin  
- Programmatic **DICOM** generation and reconciliation from MWL  
- Practical PACS ops: AET authorization, presentation contexts, Docker config

---

## Roadmap

- MPPS (Performed Procedure Step) simulation  
- C-MOVE end-to-end (Orthanc → local SCP)  
- HL7 v2 (ADT/ORM) + interface-engine style routing  
- DICOMweb (QIDO/WADO/STOW) examples + basic analytics notebooks  
- Routing rules (Orthanc Lua) + anonymization pipelines

---

## License

MIT
