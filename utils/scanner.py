import pytesseract
from PIL import Image
import re
import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class ProductScanner:
    def __init__(self):
        # Check if tesseract is in path
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            logger.warning("Tesseract not found. Please install tesseract-ocr.")
            # Windows fallback (optional, for dev)
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def preprocess_image(self, image_path):
        """
        Advanced preprocessing to improve OCR accuracy for small text on product labels.
        """
        try:
            # Read image using OpenCV
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian Blur to reduce noise
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Adaptive Thresholding (good for varying lighting conditions)
            thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            
            # Save processed image for debugging (optional)
            cv2.imwrite(image_path + "_processed.jpg", denoised)
            
            return denoised
        except Exception as e:
            logger.error(f"Preprocessing Error: {e}")
            return Image.open(image_path) # Fallback to original PIL image

    def extract_text(self, image_path):
        try:
            # Preprocess
            processed_img = self.preprocess_image(image_path)
            
            # Configure Tesseract
            # --oem 3: Default OCR Engine Mode
            # --psm 6: Assume a single uniform block of text (good for labels)
            # --psm 11: Sparse text (good for scattered labels) -> Let's try 3 or 6 first, or 11 if fails
            custom_config = r'--oem 3 --psm 6' 
            
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            return text
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return ""

    def analyze_compliance(self, text):
        """
        Strict Compliance Check based on Legal Metrology Act (Packaged Commodities) Rules, 2011.
        Checks for 7 Mandatory Declarations.
        """
        text_lower = text.lower()
        
        # Initialize Report
        report = {
            "declarations": {
                "manufacturer_details": {"found": False, "value": "Missing", "label": "Name & Address of Mfr/Packer"},
                "common_name": {"found": False, "value": "Missing", "label": "Common/Generic Name"},
                "net_quantity": {"found": False, "value": "Missing", "label": "Net Quantity"},
                "mrp": {"found": False, "value": "Missing", "label": "MRP (Retail Price)"},
                "date_of_mfg": {"found": False, "value": "Missing", "label": "Month & Year of Mfg/Packing"},
                "consumer_care": {"found": False, "value": "Missing", "label": "Consumer Care Details"},
                "country_of_origin": {"found": False, "value": "Missing", "label": "Country of Origin (if imported)"}
            },
            "compliance_score": 0,
            "status": "Non-Compliant",
            "missing_count": 7
        }

        # --- 1. MRP Check ---
        # Look for MRP, Price, Rs., INR followed by digits
        mrp_pattern = r'(mrp|price|rs\.?|inr)\s*[:\-\s]?\s*(\d+(?:[.,]\d{2})?)'
        mrp_match = re.search(mrp_pattern, text_lower)
        if mrp_match:
            report["declarations"]["mrp"] = {"found": True, "value": mrp_match.group(2), "label": "MRP (Retail Price)"}

        # --- 2. Net Quantity Check ---
        # Look for Net Qty, Net Weight, Volume followed by digits and unit (g, kg, ml, l, pc)
        qty_pattern = r'(net\s*(?:qty|quantity|wt|weight|vol|volume)|contents)\s*[:\-\s]?\s*(\d+\s*[.,]?\s*(?:g|kg|ml|l|ltr|pcs|pieces))'
        qty_match = re.search(qty_pattern, text_lower)
        if qty_match:
            report["declarations"]["net_quantity"] = {"found": True, "value": qty_match.group(2), "label": "Net Quantity"}

        # --- 3. Date of Mfg/Packing Check ---
        # Look for Pkd, Mfg, Date, Use By, Exp followed by date format
        date_pattern = r'(pkd|mfg|mfd|packed|manufactured|date|use\s*by|expiry|exp)\s*[:\-\s]?\s*(\d{2}[/\-.]\d{2}[/\-.]\d{2,4}|\d{2}\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{2,4})'
        date_match = re.search(date_pattern, text_lower)
        if date_match:
            report["declarations"]["date_of_mfg"] = {"found": True, "value": date_match.group(2), "label": "Month & Year of Mfg/Packing"}

        # --- 4. Consumer Care Check ---
        # Look for Email, Phone, Customer Care, Feedback, Complaint
        care_pattern = r'(customer\s*care|consumer\s*care|feedback|complaint|contact|email|phone|tel|call)\s*[:\-\s]?'
        # Check for email specifically
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        # Check for phone specifically (India: +91 or 10 digits or 1800)
        phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}|1800[\-\s]?\d{3}[\-\s]?\d{4}'
        
        care_match = re.search(care_pattern, text_lower)
        email_match = re.search(email_pattern, text_lower)
        phone_match = re.search(phone_pattern, text_lower)
        
        if care_match or email_match or phone_match:
            val = ""
            if email_match: val += email_match.group(0) + " "
            if phone_match: val += phone_match.group(0)
            if not val: val = "Details Detected"
            report["declarations"]["consumer_care"] = {"found": True, "value": val, "label": "Consumer Care Details"}

        # --- 5. Manufacturer/Packer Check ---
        # Look for "Manufactured by", "Marketed by", "Packed by", "Mfd by"
        mfr_pattern = r'(manufactured|marketed|packed|mfd|mktd)\s*(?:by|in)?\s*[:\-\s]?\s*([a-z0-9\s,.]+)'
        mfr_match = re.search(mfr_pattern, text_lower)
        if mfr_match:
            # Take first 50 chars as value
            report["declarations"]["manufacturer_details"] = {"found": True, "value": mfr_match.group(2)[:50] + "...", "label": "Name & Address of Mfr/Packer"}

        # --- 6. Country of Origin Check ---
        # Look for "Country of Origin", "Made in", "Origin"
        origin_pattern = r'(country\s*of\s*origin|made\s*in|origin)\s*[:\-\s]?\s*([a-z\s]+)'
        origin_match = re.search(origin_pattern, text_lower)
        if origin_match:
             report["declarations"]["country_of_origin"] = {"found": True, "value": origin_match.group(2), "label": "Country of Origin"}
        else:
            # If "Made in India" is implicitly found via address, we might assume it, but strict check requires explicit declaration for imported.
            # For domestic, it's often part of address. If Mfr address contains "India", we can count it?
            # The Act says "Country of Origin" is mandatory for *imported* packages.
            # However, for consistency, we check if it's declared.
            if "india" in text_lower:
                 report["declarations"]["country_of_origin"] = {"found": True, "value": "India (Inferred)", "label": "Country of Origin"}

        # --- 7. Common/Generic Name Check ---
        # This is hard with Regex. Usually it's the largest text or near "Name of Commodity".
        # We will look for specific keyword "Commodity" or "Product" or "Name"
        name_pattern = r'(commodity|product|item)\s*(?:name)?\s*[:\-\s]?\s*([a-z0-9\s]+)'
        name_match = re.search(name_pattern, text_lower)
        if name_match:
            report["declarations"]["common_name"] = {"found": True, "value": name_match.group(2), "label": "Common/Generic Name"}
        else:
            # Fallback: If we found MRP and Qty, there's likely a product name we missed.
            # We can't easily guess it without an LLM. 
            # For "100% accuracy" request, we mark it missing if not explicit.
            pass

        # Calculate Score
        found_count = sum(1 for k, v in report["declarations"].items() if v["found"])
        report["missing_count"] = 7 - found_count
        report["compliance_score"] = int((found_count / 7) * 100)
        
        if report["compliance_score"] == 100:
            report["status"] = "Fully Compliant"
        elif report["compliance_score"] >= 70:
            report["status"] = "Partially Compliant"
        else:
            report["status"] = "Non-Compliant"

        return {
            "product_name": report["declarations"]["common_name"]["value"] if report["declarations"]["common_name"]["found"] else "Unknown Product",
            "compliance_status": report["status"],
            "compliance_score": report["compliance_score"],
            "details": report["declarations"],
            "message": f"Found {found_count}/7 Mandatory Declarations."
        }

scanner = ProductScanner()
