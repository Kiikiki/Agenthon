from google import genai
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

apiKey = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=apiKey)

def extractEventDetails(emails, client):
    combinedContent = ""

    for i, email in enumerate(emails):
        combinedContent += f"[Email {i + 1}]\n {email}\n\n"

    prompt = f"""
        Extract events from the emails below.

        Return ONLY a valid JSON array:
        
        Format:
        [
        {{
            "eventName": "...",
            "organization": "...",
            "dateTime": "DD-MM-YYYY HH:MM"
        }}
        ]

        If no event in an email, skip it.

        Emails:
        {combinedContent}
    """

    try:
        response = client.chat.completions.create(
            model = "llama-3.1-8b-instant",
            messages = [
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"{bcolors.red}[API Error]{bcolors.ENDC} {e}")
        return "[]"

def displayEvent(eventList):
    if not eventList:
        print("No events found in recent emails")
        return

    print("\nUpcoming Events from Emails:")
    for idx, event in enumerate(eventList, 1):
        print(f"{idx}. {event['eventName']} - {event['organization']} on {event['dateTime']}")

def addEvent(eventList, recentEmails, client):
    eventInfo = extractEventDetails(recentEmails, client)
    try:
        cleanData = cleanJson(eventInfo)
        events = json.loads(cleanData)

        for event in events:
            if event and not isDuplicate(event, eventList):
                eventList.append(event)
    
    except Exception as e:
        print(f"{bcolors.red}[Error]{bcolors.ENDC} Failed to extract events: {e}")

def isDuplicate(newEvent, eventList):
    for event in eventList:
        if (
            event["eventName"].strip().lower() == newEvent["eventName"].strip().lower()
            and event["dateTime"].strip().lower() == newEvent["dateTime"].strip().lower()
        ):
            return True
    return False

def cleanJson(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    start = text.find('[')
    end = text.rfind(']') + 1

    if start != -1 and end != -1:
        return text[start:end]

    return text