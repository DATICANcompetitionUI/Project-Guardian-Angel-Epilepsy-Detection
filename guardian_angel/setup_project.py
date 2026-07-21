"""
SETUP PROJECT ON LOCAL MACHINE
Run this after extracting the ZIP
python setup_project.py
"""

import os
import subprocess
import sys

print("=" * 70)
print("👼 GUARDIAN ANGEL - LOCAL SETUP")
print("=" * 70)

# 1. Check Python version
print("\n📌 Checking Python version...")
python_version = sys.version_info
print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 12):
    print("   ⚠️ Recommended: Python 3.12+")

# 2. Create virtual environment
print("\n📌 Creating virtual environment...")
if not os.path.exists('venv'):
    subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    print("   ✅ Virtual environment created")
else:
    print("   ✅ Virtual environment already exists")

# 3. Activate and install dependencies
print("\n📌 Installing dependencies...")

# Determine activation command
if sys.platform == 'win32':
    activate = 'venv\\Scripts\\activate'
    python_cmd = 'venv\\Scripts\\python'
else:
    activate = 'source venv/bin/activate'
    python_cmd = 'venv/bin/python'

# Install requirements
subprocess.run([python_cmd, '-m', 'pip', 'install', '--upgrade', 'pip'])
subprocess.run([python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'])

print("   ✅ Dependencies installed")

# 4. Create .env file
print("\n📌 Creating .env file...")
if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write("""# Guardian Angel - Environment Variables
# Fill in your Twilio credentials for SMS alerts

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
""")
    print("   ✅ .env file created (fill in your credentials)")
else:
    print("   ✅ .env file already exists")

# 5. Verify app exists
print("\n📌 Verifying app files...")
if os.path.exists('app/app.py'):
    print("   ✅ app/app.py found")
else:
    print("   ❌ app/app.py not found - check your folder structure")

# 6. Final instructions
print("\n" + "=" * 70)
print("✅ LOCAL SETUP COMPLETE!")
print("=" * 70)

print("""
📌 To run the app:

   # Activate virtual environment
   # Windows:
   venv\\Scripts\\activate

   # Mac/Linux:
   source venv/bin/activate

   # Run the app
   streamlit run app/app.py

📌 To install as PWA on phone:
   1. Open http://localhost:8501 in Chrome
   2. Tap "Add to Home Screen"
   3. Use as standalone app

📌 For emergency SMS alerts:
   1. Sign up at https://www.twilio.com/try-twilio
   2. Get Account SID, Auth Token, and phone number
   3. Add to .env file
   4. Restart the app

📌 Good luck with the competition! 🏆
""")