from repository import TaskRepo
from adapters.database import task_table, engine

task_repository = TaskRepo(engine, task_table)
