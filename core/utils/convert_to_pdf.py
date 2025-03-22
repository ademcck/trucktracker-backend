import os
from glob import glob
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from django.conf import settings
from core.settings.base import BASE_DIR

def convert_svg_to_pdf(output_pdf_name, task_id):
    # Find SVG files ordered as _*page_*1.svg, _*page_*2.svg
    svg_files = sorted(glob(f"{BASE_DIR}/core/utils/temp/{task_id}/_*page_*[0-9].svg"))
    
    if not svg_files:
        print("Hiç SVG dosyası bulunamadı!")
        return
    
    print(f"Bulunan SVG dosyaları: {svg_files}")
    
    # Create path to save PDF file in media/pdf folder
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, 'pdf', output_pdf_name)
    
    # Create media/pdf folder if it does not exist
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
    
    # create Canvas 
    c = canvas.Canvas(pdf_output_path, pagesize=letter)
    
    # Convert every SVG file and add it to PDF
    for svg_file in svg_files:
        try:
            # Convert SVG to ReportLab Graphics object
            drawing = svg2rlg(svg_file)
            
            if drawing:
                # Drawing on Canvas
                drawing.drawOn(c, 0, 0)
                
                # Complete page and add new page
                c.showPage()
                
                # del svg file after converting to SVG 
                os.remove(svg_file)
            else:
                print(f"warning: {svg_file} ")
        except Exception as e:
            print(f"Error: Problem processing {svg_file} - {str(e)}")
    
    # save PDF
    c.save()