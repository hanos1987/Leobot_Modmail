import praw
from config import reddit_config, openai_config

reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["client_secret"],
    username=reddit_config["username"],
    password=reddit_config["password"],
    user_agent=reddit_config["user_agent"]
)

print(f"Logged in as: {reddit.user.me()}")
subreddit = reddit.subreddit("YOUR_SUBREDDIT_NAME")
print(f"Subreddit: {subreddit.display_name}")

for conversation in subreddit.modmail.conversations(state="all"):
    print(f"Conversation from {conversation.authors[0].name}")
