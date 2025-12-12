from PIL import Image, ImageDraw, ImageFont
from utils.scanner import scanner
import os

def create_test_image(path):
    # Create a white image
    img = Image.new('RGB', (600, 400), color='white')
    d = ImageDraw.Draw(img)
    
    # Add text simulating a product label with some noise/issues
    text = """
    PREMIUM WHEAT BISCUITS
    
    Manufactured by:
    Golden Foods Pvt Ltd,
    123, Industrial Area, Mumbai, India.
    
    MRP Rs. 50.00 (Incl of all taxes)
    Net Weight: 100 g
    
    Pkd: 12/12/2025
    Use by: 6 months from mfg
    
    For feedback contact:
    care@goldenfoods.com
    Ph: 1800-123-4567
    
    Ingredients: Wheat, Sugar, Edible Oil.
    """
    
    d.text((20, 20), text, fill=(0, 0, 0))
    
    img.save(path)
    print(f"Test image created at {path}")

def test_scanner():
    img_path = "test_product_v2.jpg"
    create_test_image(img_path)
    
    print("Running OCR extraction...")
    text = scanner.extract_text(img_path)
    print(f"Extracted Text:\n{text}")
    
    print("\nAnalyzing Compliance (Metrology Act)...")
    result = scanner.analyze_compliance(text)
    
    print(f"\nStatus: {result['compliance_status']} (Score: {result['compliance_score']}%)")
    print("-" * 30)
    for key, item in result['details'].items():
        status = "[PASS]" if item['found'] else "[FAIL]"
        print(f"{status} {item['label']}: {item['value']}")
    
    # Cleanup
    if os.path.exists(img_path):
        os.remove(img_path)
    if os.path.exists(img_path + "_processed.jpg"):
        os.remove(img_path + "_processed.jpg")

if __name__ == "__main__":
    test_scanner()
