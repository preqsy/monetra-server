import os
import firebase_admin
from firebase_admin import credentials
from core import settings


def init_firebase():
    """
    Initialize Firebase Admin SDK if not already initialized.
    """
    if firebase_admin._apps:
        return firebase_admin.get_app()

    if settings.FIREBASE_ADMIN_SDK_JSON_PATH and os.path.exists(
        settings.FIREBASE_ADMIN_SDK_JSON_PATH
    ):
        cred = credentials.Certificate(settings.FIREBASE_ADMIN_SDK_JSON_PATH)
        print("Initializing Firebase with provided service account JSON.")
        return firebase_admin.initialize_app(
            cred,
            {
                "projectId": "montera-a9760",
            },
        )
    else:
        print("Initializing Firebase with default credentials.")
        return firebase_admin.initialize_app()
