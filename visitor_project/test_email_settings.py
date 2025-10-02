import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visitor_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("Testing email configuration...")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

try:
    result = send_mail(
        'Test Email from Visitor System',
        'This is a test email to verify email configuration.',
        settings.DEFAULT_FROM_EMAIL,
        ['katagasamson@twcc-tz.org'],  # Send to yourself for testing
        fail_silently=False,
    )
    print(f"✅ Test email sent successfully! Result: {result}")
except Exception as e:
    print(f"❌ Error sending test email: {e}")
    import traceback
    traceback.print_exc()