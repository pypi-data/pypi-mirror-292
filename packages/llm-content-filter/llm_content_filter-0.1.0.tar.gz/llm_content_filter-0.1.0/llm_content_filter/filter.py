# llm_content_filter/filter.py

class LLMContentFilter:
    def __init__(self, banned_words=None):
        if banned_words is None:
            self.banned_words = {"violence", "hate", "discrimination", "abuse", "offensive"}
        else:
            self.banned_words = set(banned_words)
    
    def is_appropriate(self, text):
        """Check if the given text is appropriate."""
        text_lower = text.lower()
        for word in self.banned_words:
            if word in text_lower:
                return False
        return True

    def filter_text(self, text):
        """Filter out inappropriate words from the text."""
        text_lower = text.lower()
        for word in self.banned_words:
            text_lower = text_lower.replace(word, "[REDACTED]")
        return text_lower
