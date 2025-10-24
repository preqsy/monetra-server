import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from core.db import SessionLocal, engine, Base
from models.user import SubscriptionPlan, PlanFeature
import json

Base.metadata.create_all(bind=engine)


# Load plans and features from config.json

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

PLANS = config.get("plans", [])
FEATURES = config.get("features", [])


def seed_subscriptions():
    db: Session = SessionLocal()
    try:
        # Seed plans
        plan_objs = []
        for plan in PLANS:
            plan_obj = db.query(SubscriptionPlan).filter_by(name=plan["name"]).first()
            if not plan_obj:
                plan_obj = SubscriptionPlan(
                    name=plan["name"],
                    price=plan["price"],
                    billing_cycle=plan["billing_cycle"],
                    description=plan["description"],
                )
                db.add(plan_obj)
                db.flush()
                print(f"Inserted plan: {plan['name']}")
            else:
                print(f"Plan already exists: {plan['name']}")
            plan_objs.append(plan_obj)

        # Seed features
        feature_objs = []
        for feature in FEATURES:
            # config.json uses 'name', not 'feature_name'
            feature_name = feature.get("feature_name") or feature.get("name")
            description = feature.get("description")
            feature_obj = (
                db.query(PlanFeature).filter_by(feature_name=feature_name).first()
            )
            if not feature_obj:
                feature_obj = PlanFeature(
                    feature_name=feature_name,
                    description=description,
                    enabled=True,
                )
                db.add(feature_obj)
                db.flush()
                print(f"Inserted feature: {feature_name}")
            else:
                print(f"Feature already exists: {feature_name}")
            feature_objs.append(feature_obj)

        # Link all features to all plans (if not already linked)
        for plan in plan_objs:
            for feature in feature_objs:
                if feature not in plan.features:
                    plan.features.append(feature)
                    print(
                        f"Linked feature '{feature.feature_name}' to plan '{plan.name}'"
                    )
        db.commit()
        print("Seeding complete.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding subscriptions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_subscriptions()
