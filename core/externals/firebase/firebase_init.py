import os
import firebase_admin
from firebase_admin import credentials
from core import settings
import json, base64

firebase_str = base64.b64decode(settings.FIREBASE_SERVICE_ACCOUNT_JSON).decode("utf-8")
# print(f"Firebase decoded string: {firebase_str}")
firebase_json = json.loads(firebase_str)


def init_firebase():
    """
    Initialize Firebase Admin SDK if not already initialized.
    """

    print(f"Firebase: {firebase_json}")
    if firebase_admin._apps:
        return firebase_admin.get_app()

    if firebase_json:
        cred = credentials.Certificate(firebase_json)
        print("Initializing Firebase with provided service account JSON.")
        return firebase_admin.initialize_app(
            cred,
            {
                "projectId": "montera-a9760",
            },
        )
    else:
        print("Initializing Firebase with default credentials and explicit projectId.")
        return firebase_admin.initialize_app(
            options={
                "projectId": "montera-a9760",
            }
        )
