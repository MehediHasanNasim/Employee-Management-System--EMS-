from rest_framework import serializers
from django.utils import timezone
from leaves.models import LeaveType, LeaveAllocation, LeaveRequest, LeaveApproval
from core.choices import Status, LeaveStatus, ApprovalType, Decision
from leaves.services import deduct_leave_days, withdraw_leave


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'alias', 'name']

class LeaveAllocationSerializer(serializers.ModelSerializer):
    remaining_days = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LeaveAllocation
        fields = ['id', 'employee', 'leave_type', 'allocated_days', 'used_days', 'remaining_days', 'valid_month']
        read_only_fields = ['used_days', 'remaining_days', 'created_at', 'updated_at']

    def validate(self, data):
        # Validate allocation data
        if data['allocated_days'] < 0:
            raise serializers.ValidationError("Allocated days cannot be negative")
        return data
    
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'reason', 'team_lead_approval', 'hr_approval', 'approved_by_team_lead', 'approved_by_hr', 'leave_status']
        read_only_fields = ['employee', 'created_at', 'updated_at', 'team_lead_approval', 
                           'hr_approval', 'approved_by_team_lead', 'approved_by_hr', 
                           'leave_status']
        
    def validate(self, data):

        # Check team membership
        request = self.context.get('request')
        employee = request.user if request else None

        # employee = data['employee']
        if not employee.team:
            raise serializers.ValidationError("Employee must belong to a team to apply for leave")
        

        # Check if end date is after start date
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        
        # Check if dates are in the future
        if data['start_date'] < timezone.now().date():
            raise serializers.ValidationError("Cannot request leave for past dates")
        
        # Check leave balance
        leave_type = data['leave_type']
        days_requested = data['days_requested']
        
        # Get allocation for the month of start_date
        month_start = data['start_date'].replace(day=1)
        try:
            allocation = LeaveAllocation.objects.get(
                employee=employee,
                leave_type=leave_type,
                valid_month=month_start,
                status=Status.ACTIVE
            )
            if allocation.remaining_days < days_requested:
                raise serializers.ValidationError(
                    f"Insufficient leave balance. Available: {allocation.remaining_days}"
                )
        except LeaveAllocation.DoesNotExist:
            raise serializers.ValidationError("No active leave allocation found for this period")
        
        return data
    

class LeaveApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApproval
        fields = ['id', 'leave_request', 'approved_by', 'approval_type', 'decision', 'approval_date', 'notes']
        read_only_fields = ['approval_date', 'created_at', 'updated_at']


    def validate(self, data):
        """Validate approval data"""
        leave_request = data['leave_request']
        approval_type = data['approval_type']
        decision = data['decision']
        
        # Check if user has permission to approve
        user = self.context['request'].user
        
        if approval_type == ApprovalType.TEAM_LEAD:
            if user.role.name != 'Team Lead' or leave_request.employee.team != user.team:
                raise serializers.ValidationError("You are not authorized to approve this request as team lead")
        
        elif approval_type == ApprovalType.HR:
            if user.role.name != 'HR':
                raise serializers.ValidationError("Only HR can provide final approval")
        
        return data