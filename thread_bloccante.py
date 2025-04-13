import threading
import time

class HeavyTaskThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._results = None
        self._is_running = False

    def run(self):
        """Heavy computation or blocking task goes here."""
        self._is_running = True
        self._results = self.heavy_function()
        self._is_running = False

    def heavy_function(self):
        """Simulate a heavy computation or blocking task."""
        time.sleep(30)  # Simulate a long task
        return "Task Completed!"

    def heavy_function1(self):
        """Simulate a heavy computation or blocking task."""
        time.sleep(30)  # Simulate a long task
        return "Task Completed!"

    def heavy_function2(self):
        """Simulate a heavy computation or blocking task."""
        time.sleep(30)  # Simulate a long task
        return "Task Completed!"

    def check(self):
        """Check if the thread is still running."""
        return self.is_alive()

    def get_results(self):
        """Retrieve the results after the task completes."""
        if self._is_running:
            raise Exception("Task is still running, results are not available yet.")
        return self._results


# Example usage:
if __name__ == "__main__":
    task = HeavyTaskThread()
    task.start()
    

    while task.check():
        print("Task is still running...")
        time.sleep(1)

    print("Task completed. Result:", task.get_results())