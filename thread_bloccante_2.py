import threading
import time
import uuid
from typing import Dict, Any, Callable, Optional, List

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, TaskThread] = {}
    
    def submit_task(self, heavy_function: Callable, task_name: Optional[str] = None) -> str:
        """
        Submit a task to be executed in a separate thread.
        
        Args:
            heavy_function: The function to execute
            task_name: Optional name for the task (auto-generated if not provided)
            
        Returns:
            task_id: Unique identifier for the submitted task
        """
        task_id = task_name or str(uuid.uuid4())
        task = TaskThread(heavy_function, task_id)
        self.tasks[task_id] = task
        task.start()
        return task_id
    
    def check_task(self, task_id: str) -> bool:
        """
        Check if a specific task is still running.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            bool: True if task is still running, False otherwise
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with ID {task_id} not found")
        return self.tasks[task_id].check()
    
    def get_task_result(self, task_id: str) -> Any:
        """
        Get the result of a specific task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Any: The result returned by the task
            
        Raises:
            Exception: If task is still running or not found
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task with ID {task_id} not found")
        return self.tasks[task_id].get_results()
    
    def get_all_task_ids(self) -> List[str]:
        """Get IDs of all tasks that have been submitted."""
        return list(self.tasks.keys())
    
    def get_running_task_ids(self) -> List[str]:
        """Get IDs of all currently running tasks."""
        return [task_id for task_id, task in self.tasks.items() if task.check()]
    
    def get_completed_task_ids(self) -> List[str]:
        """Get IDs of all completed tasks."""
        return [task_id for task_id, task in self.tasks.items() if not task.check()]
    
    def get_all_available_results(self) -> Dict[str, Any]:
        """Get results of all completed tasks."""
        results = {}
        for task_id in self.get_completed_task_ids():
            try:
                results[task_id] = self.get_task_result(task_id)
            except Exception as e:
                results[task_id] = f"Error retrieving result: {str(e)}"
        return results


class TaskThread(threading.Thread):
    def __init__(self, function: Callable, task_id: str):
        super().__init__()
        self.function = function
        self.task_id = task_id
        self._results = None
        self._is_running = False
        self._error = None
    
    def run(self):
        """Execute the heavy function and capture results or errors."""
        self._is_running = True
        try:
            self._results = self.function()
        except Exception as e:
            self._error = e
        finally:
            self._is_running = False
    
    def check(self):
        """Check if the thread is still running."""
        return self.is_alive()
    
    def get_results(self):
        """
        Retrieve the results after the task completes.
        
        Raises:
            Exception: If task is still running or encountered an error
        """
        if self._is_running:
            raise Exception("Task is still running, results are not available yet.")
        if self._error:
            raise Exception(f"Task failed with error: {str(self._error)}")
        return self._results


# Example usage:
def example():
    def heavy_task1():
        """Simulate a heavy computation task."""
        time.sleep(5)
        return "Task 1 Completed!"
    
    def heavy_task2():
        """Simulate another heavy computation task."""
        time.sleep(8)
        return "Task 2 Completed!"
    
    def heavy_task3():
        """Simulate a task that raises an exception."""
        time.sleep(3)
        raise ValueError("Simulated error in task 3")
    
    # Create a task manager
    manager = TaskManager()
    
    # Submit multiple tasks
    task1_id = manager.submit_task(heavy_task1, "task1")
    task2_id = manager.submit_task(heavy_task2, "task2")
    task3_id = manager.submit_task(heavy_task3, "task3")