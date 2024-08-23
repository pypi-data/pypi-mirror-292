import argparse
from datetime import datetime
import json
import os


LOG_FILE = "time_log.json"
CURRENT = "current_task"
TASKS = "tasks"
TASK_NAME = "task_name"
LAST_UPDATED = "last_updated"
TIME_SPENT = "time_spent"

class TimeTracker:
    def __init__(self):
      self.tasks = {}
      self.current_task = None
    
    def load_data(self):
      data = { CURRENT: None, TASKS:{} }
      if os.path.exists(LOG_FILE):
          with open(LOG_FILE, 'r') as file:
              data = json.load(file)
      self.tasks = data[TASKS]
      self.current_task = data[CURRENT]

    def save_data(self):
      data = { CURRENT: self.current_task, TASKS: self.tasks }
      with open(LOG_FILE, 'w') as file:
        json.dump(data, file, indent=4)

    def create_task(self, task_name):
        self.tasks[task_name] = {TASK_NAME: task_name, LAST_UPDATED: None, TIME_SPENT: 0}
        print(f"Added '{task_name}' to tracked tasks")

    def update_current(self):
        if self.current_task is None:
            return
        current_task = self.tasks[self.current_task]
        last_updated = datetime.fromisoformat(current_task[LAST_UPDATED])
        now = datetime.now()
        elapsed_time = now - last_updated
        current_task[TIME_SPENT] += int(elapsed_time.total_seconds())
        current_task[LAST_UPDATED] = now.isoformat()

    def start_task(self, task_name):
        self.update_current()
        if task_name not in self.tasks:
            self.create_task(task_name)
        now = datetime.now().isoformat()
        self.tasks[task_name][LAST_UPDATED] = now
        self.current_task = task_name
        print(f"Started tracking task: '{task_name}' at {now}")

    def pause_task(self, ):
        if self.current_task is None:
            print("No task is currently running.")
            return
        self.update_current()
        current_task_name = self.current_task
        self.current_task = None
        print(f"Paused the current task '{current_task_name}'.")

    def log_tasks(self, ):
        self.update_current()
        if len(self.tasks) == 0:
            print("No tasks logged.")
            return
        for _,entry in self.tasks.items():
            print(f"Task: {entry[TASK_NAME]} | Last Updated: {entry[LAST_UPDATED]} | Time Spent: {entry[TIME_SPENT]}")



def main():
    parser = argparse.ArgumentParser(description="Task Time Tracking Tool")
    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser('start', help="Start a new task.")
    start_parser.add_argument('task', type=str, help="The name of the task to start.")

    subparsers.add_parser('pause', help="Pause the current task.")

    subparsers.add_parser('log', help="Show logged tasks.")

    args = parser.parse_args()

    t4 = TimeTracker()
    try:
        t4.load_data()
        if args.command == "start":
            t4.start_task(args.task)
        elif args.command == "pause":
            t4.pause_task()
        elif args.command == "log":
            t4.log_tasks()
        else:
            parser.print_help()
        t4.save_data()
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    main()


        
        