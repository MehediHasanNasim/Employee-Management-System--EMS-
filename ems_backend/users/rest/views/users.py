from rest_framework import generics, status
from rest_framework.response import Response
from users.models import User, Team, UserRole
from users.rest.serializers.users import UserSerializer, TeamSerializer, UserRoleSerializer
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

class UserRoleRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer


# Team Views
class TeamListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class TeamRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


# User views
class UserListCreateView(ActiveQuerysetMixin, generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroyView(ActiveQuerysetMixin, SoftDeleteMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserTeamListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        team_id = self.kwargs['team_id']
        qs = super().get_queryset()  # ActiveQuerysetMixin applies Status.ACTIVE
        return qs.filter(team_id=team_id)