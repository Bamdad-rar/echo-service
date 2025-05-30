from scheduler.models import Task

def next_occurrence(task: Task) -> int | None:
    match task.period:
        case "seconds": return second_planner(task)
        case "minutes": return minute_planner(task)
        case "hours": return hour_planner(task)
        case "days": return day_planner(task)
        case "weeks": return week_planner(task)
        case "months": return month_planner(task)
        case "jmonths": return jmonth_planner(task)
    return None


def second_planner(task: Task) -> int:
    ...

def minute_planner(task: Task) -> int:
    ...

def hour_planner(task: Task) -> int:
    ...

def day_planner(task: Task) -> int:
    ...

def week_planner(task: Task) -> int:
    ...


def month_planner(task: Task) -> int:
    ...


def jmonth_planner(task: Task) -> int:
    ...

