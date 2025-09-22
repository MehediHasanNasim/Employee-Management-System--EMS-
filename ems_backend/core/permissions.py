from rest_framework import permissions
from core.choices import Status


def get_user_role_name(user):
    return getattr(getattr(user, "role", None), "name", None)


def get_action(request, view):
    if request.method == "GET":
        if hasattr(view, "get_object"):
            return "retrieve"
        return "list"
    if request.method == "POST":
        return "create"
    if request.method in ["PUT", "PATCH"]:
        return "update"
    if request.method == "DELETE":
        return "destroy"
    return None


class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_user_role_name(request.user) == "HR"
        )


class IsTeamLead(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_user_role_name(request.user) == "Team Lead"
        )


class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_user_role_name(request.user) == "Employee"
        )
    

class IsTeamLeadOfEmployee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "team"):
            return obj.team and obj.team.team_lead == request.user
        elif hasattr(obj, "employee"):
            return obj.employee.team and obj.employee.team.team_lead == request.user
        return False
    

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "employee"):
            return obj.employee == request.user
        elif hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user


class UserPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        if role == "HR":
            return True
        if role == "Team Lead" and action == "list":
            return True
        if role == "Employee" and action in ["retrieve", "update", "partial_update"]:
            return True

        return False
    
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        if role == "HR":
            return True
        if role == "Team Lead" and getattr(obj, "team", None) == getattr(
            request.user, "team", None
        ):
            return action == "retrieve"
        if role == "Employee" and obj == request.user:
            return action in ["retrieve", "update", "partial_update"]

        return False
    

class TeamPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        # Only HR can manage teams
        if role == "HR":
            return True

        # Others can only list/view teams
        return action in ["list", "retrieve"]

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or get_user_role_name(request.user) == "HR":
            return True
        return get_action(request, view) == "retrieve"
    


class LeaveAllocationPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        if role == "HR":
            return True
        if role == "Employee" and action == "list":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or get_user_role_name(request.user) == "HR":
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        if role == "Employee" and obj.employee == request.user:
            return action == "retrieve"

        return False



class LeaveRequestPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        role = get_user_role_name(request.user)
        # action = get_action(request, view)
        method = request.method  # GET, POST, etc.

        if role == "HR":
            return True
        if role == "Team Lead" and method in ["GET", "POST"]:
            return True
        if role == "Employee" and method in ["GET", "POST"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or get_user_role_name(request.user) == "HR":
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        # Team Lead can approve/reject requests from their team members
        if (
            role == "Team Lead"
            and obj.employee.team == getattr(request.user, "team", None)
            and obj.employee != request.user
        ):
            return action in ["retrieve", "update", "partial_update"]

        # Employees can only view their own requests
        if role == "Employee" and obj.employee == request.user:
            return action in ["retrieve", "list"]

        return False
    


class LeaveApprovalPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        if role == "HR":
            return True
        if role == "Team Lead" and action in ["list", "create"]:
            return True
        if role == "Employee" and action == "list":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or get_user_role_name(request.user) == "HR":
            return True

        role = get_user_role_name(request.user)
        action = get_action(request, view)

        # Team Lead can manage approvals for their team members' requests
        if (
            role == "Team Lead"
            and obj.leave_request.employee.team == getattr(request.user, "team", None)
            and obj.leave_request.employee != request.user
        ):
            return action in ["retrieve", "update", "partial_update"]

        # Employees can only view approvals for their own requests
        if role == "Employee" and obj.leave_request.employee == request.user:
            return action == "retrieve"

        return False

