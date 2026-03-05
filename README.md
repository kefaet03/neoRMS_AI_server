# RMS AI Modules API Server

Production-ready FastAPI server for the Restaurant Management System AI modules.

## 📁 Project Structure

```
api_server/
├── app/
│   ├── __init__.py
│   ├── config.py           # Application settings
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py        # Health check endpoint
│   │   ├── recommendation.py # Food recommendations
│   │   ├── review.py        # Review analysis
│   │   └── sentiment.py     # Sentiment analysis
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py          # Base response schemas
│   │   ├── recommendation.py
│   │   ├── review.py
│   │   └── sentiment.py
│   └── services/
│       ├── __init__.py
│       ├── recommendation_service.py
│       ├── review_service.py
│       └── sentiment_service.py
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── run.py                   # Server entry point
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Create Virtual Environment

```powershell
cd api_server
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

```powershell
copy .env.example .env
# Edit .env if needed
```

### 4. Run the Server

```powershell
python run.py
```

Or using uvicorn directly:

```powershell
uvicorn app.main:app --reload --port 8000
```

### 5. Access the API

- **API Documentation (Swagger):** http://localhost:8888/docs
- **ReDoc Documentation:** http://localhost:8888/redoc
- **Health Check:** http://localhost:8888/health

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/recommend` | Get food recommendations |
| POST | `/analyze-review` | Analyze reviews for complaints |
| POST | `/sentiment` | Sentiment analysis |

### Response Format

All endpoints return responses in this structure:

```json
{
    "success": true,
    "data": { ... },
    "message": "optional message"
}
```

---

## 🧪 Testing the Endpoints

### Health Check

```powershell
curl http://localhost:8888/health
```

**Expected Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "recommendation_engine": "ready",
            "review_analyzer": "ready",
            "sentiment_analyzer": "ready"
        }
    },
    "message": "Service is operational"
}
```

---

### 1. Recommendation Endpoint

**Request:**
```powershell
curl -X POST http://localhost:8888/recommend `
  -H "Content-Type: application/json" `
  -d '{"already_ordered": ["Kacchi Biryani", "Borhani"], "num_recommendations": 3}'
```

**Or using Invoke-RestMethod (PowerShell):**
```powershell
$body = @{
    already_ordered = @("Kacchi Biryani", "Borhani")
    num_recommendations = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8888/recommend" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
    "success": true,
    "data": {
        "recommendations": ["Chicken Roast", "Beef Kala Bhuna", "Tandoori Roti"],
        "based_on": ["Kacchi Biryani", "Borhani"]
    },
    "message": "Successfully generated 3 recommendations"
}
```

---

### 2. Review Analysis Endpoint

**Request:**
```powershell
curl -X POST http://localhost:8888/analyze-review `
  -H "Content-Type: application/json" `
  -d '{"reviews": ["The burger was cold and tasteless", "Biryani ta oshadharon chilo!", "Delivery took 2 hours and food was stale"]}'
```

**Or using Invoke-RestMethod (PowerShell):**
```powershell
$body = @{
    reviews = @(
        "The burger was cold and tasteless",
        "Biryani ta oshadharon chilo!",
        "Delivery took 2 hours and food was stale"
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8888/analyze-review" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
    "success": true,
    "data": {
        "total_reviews": 3,
        "kept_reviews": 3,
        "ignored_reviews": 0,
        "total_complaints": 3,
        "complaints": [
            {"item": "burger", "issue": "cold", "category": "temperature"},
            {"item": "burger", "issue": "tasteless", "category": "taste"},
            {"item": "food", "issue": "stale", "category": "taste"}
        ],
        "complaints_grouped": {
            "burger": {
                "cold": {"count": 1, "category": "temperature"},
                "tasteless": {"count": 1, "category": "taste"}
            },
            "food": {
                "stale": {"count": 1, "category": "taste"}
            }
        }
    },
    "message": "Analyzed 3 reviews, extracted 3 complaints"
}
```

---

### 3. Sentiment Analysis Endpoint

**Request:**
```powershell
curl -X POST http://localhost:8888/sentiment `
  -H "Content-Type: application/json" `
  -d '{"text": "The food was amazing and the service was excellent!"}'
```

**Or using Invoke-RestMethod (PowerShell):**
```powershell
$body = @{
    text = "The food was amazing and the service was excellent!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8888/sentiment" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
    "success": true,
    "data": {
        "text": "The food was amazing and the service was excellent!",
        "sentiment_label": 2,
        "sentiment_name": "Positive",
        "confidence": 0.75,
        "scores": {
            "negative": 0.1,
            "neutral": 0.15,
            "positive": 0.75
        }
    },
    "message": "Sentiment: Positive"
}
```

---

## 🧪 Comprehensive Test Script

Save this as `test_api.py` and run it to test all endpoints:

```python
"""
Test script for RMS AI Modules API.
Run: python test_api.py
"""

import httpx
import json

BASE_URL = "http://localhost:8888"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*50)
    print("TEST: Health Check")
    print("="*50)
    
    response = httpx.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    print("✓ PASSED")

def test_recommend():
    """Test recommendation endpoint."""
    print("\n" + "="*50)
    print("TEST: Food Recommendations")
    print("="*50)
    
    payload = {
        "already_ordered": ["Kacchi Biryani", "Borhani"],
        "num_recommendations": 3
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/recommend", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert len(response.json()["data"]["recommendations"]) > 0
    print("✓ PASSED")

def test_review_analysis():
    """Test review analysis endpoint."""
    print("\n" + "="*50)
    print("TEST: Review Analysis")
    print("="*50)
    
    payload = {
        "reviews": [
            "The burger was cold and tasteless",
            "Biryani ta oshadharon chilo!",
            "Delivery took 2 hours and the food was stale",
            "The waiter was very rude"
        ]
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = httpx.post(f"{BASE_URL}/analyze-review", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    print("✓ PASSED")

def test_sentiment():
    """Test sentiment analysis endpoint."""
    print("\n" + "="*50)
    print("TEST: Sentiment Analysis")
    print("="*50)
    
    test_cases = [
        ("The food was amazing and delicious!", "Positive"),
        ("It was okay, nothing special", "Neutral"),
        ("Terrible food, worst experience ever!", "Negative"),
    ]
    
    for text, expected in test_cases:
        payload = {"text": text}
        print(f"\nInput: '{text}'")
        
        response = httpx.post(f"{BASE_URL}/sentiment", json=payload)
        result = response.json()
        
        print(f"Predicted: {result['data']['sentiment_name']}")
        print(f"Confidence: {result['data']['confidence']:.2%}")
        
        assert response.status_code == 200
        assert result["success"] == True
    
    print("\n✓ PASSED")

def main():
    print("\n" + "#"*50)
    print("# RMS AI MODULES API - TEST SUITE")
    print("#"*50)
    
    try:
        test_health()
        test_recommend()
        test_review_analysis()
        test_sentiment()
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✓")
        print("="*50 + "\n")
        
    except httpx.ConnectError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the server is running at", BASE_URL)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
```

Run the test:
```powershell
python test_api.py
```

---

## 📊 Model Information

### 1. Recommendation Engine (AM1)
- **Algorithm:** Conditional Probability
- **P(item_j | item_i)**: Probability of ordering item_j given item_i was ordered
- **Data:** Sample order history (can be replaced with database)

### 2. Review Analyzer (AM4)
- **LLM:** Google Gemini (with API key) or keyword-based mock
- **Pre-filter:** Skips reviews < 10 characters
- **Categories:** temperature, taste, quality, cooking, service, hygiene, other

### 3. Sentiment Analyzer (AM42)
- **Model:** Logistic Regression
- **Vectorizer:** TF-IDF (max_features=5000)
- **Classes:** Negative (0), Neutral (1), Positive (2)
- **Model Path:** `../AM42/saved_models/logistic_regression.pkl`

---

## ⚙️ Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | RMS AI Modules API | Application name |
| `APP_VERSION` | 1.0.0 | API version |
| `DEBUG` | false | Enable debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `CORS_ORIGINS` | ["*"] | Allowed CORS origins |
| `GEMINI_API_KEY` | - | Google Gemini API key (optional) |

---

## 🔧 Development

### Enable Debug Mode

```powershell
$env:DEBUG="true"
python run.py
```

### Run with Auto-reload

```powershell
uvicorn app.main:app --reload --port 8000
```

---

## 📝 Notes

1. **Sentiment Model:** The server looks for the trained model at `../AM42/saved_models/logistic_regression.pkl`. If not found, it uses mock predictions.

2. **Review Analyzer:** Uses keyword-based extraction by default. Set `GEMINI_API_KEY` to use the actual LLM.

3. **Recommendation Engine:** Uses sample order history. In production, integrate with your database.

---

## 📄 License

Internal use only - CSE 4100 Project
