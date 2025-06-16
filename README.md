# Feedback Analyzer

A FastAPI-based service for analyzing customer feedback using sentiment analysis and topic modeling.

## 📘 README Instructions

### 1. Setup & Usage

#### Prerequisites
- Python 3.8+
- MongoDB
- SMTP server (for notifications)

#### Installation
```bash
# Clone the repository
git clone <repository-url>
cd feedback-analyzer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Environment Setup
```bash
# MongoDB Configuration
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DB=feedback_analyzer

# JWT Configuration
export JWT_SECRET_KEY=your-secret-key
export JWT_ALGORITHM=HS256
export ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP Configuration
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export SUPPORT_EMAIL=support@feedback.com
```

#### Running the Application
```bash
# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_feedback_service.py

# Run with coverage
pytest --cov=feedback_analyzer
```

### 2. Assumptions Made

#### Customer Data
1. **Phone Numbers**
   - Assumed to be in international format
   - Minimum length of 10 digits
   - No specific country code validation

2. **Email Addresses**
   - Must be unique per user
   - Valid email format required
   - No domain-specific validation

3. **Customer Names**
   - Minimum length of 2 characters
   - Maximum length of 100 characters
   - No special character restrictions

#### Feedback Analysis
1. **Sentiment Analysis**
   - Three categories: positive, negative, neutral
   - Binary classification for negative vs. non-negative
   - Confidence scores for each sentiment

2. **Topic Classification**
   - Five predefined topics:
     - Product Quality
     - Customer Service
     - Delivery
     - Pricing
     - Usability
   - Single main topic per feedback
   - Multiple topics possible with confidence scores

3. **Notification System**
   - Immediate notification for negative feedback
   - Single support email recipient
   - No retry mechanism for failed notifications

#### System Behavior
1. **Authentication**
   - JWT tokens expire after 30 minutes
   - No refresh token mechanism
   - No password reset functionality

2. **Data Storage**
   - MongoDB for all data persistence
   - No data archival strategy
   - No data backup mechanism

3. **Error Handling**
   - Graceful degradation for external service failures
   - No automatic retry for failed operations
   - Basic error logging

### 3. Technical Decisions Log

#### 1. Framework Choice: FastAPI
**Chosen**: FastAPI
**Why**:
- Native async support
- Automatic API documentation
- Type hints and validation
- High performance
- Easy to test

**Alternatives Considered**:
- Django: Too heavy for this use case
- Flask: Lacks native async support
- Express.js: Python ecosystem better for ML tasks

#### 2. Database: MongoDB
**Chosen**: MongoDB
**Why**:
- Schema flexibility for feedback data
- Good performance for read/write operations
- Easy to scale
- Native JSON support

**Alternatives Considered**:
- PostgreSQL: Too rigid schema for feedback data
- Redis: Not suitable for long-term storage
- MySQL: Less flexible for unstructured data

#### 3. Authentication: JWT
**Chosen**: JWT (JSON Web Tokens)
**Why**:
- Stateless authentication
- Easy to implement
- Widely supported
- Good for microservices

**Alternatives Considered**:
- Session-based: Requires server-side storage
- OAuth2: Overkill for this use case
- API Keys: Less secure

#### 4. ML Libraries
**Chosen**: Hugging Face Transformers
**Why**:
- State-of-the-art models
- Easy to use
- Good documentation
- Active community

**Alternatives Considered**:
- NLTK: Less accurate
- spaCy: More complex setup
- Custom implementation: Too time-consuming

#### 5. Notification System
**Chosen**: SMTP Email
**Why**:
- Simple to implement
- Widely supported
- No additional infrastructure needed
- Easy to test

**Alternatives Considered**:
- Webhooks: More complex to implement
- Message queues: Overkill for this use case
- Push notifications: Requires mobile app

#### 6. API Design
**Chosen**: RESTful with JSON
**Why**:
- Simple to understand
- Widely adopted
- Easy to test
- Good tooling support

**Alternatives Considered**:
- GraphQL: Overkill for this use case
- gRPC: More complex to implement
- SOAP: Too verbose

#### 7. Testing Framework
**Chosen**: Pytest
**Why**:
- Simple syntax
- Good fixture system
- Great for async testing
- Extensive plugin ecosystem

**Alternatives Considered**:
- Unittest: More verbose
- Nose: Less maintained
- Robot Framework: Overkill for this use case

## Features

### User Authentication
- Secure signup with email validation and password requirements
- JWT-based login system with token expiration (30 minutes)
- Protected routes with proper authentication

### Feedback Analysis
- Public feedback submission endpoint
- Protected endpoints for viewing and analyzing feedback
- Filtering by sentiment and topic
- Statistics endpoint
- Individual feedback retrieval
- Automatic email notifications for negative feedback

### Security
- JWT-based authentication
- Password hashing
- Protected routes
- Token expiration (30 minutes)

#### Notifications
- Automatic email alerts for negative feedback
- Configurable SMTP settings
- Detailed feedback information in notifications

## API Documentation

### User Authentication

#### Signup (Public)
```bash
curl -X POST "http://localhost:8000/users/signup" \
-H "Content-Type: application/json" \
-d '{
    "email": "new.user@example.com",
    "full_name": "New User",
    "phone": "+1234567890",
    "password": "TestPass123"
}'
```

Password Requirements:
- Minimum 8 characters
- Must contain uppercase letter
- Must contain lowercase letter
- Must contain number

#### Login (Public)
```bash
curl -X POST "http://localhost:8000/users/login" \
-H "Content-Type: application/json" \
-d '{
    "email": "test1.user@example.com",
    "password": "TestPass123"
}'
```

Response:
```json
{
    "user": {
        "id": "...",
        "email": "...",
        "full_name": "...",
        "phone": "...",
        "created_at": "..."
    },
    "access_token": "...",
    "token_type": "bearer"
}
```

### Feedback Operations

#### Submit and Analyze Feedback (Public)
```bash
curl -X POST "http://localhost:8000/feedback/submit-and-analyze-feedback" \
-H "Content-Type: application/json" \
-d '{
    "feedback_text": "The product quality is excellent and delivery was fast!",
    "customer": {
        "name": "John Doe",
        "phone": "+1234567890"
    }
}'
```

Note: If the feedback sentiment is negative, an automatic email notification will be sent to the support team.

Response:
```json
{
    "id": "...",
    "text": "...",
    "customer": {
        "name": "...",
        "phone": "..."
    },
    "sentiment": "...",
    "sentiment_scores": {...},
    "main_topic": "...",
    "topic_scores": {...},
    "top_topics": [...],
    "created_at": "..."
}
```

#### List All Feedback (Protected)
```bash
curl -X GET "http://localhost:8000/feedback?skip=0&limit=10" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### List Feedback with Filters (Protected)
```bash
# Filter by sentiment
curl -X GET "http://localhost:8000/feedback?sentiment=positive&skip=0&limit=10" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by topic
curl -X GET "http://localhost:8000/feedback?topic=product_quality&skip=0&limit=10" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by both
curl -X GET "http://localhost:8000/feedback?sentiment=positive&topic=product_quality&skip=0&limit=10" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Valid Values:
- Sentiment: "positive", "negative", "neutral"
- Topics: "product_quality", "customer_service", "delivery", "pricing", "usability"

#### Get Feedback Statistics (Protected)
```bash
curl -X GET "http://localhost:8000/feedback/stats" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
    "total_feedback": 0,
    "sentiment_distribution": {
        "positive": 0,
        "negative": 0,
        "neutral": 0
    },
    "topic_distribution": {
        "product_quality": 0,
        "customer_service": 0,
        "delivery": 0,
        "pricing": 0,
        "usability": 0
    }
}
```

#### Get Feedback by ID (Protected)
```bash
curl -X GET "http://localhost:8000/feedback/{feedback_id}" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request (validation errors, duplicate email)
- 401: Unauthorized (invalid or expired token)
- 500: Internal Server Error

## Security Notes

1. Access tokens expire after 30 minutes
2. All endpoints except feedback submission require authentication
3. Passwords are hashed before storage
4. Email addresses must be unique
5. Phone numbers are validated for format

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MongoDB connection:
Create a `.env` file with your MongoDB connection string:
```
MONGODB_URL=your_mongodb_connection_string
```

3. Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### Endpoints

1. `POST /analyze-feedback` - Analyze feedback sentiment and topics
2. `GET /feedback/{feedback_id}` - Get feedback by ID
3. `GET /feedback` - List feedback with optional filtering
4. `GET /feedback/stats` - Get feedback statistics
5. `GET /` - API information

## Test Scenarios

### 1. Submit Different Types of Feedback

```bash
# Positive Product Quality Feedback
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "The product quality is excellent! The materials are top-notch and the design is beautiful.",
           "customer_id": "CUST001"
         }'

# Negative Customer Service Feedback
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Terrible customer service experience. The staff was rude and unhelpful.",
           "customer_id": "CUST002"
         }'

# Mixed Delivery Feedback
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "The delivery was fast but the product arrived damaged. The packaging needs improvement.",
           "customer_id": "CUST003"
         }'

# Neutral Pricing Feedback
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "The price is reasonable for the features offered. Nothing special but not overpriced either.",
           "customer_id": "CUST004"
         }'

# Usability Feedback
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "The interface is easy to use but could use some improvements in the navigation.",
           "customer_id": "CUST005"
         }'
```

### 2. List and Filter Feedback

```bash
# Get all feedback
curl "http://localhost:8000/feedback"

# Get feedback with pagination
curl "http://localhost:8000/feedback?skip=0&limit=2"

# Filter by sentiment
curl "http://localhost:8000/feedback?sentiment=positive"
curl "http://localhost:8000/feedback?sentiment=negative"
curl "http://localhost:8000/feedback?sentiment=neutral"

# Filter by topic
curl "http://localhost:8000/feedback?topic=product_quality"
curl "http://localhost:8000/feedback?topic=customer_service"
curl "http://localhost:8000/feedback?topic=delivery"
curl "http://localhost:8000/feedback?topic=pricing"
curl "http://localhost:8000/feedback?topic=usability"
```

### 3. Get Feedback Statistics

```bash
# Get overall statistics
curl "http://localhost:8000/feedback/stats"
```

### 4. Get Specific Feedback by ID

```bash
# Replace {feedback_id} with an actual ID from the POST response
curl "http://localhost:8000/feedback/{feedback_id}"
```

### 5. Test Edge Cases

```bash
# Empty text
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "",
           "customer_id": "CUST006"
         }'

# Very long text
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "This is a very long feedback that contains multiple topics and sentiments. The product quality is excellent, but the customer service was terrible. The delivery was fast, but the pricing seems a bit high. The interface is easy to use but could use some improvements. Overall, it is a mixed experience with both positive and negative aspects.",
           "customer_id": "CUST007"
         }'

# Special characters
curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Product quality: 5/5 ⭐⭐⭐⭐⭐, but customer service: 1/5 ⭐",
           "customer_id": "CUST008"
         }'
```

### 6. Test Invalid Scenarios

```bash
# Invalid feedback ID
curl "http://localhost:8000/feedback/invalid_id"

# Invalid sentiment filter
curl "http://localhost:8000/feedback?sentiment=invalid"

# Invalid topic filter
curl "http://localhost:8000/feedback?topic=invalid"

# Invalid pagination
curl "http://localhost:8000/feedback?skip=-1&limit=0"
```

### 7. Get API Information

```bash
# Get API documentation
curl "http://localhost:8000/"
```

## Complete Test Flow

To test the complete flow, you can run these commands in sequence:

```bash
# 1. Submit feedback and save the ID
RESPONSE=$(curl -X POST "http://localhost:8000/analyze-feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "The product quality is excellent!",
           "customer_id": "CUST001"
         }')

# 2. Extract the ID from the response
FEEDBACK_ID=$(echo $RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

# 3. Get the specific feedback
curl "http://localhost:8000/feedback/$FEEDBACK_ID"

# 4. Get all feedback
curl "http://localhost:8000/feedback"

# 5. Get statistics
curl "http://localhost:8000/feedback/stats"
```

## Response Formats

### POST /analyze-feedback Response
```json
{
    "id": "feedback_id",
    "text": "feedback text",
    "customer_id": "customer_id",
    "sentiment": "positive|negative|neutral",
    "sentiment_scores": {
        "positive": 0.8,
        "negative": 0.2
    },
    "main_topic": "topic_name",
    "topic_scores": {
        "product_quality": 0.6,
        "customer_service": 0.2,
        "delivery": 0.1,
        "pricing": 0.05,
        "usability": 0.05
    },
    "top_topics": ["topic1", "topic2"],
    "created_at": "timestamp"
}
```

### GET /feedback/stats Response
```json
{
    "total_feedback": 10,
    "sentiment_distribution": {
        "positive": 5,
        "negative": 3,
        "neutral": 2
    },
    "topic_distribution": {
        "product_quality": 4,
        "customer_service": 2,
        "delivery": 2,
        "pricing": 1,
        "usability": 1
    }
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses include a detail message explaining the error:
```json
{
    "detail": "Error message"
}
```

## API Test Examples

Here are some example curl commands to test the API endpoints:

### 1. Submit Feedback (Public)
```bash
curl -X POST "http://localhost:8000/feedback/submit-and-analyze-feedback" \
-H "Content-Type: application/json" \
-d '{
    "feedback_text": "The product quality is excellent but delivery was slow",
    "customer": {
        "name": "John Doe",
        "phone": "+1234567890"
    }
}'
```

### 2. List All Feedback (Protected)
```bash
curl -X GET "http://localhost:8000/feedback?skip=0&limit=10" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODRmMWU0NDlkMzRiYzQ4NGY4MDRlZWMiLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJOZXcgVXNlciIsImV4cCI6MTc1MDAxNzQwM30.iZT2qY3QF889JY-3yGluwK2OqPs64cexc3vBdBpH6u0"
```

### 3. List Feedback with Filters (Protected)
```bash
# Filter by sentiment
curl -X GET "http://localhost:8000/feedback?sentiment=positive" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODRmMWU0NDlkMzRiYzQ4NGY4MDRlZWMiLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJOZXcgVXNlciIsImV4cCI6MTc1MDAxNzQwM30.iZT2qY3QF889JY-3yGluwK2OqPs64cexc3vBdBpH6u0"

# Filter by topic
curl -X GET "http://localhost:8000/feedback?topic=product_quality" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODRmMWU0NDlkMzRiYzQ4NGY4MDRlZWMiLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJOZXcgVXNlciIsImV4cCI6MTc1MDAxNzQwM30.iZT2qY3QF889JY-3yGluwK2OqPs64cexc3vBdBpH6u0"

# Filter by both sentiment and topic
curl -X GET "http://localhost:8000/feedback?sentiment=positive&topic=product_quality" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODRmMWU0NDlkMzRiYzQ4NGY4MDRlZWMiLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJOZXcgVXNlciIsImV4cCI6MTc1MDAxNzQwM30.iZT2qY3QF889JY-3yGluwK2OqPs64cexc3vBdBpH6u0"

# Pagination
curl -X GET "http://localhost:8000/feedback?skip=0&limit=10" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODRmMWU0NDlkMzRiYzQ4NGY4MDRlZWMiLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJOZXcgVXNlciIsImV4cCI6MTc1MDAxNzQwM30.iZT2qY3QF889JY-3yGluwK2OqPs64cexc3vBdBpH6u0"
```

### 4. Get Feedback Statistics (Protected)
```bash
curl -X GET "http://localhost:8000/feedback/stats" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODRmMWU0NDlkMzRiYzQ4NGY4MDRlZWMiLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJOZXcgVXNlciIsImV4cCI6MTc1MDAxNzQwM30.iZT2qY3QF889JY-3yGluwK2OqPs64cexc3vBdBpH6u0"
```

### 5. Get Feedback by ID (Protected)
```bash
# Replace {feedback_id} with an actual feedback ID from your database
curl -X GET "http://localhost:8000/feedback/{feedback_id}" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODRmMWU0NDlkMzRiYzQ4NGY4MDRlZWMiLCJlbWFpbCI6Im5ld3VzZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJOZXcgVXNlciIsImV4cCI6MTc1MDAxNzQwM30.iZT2qY3QF889JY-3yGluwK2OqPs64cexc3vBdBpH6u0"
```

### Expected Response Formats

#### 1. Submit Feedback Response
```json
{
    "id": "feedback_id",
    "text": "The product quality is excellent but delivery was slow",
    "customer": {
        "name": "John Doe",
        "phone": "+1234567890"
    },
    "sentiment": "positive",
    "sentiment_scores": {
        "positive": 0.8,
        "negative": 0.1,
        "neutral": 0.1
    },
    "main_topic": "product_quality",
    "topic_scores": {
        "product_quality": 0.7,
        "delivery": 0.3
    },
    "top_topics": ["product_quality", "delivery"],
    "created_at": "2024-03-14T12:00:00Z"
}
```

#### 2. List Feedback Response
```json
[
    {
        "id": "feedback_id",
        "text": "The product quality is excellent but delivery was slow",
        "customer": {
            "name": "John Doe",
            "phone": "+1234567890"
        },
        "sentiment": "positive",
        "sentiment_scores": {
            "positive": 0.8,
            "negative": 0.1,
            "neutral": 0.1
        },
        "main_topic": "product_quality",
        "topic_scores": {
            "product_quality": 0.7,
            "delivery": 0.3
        },
        "top_topics": ["product_quality", "delivery"],
        "created_at": "2024-03-14T12:00:00Z"
    }
]
```

#### 3. Stats Response
```json
{
    "total_feedback": 100,
    "sentiment_distribution": {
        "positive": 60,
        "negative": 20,
        "neutral": 20
    },
    "topic_distribution": {
        "product_quality": 30,
        "customer_service": 25,
        "delivery": 20,
        "pricing": 15,
        "usability": 10
    }
}
```

### Important Notes
1. The access token expires after 30 minutes, so you'll need to login again if it expires
2. Replace `{feedback_id}` with an actual feedback ID from your database
3. Valid sentiment values are: "positive", "negative", "neutral"
4. Valid topic values are: "product_quality", "customer_service", "delivery", "pricing", "usability"
5. The feedback submission endpoint is public and doesn't require authentication
6. All other endpoints require authentication via the Authorization header 

## Environment Variables

The following environment variables can be configured:

```bash
# SMTP Configuration for Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SUPPORT_EMAIL=support@feedback.com
```

## Testing the Notification Feature

### 1. Setup SMTP Configuration

First, set up your SMTP configuration in your environment:

```bash
# For Gmail (recommended for testing)
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your-gmail@gmail.com
export SMTP_PASSWORD=your-app-password  # Use App Password, not your regular password
export SUPPORT_EMAIL=support@feedback.com

# For testing with Mailtrap (alternative)
export SMTP_SERVER=sandbox.smtp.mailtrap.io
export SMTP_PORT=2525
export SMTP_USERNAME=your-mailtrap-username
export SMTP_PASSWORD=your-mailtrap-password
export SUPPORT_EMAIL=support@feedback.com
```

Note: For Gmail, you need to:
1. Enable 2-factor authentication
2. Generate an App Password (Google Account → Security → App Passwords)
3. Use the App Password instead of your regular password

### 2. Test Negative Feedback

Send a feedback with negative sentiment:

```bash
curl -X POST "http://localhost:8000/feedback/submit-and-analyze-feedback" \
-H "Content-Type: application/json" \
-d '{
    "feedback_text": "I am very disappointed with the product quality. The delivery was late and the customer service was terrible. This is the worst experience I have ever had.",
    "customer": {
        "name": "Test Customer",
        "phone": "+1234567890"
    }
}'
```

Expected Results:
1. You should receive a 200 OK response with the feedback analysis
2. Check your email (or Mailtrap inbox) for a notification with:
   - Subject: "⚠️ Negative Feedback Alert"
   - Feedback details including ID, customer info, and sentiment score
   - The full feedback text

### 3. Test Positive Feedback (No Notification)

Send a feedback with positive sentiment to verify notifications are only sent for negative feedback:

```bash
curl -X POST "http://localhost:8000/feedback/submit-and-analyze-feedback" \
-H "Content-Type: application/json" \
-d '{
    "feedback_text": "I am very happy with the product quality. The delivery was fast and the customer service was excellent. This is the best experience I have ever had.",
    "customer": {
        "name": "Test Customer",
        "phone": "+1234567890"
    }
}'
```

Expected Results:
1. You should receive a 200 OK response with the feedback analysis
2. No email notification should be sent

### 4. Verify Notification Content

The notification email should contain:
```
Subject: ⚠️ Negative Feedback Alert

Negative feedback received that requires attention:

Feedback ID: [feedback_id]
Customer: [customer_name]
Phone: [customer_phone]
Sentiment Score: [negative_score]
Main Topic: [main_topic]

Feedback Text:
[full_feedback_text]

Please review and respond promptly.
```

### 5. Troubleshooting

If you don't receive notifications:

1. Check the application logs for any SMTP errors
2. Verify your SMTP configuration:
   ```bash
   # Test SMTP connection
   python3 -c "
   import smtplib
   server = smtplib.SMTP('$SMTP_SERVER', $SMTP_PORT)
   server.starttls()
   server.login('$SMTP_USERNAME', '$SMTP_PASSWORD')
   server.quit()
   print('SMTP connection successful!')
   "
   ```
3. For Gmail:
   - Ensure 2-factor authentication is enabled
   - Verify you're using an App Password
   - Check if your account has any security restrictions
4. For Mailtrap:
   - Verify your credentials in the Mailtrap dashboard
   - Check if your inbox is not full

### 6. Testing with Different Sentiment Levels

Test with various feedback texts to ensure proper sentiment detection:

```bash
# Strongly Negative
curl -X POST "http://localhost:8000/feedback/submit-and-analyze-feedback" \
-H "Content-Type: application/json" \
-d '{
    "feedback_text": "This is absolutely terrible. I want a refund immediately. The worst service ever.",
    "customer": {
        "name": "Angry Customer",
        "phone": "+1234567890"
    }
}'

# Mildly Negative
curl -X POST "http://localhost:8000/feedback/submit-and-analyze-feedback" \
-H "Content-Type: application/json" \
-d '{
    "feedback_text": "The product was okay but could be better. Delivery was a bit slow.",
    "customer": {
        "name": "Neutral Customer",
        "phone": "+1234567890"
    }
}'

# Neutral
curl -X POST "http://localhost:8000/feedback/submit-and-analyze-feedback" \
-H "Content-Type: application/json" \
-d '{
    "feedback_text": "The product arrived on time. It works as expected.",
    "customer": {
        "name": "Neutral Customer",
        "phone": "+1234567890"
    }
}'
```

Remember to check your email (or Mailtrap inbox) after each test to verify that notifications are only sent for negative feedback. 

## Production Readiness

### 1. Priority Improvements

#### Security Enhancements
1. **Authentication & Authorization**
   - Implement refresh token mechanism
   - Add rate limiting for API endpoints
   - Implement IP-based blocking for suspicious activities
   - Add password reset functionality
   - Implement MFA for admin users

2. **Data Protection**
   - Encrypt sensitive data at rest
   - Implement data masking for PII
   - Add data retention policies
   - Implement secure audit logging
   - Regular security audits

3. **API Security**
   - Add API key management
   - Implement request signing
   - Add CORS policies
   - Implement API versioning
   - Add request validation middleware

#### Performance Optimizations
1. **Database**
   - Implement database sharding
   - Add read replicas
   - Optimize indexes
   - Implement caching layer
   - Add database connection pooling

2. **Application**
   - Implement request queuing
   - Add response caching
   - Optimize ML model loading
   - Implement batch processing
   - Add request compression

3. **ML Pipeline**
   - Implement model versioning
   - Add model performance monitoring
   - Implement A/B testing capability
   - Add model retraining pipeline
   - Implement model fallback mechanisms

### 2. Scaling Strategy

#### Horizontal Scaling
1. **Application Layer**
   - Containerize application (Docker)
   - Implement Kubernetes orchestration
   - Add load balancing
   - Implement auto-scaling
   - Use CDN for static content

2. **Database Layer**
   - Implement MongoDB sharding
   - Add read replicas
   - Implement database clustering
   - Add connection pooling
   - Implement data partitioning

3. **ML Services**
   - Separate ML services into microservices
   - Implement model serving infrastructure
   - Add model caching
   - Implement batch processing
   - Add model versioning

#### Vertical Scaling
1. **Resource Optimization**
   - Optimize memory usage
   - Implement connection pooling
   - Add request queuing
   - Optimize database queries
   - Implement caching strategies

2. **Infrastructure**
   - Use high-performance instances
   - Implement SSD storage
   - Add dedicated ML hardware
   - Optimize network configuration
   - Implement resource limits

### 3. Security Measures

#### Infrastructure Security
1. **Network Security**
   - Implement VPC
   - Add WAF
   - Configure security groups
   - Implement DDoS protection
   - Add network monitoring

2. **Application Security**
   - Regular security audits
   - Implement SAST/DAST
   - Add dependency scanning
   - Implement secrets management
   - Add security headers

3. **Data Security**
   - Implement encryption at rest
   - Add encryption in transit
   - Implement data masking
   - Add access controls
   - Implement audit logging

### 4. Monitoring & Observability

#### Application Monitoring
1. **Metrics**
   - Response times
   - Error rates
   - Request volumes
   - Resource usage
   - API latency

2. **Logging**
   - Structured logging
   - Log aggregation
   - Log retention policies
   - Error tracking
   - Audit logging

3. **Tracing**
   - Request tracing
   - Performance profiling
   - Dependency tracking
   - Error tracking
   - User journey tracking

#### Business Metrics
1. **Feedback Analysis**
   - Sentiment trends
   - Topic distribution
   - Response times
   - Customer satisfaction
   - Issue resolution time

2. **System Health**
   - Uptime monitoring
   - Performance metrics
   - Resource utilization
   - Error rates
   - API availability

3. **Security Metrics**
   - Failed login attempts
   - API usage patterns
   - Security incidents
   - Access patterns
   - Compliance status

### 5. Disaster Recovery

#### Backup Strategy
1. **Data Backup**
   - Regular database backups
   - Configuration backups
   - Log backups
   - ML model backups
   - User data backups

2. **Recovery Procedures**
   - Disaster recovery plan
   - Backup restoration
   - Service recovery
   - Data recovery
   - Incident response

3. **High Availability**
   - Multi-region deployment
   - Failover mechanisms
   - Load balancing
   - Data replication
   - Service redundancy

### 6. Compliance & Governance

#### Data Compliance
1. **Data Protection**
   - GDPR compliance
   - Data retention policies
   - Privacy controls
   - Data access controls
   - Audit trails

2. **Security Compliance**
   - Security standards
   - Regular audits
   - Compliance reporting
   - Policy enforcement
   - Risk management

3. **Operational Compliance**
   - SLA monitoring
   - Performance standards
   - Quality metrics
   - Service levels
   - Operational procedures

## Project Analysis & Future Directions

### Trade-offs Made

1. **Architecture Decisions**
   - Chose monolithic architecture over microservices for faster initial development
   - Used MongoDB for flexibility in schema evolution vs. strict relational database
   - Implemented synchronous ML processing vs. async queue for simplicity
   - Used in-memory ML model loading vs. model serving infrastructure

2. **Technical Trade-offs**
   - Simplicity vs. Scalability: Started with a simpler architecture that can be scaled later
   - Development Speed vs. Performance: Prioritized rapid development over premature optimization
   - Flexibility vs. Security: Implemented basic security with room for enhancement
   - Real-time vs. Batch Processing: Chose real-time analysis over batch processing

3. **Feature Trade-offs**
   - Basic notification system vs. comprehensive alerting
   - Simple authentication vs. complex auth system
   - Basic monitoring vs. comprehensive observability
   - Single-region deployment vs. multi-region setup

### Business Goals Achievement

1. **Core Objectives**
   - ✅ Real-time feedback analysis
   - ✅ Automated sentiment detection
   - ✅ Topic classification
   - ✅ Negative feedback alerts
   - ✅ Basic analytics dashboard

2. **Customer Value**
   - Quick response to negative feedback
   - Actionable insights from feedback analysis
   - Easy-to-use API interface
   - Scalable solution for growing needs

3. **Operational Goals**
   - Automated feedback processing
   - Reduced manual review time
   - Improved response time to issues
   - Data-driven decision making

### Future Improvements (Given More Time)

1. **Immediate Priorities**
   - Implement comprehensive error handling
   - Add automated testing suite
   - Enhance security measures
   - Improve documentation
   - Add performance monitoring

2. **Feature Enhancements**
   - Advanced analytics dashboard
   - Custom notification rules
   - Feedback trend analysis
   - Automated response suggestions
   - Integration with CRM systems

3. **Technical Improvements**
   - Implement caching layer
   - Add database indexing
   - Optimize ML model performance
   - Implement rate limiting
   - Add request validation

4. **Business Enhancements**
   - Custom reporting
   - User role management
   - API usage analytics
   - SLA monitoring
   - Cost optimization

5. **Long-term Vision**
   - Machine learning model improvements
   - Advanced natural language processing
   - Predictive analytics
   - Automated workflow integration
   - Multi-language support 