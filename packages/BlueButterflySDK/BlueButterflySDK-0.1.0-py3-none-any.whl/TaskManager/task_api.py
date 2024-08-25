from TaskManager.task_manager import TaskManager

class TaskAPI:
    def __init__(self):
        self.manager = TaskManager()

    def create_task(self, title, description=None, due_date=None, priority="Normal"):
        """
        Create a new task and add it to the task manager.
        """
        return self.manager.add_task(title, description, due_date, priority)

    def get_task(self, task_id):
        """
        Retrieve a task by its ID.
        """
        return self.manager.get_task(task_id)

    def update_task(self, task_id, title=None, description=None, due_date=None, priority=None):
        """
        Update an existing task.
        """
        return self.manager.update_task(task_id, title=title, description=description, due_date=due_date, priority=priority)

    def delete_task(self, task_id):
        """
        Delete a task by its ID.
        """
        return self.manager.delete_task(task_id)

    def list_all_tasks(self):
        """
        List all tasks.
        """
        return self.manager.list_tasks()

    def list_completed_tasks(self):
        """
        List all completed tasks.
        """
        return self.manager.list_tasks(completed=True)

    def list_pending_tasks(self):
        """
        List all pending (not completed) tasks.
        """
        return self.manager.list_tasks(completed=False)

    def complete_task(self, task_id):
        """
        Mark a task as completed.
        """
        return self.manager.mark_task_completed(task_id)
