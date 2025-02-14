import re
from collections import Counter

def exclude_letters(words: list[str], letters: str):
    """Exclude words that contain any of the given letters."""
    return [word for word in words if not any(letter in word for letter in letters)]

def filter_by_length(words: list[str], exact_length: int):
    """Keep only words that have the exact specified length."""
    return [word for word in words if len(word) == exact_length]

def contains_letters(words: list[str], substring: str):
    """Keep only words that contain all letters in the substring, considering duplicate letters as one letter."""
    substring_counter = Counter(substring)  # Count occurrences of each letter in substring
    
    filtered_words = []
    for word in words:
        word_counter = Counter(word)  # Count occurrences of each letter in word
        
        # Check if word contains at least as many occurrences of each letter in substring
        if all(word_counter[char] >= count for char, count in substring_counter.items()):
            filtered_words.append(word)
    
    return filtered_words

def filter_by_pattern(words: list[str], pattern: str):
    """Keep only words that match the given pattern with fixed letters and wildcards. Wildcards is represented by the '?' character.
       Each '?' in the pattern can match any single character, while fixed letters must match the corresponding position in the word."""
    regex_pattern = pattern.replace('?', '.')
    regex = re.compile(f'^{regex_pattern}$')
    return [word for word in words if regex.match(word)]