import qrcode
import io
import base64
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def generate_qr_code(visitor):
    """Generate QR code for visitor"""
    qr_data = f"Visitor: {visitor.name}\nBadge ID: {visitor.badge_id}\nHost: {visitor.host.name}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

def send_visitor_notification(visitor):
    """Send email notifications to both host and visitor"""
    
    # Generate QR code
    qr_code = generate_qr_code(visitor)
    
    # Email context for both emails
    context = {
        'visitor': visitor,
        'qr_code': qr_code,
        'check_in_time': visitor.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 1. Send notification to HOST
    host_subject = f'Visitor Alert: {visitor.name} is here to see you'
    host_html_message = render_to_string('visitor_app/emails/host_notification.html', context)
    host_plain_message = strip_tags(host_html_message)
    
    host_email = EmailMultiAlternatives(
        subject=host_subject,
        body=host_plain_message,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL
        to=[visitor.host.email],
    )
    host_email.attach_alternative(host_html_message, "text/html")
    host_email.send()
    
    # 2. Send badge details to VISITOR (only if visitor provided email)
    if visitor.email:
        visitor_subject = f'Your Visitor Badge - {visitor.name}'
        visitor_html_message = render_to_string('visitor_app/emails/visitor_badge.html', context)
        visitor_plain_message = strip_tags(visitor_html_message)
        
        visitor_email = EmailMultiAlternatives(
            subject=visitor_subject,
            body=visitor_plain_message,
            from_email=None,
            to=[visitor.email],
        )
        visitor_email.attach_alternative(visitor_html_message, "text/html")
        visitor_email.send()