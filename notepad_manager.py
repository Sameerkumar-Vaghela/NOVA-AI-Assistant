import os
import datetime
import subprocess
import time
import psutil
import win32gui
import win32con

class NotepadManager:
    def __init__(self):
        self.current_file = None
        self.notepad_process = None
        # Set up notes directory in Documents
        self.notes_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Nova_Notes')
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)

    def create_note(self, content):
        """Create a new note with the given content and save automatically"""
        try:
            # Generate timestamp filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_file = f"note_{timestamp}.txt"
            file_path = os.path.join(self.notes_dir, self.current_file)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Open the file in Notepad to show the content
            self.notepad_process = subprocess.Popen(['notepad.exe', file_path])
            time.sleep(1)  # Wait for Notepad to open
            
            # Find and minimize Notepad window
            hwnd = win32gui.FindWindow("Notepad", None)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            
            return True, f"Note saved as: {self.current_file}"
            
        except Exception as e:
            return False, f"Error creating note: {str(e)}"

    def append_to_note(self, additional_content):
        """Append content to the current note"""
        try:
            if not self.current_file:
                return False, "No active note to append to"
                
            file_path = os.path.join(self.notes_dir, self.current_file)
            
            # Append the new content with a newline
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write('\n' + additional_content)
            
            # Close current Notepad and reopen
            if self.notepad_process:
                try:
                    self.notepad_process.terminate()
                except:
                    pass
                
            time.sleep(1)  # Wait for file to be saved
            
            # Open new instance of Notepad
            self.notepad_process = subprocess.Popen(['notepad.exe', file_path])
            time.sleep(0.5)  # Wait for Notepad to open
            
            return True, "Content added"
            
        except Exception as e:
            return False, str(e)

    def save_and_close(self):
        """Save and close the current note"""
        try:
            if self.notepad_process:
                # Get the process and all its children
                parent = psutil.Process(self.notepad_process.pid)
                children = parent.children(recursive=True)
                
                # Terminate children first
                for child in children:
                    child.terminate()
                
                # Terminate parent
                self.notepad_process.terminate()
                self.notepad_process = None
                
                time.sleep(0.5)  # Wait for process to close
            
            return True, f"Note saved as {self.current_file}"
            
        except Exception as e:
            return False, f"Error closing note: {str(e)}"

    def read_note(self, file_name):
        """Open an existing note in Notepad"""
        try:
            file_path = os.path.join(self.notes_dir, file_name)
            if not os.path.exists(file_path):
                return False, "File not found"
            
            subprocess.Popen(['notepad.exe', file_path])
            return True, f"Opening note: {file_name}"
            
        except Exception as e:
            return False, f"Error opening note: {str(e)}"

    def list_notes(self):
        """List all available notes"""
        try:
            if not os.path.exists(self.notes_dir):
                return []
            
            notes = [f for f in os.listdir(self.notes_dir) if f.endswith('.txt')]
            return sorted(notes, reverse=True)  # Most recent first
        except Exception:
            return [] 