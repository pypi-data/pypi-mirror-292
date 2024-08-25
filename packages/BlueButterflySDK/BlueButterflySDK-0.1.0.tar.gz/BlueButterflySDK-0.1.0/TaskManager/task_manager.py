class Task:
    def __init__(self, title, description=None, due_date=None, priority="Normal"):
        self.id = id(self)  # Unique identifier for the task
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.is_completed = False

    def __repr__(self):
        return f"<Task id={self.id}, title={self.title}, completed={self.is_completed}>"

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def add_task(self, title, description=None, due_date=None, priority="Normal"):
        task = Task(title, description, due_date, priority)
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def update_task(self, task_id, **kwargs):
        task = self.get_task(task_id)
        if not task:
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        return task

    def delete_task(self, task_id):
        return self.tasks.pop(task_id, None)

    def list_tasks(self, completed=None):
        if completed is None:
            return list(self.tasks.values())
        return [task for task in self.tasks.values() if task.is_completed == completed]

    def mark_task_completed(self, task_id):
        task = self.get_task(task_id)
        if task:
            task.is_completed = True
        return task

