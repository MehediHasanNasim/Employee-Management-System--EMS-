from rest_framework import generics, status
from rest_framework.response import Response
from leaves.models import LeaveType, LeaveAllocation, LeaveRequest, LeaveApproval
from leaves.rest.serializers.leaves import (
    LeaveTypeSerializer, LeaveAllocationSerializer, 
    LeaveRequestSerializer, LeaveApprovalSerializer
)
from core.choices import Status, LeaveStatus, ApprovalType, Decision


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


class LeaveTypeRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer


# LeaveAllocation Views
class LeaveAllocationListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = LeaveAllocation.objects.all()
    serializer_class = LeaveAllocationSerializer


class LeaveAllocationRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveAllocation.objects.all()
    serializer_class = LeaveAllocationSerializer


# LeaveRequest Views
class LeaveRequestListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer


class LeaveRequestRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer


# LeaveApproval Views
class LeaveApprovalListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer


class LeaveApprovalRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer


# Employee-specific Lists
class EmployeeLeaveAllocationListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveAllocation.objects.all()
    serializer_class = LeaveAllocationSerializer

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        qs = super().get_queryset()  
        return qs.filter(employee_id=employee_id)


class EmployeeLeaveRequestListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        qs = super().get_queryset()  
        return qs.filter(employee_id=employee_id)


# LeaveRequest-specific Approvals
class LeaveRequestApprovalListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveApproval.objects.all() 
    serializer_class = LeaveApprovalSerializer

    def get_queryset(self):
        leave_request_id = self.kwargs['leave_request_id']
        qs = super().get_queryset()  
        return qs.filter(leave_request_id=leave_request_id)


# User-specific Given Approvals
class UserGivenApprovalsListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        qs = super().get_queryset()  
        return qs.filter(approved_by_id=user_id)