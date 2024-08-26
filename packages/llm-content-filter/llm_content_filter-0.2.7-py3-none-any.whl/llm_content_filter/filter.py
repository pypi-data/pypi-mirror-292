import json
import logging
import unicodedata
from pathlib import Path

class LLMContentFilter:
    def __init__(self, banned_words=None, banned_words_file=None):
        self.logger = logging.getLogger(__name__)
        self.synonyms = {}
        self.severity_levels = {}
        self.replacement_words = {"default": "[REDACTED]"}
        self.contextual_filtering = {"enabled": False, "context_threshold": 0.8}

        if banned_words_file:
            self.load_banned_words_from_file(banned_words_file)
        else:
            default_file = Path(__file__).parent / "default_banned_words.json"
            if default_file.exists():
                self.load_banned_words_from_file(default_file)
            elif banned_words is None:
                self.banned_words = {"violence", "hate", "discrimination", "abuse", "offensive"}
            else:
                self.banned_words = self.validate_banned_words(banned_words)
    
    def validate_banned_words(self, words):
        """Ensure that all banned words are valid strings."""
        return {word for word in words if isinstance(word, str) and word.strip()}
    
    def load_banned_words_from_file(self, file_path):
        """Load banned words and settings from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.banned_words = self.validate_banned_words(data.get("banned_words", []))
                self.synonyms = data.get("synonyms", {})
                self.severity_levels = data.get("severity_levels", {})
                self.replacement_words = data.get("replacement_words", {"default": "[REDACTED]"})
                if "default" not in self.replacement_words:
                    self.replacement_words["default"] = "[REDACTED]"
                self.contextual_filtering = data.get("contextual_filtering", {"enabled": False, "context_threshold": 0.8})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading banned words from file: {e}")
            self.banned_words = set()
    
    def save_banned_words_to_file(self, file_path):
        """Save the current settings to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({
                    "banned_words": list(self.banned_words),
                    "synonyms": self.synonyms,
                    "severity_levels": self.severity_levels,
                    "replacement_words": self.replacement_words,
                    "contextual_filtering": self.contextual_filtering
                }, file, indent=4)
        except IOError as e:
            self.logger.error(f"Error saving banned words to file: {e}")
    
    def normalize_text(self, text):
        """Normalize the text to remove accents and special characters."""
        return ''.join(
            c for c in unicodedata.normalize('NFD', text) 
            if unicodedata.category(c) != 'Mn'
        )
    
    def is_appropriate(self, text):
        """Check if the given text is appropriate."""
        text_lower = self.normalize_text(text.lower())
        all_banned_words = self.banned_words.union(*self.synonyms.values())
        for word in all_banned_words:
            if word in text_lower:
                return False
        return True

    def filter_text(self, text, replacement=None):
        """Filter out inappropriate words from the text.
        
        Args:
            text (str): The input text to be filtered.
            replacement (str, optional): The string to replace banned words with. 
                                         Defaults to the 'default' replacement word.
        """
        text_lower = self.normalize_text(text.lower())
        for word in self.banned_words:
            synonym_list = self.synonyms.get(word, [])
            actual_replacement = replacement or self.replacement_words.get(word, self.replacement_words["default"])
            for synonym in [word] + synonym_list:
                text_lower = text_lower.replace(synonym, actual_replacement)
        return text_lower
