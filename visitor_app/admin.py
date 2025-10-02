from django.contrib import admin
from .models import Employee, Visitor
from .models import Employee, Visitor, Staff, StaffCheckInOut

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



@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'staff_id', 'email', 'department', 'phone', 'is_active', 'date_joined']
    list_filter = ['department', 'is_active', 'date_joined']
    search_fields = ['name', 'staff_id', 'email', 'phone']
    list_editable = ['is_active']
    ordering = ['name']

@admin.register(StaffCheckInOut)
class StaffCheckInOutAdmin(admin.ModelAdmin):
    list_display = ['staff', 'check_in_time', 'check_out_time', 'is_checked_in', 'duration_display']
    list_filter = ['is_checked_in', 'check_in_time', 'staff__department']
    search_fields = ['staff__name', 'staff__staff_id']
    readonly_fields = ['check_in_time']
    date_hierarchy = 'check_in_time'
    
    def duration_display(self, obj):
        if obj.check_out_time:
            duration = obj.check_out_time - obj.check_in_time
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m"
        return "In Progress"
    duration_display.short_description = 'Duration'