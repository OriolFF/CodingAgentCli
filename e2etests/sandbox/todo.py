class Todo:
        def __init__(self, tasks=None):
            self.tasks = list(tasks or [])

        def add_task(self, task):
            self.tasks.append(task)

        def view_tasks(self):
            for index, task in enumerate(self.tasks, 1):
                print(f"{index}. {task}")

        def delete_task(self, task_index):
            if 0 < task_index <= len(self.tasks):
                del self.tasks[task_index - 1]
            else:
                print("Invalid index")