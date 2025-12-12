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

@app.post("/scan")
async def scan_product(file: UploadFile = File(...)):
    try:
        # Save the file temporarily
        file_location = f"{UPLOAD_DIR}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Image saved to {file_location}")

        # Extract text and analyze
        extracted_text = scanner.extract_text(file_location)
        analysis_result = scanner.analyze_compliance(extracted_text)
        
        analysis_result["message"] = "Analysis complete."

        return JSONResponse(content=analysis_result)

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run on 0.0.0.0 to be accessible on network (crucial for Pi)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
