from lxml import etree

def analyze_dm(xml_bytes: bytes) -> dict:
    root = etree.fromstring(xml_bytes)

    ns = {"s": root.nsmap.get(None)}  # default namespace

    # ---- Basic extraction ----
    steps = root.findall(".//s:proceduralStep", namespaces=ns)
    warnings = root.findall(".//s:warning", namespaces=ns)
    cautions = root.findall(".//s:caution", namespaces=ns)
    notes = root.findall(".//s:note", namespaces=ns)

    # ---- Simple heuristics ----
    dm_type_guess = "procedural" if steps else "non-procedural"

    quality_flags = []

    if dm_type_guess == "procedural" and len(steps) == 0:
        quality_flags.append("Procedural DM with no steps")

    if len(steps) > 15:
        quality_flags.append("Large number of steps – consider splitting DM")

    if warnings and not steps:
        quality_flags.append("Warnings present but no procedure")

    return {
        "dm_type_guess": dm_type_guess,
        "counts": {
            "steps": len(steps),
            "warnings": len(warnings),
            "cautions": len(cautions),
            "notes": len(notes)
        },
        "quality_flags": quality_flags
    }
