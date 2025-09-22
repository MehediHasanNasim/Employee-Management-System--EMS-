from django.utils import timezone
from django.db import transaction
from leaves.models import LeaveAllocation
from core.choices import LeaveStatus, ApprovalType, Decision, Status

def process_leave_approval(leave_request, approved_by, approval_type, decision, notes=""):
    # Process leave approval and update allocations
    from leaves.models import LeaveApproval
    
    # Create approval record
    approval = LeaveApproval.objects.create(
        leave_request=leave_request,
        approved_by=approved_by,
        approval_type=approval_type,
        decision=decision,
        notes=notes
    )
    
    # Update leave request status
    if approval_type == ApprovalType.TEAM_LEAD:
        leave_request.team_lead_approval = (decision == Decision.APPROVE)
        leave_request.approved_by_team_lead = approved_by
        leave_request.leave_status = LeaveStatus.TEAM_LEAD_APPROVED if decision == Decision.APPROVE else LeaveStatus.REJECTED
    
    elif approval_type == ApprovalType.HR:
        leave_request.hr_approval = (decision == Decision.APPROVE)
        leave_request.approved_by_hr = approved_by
        leave_request.leave_status = LeaveStatus.HR_APPROVED if decision == Decision.APPROVE else LeaveStatus.REJECTED
        
        # Deduct leave days only when HR approves
        if decision == Decision.APPROVE:
            deduct_leave_days(leave_request)
    
    leave_request.save()
    return approval

def deduct_leave_days(leave_request):
    # Deduct leave days from allocation
    month_start = leave_request.start_date.replace(day=1)
    allocation, created = LeaveAllocation.objects.get_or_create(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        valid_month=month_start,
        defaults={'allocated_days': 2}  # Default allocation
    )
    allocation.used_days += leave_request.days_requested
    allocation.save()

def withdraw_leave(leave_request, withdrawn_by, notes=""):
    # Withdraw approved leave and restore days
    from leaves.models import LeaveApproval
    
    # Restore leave days
    month_start = leave_request.start_date.replace(day=1)
    allocation = LeaveAllocation.objects.get(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        valid_month=month_start,
        status=Status.ACTIVE
    )
    allocation.used_days -= leave_request.days_requested
    allocation.save()
    
    # Create withdrawal record
    approval = LeaveApproval.objects.create(
        leave_request=leave_request,
        approved_by=withdrawn_by,
        approval_type=ApprovalType.HR,
        decision=Decision.WITHDRAW,
        notes=notes
    )
    
    # Update leave request
    leave_request.leave_status = LeaveStatus.WITHDRAWN
    leave_request.hr_approval = False
    leave_request.save()
    
    return approval