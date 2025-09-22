from django.urls import path
from users.rest.views.users import (
    UserRoleListCreateView, UserRoleRetrieveUpdateDestroyView,
    TeamListCreateView, TeamRetrieveUpdateDestroyView,
    UserListCreateView, UserRetrieveUpdateDestroyView,
    UserTeamListView
)

urlpatterns = [
    # UserRole endpoints
    path('roles/', UserRoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', UserRoleRetrieveUpdateDestroyView.as_view(), name='role-detail'),
    
    # Team endpoints
    path('teams/', TeamListCreateView.as_view(), name='team-list-create'),
    path('teams/<int:pk>/', TeamRetrieveUpdateDestroyView.as_view(), name='team-detail'),
    
    # User endpoints
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    path('teams/<int:team_id>/users/', UserTeamListView.as_view(), name='team-users-list'),
]