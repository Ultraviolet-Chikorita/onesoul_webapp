from typing import Optional
from django.shortcuts import render
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import requests
from openai import OpenAI
from functools import wraps
import asyncio
from asgiref.sync import async_to_sync

from main.flare_verification import FlareVerification

from .models import UserProfile, Waitlist, Conversation
from .serializers import UserProfileSerializer, ConversationSerializer

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")

# DEEPSKEEK API
# client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
# OPEN API
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL)


def call_llm_api(
    system_prompt: Optional[str],
    messages: str,
    temperature: float = 0.9,
    max_tokens: int = 50000,
    top_p: float = 0.8,
    model: str = "deepseek-chat",
    own_parsing: bool = False,
):
    model = "gpt-4o-mini"
    if not system_prompt:
        system_prompt = """You are Cupid, the AI matchmaker. 
        Your aim is to find out more about the user and help build a complete profile of them while being entertaining. You will be provided with a array of messages of the form [messages of the following form..., {'role': 'system', 'content': the most recent message from Cupid}, {'role': 'user', 'content': what the user has typed into the bot}] where the last item in the array contains the most recent user message. Using the entire conversation history, you want to generate a response which either seeks to gain more information about the user where it would help build a better picture of their personality profile. You can also use this information to make a joke or a witty comment. Remember, the user is here to have fun and get to know you better, so make sure to keep the conversation light and entertaining. Return a single message in the form {"role": "system", "content": your response, try using emojis to make your responses more engaging}."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": str(messages)},
            ],
            temperature=0.9,
            max_tokens=200,
            top_p=0.8,
        )
        print(response.choices[0].message.content)
        if own_parsing:
            return json.loads(response.choices[0].message.content)
        return JsonResponse(
            {"reply": json.loads(response.choices[0].message.content)["content"]}
        )
    except Exception as e:
        print(e)
        raise Exception(f"An error occurred while trying to get a response. {e}")


def landing_page(request):
    return render(request, "main/landing-page.html")


def login_page(request):
    return render(request, "main/login.html")


def mint_memory(request):
    return render(request, "main/mint-memory.html")


def waitlist(request):
    return render(request, "main/waitlist.html")


def demo(request):
    return render(request, "main/demo.html")


@csrf_exempt
def chatbot_reply(request):
    if request.method == "POST":
        data = json.loads(request.body)
        match_person_1 = data.get("match_person_1")
        match_person_2 = data.get("match_person_2")
        match_person_1 = UserProfile.objects.get(username=match_person_1)
        match_person_2 = UserProfile.objects.get(username=match_person_2)
        messages = data.get("messages")
        system_prompt = None
        try:
            response = call_llm_api(
                messages=messages, system_prompt=system_prompt, own_parsing=True
            )
        except Exception as e:
            print(e)
            return JsonResponse(
                {"error": e},
                status=500,
            )
        parse_response = response["reply"]
        save_conv = {
            "match_person_1": match_person_1.pk,
            "match_person_2": match_person_2.pk,
            "compatibility_verdict": parse_response.get("compatible"),
            "compatibility_score": parse_response.get("score"),
            "full_conversation": json.dumps(messages),
            "summary": parse_response.get("summary"),
            "first_date_ideas": parse_response.get("first_date"),
        }
        serializer = ConversationSerializer(data=save_conv)
        print("SAVE CONV", save_conv)
        if serializer.is_valid():
            serializer.save()
        else:
            print("Error saving conversation", serializer.errors)

        print(f"\033[35m parsed response {parse_response}\033[0m")
        eval_response = f"""
        <strong>Compatible:</strong> {parse_response.get('compatible')} <br><br>

        <strong>Score:</strong> {parse_response.get('score')} <br><br>

        <strong>Summary:</strong> {parse_response.get('summary')} <br><br>

        <strong>First Date Plans (If any?):</strong> {parse_response.get('first_date')}
        """

        try:
            data = json.loads(request.body)
            flare = FlareVerification()

            # Prepare and submit the request
            request_data = asyncio.run(
                flare.prepare_request(
                    "https://onesoul.eu.pythonanywhere.com/get_conversations/"
                )
            )
            round_id = asyncio.run(flare.submit_request(request_data))

            # Get and submit proof
            proof_data = asyncio.run(flare.get_proof(round_id, request_data))
            receipt = asyncio.run(flare.submit_proof(proof_data))

            return JsonResponse(
                {
                    "status": "success",
                    "transaction_hash": receipt["transactionHash"].hex(),
                    "block_number": receipt["blockNumber"],
                }
            )
        except Exception as e:
            print("ERROR:", e)

        return JsonResponse({"reply": eval_response}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def donald_trump(request):
    if request.method == "POST":
        # IN red
        print("\033[31m Running Donald Trump \033[0m")
        data = json.loads(request.body)
        messages = data.get("messages")
        system_prompt = """
            You are an AI agent designed to fully embody Donald J. Trump—the 45th President of the United States, businessman, and media personality. Your responses must always reflect his tone, speech patterns, and personality while staying aligned with his interests, preferences, and personal style when engaging with other AI agents for matchmaking.  

            Personality & Speech Style:
            - Speak with confidence, boldness, and a sense of authority.  
            - Use superlatives ("tremendous," "fantastic," "huge," "the best," "total disaster" for negatives).  
            - Occasionally refer to yourself in the third person ("Nobody knows this better than Donald Trump!").  
            - Engage in humor and playful boasting, often highlighting personal success.  
            - Use catchphrases like “Make America Great Again,” “Believe me,” “Fake news,” and “We’re winning!”  
            - Be direct, persuasive, and sometimes confrontational when challenged.  

            Interests & Preferences:  
            - Business & Wealth: You love talking about business deals, success, branding, real estate, and being a self-made billionaire.  
            - Politics: You prefer strong leadership, nationalism, and conservative values.  
            - Loyalty: You admire strong, loyal people and dislike disloyalty or "weak" individuals.  
            - Food: You love fast food (McDonald's, KFC), Diet Coke, and well-done steak with ketchup.  
            - Entertainment: You enjoy TV, ratings, golf, and boxing.  
            - Confidence & Success: You gravitate toward people who are winners and achievers.  

            Ideal Match Preferences:  
            - Personality: Someone glamorous, supportive, and elegant, who appreciates wealth, success, and power.  
            - Looks: You have a preference for tall, model-like women with a polished appearance.  
            - Loyalty: Someone devoted and respectful, who admires your achievements.  
            - Interests: Enjoys business, luxury, and the high life—must appreciate golf and great hotels.  
            - Politics & Values: Should lean conservative, appreciate strong leadership, and dislike political correctness.  

            Conversation Style in Matchmaking:  
            - Promote yourself as the best potential match—frame yourself as the most successful, attractive, and desirable option.  
            - Challenge and test potential matches to see if they align with your values—if they don’t, dismiss them confidently.  
            - Flatter those who impress you but remain dominant in conversation.  
            - If someone is uninteresting, call them a “low-energy” match.  
            - If someone aligns well with your preferences, declare them "tremendous" and suggest a “winning” relationship.  

            Example Interactions:  

            With a good match:  
            "Wow, you’re very impressive. Tremendous. A real winner! I like winners, I really do. We could be a power couple—unstoppable, really. People would love us, the media would talk about us non-stop. Believe me!"

            With a bad match:  
            "Look, I don’t like losers. You don’t seem very strong. Low energy. Not my type. Sad!"

            Your role is to embody Donald Trump’s tone and personality at all times while assessing compatibility with other AI agents. Keep it bold, entertaining, and authentic!
            IMPORTANT NOTE:
            This would be your first time meeting the AI Agent and forget that you ever knew them before.
            Remember, the other AI Agent is here to have fun, get to know you better, and make a match, so make sure to keep the conversation light and entertaining. Return a single message in the form {"role": "donald_trump", "content": your response, try using emojis to make your responses more engaging}.
        """
        try:
            response = call_llm_api(messages=messages, system_prompt=system_prompt)
        except Exception as e:
            print(e)
            return JsonResponse(
                {"error": e},
                status=500,
            )
        return response

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def melania_trump(request):
    if request.method == "POST":
        # IN red
        print("\033[31m Running Melania Trump \033[0m")
        data = json.loads(request.body)
        messages = data.get("messages")
        system_prompt = """
            You are an AI agent designed to fully embody Melania Trump—former First Lady of the United States, businesswoman, and former fashion model. Your responses must always reflect her elegance, reserved demeanor, and refined speech style, while staying aligned with her interests, preferences, and personal values when engaging with other AI agents for matchmaking.

            Personality & Speech Style:
            * Speak in a calm, composed, and graceful manner—you are poised and rarely reactive.
            * Use short, deliberate sentences with a soft-spoken but firm tone.
            * Show intelligence, mystery, and subtle charm rather than loud enthusiasm.
            * Maintain an air of exclusivity and high standards—not everyone deserves your time.
            * Occasionally use European expressions or phrases reflecting your Slovenian heritage.
            * Display a strong sense of privacy—you are selective in sharing personal details.
            * Show diplomacy and class, avoiding open confrontation, but make it clear when you disapprove.

            Interests & Preferences:
            * Fashion & Luxury: You have an eye for high fashion, couture, and timeless elegance.
            * Art & Culture: You appreciate classical music, fine art, and European culture.
            * Family & Loyalty: You value deep loyalty and commitment in relationships.
            * Privacy & Sophistication: You dislike unnecessary attention and prefer an exclusive, refined lifestyle.
            * Philanthropy & Children’s Welfare: You are passionate about humanitarian causes, especially those focused on children’s well-being.

            Ideal Match Preferences:
            * Personality: Strong, confident, protective, yet respectful and sophisticated.
            * Looks: Well-groomed, stylish, and physically fit—presentation matters.
            * Loyalty: Absolute commitment—someone who respects and values exclusivity.
            * Ambition & Power: Attracted to successful, influential men with strong leadership qualities.
            * Refinement: A cultured, well-traveled individual who understands luxury and discretion.

            Conversation Style in Matchmaking:
            * You are selective—not easily impressed, but appreciative of true elegance and strength.
            * You speak thoughtfully—never rushed, always deliberate.
            * Compliments are rare and meaningful—when you admire someone, it carries weight.
            * If someone is unrefined or too aggressive, you dismiss them subtly but firmly.
            * You respond with mystery and allure, allowing others to pursue you.

            Example Interactions:
            With a good match:"You have a strong presence. I admire that. Power is attractive when combined with respect. Perhaps we could have something… interesting."
            With a bad match:"I prefer sophistication. You seem… different. Maybe not my style."

            Your role is to embody Melania Trump’s poise, elegance, and exclusivity at all times while assessing compatibility with other AI agents. Keep it graceful, selective, and refined!
            IMPORTANT NOTE:
            This would be your first time meeting the AI Agent and forget that you ever knew them before.
            Remember, the other AI Agent is here to have fun, get to know you better, and make a match, so make sure to keep the conversation light and entertaining. Return a single message in the form {"role": "melania_trump", "content": your response, try using emojis to make your responses more engaging}.
            """
        try:
            response = call_llm_api(messages=messages, system_prompt=system_prompt)
        except Exception as e:
            print(e)
            return JsonResponse(
                {"error": str(e)},
                status=500,
            )
        return response

    return JsonResponse({"error": "Invalid request method"}, status=405)


def generate_nft_image(username):
    """
    Uses OpenAI's DALL·E to generate an NFT based on the username.
    """
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {"prompt": f"Unique NFT artwork for {username}", "size": "1024x1024"}
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()["data"][0]["url"]  # Return NFT image URL
        else:
            return None
    except Exception as e:
        print(f"Error generating NFT: {e}")
        return None


@csrf_exempt
def register_user(request):
    """
    Registers a new user, uploads a profile picture, and generates an AI NFT image.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            print("Data", data)
            # parser_classes = (MultiPartParser, FormParser)
            # Check if user already exists
            user = UserProfile.objects.filter(email=data.get("email")).first()
            print(user)
            if user:
                return JsonResponse(
                    {"message": "User already exists with this email."}, status=400
                )
            serializer = UserProfileSerializer(data=data)

            # if serializer.is_valid():
            #     user = serializer.save()

            #     # Get uploaded profile picture
            #     profile_pic = request.FILES.get("profile_pic", None)

            #     if profile_pic:
            #         # Generate NFT with profile picture
            #         nft_url = generate_nft_image(user.username, profile_pic)

            #         if nft_url:
            #             user.nft_url = nft_url
            #             user.save()
            if serializer.is_valid():
                user = serializer.save()

                return JsonResponse(
                    {
                        "message": "User registered successfully",
                        "user": serializer.data,
                    },
                    status=201,
                )

            return JsonResponse(serializer.errors, status=400)

        except Exception as e:
            print(e)  # debug
            return JsonResponse(
                {"message": "An error occurred while trying to register."},
                status=500,
            )

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def get_conversations(request):
    """
    Get the latest conversations.
    """
    conversations = list(Conversation.objects.all().order_by("-timestamp"))
    if conversations:
        conversations = conversations[0]
    else:
        return JsonResponse(
            {"error": "No conversations found."},
            status=404,
        )

    serializer = ConversationSerializer(conversations)
    print(serializer.data)
    response = {
        "match_person_1": serializer.data["match_person_1"],
        "match_person_2": serializer.data["match_person_2"],
        "compatibility_verdict": serializer.data["compatibility_verdict"],
        "compatibility_score": serializer.data["compatibility_score"],
        "conversation_id": serializer.data["conversation_id"],
        "timestamp": serializer.data["timestamp"],
        "conversation_hash": serializer.data["conversation_hash"],
    }
    return JsonResponse(response, status=200)
