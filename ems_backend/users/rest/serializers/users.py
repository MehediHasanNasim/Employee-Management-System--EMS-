from rest_framework import serializers
from users.models import User, Team, UserRole
from core.choices import Status


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'alias', 'name']

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'alias', 'name', 'description', 'team_lead']

    def validate_team_lead(self, value):
        # Validate that team lead has appropriate role
        if value and value.role.name != 'Team Lead':
            raise serializers.ValidationError("Team lead must have 'Team Lead' role")
        return value
    
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'alias', 'username', 'email', 'first_name', 'last_name', 
                 'password', 'role', 'team', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        if "riseuplabs" not in value:
            raise serializers.ValidationError("Email must contain 'riseuplabs'")
        return value
    
    def validate(self, data):
        role = data.get('role')
        team = data.get('team')
        
        if role and role.name == 'Employee' and not team:
            raise serializers.ValidationError("Employees must belong to a team")
        
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    

