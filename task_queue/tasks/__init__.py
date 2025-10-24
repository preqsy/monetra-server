from task_queue.tasks.account import add_default_accounts, add_default_currency
from task_queue.tasks.category import add_user_default_categories
from task_queue.tasks.currency import update_currencies_exchange_rate
from task_queue.tasks.mono import retrieve_user_mono_transactions
from task_queue.tasks.user import update_user_last_activity


registered_tasks = [
    add_default_currency,
    retrieve_user_mono_transactions,
    add_default_accounts,
    update_currencies_exchange_rate,
    add_user_default_categories,
    update_user_last_activity,
]
