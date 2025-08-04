#!/usr/bin/env python3
"""
Helper script to create a .env file with default configuration values.
Run this script to generate your .env file.
"""

import os

def create_env_file():
    """Create a .env file with default configuration"""
    
    env_content = """# Environment Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=names.db

# Server Configuration
HOST=0.0.0.0
PORT=5000

# URLs
PRODUCTION_URL=https://novel-ebook.onrender.com
LOCAL_URL=http://localhost:5000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5000,https://novel-ebook.onrender.com

# Logging
LOG_LEVEL=INFO

# Security (change in production)
SECRET_KEY=dev-secret-key-change-in-production
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("📝 You can now customize the values in the .env file as needed.")
        print("🚀 Run 'python app.py' to start the application.")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 