import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import threading
import customtkinter as ctk
import tkinter as tk  # Import tkinter for standard GUI components
from calculation import extract_calculation, calculate  # Importing from the new calculation module
from browser_manager import close_browser, close_current_tab, minimize_window  # Importing the close_browser function and close_current_tab function
from assistant_logic import speak, takeCommand  # Importing assistant logic functions
from weather_manager import get_weather  # Importing the weather manager
import pyjokes  # Importing the pyjokes module for jokes
from news_manager import get_news, country_code_mapping  # Importing the news manager and country code mapping
from PIL import ImageGrab  # Importing ImageGrab for taking screenshots
import time  # Importing time to generate unique filenames
import os  # Import os to use for opening the calculator
import socket  # Import socket to get the IP address
from email_manager import send_email
import requests
from urllib.parse import quote
import re
from reminder_manager import ReminderManager
from music_manager import MusicManager
import PyPDF2
from PyPDF2 import PdfReader
from pdf_manager import PDFManager
from tkinter import filedialog
from notepad_manager import NotepadManager
from gemini_api import query_gemini_api
from tkinter import simpledialog  # <-- for pop‑up input dialogs

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def read_pdf(file_path, page_number=None):
    """
    Read a PDF file and return its content.
    If page_number is specified, read only that page.
    """
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        
        if page_number is not None:
            # Adjust page number to 0-based index
            page_idx = page_number - 1
            if page_idx < 0 or page_idx >= total_pages:
                return f"Error: Page {page_number} does not exist. PDF has {total_pages} pages."
            return reader.pages[page_idx].extract_text()
        else:
            # Read all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

class AssistantWindow:
    def __init__(self):
        self.window = None
        self.loading_label = None  # Initialize loading_label
        self.reminder_manager = ReminderManager()  # Initialize reminder manager
        self.reminder_manager.start_scheduler()    # Start the scheduler
        self.music_manager = MusicManager()
        self.pdf_manager = PDFManager()  # Add this line
        self.notepad_manager = NotepadManager()  # Add this line
        self.setup_window()

    def setup_window(self):
        self.window = ctk.CTk()
        self.window.title("Nova AI Assistant")
        self.window.geometry("600x700")
        self.window.resizable(True, True)  # Allow resizing
        self.window.minsize(400, 500)  # Set minimum size
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main frame with a soothing background color
        self.main_frame = ctk.CTkFrame(self.window, fg_color="#1E1E1E")  # Darker background for better eye comfort
        self.main_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Create title label with a new font and color
        self.title_label = ctk.CTkLabel(self.main_frame, text="Nova AI Assistant", font=("Helvetica", 24, "bold"), text_color="#00BFFF")  # Softer blue color
        self.title_label.pack(pady=10)

        # Create loading label
        self.loading_label = ctk.CTkLabel(self.main_frame, text="", font=("Helvetica", 12), text_color="#FFFFFF")
        self.loading_label.pack(pady=10)

        # Create chat display area with custom styling
        self.text_area = ctk.CTkTextbox(self.main_frame, 
                                          width=600, 
                                          height=400,
                                          font=("Arial", 12),
                                          corner_radius=10,
                                          fg_color="#F0F0F0",  # Light gray background for text area
                                          text_color="#000000")  # Black text for contrast
        self.text_area.pack(padx=10, pady=10, fill='both', expand=True)

                # Create input box for manual input
        self.input_var = tk.StringVar()
        self.input_entry = ctk.CTkEntry(self.main_frame, textvariable=self.input_var, width=400, corner_radius=10, fg_color="#FFFFFF", text_color="#000000")  # White background for input
        self.input_entry.pack(pady=10)

        # Create button to submit manual input
        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.submit_input, corner_radius=10, fg_color="#4CAF50", text_color="#FFFFFF")  # Green button
        self.submit_button.pack(pady=10)

        # Create button to trigger voice input
        self.voice_button = ctk.CTkButton(self.main_frame, text="Speak", command=self.start_voice_input, corner_radius=10, fg_color="#2196F3", text_color="#FFFFFF")  # Blue button
        self.voice_button.pack(pady=10)
        # Create Music Control Frame
        self.music_frame = ctk.CTkFrame(self.main_frame, fg_color="#2E2E2E")
        self.music_frame.pack(padx=10, pady=5, fill='x')

        # Music Control Label
        self.music_label = ctk.CTkLabel(self.music_frame, 
                                       text="Music Controls", 
                                       font=("Helvetica", 14, "bold"),
                                       text_color="#00BFFF")
        self.music_label.pack(pady=5)

        # Music Buttons Frame
        self.music_buttons_frame = ctk.CTkFrame(self.music_frame, fg_color="#2E2E2E")
        self.music_buttons_frame.pack(pady=5)

        # Music Control Buttons
        self.play_button = ctk.CTkButton(self.music_buttons_frame, 
                                        text="Play", 
                                        command=lambda: self.process_music_command("play music"),
                                        width=80,
                                        fg_color="#4CAF50")
        self.play_button.pack(side='left', padx=5)

        self.pause_button = ctk.CTkButton(self.music_buttons_frame, 
                                         text="Pause", 
                                         command=lambda: self.process_music_command("pause music"),
                                         width=80,
                                         fg_color="#FFA500")
        self.pause_button.pack(side='left', padx=5)

        self.resume_button = ctk.CTkButton(self.music_buttons_frame, 
                                          text="Resume", 
                                          command=lambda: self.process_music_command("resume music"),
                                          width=80,
                                          fg_color="#2196F3")
        self.resume_button.pack(side='left', padx=5)

        self.stop_button = ctk.CTkButton(self.music_buttons_frame, 
                                        text="Stop", 
                                        command=lambda: self.process_music_command("stop music"),
                                        width=80,
                                        fg_color="#FF0000")
        self.stop_button.pack(side='left', padx=5)

        self.list_songs_button = ctk.CTkButton(self.music_buttons_frame, 
                                              text="List Songs", 
                                              command=lambda: self.process_music_command("list songs"),
                                              width=80,
                                              fg_color="#9C27B0")
        self.list_songs_button.pack(side='left', padx=5)

        # Now Playing Label
        self.now_playing_label = ctk.CTkLabel(self.music_frame, 
                                             text="Now Playing: None", 
                                             font=("Helvetica", 12),
                                             text_color="#FFFFFF")
        self.now_playing_label.pack(pady=5)



        # Create status label with a different color
        self.status_label = ctk.CTkLabel(self.main_frame, 
                                           text="Nova is ready...",
                                           font=("Helvetica", 14),
                                           text_color="#4CAF50")
        self.status_label.pack(pady=10)

    def submit_input(self):
        """Process the input from the entry box."""
        query = self.input_var.get()
        self.input_var.set("")  # Clear the input box
        process_query(query)  # Process the query

    def start_voice_input(self):
        """Start listening for voice input."""
        query = takeCommand()  # Get input from the microphone
        process_query(query)  # Process the query

    def show(self):
        """Show the assistant window"""
        if not self.window:
            self.setup_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def hide(self):
        """Hide the assistant window"""
        if self.window:
            self.window.withdraw()

    def update_text(self, message, sender="Nova"):
        if not self.window:
            return
        tag = "assistant" if sender == "Nova" else "user"
        self.text_area.tag_config("assistant", foreground="#00BFFF")  # Softer blue for assistant
        self.text_area.tag_config("user", foreground="#4CAF50")  # Green for user
        
        self.text_area.insert("end", f"\n{sender}: ", tag)
        self.text_area.insert("end", f"{message}\n")
        self.text_area.see("end")
        
    def start(self):
        """Show the assistant window"""
        if self.window:
            self.window.mainloop()

    def show_functionalities(self):
        functionalities = (
            "Here are some things I can do for you:\n"
            "1. Search Wikipedia            21. Tell the current time\n"
            "2. Open YouTube                22. Take a screenshot\n"
            "3. Play a video on YouTube     23. Close YouTube\n"
            "4. Get the latest news         24. Close Google\n"
            "5. Provide weather information  25. Exit the assistant\n"
            "6. Tell a joke                 26. Sleep mode\n"
            "7. Perform calculations        27. Open Google Calculator\n"
            "8. Send email                  28. Get IP address\n"
            "9. Close current tab           29. Get current day\n"
            "10. Minimize (say down) window\n"
            "11. Set reminder (specify hour 0-23 and minute 0-59)\n"
            "12. Show reminders (view all active reminders)\n"
            "13. Play music (from your music directory)\n"
            "14. Stop music\n"
            "15. Pause music\n"
            "16. Resume music\n"
            "17. Create a note\n"
            "18. Read a note\n"
            "19. List notes\n"
            "20. Manage PDF files (read PDF)\n\n"
            "For reminders, just say 'set reminder' and I'll ask for:\n"
            "- Hour (in 24-hour format)\n"
            "- Minute\n"
            "- Reminder message\n"
            "The reminder will notify you with sound, popup, and email!"
        )
        self.update_text(functionalities)

    def process_music_command(self, command):
        """Process music control commands from GUI buttons"""
        if command == "play music":
            try:
                # Use raw string and forward slashes for path
                music_dir = r"D:/Users/Rajesh Prajapati/ff/my data/Music/ms"
                
                # Add input dialog for specific song
                speak("Would you like to play a specific song? Say yes or no")
                response = takeCommand().lower()
                
                specific_song = None
                if 'yes' in response:
                    speak("Which song would you like to play?")
                    song_name = takeCommand()
                    if song_name != "None":
                        specific_song = song_name
                
                success, message = self.music_manager.play_music(music_dir, specific_song)
                if success:
                    self.now_playing_label.configure(text=f"Now Playing: {message.replace('Playing: ', '')}")
                self.update_text(message)
            except Exception as e:
                self.update_text(f"Error playing music: {str(e)}")
        
        elif command == "pause music":
            success, message = self.music_manager.pause_music()
            if success:
                self.now_playing_label.configure(text="Now Playing: Paused")
            self.update_text(message)
        
        elif command == "resume music":
            success, message = self.music_manager.resume_music()
            if success and self.music_manager.current_track:
                self.now_playing_label.configure(text=f"Now Playing: {os.path.basename(self.music_manager.current_track)}")
            self.update_text(message)
        
        elif command == "stop music":
            success, message = self.music_manager.stop_music()
            if success:
                self.now_playing_label.configure(text="Now Playing: None")
            self.update_text(message)
        
        elif command == "list songs":
            songs = self.music_manager.list_songs()
            if songs:
                song_list = "Available songs:\n" + "\n".join(songs)
                self.update_text(song_list)
                speak("Here are the available songs")
            else:
                self.update_text("No songs available")
                speak("No songs found in the music directory")

# Create global instance
assistant_window = None

def process_query(query):
    """Process the query from either voice or keyboard input."""
    global gui_active
    if query == "None":
        return

    # Show loading indicator
    assistant_window.loading_label.configure(text="Processing...")
      # Start the loading spinner

    if not gui_active and ('start' in query or 'open' in query or 'wake up' in query or 'nova' in query):
        gui_active = True
        assistant_window.show()
        speak("Hello! I'm Nova, How can I help you?")
        assistant_window.show_functionalities()  # Show functionalities
        return

    if gui_active:
        # Check for Chat GPT command
        if 'chat gpt' in query.lower():
            # Extract the user query after "chat gpt"
            user_query = query.lower().replace("chat gpt", "").strip()
            if user_query:
                # Call the Gemini API
                response = query_gemini_api(user_query)
                if "error" not in response:
                    # Process and speak the response
                    answer = response.get("answer", "I couldn't find an answer.")
                    speak(answer)
                    assistant_window.update_text(f"Chat GPT: {answer}")
                else:
                    speak("Sorry, there was an error with the Gemini API.")
                    assistant_window.update_text("Error with Gemini API.")
            else:
                speak("Please provide a query after 'Chat GPT'.")
                assistant_window.update_text("No query provided after 'Chat GPT'.")

        # Check for news command
        if 'news' in query:
            speak("Which country do you want news from?")
            country_name = takeCommand()  # Get country name from user
            if country_name == "None":  # If voice input is not given, check for typed input
                country_name = query  # Use the typed input instead
            country_code = country_code_mapping.get(country_name.lower())  # Get country code from mapping
            if country_code:  # Ensure country code is found
                speak("Would you like news for a specific city or state? Please specify.")
                location_type = takeCommand().lower()  # Get city or state from user
                if 'city' in location_type:
                    speak("Please specify the city.")
                    city_name = takeCommand()  # Get city name from user
                    # Fetch news for the specified city
                    api_key = "pub_681657c9928c048f2caf5dab3590329efe16d"  # Your NewsData.io API key
                    news_articles = get_news(api_key, country_code, city=city_name)  # Fetch news by city
                elif 'state' in location_type:
                    speak("Please specify the state.")
                    state_name = takeCommand()  # Get state name from user
                    # Fetch news for the specified state
                    api_key = "pub_681657c9928c048f2caf5dab3590329efe16d"  # Your NewsData.io API key
                    news_articles = get_news(api_key, country_code, state=state_name)  # Fetch news by state
                else:
                    # If neither city nor state is specified, fetch general news for the country
                    api_key = "pub_681657c9928c048f2caf5dab3590329efe16d"  # Your NewsData.io API key
                    news_articles = get_news(api_key, country_code)  # Fetch news by country
                
                if news_articles:
                    news_summary = "\n".join(news_articles)
                    speak(f"Here are the latest news headlines from {country_name}:")
                    assistant_window.update_text(f"Latest News from {country_name}:\n{news_summary}")
                else:
                    speak("Sorry, I couldn't fetch the news at the moment. Please try again later.")
            else:
                speak("I didn't recognize that country name. Please try again.")
        
        # Check for related news command
        elif 'related  about' in query:
            topic = query.replace("related news about", "").strip()  # Extract the topic from the query
            api_key = "pub_681657c9928c048f2caf5dab3590329efe16d"  # Your NewsData.io API key
            news_articles = get_news(api_key, None, topic)  # Fetch related news
            if news_articles:
                news_summary = "\n".join(news_articles)
                speak(f"Here are the latest news headlines related to {topic}:")
                assistant_window.update_text(f"Latest News about {topic}:\n{news_summary}")
            else:
                speak("Sorry, I couldn't fetch the related news at the moment. Please try again later.")
        
        # Check for Google search command
        elif 'search about' in query or 'on google' in query:
            search_query = query.replace("search for", "").replace("on google", "").strip()  # Extract the search term
            if search_query:
                search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"  # Construct the search URL
                webbrowser.open(search_url)  # Open the search URL in the default web browser
                speak(f"Opening Google for {search_query}.")
                assistant_window.update_text(f"Opening Google for {search_query}.")
            else:
                speak("Please specify what you want to search for on Google.")

                
        # Check if the query contains the word 'wikipedia'
        if 'wikipedia' in query or 'detail about' in query:
            # Inform the user that a Wikipedia search is starting
            speak('Searching Wikipedia...')
            # Remove the word 'wikipedia' from the query to get the actual search term
            query = query.replace("wikipedia", "")
            # Fetch a summary from Wikipedia based on the modified query
            results = wikipedia.summary(query, sentences=2)
            # Inform the user that the results are coming from Wikipedia
            speak("According to Wikipedia")
            # Update the assistant window with the fetched results
            assistant_window.update_text(f"Result: {results}")
            # Speak out the results to the user
            speak(results)        
        
        # Check for calculator command
        elif 'calculator' in query or 'open calculator' in query:
            if os.name == 'nt':  # For Windows
                os.system('calc')  # Open Windows Calculator
            elif os.name == 'posix':  # For macOS
                os.system('open -a Calculator')  # Open macOS Calculator
            else:
                speak("Sorry, I cannot open the calculator on this operating system.")
            speak("Opening calculator.")
            assistant_window.update_text("Opening calculator.")
        
        # Check for YouTube play command
        if 'play' in query and 'youtube' in query:
            # Extract the video title from the query
            video_title = query.replace("play", "").replace("youtube", "").strip()
            if video_title:
                try:
                    # Search for the video
                    search_query = quote(video_title) 
                    html = requests.get(f"https://www.youtube.com/results?search_query={search_query}").text
                    
                    # Find video ID of the first result
                    video_ids = re.findall(r"watch\?v=(\S{11})", html)
                    if video_ids:
                        # Get first video ID and create direct play URL
                        first_video = f"https://www.youtube.com/watch?v={video_ids[0]}"
                        webbrowser.open(first_video)
                        speak(f"Playing {video_title} on YouTube")
                        assistant_window.update_text(f"Playing video: {video_title}")
                    else:
                        speak("No videos found for your search")
                        assistant_window.update_text("No videos found")
                except Exception as e:
                    speak("Sorry, there was an error playing the video")
                    assistant_window.update_text(f"Error playing video: {str(e)}")
            else:
                speak("Please specify what you want to play on YouTube")
                assistant_window.update_text("Please specify what to play")
          
        # Weather functionality
        elif 'weather' in query:
            speak("Which city?")
            city = takeCommand()  # Get city name from user
            if city != "None":
                api_key = "29671cdf7262218be46f54a04aea3b20"  # Replace with your OpenWeatherMap API key
                weather_info = get_weather(city, api_key)
                if weather_info:
                    temp, humidity, description = weather_info
                    temp = f"{temp:.2f}"  # Format temperature to show 2 decimal places
                    speak(f"The temperature is {temp} degrees Celsius, humidity is {humidity} percent, and the weather is {description}.")
                    assistant_window.update_text(f"Weather in {city}: {temp}°C, {humidity}%, {description}")
                else:
                    speak("Sorry, I couldn't find the weather for that city.")
        if 'open youtube' in query:
            webbrowser.open("youtube.com")
        elif 'open google' in query:
            webbrowser.open("google.com")
        elif 'close youtube' in query:
            if close_browser('youtube'):
                speak("Closed YouTube")
            else:
                speak("YouTube is not open or I couldn't close it")
        elif 'close google' in query:
            if close_browser('google'):
                speak("Closed Google")
            else:
                speak("Google is not open or I couldn't close it")
        elif any(word in query for word in ['calculate', 'compute', 'what is']):
            calc_text = extract_calculation(query)
            result = calculate(calc_text)
            speak(result)
            assistant_window.update_text(f"Calculation: {calc_text}\n{result}")
        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {strTime}")
            assistant_window.update_text(f"Time is : {strTime}\n")
        elif 'joke' in query:
            speak(pyjokes.get_joke())
            assistant_window.update_text(pyjokes.get_joke())
        elif 'exit' in query:
            speak("Thanks for using me. Have a good day!")
            assistant_window.window.quit()
            return
        elif 'sleep' in query or 'goodbye' in query:
            speak("Going to sleep mode. Say 'start' when you need me!")
            assistant_window.hide()
            gui_active = False
            return
        # Check for screenshot command
        if 'screenshot' in query:
            timestamp = time.strftime("%Y%m%d_%H%M%S")  # Create a timestamp
            filename = f"screenshot_{timestamp}.png"  # Generate a unique filename
            screenshot = ImageGrab.grab()  # Capture the current screen
            screenshot.save(filename)  # Save the screenshot with the unique filename
            speak(f"Screenshot taken Successfully")
            assistant_window.update_text(f"Screenshot taken and saved as {filename}.")

        # Check for IP address command
        elif 'ip address' in query or 'my ip' in query:
            ip_address = socket.gethostbyname(socket.gethostname())  # Get the IP address
            speak(f"Your IP address is {ip_address}.")
            assistant_window.update_text(f"Your IP address is: {ip_address}")

        # Check for day command
        elif 'day' in query or 'what day is it' in query:
            today = datetime.datetime.now().strftime("%A")  # Get the current day
            speak(f"Today is {today}.")
            assistant_window.update_text(f"Today is: {today}")

        # Check for email command
        elif 'send email' in query or 'send mail' in query:
            try:
                speak("Please type the recipient's email address in the text bar and press Submit")
                assistant_window.status_label.configure(text="Waiting for email address...")
                
                # Create a new StringVar for email input
                email_var = tk.StringVar()
                
                def on_submit(event=None):
                    email = assistant_window.input_entry.get()
                    email_var.set(email)
                    assistant_window.input_entry.delete(0, 'end')  # Clear the input
                
                # Bind the submit button and Enter key to the on_submit function
                old_command = assistant_window.submit_button.cget('command')
                assistant_window.submit_button.configure(command=on_submit)
                assistant_window.input_entry.bind('<Return>', on_submit)
                
                # Wait for the email input
                assistant_window.window.wait_variable(email_var)
                recipient_email = email_var.get()
                
                # Restore original command
                assistant_window.submit_button.configure(command=old_command)
                assistant_window.input_entry.unbind('<Return>')
                
                if '@' not in recipient_email or '.' not in recipient_email:
                    speak("Invalid email address. Please try again.")
                    assistant_window.status_label.configure(text="Nova is ready...")
                    return
                
                speak("What's the subject of the email?")
                subject = takeCommand()
                
                speak("What message would you like to send?")
                message = takeCommand()
                
                # Your email credentials
                sender_email = "rajesh2803p@gmail.com"
                sender_password = "islunadrxmfwxpkq"
                
                success, result = send_email(sender_email, sender_password, recipient_email, subject, message)
                
                if success:
                    speak("Email has been sent successfully!")
                    assistant_window.update_text("Email sent successfully!")
                else:
                    speak("Sorry, I couldn't send the email.")
                    assistant_window.update_text(f"Failed to send email: {result}")
                
                assistant_window.status_label.configure(text="Nova is ready...")
            except Exception as e:
                speak("Sorry, there was an error sending the email.")
                assistant_window.update_text(f"Error sending email: {str(e)}")
                assistant_window.status_label.configure(text="Nova is ready...")

        # Check for close tab command
        elif 'close tab' in query:
            if close_current_tab():
                speak("Closed the current tab")
                assistant_window.update_text("Closed the current tab")
            else:
                speak("Sorry, I couldn't close the tab")
                assistant_window.update_text("Failed to close tab")

        # Check for minimize window command
        elif 'down window' in query or 'minimize current window' in query:
            if minimize_window():
                speak("Minimized the current window")
                assistant_window.update_text("Minimized the current window")
            else:
                speak("Sorry, I couldn't minimize the window")
                assistant_window.update_text("Failed to minimize window")

        # Check for reminder command
        elif 'set reminder' in query or 'remind me' in query:
            try:
                speak("What hour would you like to set the reminder for? (0-23)")
                hour_str = takeCommand()
                try:
                    hour = int(hour_str)
                    if hour < 0 or hour > 23:
                        speak("Please specify a valid hour between 0 and 23")
                        return
                except ValueError:
                    speak("Please specify a valid hour")
                    return

                speak("What minute? (0-59)")
                minute_str = takeCommand()
                try:
                    minute = int(minute_str)
                    if minute < 0 or minute > 59:
                        speak("Please specify a valid minute between 0 and 59")
                        return
                except ValueError:
                    speak("Please specify a valid minute")
                    return

                speak("What should I remind you about?")
                reminder_message = takeCommand()
                
                # Set default email without asking
                reminder_email = "rajesh2803p@gmail.com"  # Your default email address

                # Set the reminder
                reminder_time = assistant_window.reminder_manager.add_reminder(
                    hour=hour,
                    minute=minute,
                    message=reminder_message,
                    notify=True,
                    speak_callback=speak,
                    email=reminder_email
                )

                # Format time in 12-hour format
                time_str = reminder_time.strftime("%I:%M %p")
                confirmation = f"Reminder set for {time_str}: {reminder_message}"
                speak(confirmation)
                assistant_window.update_text(confirmation)

            except Exception as e:
                speak("Sorry, I couldn't set the reminder. Please try again.")
                assistant_window.update_text(f"Error setting reminder: {str(e)}")

        elif 'show reminders' in query:
            active_reminders = assistant_window.reminder_manager.get_active_reminders()
            if active_reminders:
                reminder_text = "Active reminders:\n"
                for reminder in active_reminders:
                    reminder_text += f"- {reminder['time'].strftime('%I:%M %p')}: {reminder['message']}\n"
                speak("Here are your active reminders")
                assistant_window.update_text(reminder_text)
            else:
                speak("You have no active reminders")
                assistant_window.update_text("No active reminders")

        # Check for play music command
        elif 'play music' in query or 'play song' in query:
            try:
                # Use raw string and forward slashes for path
                music_dir = r"D:\python\Nova\Nova\myad"
                
                # Check if a specific song was requested
                specific_song = None
                if 'play song' in query:
                    # Extract song name after "play song"
                    song_part = query.split('play song')[-1].strip()
                    if song_part:
                        specific_song = song_part
                        speak(f"Looking for song: {specific_song}")
                
                success, message = assistant_window.music_manager.play_music(music_dir, specific_song)
                if success:
                    speak(f"Playing {message}")
                    assistant_window.now_playing_label.configure(text=f"Now Playing: {message.replace('Playing: ', '')}")
                else:
                    speak(message)
                assistant_window.update_text(message)
            except Exception as e:
                speak("Error playing music")
                assistant_window.update_text(f"Error: {str(e)}")

        elif 'list songs' in query or 'show songs' in query:
            songs = assistant_window.music_manager.list_songs()
            if songs:
                song_list = "Available songs:\n" + "\n".join(songs)
                assistant_window.update_text(song_list)
                speak("Here are the available songs")
            else:
                speak("No songs found in the music directory")
                assistant_window.update_text("No songs available")

        # Check for stop music command
        elif 'stop music' in query:
            success, message = assistant_window.music_manager.stop_music()
            speak(message)
            assistant_window.update_text(message)

        # Check for pause music command
        elif 'pause music' in query:
            success, message = assistant_window.music_manager.pause_music()
            speak(message)
            assistant_window.update_text(message)

        # Check for resume music command
        elif 'resume music' in query:
            success, message = assistant_window.music_manager.resume_music()
            speak(message)
            assistant_window.update_text(message)

        elif 'read pdf' in query:
            try:
                speak("Please select a PDF file")
                assistant_window.status_label.configure(text="Waiting for PDF selection...")
                
                # Open file dialog
                pdf_path = filedialog.askopenfilename(
                    title="Select PDF file",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
                )
                
                if not pdf_path:  # User cancelled selection
                    speak("PDF selection cancelled")
                    return
                
                # First try to read the PDF
                success, content = assistant_window.pdf_manager.read_pdf(pdf_path)
                if not success:
                    speak("Error opening PDF file")
                    assistant_window.update_text(f"Error: {content}")
                    return
                
                total_pages = assistant_window.pdf_manager.get_total_pages()
                if total_pages == 0:
                    speak("This PDF appears to be empty or corrupted")
                    return
                
                speak(f"PDF has {total_pages} pages. Starting to read. Say stop anytime to stop reading.")
                assistant_window.update_text(f"PDF has {total_pages} pages\n")
                
                # Create a flag for stopping
                should_stop = False
                
                def check_stop_command():
                    nonlocal should_stop
                    while True:
                        command = takeCommand().lower().strip()
                        if command and 'stop' in command:
                            should_stop = True
                            break
                
                # Start the stop command listener in a separate thread
                stop_listener = threading.Thread(target=check_stop_command, daemon=True)
                stop_listener.start()
                
                # Read page by page
                for page_num in range(1, total_pages + 1):
                    if should_stop:
                        speak("Stopping PDF reading")
                        break
                        
                    success, content = assistant_window.pdf_manager.read_pdf(pdf_path, page_num)
                    
                    if success and content.strip():
                        # Update the text area
                        page_header = f"\n--- Page {page_num} of {total_pages} ---\n"
                        assistant_window.update_text(page_header + content)
                        
                        # Announce page number
                        speak(f"Reading page {page_num}")
                        
                        # Break content into smaller chunks for speaking
                        words = content.split()
                        chunk_size = 20  # Number of words per chunk
                        chunks = [' '.join(words[i:i+chunk_size]) 
                                for i in range(0, len(words), chunk_size)]
                        
                        for chunk in chunks:
                            if should_stop:
                                break
                            if chunk.strip():
                                speak(chunk)
                    else:
                        if should_stop:
                            break
                        error_message = f"\n--- Page {page_num} of {total_pages} ---\nError: {content}"
                        assistant_window.update_text(error_message)
                        speak(f"Error reading page {page_num}")
                
                if not should_stop:
                    speak("Finished reading the PDF")
                
            except Exception as e:
                speak("Sorry, there was an error reading the PDF")
                assistant_window.update_text(f"Error reading PDF: {str(e)}")
            finally:
                assistant_window.status_label.configure(text="Nova is ready...")
                assistant_window.pdf_manager.close_pdf()

        elif 'write note' in query or 'create note' in query:
            try:
                speak("What would you like me to write in the note?")
                content = takeCommand()
                
                if content.lower() in ['nothing', 'cancel']:
                    speak("Note taking cancelled")
                    return
                
                # Create and save note
                success, message = assistant_window.notepad_manager.create_note(content)
                if success:
                    speak("Note saved successfully")
                    assistant_window.update_text(f"Written and saved: {content}\n{message}")
                else:
                    speak(f"Error creating note: {message}")
                    
            except Exception as e:
                speak("Sorry, there was an error with the notepad")
                assistant_window.update_text(f"Error: {str(e)}")

        elif 'read note' in query:
            try:
                # List available notes
                notes = assistant_window.notepad_manager.list_notes()
                if not notes:
                    speak("No saved notes found")
                    return
                    
                speak("Here are your saved notes:")
                notes_list = "\n".join(notes)
                assistant_window.update_text(f"Available notes:\n{notes_list}")
                
                speak("Which note would you like me to read? Say the file name.")
                file_name = takeCommand()
                
                if file_name.lower() in ['cancel', 'nothing']:
                    speak("Cancelled reading note")
                    return
                
                # Try to find the closest matching filename
                matching_notes = [n for n in notes if file_name.lower() in n.lower()]
                if matching_notes:
                    file_name = matching_notes[0]  # Use the first match
                    success, content = assistant_window.notepad_manager.read_note(file_name)
                    if success:
                        speak(f"Reading note {file_name}")
                        assistant_window.update_text(f"Content of {file_name}:\n{content}")
                        speak(content)
                    else:
                        speak(f"Error reading note: {content}")
                else:
                    speak("Could not find a matching note")
                    
            except Exception as e:
                speak("Sorry, there was an error reading the note")
                assistant_window.update_text(f"Error: {str(e)}")

        elif 'list notes' in query:
            try:
                notes = assistant_window.notepad_manager.list_notes()
                if notes:
                    speak("Here are your saved notes:")
                    notes_list = "\n".join(notes)
                    assistant_window.update_text(f"Available notes:\n{notes_list}")
                else:
                    speak("No saved notes found")
                    
            except Exception as e:
                speak("Sorry, there was an error listing the notes")
                assistant_window.update_text(f"Error: {str(e)}")

    # After processing, hide the loading indicator
    assistant_window.loading_label.configure(text="") 

def assistant_loop():
    global gui_active
    gui_active = False
    while True:
        # Wait for the user to wake up the assistant
        query = takeCommand()  # Get input from the microphone
        process_query(query)  # Process the query

def main():
    global assistant_window
    assistant_window = AssistantWindow()
    assistant_window.hide()  # Hide window initially
    
    print("Say 'start' or 'open' to start the GUI assistant...")
    
    # Start the assistant logic in a separate thread
    threading.Thread(target=assistant_loop, daemon=True).start()
    
    # Run the GUI main loop in the main thread
    assistant_window.start()

if __name__ == "__main__":
    main() 