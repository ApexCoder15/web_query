from PIL import Image
import pytesseract
import re

def get_text(img_path):
    # Load image
    image = Image.open(img_path)

    # Extract text
    try:
        text = pytesseract.image_to_string(image)
        return text
    except: 
        return None
    
