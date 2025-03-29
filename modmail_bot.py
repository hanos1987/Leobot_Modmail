# modmail_bot.py
import praw
import time
from openai import OpenAI
from config import reddit_config, openai_config  # Importing credentials from config.py

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

subreddit = reddit.subreddit("YOUR_SUBREDDIT_NAME")  # Replace with your subreddit

def generate_ai_response(message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You’re a modmail assistant. Respond politely but firmly to annoying users."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

def check_modmail():
    for conversation in subreddit.modmail.conversations(state="new"):
        author_name = conversation.authors[0].name  # Get the sender's username
        if author_name == "rubber_duck_army":  # Only respond to u/rubber_duck_army
            print(f"New message from {author_name}: {conversation.messages[0].body}")
            ai_reply = generate_ai_response(conversation.messages[0].body)
            conversation.reply(ai_reply)
            conversation.read()
        else:
            print(f"Ignoring message from {author_name} (not u/rubber_duck_army)")

while True:
    check_modmail()
    time.sleep(60)  # Check every minute
