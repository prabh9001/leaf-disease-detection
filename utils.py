"""
Base64 Image Test for Leaf Disease Detection
===========================================

This script demonstrates how to send base64 image data directly to the detector.
"""

import json
import sys,os
import base64
import datetime
from pathlib import Path

# Add the Leaf Disease directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "Leaf Disease"))

# Detector is imported inside functions to avoid naming collisions at module level


def test_with_base64_data(base64_image_string: str):
    """
    Test disease detection with base64 image data

    Args:
        base64_image_string (str): Base64 encoded image data
    """
    try:
        from leaf_detector import LeafDiseaseDetector
        detector = LeafDiseaseDetector()
        result = detector.analyze_leaf_image_base64(base64_image_string)
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f'{{"error": "{str(e)}"}}')
        return None


def convert_image_to_base64_and_test(image_bytes: bytes):
    """
    Convert image bytes to base64 and test it

    Args:
        image_bytes (bytes): Image data in bytes
    """
    try:
        if not image_bytes:
            print('{"error": "No image bytes provided"}')
            return None

        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        print(f"Converted image to base64 ({len(base64_string)} characters)")
        return test_with_base64_data(base64_string)
    except Exception as e:
        print(f'{{"error": "{str(e)}"}}')
        return None


def create_pdf_report(result: dict, image_bytes: bytes = None):
    """
    Generate a PDF report for the disease analysis.
    """
    from fpdf import FPDF
    import tempfile
    
    def clean_text(text):
        if not text: return ""
        if not isinstance(text, str): text = str(text)
        # Replace common Unicode characters that cause Helvetica/Arial encoding issues
        replacements = {
            '\u2013': '-', # en dash
            '\u2014': '-', # em dash
            '\u2011': '-', # non-breaking hyphen
            '\u2018': "'", # left single quote
            '\u2019': "'", # right single quote
            '\u201c': '"', # left double quote
            '\u201d': '"', # right double quote
            '\u2022': '*', # bullet point
            '\u2122': '(TM)',
            '\u00ae': '(R)',
            '\u00a9': '(C)',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Final pass to ensure it's compatible with latin-1
        return text.encode('latin-1', 'replace').decode('latin-1')

    class PDF(FPDF):
        def header(self):
            # Brand highlight at the top
            self.set_fill_color(22, 101, 52) # Dark Green (#166534)
            self.rect(0, 0, 210, 15, 'F')
            
            self.ln(5)
            try:
                self.set_font('Helvetica', 'B', 20)
                self.set_text_color(22, 101, 52)
            except:
                pass
            self.cell(0, 15, 'Plant Health & Treatment Report', 0, 1, 'C')
            
            # Subtle accent line
            self.set_draw_color(74, 222, 128) # Light Green (#4ade80)
            self.set_line_width(0.5)
            self.line(40, 32, 170, 32)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Page {self.page_no()} | Leaf Disease AI Diagnostic System', 0, 0, 'C')

    # Initialize PDF
    pdf = PDF()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    base_font = "Helvetica"
    effective_width = pdf.w - 2 * 15

    # 1. Image Section
    if image_bytes:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            # Center the image
            img_w = 80
            pdf.image(tmp_path, x=(210-img_w)/2, y=pdf.get_y(), w=img_w)
            os.unlink(tmp_path)
            pdf.ln(65)
        except:
            pdf.ln(5)

    # 2. Plant Summary Section
    pdf.set_fill_color(240, 249, 241) # Very light green bg
    pdf.set_text_color(22, 101, 52)
    pdf.set_font(base_font, 'B', 14)
    pdf.cell(effective_width, 10, "  " + clean_text(f"Plant: {result.get('plant_name', 'Unknown')}"), 0, 1, 'L', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(base_font, 'I', 11)
    pdf.cell(effective_width, 8, clean_text(f"Scientific Name: {result.get('scientific_name', 'N/A')}"), 0, 1)
    pdf.ln(5)

    # 3. Diagnostic Results
    pdf.set_draw_color(220, 220, 220)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font(base_font, 'B', 12)
    pdf.set_text_color(30, 64, 175) # Dark Blue
    status_text = "DISEASE DETECTED" if result.get('disease_detected') else "PLANT IS HEALTHY"
    pdf.cell(effective_width, 10, status_text, 0, 1)
    
    pdf.set_text_color(0, 0, 0)
    if result.get('disease_detected'):
        pdf.set_font(base_font, 'B', 11)
        pdf.cell(40, 8, "Primary Issue:", 0, 0)
        pdf.set_font(base_font, '', 11)
        pdf.cell(0, 8, clean_text(result.get('disease_name', 'N/A')), 0, 1)
        
        pdf.set_font(base_font, 'B', 11)
        pdf.cell(40, 8, "Severity Level:", 0, 0)
        pdf.set_font(base_font, '', 11)
        pdf.cell(0, 8, clean_text(result.get('severity', 'Moderate') or 'Moderate').upper(), 0, 1)
        
        pdf.set_font(base_font, 'B', 11)
        pdf.cell(40, 8, "AI Confidence:", 0, 0)
        pdf.set_font(base_font, '', 11)
        pdf.cell(0, 8, f"{result.get('confidence', 0)}%", 0, 1)

    # 4. Detailed Symptoms
    pdf.ln(5)
    pdf.set_fill_color(248, 250, 252) # Light blue-gray bg
    pdf.set_font(base_font, 'B', 12)
    pdf.cell(effective_width, 10, "  Symptom Analysis", 0, 1, 'L', True)
    pdf.set_font(base_font, '', 10)
    pdf.ln(2)
    for s in result.get('symptoms', []):
        pdf.set_x(20)
        pdf.multi_cell(effective_width-10, 7, clean_text(f"- {s}"))
    
    # 5. Full Treatment Points (Enhanced)
    pdf.ln(5)
    pdf.set_fill_color(255, 247, 237) # Light orange bg
    pdf.set_font(base_font, 'B', 12)
    pdf.cell(effective_width, 10, "  Recommended Treatment & Actions", 0, 1, 'L', True)
    pdf.set_font(base_font, '', 10)
    pdf.ln(2)
    treatment_points = result.get('treatment', [])
    if not treatment_points:
        pdf.set_x(20)
        pdf.multi_cell(effective_width-10, 7, "No specific treatment required. Continue regular care.")
    else:
        for t in treatment_points:
            pdf.set_x(20)
            pdf.multi_cell(effective_width-10, 7, clean_text(f"• {t}"))

    # 6. Personalized Care Calendar
    calendar = result.get('care_calendar', {})
    if calendar:
        pdf.ln(5)
        pdf.set_fill_color(240, 253, 244) # Light green bg
        pdf.set_font(base_font, 'B', 12)
        pdf.cell(effective_width, 10, "  Personalized Ongoing Care Schedule", 0, 1, 'L', True)
        pdf.set_font(base_font, '', 10)
        pdf.ln(2)
        for activity, notes in calendar.items():
            if notes:
                pdf.set_x(20)
                pdf.set_font(base_font, 'B', 10)
                pdf.cell(30, 7, f"{activity.title()}:", 0, 0)
                pdf.set_font(base_font, '', 10)
                pdf.multi_cell(effective_width-40, 7, clean_text(notes))

    # 7. Timestamps
    pdf.ln(10)
    pdf.set_font(base_font, 'I', 8)
    pdf.set_text_color(100, 100, 100)
    timestamp = result.get('analysis_timestamp') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.cell(effective_width, 10, clean_text(f"Report Generated: {timestamp}"), 0, 1, 'R')

    return bytes(pdf.output(dest='S'))

def main():
    """Test with base64 conversion"""
    image_path = "Media/brown-spot-4 (1).jpg"
    convert_image_to_base64_and_test(image_path)


if __name__ == "__main__":
    main()
