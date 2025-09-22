from rest_framework import generics, status
from rest_framework.response import Response
from users.models import User, Team, UserRole
from users.rest.serializers.users import UserSerializer, TeamSerializer, UserRoleSerializer
from core.permissions import UserPermissions, TeamPermissions, IsHR
from core.permissions import get_user_role_name
from core.choices import Status


# Mixins
class ActiveQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status=Status.ACTIVE)
    
class SoftDeleteMixin:
    def perform_destroy(self, instance):
        instance.status = Status.REMOVED
        instance.save()


# UserRole Views
class UserRoleListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsHR]

class UserRoleRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsHR]


# Team Views
class TeamListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [TeamPermissions]


class TeamRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [TeamPermissions]


# User views
class UserListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermissions]

    def get_queryset(self):
        qs = super().get_queryset()

        # Superusers can see everything
        if self.request.user.is_superuser:
            return qs

        role = get_user_role_name(self.request.user)

        if role == "HR":
            return qs

        if role == "Team Lead":
            return qs.filter(team=self.request.user.team)

        if role == "Employee":
            return qs.filter(id=self.request.user.id)

        return qs.none()
    

class UserRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermissions]


class UserTeamListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermissions]


    def get_queryset(self):
        team_id = self.kwargs['team_id']
        qs = User.objects.filter(status=Status.ACTIVE, team_id=team_id)
        
        # Only allow if user has access to this team
        if (self.request.user.role.name == 'HR' or 
            (self.request.user.role.name == 'Team Lead' and self.request.user.team_id == team_id)):
            return qs
        
        return qs.none()