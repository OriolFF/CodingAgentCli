def capitalize_words(s):
    words = s.split()
    return " ".join([word.capitalize() for word in words])

def reverse_string(s):
    return s[::-1]

def count_vowels(s):
    vowels = set("aeiouAEIOU")
    return sum(c in vowels for c in s)