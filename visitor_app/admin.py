from django.contrib import admin
from .models import Employee, Visitor

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'department', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'email']

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'host', 'check_in_time', 'check_out_time', 'is_checked_in']
    list_filter = ['is_checked_in', 'check_in_time', 'host']
    search_fields = ['name', 'company', 'badge_id']
    readonly_fields = ['badge_id', 'check_in_time']