from django.urls import path
from leaves.rest.views.leaves import (
    LeaveTypeListCreateView, LeaveTypeRetrieveUpdateDestroyView,
    LeaveAllocationListCreateView, LeaveAllocationRetrieveUpdateDestroyView,
    LeaveRequestListCreateView, LeaveRequestRetrieveUpdateDestroyView,
    LeaveApprovalListCreateView, LeaveApprovalRetrieveUpdateDestroyView,
    EmployeeLeaveAllocationListView, EmployeeLeaveRequestListView,
    LeaveRequestApprovalListView, UserGivenApprovalsListView,

)


urlpatterns = [
    # LeaveType endpoints
    path('types/', LeaveTypeListCreateView.as_view(), name='leave-type-list-create'),
    path('types/<int:pk>/', LeaveTypeRetrieveUpdateDestroyView.as_view(), name='leave-type-detail'),
    
    # LeaveAllocation endpoints
    path('allocations/', LeaveAllocationListCreateView.as_view(), name='leave-allocation-list-create'),
    path('allocations/<int:pk>/', LeaveAllocationRetrieveUpdateDestroyView.as_view(), name='leave-allocation-detail'),
    path('employees/<int:employee_id>/allocations/', EmployeeLeaveAllocationListView.as_view(), name='employee-leave-allocations'),
    
    # LeaveRequest endpoint
    path('requests/', LeaveRequestListCreateView.as_view(), name='leave-request-list-create'),
    path('requests/<int:pk>/', LeaveRequestRetrieveUpdateDestroyView.as_view(), name='leave-request-detail'),
    path('employees/<int:employee_id>/requests/', EmployeeLeaveRequestListView.as_view(), name='employee-leave-requests'),

    # LeaveApproval endpoints
    path('approvals/', LeaveApprovalListCreateView.as_view(), name='leave-approval-list-create'),
    path('approvals/<int:pk>/', LeaveApprovalRetrieveUpdateDestroyView.as_view(), name='leave-approval-detail'),
    path('requests/<int:leave_request_id>/approvals/', LeaveRequestApprovalListView.as_view(), name='leave-request-approvals'),
    path('users/<int:user_id>/given-approvals/', UserGivenApprovalsListView.as_view(), name='user-given-approvals'),
]

