import os
from datetime import datetime
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image


def _try_parse_amount(value, default=30000):
    if not value:
        return default
    # Strip non-digits
    digits = ''.join(ch for ch in str(value) if ch.isdigit())
    try:
        return int(digits) if digits else default
    except Exception:
        return default


def generate_invoice_for_booking(booking, items=None, payment_info=None, notes=None):
    """
    Generate a detailed A4 PDF invoice for a Booking instance and return the file path.

    - `items`: optional list of dicts {desc, qty, unit} to override defaults.
    - `payment_info`: optional dict with transaction_id, method, date, status, amount_paid
    - `notes`: optional string for terms/cancellation policy
    """
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)

    filename = f"invoice_booking_{booking.id}.pdf"
    file_path = os.path.join(invoices_dir, filename)

    # Default items if none provided
    if items is None:
        per_person_price = _try_parse_amount(getattr(booking, 'budget_range', None), default=30000)
        items = [
            {'desc': 'Travel Package (per person)', 'qty': booking.num_travelers or 1, 'unit': per_person_price},
            {'desc': 'Hotel', 'qty': 1, 'unit': 9000},
            {'desc': 'Transportation', 'qty': 1, 'unit': 5000},
        ]

    # Compute totals
    for it in items:
        it['qty'] = int(it.get('qty', 1))
        it['unit'] = int(it.get('unit', 0))
        it['total'] = it['qty'] * it['unit']

    subtotal = sum(it['total'] for it in items)
    tax = int(subtotal * 0.05)  # 5% tax default
    discount = int(payment_info.get('discount', 0)) if payment_info and payment_info.get('discount') else 0
    grand_total = subtotal + tax - discount
    amount_paid = int(payment_info.get('amount_paid', 0)) if payment_info else 0
    balance = grand_total - amount_paid

    # Document
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = ParagraphStyle('heading', parent=styles['Heading2'], alignment=0, fontSize=14)

    story = []

    # Header
    story.append(Paragraph('VOYAGE Travel Agency', ParagraphStyle('title', parent=styles['Title'], fontSize=18)))
    story.append(Paragraph('GST: ________ | Phone: +91 XXXXX XXXXX | Email: support@agency.com | website: example.com', normal))
    story.append(Spacer(1, 6))
    story.append(Paragraph('<b>INVOICE</b>', heading))
    story.append(Spacer(1, 8))

    # Invoice info table (two columns)
    invoice_no = f"INV-{booking.id:06d}"
    invoice_date = datetime.utcnow().strftime('%Y-%m-%d')
    payment_status = payment_info.get('status', 'Pending') if payment_info else 'Pending'
    payment_method = payment_info.get('method', 'N/A') if payment_info else 'N/A'

    info_data = [
        ['Invoice No:', invoice_no, 'Invoice Date:', invoice_date],
        ['Booking ID:', str(booking.id), 'Payment Status:', payment_status],
        ['Payment Method:', payment_method, '', ''],
    ]
    t = Table(info_data, colWidths=[40 * mm, 60 * mm, 40 * mm, 60 * mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Customer & Trip details
    cust_data = [
        ['Customer Details', 'Trip Details'],
        [f"Name: {booking.full_name}\nEmail: {booking.email}\nPhone: {booking.phone}\nAddress: {'N/A'}",
         f"Destination: {booking.destination_name or (booking.destination.name if booking.destination else '')}\nPackage: {'Standard'}\nDeparture: {booking.travel_date or ''}\nReturn: {'N/A'}\nTravelers: {booking.num_travelers}"]
    ]
    t2 = Table(cust_data, colWidths=[95 * mm, 95 * mm])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))

    # Cost breakdown table
    table_data = [['Description', 'Qty', 'Unit (₹)', 'Total (₹)']]
    for it in items:
        table_data.append([it['desc'], str(it['qty']), f"{it['unit']:,}", f"{it['total']:,}"])

    table_data.append(['', '', 'Subtotal (₹)', f"{subtotal:,}"])
    table_data.append(['', '', 'Tax (₹)', f"{tax:,}"])
    table_data.append(['', '', 'Discount (₹)', f"-{discount:,}"])
    table_data.append(['', '', '<b>Grand Total (₹)</b>', f"<b>{grand_total:,}</b>"])
    table = Table(table_data, colWidths=[95 * mm, 25 * mm, 35 * mm, 35 * mm])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -5), 0.25, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (2, -4), (-1, -1), 'RIGHT'),
        ('SPAN', (0, -4), (2, -4)),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))

    # Payment details
    txn = payment_info.get('transaction_id', 'N/A') if payment_info else 'N/A'
    pay_date = payment_info.get('date', '') if payment_info else ''
    pay_details = [['Transaction ID:', txn], ['Payment Date:', pay_date], ['Status:', payment_status]]
    t3 = Table(pay_details, colWidths=[60 * mm, 120 * mm])
    t3.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(t3)
    story.append(Spacer(1, 12))

    # Notes
    notes_text = notes or 'Cancellation and refund policies apply as per terms and conditions.'
    story.append(Paragraph('<b>Notes</b>', styles['Heading4']))
    story.append(Paragraph(notes_text, normal))
    story.append(Spacer(1, 14))

    # Footer
    story.append(Paragraph('Thank you for choosing VOYAGE Travel Agency', normal))
    story.append(Paragraph('Website: example.com | support@agency.com | +91 XXXXX XXXXX', normal))

    doc.build(story)

    return file_path
