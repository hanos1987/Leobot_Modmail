# modmail_bot.py (Leobot)
import praw
import time
from datetime import datetime, timedelta
from openai import OpenAI
from config import reddit_config, openai_config

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["client_secret"],
    username=reddit_config["username"],
    password=reddit_config["password"],
    user_agent=reddit_config["user_agent"]
)

# Initialize OpenAI client
client = OpenAI(api_key=openai_config["api_key"])

# Set the subreddit to monitor
subreddit = reddit.subreddit("SleepTokenTheory")  # Change to "LeobotTest" if needed

# Dictionary to track conversation activity (conversation ID -> last message time)
conversation_tracker = {}

def generate_ai_response(message, is_follow_up=False):
    """Generate an AI response using OpenAI."""
    if is_follow_up:
        prompt = "You’re Leobot, a modmail assistant. The user hasn’t replied in a while. Send a polite, engaging follow-up to keep the chat going."
    else:
        prompt = "You’re Leobot, a modmail assistant. Respond politely but firmly to annoying users."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"{datetime.now()} - OpenAI API error: {e}")
        return "Sorry, I encountered an error while generating a response."

def check_modmail():
    """Check Modmail for new messages from u/rubber_duck_army and respond."""
    current_time = datetime.now()
    print(f"{current_time} - Checking Modmail for {subreddit.display_name}...")

    try:
        # Fetch all Modmail conversations (new, in progress, archived)
        conversations = list(subreddit.modmail.conversations(state="all"))
        print(f"{current_time} - Found {len(conversations)} Modmail conversations")
        
        if not conversations:
            print(f"{current_time} - No Modmail conversations found")
            return

        for conversation in conversations:
            # Get the author of the conversation
            author_name = conversation.authors[0].name if conversation.authors else "Unknown"
            convo_id = conversation.id
            last_message = conversation.messages[-1].body if conversation.messages else "No messages"
            message_time = datetime.fromtimestamp(float(conversation.last_updated)).strftime("%Y-%m-%d %H:%M:%S")
            message_count = len(conversation.messages)
            is_new = conversation.is_new

            # Log details about the conversation
            print(f"{current_time} - Modmail Conversation {convo_id} from {author_name} (Messages: {message_count}, Is New: {is_new}, Last updated: {message_time}): {last_message[:50]}...")

            # Check if the author is u/rubber_duck_army (case-insensitive)
            if author_name.lower() == "rubber_duck_army".lower():
                # Handle new conversations
                if conversation.last_updated and convo_id not in conversation_tracker:
                    last_message_time = datetime.fromtimestamp(float(conversation.last_updated))
                    conversation_tracker[convo_id] = last_message_time
                    print(f"{current_time} - New Modmail message from {author_name}: {last_message}")
                    ai_reply = generate_ai_response(last_message)
                    print(f"{current_time} - Sending reply: {ai_reply}")
                    try:
                        conversation.reply(ai_reply)
                        print(f"{current_time} - Successfully sent reply to conversation {convo_id}")
                    except Exception as e:
                        print(f"{current_time} - Error sending reply to conversation {convo_id}: {e}")
                    conversation_tracker[convo_id] = datetime.now()
                    conversation.read()

                # Handle follow-ups for existing conversations
                elif convo_id in conversation_tracker:
                    last_active = conversation_tracker[convo_id]
                    if current_time - last_active > timedelta(minutes=5):
                        print(f"{current_time} - 5 minutes passed, sending follow-up to {convo_id}")
                        follow_up_message = "Just checking in—any thoughts on this?"
                        ai_reply = generate_ai_response(follow_up_message, is_follow_up=True)
                        print(f"{current_time} - Sending follow-up reply: {ai_reply}")
                        try:
                            conversation.reply(ai_reply)
                            print(f"{current_time} - Successfully sent follow-up to conversation {convo_id}")
                        except Exception as e:
                            print(f"{current_time} - Error sending follow-up to conversation {convo_id}: {e}")
                        conversation_tracker[convo_id] = datetime.now()
            else:
                print(f"{current_time} - Ignoring Modmail message from {author_name} (not u/rubber_duck_army)")
    except Exception as e:
        print(f"{current_time} - Error checking Modmail: {e}")

# Initial setup logs
print(f"Logged in as: {reddit.user.me()}")
print(f"Subreddit: {subreddit.display_name}")

# Main loop to check Modmail every 60 seconds
while True:
    check_modmail()
    time.sleep(60)
