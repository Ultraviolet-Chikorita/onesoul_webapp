from rest_framework import serializers
from .models import UserProfile, Conversation


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"  # Include all fields
        read_only_fields = ["timestamp", "user_id"]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"  # Include all fields
        read_only_fields = ["conversation_id", "timestamp", "conversation_hash"]
