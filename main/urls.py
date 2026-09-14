from django.urls import path

from . import views
from .access import public_post

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("mint-memory/", views.mint_memory, name="mint_memory"),
    path("waitlist/", views.waitlist, name="waitlist"),
    path("demo/", views.demo, name="demo"),
    path("chatbot-reply/", public_post(views.chatbot_reply), name="chatbot_reply"),
    path("donald_trump/", public_post(views.donald_trump), name="donald_trump"),
    path("melania_trump/", public_post(views.melania_trump), name="melania_trump"),
    path("register/", public_post(views.register_user), name="register"),
    path("get_conversations/", views.get_conversations, name="get_conversations"),
]
