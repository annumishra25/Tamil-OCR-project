"""
FastAPI Backend Server for Tamil Palm-Leaf Manuscript Digitization Laboratory
Stage 10: Final API Integration

Endpoints:
- POST /api/analyze      (Image quality profiling)
- POST /api/ocr          (Single-line OCR inference)
- POST /api/process      (Full end-to-end folio digitization)
- GET  /api/status       (Hardware & model status)
- GET  /api/metrics      (Quantitative CER/WER metrics)
- GET  /api/experiments  (Full experimental matrix)
"""

import sys
import os
import io
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import torch

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
sys.path.append(str(PROJECT_ROOT))

from src.pipeline import EndToEndPalmLeafPipeline
from src.preprocessing.quality_analysis import analyze_image_quality
from src.evaluation.metrics import calculate_cer, calculate_wer

app = FastAPI(
    title="Tamil Palm-Leaf Manuscript Digitization API",
    description="Backend API for adaptation of TamilCRNN on degraded historical manuscripts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy pipeline singleton
_pipeline_instance: Optional[EndToEndPalmLeafPipeline] = None

def get_pipeline() -> EndToEndPalmLeafPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = EndToEndPalmLeafPipeline()
    return _pipeline_instance


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    """Returns GPU and model runtime status."""
    has_cuda = torch.cuda.is_available()
    return {
        "status": "ONLINE",
        "gpu": {
            "name": torch.cuda.get_device_name(0) if has_cuda else "CPU",
            "cuda_available": has_cuda,
            "cuda_version": torch.version.cuda if has_cuda else "N/A",
            "allocated_vram_mb": round(torch.cuda.memory_allocated() / (1024**2), 2) if has_cuda else 0
        },
        "pipeline": {
            "active_stage": "Stage 10: Final Integration & Evaluation",
            "model_architecture": "TamilCRNN (53.79M Params, ResNet-BiLSTM-CTC)",
            "checkpoint": "models/checkpoints/stage8/best_tamil_crnn.pth",
            "confidence_threshold": 0.85,
            "post_correction": "Conservative Unicode NFC & Combining Mark Attachment"
        }
    }


@app.get("/api/metrics")
def get_metrics() -> Dict[str, Any]:
    """Returns official evaluated CER and WER metrics."""
    metrics_path = PROJECT_ROOT / "results" / "metrics" / "confidence" / "stage9_evaluation_matrix.json"
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"metrics": data}
    return {"status": "NOT_EVALUATED"}


@app.get("/api/experiments")
def get_experiments() -> Dict[str, Any]:
    """Returns final experimental matrix comparison."""
    matrix_path = PROJECT_ROOT / "results" / "metrics" / "final_results.json"
    if matrix_path.exists():
        with open(matrix_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"experiments": data}
    # Fallback to stage 9 evaluation matrix
    stage9_matrix = PROJECT_ROOT / "results" / "metrics" / "confidence" / "stage9_evaluation_matrix.json"
    if stage9_matrix.exists():
        with open(stage9_matrix, "r", encoding="utf-8") as f:
            return {"experiments": json.load(f)}
    return {"experiments": []}


@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Profiles image quality, contrast, sharpness, and illumination uniformity."""
    try:
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        import numpy as np
        img_np = np.array(pil_img)
        quality = analyze_image_quality(img_np)
        return {
            "filename": file.filename,
            "dimensions": {"width": pil_img.width, "height": pil_img.height},
            "quality": quality
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ocr")
async def ocr_single_line(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Performs OCR on a single line crop using SecondPassRouter and TamilPostCorrector."""
    try:
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        pipeline = get_pipeline()
        res = pipeline.router.process_line(pil_img, source_id="API_UPLOAD", line_id="LINE_001")
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process")
async def process_full_folio(
    file: UploadFile = File(...),
    folio_id: str = Form("UPLOADED_FOLIO")
) -> Dict[str, Any]:
    """Executes complete end-to-end digitization on a full palm-leaf folio image."""
    try:
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        pipeline = get_pipeline()
        result = pipeline.process_folio(pil_img, folio_id=folio_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
