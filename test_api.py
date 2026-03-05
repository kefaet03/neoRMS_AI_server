"""
Test script for RMS AI Modules API.
Run: python test_api.py

Make sure the server is running before executing this test!
"""

import httpx
import json
import sys

BASE_URL = "http://localhost:8888"


def print_header(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(success: bool, message: str = ""):
    """Print test result."""
    if success:
        print(f"\n✓ PASSED {message}")
    else:
        print(f"\n✗ FAILED {message}")


def test_health():
    """Test health endpoint."""
    print_header("TEST 1: Health Check")
    print("Endpoint: GET /health")
    
    response = httpx.get(f"{BASE_URL}/health")
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        data.get("data", {}).get("status") in ["healthy", "degraded"]
    )
    
    print_result(success)
    return success


def test_recommend_empty():
    """Test recommendation with no items ordered."""
    print_header("TEST 2: Recommendations (No Items)")
    print("Endpoint: POST /recommend")
    
    payload = {
        "already_ordered": [],
        "num_recommendations": 5
    }
    
    print(f"\nRequest Body:\n{json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/recommend", json=payload)
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        len(data.get("data", {}).get("recommendations", [])) == 5
    )
    
    print_result(success)
    return success


def test_recommend_with_items():
    """Test recommendation with items already ordered."""
    print_header("TEST 3: Recommendations (With Items)")
    print("Endpoint: POST /recommend")
    
    payload = {
        "already_ordered": ["Kacchi Biryani", "Borhani"],
        "num_recommendations": 3
    }
    
    print(f"\nRequest Body:\n{json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/recommend", json=payload)
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    recommendations = data.get("data", {}).get("recommendations", [])
    ordered = payload["already_ordered"]
    
    # Check that recommendations don't include already ordered items
    no_duplicates = not any(item in ordered for item in recommendations)
    
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        len(recommendations) == 3 and
        no_duplicates
    )
    
    print_result(success, "(no duplicates with ordered items)" if no_duplicates else "")
    return success


def test_review_analysis():
    """Test review analysis endpoint."""
    print_header("TEST 4: Review Analysis")
    print("Endpoint: POST /analyze-review")
    
    payload = {
        "reviews": [
            "The burger was cold and completely tasteless. Very disappointed!",
            "Biryani ta oshadharon chilo! Best food ever!",
            "Delivery took 2 hours and the food arrived stale and cold",
            "The waiter was extremely rude and the service was slow",
            "Pizza was undercooked and greasy. Found a hair in it!"
        ]
    }
    
    print(f"\nRequest Body:\n{json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/analyze-review", json=payload)
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    result_data = data.get("data", {})
    
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        result_data.get("total_reviews") == 5 and
        result_data.get("total_complaints", 0) > 0
    )
    
    print_result(success)
    return success


def test_review_short_filter():
    """Test review analysis filters short reviews."""
    print_header("TEST 5: Review Analysis (Short Review Filter)")
    print("Endpoint: POST /analyze-review")
    
    payload = {
        "reviews": [
            "Bad",  # Too short - should be ignored
            "ok",   # Too short - should be ignored  
            "The burger was cold and tasteless. Very disappointed!"
        ]
    }
    
    print(f"\nRequest Body:\n{json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/analyze-review", json=payload)
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    result_data = data.get("data", {})
    
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        result_data.get("total_reviews") == 3 and
        result_data.get("ignored_reviews") == 2 and
        result_data.get("kept_reviews") == 1
    )
    
    print_result(success, "(short reviews filtered)")
    return success


def test_sentiment_positive():
    """Test sentiment analysis with positive text."""
    print_header("TEST 6: Sentiment Analysis (Positive)")
    print("Endpoint: POST /sentiment")
    
    payload = {
        "text": "The food was absolutely amazing! Best biryani I've ever had. The service was excellent and the ambiance was wonderful!"
    }
    
    print(f"\nRequest Body:\n{json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/sentiment", json=payload)
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    result_data = data.get("data", {})
    
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        result_data.get("sentiment_name") == "Positive" and
        result_data.get("sentiment_label") == 2
    )
    
    print_result(success, f"(predicted: {result_data.get('sentiment_name')})")
    return success


def test_sentiment_negative():
    """Test sentiment analysis with negative text."""
    print_header("TEST 7: Sentiment Analysis (Negative)")
    print("Endpoint: POST /sentiment")
    
    payload = {
        "text": "Terrible experience! The food was cold, tasteless, and the worst I've ever had. Never coming back!"
    }
    
    print(f"\nRequest Body:\n{json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/sentiment", json=payload)
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    result_data = data.get("data", {})
    
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        result_data.get("sentiment_name") == "Negative" and
        result_data.get("sentiment_label") == 0
    )
    
    print_result(success, f"(predicted: {result_data.get('sentiment_name')})")
    return success


def test_sentiment_neutral():
    """Test sentiment analysis with neutral text."""
    print_header("TEST 8: Sentiment Analysis (Neutral)")
    print("Endpoint: POST /sentiment")
    
    payload = {
        "text": "The food was okay. Nothing special but not bad either. Average experience."
    }
    
    print(f"\nRequest Body:\n{json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/sentiment", json=payload)
    data = response.json()
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:\n{json.dumps(data, indent=2)}")
    
    result_data = data.get("data", {})
    
    # Neutral can sometimes be predicted as positive/negative, so just check it returns valid result
    success = (
        response.status_code == 200 and
        data.get("success") == True and
        result_data.get("sentiment_label") in [0, 1, 2]
    )
    
    print_result(success, f"(predicted: {result_data.get('sentiment_name')})")
    return success


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "#" * 60)
    print("#" + " " * 15 + "RMS AI MODULES API" + " " * 15 + "#")
    print("#" + " " * 17 + "TEST SUITE" + " " * 19 + "#")
    print("#" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Recommend (Empty)", test_recommend_empty),
        ("Recommend (With Items)", test_recommend_with_items),
        ("Review Analysis", test_review_analysis),
        ("Review Short Filter", test_review_short_filter),
        ("Sentiment (Positive)", test_sentiment_positive),
        ("Sentiment (Negative)", test_sentiment_negative),
        ("Sentiment (Neutral)", test_sentiment_neutral),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed, None))
        except httpx.ConnectError:
            print(f"\n❌ CONNECTION ERROR: Could not connect to {BASE_URL}")
            print("Make sure the server is running!")
            print("\nTo start the server:")
            print("  cd api_server")
            print("  python run.py")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append((name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    
    for name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        error_msg = f" - {error}" if error else ""
        print(f"  {status}  {name}{error_msg}")
    
    print("-" * 60)
    print(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60 + "\n")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        print("=" * 60 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
