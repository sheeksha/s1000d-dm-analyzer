from fastapi import FastAPI, UploadFile, File
from analyser import analyze_dm

app = FastAPI(title="S1000D DM Analyzer")

@app.post("/analyze-dm")
async def analyze_dm_endpoint(file: UploadFile = File(...)):
    xml_bytes = await file.read()
    result = analyze_dm(xml_bytes)
    return result
