import re
from collections import Counter

class WordFilter:
    def __init__(self):
        self.excluded_letters = set()
        self.included_letters = set()
        self.pattern = None
        self.length = None
        self.word_count = 0

    def exclude_letters(self, words: list[str], letters: str):
        """Exclude words that contain any of the given letters."""
        conflicting_letters = set(letters).intersection(self.included_letters)
        if conflicting_letters:
            print(f"Cannot exclude letters {conflicting_letters} as they are already in contained letters.")
            return words

        self.excluded_letters.update(letters)
        filtered_words = [word for word in words if not any(letter in word for letter in letters)]
        self.word_count = len(filtered_words)
        return [word for word in words if not any(letter in word for letter in letters)]

    def include_letters(self, words: list[str], letters: str):
        """Keep only words that contain all letters in the substring, considering duplicate letters as one letter."""
        conflicting_letters = set(letters).intersection(self.excluded_letters)
        if conflicting_letters:
            print(f"Cannot contain letters {conflicting_letters} as they are already in excluded letters.")
            return words

        self.included_letters.update(letters)

        letter_counter = Counter(letters)  # Count occurrences of each letter in substring
        filtered_words = []
        for word in words:
            word_counter = Counter(word)  # Count occurrences of each letter in word

            # Check if word contains at least as many occurrences of each letter in substring
            if all(word_counter[char] >= count for char, count in letter_counter.items()):
                filtered_words.append(word)
        self.word_count = len(filtered_words)
        return filtered_words

    def by_pattern(self, words: list[str], pattern: str):
        """Keep only words that match the given pattern with fixed letters and wildcards. Wildcards is represented by the '?' character.
               Each '?' in the pattern can match any single character, while fixed letters must match the corresponding position in the word."""
        self.pattern = pattern
        regex_pattern = pattern.replace('?', '.')
        regex = re.compile(f'^{regex_pattern}$')

        filtered_words = [word for word in words if regex.match(word)]
        self.word_count = len(filtered_words)
        return filtered_words

    def by_length(self, words: list[str], exact_length: int):
        """Keep only words that have the exact specified length."""
        if exact_length != 0:
            filtered_words = [word for word in words if len(word) == exact_length]
        else:
            filtered_words = words
        return filtered_words