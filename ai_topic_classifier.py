from typing import Dict, List
from openai import AsyncOpenAI
import os
import logging
from dotenv import load_dotenv
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AITopicClassifier:
    def __init__(self):
        """Initialize the AI Topic Classifier with OpenAI Async client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.valid_topics = [
            "product_quality",
            "customer_service",
            "delivery",
            "pricing",
            "usability"
        ]

    async def classify(self, text: str) -> Dict[str, float]:
        """
        Classify the main topics in the given text using OpenAI API.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, float]: A dictionary containing topic scores
        """
        try:
            if not text:
                return {topic: 0.0 for topic in self.valid_topics}

            prompt = f"""Analyze this customer feedback and assign relevance scores to each topic:

Text: "{text}"

Return a JSON object like:
{{"product_quality": 0.3, "customer_service": 0.0, ...}}

Score each topic from 0.0 to 1.0 based on:
- product_quality: mentions of build, design, performance
- customer_service: support, interaction, help
- delivery: shipping, arrival, courier
- pricing: cost, value, affordability
- usability: ease of use, interface, setup

Rules:
- 0.0: No mention
- 0.3: Brief mention
- 0.6: Clear mention with details
- 0.9: Strong focus
"""

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a precise topic classifier. Return topic scores in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            logger.debug(f"OpenAI raw output: {result}")

            scores = json.loads(result)
            topic_scores = {}

            for topic in self.valid_topics:
                try:
                    score = float(scores.get(topic, 0.0))
                    topic_scores[topic] = min(max(score, 0.0), 1.0)
                except (ValueError, TypeError):
                    topic_scores[topic] = 0.0

            return topic_scores

        except Exception as e:
            logger.error(f"Error in topic classification: {str(e)}")
            return {topic: 0.0 for topic in self.valid_topics}

    async def get_main_topic(self, text: str) -> str:
        """
        Return the topic with the highest relevance score.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            str: The main topic
        """
        try:
            scores = await self.classify(text)
            if not scores:
                return "general"

            max_score = max(scores.values())
            if max_score == 0:
                return "general"

            return max(scores.items(), key=lambda x: x[1])[0]

        except Exception as e:
            logger.error(f"Error getting main topic: {str(e)}")
            return "general"

    async def get_top_topics(self, text: str, n: int = 2) -> List[str]:
        """
        Return the top N topics with non-zero scores.
        
        Args:
            text (str): The text to analyze
            n (int): Number of top topics to return
            
        Returns:
            List[str]: List of top topics
        """
        try:
            scores = await self.classify(text)
            if not scores:
                return ["general"]

            sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_topics = [topic for topic, score in sorted_topics if score > 0][:n]

            return top_topics if top_topics else ["general"]

        except Exception as e:
            logger.error(f"Error getting top topics: {str(e)}")
            return ["general"]

# Create a singleton instance
ai_topic_classifier = AITopicClassifier() 