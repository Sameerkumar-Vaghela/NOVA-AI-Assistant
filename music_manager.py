import pygame
import os
from pathlib import Path
import difflib  # For finding close matches of song names

class MusicManager:
    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        self.current_track = None
        self.music_files = []  # Store all found music files
        self.music_dir = None  # Store the music directory

    def scan_directory(self, music_dir):
        """Scan directory for music files"""
        self.music_dir = music_dir
        self.music_files = []
        supported_formats = ('.mp3', '.wav', '.ogg')
        
        # Search for music files in the directory
        for file in Path(music_dir).glob('**/*'):
            if file.suffix.lower() in supported_formats:
                self.music_files.append(str(file))
        
        return len(self.music_files) > 0

    def find_song(self, song_name):
        """Find a song by name, using fuzzy matching"""
        if not self.music_files:
            return None

        # Get all song names without path and extension
        song_names = [os.path.splitext(os.path.basename(f))[0].lower() for f in self.music_files]
        
        # Try to find the best match
        matches = difflib.get_close_matches(song_name.lower(), song_names, n=1, cutoff=0.6)
        
        if matches:
            # Find the corresponding full path
            index = song_names.index(matches[0])
            return self.music_files[index]
        
        return None

    def play_music(self, music_dir, specific_song=None):
        """Play music from the specified directory"""
        try:
            # Scan directory if it's new or different
            if self.music_dir != music_dir:
                if not self.scan_directory(music_dir):
                    return False, "No supported music files found in the directory"

            if specific_song:
                # Try to find and play the requested song
                song_path = self.find_song(specific_song)
                if not song_path:
                    return False, f"Could not find a song matching '{specific_song}'"
                
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.current_track = song_path
                return True, f"Playing: {os.path.basename(song_path)}"
            else:
                # Play the first available song if no specific song requested
                if self.music_files:
                    pygame.mixer.music.load(self.music_files[0])
                    pygame.mixer.music.play()
                    self.is_playing = True
                    self.current_track = self.music_files[0]
                    return True, f"Playing: {os.path.basename(self.music_files[0])}"
                return False, "No music files available"
            
        except Exception as e:
            return False, f"Error playing music: {str(e)}"

    def list_songs(self):
        """Return a list of available songs"""
        return [os.path.splitext(os.path.basename(f))[0] for f in self.music_files]

    def stop_music(self):
        """Stop the currently playing music"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            return True, "Music stopped"
        return False, "No music is playing"

    def pause_music(self):
        """Pause the currently playing music"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            return True, "Music paused"
        return False, "No music is playing"

    def resume_music(self):
        """Resume the paused music"""
        if not self.is_playing and self.current_track:
            pygame.mixer.music.unpause()
            self.is_playing = True
            return True, "Music resumed"
        return False, "No music to resume" 