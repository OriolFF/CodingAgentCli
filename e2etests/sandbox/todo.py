import os
from typing import List

DATA_FILE = "todos.txt"  # Data storage file

def load_todos() -> List[str]:
    if not os.path.isfile(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        todos = [line.strip("\n") for line in f.readlines()]
    return todos

def save_todos(todos: List[str]):
    with open(DATA_FILE, "w") as f:
        for todo in todos:
            f.write(f"{todo}\n")

def add_todo(todo: str) -> None:
    todos = load_todos()
    todos.append(todo)
    save_todos(todos)

def remove_todo(index: int) -> None:
    todos = load_todos()
    if len(todos) <= index:
        return
    del todos[index]
    save_todos(todos)