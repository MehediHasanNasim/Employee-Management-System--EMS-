from rest_framework import generics, status
from rest_framework.response import Response
from leaves.models import LeaveType, LeaveAllocation, LeaveRequest, LeaveApproval
from leaves.rest.serializers.leaves import (
    LeaveTypeSerializer, LeaveAllocationSerializer, 
    LeaveRequestSerializer, LeaveApprovalSerializer
)
from core.permissions import IsHR, LeaveAllocationPermissions, LeaveRequestPermissions, IsTeamLead, IsOwner, LeaveApprovalPermissions
from core.choices import Status, LeaveStatus, ApprovalType, Decision
from core.utils import get_user_role
from leaves.services import process_leave_approval



# Mixins
class ActiveQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status=Status.ACTIVE)

class SoftDeleteMixin:
    def perform_destroy(self, instance):
        instance.status = Status.REMOVED
        instance.save()


# LeaveType Views
class LeaveTypeListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsHR] 

    filterset_fields = ["name", "status"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

class LeaveTypeRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsHR]


# LeaveAllocation Views
class LeaveAllocationListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = LeaveAllocation.objects.all()
    serializer_class = LeaveAllocationSerializer
    permission_classes = [LeaveAllocationPermissions]

    filterset_fields = ["employee", "leave_type", "status", "year"]
    search_fields = ["employee__username", "employee__email", "leave_type__name"]
    ordering_fields = ["year", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        
        # HR can see all allocations
        if self.request.user.role.name == 'HR':
            return qs
        
        # Employees can only see their own allocations
        if self.request.user.role.name == 'Employee':
            return qs.filter(employee=self.request.user)
        
        return qs.none()

class LeaveAllocationRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveAllocation.objects.all()
    serializer_class = LeaveAllocationSerializer
    permission_classes = [LeaveAllocationPermissions]



# LeaveRequest Views
class LeaveRequestListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [LeaveRequestPermissions]

    filterset_fields = ["employee", "leave_type", "status", "leave_status", "start_date", "end_date"]
    search_fields = ["employee__username", "employee__email", "leave_type__name", "reason"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        role = get_user_role(self.request.user)

        if role == 'SuperAdmin':
            return qs  
        if role == 'HR':
            return qs
        if role == 'Team Lead':
            return qs.filter(employee__team=self.request.user.team)
        if role == 'Employee':
            return qs.filter(employee=self.request.user)

        return qs.none()
    
    def perform_create(self, serializer):
        role = get_user_role(self.request.user)
        if role == 'Employee':
            serializer.save(employee=self.request.user)
        else:
            serializer.save()

class LeaveRequestRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [LeaveRequestPermissions]


# LeaveApproval Views
class LeaveApprovalListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer
    permission_classes = [LeaveApprovalPermissions]  

    filterset_fields = ["leave_request", "approval_type", "decision", "status"]
    search_fields = ["leave_request__employee__username", "leave_request__employee__email", "notes"]
    ordering_fields = ["created_at", "decision"]
    ordering = ["-created_at"]


    def get_queryset(self):
        qs = super().get_queryset()
        role = get_user_role(self.request.user)

        if role == 'SuperAdmin':
            return qs  
        if role == 'HR':
            return qs
        if role == 'Team Lead':
            return qs.filter(
                leave_request__employee__team=self.request.user.team
            )
        if role == 'Employee':
            return qs.filter(leave_request__employee=self.request.user)

        return qs.none()
    
    def create(self, request, *args, **kwargs):
        # Override create to handle approval business logic"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        leave_request = serializer.validated_data['leave_request']
        approval_type = serializer.validated_data['approval_type']
        decision = serializer.validated_data['decision']
        notes = serializer.validated_data.get('notes', '')
        
        # Permission checks
        if approval_type == ApprovalType.TEAM_LEAD:
            if request.user.role.name != 'Team Lead':
                return Response({'error': 'Only Team Leads can approve as team lead'}, status=403)
            if leave_request.employee.team != request.user.team:
                return Response({'error': 'Can only approve leaves for your team'}, status=403)
            if leave_request.employee == request.user:
                return Response({'error': 'Cannot approve your own leave'}, status=403)
        
        elif approval_type == ApprovalType.HR:
            if request.user.role.name != 'HR':
                return Response({'error': 'Only HR can give final approval'}, status=403)
        
        # Process approval with business logic
        approval = process_leave_approval(leave_request, request.user, approval_type, decision, notes)
        
        # Return the created approval
        response_serializer = self.get_serializer(approval)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LeaveApprovalRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer
    permission_classes = [LeaveApprovalPermissions]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # HR can see all approvals
        if self.request.user.role.name == 'HR':
            return qs
        
        # Team Lead can see approvals for their team members' requests
        if self.request.user.role.name == 'Team Lead':
            return qs.filter(
                leave_request__employee__team=self.request.user.team
            )
        
        # Employees can only see approvals for their own requests
        if self.request.user.role.name == 'Employee':
            return qs.filter(leave_request__employee=self.request.user)
        
        return qs.none()


# Employee-specific Lists
class EmployeeLeaveAllocationListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveAllocation.objects.all()
    serializer_class = LeaveAllocationSerializer
    permission_classes = [LeaveAllocationPermissions]

    filterset_fields = ["leave_type", "status", "year"]
    search_fields = ["leave_type__name", "employee__username", "employee__email"]
    ordering_fields = ["year", "created_at"]
    ordering = ["-created_at"]


    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        qs = super().get_queryset().filter(employee_id=employee_id)
        
        # Check if user has permission to view this employee's allocations
        if (self.request.user.role.name == 'HR' or 
            (self.request.user.role.name == 'Team Lead' and 
             self.request.user.team.members.filter(id=employee_id).exists()) or
            self.request.user.id == employee_id):
            return qs
        
        return qs.none()


class EmployeeLeaveRequestListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [LeaveRequestPermissions]

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        qs = super().get_queryset().filter(employee_id=employee_id)
        
        # Check if user has permission to view this employee's requests
        if (self.request.user.role.name == 'HR' or 
            (self.request.user.role.name == 'Team Lead' and 
             self.request.user.team.members.filter(id=employee_id).exists()) or
            self.request.user.id == employee_id):
            return qs
        
        return qs.none()


# LeaveRequest-specific Approvals
class LeaveRequestApprovalListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveApproval.objects.all() 
    serializer_class = LeaveApprovalSerializer
    permission_classes = [LeaveApprovalPermissions]

    filterset_fields = ["leave_type", "status", "leave_status", "start_date", "end_date"]
    search_fields = ["leave_type__name", "employee__username", "employee__email", "reason"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        leave_request_id = self.kwargs['leave_request_id']
        qs = LeaveApproval.objects.filter(status=Status.ACTIVE, leave_request_id=leave_request_id)
        
        # Check if user has permission to view this leave request's approvals
        try:
            from leaves.models import LeaveRequest
            leave_request = LeaveRequest.objects.get(id=leave_request_id, status=Status.ACTIVE)
            
            # HR can see all
            if self.request.user.role.name == 'HR':
                return qs
            
            # Team Lead can see if it's from their team
            if (self.request.user.role.name == 'Team Lead' and 
                leave_request.employee.team == self.request.user.team):
                return qs
            
            # Employee can see if it's their own request
            if (self.request.user.role.name == 'Employee' and 
                leave_request.employee == self.request.user):
                return qs
                
        except LeaveRequest.DoesNotExist:
            pass
        
        return qs.none()
    

# User-specific Given Approvals
class UserGivenApprovalsListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer
    permission_classes = [LeaveApprovalPermissions]

    filterset_fields = ["leave_type", "status", "leave_status", "start_date", "end_date"]
    search_fields = ["leave_type__name", "employee__username", "employee__email", "reason"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]

    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        qs = LeaveApproval.objects.filter(status=Status.ACTIVE, approved_by_id=user_id)
        
        if self.request.user.role.name == 'HR':
            return qs
        
        # Users can only see their own given approvals
        if self.request.user.id == user_id:
            return qs
        
        if (self.request.user.role.name == 'Team Lead' and 
            self.request.user.team.members.filter(id=user_id).exists()):
            return qs
        
        return qs.none()