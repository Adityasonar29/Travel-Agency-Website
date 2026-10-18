import os
import os
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from apps.core.models import SiteSettings

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image


def _display_date(value):
    return value.strftime('%d %b %Y') if value else '-'


def _money(value):
    return f"${Decimal(value or 0):,.2f}"


def _destination_text(booking):
    if booking.tour:
        destinations = list(booking.tour.destinations.all())
        if destinations:
            return ', '.join(f'{item.name}, {item.country}' for item in destinations)
    return booking.destination_name or 'Personalized journey'


def generate_invoice_for_booking(booking, items=None, payment_info=None, notes=None):
    """
    Generate a detailed A4 PDF invoice for a Booking instance and return the file path.

    - `items`: optional list of dicts {desc, qty, unit} to override defaults.
    - `payment_info`: optional dict with transaction_id, method, date, status, amount_paid
    - `notes`: optional string for terms/cancellation policy
    """
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)

    filename = f"invoice_{booking.booking_id or booking.id}.pdf"
    file_path = os.path.join(invoices_dir, filename)

    # Default items come directly from the selected tour and locked booking total.
    if items is None:
        travelers = booking.num_travelers or 1
        package_name = booking.tour.name if booking.tour else 'Personalized journey request'
        unit_price = booking.tour.price_per_person if booking.tour else (booking.total_amount or 0)
        items = [
            {'desc': package_name, 'qty': travelers if booking.tour else 1, 'unit': unit_price},
        ]

    # Compute totals
    for it in items:
        it['qty'] = int(it.get('qty', 1))
        it['unit'] = int(it.get('unit', 0))
        it['total'] = it['qty'] * it['unit']

    subtotal = sum(it['total'] for it in items)
    # Booking.total_amount is the amount shown throughout the website.
    # Never add an unrecorded tax or invented services to the invoice.
    if booking.total_amount is not None:
        subtotal = booking.total_amount
        if len(items) == 1:
            items[0]['unit'] = subtotal / max(items[0]['qty'], 1)
            items[0]['total'] = subtotal
    discount = int(payment_info.get('discount', 0)) if payment_info and payment_info.get('discount') else 0
    grand_total = subtotal - discount
    amount_paid = int(payment_info.get('amount_paid', grand_total) if payment_info else (grand_total if booking.payment_status in {'paid', 'refunded'} else 0))
    balance = grand_total - amount_paid

    # Document
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=12 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = ParagraphStyle('heading', parent=styles['Heading2'], alignment=0, fontSize=14)

    story = []

    invoice_no = booking.invoice_number or f"INV-{booking.booking_id or booking.id}"

    # Branded header
    site_settings = SiteSettings.load()
    header_title = ParagraphStyle('InvoiceHeaderTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=19, leading=22, textColor=colors.white)
    header_meta = ParagraphStyle('InvoiceHeaderMeta', parent=normal, fontSize=7.5, leading=10, textColor=colors.HexColor('#e8dfd2'))
    header_label = ParagraphStyle('InvoiceHeaderLabel', parent=normal, fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#d8bd8c'), alignment=2)
    header_value = ParagraphStyle('InvoiceHeaderValue', parent=normal, fontSize=8.5, leading=11, textColor=colors.white, alignment=2)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'voyage-logo.png')
    logo = Image(logo_path, width=46 * mm, height=20 * mm, kind='proportional') if os.path.exists(logo_path) else Paragraph('VOYAGE', header_title)
    brand = [logo, Paragraph(f'{site_settings.address}<br/>Phone: {site_settings.phone}<br/>Email: {site_settings.email}', header_meta)]
    invoice_heading = [Paragraph('INVOICE', header_title), Paragraph(invoice_no, header_label)]
    header = Table([[brand, invoice_heading]], colWidths=[116 * mm, 62 * mm], hAlign='LEFT')
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1b1a18')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#b89458')),
    ]))
    story.append(header)
    story.append(Spacer(1, 6))

    # Invoice info table (two columns)
    invoice_date = _display_date(booking.invoice_generated_at or booking.payment_date or timezone.now())
    payment_status = payment_info.get('status') if payment_info and payment_info.get('status') else booking.get_payment_status_display()
    payment_method = payment_info.get('method') if payment_info and payment_info.get('method') else booking.get_payment_method_display() or '-'

    info_data = [
        ['Invoice No:', invoice_no, 'Invoice Date:', invoice_date],
        ['Booking ID:', str(booking.booking_id or booking.id), 'Booking Status:', booking.get_status_display()],
        ['Payment Status:', payment_status, 'Payment Method:', payment_method],
        ['Transaction ID:', payment_info.get('transaction_id', booking.payment_transaction_id or '-') if payment_info else (booking.payment_transaction_id or '-'), 'Payment Date:', _display_date(booking.payment_date)],
    ]
    t = Table(info_data, colWidths=[32 * mm, 53 * mm, 32 * mm, 61 * mm], hAlign='LEFT')
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
        [f"Name: {booking.full_name}\nEmail: {booking.email}\nPhone: {booking.phone}\nContact: {booking.get_contact_preference_display()}",
        f"Destination: {_destination_text(booking)}\nPackage: {booking.tour.name if booking.tour else 'Personalized journey'}\nDeparture: {_display_date(booking.travel_date)}\nReturn: {_display_date(booking.return_date)}\nTravelers: {booking.num_travelers} (Adults: {booking.adults}, Children: {booking.children})\nFrom: {booking.origin or '-'}"]
    ]
    t2 = Table(cust_data, colWidths=[89 * mm, 89 * mm], hAlign='LEFT')
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
    table_data = [['Description', 'Qty', 'Unit', 'Amount']]
    for it in items:
        table_data.append([it['desc'], str(it['qty']), _money(it['unit']), _money(it['total'])])

    table_data.append(['', '', 'Subtotal', _money(subtotal)])
    table_data.append(['', '', 'Discount', f"- {_money(discount)}"])
    table_data.append(['', '', 'Grand Total', _money(grand_total)])
    table_data.append(['', '', 'Amount Paid', _money(amount_paid)])
    table_data.append(['', '', 'Balance Due', _money(balance)])
    table = Table(table_data, colWidths=[84 * mm, 22 * mm, 36 * mm, 36 * mm], hAlign='LEFT')
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#b9b1a5')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eee9e1')),
        ('BACKGROUND', (0, -5), (-1, -1), colors.HexColor('#fbfaf7')),
        ('FONTNAME', (2, -3), (-1, -3), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -3), (-1, -3), 0.8, colors.HexColor('#b89458')),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (2, -5), (-1, -1), 'RIGHT'),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))

    # Notes
    notes_text = notes or (
        'Refund initiated. Please allow up to 24 hours for the amount to be returned.'
        if booking.payment_status == 'refunded'
        else 'Cancellation and refund policies apply as per terms and conditions.'
    )
    story.append(Paragraph('<b>Notes</b>', styles['Heading4']))
    story.append(Paragraph(notes_text, normal))
    story.append(Spacer(1, 14))

    # Footer
    story.append(Paragraph('Thank you for choosing VOYAGE Travel Agency', normal))
    story.append(Paragraph(f'Website: Voyage Travel Agency | {site_settings.email} | {site_settings.phone}', normal))

    doc.build(story)

    return file_path
