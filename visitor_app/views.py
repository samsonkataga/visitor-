import qrcode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import io
import base64
from django.conf import settings 
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string  # Add this import
from django.contrib import messages
from .models import Visitor, Employee, Staff, StaffCheckInOut
from .forms import VisitorCheckInForm, CheckOutForm
from .utils import send_visitor_notification, generate_qr_code
from datetime import datetime, date
from .forms import VisitorCheckInForm, CheckOutForm, StaffRegistrationForm, StaffCheckInForm, StaffCheckOutForm
from .decorators import admin_required

def home(request):
    # Get current date
    today = timezone.now().date()
    
    # Calculate statistics
    today_count = Visitor.objects.filter(
        check_in_time__date=today
    ).count()
    
    month_count = Visitor.objects.filter(
        check_in_time__year=today.year,
        check_in_time__month=today.month
    ).count()
    
    year_count = Visitor.objects.filter(
        check_in_time__year=today.year
    ).count()
    
    total_visitors = Visitor.objects.count()
    
    context = {
        'today_count': today_count,
        'month_count': month_count,
        'year_count': year_count,
        'total_visitors': total_visitors,
    }
    
    return render(request, 'visitor_app/base.html', context)

def send_visitor_emails(visitor):
    """Send emails to host and visitor after check-in"""
    try:
        # Generate QR code for email
        qr_data = f"Visitor: {visitor.name}\nBadge ID: {visitor.badge_id}\nHost: {visitor.host.name}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_base64}"
        
        # Email to Host
        host_subject = f'Visitor Notification: {visitor.name} is here to see you'
        host_context = {
            'host_name': visitor.host.name,
            'visitor_name': visitor.name,
            'visitor_company': visitor.company,
            'visitor_email': visitor.email,
            'visitor_phone': visitor.phone,
            'visitor_purpose': visitor.purpose,
            'checkin_time': visitor.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            'badge_id': visitor.badge_id,
        }
        
        host_html_content = render_to_string('visitor_app/emails/host_notification.html', host_context)
        host_text_content = f"""
        Hello {visitor.host.name},

        You have a visitor waiting for you at the reception.

        Visitor Details:
        Name: {visitor.name}
        Company: {visitor.company or 'Not specified'}
        Email: {visitor.email or 'Not specified'}
        Phone: {visitor.phone}
        Purpose: {visitor.purpose or 'Not specified'}
        Check-in Time: {visitor.check_in_time.strftime('%Y-%m-%d %H:%M:%S')}
        Badge ID: {visitor.badge_id}

        Please proceed to the reception to meet your visitor.

        This is an automated notification from Visitor Management System
        """
        
        print(f"Attempting to send email to host: {visitor.host.email}")
        
        host_email = EmailMultiAlternatives(
            subject=host_subject,
            body=host_text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[visitor.host.email]
        )
        host_email.attach_alternative(host_html_content, "text/html")
        host_email_sent = host_email.send()
        print(f"Host email sent: {host_email_sent}")

        # Email to Visitor (only if visitor provided email)
        if visitor.email:
            visitor_subject = f'Your Visitor Badge - {visitor.badge_id}'
            visitor_context = {
                'visitor_name': visitor.name,
                'visitor_company': visitor.company,
                'host_name': visitor.host.name,
                'badge_id': visitor.badge_id,
                'checkin_time': visitor.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'qr_code_url': qr_code_url,
            }
            
            visitor_html_content = render_to_string('visitor_app/emails/visitor_badge.html', visitor_context)
            visitor_text_content = f"""
            Hello {visitor.name},

            Thank you for checking in. Here is your visitor badge information:

            VISITOR BADGE
            Name: {visitor.name}
            Company: {visitor.company or 'N/A'}
            Host: {visitor.host.name}
            Badge ID: {visitor.badge_id}
            Check-in Time: {visitor.check_in_time.strftime('%Y-%m-%d %H:%M:%S')}

            Please keep this badge information available during your visit.

            Check-out Instructions:
            When leaving, please present your badge ID ({visitor.badge_id}) at the reception 
            or use the check-out system.

            This is an automated email from Visitor Management System
            """
            
            print(f"Attempting to send email to visitor: {visitor.email}")
            
            visitor_email = EmailMultiAlternatives(
                subject=visitor_subject,
                body=visitor_text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[visitor.email]
            )
            visitor_email.attach_alternative(visitor_html_content, "text/html")
            visitor_email_sent = visitor_email.send()
            print(f"Visitor email sent: {visitor_email_sent}")
        else:
            print("No email provided for visitor, skipping visitor email")
            
    except Exception as e:
        print(f"Error in send_visitor_emails: {str(e)}")
        import traceback
        traceback.print_exc()

def checkin(request):
    if request.method == 'POST':
        form = VisitorCheckInForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            # Generate unique badge ID
            import uuid
            visitor.badge_id = str(uuid.uuid4())[:8].upper()
            visitor.save()
            
            # Send emails to host and visitor
            send_visitor_emails(visitor)
            
            return redirect('badge', badge_id=visitor.badge_id)
    else:
        form = VisitorCheckInForm()
    
    return render(request, 'visitor_app/checkin.html', {'form': form})

def checkout(request):
    if request.method == 'POST':
        form = CheckOutForm(request.POST)
        if form.is_valid():
            badge_id = form.cleaned_data['badge_id']
            try:
                visitor = Visitor.objects.get(badge_id=badge_id, is_checked_in=True)
                visitor.check_out()
                return render(request, 'visitor_app/checkout.html', {
                    'form': form,
                    'success': True,
                    'visitor': visitor
                })
            except Visitor.DoesNotExist:
                form.add_error('badge_id', 'Invalid badge ID or visitor already checked out')
    else:
        form = CheckOutForm()
    
    return render(request, 'visitor_app/checkout.html', {'form': form})

def badge(request, badge_id):
    visitor = get_object_or_404(Visitor, badge_id=badge_id)
    
    # Generate QR code
    qr_code = generate_qr_code(visitor)
    
    return render(request, 'visitor_app/badge.html', {
        'visitor': visitor,
        'qr_code': qr_code
    })

@admin_required
def reports(request):
    # Get all visitors in LIFO order (newest first)
    visitors_list = Visitor.objects.all().order_by('-check_in_time')
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            visitors_list = visitors_list.filter(
                check_in_time__date=filter_date
            )
        except ValueError:
            pass
    
    # Pagination - 10 visitors per page
    paginator = Paginator(visitors_list, 10)
    page = request.GET.get('page')
    
    try:
        visitors = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        visitors = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        visitors = paginator.page(paginator.num_pages)
    
    return render(request, 'visitor_app/reports.html', {
        'visitors': visitors,
        'date_filter': date_filter
    })

def employees(request):
    employees_list = Employee.objects.filter(is_active=True)
    return render(request, 'visitor_app/employees.html', {'employees': employees_list})


def staff_registration(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f'Staff member {staff.name} registered successfully!')
            return redirect('staff_list')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'visitor_app/staff_registration.html', {'form': form})

def staff_checkin(request):
    if request.method == 'POST':
        form = StaffCheckInForm(request.POST)
        if form.is_valid():
            staff_id = form.cleaned_data['staff_id']
            try:
                staff = Staff.objects.get(staff_id=staff_id, is_active=True)
                
                # Check if staff is already checked in
                if StaffCheckInOut.objects.filter(staff=staff, is_checked_in=True).exists():
                    messages.error(request, f'{staff.name} is already checked in!')
                else:
                    # Create new check-in record
                    checkin_record = StaffCheckInOut.objects.create(staff=staff)
                    messages.success(request, f'{staff.name} checked in successfully at {checkin_record.check_in_time.strftime("%H:%M")}')
                    return redirect('staff_reports')
                    
            except Staff.DoesNotExist:
                form.add_error('staff_id', 'Invalid staff ID or staff not found')
    else:
        form = StaffCheckInForm()
    
    return render(request, 'visitor_app/staff_checkin.html', {'form': form})

def staff_checkout(request):
    if request.method == 'POST':
        form = StaffCheckOutForm(request.POST)
        if form.is_valid():
            staff_id = form.cleaned_data['staff_id']
            try:
                staff = Staff.objects.get(staff_id=staff_id, is_active=True)
                
                # Find active check-in record
                try:
                    checkin_record = StaffCheckInOut.objects.get(staff=staff, is_checked_in=True)
                    checkin_record.check_out()
                    duration = checkin_record.duration()
                    hours, remainder = divmod(duration.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    messages.success(request, f'{staff.name} checked out successfully. Duration: {int(hours)}h {int(minutes)}m')
                    return redirect('staff_reports')
                    
                except StaffCheckInOut.DoesNotExist:
                    form.add_error('staff_id', f'{staff.name} is not currently checked in')
                    
            except Staff.DoesNotExist:
                form.add_error('staff_id', 'Invalid staff ID or staff not found')
    else:
        form = StaffCheckOutForm()
    
    return render(request, 'visitor_app/staff_checkout.html', {'form': form})

def staff_list(request):
    staff_list = Staff.objects.filter(is_active=True).order_by('name')
    return render(request, 'visitor_app/staff_list.html', {'staff_list': staff_list})


@admin_required
def staff_reports(request):
    # Get all staff check-in/out records in LIFO order
    staff_records_list = StaffCheckInOut.objects.all().order_by('-check_in_time')
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            staff_records_list = staff_records_list.filter(
                check_in_time__date=filter_date
            )
        except ValueError:
            pass
    
    # Filter by staff member if provided
    staff_filter = request.GET.get('staff')
    if staff_filter:
        staff_records_list = staff_records_list.filter(staff__id=staff_filter)
    
    # Pagination - 10 records per page
    paginator = Paginator(staff_records_list, 10)
    page = request.GET.get('page')
    
    try:
        staff_records = paginator.page(page)
    except PageNotAnInteger:
        staff_records = paginator.page(1)
    except EmptyPage:
        staff_records = paginator.page(paginator.num_pages)
    
    staff_members = Staff.objects.filter(is_active=True)
    
    return render(request, 'visitor_app/staff_reports.html', {
        'staff_records': staff_records,
        'date_filter': date_filter,
        'staff_filter': staff_filter,
        'staff_members': staff_members,
    })





# import qrcode
# import io
# import base64
# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse
# from django.utils import timezone
# from django.db.models import Q
# from .models import Visitor, Employee
# from .forms import VisitorCheckInForm, CheckOutForm
# from datetime import datetime, date

# def home(request):
#     return render(request, 'visitor_app/base.html')

# def checkin(request):
#     if request.method == 'POST':
#         form = VisitorCheckInForm(request.POST)
#         if form.is_valid():
#             visitor = form.save(commit=False)
#             # Generate unique badge ID
#             import uuid
#             visitor.badge_id = str(uuid.uuid4())[:8].upper()
#             visitor.save()
#             return redirect('badge', badge_id=visitor.badge_id)
#     else:
#         form = VisitorCheckInForm()
    
#     return render(request, 'visitor_app/checkin.html', {'form': form})

# def checkout(request):
#     if request.method == 'POST':
#         form = CheckOutForm(request.POST)
#         if form.is_valid():
#             badge_id = form.cleaned_data['badge_id']
#             try:
#                 visitor = Visitor.objects.get(badge_id=badge_id, is_checked_in=True)
#                 visitor.check_out()
#                 return render(request, 'visitor_app/checkout.html', {
#                     'form': form,
#                     'success': True,
#                     'visitor': visitor
#                 })
#             except Visitor.DoesNotExist:
#                 form.add_error('badge_id', 'Invalid badge ID or visitor already checked out')
#     else:
#         form = CheckOutForm()
    
#     return render(request, 'visitor_app/checkout.html', {'form': form})

# def badge(request, badge_id):
#     visitor = get_object_or_404(Visitor, badge_id=badge_id)
    
#     # Generate QR code
#     qr_data = f"Visitor: {visitor.name}\nBadge ID: {visitor.badge_id}\nHost: {visitor.host.name}"
#     qr = qrcode.QRCode(version=1, box_size=10, border=5)
#     qr.add_data(qr_data)
#     qr.make(fit=True)
    
#     img = qr.make_image(fill_color="black", back_color="white")
#     buffer = io.BytesIO()
#     img.save(buffer, format='PNG')
#     qr_code = base64.b64encode(buffer.getvalue()).decode()
    
#     return render(request, 'visitor_app/badge.html', {
#         'visitor': visitor,
#         'qr_code': qr_code
#     })

# def reports(request):
#     visitors = Visitor.objects.all().order_by('-check_in_time')
    
#     # Filter by date
#     date_filter = request.GET.get('date')
#     if date_filter:
#         try:
#             filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
#             visitors = visitors.filter(
#                 check_in_time__date=filter_date
#             )
#         except ValueError:
#             pass
    
#     return render(request, 'visitor_app/reports.html', {
#         'visitors': visitors,
#         'date_filter': date_filter
#     })

# def employees(request):
#     employees_list = Employee.objects.filter(is_active=True)
#     return render(request, 'visitor_app/employees.html', {'employees': employees_list})