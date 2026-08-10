import os
from io import BytesIO
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

def format_ordinal_date(d):
    """
    Formats a datetime.date object into a readable ordinal format.
    """
    day = d.day
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix} {d.strftime('%B, %Y')}"

def generate_payment_receipt_pdf(payment):
    
    # Generates the PDF receipt
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # 1. Header logos and text
    edu_logo_path = os.path.join(settings.MEDIA_ROOT, 'edu_logo.png')
    spoken_logo_path = os.path.join(settings.MEDIA_ROOT, 'spoken_logo.png')
    
    # Left Logo
    if os.path.exists(edu_logo_path):
        p.drawImage(edu_logo_path, 54, 730, width=70, height=70, mask='auto')
    
    # Right Logo
    if os.path.exists(spoken_logo_path):
        p.drawImage(spoken_logo_path, 471.27, 730, width=70, height=70, mask='auto')
        
    # Center Heading Text
    p.setFont("Helvetica-Bold", 15)
    p.setFillColor(colors.HexColor('#1F4E78')) # Deep blue
    p.drawCentredString(297.6, 785, "EduPyramids Educational Services Pvt. Ltd.")
    
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#D9534F')) # Orange/Red
    p.drawCentredString(297.6, 765, "A SINE, IIT Bombay, Incubated Company")
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(297.6, 745, "https://spoken-tutorial.org")
    
    # Text under logos
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(89, 715, "EduPyramids")
    
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#D9534F'))
    p.drawCentredString(506, 718, "Spoken Tutorial")
    p.setFont("Helvetica", 7)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawCentredString(506, 708, "Developed at IIT Bombay")
    
    # 2. Reference Number
    ref_no = f"Ref.No. ST/{payment.payment_date.year}/{10000 + payment.id}"
    p.setFont("Helvetica", 10)
    p.drawString(54, 665, ref_no)
    
    # 3. Title
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(297.6, 625, "ACKNOWLEDGEMENT RECEIPT OF PAYMENT")
    
    # 4. Greetings
    p.setFont("Helvetica", 10)
    p.drawString(54, 585, "Greetings!")
    
    # Styles for body text
    body_style = ParagraphStyle(
        name='ReceiptBody',
        fontName='Helvetica',
        fontSize=10.5,
        leading=16,
        alignment=4 # Justified
    )
    
    # 5. First Paragraph
    p1_text = (
        "We are truly grateful for the prompt payment made to continue the training at your institute. "
        "This indicates a high degree of acceptance of the numerous benefits the Courses introduced by Spoken Tutorial, "
        "EduPyramids, SINE, IIT Bombay are providing to the students. Thank you for the same. Started in 2009, the "
        "Spoken Tutorial was developed at IIT Bombay with funding from the Ministry of Education, Government of "
        "India to spread IT literacy all over India. We are also proud to share that the Spoken Tutorial pedagogy has "
        "recently been approved as an IEEE Global Standard - making it India's first EdTech model to receive such "
        "international recognition."
    )
    p1 = Paragraph(p1_text, body_style)
    _, h1 = p1.wrap(487.27, 200)
    p1.drawOn(p, 54, 570 - h1)
    
    # 6. Payment Paragraph
    try:
        amount_formatted = "{:,}".format(int(payment.amount))
    except (ValueError, TypeError):
        amount_formatted = str(payment.amount)
        
    date_formatted = format_ordinal_date(payment.payment_date)
    
    # Institution location strings
    institution = payment.academic.institution_name
    city = payment.academic.city.name if payment.academic.city else ""
    district = payment.academic.district.name if payment.academic.district else ""
    state = payment.academic.state.name if payment.academic.state else ""
    
    loc_parts = [p for p in [institution, city, district, state] if p]
    location_str = ", ".join(loc_parts)
    
    p2_text = (
        f"Please find the acknowledgement of payment of <b>Rs. {amount_formatted}/-</b> "
        f"made by <b>{location_str}</b> on <b>{date_formatted}</b>."
    )
    p2 = Paragraph(p2_text, body_style)
    _, h2 = p2.wrap(487.27, 100)
    p2.drawOn(p, 54, 435 - h2)
    
    # 7. UTR / Transaction ID
    utr_str = payment.transactionid or "N/A"
    p3_text = f"UTR Number / Transaction ID: <b>{utr_str}</b>"
    p3 = Paragraph(p3_text, body_style)
    _, h3 = p3.wrap(487.27, 50)
    p3.drawOn(p, 54, 380)
    
    # 8. Formal Receipt
    p4_text = "Please treat this as a formal receipt."
    p4 = Paragraph(p4_text, body_style)
    _, h4 = p4.wrap(487.27, 50)
    p4.drawOn(p, 54, 340)
    
    # 9. Signature Header
    footer_img_path = os.path.join(settings.MEDIA_ROOT, 'footer.png')
    if os.path.exists(footer_img_path):
        p.drawImage(footer_img_path, 54, 260, width=160, height=35, mask='auto')
    else:
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(colors.HexColor('#2980B9'))
        p.drawString(54, 280, "For EduPyramids")
        p.setFont("Helvetica", 9)
        p.drawString(54, 265, "Educational Services Pvt. Ltd.")
        
    # Signature
    sig_img_path = os.path.join(settings.MEDIA_ROOT, 'signature.png')
    if os.path.exists(sig_img_path):
        p.drawImage(sig_img_path, 54, 190, width=120, height=45, mask='auto')
        
    # Stamp
    stamp_img_path = os.path.join(settings.MEDIA_ROOT, 'stamp.png')
    if os.path.exists(stamp_img_path):
        p.drawImage(stamp_img_path, 180, 180, width=75, height=75, mask='auto')
        
    # Coordinator Info
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawString(54, 150, "Mrs. Akanksha Saini")
    p.setFont("Helvetica", 9)
    p.drawString(54, 138, "National Coordinator")
    p.drawString(54, 126, "Spoken Tutorial, EduPyramids, SINE, IIT Bombay")
    
    # 10. Footer Branding Line and Text
    p.setStrokeColor(colors.HexColor('#1F4E78'))
    p.setLineWidth(1)
    p.line(54, 65, 541.27, 65)
    
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(297.6, 50, "Spoken Tutorial brought to you by EduPyramids")
    
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawCentredString(297.6, 36, "Seat 60, SINE, RBTIC Building, IIT Bombay, Powai, Mumbai - 400 076")
    p.drawCentredString(297.6, 24, "+ 91 22 25764229")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
