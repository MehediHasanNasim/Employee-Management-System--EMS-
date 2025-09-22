from rest_framework import serializers
from leaves.models import LeaveType, LeaveAllocation, LeaveRequest, LeaveApproval
from core.choices import Status, LeaveStatus, ApprovalType, Decision

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'alias', 'name']

class LeaveAllocationSerializer(serializers.ModelSerializer):
    remaining_days = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveAllocation
        fields = ['id', 'employee', 'leave_type', 'allocated_days', 'used_days', 'valid_month']
        read_only_fields = ['used_days', 'remaining_days', 'created_at', 'updated_at']

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'reason', 'team_lead_approval', 'hr_approval', 'approved_by_team_lead', 'approved_by_hr', 'leave_status']
        read_only_fields = ['created_at', 'updated_at', 'team_lead_approval', 
                           'hr_approval', 'approved_by_team_lead', 'approved_by_hr', 
                           'leave_status']

class LeaveApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApproval
        fields = ['id', 'leave_request', 'approved_by', 'approval_type', 'decision', 'approval_date', 'notes']
        read_only_fields = ['approval_date', 'created_at', 'updated_at']