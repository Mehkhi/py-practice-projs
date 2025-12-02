#!/usr/bin/env python3
"""
Run script for Flask Mini API.

This script starts the Flask development server.
"""

import os
import sys
from flask_mini_api.main import app, db_manager

def main():
    """Main function to run the Flask app."""
    print("🚀 Starting Flask Mini API...")
    print("=" * 50)

    # Initialize database
    try:
        db_manager.init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

    # Print useful information
    print("\n📋 API Information:")
    print(f"   • URL: http://localhost:5001")
    print(f"   • Documentation: http://localhost:5001/docs/")
    print(f"   • Health Check: http://localhost:5001/health")
    print("\n🔧 Available endpoints:")
    print("   • GET    /health                    - Health check")
    print("   • POST   /api/auth/register         - Register user")
    print("   • POST   /api/auth/login            - Login user")
    print("   • GET    /api/tasks                 - Get all tasks")
    print("   • POST   /api/tasks                 - Create task")
    print("   • GET    /api/tasks/<id>            - Get specific task")
    print("   • PUT    /api/tasks/<id>            - Update task")
    print("   • DELETE /api/tasks/<id>            - Delete task")
    print("   • GET    /api/users                 - Get all users")
    print("   • POST   /api/users                 - Create user")
    print("   • GET    /api/users/<id>            - Get specific user")
    print("   • PUT    /api/users/<id>            - Update user")
    print("   • DELETE /api/users/<id>            - Delete user")
    print("\n🔑 Authentication:")
    print("   • All API endpoints (except /health and /auth/*) require API key")
    print("   • Include API key in header: X-API-Key: your_api_key")
    print("   • Or in Authorization header: Bearer your_api_key")
    print("\n📖 Run 'python demo.py' to see the API in action!")
    print("=" * 50)

    # Start the Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Flask Mini API...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
