from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("mint-memory/", views.mint_memory, name="mint_memory"),
    path("waitlist/", views.waitlist, name="waitlist"),
    path("demo/", views.demo, name="demo"),
    path("chatbot-reply/", views.chatbot_reply, name="chatbot_reply"),
    path("donald_trump/", views.donald_trump, name="donald_trump"),
    path("melania_trump/", views.melania_trump, name="melania_trump"),
    path("register/", views.register_user, name="register"),
    path("get_conversations/", views.get_conversations, name="get_conversations"),
]
