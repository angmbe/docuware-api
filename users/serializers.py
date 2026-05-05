# users/serializers.py
from rest_framework import serializers
from .models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    profileID = serializers.IntegerField(source='profileid', read_only=True)
    profileName = serializers.CharField(source='profilename', read_only=True)

    class Meta:
        model = Profile
        fields = ['profileID', 'profileName']

class UserSerializer(serializers.ModelSerializer):
    userID = serializers.IntegerField(source='userid', read_only=True)
    userName = serializers.CharField(source='username', read_only=True)
    fullName = serializers.CharField(source='fullname', read_only=True)
    profileID = serializers.IntegerField(source='profile_id', read_only=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['userID', 'userName', 'fullName', 'status', 'profileID', 'profile']
