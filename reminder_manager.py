import datetime
import time
import threading
from plyer import notification
import schedule
from email_manager import send_email

class ReminderManager:
    def __init__(self):
        self.reminders = []
        self.scheduler_thread = None
        self._running = False

    def start_scheduler(self):
        """Start the scheduler thread"""
        self._running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def add_reminder(self, hour, minute, message, notify=True, speak_callback=None, email=None):
        """Add a new reminder for a specific time"""
        # Calculate target time for today
        now = datetime.datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If the time has already passed today, schedule for tomorrow
        if target_time <= now:
            target_time += datetime.timedelta(days=1)
        
        def reminder_action():
            try:
                # Show notification with longer timeout (30 seconds instead of 10)
                if notify:
                    notification.notify(
                        title="Nova Assistant Reminder",  # Added assistant name to title
                        message=message,
                        timeout=30,  # Increased timeout to 30 seconds
                        app_icon=None,  # You can add an icon path here if you want
                        app_name="Nova Assistant"
                    )
                
                # Speak the reminder if callback provided
                if speak_callback:
                    speak_callback(f"Reminder: {message}")
                
                # Send email if provided
                if email:
                    try:
                        if speak_callback:
                            speak_callback(f"Attempting to send email reminder to {email}")
                        
                        sender_email = "rajesh2803p@gmail.com"
                        sender_password = "kqlphsddvxeqltdl"
                        subject = "Nova Assistant Reminder"
                        
                        success, result = send_email(sender_email, sender_password, email, subject, message)
                        
                        if success:
                            if speak_callback:
                                speak_callback("Email reminder sent successfully")
                        else:
                            if speak_callback:
                                speak_callback(f"Failed to send reminder email: {result}")
                
                    except Exception as e:
                        if speak_callback:
                            speak_callback(f"Error sending reminder email: {str(e)}")
                
                # Remove the job after it's done
                return schedule.CancelJob
            
            except Exception as e:
                if speak_callback:
                    speak_callback(f"Error in reminder action: {str(e)}")
                return schedule.CancelJob

        # Schedule the reminder
        schedule.every().day.at(target_time.strftime("%H:%M")).do(reminder_action)
        
        self.reminders.append({
            'time': target_time,
            'message': message,
            'email': email
        })
        
        return target_time

    def stop_scheduler(self):
        """Stop the scheduler thread"""
        self._running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        schedule.clear()
        self.reminders = []

    def get_active_reminders(self):
        """Get list of active reminders"""
        current_time = datetime.datetime.now()
        active_reminders = [r for r in self.reminders if r['time'] > current_time]
        return active_reminders 