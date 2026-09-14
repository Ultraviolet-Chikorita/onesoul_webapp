from rest_framework import serializers

from .models import Conversation, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["timestamp", "user_id"]


class ConversationSerializer(serializers.ModelSerializer):
    compatibility_score = serializers.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ["conversation_id", "timestamp", "conversation_hash"]

    def validate(self, attrs):
        person_1 = attrs.get("match_person_1")
        person_2 = attrs.get("match_person_2")
        if person_1 is not None and person_1 == person_2:
            raise serializers.ValidationError("A conversation match requires two distinct profiles.")
        return attrs
