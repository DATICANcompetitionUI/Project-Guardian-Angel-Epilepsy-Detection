"""
TEST FIREBASE CONNECTION
Run: python test_firebase.py
"""

import pyrebase
from firebase_config import FIREBASE_CONFIG

print("🔄 Testing Firebase connection...")

try:
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    auth = firebase.auth()
    db = firebase.database()
    
    # Try to create a test user
    test_email = "test@test.com"
    test_password = "test1234"
    
    try:
        user = auth.create_user_with_email_and_password(test_email, test_password)
        print("✅ Authentication works! User created.")
        
        # Test database
        db.child("test").push({"message": "Firebase is working!"})
        print("✅ Database works! Data saved.")
        
        print("\n🎉 ALL GOOD! Firebase is configured correctly.")
        
    except Exception as e:
        error = str(e)
        if "EMAIL_EXISTS" in error:
            print("✅ Authentication works (test user already exists).")
        elif "CONFIGURATION_NOT_FOUND" in error:
            print("❌ ERROR: Enable Email/Password authentication in Firebase Console.")
            print("   Go to: Firebase Console → Authentication → Sign-in methods → Email/Password → Enable")
        else:
            print(f"❌ Error: {error}")
            
except Exception as e:
    print(f"❌ Failed to initialize Firebase: {e}")
    print("Check your FIREBASE_CONFIG in firebase_config.py")