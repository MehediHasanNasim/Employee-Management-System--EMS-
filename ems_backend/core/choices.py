from django.db import models

class Status(models.TextChoices):
    ACTIVE = "Active", "ACTIVE"
    INACTIVE = "Inactive", "INACTIVE"
    REMOVED = "Removed", "REMOVED"

class LeaveStatus(models.TextChoices):
    PENDING = "Pending", "PENDING"
    TEAM_LEAD_APPROVED = "team_lead_approved", "TEAM_LEAD_APPROVED"
    HR_APPROVED = "hr_approved", "HR_APPROVED"
    REJECTED = "Rejected", "REJECTED"
    WITHDRAWN = "Withdrawn", "WITHDRAWN"

class ApprovalType(models.TextChoices):
    TEAM_LEAD = "team_lead", "TEAM_LEAD"
    HR = "hr", "HR"

class Decision(models.TextChoices):
    APPROVE = "Approved", "APPROVED"
    REJECT = "Rejected", "REJECTED"
    WITHDRAW = "Withdrawn", "WITHDRAWN"