from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import shutil
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ClearTag Pi Scanner")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

from utils.scanner import scanner
from utils.camera import camera

@app.post("/scan")
async def scan_product():
    """
    Triggers the Pi Camera to take a picture, then analyzes it.
    """
    try:
        # 1. Capture Image
        logger.info("Starting capture sequence...")
        file_location = camera.capture()
        
        # 2. Extract text and analyze
        logger.info(f"Analyzing {file_location}...")
        extracted_text = scanner.extract_text(file_location)
        analysis_result = scanner.analyze_compliance(extracted_text)
        
        # Add image URL so frontend can display what was captured
        # We need to serve the uploads directory
        filename = os.path.basename(file_location)
        analysis_result["image_url"] = f"/uploads/{filename}"
        analysis_result["message"] = "Scan complete."

        return JSONResponse(content=analysis_result)

    except Exception as e:
        logger.error(f"Error processing scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount uploads to serve captured images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    # Run on 0.0.0.0 to be accessible on network (crucial for Pi)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
