# modmail_bot.py (Leobot)
import praw
import time
from datetime import datetime, timedelta
from openai import OpenAI
from config import reddit_config, openai_config

# Reddit setup using config values
reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["client_secret"],
    username=reddit_config["username"],
    password=reddit_config["password"],
    user_agent=reddit_config["user_agent"]
)

# OpenAI setup using config values
client = OpenAI(api_key=openai_config["api_key"])

# Set the subreddit to SleepTokenTheory
subreddit = reddit.subreddit("SleepTokenTheory")

# Store conversation state (conversation ID -> last message time)
conversation_tracker = {}

def generate_ai_response(message, is_follow_up=False):
    if is_follow_up:
        prompt = "You’re Leobot, a modmail assistant. The user hasn’t replied in a while. Send a polite, engaging follow-up to keep the chat going."
    else:
        prompt = "You’re Leobot, a modmail assistant. Respond politely but firmly to annoying users."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

def check_modmail():
    current_time = datetime.now()

    # Check for messages from u/rubber_duck_army
    for conversation in subreddit.modmail.conversations(state="all"):
        author_name = conversation.authors[0].name
        convo_id = conversation.id

        if author_name == "rubber_duck_army":
            # Handle new or unread messages
            if conversation.last_updated and convo_id not in conversation_tracker:
                last_message_time = datetime.fromtimestamp(float(conversation.last_updated))
                conversation_tracker[convo_id] = last_message_time
                print(f"New message from {author_name}: {conversation.messages[-1].body}")
                ai_reply = generate_ai_response(conversation.messages[-1].body)
                conversation.reply(ai_reply)
                conversation_tracker[convo_id] = datetime.now()
                conversation.read()

            # Check for inactivity and send follow-up
            elif convo_id in conversation_tracker:
                last_active = conversation_tracker[convo_id]
                if current_time - last_active > timedelta(minutes=5):
                    print(f"5 minutes passed, sending follow-up to {convo_id}")
                    follow_up_message = "Just checking in—any thoughts on this?"
                    ai_reply = generate_ai_response(follow_up_message, is_follow_up=True)
                    conversation.reply(ai_reply)
                    conversation_tracker[convo_id] = datetime.now()
        else:
            print(f"Ignoring message from {author_name} (not u/rubber_duck_army)")

# Initial check to confirm login and subreddit access
print(f"Logged in as: {reddit.user.me()}")
print(f"Subreddit: {subreddit.display_name}")

# Main loop
while True:
    check_modmail()
    time.sleep(60)
