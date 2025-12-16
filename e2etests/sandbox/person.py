class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age

    def greet(self):
        text = f"Hi, I am {self._name} and I am {self._age} years old."
        return text