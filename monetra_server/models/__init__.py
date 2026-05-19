from . import (
    transaction,
    user,
    account,
    currency,
    category,
    planner,
    rules,
    budget,
    chat,
)
from monetra_server.core.db import engine


# user.Base.metadata.create_all(bind=engine)
# account.Base.metadata.create_all(bind=engine)
# currency.Base.metadata.create_all(bind=engine)
