import os
import random

class QuotesManager:
    def __init__(self, active_file_path=None, shuffle=False):
        self.active_file_path = active_file_path
        self.shuffle = shuffle
        self.quotes = []
        self.shuffled_pool = []
        self.current_index = -1
        self.history = []  # Stack of past quote indices for 'go back'
        self.history_index = -1
        
        if self.active_file_path:
            self.reload()

    def set_active_file(self, file_path):
        """Sets a new active quote file and reloads."""
        if self.active_file_path != file_path:
            self.active_file_path = file_path
            self.reload()

    def set_shuffle(self, shuffle):
        """Toggles shuffle mode."""
        if self.shuffle != shuffle:
            self.shuffle = shuffle
            self._reset_navigation()

    def reload(self):
        """Loads and parses quotes from the active file."""
        self.quotes = []
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            print(f"Quotes file not found or not set: {self.active_file_path}")
            self.quotes = ["No quotes found. Select a quote file in Settings."]
            self._reset_navigation()
            return

        try:
            with open(self.active_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.quotes.append(line)
        except Exception as e:
            print(f"Error loading quotes file {self.active_file_path}: {e}")
            self.quotes = [f"Error loading quotes: {str(e)}"]

        if not self.quotes:
            self.quotes = ["The selected quote file is empty."]

        self._reset_navigation()

    def _reset_navigation(self):
        """Resets the indices and history queues."""
        self.current_index = -1
        self.history = []
        self.history_index = -1
        
        if self.shuffle:
            self.shuffled_pool = list(range(len(self.quotes)))
            random.shuffle(self.shuffled_pool)
        else:
            self.shuffled_pool = []

    def get_current(self):
        """Returns the currently active quote."""
        if not self.quotes:
            return ""
        if self.current_index < 0 or self.current_index >= len(self.quotes):
            self.get_next()
        return self.quotes[self.current_index]

    def get_next(self):
        """Navigates to the next quote and returns it."""
        if not self.quotes:
            return ""

        # If we are navigating inside the back-history
        if self.history_index >= 0 and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_index = self.history[self.history_index]
            return self.quotes[self.current_index]

        # Otherwise, generate a new quote index
        next_idx = 0
        if self.shuffle:
            if not self.shuffled_pool:
                self.shuffled_pool = list(range(len(self.quotes)))
                random.shuffle(self.shuffled_pool)
                # Avoid immediately repeating the last quote if possible
                if len(self.quotes) > 1 and self.current_index == self.shuffled_pool[-1]:
                    self.shuffled_pool.insert(0, self.shuffled_pool.pop())
            
            next_idx = self.shuffled_pool.pop()
        else:
            if self.current_index == -1:
                next_idx = 0
            else:
                next_idx = (self.current_index + 1) % len(self.quotes)

        # Update history
        self.current_index = next_idx
        self.history.append(next_idx)
        # Cap history size to 100
        if len(self.history) > 100:
            self.history.pop(0)
        self.history_index = len(self.history) - 1

        return self.quotes[self.current_index]

    def get_previous(self):
        """Navigates to the previous quote from history and returns it."""
        if not self.quotes:
            return ""

        # If we have history we can walk back into
        if self.history_index > 0:
            self.history_index -= 1
            self.current_index = self.history[self.history_index]
            return self.quotes[self.current_index]
        
        # Otherwise, if sequential, wrap backwards
        if not self.shuffle:
            self.current_index = (self.current_index - 1) % len(self.quotes)
            self.history.insert(0, self.current_index)
            self.history_index = 0
            return self.quotes[self.current_index]

        # If shuffle and no history, just return the current one (cannot backtrack further)
        return self.quotes[self.current_index]
