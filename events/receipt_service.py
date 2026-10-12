import os
import re
from io import BytesIO
from datetime import timedelta
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame,
    Spacer, Table, TableStyle, PageBreak, KeepTogether, Image, NextPageTemplate
)

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
    p.setFillColor(colors.HexColor('#0055A5'))
    p.drawCentredString(297.6, 745, "https://spoken-tutorial.org")
    
    
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


def generate_letter_of_association_pdf(payment):
    """
    Generates the official Letter of Association (LOA) PDF for an Academic Center.
    Matches the official EduPyramids / Spoken Tutorial IIT Bombay LOA template.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # 1. Header logos and text
    edu_logo_path = os.path.join(settings.MEDIA_ROOT, 'edu_logo.png')
    spoken_logo_path = os.path.join(settings.MEDIA_ROOT, 'spoken_logo.png')

    if os.path.exists(edu_logo_path):
        p.drawImage(edu_logo_path, 54, 730, width=70, height=70, mask='auto')

    if os.path.exists(spoken_logo_path):
        p.drawImage(spoken_logo_path, 471.27, 730, width=70, height=70, mask='auto')

    p.setFont("Helvetica-Bold", 15)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(297.6, 785, "EduPyramids Educational Services Pvt. Ltd.")

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#D9534F'))
    p.drawCentredString(297.6, 765, "A SINE, IIT Bombay, Incubated Company")

    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor('#0055A5'))
    p.drawCentredString(297.6, 745, "https://spoken-tutorial.org")

    # 2. Reference Number and Date
    ref_no = f"Ref.No. ST/{payment.payment_date.year}/{10000 + payment.id}"
    date_formatted = format_ordinal_date(payment.payment_date)
    date_str = f"Date: - {date_formatted}"

    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawString(54, 695, ref_no)
    p.drawRightString(541.27, 695, date_str)

    # 3. Document Title
    p.setFont("Helvetica-Bold", 13)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(297.6, 660, "LETTER OF ASSOCIATION")

    # 4. Recipient block
    academic = payment.academic
    institution = academic.institution_name
    address = academic.address or ""
    city = academic.city.name if academic.city else ""
    district = academic.district.name if academic.district else ""
    state = academic.state.name if academic.state else ""
    pincode = str(academic.pincode) if academic.pincode else ""

    loc_line = ", ".join([part for part in [city, state] if part])
    if pincode:
        loc_line = f"{loc_line} – {pincode}"

    # Clean up newline and whitespace anomalies from raw database address field
    clean_address = re.sub(r'[\r\n\t]+', ', ', address)
    clean_address = re.sub(r'\s+', ' ', clean_address)
    clean_address = re.sub(r'\s*,\s*', ', ', clean_address)
    clean_address = re.sub(r'(,\s*)+', ', ', clean_address).strip(', ')
    if institution and clean_address.lower().startswith(institution.lower()):
        clean_address = clean_address[len(institution):].strip(', ')
    clean_address = re.sub(r'^(,\s*)+', '', clean_address).strip(', ')

    recipient_style = ParagraphStyle(
        name='LOARecipient',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#000000')
    )

    recipient_lines = ["To,", "The Principal,", f"<b>{institution}</b>,"]
    if clean_address:
        recipient_lines.append(f"{clean_address},")
    if loc_line:
        recipient_lines.append(f"{loc_line}.")

    recipient_html = "<br/>".join(recipient_lines)
    recipient_p = Paragraph(recipient_html, recipient_style)
    _, rec_height = recipient_p.wrap(487.27, 200)

    y = 625
    recipient_p.drawOn(p, 54, y - rec_height)
    y = y - rec_height - 12

    # Styles for body text
    body_style = ParagraphStyle(
        name='LOABody',
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        alignment=4  # Justified
    )

    # 5. First Paragraph (Association Announcement & IEEE Standard)
    p1_text = (
        f"We are happy to announce the <b>ASSOCIATION</b> of Knowledge Partner <b>Spoken Tutorial, "
        f"EduPyramids, SINE, IIT Bombay</b> with <b>{institution}</b>. Your institute is now officially "
        f"an <b>Academic Partner</b>. Started in 2009, the Spoken Tutorial was developed at IIT Bombay "
        f"with funding from the Ministry of Education, Government of India to spread IT literacy all "
        f"over India. We promote the learning and usage of Free & Open-Source Software (FOSS) through an "
        f"Audio-Video teaching tool, viz, 'Spoken Tutorial'. We are also proud to share that the Spoken "
        f"Tutorial pedagogy has recently been approved as an IEEE Global Standard - making it India's first "
        f"EdTech model to receive such international recognition."
    )
    p1 = Paragraph(p1_text, body_style)
    _, h1 = p1.wrap(487.27, 200)
    p1.drawOn(p, 54, y - h1)
    y = y - h1 - 12

    # 6. Second Paragraph (Validity & Fee)
    try:
        amount_formatted = "{:,}".format(int(payment.amount))
    except (ValueError, TypeError):
        amount_formatted = str(payment.amount)

    sub_days = int(payment.subscription) if payment.subscription and str(payment.subscription).isdigit() else 365
    expiry_date = payment.payment_date + timedelta(days=sub_days)
    expiry_formatted = format_ordinal_date(expiry_date)

    p2_text = (
        f"We support and motivate institutes to train students in Basic Computer, Software and IT Skills. "
        f"The course and the training are offered for <b>Rs. {amount_formatted}/-</b>. This letter is issued for "
        f"a period of one year, from <b>{date_formatted}</b> to <b>{expiry_formatted}</b>, to <b>{institution}</b>."
    )
    p2 = Paragraph(p2_text, body_style)
    _, h2 = p2.wrap(487.27, 100)
    p2.drawOn(p, 54, y - h2)
    y = y - h2 - 12

    # 7. Third Paragraph (Enrolment & ICT Contribution)
    p3_text = (
        "Looking forward to many enrolments from the institute. You are making an outstanding contribution "
        "to using ICT-based teaching and learning methodology for students of your institute."
    )
    p3 = Paragraph(p3_text, body_style)
    _, h3 = p3.wrap(487.27, 100)
    p3.drawOn(p, 54, y - h3)

    # 8. Signature Block
    footer_img_path = os.path.join(settings.MEDIA_ROOT, 'footer.png')
    if os.path.exists(footer_img_path):
        p.drawImage(footer_img_path, 54, 250, width=160, height=35, mask='auto')
    else:
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(colors.HexColor('#2980B9'))
        p.drawString(54, 265, "For EduPyramids")
        p.setFont("Helvetica", 9)
        p.drawString(54, 252, "Educational Services Pvt. Ltd.")

    sig_img_path = os.path.join(settings.MEDIA_ROOT, 'signature.png')
    if os.path.exists(sig_img_path):
        p.drawImage(sig_img_path, 54, 180, width=120, height=45, mask='auto')

    stamp_img_path = os.path.join(settings.MEDIA_ROOT, 'stamp.png')
    if os.path.exists(stamp_img_path):
        p.drawImage(stamp_img_path, 180, 170, width=75, height=75, mask='auto')

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawString(54, 140, "Mrs. Akanksha Saini")
    p.setFont("Helvetica", 9)
    p.drawString(54, 128, "National Coordinator")
    p.drawString(54, 116, "Spoken Tutorial, EduPyramids, SINE, IIT Bombay")

    # 9. Footer Branding Line and Address
    p.setStrokeColor(colors.HexColor('#1F4E78'))
    p.setLineWidth(1)
    p.line(54, 65, 541.27, 65)

    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(297.6, 50, "Spoken Tutorial brought to you by EduPyramids")

    p.setFont("Helvetica", 8)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawCentredString(297.6, 36, "6016 A, SINE, RBTIC Building IIT Bombay, Powai, Mumbai 400 076")
    p.drawCentredString(297.6, 24, "+91 22-25764229 | contact@edupyramids.org | GSTIN: 27AAICE5225E1ZT | CIN: U85499MH2024PTC435910")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


def generate_letter_of_completion_pdf(payment):
    """
    Generates an Annual Report / Certificate of Training (LOC) PDF for an AcademicCenter's subscription year.
    Lists all workshops/trainings completed during that subscription period.
    """
    from events.models import TrainingRequest
    from django.db.models import Sum

    buffer = BytesIO()
    PAGE_WIDTH, PAGE_HEIGHT = A4
    margin = 54
    printable_width = PAGE_WIDTH - 2 * margin

    start_date = payment.payment_date
    sub_days = int(payment.subscription) if payment.subscription and str(payment.subscription).isdigit() else 365
    end_date = start_date + timedelta(days=sub_days)
    academic_session = f"{start_date.year}-{end_date.year}" if start_date.year != end_date.year else f"{start_date.year}"
    ref_no = f"Ref.No. ST/{end_date.year}/{10000 + payment.id}"
    date_str = f"Date: - {end_date.strftime('%d/%m/%Y')}"

    # Query completed trainings in that period
    trainings = TrainingRequest.objects.filter(
        training_planner__academic_id=payment.academic_id,
        sem_start_date__gte=start_date,
        sem_start_date__lte=end_date,
        participants__gt=0
    ).select_related('department', 'course__foss').order_by('department__name', 'course__foss__foss')

    total_workshops = trainings.count()
    total_participants = trainings.aggregate(Sum('participants'))['participants__sum'] or 0

    def draw_footer(canvas):
        canvas.setStrokeColor(colors.HexColor('#1F4E78'))
        canvas.setLineWidth(1)
        canvas.line(margin, 65, PAGE_WIDTH - margin, 65)

        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(colors.HexColor('#1F4E78'))
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 50, "Spoken Tutorial brought to you by EduPyramids")

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor('#000000'))
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 36, "6016 A, SINE, RBTIC Building IIT Bombay, Powai, Mumbai 400 076")
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 24, "+91 22-25764229 | contact@edupyramids.org | GSTIN: 27AAICE5225E1ZT | CIN: U85499MH2024PTC435910")

    def draw_header_footer_p1(canvas, doc):
        canvas.saveState()
        edu_logo_path = os.path.join(settings.MEDIA_ROOT, 'edu_logo.png')
        spoken_logo_path = os.path.join(settings.MEDIA_ROOT, 'spoken_logo.png')

        if os.path.exists(edu_logo_path):
            canvas.drawImage(edu_logo_path, 54, 730, width=70, height=70, mask='auto')

        if os.path.exists(spoken_logo_path):
            canvas.drawImage(spoken_logo_path, 471.27, 730, width=70, height=70, mask='auto')

        canvas.setFont("Helvetica-Bold", 15)
        canvas.setFillColor(colors.HexColor('#1F4E78'))
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 785, "EduPyramids Educational Services Pvt. Ltd.")

        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(colors.HexColor('#D9534F'))
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 765, "A SINE, IIT Bombay, Incubated Company")

        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.HexColor('#0055A5'))
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 745, "https://spoken-tutorial.org")

        draw_footer(canvas)
        canvas.restoreState()

    def draw_header_footer_later(canvas, doc):
        canvas.saveState()
        draw_footer(canvas)
        canvas.restoreState()

    frame_p1 = Frame(margin, 75, printable_width, PAGE_HEIGHT - 75 - 110, id='frame_p1',
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_later = Frame(margin, 75, printable_width, PAGE_HEIGHT - 75 - 54, id='frame_later',
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    template_p1 = PageTemplate(id='FirstPage', frames=frame_p1, onPage=draw_header_footer_p1)
    template_later = PageTemplate(id='LaterPage', frames=frame_later, onPage=draw_header_footer_later)

    doc = BaseDocTemplate(buffer, pagesize=A4, pageTemplates=[template_p1, template_later])

    # Paragraph Styles
    ref_style = ParagraphStyle('LOCRef', fontName='Helvetica', fontSize=9.5, leading=12)
    date_style = ParagraphStyle('LOCDate', fontName='Helvetica', fontSize=9.5, leading=12, alignment=TA_RIGHT)
    title_style = ParagraphStyle('LOCTitle', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor('#1F4E78'), alignment=TA_CENTER)
    recipient_style = ParagraphStyle('LOCRecipient', fontName='Helvetica', fontSize=9.5, leading=13.5)
    subject_style = ParagraphStyle('LOCSubject', fontName='Helvetica-Bold', fontSize=9.5, leading=13.5)
    body_style = ParagraphStyle('LOCBody', fontName='Helvetica', fontSize=9, leading=13.5, alignment=TA_JUSTIFY)

    kpi_label_style = ParagraphStyle('LOCKPILabel', fontName='Helvetica-Bold', fontSize=9.5, leading=13)
    kpi_val_style = ParagraphStyle('LOCKPIVal', fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=TA_CENTER)

    story = []

    # 1. Ref & Date table
    ref_table = Table([[Paragraph(ref_no, ref_style), Paragraph(date_str, date_style)]], colWidths=[240, printable_width - 240])
    ref_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 10))

    # 2. Document Title
    story.append(Paragraph("CERTIFICATE OF TRAINING", title_style))
    story.append(Spacer(1, 10))

    # 3. Recipient Address
    academic = payment.academic
    institution = academic.institution_name
    address = academic.address or ""
    city = academic.city.name if academic.city else ""
    state = academic.state.name if academic.state else ""
    pincode = str(academic.pincode) if academic.pincode else ""

    loc_line = ", ".join([part for part in [city, state] if part])
    if pincode:
        loc_line = f"{loc_line} - {pincode}"

    recipient_text = f"To,<br/>The Principal,<br/><b>{institution}</b>,<br/>"
    if address:
        recipient_text += f"{address},<br/>"
    if loc_line:
        recipient_text += f"{loc_line}."
    story.append(Paragraph(recipient_text, recipient_style))
    story.append(Spacer(1, 8))

    # 4. Subject Line
    subject_text = f"Subject - Status of Training done in collaboration with Spoken Tutorial, EduPyramids, SINE, IIT Bombay ({academic_session})"
    story.append(Paragraph(subject_text, subject_style))
    story.append(Spacer(1, 8))

    # 5. Body Paragraphs
    p1_text = (
        f"This is as per the agreement between <b>{institution}</b>, and the Spoken Tutorial, "
        f"EduPyramids, SINE, IIT Bombay. Started in 2009, the Spoken Tutorial was developed at "
        f"IIT Bombay with funding from the Ministry of Education, Government of India was to promote "
        f"IT literacy through Open-Source Software. We are also proud to share that the Spoken "
        f"Tutorial pedagogy has recently been approved as an IEEE Global Standard - making it India’s "
        f"first EdTech model to receive such international recognition."
    )
    story.append(Paragraph(p1_text, body_style))
    story.append(Spacer(1, 6))

    p2_text = (
        f"The students of <b>{institution}</b>, have enrolled in various FOSS (Free and Open-Source Software) "
        f"developed and certified by Spoken Tutorial, EduPyramids, SINE, IIT Bombay during the academic session "
        f"{academic_session}."
    )
    story.append(Paragraph(p2_text, body_style))
    story.append(Spacer(1, 6))

    p3_text = f"Details of students enrolled in various FOSS during academic session {academic_session}."
    story.append(Paragraph(p3_text, body_style))
    story.append(Spacer(1, 8))

    # 6. KPI Summary Table
    kpi_data = [
        [Paragraph("Total Number of Workshop / Training", kpi_label_style), Paragraph(str(total_workshops), kpi_val_style)],
        [Paragraph("Total Participants Count", kpi_label_style), Paragraph(str(total_participants), kpi_val_style)]
    ]
    kpi_table = Table(kpi_data, colWidths=[340, printable_width - 340])
    kpi_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1F4E78')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9FA')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    # 7. Signature Block
    footer_img_path = os.path.join(settings.MEDIA_ROOT, 'footer.png')
    sig_img_path = os.path.join(settings.MEDIA_ROOT, 'signature.png')
    stamp_img_path = os.path.join(settings.MEDIA_ROOT, 'stamp.png')

    sig_elements = []
    sig_company_style = ParagraphStyle('LOCSigCo', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#1F4E78'))
    sig_name_style = ParagraphStyle('LOCSigName', fontName='Helvetica-Bold', fontSize=9.5, leading=13)
    sig_title_style = ParagraphStyle('LOCSigTitle', fontName='Helvetica', fontSize=8.5, leading=12)

    if os.path.exists(footer_img_path):
        sig_elements.append(Image(footer_img_path, width=150, height=33))
        sig_elements.append(Spacer(1, 4))
    else:
        sig_elements.append(Paragraph("<b>For EduPyramids Educational Services Pvt. Ltd.</b>", sig_company_style))
        sig_elements.append(Spacer(1, 6))

    has_sig = os.path.exists(sig_img_path)
    has_stamp = os.path.exists(stamp_img_path)

    if has_sig or has_stamp:
        sig_cell = Image(sig_img_path, width=100, height=38) if has_sig else Paragraph("", body_style)
        stamp_cell = Image(stamp_img_path, width=60, height=60) if has_stamp else Paragraph("", body_style)
        sig_tbl = Table([[sig_cell, stamp_cell]], colWidths=[110, 80])
        sig_tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        sig_elements.append(sig_tbl)
        sig_elements.append(Spacer(1, 4))
    else:
        sig_elements.append(Spacer(1, 20))

    sig_elements.append(Paragraph("<b>Mrs. Akanksha Saini</b>", sig_name_style))
    sig_elements.append(Paragraph("National Coordinator", sig_title_style))
    sig_elements.append(Paragraph("Spoken Tutorial, EduPyramids, SINE, IIT Bombay", sig_title_style))

    story.append(KeepTogether(sig_elements))

    # Switch template and move to Page 2
    story.append(NextPageTemplate('LaterPage'))
    story.append(PageBreak())

    # --- Page 2+: Training breakdown table ---
    story.append(ref_table)
    story.append(Spacer(1, 10))

    th_center = ParagraphStyle('LOCTHC', fontName='Helvetica-Bold', fontSize=9, leading=11, alignment=TA_CENTER, textColor=colors.white)
    th_left = ParagraphStyle('LOCTHL', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)
    th_right = ParagraphStyle('LOCTHR', fontName='Helvetica-Bold', fontSize=9, leading=11, alignment=TA_RIGHT, textColor=colors.white)

    td_center = ParagraphStyle('LOCTDC', fontName='Helvetica', fontSize=8.5, leading=11, alignment=TA_CENTER)
    td_left = ParagraphStyle('LOCTDL', fontName='Helvetica', fontSize=8.5, leading=11)
    td_right = ParagraphStyle('LOCTDR', fontName='Helvetica', fontSize=8.5, leading=11, alignment=TA_RIGHT)

    table_data = [[
        Paragraph("<b>Sr. No</b>", th_center),
        Paragraph("<b>Department</b>", th_left),
        Paragraph("<b>FOSS</b>", th_left),
        Paragraph("<b>Participants</b>", th_right)
    ]]

    if trainings.exists():
        for idx, tr in enumerate(trainings, 1):
            dept_name = tr.department.name if tr.department else ""
            foss_name = tr.course.foss.foss if (tr.course and tr.course.foss) else ""
            table_data.append([
                Paragraph(str(idx), td_center),
                Paragraph(dept_name, td_left),
                Paragraph(foss_name, td_left),
                Paragraph(str(tr.participants), td_right)
            ])
    else:
        table_data.append([
            Paragraph("-", td_center),
            Paragraph("No completed training records found for this subscription period.", td_left),
            Paragraph("-", td_left),
            Paragraph("0", td_right)
        ])

    detail_table = Table(table_data, colWidths=[45, 215, 145, printable_width - 45 - 215 - 145], repeatRows=1)
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F4E78')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
    ]
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#F8F9FA')))
    detail_table.setStyle(TableStyle(t_style))

    story.append(detail_table)

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_letter_of_appreciation_pdf(payment, organiser=None):
    """
    Generates the official Letter of Appreciation PDF for a Faculty / Organiser.
    Matches the official EduPyramids / Spoken Tutorial IIT Bombay template.
    Issued with the 1-year completion rule acknowledging the faculty coordinator's contributions.
    """
    from events.models import Organiser

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # 1. Header logos and text
    edu_logo_path = os.path.join(settings.MEDIA_ROOT, 'edu_logo.png')
    spoken_logo_path = os.path.join(settings.MEDIA_ROOT, 'spoken_logo.png')

    if os.path.exists(edu_logo_path):
        p.drawImage(edu_logo_path, 54, 730, width=70, height=70, mask='auto')

    if os.path.exists(spoken_logo_path):
        p.drawImage(spoken_logo_path, 471.27, 730, width=70, height=70, mask='auto')

    p.setFont("Helvetica-Bold", 15)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(297.6, 785, "EduPyramids Educational Services Pvt. Ltd.")

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#D9534F'))
    p.drawCentredString(297.6, 765, "A SINE, IIT Bombay, Incubated Company")

    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor('#0055A5'))
    p.drawCentredString(297.6, 745, "https://spoken-tutorial.org")

    # 2. Reference Number and Date
    sub_days = int(payment.subscription) if payment.subscription and str(payment.subscription).isdigit() else 365
    issue_date = payment.payment_date + timedelta(days=sub_days)
    ref_no = f"Ref.No. ST/{payment.payment_date.year}/APP-{payment.id}"
    date_formatted = format_ordinal_date(issue_date)
    date_str = f"Date: - {date_formatted}"

    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawString(54, 695, ref_no)
    p.drawRightString(541.27, 695, date_str)

    # 3. Document Title
    p.setFont("Helvetica-Bold", 13)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(297.6, 660, "LETTER OF APPRECIATION")

    # 4. Resolve Faculty / Organiser recipient
    faculty_name = "Faculty Coordinator"
    if organiser and hasattr(organiser, 'user'):
        full_name = f"{organiser.user.first_name} {organiser.user.last_name}".strip()
        faculty_name = full_name if full_name else organiser.user.username
    else:
        org = Organiser.objects.filter(academic=payment.academic).first()
        if org and hasattr(org, 'user'):
            full_name = f"{org.user.first_name} {org.user.last_name}".strip()
            faculty_name = full_name if full_name else org.user.username
        elif payment.name_of_the_payer:
            faculty_name = payment.name_of_the_payer

    academic = payment.academic
    institution = academic.institution_name
    state = academic.state.name if academic.state else (payment.state.name if payment.state else "")
    acad_year = f"{payment.payment_date.year}-{str(payment.payment_date.year + 1)[-2:]}"

    # Recipient block
    recipient_style = ParagraphStyle(
        name='ApprRecipient',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#000000')
    )

    recipient_lines = ["To,", f"<b>{faculty_name}</b>,", f"{institution},"]
    if state:
        recipient_lines.append(f"{state}.")
    recipient_html = "<br/>".join(recipient_lines)
    recipient_p = Paragraph(recipient_html, recipient_style)
    _, rec_height = recipient_p.wrap(487.27, 200)

    y = 625
    recipient_p.drawOn(p, 54, y - rec_height)
    y = y - rec_height - 14

    body_style = ParagraphStyle(
        name='AppreciationBody',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        alignment=4  # Justified
    )

    # 5. Body Paragraphs
    p1_text = (
        f"We express our thanks and appreciation to <b>{faculty_name}</b> for spreading awareness and holding workshops "
        f"introduced by Spoken Tutorial, EduPyramids, SINE, IIT Bombay at <b>{institution}</b>, <b>{state}</b>, "
        f"for the academic year <b>{acad_year}</b>. Started in 2009, the Spoken Tutorial was developed at IIT Bombay "
        f"with funding from the Ministry of Education, Government of India to spread IT literacy all over India. "
        f"We are also proud to share that the Spoken Tutorial pedagogy has recently been approved as an IEEE Global Standard "
        f"- making it India’s first EdTech model to receive such international recognition."
    )
    p1 = Paragraph(p1_text, body_style)
    _, h1 = p1.wrap(487.27, 200)
    p1.drawOn(p, 54, y - h1)
    y = y - h1 - 10

    p2_text = (
        f"You are making an outstanding contribution by using ICT-based teaching and learning methodology for "
        f"students and the faculties of <b>{institution}</b>, <b>{state}</b>. Your contribution to the implementation "
        f"of our software training in association with Spoken Tutorial, EduPyramids, SINE, IIT Bombay was significant "
        f"and has played a part in it becoming the fastest-growing company. Your excellent skills and courteous attitude "
        f"have helped tremendously, in spreading awareness of our software training."
    )
    p2 = Paragraph(p2_text, body_style)
    _, h2 = p2.wrap(487.27, 200)
    p2.drawOn(p, 54, y - h2)
    y = y - h2 - 10

    p3_text = "I like to thank you for contributing to the software training and awareness events at your institute."
    p3 = Paragraph(p3_text, body_style)
    _, h3 = p3.wrap(487.27, 100)
    p3.drawOn(p, 54, y - h3)
    y = y - h3 - 10

    p4_text = f"I am confident that we will continue to receive your support in making India IT-literate by expanding the company’s presence in <b>{state}</b>."
    p4 = Paragraph(p4_text, body_style)
    _, h4 = p4.wrap(487.27, 100)
    p4.drawOn(p, 54, y - h4)

    # 6. Signature Block
    footer_img_path = os.path.join(settings.MEDIA_ROOT, 'footer.png')
    if os.path.exists(footer_img_path):
        p.drawImage(footer_img_path, 54, 215, width=160, height=35, mask='auto')

    sig_img_path = os.path.join(settings.MEDIA_ROOT, 'signature.png')
    if os.path.exists(sig_img_path):
        p.drawImage(sig_img_path, 54, 145, width=120, height=45, mask='auto')

    stamp_img_path = os.path.join(settings.MEDIA_ROOT, 'stamp.png')
    if os.path.exists(stamp_img_path):
        p.drawImage(stamp_img_path, 180, 135, width=75, height=75, mask='auto')

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawString(54, 105, "Mrs. Akanksha Saini")
    p.setFont("Helvetica", 9)
    p.drawString(54, 93, "National Coordinator")
    p.drawString(54, 81, "Spoken Tutorial, EduPyramids, SINE, IIT Bombay")

    # 7. Footer Branding Line and Address
    p.setStrokeColor(colors.HexColor('#1F4E78'))
    p.setLineWidth(1)
    p.line(54, 65, 541.27, 65)

    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.HexColor('#1F4E78'))
    p.drawCentredString(297.6, 50, "Spoken Tutorial brought to you by EduPyramids")

    p.setFont("Helvetica", 8)
    p.setFillColor(colors.HexColor('#000000'))
    p.drawCentredString(297.6, 36, "6016 A, SINE, RBTIC Building IIT Bombay, Powai, Mumbai 400 076")
    p.drawCentredString(297.6, 24, "+91 22-25764229 | contact@edupyramids.org | GSTIN: 27AAICE5225E1ZT | CIN: U85499MH2024PTC435910")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


