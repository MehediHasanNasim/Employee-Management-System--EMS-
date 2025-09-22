from django.contrib import admin
from .models import LeaveType, LeaveAllocation, LeaveRequest, LeaveApproval

# LeaveType
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name',)


# LeaveAllocation
@admin.register(LeaveAllocation)
class LeaveAllocationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'allocated_days', 'used_days', 'remaining_days', 'valid_month', 'status')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__email', 'leave_type__name')
    autocomplete_fields = ('employee', 'leave_type')


# LeaveRequest
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'leave_status', 'team_lead_approval', 'hr_approval', 'status')
    list_filter = ('leave_status', 'team_lead_approval', 'hr_approval', 'status', 'leave_type')
    search_fields = ('employee__email', 'leave_type__name', 'reason')
    autocomplete_fields = ('employee', 'leave_type', 'approved_by_team_lead', 'approved_by_hr')


# LeaveApproval
@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('leave_request', 'approved_by', 'approval_type', 'decision', 'approval_date', 'status')
    list_filter = ('approval_type', 'decision', 'status')
    search_fields = ('leave_request__employee__email', 'approved_by__email', 'notes')
    autocomplete_fields = ('leave_request', 'approved_by')
