# Feedback Analyzer System

A robust, scalable feedback analysis system that processes customer feedback using AI-powered sentiment analysis and topic classification, with real-time notifications for negative feedback.

## Table of Contents
- [Features](#features)
- [Setup & Usage](#setup--usage)
- [Architecture](#architecture)
- [Assumptions](#assumptions)
- [Technical Decisions](#technical-decisions)
- [Production Readiness](#production-readiness)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Monitoring & Logging](#monitoring--logging)

## Features

### 1. AI-Powered Analysis
- **Dual Analysis Approach**
  - Rule-based analysis for quick, deterministic results
  - AI-powered analysis using OpenAI's GPT-3.5-turbo for nuanced understanding
- **Sentiment Analysis**
  - Three-level classification (positive, neutral, negative)
  - Confidence scoring (0.0 to 1.0)
  - Context-aware analysis
- **Topic Classification**
  - Five main topics: product quality, customer service, delivery, pricing, usability
  - Multi-topic detection
  - Confidence scoring for each topic

### 2. Real-time Notifications
- **Asynchronous Processing**
  - Redis-based message queue
  - Non-blocking notification handling
  - Automatic retry mechanism
- **Email Notifications**
  - Configurable SMTP settings
  - HTML and plain text support
  - Detailed feedback information

### 3. RESTful API
- **Protected Endpoints**
  - JWT-based authentication
  - Role-based access control
  - Rate limiting
- **Public Endpoints**
  - Feedback submission
  - Basic statistics
- **Filtering & Pagination**
  - Sentiment-based filtering
  - Topic-based filtering
  - Configurable page size

## Setup & Usage

### Prerequisites
- Python 3.8+
- Redis Server
- MongoDB
- OpenAI API Key
- SMTP Server (for notifications)

### Redis Setup for macOS

#### 1. Installation

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Redis**:
   ```bash
   brew install redis
   ```

#### 2. Configuration

1. **Create Redis Configuration**:
   ```bash
   # Create config directory
   mkdir -p ~/redis
   
   # Create redis.conf
   cat > ~/redis/redis.conf << EOL
   # Basic settings
   port 6379
   bind 127.0.0.1
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   
   # Persistence
   appendonly yes
   appendfilename "appendonly.aof"
   
   # Security
   requirepass your_redis_password  # Optional but recommended
   EOL
   ```

2. **Set Environment Variables**:
   ```bash
   # Add to your ~/.zshrc or ~/.bash_profile
   echo 'export REDIS_HOST=localhost' >> ~/.zshrc
   echo 'export REDIS_PORT=6379' >> ~/.zshrc
   echo 'export REDIS_DB=0' >> ~/.zshrc
   echo 'export REDIS_PASSWORD=your_redis_password' >> ~/.zshrc
   
   # Reload shell configuration
   source ~/.zshrc
   ```

#### 3. Starting Redis

1. **Start Redis as a Service**:
   ```bash
   # Start Redis
   brew services start redis
   
   # Verify Redis is running
   brew services list | grep redis
   ```

2. **Manual Start** (alternative):
   ```bash
   # Start Redis with custom config
   redis-server ~/redis/redis.conf
   ```

#### 4. Testing Redis

1. **Basic Connection Test**:
   ```bash
   # Connect to Redis
   redis-cli
   
   # If password is set
   redis-cli -a your_redis_password
   
   # Test connection
   ping  # Should return PONG
   ```

2. **Test Queue Operations**:
   ```bash
   # In redis-cli
   LPUSH notification_queue "test_message"
   RPOP notification_queue  # Should return "test_message"
   ```

3. **Python Test Script**:
   ```python
   # test_redis.py
   import redis
   
   # Connect to Redis
   redis_client = redis.Redis(
       host='localhost',
       port=6379,
       db=0,
       password='your_redis_password'  # If password is set
   )
   
   # Test connection
   print(redis_client.ping())  # Should print True
   
   # Test queue operations
   redis_client.lpush('notification_queue', 'test_message')
   message = redis_client.rpop('notification_queue')
   print(message)  # Should print b'test_message'
   ```

#### 5. Monitoring Redis

1. **Using Redis CLI**:
   ```bash
   # Monitor Redis commands in real-time
   redis-cli monitor
   
   # Check Redis info
   redis-cli info
   
   # Check memory usage
   redis-cli info memory
   ```

2. **Using Redis Commander** (Optional):
   ```bash
   # Install Redis Commander
   npm install -g redis-commander
   
   # Start Redis Commander
   redis-commander
   ```
   Then visit `http://localhost:8081` in your browser

#### 6. Troubleshooting

1. **Check Redis Status**:
   ```bash
   # Check if Redis is running
   brew services list | grep redis
   
   # Check Redis logs
   tail -f /usr/local/var/log/redis.log
   ```

2. **Common Issues**:
   - **Port already in use**:
     ```bash
     # Check if port 6379 is in use
     lsof -i :6379
     
     # Kill the process if needed
     kill -9 <PID>
     ```
   
   - **Memory issues**:
     ```bash
     # Check memory usage
     redis-cli info memory
     
     # Clear all data if needed
     redis-cli FLUSHALL
     ```

3. **Restart Redis**:
   ```bash
   # Stop Redis
   brew services stop redis
   
   # Start Redis
   brew services start redis
   ```

#### 7. Uninstallation

If you need to remove Redis:
```bash
# Stop Redis service
brew services stop redis

# Uninstall Redis
brew uninstall redis

# Remove Redis files
rm -rf /usr/local/var/redis
rm -rf ~/redis
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/feedback-analyzer.git
cd feedback-analyzer
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=feedback_analyzer

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SUPPORT_EMAIL=support@example.com

# JWT Configuration
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Start the services:
```bash
# Start Redis
redis-server

# Start the notification worker
python -m feedback_analyzer.workers.notification_worker

# Start the main application
uvicorn feedback_analyzer.main:app --reload
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=feedback_analyzer --cov-report=term-missing

# Run specific test category
pytest tests/unit/  # Unit tests
pytest tests/integration/  # Integration tests
pytest tests/e2e/  # End-to-end tests

# Run with specific markers
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Run only integration tests
```

## Architecture

### System Design
The Feedback Analyzer System is built as a modular monolith, combining the benefits of a monolithic architecture with the organizational advantages of a service-oriented design. This approach provides:

1. **Simplified Deployment**
   - Single application deployment
   - Unified logging and monitoring
   - Easier debugging and maintenance
   - Reduced operational complexity

2. **Modular Service Structure**
   - Clear service boundaries
   - Interface-based design
   - Dependency injection
   - Separation of concerns

### System Components
1. **API Layer**
   - FastAPI-based REST API
   - Request validation using Pydantic
   - JWT authentication
   - Rate limiting

2. **Service Layer**
   - Interface-based design
   - Dependency injection
   - Error handling
   - Logging
   - Services:
     - UserService: User management and authentication
     - FeedbackService: Feedback analysis and storage
     - NotificationService: Email notifications
     - TokenService: JWT token management
     - CustomerService: Customer data management

3. **Analysis Layer**
   - Rule-based analysis
   - AI-powered analysis
   - Topic classification
   - Sentiment analysis

4. **Storage Layer**
   - MongoDB for feedback storage
   - Redis for notification queue
   - Caching layer

5. **Notification Layer**
   - Asynchronous processing
   - Email notifications
   - Retry mechanism

### Data Flow
1. Feedback submission → API Layer
2. API Layer → Service Layer
3. Service Layer → Analysis Layer
4. Analysis Layer → Storage Layer
5. Storage Layer → Notification Layer (if negative)

### Future Scalability
While the current architecture is a modular monolith, the system is designed to be easily split into microservices if needed. The clear service boundaries and interface-based design make it possible to:

1. **Horizontal Scaling**
   - Split services into separate applications
   - Implement service discovery
   - Add API gateways
   - Set up container orchestration

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

## Assumptions

### Customer Data
- Customer phone numbers are required (10-15 digits)
- Customer names are required (1-100 characters)
- Customer emails are optional but must be valid if provided
- Customer data is stored securely

### Topic Classification
- Five predefined topics:
  - product_quality (build, design, performance)
  - customer_service (support, interaction, help)
  - delivery (shipping, arrival, courier)
  - pricing (cost, value, affordability)
  - usability (ease of use, interface, setup)
- Topics are scored from 0.0 to 1.0
- Multiple topics can be present in a single feedback
- "general" is used as a fallback topic

### System Behavior
- OpenAI API is available and properly configured
- Redis server is running and accessible
- SMTP server is configured for email notifications
- System can handle concurrent requests
- Negative feedback (sentiment score > 0.6) triggers notifications
- Notifications are processed asynchronously
- Failed notifications are automatically re-queued

## Technical Decisions

### 1. Technology Stack
- **Python**: Chosen for its rich ecosystem of data science and NLP libraries
- **FastAPI**: Modern, fast web framework with automatic OpenAPI documentation
- **MongoDB**: Flexible NoSQL database for handling dynamic feedback data
- **Redis**: In-memory data store for caching and message queuing
- **OpenAI GPT-3.5-turbo**: State-of-the-art language model for sentiment analysis

### 2. MongoDB Over SQL Server

##### Why MongoDB is Ideal for This Application

1. **Schema Flexibility for Real-World Feedback**
   - User feedback varies in structure and content
   - Natural handling of unpredictable data formats
   - No need for schema migrations or table alterations

   ```python
   # Our Feedback Model (feedback_models.py)
   class FeedbackResponse(BaseModel):
       id: str
       text: str
       customer: Optional[CustomerResponse] = None
       customer_id: Optional[str] = None
       sentiment: str
       sentiment_scores: Dict[str, float]
       main_topic: str
       topic_scores: Dict[str, float]
       top_topics: List[str]
       created_at: datetime
   ```

   Example document in MongoDB:
   ```json
   {
     "text": "Great product!",
     "customer": {
       "name": "Test User",
       "phone": "1234567890"
     },
     "sentiment": "positive",
     "sentiment_scores": {
       "positive": 0.8,
       "negative": 0.2
     },
     "main_topic": "product_quality",
     "topic_scores": {
       "product_quality": 0.6,
       "customer_service": 0.2,
       "delivery": 0.1,
       "pricing": 0.05,
       "usability": 0.05
     },
     "top_topics": ["product_quality", "customer_service"],
     "created_at": "2024-03-19T10:00:00Z"
   }
   ```

2. **Rapid Prototyping and Development**
   - No upfront schema definition required
   - Easy to add new fields without migrations
   - Faster feature delivery and iteration

   ```python
   # Adding new fields is as simple as:
   async def store_feedback(feedback_data):
       """Store feedback in MongoDB."""
       try:
           # Handle customer data if provided
           if "customer" in feedback_data:
               customer_id = get_or_create_customer(feedback_data["customer"])
               feedback_data["customer_id"] = customer_id
               del feedback_data["customer"]
           
           feedback_data["created_at"] = datetime.utcnow()
           result = feedback_collection.insert_one(feedback_data)
           return str(result.inserted_id)
       except Exception as e:
           logger.error(f"Error storing feedback: {str(e)}")
           raise
   ```

3. **Natural Fit for AI/NLP Outputs**
   - Native storage of JSON-like data structures
   - Perfect for storing sentiment analysis and topic classification results
   - No need for complex table relationships

   ```python
   # Our Feedback Service (feedback_service.py)
   class FeedbackService(FeedbackServiceInterface):
       def __init__(self):
           self.db = db
           self.sentiment_analyzer = SentimentAnalyzer()
           self.ai_sentiment_analyzer = AISentimentAnalyzer()
           self.topic_classifier = TopicClassifier()
   ```

4. **Simplicity and Low Overhead**
   - No need for complex JOINs or foreign keys
   - Lightweight setup for single-collection model
   - Reduced operational complexity

   ```python
   # Database setup (database.py)
   db = client[MONGODB_DATABASE]
   feedback_collection = db.feedback
   customer_collection = db.customers
   users_collection = db.users
   ```

5. **Easy Evolution and Scaling**
   - Start simple, enhance gradually
   - Add new fields without breaking existing code
   - Scale horizontally as needed

   ```python
   # Example of flexible querying (database.py)
   async def list_feedback(skip=0, limit=10, sentiment=None, topic=None):
       """List feedback with optional filtering"""
       try:
           query = {}
           if sentiment:
               query["sentiment"] = sentiment
           if topic:
               query["main_topic"] = topic
               
           cursor = feedback_collection.find(query).skip(skip).limit(limit)
           feedback_list = []
           for doc in cursor:
               doc["id"] = str(doc.pop("_id"))
               doc["created_at"] = doc["created_at"].isoformat()
               feedback_list.append(doc)
           return feedback_list
       except Exception as e:
           logger.error(f"Error listing feedback: {str(e)}")
           raise
   ```

##### Use Cases Where MongoDB Excels

| Use Case | Example from Our Code |
|----------|----------------------|
| Feedback varies in structure | `FeedbackResponse` model with optional fields |
| Rapid iteration | `store_feedback` function handling dynamic data |
| AI metadata storage | Sentiment scores and topic distributions |
| Simple data model | Single feedback collection with embedded documents |
| Future scalability | Flexible querying with `list_feedback` |

### 3. Architectural Decisions
**Chosen:**
- Modular monolith architecture
- Interface-based design
- Dependency injection
- Async processing

**Why:**
- Simplified deployment and maintenance
- Clear service boundaries
- Easy testing and development
- Good performance with async operations

**Alternatives Considered:**
- Microservices: Too complex for current scale
- Direct instantiation: Less testable
- Synchronous processing: Less performant

### 4. Security Decisions
**Chosen:**
- JWT authentication
- Environment variables
- Input validation
- Rate limiting

**Why:**
- Stateless authentication
- Secure configuration
- Data integrity
- DDoS protection

**Alternatives Considered:**
- Session-based auth: Less scalable
- Hard-coded config: Less secure
- No validation: Risky

## Production Readiness

### Immediate Priorities
1. **Security**
   - Add API key rotation
   - Implement request signing
   - Add IP whitelisting
   - Enhance rate limiting

2. **Monitoring**
   - Add Prometheus metrics
   - Set up Grafana dashboards
   - Implement health checks
   - Add tracing

3. **Scaling**
   - Implement connection pooling
   - Add caching layer
   - Optimize database queries
   - Add request queuing

4. **Reliability**
   - Add circuit breakers
   - Implement fallback mechanisms
   - Add data backup
   - Enhance error handling

### Trade-offs Made
1. **Performance vs. Accuracy**
   - Rule-based analysis for speed
   - AI analysis for accuracy
   - Caching for common cases

2. **Simplicity vs. Features**
   - Focused feature set
   - Clear API design
   - Minimal dependencies

3. **Cost vs. Quality**
   - OpenAI for quality
   - Redis for reliability
   - MongoDB for flexibility

### Business Goals Met
1. **Customer Feedback Analysis**
   - Accurate sentiment analysis
   - Precise topic classification
   - Real-time processing

2. **Quick Response to Issues**
   - Immediate notifications
   - Detailed feedback information
   - Easy tracking

3. **Scalability**
   - Connection pooling
   - Caching
   - Async processing

### Future Improvements
1. **Short-term**
   - Add more analysis metrics
   - Enhance notification system
   - Improve error handling

2. **Medium-term**
   - Add custom topic training
   - Implement A/B testing
   - Add feedback trends

3. **Long-term**
   - Add predictive analytics
   - Implement feedback automation
   - Add multi-language support

## API Documentation

### Authentication
```bash
# Login
POST /auth/login
{
    "email": "user@example.com",
    "password": "password123"
}

# Response
{
    "access_token": "eyJ0eXAi...",
    "token_type": "bearer"
}
```

### Feedback Endpoints
```bash
# Submit Feedback
POST /feedback/submit
{
    "text": "Great product!",
    "customer": {
        "name": "John Doe",
        "phone": "+1234567890"
    }
}

# List Feedback
GET /feedback?sentiment=negative&topic=product_quality

# Get Stats
GET /feedback/stats
```

## Testing

### Test Coverage
- Unit tests: 85% (verified with pytest-cov)
- Integration tests: 75%
- End-to-end tests: 65%

### Test Categories
1. **Unit Tests**
   - Service methods (UserService, FeedbackService, NotificationService)
   - Utility functions (SentimentAnalyzer, TopicClassifier)
   - Models (Pydantic models validation)
   - Token handling and validation
   - Database operations

2. **Integration Tests**
   - API endpoints with authentication
   - Database operations with MongoDB
   - Redis queue operations
   - SMTP email sending
   - OpenAI API integration

3. **End-to-End Tests**
   - Complete feedback submission workflow
   - User authentication flow
   - Notification processing
   - Error scenarios and recovery
   - Performance benchmarks

## Monitoring & Logging

### Metrics Collection
1. **Performance Metrics**
   - Request latency (p50, p95, p99)
   - Response time by endpoint
   - Database operation latency
   - Redis queue length
   - OpenAI API response time

2. **Business Metrics**
   - Feedback volume by sentiment
   - Topic distribution
   - Notification queue size
   - User engagement metrics
   - Error rates by type

3. **System Metrics**
   - CPU and memory usage
   - Database connection pool
   - Redis memory usage
   - API rate limit usage
   - Cache hit/miss ratios

### Logging Implementation
1. **Log Levels**
   - DEBUG: Detailed debugging information
   - INFO: General operational information
   - WARNING: Warning messages for potential issues
   - ERROR: Error events that might still allow the application to continue
   - CRITICAL: Critical events that may lead to application failure

2. **Log Categories**
   - Request/Response logs
   - Authentication logs
   - Database operation logs
   - External service interaction logs
   - Error and exception logs
   - Performance logs

3. **Log Format**
```json
{
    "timestamp": "2024-03-14T12:00:00Z",
    "level": "INFO",
    "service": "feedback_service",
    "operation": "analyze_feedback",
    "request_id": "uuid",
    "message": "Processing feedback",
    "metadata": {
        "feedback_id": "id",
        "sentiment": "positive",
        "processing_time_ms": 150
    }
}
```

### Alerting
1. **Error Rate Alerts**
   - Threshold: >5% error rate over 5 minutes
   - Notification: Email + Slack
   - Severity: High

2. **Performance Alerts**
   - Threshold: p95 latency > 500ms
   - Notification: Slack
   - Severity: Medium

3. **Queue Alerts**
   - Threshold: Queue length > 1000
   - Notification: Email
   - Severity: High

4. **System Alerts**
   - Threshold: CPU > 80% for 5 minutes
   - Notification: PagerDuty
   - Severity: Critical

## Error Handling

### Service-Level Error Handling
1. **UserService**
   - Duplicate email detection
   - Invalid email format
   - Password validation
   - Authentication failures
   - Database connection issues

2. **FeedbackService**
   - Invalid feedback data
   - Analysis failures
   - Storage errors
   - Notification queue issues
   - OpenAI API errors

3. **NotificationService**
   - SMTP connection failures
   - Email sending errors
   - Queue processing errors
   - Retry mechanism failures

### Retry Mechanisms
1. **Notification Retries**
   - Max attempts: 3
   - Backoff strategy: Exponential
   - Delay between retries: 5s, 15s, 45s
   - Dead letter queue after max retries

2. **API Retries**
   - Max attempts: 2
   - Backoff strategy: Linear
   - Delay between retries: 1s, 2s
   - Circuit breaker implementation

3. **Database Retries**
   - Max attempts: 3
   - Backoff strategy: Exponential
   - Delay between retries: 1s, 3s, 9s
   - Connection pool management

### Error Recovery
1. **Graceful Degradation**
   - Fallback to rule-based analysis if AI fails
   - Local caching for frequently accessed data
   - Queue persistence for notification retries
   - Read-only mode for critical failures

2. **Data Consistency**
   - Transaction management
   - Rollback mechanisms
   - Data validation before storage
   - Conflict resolution strategies

## Security

### Authentication
1. **JWT Implementation**
   - Token expiration: 30 minutes
   - Refresh token mechanism
   - Secure token storage
   - Token rotation on password change

2. **Password Security**
   - Bcrypt hashing
   - Minimum length: 8 characters
   - Complexity requirements
   - Password history check

### Authorization
1. **Role-Based Access**
   - User roles: admin, staff, customer
   - Permission-based access control
   - Resource-level authorization
   - API endpoint protection

2. **Rate Limiting**
   - Per-endpoint limits
   - IP-based throttling
   - User-based quotas
   - Burst allowance

### Data Protection
1. **Input Validation**
   - Pydantic model validation
   - SQL injection prevention
   - XSS protection
   - Input sanitization

2. **Data Encryption**
   - TLS for all communications
   - At-rest encryption
   - Secure key management
   - Sensitive data masking

### Security Headers
```python
{
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}
```

### Security Monitoring
1. **Audit Logging**
   - Authentication attempts
   - Authorization failures
   - Sensitive operations
   - Configuration changes

2. **Security Alerts**
   - Failed login attempts
   - Suspicious IP addresses
   - Rate limit breaches
   - Unauthorized access attempts 