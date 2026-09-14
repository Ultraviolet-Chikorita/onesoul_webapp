from datetime import date

from django.test import TestCase

from .models import Conversation, UserProfile
from .serializers import ConversationSerializer


class ConversationSerializerTests(TestCase):
    def setUp(self):
        self.alice = UserProfile.objects.create(
            first_name="Alice",
            last_name="Example",
            date_of_birth=date(2000, 1, 1),
            username="alice",
            email="alice@example.com",
            gender="female",
        )
        self.bob = UserProfile.objects.create(
            first_name="Bob",
            last_name="Example",
            date_of_birth=date(2000, 2, 2),
            username="bob",
            email="bob@example.com",
            gender="male",
        )

    def payload(self, **overrides):
        data = {
            "match_person_1": self.alice.pk,
            "match_person_2": self.bob.pk,
            "compatibility_verdict": "Potential match",
            "compatibility_score": 75,
            "full_conversation": "Hello there",
            "summary": "A short conversation",
            "first_date_ideas": "Coffee",
        }
        data.update(overrides)
        return data

    def test_score_must_stay_in_ui_contract_range(self):
        low = ConversationSerializer(data=self.payload(compatibility_score=-1))
        high = ConversationSerializer(data=self.payload(compatibility_score=101))

        self.assertFalse(low.is_valid())
        self.assertFalse(high.is_valid())
        self.assertIn("compatibility_score", low.errors)
        self.assertIn("compatibility_score", high.errors)

    def test_self_match_is_rejected(self):
        serializer = ConversationSerializer(
            data=self.payload(match_person_2=self.alice.pk)
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_valid_match_can_be_saved(self):
        serializer = ConversationSerializer(data=self.payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)

        conversation = serializer.save()

        self.assertEqual(conversation.compatibility_score, 75)
        self.assertEqual(len(conversation.conversation_hash), 64)


class ConversationHashTests(TestCase):
    def setUp(self):
        self.alice = UserProfile.objects.create(
            first_name="Alice",
            last_name="Example",
            date_of_birth=date(2000, 1, 1),
            username="alice-hash",
            email="alice-hash@example.com",
            gender="female",
        )
        self.bob = UserProfile.objects.create(
            first_name="Bob",
            last_name="Example",
            date_of_birth=date(2000, 2, 2),
            username="bob-hash",
            email="bob-hash@example.com",
            gender="male",
        )

    def make_conversation(self, score):
        return Conversation.objects.create(
            match_person_1=self.alice,
            match_person_2=self.bob,
            compatibility_verdict="Potential match",
            compatibility_score=score,
            full_conversation="Same transcript",
            summary="Same summary",
            first_date_ideas="Coffee",
        )

    def test_hash_is_stable_for_same_semantic_payload(self):
        first = self.make_conversation(70)
        expected_hash = first.conversation_hash
        first.delete()
        second = self.make_conversation(70)

        self.assertEqual(second.conversation_hash, expected_hash)

    def test_hash_changes_when_scored_outcome_changes(self):
        first = self.make_conversation(70)
        first_hash = first.conversation_hash
        first.delete()
        second = self.make_conversation(71)

        self.assertNotEqual(second.conversation_hash, first_hash)
