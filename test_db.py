import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_submit_feedback():
    """Test submitting feedback with customer ID."""
    feedback = {
        "text": "The product quality is excellent and customer service was great!",
        "customer_id": "TEST_CUST_001"
    }
    response = requests.post(f"{BASE_URL}/analyze-feedback", json=feedback)
    print("\n1. Submit Feedback Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()["id"]

def test_get_feedback(feedback_id):
    """Test retrieving feedback by ID."""
    response = requests.get(f"{BASE_URL}/feedback/{feedback_id}")
    print("\n2. Get Feedback Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_list_feedback():
    """Test listing feedback with filters."""
    # Test different filter combinations
    filters = [
        "?sentiment=positive",
        "?topic=product_quality",
        "?sentiment=positive&topic=product_quality",
        "?limit=2&skip=0"
    ]
    
    print("\n3. List Feedback Tests:")
    for filter_query in filters:
        response = requests.get(f"{BASE_URL}/feedback{filter_query}")
        print(f"\nFilter: {filter_query}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_stats():
    """Test getting feedback statistics."""
    response = requests.get(f"{BASE_URL}/feedback/stats")
    print("\n4. Get Stats Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_multiple_submissions():
    """Test submitting multiple feedback entries."""
    feedbacks = [
        {
            "text": "Great product quality!",
            "customer_id": "TEST_CUST_001"
        },
        {
            "text": "Terrible customer service experience.",
            "customer_id": "TEST_CUST_002"
        },
        {
            "text": "The delivery was fast but the product was damaged.",
            "customer_id": "TEST_CUST_003"
        }
    ]
    
    print("\n5. Multiple Submissions Test:")
    for feedback in feedbacks:
        response = requests.post(f"{BASE_URL}/analyze-feedback", json=feedback)
        print(f"\nSubmitted: {feedback['text']}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def run_all_tests():
    """Run all test cases."""
    print("Starting MongoDB Integration Tests...")
    
    # Test 1: Submit feedback
    feedback_id = test_submit_feedback()
    
    # Test 2: Get feedback by ID
    test_get_feedback(feedback_id)
    
    # Test 3: List feedback with filters
    test_list_feedback()
    
    # Test 4: Get statistics
    test_get_stats()
    
    # Test 5: Multiple submissions
    test_multiple_submissions()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_all_tests() 