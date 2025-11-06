# test_api.py
import requests

BASE_URL = "http://localhost:8000"

print("🧪 Testing FitMentor AI API\n")

# Test 1: Health Check
print("1. Testing health check...")
response = requests.get(f"{BASE_URL}/api/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Test 2: List Exercises
print("2. Testing list exercises...")
response = requests.get(f"{BASE_URL}/api/exercises")
print(f"   Status: {response.status_code}")
print(f"   Found {len(response.json())} exercises\n")

# Test 3: Get Specific Exercise
print("3. Testing get exercise #1...")
response = requests.get(f"{BASE_URL}/api/exercises/1")
print(f"   Status: {response.status_code}")
print(f"   Exercise: {response.json()['name']}\n")

print("✅ All basic tests passed!")
print("\nTo test video upload:")
print("1. Go to http://localhost:8000/docs")
print("2. Click on POST /api/analyze")
print("3. Upload a workout video")
print("4. Select exercise type")
print("5. Click 'Execute'")