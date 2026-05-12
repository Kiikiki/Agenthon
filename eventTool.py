from google import genai
from dotenv import load_dotenv
import os
import time

class bcolors:
    red = "\033[91m"
    green = "\033[92m"
    blue = "\033[94m"
    yellow = "\033[93m"
    ENDC = "\033[0m"

apiKey = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=apiKey)

def sortEmailEvent(emailContent, client):
    prompt = f"""
    Extract event if present.

    STRICT RULES:
    - First line MUST be exactly: Event | Organization | DD-MM-YYYY HH:MM
    - Use "|" as separator ONLY
    - No extra text before or after
    - If no event → reply EXACTLY: No event

    Email:
    {emailContent}
    """
    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = prompt
        )
    
    except Exception as e:
        time.sleep(40)

        try:
            response = client.models.generate_content(
                model = "gemini-2.5-flash",
                contents = prompt
            )
            return response.text.strip()
        except:
            return "No event"
        

    return response.text.strip()

def extractEventDetails(eventInfo):
    if "No event" in eventInfo.lower():
        return None

    try:
        info = eventInfo.split("|")
        if len(info) < 3:
            print(f"{bcolors.red}[Error extracting] {bcolors.ENDC}Invalid event format")
            return None
        
        eventName = info[0].strip()
        organization = info[1].strip()
        dateTime = info[2].strip()

        return {
            "eventName": eventName,
            "organization": organization,
            "dateTime": dateTime,
        }
    
    except Exception as e:
        print(f"{bcolors.red}[Error extracting] {bcolors.ENDC}{e}")
        return None
    
def displayEvent(eventList):
    if not eventList:
        print("No events found in recent emails")
        return

    print("\nUpcoming Events from Emails:")
    for idx, event in enumerate(eventList, 1):
        print(f"{idx}. {event['eventName']} - {event['organization']} on {event['dateTime']}")
        if event['description']:
            print(f"   Description: {event['description']}")

def addEvent(eventList, recentEmails, client):
    for email in recentEmails:
        eventInfo = sortEmailEvent(email, client)
        eventDetails = extractEventDetails(eventInfo)
        if eventDetails and not isDuplicate(eventDetails, eventList):
            eventList.append(eventDetails)

def isDuplicate(newEvent, eventList):
    for event in eventList:
        if (
            event["eventName"].strip().lower() == newEvent["eventName"].strip().lower()
            and event["dateTime"].strip().lower() == newEvent["dateTime"].strip().lower()
        ):
            return True
    return False