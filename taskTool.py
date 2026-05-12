from datetime import datetime
from google import genai
from dotenv import load_dotenv
import os

# color text
class bcolors:
    red = "\033[91m"
    green = "\033[92m"
    blue = "\033[94m"
    yellow = "\033[93m"
    ENDC = "\033[0m"

load_dotenv()

apiKey = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=apiKey)

def uploadTask(taskList):
    task = input("task: ")

    while True:
        deadlineStr = input("deadline (DD-MM-YYYY) | (time): ")
        try:
            deadline = datetime.strptime(deadlineStr, "%d-%m-%Y | %H:%M")
            break
        except ValueError:
            print("Invalid date format. Please try again!")

    print(f"\nTask     : {task}")
    print(f"Deadline : {deadline}")
    confirm = input("Confirm upload? (y/n): ")
    
    if confirm.lower() == 'y':
        taskList.append({
            "task": task,
            "deadline": deadline,
            "status": "pending"
        })
        print("\nTask uploaded successfully!")
    else:
        print("\nTask upload cancelled.")

    return taskList

def viewTasks(taskList):
    if not taskList:
        print("\nEmpty or something wrong with the view tasks function... TwT")
        return

    activeTasks = [task for task in taskList if task['status'] != "completed"]

    if not activeTasks:
        print("\nAll tasks are completed! Great job!")
        return

    print("\nCurrent Tasks:")
    for idx, task in enumerate(activeTasks, 1):
        deadline = task['deadline']
        taskStatus = task['status']

        daysLeft = (deadline - datetime.now()).days
        
        if taskStatus == "completed":
            continue
        elif daysLeft < 0:
            status = f"{bcolors.red}Overdue by {abs(daysLeft)} days ago{bcolors.ENDC}"
        elif daysLeft == 0:
            status = f"{bcolors.yellow}Due Today{bcolors.ENDC}"
        else:
            status = f"{daysLeft} days left"

        print(f"{idx}. {task['task']} - Deadline: {deadline} ({status})")
    
def deleteTask(taskList):
    if not taskList:
        return

    try:
        choice = int(input("\nEnter the number of the task to delete: "))
        if 1 <= choice <= len(taskList):
            deletedTask = taskList.pop(choice - 1)
            print(f"\nTask '{deletedTask['task']}' deleted successfully!")
        else:
            print("\nInvalid choice. Please try again.")
    except ValueError:
        print("\nInvalid input. Please enter a number.")

def finishTaskAgent(taskList, emails, client):
    allEmailsText = ""

    for email in emails:
        snippet = email.get('snippet', '')
        allEmailsText += snippet + "\n"

    for task in taskList:
        if task["status"] == "completed":
            continue

        # LLM
        result = checkTaskCompletion(task['task'], allEmailsText, client)

        if result:
            task['status'] = "completed"
            print(f"\n{bcolors.blue}[Assistant]{bcolors.ENDC} {task['task']} marked as completed!")
            break

def checkTaskCompletion(task, emailContent, client):
    prompt = f"""
    You are an assistant that checks task completion based on email content.
    
    Task: 
    {task}

    Email Content: 
    {emailContent}

    Does the email confirm the task is completed?
    Answer only with: 'yes' or 'no'.
    """

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = prompt
    )

    answer = response.text.strip().lower()

    return "yes" in answer
    

def finishTaskManual(taskList):
    if not taskList:
        return

    try:
        choice = int(input("\nEnter the index of the task to mark as finished: "))
        if 1 <= choice <= len(taskList):
            taskList[choice - 1]['status'] = "completed"
            print(f"\nTask '{taskList[choice - 1]['task']}' marked as completed!")
        else:
            print(f"\n{bcolors.red}Invalid choice. Please try again.{bcolors.ENDC}")
    except ValueError:
        print(f"\n{bcolors.red}Invalid input. Please enter a number.{bcolors.ENDC}")
