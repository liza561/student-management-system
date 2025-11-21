# firebase_admin_init.py
import os
import firebase_admin
from firebase_admin import credentials

SERVICE_ACCOUNT_PATH = os.environ.get("serviceAccountKey.json") or "/path/to/serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
