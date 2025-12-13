def edit_files(instructions):
    instructions = f"""\
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello! I am {self.name} and I'm {self.age} years old."
    """

    assistance = {"instructions": instructions + "\n\n"}

    # Create file sandbox/models.py if it doesn't exist already
    create_file = {"path": "sandbox/models.py", "content": ""}
    edit_request = {"request": assistance, "options": {"replace_existing": True}}
    res = edit_files(edit_request)

    # Add the code to the existing file
    append_content = {"path": "sandbox/models.py", "content": instructions}
    edit_request = {"request": append_content, "options": {"append": True}}
    res = edit_files(edit_request)

print("Created sandbox/models.py with the Person class")