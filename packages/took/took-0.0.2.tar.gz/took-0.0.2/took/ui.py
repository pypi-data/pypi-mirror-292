import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text


# Load JSON data from file
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Display the current task
def show_current_task(tt):
    console = Console()
    current_task = tt.current_task
    task_info = tt.tasks.get(current_task, {})
    
    if task_info:
        console.print(Panel(f"Current Task: {current_task}", style="bold green"))
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Task Name", style="dim", width=20)
        table.add_column("Last Updated", style="dim", width=30)
        table.add_column("Time Spent (s)", style="dim")
        table.add_row(
            task_info["task_name"],
            task_info["last_updated"],
            str(task_info["time_spent"])
        )
        console.print(table)
    else:
        console.print(f"No information available for current task: {current_task}")

# Display all tasks
def show_all_tasks(tt):
    console = Console()
    tasks = tt.tasks
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Task Name", style="dim", width=20)
    table.add_column("Last Updated", style="dim", width=30)
    table.add_column("Time Spent (s)", style="dim")
    
    for task_name, task_info in tasks.items():
        table.add_row(
            task_info["task_name"],
            task_info["last_updated"],
            str(task_info["time_spent"])
        )
    
    console.print(Panel("All Tasks", style="bold blue"))
    console.print(table)

# Main function to navigate through tasks
def main(tt):
    data = load_data("time_log.json")
    console = Console()

    while True:
        console.print(Panel("Took Navigator", style="bold cyan"))
        console.print("1. View Current Task")
        console.print("2. View All Tasks")
        console.print("3. Exit")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"])
        tt.refresh()
        if choice == "1":
            show_current_task(tt)
        elif choice == "2":
            show_all_tasks(tt)
        elif choice == "3":
            console.print("Exiting...")
            break

# if __name__ == "__main__":
#     main()
