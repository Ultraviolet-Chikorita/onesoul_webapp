import hashlib
from django.db import models

# Create your models here.


class Waitlist(models.Model):
    fullname = models.CharField(max_length=100)
    email = models.EmailField()
    date_joined = models.DateTimeField(auto_now_add=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        return (
            self.fullname
            + " | "
            + self.email
            + " | "
            + str(self.date_joined)
            + " | "
            + str(self.date_of_birth)
        )


class UserProfile(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    username = models.CharField(max_length=50, unique=True)
    # profile_img = models.ImageField(upload_to="nfts/")  # Stores NFT as an image file
    # nft_url = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    gender = models.CharField(max_length=10)
    race = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"


class Conversation(models.Model):
    conversation_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    match_person_1 = models.ForeignKey(
        UserProfile, related_name="conversations_as_person_1", on_delete=models.CASCADE
    )
    match_person_2 = models.ForeignKey(
        UserProfile, related_name="conversations_as_person_2", on_delete=models.CASCADE
    )
    compatibility_verdict = models.TextField()
    compatibility_score = models.IntegerField()
    full_conversation = models.TextField()
    summary = models.TextField()
    first_date_ideas = models.TextField()
    conversation_hash = models.CharField(
        max_length=64, unique=True
    )  # Store SHA256 hash

    def save(self, *args, **kwargs):
        # Generate a unique hash based on match_person_1, match_person_2, and conversation_text
        hash_input = f"{self.match_person_1.username}{self.match_person_2.username}{self.full_conversation}{self.compatibility_score}{self.summary}{self.compatibility_verdict}".encode()
        self.conversation_hash = hashlib.sha256(hash_input).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Conversation {self.conversation_id} - {self.match_person_1} & {self.match_person_2}"
