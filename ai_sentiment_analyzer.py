from typing import Dict, Literal
import os
from openai import OpenAI
import logging
import json

class AISentimentAnalyzer:
    def __init__(self):
        """Initialize the AI Sentiment Analyzer with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = logging.getLogger(__name__)

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of the given text using OpenAI's API.
        Returns a dictionary with positive and negative scores.
        """
        try:
            print("\n=== Sentiment Analysis Request ===")
            print(f"Input Text: {text}")
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a sentiment analysis expert. Analyze the given text and return ONLY a JSON object with two float values between 0 and 1:
                    {
                        "positive": <positive_score>,
                        "negative": <negative_score>
                    }
                    The scores should sum to 1.0. Be precise and objective in your analysis."""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
            
            print("\nRequest to OpenAI:")
            print(json.dumps(messages, indent=2))

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent results
                response_format={"type": "json_object"}
            )

            # Extract the JSON response
            result = response.choices[0].message.content
            print("\nResponse from OpenAI:")
            print(json.dumps(json.loads(result), indent=2))

            scores = json.loads(result)

            # Ensure scores are between 0 and 1
            scores["positive"] = min(max(float(scores["positive"]), 0.0), 1.0)
            scores["negative"] = min(max(float(scores["negative"]), 0.0), 1.0)

            print("\nFinal Scores:")
            print(json.dumps(scores, indent=2))
            print("===============================\n")

            return scores

        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            print(f"\nError in sentiment analysis: {str(e)}")
            # Return neutral scores in case of error
            return {
                "positive": 0.5,
                "negative": 0.5
            }

    def get_sentiment(self, text: str) -> Literal["positive", "neutral", "negative"]:
        """
        Get the overall sentiment of the text.
        Returns one of: "positive", "neutral", or "negative"
        """
        try:
            print("\n=== Getting Overall Sentiment ===")
            print(f"Input Text: {text}")
            
            scores = self.analyze(text)

            # Define thresholds for sentiment classification
            POSITIVE_THRESHOLD = 0.6
            NEGATIVE_THRESHOLD = 0.4

            # If scores are exactly 0.5, it's neutral
            if abs(scores["positive"] - 0.5) < 0.1 and abs(scores["negative"] - 0.5) < 0.1:
                sentiment = "neutral"
            # If negative score is very high, it's negative
            elif scores["negative"] > 0.8:
                sentiment = "negative"
            # Check if the text has a strong positive or negative sentiment
            elif scores["positive"] > POSITIVE_THRESHOLD and scores["positive"] > scores["negative"]:
                sentiment = "positive"
            elif scores["negative"] > NEGATIVE_THRESHOLD and scores["negative"] > scores["positive"]:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            print(f"\nDetermined Sentiment: {sentiment}")
            print("===============================\n")
            return sentiment

        except Exception as e:
            self.logger.error(f"Error in sentiment classification: {str(e)}")
            print(f"\nError in sentiment classification: {str(e)}")
            return "neutral"

    def get_detailed_analysis(self, text: str) -> Dict:
        """
        Get a detailed sentiment analysis including the main sentiment, scores,
        and a brief explanation.
        """
        try:
            print("\n=== Detailed Sentiment Analysis ===")
            print(f"Input Text: {text}")
            
            messages = [
                {
                    "role": "system",
                    "content": """Analyze the sentiment of the given text and return a JSON object with:
                    1. The overall sentiment (positive, neutral, or negative)
                    2. Positive and negative scores (between 0 and 1)
                    3. A brief explanation of the analysis
                    4. Key phrases that influenced the sentiment
                    Format:
                    {
                        "sentiment": "positive/neutral/negative",
                        "scores": {
                            "positive": <score>,
                            "negative": <score>
                        },
                        "explanation": "<brief explanation>",
                        "key_phrases": ["phrase1", "phrase2", ...]
                    }"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
            
            print("\nRequest to OpenAI:")
            print(json.dumps(messages, indent=2))

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            print("\nResponse from OpenAI:")
            print(json.dumps(json.loads(result), indent=2))
            print("===============================\n")

            return json.loads(result)

        except Exception as e:
            self.logger.error(f"Error in detailed analysis: {str(e)}")
            print(f"\nError in detailed analysis: {str(e)}")
            return {
                "sentiment": "neutral",
                "scores": {"positive": 0.5, "negative": 0.5},
                "explanation": "Error occurred during analysis",
                "key_phrases": []
            } 