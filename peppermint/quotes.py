import os
import random

class QuotesManager:
    def __init__(self, active_file_path=None, shuffle=False):
        self.active_file_path = active_file_path
        self.shuffle = shuffle
        self.quotes = []
        self.current_index = -1
        if self.active_file_path:
            self.reload()

    def set_active_file(self, file_path):
        if self.active_file_path != file_path:
            self.active_file_path = file_path
            self.reload()

    def set_shuffle(self, shuffle):
        self.shuffle = shuffle

    def reload(self):
        self.quotes = []
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            self.quotes = ["No quotes found. Select a quote file in Settings."]
            self.current_index = -1
            return
        try:
            with open(self.active_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.quotes.append(line)
        except Exception as e:
            self.quotes = [f"Error loading quotes: {str(e)}"]

        if not self.quotes:
            self.quotes = ["The selected quote file is empty."]
        self.current_index = -1

    def get_current(self):
        if not self.quotes:
            return ""
        if self.current_index < 0 or self.current_index >= len(self.quotes):
            self.get_next()
        return self.quotes[self.current_index]

    def get_next(self):
        if not self.quotes:
            return ""
        if self.shuffle:
            self.current_index = random.randint(0, len(self.quotes) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.quotes)
        return self.quotes[self.current_index]

    def get_previous(self):
        if not self.quotes:
            return ""
        if self.shuffle:
            self.current_index = random.randint(0, len(self.quotes) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.quotes)
        return self.quotes[self.current_index]
