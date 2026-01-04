# firebase_admin.py
import firebase_admin
from firebase_admin import credentials, auth
import os

def initialize_firebase_admin():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase Admin is already initialized
        if not firebase_admin._apps:
            # Get Firebase service account key from environment
            service_account_key = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
            
            if service_account_key:
                # Use JSON key from environment variable
                cred_dict = json.loads(service_account_key)
                cred = credentials.Certificate(cred_dict)
            else:
                # Use default credentials (for local development)
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing Firebase Admin: {str(e)}")
        return False

def verify_phone_token(id_token):
    """Verify Firebase phone authentication token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            'success': True,
            'uid': decoded_token['uid'],
            'phone_number': decoded_token.get('phone_number')
        }
    except auth.ExpiredIdTokenError:
        return {'success': False, 'message': 'Token expired'}
    except auth.InvalidIdTokenError:
        return {'success': False, 'message': 'Invalid token'}
    except Exception as e:
        return {'success': False, 'message': str(e)}