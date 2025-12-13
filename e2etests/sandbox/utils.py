def capitalize_words(text):
    words = text.split()
    return " ".join([word.capitalize() for word in words])

def reverse_string(text):
    return text[::-1]

def count_vowels(text):
    vowel_count = { 'a': 0, 'e': 0, 'i': 0, 'o': 0, 'u': 0 }

    for char in text:
        if char in vowel_count and char != char.lower():
            continue

        vowel_count[char] = 1 if char in "aeiou" else 0

    return sum(vowel_count.values())