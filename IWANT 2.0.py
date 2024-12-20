import pyttsx3
import speech_recognition as sr
from datetime import datetime
import os
import random
from requests import get
import wikipedia
import webbrowser
import time
import requests
import pyjokes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import PyPDF2
import pywhatkit as kit
import pyautogui
import sys
import smtplib
from bs4 import BeautifulSoup
import python_weather
import asyncio
from pywikihow import WikiHow
import speedtest
import pyperclip
import psutil
from screen_brightness_control import set_brightness
from translate import Translator
from gtts import gTTS
import pygame
import spacy
import threading
import re
import queue
import sqlite3
from docx import Document

def create_database():
    conn = sqlite3.connect("my_assistant.db")
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserQueries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        response_text TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def store_query(query_text):
    conn = sqlite3.connect("my_assistant.db")
    cursor = conn.cursor()

    # Insert only the query into the table
    cursor.execute("""
    INSERT INTO UserQueries (query_text, timestamp) VALUES (?, ?)
    """, (query_text, datetime.now()))
    
    conn.commit()
    conn.close()
    print(f"Query '{query_text}' saved to database successfully!")


def get_all_queries():
    conn = sqlite3.connect("my_assistant.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM UserQueries")
    queries = cursor.fetchall()
    
    for query in queries:
        print(f"Query: {query[1]} (Response: {query[2]}, Timestamp: {query[3]})")
    
    conn.close()

nlp = spacy.load("en_core_web_sm")


def initialize_tts_engine():
    """Initialize the TTS engine and set the desired voice."""
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')

    # Set desired voice (e.g., David or Hazel based on your system)
    engine.setProperty('voice', voices[1].id)  # Example: voices[1] for David
    return engine


engine = initialize_tts_engine()

def speak(audio):
    """Speak the provided text."""
    engine.say(audio)
    engine.runAndWait()
    print(audio)

def takecommand(max_retries=3):
    """Listen for a command and return the recognized text in lower case."""
    r = sr.Recognizer()
    retries = 0

    while retries < max_retries:
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1

            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=15)
            except sr.WaitTimeoutError:
                print("Timeout. Please try again.")
                retries += 1
                continue

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-US')
            print(f"User said: {query}")
            store_query(query.lower())
            return query.lower()

        except sr.UnknownValueError:
            print("Sorry, I did not understand that. Please try again.")
            retries += 1
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            retries += 1

    print("Maximum retries reached. Exiting.")
    return "none"

def wish():
    hour = int(datetime.now().hour)
    current_time = datetime.now().strftime("%I:%M %p")
    
    # Time-based greeting
    if 0 <= hour < 12:
        speak(f"Good morning sir! It's {current_time}")
    elif 12 <= hour < 18:
        speak(f"Good afternoon sir! It's {current_time}")
    else:
        speak(f"Good evening sir! It's {current_time}")
    
    # List of possible introduction responses
    introductions = [
        "I am I WANT. Please tell me how I can help you.",
        "I am I WANT. How may I assist you today?",
        "I am I WANT, ready to assist you. What can I do for you?",
        "I am I WANT. How can I be of service to you?",
        "Hello, I am I WANT. Let me know what you need help with."
    ]
    
    # Randomly select an introduction response
    speak(random.choice(introductions))
    #speak(f"The current language is {languages[current_language]}.")
    #speak("Say 'change language' to switch languages, or 'exit' to quit.")


def handle_failure():
    speak("Custom failure handler: Taking action after max retries.")
    speak("do you want to continue creative mode, sir?")
    querry = takecommand().lower()
    if "yes" in querry or "absolute" in querry:
       speak("Continuing with creative mode.")
       search_wikihow("creative")
    elif "no" in querry:
       start()


def recognize_intent(user_command):
    # Process the input command using spaCy
    doc = nlp(user_command)

    # Define a set of sample intents
    intents = {
   "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", "howdy", "yo", "what's up", "hiya"],
    

    # Farewell
    "farewell": ["bye", "goodbye", "see you", "later", "take care", "peace out", "adieu", "see ya", "catch you later"],
    "sleep mode": ["sleep","you can go to sleep now"],
    # Time & Date
    "time": ["time", "clock", "what's the time", "current time", "tell me the time", "hour", "minute", "time now", "what time is it", "show me the time"],
    "date": ["date", "today's date", "current date", "calendar", "what's the date", "day", "month", "year", "what day is it", "when is it", "what's today's date"],
    
    # Weather
    "weather": ["weather", "forecast", "rain", "snow", "temperature", "cloudy", "sunny", "storm", "weather report", "weather update", "what's the weather like", "is it raining", "is it cold"],
    
    # News & Information
    "news": ["news", "headlines", "breaking news", "latest news", "what's happening", "current events", "tell me the news", "update", "news update", "give me the news"],
    "search": ["search", "look up", "find", "search for", "google", "look for", "find out", "check", "search online", "find me information on", "what about", "can you look up"],
    
    # Entertainment
    "joke": ["joke", "tell me a joke", "make me laugh", "funny", "humor", "comedy", "tell a funny one", "laugh", "something funny", "humorous"],
    "stop music": ["stop music", "pause music", "stop the song", "pause the song", "stop playing music", "pause the tune", "stop the track", "pause the track", "stop the music player", "stop the song request"],
    "music": ["play music", "song", "music", "play a song", "music player", "tune", "track", "play a tune", "song request", "play my favorite song", "put on music"],
    "game": ["start game", "play a game", "let's play", "begin game", "start the game", "I want to play", "play", "let's start", "start the fun", "game on"],

    # Reminders & Alarms
    "reminder": ["remind me", "reminder", "alert", "notify me", "don't forget", "remember", "schedule", "set reminder", "tell me to", "put it on my list", "alert me to"],
    "alarm": ["set alarm", "wake me up", "alarm", "wake up", "remind me to wake up", "set an alarm", "wake me in the morning", "time to wake up", "set an alarm for"],
    
    # Device & Home Control
    "device control": ["turn on", "turn off", "open", "close", "shut down", "start", "stop", "open app", "close app", "open the lights", "turn on the lights", "dim the lights", "turn off the music", "mute the sound"],
    "volume control": ["volume up", "volume down", "increase volume", "decrease volume", "mute", "unmute", "turn the volume up", "turn the volume down", "raise the volume", "lower the volume"],
    "brightness control": ["increase brightness", "dim the screen", "brightness up", "brightness down", "make it brighter", "make it dimmer", "set screen brightness", "adjust brightness"],
    "screenshot": ["take a screenshot", "capture screen", "screenshot", "capture image", "take a screen capture", "snap a screenshot", "take a snapshot", "capture the screen", "screen capture", "screenshot now"],

    # Calculator & Math
    "calculator": ["calculate", "math", "add", "subtract", "multiply", "divide", "sum", "product", "math calculation", "solve", "plus", "minus", "times", "divided by", "calculate for me"],
    
    # Device Status & Health Check
    "battery": ["battery", "battery status", "how much battery", "battery level", "how much charge", "check battery", "is my battery full", "battery percentage"],
    "device info": ["device info", "system status", "status check", "what's my system info", "how's my device doing", "check my phone", "system check"],
    
    # System Control & Commands
    "shutdown": ["shutdown", "turn off", "power off", "shut down", "turn off the device", "turn off the system", "power off the system", "shutdown now", "end session"],
    "restart": ["restart", "reboot", "reboot system", "restart device", "reboot now", "turn off and on again", "reboot the system"],
    "lock_screen": ["lock screen", "lock the computer", "lock my screen", "lock my PC", "lock the system", "secure screen", "screen lock", "lock my desktop", "secure my computer"],
    "sleep": ["sleep", "put the computer to sleep", "go to sleep", "hibernate", "sleep mode", "turn off the screen", "put my PC to sleep", "put the system to sleep"],
    "switch_window": ["switch window", "next window", "switch to next window", "go to the next window", "switch application", "switch task", "change window", "move to the next window"], 

    "social media": ["social media", "post", "share", "status update", "tweet", "instagram", "facebook", "send a tweet", "make a post", "update my status", "post on social media"],
    
    # Smart Home Devices
    "temperature control": ["temperature", "air conditioner", "thermostat", "set temperature", "adjust temperature", "cool down", "heat up", "set AC to", "turn on AC", "turn off heater"],
    "light control": ["lights", "turn on lights", "turn off lights", "dim lights", "brighten lights", "change lights", "set lights to", "adjust lighting"],
    
    # Location & Navigation
    "location": ["where am I", "what's my location", "location", "where is", "where is the nearest", "what's near me", "how do I get to", "find location", "map location", "find me on the map"],
    "navigation": ["navigate", "directions", "how to get to", "find directions", "get directions", "where is", "what's the best route to", "how far is"],
    
    # Miscellaneous & Fun
    "fun fact": ["fun fact", "interesting fact", "tell me a fun fact", "did you know", "facts", "interesting info", "tell me something interesting"],
    "quote": ["quote", "give me a quote", "inspirational quote", "motivational quote", "quote of the day", "tell me a quote", "show me a quote"],
    "random fact": ["random fact", "tell me something random", "strange fact", "weird fact", "fact of the day"],

    # Location
    "ip_address": ["IP address", "what's my IP", "my IP address", "show my IP", "ip address", "find my IP", "current IP"],
    "internet_speed": ["internet speed", "check internet speed", "how fast is my internet", "network speed", "speed test", "check my speed", "internet connection speed", "download speed", "upload speed", "ping test", "internet performance", "bandwidth", "test my internet"],
    # Clipboard
    "clipboard": ["clipboard", "copy", "paste", "cut", "copy to clipboard", "paste from clipboard", "clear clipboard", "show clipboard contents", "get clipboard", "manage clipboard"],
    
    # File Management
    "file management": ["file", "open file", "close file", "rename file", "move file", "delete file", "copy file", "paste file", "file explorer", "manage files", "list files", "search files"],
    "file_composer": ["create", "write", "draft", "form", "construct", "generate", "develop", "design", "build", "compose", "assemble", "put together", "organize", "create a file", "make a document", "compose a letter", "design a report", "build a presentation"], 
    # System Monitoring
    "system monitor": ["system monitor", "system stats", "performance", "CPU usage", "memory usage", "check system", "check resources", "how's my system", "monitor system", "system performance", "show system status"],
    
    # Timer
    "timer": ["set timer", "countdown", "timer", "start timer", "stop timer", "reset timer", "set countdown", "countdown timer", "timer for", "how much time left", "alarm timer", "set timer for x minutes"],
    
    # Note-Taking
    "note": ["note", "take a note", "write down", "remember", "write a note", "add note", "create note", "note it down", "set note", "save a note", "remind me about"],
    
    # Creative Mode
    "creative mode": ["creative mode", "creative", "creativity", "idea", "let's be creative", "start creative mode", "creativity mode", "open creative mode", "unlock creative mode", "brainstorming mode"],
    
    # Open and Close System Software
    "open software": ["open", "launch", "start", "run", "open software", "open application", "launch program", "run application", "open the app", "start the software"],
    "close software": ["close", "exit", "quit", "close software", "close application", "exit program", "quit application", "shut down software", "end program", "terminate application"],
    
    # Intro of Assistant
    "intro": ["introduce yourself", "who are you", "what can you do", "tell me about yourself", "give me an introduction", "what are your capabilities", "what can I ask you", "tell me more about you", "introduce your features"],
    "owner": ["who is the owner", "tell me about the owner", "who created you", "who made you", "who is behind this", "who developed you", "who is your creator", "who is the person behind you", "tell me about your creator", "who owns you"],

    # PDF Reader
    "pdf": ["read pdf", "open pdf", "view pdf", "read document", "open document", "show me the pdf", "open the pdf file", "read the file", "open my pdf", "pdf viewer"],
    
    # Wikipedia
    "wikipedia": ["wikipedia", "search on wikipedia", "tell me about", "search", "find on wikipedia", "get info from wikipedia", "wikipedia search", "tell me about [topic]", "what is [topic]"],
    
    # Send WhatsApp
    "whatsapp": ["whatsapp", "send message on whatsapp", "whatsapp message", "message on whatsapp", "send text on whatsapp", "whatsapp contact", "send whatsapp to", "whatsapp text", "message via whatsapp", "open whatsapp"],
    
    # Send Email
    "email": ["send email", "email", "send message", "compose email", "send an email", "email to", "send an email to", "compose a message", "email message", "email send", "send an email to [contact]"],
    
    # Reminder and Task Management
    "task": ["task", "to-do list", "task list", "remind me to", "add task", "create task", "task manager", "add to task list", "mark as done", "complete task", "check task", "task reminder"],
    
    # File Conversion
    "file conversion": ["convert file", "convert to", "change file format", "file conversion", "convert to pdf", "convert to image", "convert audio", "convert video", "change format", "convert text", "convert from [file type] to [target type]"],
}

    # Convert user input to lowercase to handle case sensitivity
    user_command_lower = user_command.lower()

    # Check for each intent category
    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_command_lower:
                return intent
    
    return "unknown"

def tell_joke():
    joke = pyjokes.get_joke()  
    speak(joke) 

def tell_joke():    
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don’t skeletons fight each other? They don’t have the guts.",
        "What do you call fake spaghetti? An impasta!"
    ]
    joke = random.choice(jokes)  
    speak(joke)

async def get_temperature(location):
    """Fetch the temperature of a given location from the weather service."""
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        try:
            
            weather = await client.get(location)
            
            
            current_temp = weather.current.temperature
            return f"The current temperature in {location} is {current_temp}°C."
        
        except AttributeError as e:
            
            return f"An error occurred while fetching the temperature: {str(e)}"
        except Exception as e:
            return f"An error occurred while fetching the temperature: {str(e)}"

def process_weather_query(query):
    if "temperature" in query or "weather" in query:
        speak("Which location would you like to check the weather for?")
        location_query = takecommand().lower()  
        
        if location_query:
            
            try:
                temperature = asyncio.run(get_temperature(location_query))
                speak(temperature)
            except RuntimeError:
               
                loop = asyncio.get_event_loop()
                temperature = loop.run_until_complete(get_temperature(location_query))
                speak(temperature)

def pdf_reader():
    speak("Which book should I read, sir?")
    book_path = input("Please enter the path of the book: ")  
    
    try:
        with open(book_path, "rb") as book:  
            pdfreader = PyPDF2.PdfFileReader(book)
            pages = pdfreader.numPages
            speak(f"Total number of pages in this PDF is {pages}.")
            
            speak("Sir, please tell me the page number you want to read.")
            pagetoread = takecommand().lower()  
            
            try:
                page_number = int(pagetoread)  
                if page_number < 1 or page_number > pages:  
                    speak(f"Sorry, this PDF has only {pages} pages. Please provide a valid page number.")
                    return
                
                page = pdfreader.getPage(page_number - 1)  
                text = page.extract_text()
                speak(f"Reading page {page_number}: {text}")
            
            except ValueError:
                speak("Sorry, I could not understand the page number. Please provide a valid number.")
    except FileNotFoundError:
        speak("Sorry, I could not find the book at the specified path.")
    except Exception as e:
        speak(f"An error occurred: {e}")

def set_alarm(alarm_time, purpose):
    speak(f"Alarm is set for {alarm_time}. I'll remind you about {purpose}.")
    
    # Start the alarm checking in a separate thread
    alarm_thread = threading.Thread(target=alarm_function, args=(alarm_time, purpose))
    alarm_thread.start()

def alarm_function(alarm_time, purpose):
    while True:
        current_time = datetime.now().strftime("%H:%M")
        
        # If the current time matches the alarm time, trigger the alarm
        if current_time == alarm_time:
            speak(f"Sorry to disturb you Sir, but it's time for {purpose}!")
            break  # Once the alarm goes off, stop checking
        
        time.sleep(30)  # Check every 30 seconds to avoid overloading the CPU

def handle_alarm_intent():
    try:
        speak("Tell me the time to set the alarm.")
        alarm_time = takecommand().lower()

        # Use regex to validate and convert time format
        match = re.match(r'(\d{1,2}):(\d{2})\s?(am|pm)?', alarm_time)
        if match:
            hour, minute, period = match.groups()

            # Convert time to 24-hour format
            hour = int(hour)
            minute = int(minute)
            
            if period:
                if period.lower() == "pm" and hour != 12:
                    hour += 12
                elif period.lower() == "am" and hour == 12:
                    hour = 0
            alarm_time = f"{hour:02}:{minute:02}"
            
            # Check if the time is valid
            datetime.strptime(alarm_time, "%H:%M")  
            
            speak("What is the alarm for?")
            purpose = takecommand().lower()

            set_alarm(alarm_time, purpose)

            speak(f"The alarm is set for {alarm_time} for {purpose}")
        
        else:
            speak("Sorry, the time format you provided is invalid. Please try again.")

    except ValueError:
        speak("Sorry, the time format you provided is invalid. Please try again.")

def news():
    main_url = "http://newsapi.org/v2/top-headlines?sources=techcrunch&apikey=5f8395144dfe4603bc2420dc724fdc28"
    
    main_page = requests.get(main_url).json()
    articles = main_page["articles"]
    head = []
    day = ["first", "second", "third", "fourth"]
    for ar in articles:
        head.append(ar["title"])  # Corrected key from "titles" to "title"
    for i in range(len(day)):
        if i < len(head):  # Prevent index out of range
            speak(f"Today's {day[i]} news is: {head[i]}")

def send_message():
    
    current_time = datetime.now()
    
    hour = current_time.hour
    minute = current_time.minute + 2

    
    if minute == 60:
        minute = 0
        hour += 1

    
    kit.sendwhatmsg("+923176240916", "This message is sent by I WANT Personal Assistant, owned by Mujeeb Butt", hour, minute)
    print(f"Message will be sent at {hour}:{minute}")

def send_email(to, content, file_path=None):
    try:
        sender_email = "buttmujeeb231@gmail.com"
        app_password = "liau nlwq fusw olcp"  

        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to
        msg['Subject'] = "Automated Email"

       
        msg.attach(MIMEText(content, 'plain'))

       
        if file_path:
            try:
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={file_path.split("/")[-1]}'
                    )
                    msg.attach(part)
            except Exception as e:
                print(f"Error attaching file: {e}")
                return

        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to, msg.as_string())

        print("Email has been sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")

email_directory = {
    "yousaf": "yousafsomro007@gmail.com",
    "jadugar": "jaadugar1577@gmail.com",
    "madad": "madadabbas333@gmail.com"
}  

def check_internet_speed():
    
    st = speedtest.Speedtest()

   
    st.get_best_server()

    
    download_speed_mbps = st.download() / 1_000_000  
    upload_speed_mbps = st.upload() / 1_000_000      


    download_speed_MBps = download_speed_mbps / 8
    upload_speed_MBps = upload_speed_mbps / 8

   
    ping = st.results.ping

    speed_text = f"Download speed is {download_speed_MBps:.2f} Mbps, Upload speed is {upload_speed_MBps:.2f} Mbps, and ping is {ping} milliseconds."

   
    speak(speed_text)
   
def file_management():
    speak("Would you like to list files, create, rename, or delete a file?")
    command = takecommand()
    
    if "list" in command:
        speak("Which directory should I list?")
        directory = input("Enter the directory path: ")
        try:
            files = os.listdir(directory)
            speak(f"Files in {directory} are: {', '.join(files)}")
        except FileNotFoundError:
            speak("Directory not found.")
    
    elif "create" in command:
        speak("Enter the file name with extension.")
        file_name = input("Enter the file name: ")
        with open(file_name, "w") as f:
            speak(f"{file_name} has been created.")
    
    elif "rename" in command:
        speak("Enter the current file name.")
        current_name = input("Enter the current file name: ")
        speak("Enter the new file name.")
        new_name = input("Enter the new file name: ")
        try:
            os.rename(current_name, new_name)
            speak(f"{current_name} has been renamed to {new_name}.")
        except FileNotFoundError:
            speak("File not found.")
    
    elif "delete" in command:
        speak("Enter the file name to delete.")
        file_name = input("Enter the file name: ")
        try:
            os.remove(file_name)
            speak(f"{file_name} has been deleted.")
        except FileNotFoundError:
            speak("File not found.") 

def clipboard_manager():
    speak("Do you want to save or retrieve clipboard content?")
    command = takecommand()
    
    if "save" in command:
        content = pyperclip.paste()
        with open("clipboard_history.txt", "a") as f:
            f.write(content + "\n")
        speak("Clipboard content has been saved.")
    
    elif "retrieve" in command:
        try:
            with open("clipboard_history.txt", "r") as f:
                history = f.readlines()
            speak(f"Clipboard history is: {''.join(history)}")
        except FileNotFoundError:
            speak("No clipboard history found.")

def system_monitoring():
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    speak(f"CPU usage is at {cpu_usage}%. Memory usage is at {memory.percent}%. Disk usage is at {disk.percent}%.")

def adjust_brightness():
    speak("What brightness level would you like? Please provide a percentage.")
    try:
        level = int(takecommand())
        set_brightness(level)
        speak(f"Brightness set to {level}%.")
    except ValueError:
        speak("Invalid brightness level.")

def timer():
    speak("For how many seconds should I set the timer?")
    try:
        seconds = int(takecommand())
        speak(f"Setting a timer for {seconds} seconds.")
        time.sleep(seconds)
        speak("Time's up!")
    except ValueError:
        speak("Invalid time input.")

def quick_notes():
    speak("What should I note down?")
    note = takecommand()
    with open("quick_notes.txt", "a") as f:
        f.write(note + "\n")
    speak("Your note has been saved.")

def guess_the_number_game():
    speak("Let's play a game! I am thinking of a number between 1 and 100. Try to guess it!")
    
    number_to_guess = random.randint(1, 100)  # Random number between 1 and 100
    attempts = 0

    while True:
        speak("What's your guess?")
        guess = takecommand().lower()

        if guess is None:
            speak("Sorry, I couldn't understand your guess. Please try again.")
            continue

        # Check if the guess is a number
        try:
            guess = int(guess)
        except ValueError:
            speak("Please say a valid number.")
            continue

        attempts += 1
        
        if guess < number_to_guess:
            speak("Higher! Try again.")
        elif guess > number_to_guess:
            speak("Lower! Try again.")
        else:
            speak(f"Congratulations! You guessed the number {number_to_guess} in {attempts} attempts.")
            break

#def start_new_document():
    file_name = f"document_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    print(f"Creating new document: {file_name}")
    speak(f"Creating a new document named {file_name}")
    return open(file_name, "w")

def add_text_to_document(file, text):
    file.write(text + "\n")
    print(f"Added text: {text}")
    speak(f"Added text: {text}")


def save_and_close_document(file):
    file.close()
    print("Document saved and closed.")
    speak("Document saved and closed.")

def start_new_document():
    # Ask the user for the file name
    speak("What would you like to name the document?")
    file_name = takecommand().lower()  # Get the user input for the file name

    # If the user doesn't provide a name, set a default one with timestamp
    if not file_name:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"document_{timestamp}.txt"

    # Add ".txt" extension if the user didn't specify it
    if not file_name.endswith('.txt'):
        file_name += '.txt'

    print(f"Creating new document: {file_name}")

    # Open the file in write mode and ensure it's writable
    try:
        with open(file_name, 'w') as file:
            file.write("This is a new document.")
            print(f"Document {file_name} created successfully!")
    except IOError as e:
        print(f"Error creating document: {e}")

    return file_name  # Return the file name for further use

def file_composer():
    speak("Would you like to start a new document or edit an existing one?")
    while True:
        command = takecommand().lower()
        
        if command:
            if "start new document" in command:
                document, file_name = start_new_document()
                speak("What would you like to write in the document?")
                while True:
                    text_command = takecommand().lower()
                    if text_command:
                        if "save document" in text_command:
                            save_and_close_document(document, file_name)
                            speak("Document saved and closed.")
                            break
                        elif "stop writing" in text_command:
                            speak("Stopped writing.")
                            break
                        else:
                            add_text_to_document(document, text_command)
            elif "open document" in command:
                speak("Please tell me the document name or path.")
                document_path = takecommand().lower()
                if document_path:
                    try:
                        document = Document(document_path)
                        speak(f"Editing the document at {document_path}")
                        while True:
                            text_command = takecommand().lower()
                            if text_command:
                                if "save document" in text_command:
                                    save_and_close_document(document, document_path)
                                    speak("Document saved and closed.")
                                    break
                                elif "stop writing" in text_command:
                                    speak("Stopped writing.")
                                    break
                                else:
                                    add_text_to_document(document, text_command)
                    except FileNotFoundError:
                        speak("Sorry, I couldn't find that document.")
            elif "exit" in command:
                speak("Exiting file management.")
                break
            else:
                speak("Sorry, I didn't understand that command.")

def search_wikihow(query="creative", max_results=10, lang="en"):
    return list(WikiHow.search(query, max_results=max_results, lang=lang))

def start():
 global is_speaking
 global current_language
 wish()
 creative_mode = False
 while True:
     query = takecommand().lower()

     intent = recognize_intent(query)

     if intent == "greeting":
        speak(f"{wish()}")


     elif intent == "sleep_mode":
        speak("okay sir i am going to sleep. you can call me anytime")
        break

     elif intent == "file management":
        file_management()
     elif intent == "file_composer":
        file_composer()
     elif intent == "clipboard":
        clipboard_manager()
    
     elif intent == "system monitor":
        system_monitoring()
     elif intent == "game":
        guess_the_number_game()

     elif intent == "brightness control":
        adjust_brightness()

     elif intent ==  "timer":
        timer()

     elif intent == "note":
        quick_notes()

     elif intent == "creative mode":
      if not creative_mode:
        speak("Creative mode is active. Tell me, how can I help you?")
        creative_mode = True
      else:
        speak("You are already in creative mode.")

     elif "exit creative" in query and creative_mode:
       speak("Exiting creative mode.")
       creative_mode = False  
       return  
  
  
     if creative_mode:
       while True:
        how = takecommand().lower()
        if not how: 
         print("Listening... Say something or say 'exit creative' to leave.") # No speech detected
         continue
       # Handle empty or meaningless input
        if not how.strip() or how.strip() in ["nothing", "no", "never mind"]:
         speak("I'm here to help. Please ask me how to do something.")
        else:
          try:
            max_results = 1  
            how_to = search_wikihow(how, max_results)

            if how_to:
                speak(how_to[0].summary)
                break
            else:
                speak("Sorry, I couldn't find any how-to guides for that.")
          except Exception as e:
            speak(f"An error occurred: {str(e)}")


     elif intent == "weather":
        process_weather_query(query)
     
     elif intent == "internet_speed":
        check_internet_speed()
        
     elif "open notepad" in query:
        __npath__ = r"C:\Windows\System32\notepad.exe"
        try:
            os.startfile(__npath__)
            speak("Opening Notepad")
        except Exception as e:
            speak(f"Error opening Notepad: {e}")

     elif "close notepad" in query:
         speak("okay sir closing notepad")
         os.system("taskkill /f /im notepad.exe")


     elif "open paint" in query:
        
        try:
            os.system("start mspaint")
            speak("Opening Paint")
        except Exception as e:
            speak(f"Error opening Paint: {e}")
    

     elif "close paint" in query:
         speak("okay sir closing paint")
         os.system("taskkill /f /im mspaint.exe")
     

     elif "open command" in query:
        try:
            os.system("start cmd")
            speak("Opening Command Prompt")
        except Exception as e:
            speak(f"Error opening Command Prompt: {e}")
     

     elif "close command" in query:
         speak("okay sir closing command prompt")
         os.system("taskkill /f /im wt.exe")


     elif intent == "music":
      music_dir = "F:\IWANT\sidhumosewala"
      songs = os.listdir(music_dir)
      rd = random.choice(songs)
      os.startfile(os.path.join(music_dir,rd))
     
    
         
     elif intent == "stop music":
         speak("okay sir closing music")
         os.system("taskkill /f /im wmplayer.exe")

    
     elif intent == "joke":
        speak("Here's a joke for you.")
        tell_joke()


     elif intent ==  "alarm":
      handle_alarm_intent()

     elif intent == "time":
        current_time = datetime.now().strftime("%H:%M")
        speak(f"the current time is {current_time}")
    
     elif intent == "date":
       current_date = datetime.now().strftime("%A, %B %d, %Y")  
       speak(f"The current date is {current_date}")

     elif intent == "intro":
        speak("I am i want an AI assistant here to help you with tasks, provide information, and answer your questions.")
        speak("I can help you with a variety of tasks such as answering questions, providing information, making calculations, telling the time or date, and assisting with various programming or tech-related tasks. Just ask and I will do my best to help!")

     elif intent == "owner":
        speak("Mujeeb is a university student studying computer science. He is passionate about video editing, graphic designing, and filmmaking. He also has an agency named Meems Production.")
        

     elif intent == "screenshot":
        speak("sir please tell me the name of this screenshot file?")
        Name = takecommand().lower()
        speak("sir please hold the screen for couple of seconds, i am taking screenshot")
        time.sleep(2)
        img = pyautogui.screenshot()
        img.save(f"{Name}.png")
        speak("screenshot is saved in our main folder")

     elif intent == "pdf":
        pdf_reader()

     elif intent == "shutdown":
      speak("Are you sure you want to shut down your computer?")
      confirmation = takecommand().lower()
      if "yes" in confirmation or "sure" in confirmation:
        speak("Shutting down the computer. Goodbye, sir!")
        os.system("shutdown /s /t 5")  
      else:
        speak("Shutdown canceled.")

     elif intent == "restart":
      speak("Are you sure you want to restart your computer?")
      confirmation = takecommand().lower()
      if "yes" in confirmation or "sure" in confirmation:
        speak("Restarting the computer. Please wait!")
        os.system("shutdown /r /t 5")  
      else:
        speak("Restart canceled.")

     elif intent == "sleep":
      speak("Putting the computer to sleep mode. Good night, sir!")
      os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")  


     elif intent == "lock_screen":
      speak("Locking the computer. See you soon!")
      os.system("rundll32.exe user32.dll,LockWorkStation")

     elif intent == "ip_address":
         ip = get("https://api.ipify.org").text
         speak(f"your ip address is {ip}")


     elif intent == "wikipedia":
         speak("searching wikipedia......")
         query = query.replace("wikipedia","")
         result = wikipedia.summary(query, sentences=2)
         speak("according to wikipedia")
         speak(result)


     elif "open youtube" in query:
         speak("opening youtube")
         webbrowser.open("https://www.youtube.com/")
         
         
     elif "open instagram" in query:
         speak("opening instagram")
         webbrowser.open("https://www.instagram.com/?utm_source=pwa_homescreen&__pwa=1")
     
     elif intent == "switch_window":
       print("Recognized command: Switch window")  
       speak("Switching the window now.")
       pyautogui.hotkey('alt', 'tab')
       time.sleep(1)
       print("Window switch attempted.")  
       speak("Window switched.")

     elif intent == "news":
         speak("please wiat sir, fetching the latest news")
         news()   

     elif "open freelance" in query:
         speak("opening fiverr")
         webbrowser.open("https://www.fiverr.com/users/mujeeburrehm712/seller_dashboard")
    
     elif intent == "search":
      speak("Sir, what should I search on Edge?")
      cm = takecommand().lower()
    
    
      search_url = f"https://www.bing.com/search?q={cm}"
    

      edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
      webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
      webbrowser.get('edge').open(search_url)

     elif intent == "whatsapp":
         send_message()
     
     
     
     elif intent == "location":
         speak("wait sir,let me check")
         try:
             ipADD = requests.get("https://api.ipify.org").text
             print(ipADD)
             url = f"https://get.geojs.io/v1/ip/geo/{ipADD}.json"
             geo_requests = requests.get(url)
             geo_data = geo_requests.json()
             city = geo_data['city']
             country = geo_data['country']
             speak(f"sir i am not sure but i think we are in {city} city of {country}  ")
         except Exception as e:
             speak("sorry sir due to network issue i am not able to find where we are.")
             pass    
  


     elif "play songs on youtube" in query:
        speak("playing your Favourite song playlist on youtube")
        webbrowser.open("https://www.youtube.com/watch?v=XTp5jaRU3Ws&list=RDXTp5jaRU3Ws&start_radio=1")


     if intent == "email":
      try:
        speak("To whom, sir?")
        rec = takecommand().lower()

        if rec in email_directory:
            to = email_directory[rec]
        else:
            speak("I couldn't find the recipient. Please say the full email address.")
            to = takecommand().lower()

             

        speak("What should I say, sir?")
        content = takecommand().lower()

        speak("Do you want to attach a file? Please say yes or no.")
        attach_file = takecommand().lower()

        file_path = None
        if attach_file in ["yes", "yeah", "yup"]:
            speak("Please provide the full path of the file.")
            file_path = input("Enter file path: ")  

        speak(f"Sending email to {to}, saying: {content}")
        if file_path:
            speak(f"Attaching the file located at {file_path}")

        speak("Are you sure you want to send this email? Please say yes or no.")
        while True:
            confirmation = takecommand().lower()
            if confirmation in ["absolute", "yes", "done"]:
                send_email(to, content, file_path)
                break
            elif confirmation in ["no", "cancel"]:
                speak("Email sending canceled.")
                print("Email sending canceled.")
                break
            else:
                speak("I didn't quite catch that. Please say yes or no.")

      except Exception as e:
        speak("An error occurred while processing the request.")
        print(f"Error: {e}")

     elif intent == "farewell": 
         speak("thanks for using me sir")
         sys.exit()
     #speak("do you have any other work?")

if __name__ == "__main__":
   while True:
    permission = takecommand()
    if "wake up" in permission:
        engine = initialize_tts_engine()
        start()
    
    elif "goodbye" in permission:
        speak("thanks for using me sir, have a good day")
        get_all_queries()
        sys.exit()
        

