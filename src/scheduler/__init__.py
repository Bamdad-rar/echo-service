from .repository import TaskRepo, RecurringPackagePollingRepo
from adapters.database import task_table, engine, poll_engine, recurring_package_table, user_recurring_package_table

task_repository = TaskRepo(engine, task_table)
recurring_pacakge_repo = RecurringPackagePollingRepo(poll_engine,user_recurring_package_table,recurring_package_table)
