import pytesseract
from PIL import Image
import re
import logging

logger = logging.getLogger(__name__)

class ProductScanner:
    def __init__(self):
        # Check if tesseract is in path (simple check)
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            logger.warning("Tesseract not found. Please install tesseract-ocr.")
            # On Windows, you might need to set the path explicitly if not in PATH
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def extract_text(self, image_path):
        try:
            image = Image.open(image_path)
            # Simple preprocessing could go here (grayscale, threshold)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return ""

    def analyze_compliance(self, text):
        """
        Simulates LLM extraction and compliance checking using Regex/Logic
        to ensure speed on Raspberry Pi.
        """
        compliance_report = {
            "mrp": {"found": False, "value": None},
            "expiry": {"found": False, "value": None},
            "fssai": {"found": False, "value": None},
            "net_qty": {"found": False, "value": None},
            "ingredients": {"found": False, "value": None}
        }

        # Normalize text
        text_lower = text.lower()

        # Check for MRP
        mrp_match = re.search(r'(mrp|price|rs\.?)\s*[:\-\s]?\s*(\d+(?:\.\d{2})?)', text_lower)
        if mrp_match:
            compliance_report["mrp"] = {"found": True, "value": mrp_match.group(2)}

        # Check for Expiry/Best Before
        expiry_match = re.search(r'(expiry|exp|best before|use by)\s*[:\-\s]?\s*(\d{2}[/\-]\d{2}[/\-]\d{2,4})', text_lower)
        if expiry_match:
            compliance_report["expiry"] = {"found": True, "value": expiry_match.group(2)}

        # Check for FSSAI
        fssai_match = re.search(r'fssai\s*[:\-\s]?\s*(\d{14})', text_lower)
        if fssai_match:
            compliance_report["fssai"] = {"found": True, "value": fssai_match.group(1)}

        # Check for Net Quantity
        qty_match = re.search(r'(net\s*qty|net\s*quantity|weight)\s*[:\-\s]?\s*(\d+\s*(?:g|kg|ml|l))', text_lower)
        if qty_match:
            compliance_report["net_qty"] = {"found": True, "value": qty_match.group(2)}
            
        # Check for Ingredients
        if "ingredients" in text_lower:
             compliance_report["ingredients"] = {"found": True, "value": "List Detected"}

        # Determine overall status
        missing_fields = [k for k, v in compliance_report.items() if not v["found"]]
        status = "Compliant" if not missing_fields else "Non-Compliant"
        
        return {
            "product_name": "Scanned Product", # Placeholder
            "compliance_status": status,
            "details": {k: v["value"] if v["found"] else "Missing" for k, v in compliance_report.items()},
            "raw_text": text[:100] + "..." # Preview
        }

scanner = ProductScanner()
