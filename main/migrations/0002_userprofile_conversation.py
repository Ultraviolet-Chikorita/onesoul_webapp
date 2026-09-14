from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "user_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("date_of_birth", models.DateField()),
                ("username", models.CharField(max_length=50, unique=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("email", models.EmailField(max_length=254)),
                ("gender", models.CharField(max_length=10)),
                ("race", models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Conversation",
            fields=[
                (
                    "conversation_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("compatibility_verdict", models.TextField()),
                ("compatibility_score", models.IntegerField()),
                ("full_conversation", models.TextField()),
                ("summary", models.TextField()),
                ("first_date_ideas", models.TextField()),
                ("conversation_hash", models.CharField(max_length=64, unique=True)),
                (
                    "match_person_1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conversations_as_person_1",
                        to="main.userprofile",
                    ),
                ),
                (
                    "match_person_2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conversations_as_person_2",
                        to="main.userprofile",
                    ),
                ),
            ],
        ),
    ]
