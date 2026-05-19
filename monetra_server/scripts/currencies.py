import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
from sqlalchemy.orm import Session

from models.currency import Currency
from core.db import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

CURRENCIES_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "currencies.json"
)


def load_currencies():
    with open(CURRENCIES_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_currencies():
    currencies = load_currencies()
    db: Session = SessionLocal()
    try:
        count = 0
        for currency in currencies:
            if not db.query(Currency).filter_by(code=currency["code"]).first():
                db.add(
                    Currency(code=currency["code"], name=currency["name"], symbol=None)
                )
                count += 1
        db.commit()
        print(f"Seeded {count} new currencies.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding currencies: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_currencies()
