
from rest_framework import serializers
from core.models import UserProfile
from django.contrib.auth import get_user_model
User = get_user_model()



class UserAccountDetailsSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    has_platform_access = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'is_staff', 'username', 'first_name', 'email', 'groups', 
            'has_platform_access', 'permissions', 'profile'
        ]

    def get_has_platform_access(self, obj):
        return obj.platform_access.filter(status='approved', access_level='view_platform').exists()
    
    def get_permissions(self, obj):
        return []
    
    def get_groups(self, obj):
        return []

    def get_profile(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        editor = {
            "isEditor": profile.is_editor
        }
        return editor