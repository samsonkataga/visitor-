import os
import django
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visitor_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("Testing Email Configuration")
print("=" * 50)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 50)

try:
    print("Attempting to send test email...")
    result = send_mail(
        'Test Email from Visitor System',
        'This is a test email to verify email configuration.',
        settings.DEFAULT_FROM_EMAIL,
        ['katagasamson@twcc-tz.org'],  # Send to yourself for testing
        fail_silently=False,
    )
    print(f"✅ SUCCESS: Test email sent! Result: {result}")
    print("Check your email inbox for the test message.")
except Exception as e:
    print(f"❌ ERROR: Failed to send test email")
    print(f"Error details: {e}")
    
    import traceback
    traceback.print_exc()

print("=" * 50)