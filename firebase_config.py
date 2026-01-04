"""
Firebase Configuration for Python Backend
Bite Me Buddy Project
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import pyrebase
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FirebaseConfig:
    """Firebase Configuration for Bite Me Buddy Project"""
    
    # ==================== WEB SDK CONFIG (FROM YOUR JS CODE) ====================
    # ये वही config है जो आपके JS code में है
    WEB_CONFIG = {
        "apiKey": "AIzaSyBmZG2Xi5WNXsEbY1gj4MQ6PKnS0gu1S4s",
        "authDomain": "bite-me-buddy.firebaseapp.com",
        "projectId": "bite-me-buddy",
        "storageBucket": "bite-me-buddy.firebasestorage.app",
        "messagingSenderId": "387282094580",
        "appId": "1:387282094580:web:422e09cff55a0ed47bd1a1",
        "measurementId": "G-DXE54QQNB4",
        "databaseURL": "https://bite-me-buddy-default-rtdb.firebaseio.com"  # Add this if using Realtime DB
    }
    
    # ==================== ENVIRONMENT VARIABLES (RECOMMENDED) ====================
    # Production के लिए environment variables use करें
    ENV_CONFIG = {
        "apiKey": os.getenv("FIREBASE_API_KEY", WEB_CONFIG["apiKey"]),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", WEB_CONFIG["authDomain"]),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", WEB_CONFIG["projectId"]),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", WEB_CONFIG["storageBucket"]),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", WEB_CONFIG["messagingSenderId"]),
        "appId": os.getenv("FIREBASE_APP_ID", WEB_CONFIG["appId"]),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", WEB_CONFIG["measurementId"]),
    }
    
    # ==================== SERVICE ACCOUNT PATH ====================
    # Download service account key from Firebase Console
    SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH", "bite-me-buddy-service-account-key.json")
    
    # ==================== DATABASE URLs ====================
    FIRESTORE_DB_URL = f"https://firestore.googleapis.com/v1/projects/{WEB_CONFIG['projectId']}/databases/(default)"
    REALTIME_DB_URL = "https://bite-me-buddy-default-rtdb.firebaseio.com"
    
    # ==================== STORAGE CONFIG ====================
    STORAGE_BUCKET = WEB_CONFIG["storageBucket"]
    
    # ==================== APP CONFIGURATION ====================
    APP_NAME = "bite-me-buddy-app"

def initialize_firebase_admin():
    """
    Initialize Firebase Admin SDK for backend operations
    Returns: Firebase app instance or None
    """
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            # Method 1: Using service account JSON file
            if os.path.exists(FirebaseConfig.SERVICE_ACCOUNT_PATH):
                cred = credentials.Certificate(FirebaseConfig.SERVICE_ACCOUNT_PATH)
                print(f"✅ Using service account file: {FirebaseConfig.SERVICE_ACCOUNT_PATH}")
            else:
                # Method 2: Using environment variables for service account
                service_account_info = {
                    "type": os.getenv("FIREBASE_TYPE", "service_account"),
                    "project_id": os.getenv("FIREBASE_PROJECT_ID", FirebaseConfig.WEB_CONFIG["projectId"]),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
                    "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
                    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", 
                                                            "https://www.googleapis.com/oauth2/v1/certs"),
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
                }
                
                if service_account_info.get("private_key"):
                    cred = credentials.Certificate(service_account_info)
                    print("✅ Using service account from environment variables")
                else:
                    raise FileNotFoundError("Service account file not found and environment variables not set")
            
            # Initialize the app
            app = firebase_admin.initialize_app(
                cred,
                {
                    'projectId': FirebaseConfig.WEB_CONFIG["projectId"],
                    'storageBucket': FirebaseConfig.STORAGE_BUCKET,
                    'databaseURL': FirebaseConfig.REALTIME_DB_URL
                },
                name=FirebaseConfig.APP_NAME
            )
            
            print(f"✅ Firebase Admin SDK initialized for project: {FirebaseConfig.WEB_CONFIG['projectId']}")
            return app
        else:
            print("ℹ️ Firebase already initialized")
            return firebase_admin.get_app(FirebaseConfig.APP_NAME)
            
    except Exception as e:
        print(f"❌ Error initializing Firebase Admin SDK: {str(e)}")
        return None

def get_pyrebase_client():
    """
    Get Pyrebase client for frontend-like operations
    Returns: Pyrebase app instance or None
    """
    try:
        # Use environment variables if available, else use web config
        config = FirebaseConfig.ENV_CONFIG if any(os.getenv(f"FIREBASE_{key}") 
                                                 for key in ["API_KEY", "AUTH_DOMAIN"]) else FirebaseConfig.WEB_CONFIG
        
        firebase = pyrebase.initialize_app(config)
        print("✅ Pyrebase client initialized")
        return firebase
    except Exception as e:
        print(f"❌ Error initializing Pyrebase: {str(e)}")
        return None

def get_firestore_client():
    """Get Firestore database client"""
    try:
        initialize_firebase_admin()
        db = firestore.client()
        print("✅ Firestore client ready")
        return db
    except Exception as e:
        print(f"❌ Error getting Firestore client: {str(e)}")
        return None

def get_auth_client():
    """Get Firebase Auth client"""
    try:
        initialize_firebase_admin()
        return auth
    except Exception as e:
        print(f"❌ Error getting Auth client: {str(e)}")
        return None

def get_storage_client():
    """Get Firebase Storage client"""
    try:
        initialize_firebase_admin()
        bucket = storage.bucket()
        return bucket
    except Exception as e:
        print(f"❌ Error getting Storage client: {str(e)}")
        return None

# Optional: Auto-initialize when imported
# APP = initialize_firebase_admin()

# Export
__all__ = [
    'FirebaseConfig',
    'initialize_firebase_admin',
    'get_pyrebase_client',
    'get_firestore_client',
    'get_auth_client',
    'get_storage_client',
    'firestore',
    'auth',
    'storage'
]