from enum import Enum
from tinydb import TinyDB, Query
from datetime import datetime
import re

from pydantic import BaseModel, Field, ConfigDict

db = TinyDB("tasks.js")
Q = Query()


class PriorityEnum(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"
    MEDIUM = "MEDIUM"


class TaskModelPost(BaseModel):
    title: str
    desc: str
    due_date: datetime | None = None
    priority: PriorityEnum | None = None
    completed: bool = Field(default=False)

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.strftime("%d.%m.%Y") if v else None},
        arbitrary_types_allowed=True,  # разрешаване на произволни типове
        extra="forbid",  # забраняване на допълнителни полета
    )


# Tasks
def add_task():
    title = input("Enter title: ")
    desc = input("Enter description: ")
    while True:
        try:
            due_date_str = input("Enter due_date (dd.mm.yyyy): ")
            due_date = datetime.strptime(due_date_str, "%d.%m.%Y")
            break
        except ValueError:
            print("Not valid format for date")
    while True:
        priority = input("Enter priority: HIGH, LOW, MEDIUM: ")
        if priority.upper() in PriorityEnum.__members__:
            priority = PriorityEnum[priority.upper()]
            break
        else:
            print("Not valid priority")
    task = TaskModelPost(title=title, desc=desc, due_date=due_date, priority=priority)  # type: ignore
    task_convert = task.model_dump()
    task_convert["due_date"] = (
        task.due_date.strftime("%d.%m.%Y") if task.due_date else None
    )
    print(task_convert)
    confirm = input("Do you want to save the task? (yes/no): ")
    if confirm.lower() == "yes":
        db.insert(task_convert)
        print("Task saved successfully!")
    else:
        print("Task not saved.")
        exit()


def list_tasks():
    print("\n=== СПИСЪК ЗАДАЧИ ===")
    print("Тук ще бъдат показани всички задачи...")
    tasks = db.all()
    [print(f"{id}: {t}") for id, t in enumerate(tasks, start=1)]


def search_by_title():
    print("\n=== ТЪРСЕНЕ ПО ЗАГЛАВИЕ ===")
    title = input("Въведете заглавие за търсене: ")
    print(f"Търсене за: {title}")
    result = db.search(Q.title.test(lambda x: title.lower() in x.lower()))  # type: ignore
    [print(f"{r.doc_id}: {r}") for r in result]


def change_task_status():
    print("\n=== ПРОМЯНА НА СТАТУС ===")
    # TODO: Имплементирай промяна на статус
    task_id = int(input("Въведете ID на задачата, която искате да промените: "))
    task = db.get(doc_id=task_id)
    if not task:
        print("Not found trask with this id {}".format(task_id))
        return

    new_status = not task["completed"]
    try:
        db.update({"completed": new_status}, doc_ids=[task_id])
    except Exception as e:
        print("Error while updating task status: {}".format(e))


def show_statistics():
    print("\n=== СТАТИСТИКА ===")
    # TODO: Имплементирай статистика
    pass


def exit_program():
    print("\n👋 Благодарим, че използвахте програмата! До скоро!")
    exit()


# end with tasks
def mapper_choices(function_choice: int):
    mapper = {
        1: add_task,
        2: list_tasks,
        3: search_by_title,
        4: change_task_status,
        5: show_statistics,
        6: exit_program,
    }
    return mapper[function_choice]


def main():
    choices = {
        1: "Add task",
        2: "List with tasks",
        3: "Search by title",
        4: "Change is done",
        5: "Statistics",
        6: "Exit",
    }
    [print(f"{key}: {val}") for key, val in choices.items()]
    choice = int(input("What is yout choice :"))
    try:
        valid_choice = mapper_choices(choice)
    except KeyError, ValueError:
        print("Not valid choice")
        return
    else:
        return valid_choice()


if __name__ == "__main__":
    main()
