from groq import Groq
from dotenv import load_dotenv
import os
import time
import json

class bcolors:
    red = "\033[91m"
    green = "\033[92m"
    blue = "\033[94m"
    yellow = "\033[93m"
    ENDC = "\033[0m"

apiKey = os.getenv("GroQ_API_KEY")
client = Groq(api_key=apiKey)

def extractEvent(email, Client):
    email = email[:1000]

    prompt = f"""
    Extract ONE event from this email.

    STRICT RULES:
    - Output EXACTLY one line
    - Format MUST be:
    eventName | organization | DD-MM-YYYY HH:MM
    - If ANY field is missing → return EXACTLY: NONE
    - Do NOT explain
    - Do NOT add extra text
    - Do NOT guess

    Email:
    {email}
    """

    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        messages = [
            {"role": "system", "content": "You are a strict event extraction tool. Follow the rules precisely. No explanations, no extra text, just the event details in the specified format."},
            {"role": "user", "content": prompt}
        ],
        temperature = 0
    )

    return response.choices[0].message.content.strip()

def extractEventDetails(text):
    if text == "NONE" or "none" in text.lower() or "|" not in text or len(text.split("|")) != 3:
        return None
    
    try:
        name, org, dt = [x.strip() for x in text.split("|")]
        return {
            "eventName": name,
            "organization": org,
            "dateTime": dt
        }
    except:
        return None

def displayEvent(eventList):
    if not eventList:
        print("No events found in recent emails")
        return

    print("\nUpcoming Events from Emails:")
    for idx, event in enumerate(eventList, 1):
        print(f"{idx}. {event['eventName']} - {event['organization']} on {event['dateTime']}")

def addEvent(eventList, recentEmails, client):
    for email in recentEmails:
        snippet = email.get("snippet", "")
        raw = extractEvent(snippet, client)
        event = extractEventDetails(raw)

        if event and not isDuplicate(event, eventList):
            eventList.append(event)
            print(f"{bcolors.green}[Assistant]{bcolors.ENDC} Added an event")

def isDuplicate(newEvent, eventList):
    for event in eventList:
        if (
            event["eventName"].strip().lower() == newEvent["eventName"].strip().lower()
            and event["dateTime"].strip().lower() == newEvent["dateTime"].strip().lower()
        ):
            return True
    return False
