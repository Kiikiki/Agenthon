from google import genai
from emailTool import authenticateGmail, getEmails, thisWeekEmail
from taskTool import uploadTask, viewTasks, deleteTask, finishTaskManual, finishTaskAgent
from eventTool import displayEvent, addEvent
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

apiKey = os.getenv("GEMINI_API_KEY")

# connection to an LLM
client = genai.Client(api_key=apiKey)

# load emails from both accounts
servicePersonal = authenticateGmail('credentialsPersonal.json', 8080)
serviceWork = authenticateGmail('credentialsWork.json', 0)

print("\nAuthentication successful for both accounts!")

personalMails = getEmails(servicePersonal)
print("\nFetched personal emails...")

workMails = getEmails(serviceWork)
print("\nFetched work emails.")

emails = personalMails + workMails
print("\nCompiled all emails from both accounts.")

recentEmails = thisWeekEmail(emails)
print("\nFiltered emails from the last week.")
print(f"\nYou have {len(recentEmails)} emails from the last week.")

taskList = []
eventList = []

# task
while True:
    print("=== AI Assitant for Task Management ===")
    print("1. check tasks")
    print("2. check events")
    print("3. exit")

    option = input("Enter your choice: ")

    if option == '1':
        while True:
            print("\nWelcome to the Task Management Section!")
            print("1. Upload Task")
            print("2. View Tasks")
            print("3. Delete Task")
            print("4. Mark Task as Completed")
            print("5. Check Task Completion by Email")
            print("6. Go Back")

            choice = input("\nEnter your choice: ") 
            if choice == '1':
                taskList = uploadTask(taskList)
            elif choice == '2':
                viewTasks(taskList)
            elif choice == '3':
                taskList = deleteTask(taskList)
            elif choice == '4':
                finishTaskManual(taskList)
            elif choice == '5':
                finishTaskAgent(taskList, recentEmails, client)
            elif choice == '6':
                print("\nGoing back to main menu...")
                break
    elif option == '2':
        while True:
            print("\nWelcome to the Event Management Section!")
            print("1. Check Events from Emails")
            print("2. View Events")
            print("3. Go Back")

            eventChoice = input("\nEnter your choice: ")
            if eventChoice == '1':
                addEvent(eventList, recentEmails, client)
            elif eventChoice == '2':
                displayEvent(eventList)
            elif eventChoice == '3':
                print("\nGoing back to main menu...")
                break
    elif option == '3':
        print("\nExiting...")
        break


    
