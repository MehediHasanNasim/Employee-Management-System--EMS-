from django.db import models
from core.models import BaseModel
from core.choices import Status, LeaveStatus, ApprovalType, Decision

class LeaveType(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    def __str__(self):
        return self.name

class LeaveAllocation(BaseModel):
    employee = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='leave_allocations')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='allocations')
    allocated_days = models.PositiveIntegerField(default=0)
    used_days = models.PositiveIntegerField(default=0)
    valid_month = models.DateField()  # First day of the month
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    @property
    def remaining_days(self):
        return self.allocated_days - self.used_days
    
    def __str__(self):
        return f"{self.employee.email} - {self.leave_type.name} - {self.valid_month}"
    
    class Meta:
        unique_together = ('employee', 'leave_type', 'valid_month')

class LeaveRequest(BaseModel):
    employee = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='requests')
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.PositiveIntegerField()
    reason = models.TextField()
    team_lead_approval = models.BooleanField(null=True, blank=True)
    hr_approval = models.BooleanField(null=True, blank=True)
    approved_by_team_lead = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='team_lead_approved_requests'
    )
    approved_by_hr = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='hr_approved_requests'
    )
    leave_status = models.CharField(max_length=20, choices=LeaveStatus.choices, default=LeaveStatus.PENDING)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    def __str__(self):
        return f"{self.employee.email} - {self.leave_type.name} - {self.start_date} to {self.end_date}"
    
    class Meta:
        ordering = ['-created_at']

class LeaveApproval(BaseModel):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='approvals')
    approved_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='given_approvals')
    approval_type = models.CharField(max_length=20, choices=ApprovalType.choices)
    decision = models.CharField(max_length=20, choices=Decision.choices)
    approval_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    def __str__(self):
        return f"{self.approval_type} - {self.decision} - {self.leave_request}"
    
    class Meta:
        ordering = ['-approval_date']