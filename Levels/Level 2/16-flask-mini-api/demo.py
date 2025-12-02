#!/usr/bin/env python3
"""
Demo script for Flask Mini API.

This script demonstrates how to use the API endpoints.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5001"

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request and return response."""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return response
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running.")
        return None

def print_response(response, title):
    """Print formatted response."""
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")

    if response is None:
        return

    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def main():
    """Main demo function."""
    print("🚀 Flask Mini API Demo")
    print("=" * 50)

    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    for i in range(10):
        response = make_request('GET', '/health')
        if response and response.status_code == 200:
            print("✅ Server is ready!")
            break
        time.sleep(1)
    else:
        print("❌ Server is not responding. Please start the server first.")
        return

    # Health check
    response = make_request('GET', '/health')
    print_response(response, "Health Check")

    # Register a new user
    user_data = {
        "username": "demouser",
        "email": "demo@example.com"
    }
    response = make_request('POST', '/api/auth/register', user_data)
    print_response(response, "User Registration")

    if response and response.status_code == 201:
        api_key = response.json().get('api_key')
        headers = {'X-API-Key': api_key}
        print(f"🔑 API Key: {api_key}")

        # Create some tasks
        tasks = [
            {
                "title": "Learn Flask",
                "description": "Build a REST API with Flask",
                "priority": "high",
                "completed": False
            },
            {
                "title": "Write tests",
                "description": "Write comprehensive unit tests",
                "priority": "medium",
                "completed": False
            },
            {
                "title": "Document API",
                "description": "Create API documentation",
                "priority": "low",
                "completed": True
            }
        ]

        created_tasks = []
        for i, task_data in enumerate(tasks, 1):
            response = make_request('POST', '/api/tasks', task_data, headers)
            print_response(response, f"Create Task {i}")
            if response and response.status_code == 201:
                created_tasks.append(response.json().get('task'))

        # Get all tasks
        response = make_request('GET', '/api/tasks', headers=headers)
        print_response(response, "Get All Tasks")

        # Update first task
        if created_tasks:
            task_id = created_tasks[0]['id']
            update_data = {"completed": True}
            response = make_request('PUT', f'/api/tasks/{task_id}', update_data, headers)
            print_response(response, f"Update Task {task_id}")

        # Get specific task
        if created_tasks:
            task_id = created_tasks[0]['id']
            response = make_request('GET', f'/api/tasks/{task_id}', headers=headers)
            print_response(response, f"Get Task {task_id}")

        # Get all users
        response = make_request('GET', '/api/users', headers=headers)
        print_response(response, "Get All Users")

        # Test error handling
        print("\n🧪 Testing Error Handling:")

        # Try to get non-existent task
        response = make_request('GET', '/api/tasks/999', headers=headers)
        print_response(response, "Get Non-existent Task (404)")

        # Try to create task without API key
        response = make_request('POST', '/api/tasks', tasks[0])
        print_response(response, "Create Task Without API Key (401)")

        # Try to create task with invalid data
        invalid_task = {"title": ""}  # Empty title
        response = make_request('POST', '/api/tasks', invalid_task, headers)
        print_response(response, "Create Task With Invalid Data (400)")

    print(f"\n{'='*50}")
    print("🎉 Demo completed!")
    print("📚 Visit http://localhost:5001/docs/ for API documentation")
    print("🔧 Use the API key above to test other endpoints")

if __name__ == "__main__":
    main()
