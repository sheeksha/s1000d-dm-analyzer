from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from lxml import etree

app = FastAPI(title="S1000D DM Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", 
                   "http://127.0.0.1:5173",
                   "https://s1000d-dm-analyzer.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def _get_text_first(root, xpath: str, ns: dict) -> str | None:
    el = root.find(xpath, namespaces=ns) if ns else root.find(xpath)
    if el is None:
        return None
    # join all text inside the element
    text = " ".join("".join(el.itertext()).split())
    return text or None

def _count(root, xpath: str, ns: dict) -> int:
    return len(root.findall(xpath, namespaces=ns)) if ns else len(root.findall(xpath))

def _detect_category(root, ns: dict) -> str:
    # order matters: pick the most specific first
    if (root.find(".//s:partsData", namespaces=ns) if ns else root.find(".//partsData")) is not None:
        return "parts"
    if (root.find(".//s:faultIsolation", namespaces=ns) if ns else root.find(".//faultIsolation")) is not None:
        return "fault"
    if (root.find(".//s:procedure", namespaces=ns) if ns else root.find(".//procedure")) is not None:
        return "procedure"
    if (root.find(".//s:description", namespaces=ns) if ns else root.find(".//description")) is not None:
        return "description"
    return "unknown"

@app.post("/analyze-dm")
async def analyze_dm(file: UploadFile = File(...)):
    xml_bytes = await file.read()

    try:
        root = etree.fromstring(xml_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {str(e)}")

    default_ns = root.nsmap.get(None)
    ns = {"s": default_ns} if default_ns else {}

    # ---- Extract metadata if present (fake files may include these) ----
    dm_title = _get_text_first(root, ".//s:dmTitle", ns) if ns else _get_text_first(root, ".//dmTitle", ns)
    dm_code  = _get_text_first(root, ".//s:dmCode", ns) if ns else _get_text_first(root, ".//dmCode", ns)

    # ---- Core counts ----
    steps    = _count(root, ".//s:proceduralStep", ns) if ns else _count(root, ".//proceduralStep", ns)
    warnings = _count(root, ".//s:warning", ns) if ns else _count(root, ".//warning", ns)
    cautions = _count(root, ".//s:caution", ns) if ns else _count(root, ".//caution", ns)
    notes    = _count(root, ".//s:note", ns) if ns else _count(root, ".//note", ns)

    category = _detect_category(root, ns)

    # ---- Quality flags (simple, useful, explainable) ----
    flags = []

    if category == "procedure" and steps == 0:
        flags.append("Procedure found but no proceduralStep elements")

    if steps > 20:
        flags.append("Procedure has more than 20 steps (consider splitting)")

    if warnings + cautions > 0 and category != "procedure":
        flags.append("Safety messages found but DM is not a procedure (check structure/placement)")

    if category == "parts" and steps > 0:
        flags.append("proceduralStep found inside parts DM (mixed intent)")

    if dm_title is None:
        flags.append("dmTitle not found (metadata missing in sample)")

    return {
        "filename": file.filename,
        "category": category,
        "metadata": {
            "dmCode": dm_code,
            "dmTitle": dm_title
        },
        "counts": {
            "steps": steps,
            "warnings": warnings,
            "cautions": cautions,
            "notes": notes
        },
        "quality_flags": flags
    }
