from typing import Dict, Literal
import re

class SentimentAnalyzer:
    def __init__(self):
        # Define positive and negative word lists with phrases
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'happy', 'satisfied', 'perfect', 'best', 'awesome',
            'outstanding', 'brilliant', 'superb', 'terrific', 'fabulous',
            'helpful', 'quality', 'nice', 'pleased'
        }
        
        # Strong negative words get higher weight
        self.strong_negative_words = {
            'terrible', 'awful', 'horrible', 'worst', 'hate', 'disappointed',
            'useless', 'waste', 'broken', 'damaged', 'faulty'
        }
        
        # Regular negative words
        self.negative_words = {
            'bad', 'poor', 'problem', 'issue', 'difficult', 'hard',
            'complicated', 'wait', 'slow', 'late', 'delayed', 'expensive',
            'overpriced'
        }
        
        # Define negative phrases that should be caught
        self.negative_phrases = [
            'too long',
            'not good',
            'not great',
            'not happy',
            'not satisfied',
            'not working',
            'does not work',
            'did not work',
            'was not',
            'were not',
            'is not',
            'are not',
            'would not recommend',
            'do not recommend',
            'cannot recommend',
            'can not recommend'
        ]
        
        # Define neutral words that indicate a neutral sentiment
        self.neutral_words = {
            'okay', 'ok', 'fine', 'average', 'normal', 'regular', 'standard',
            'typical', 'usual', 'expected', 'decent', 'adequate', 'sufficient',
            'moderate', 'fair', 'reasonable', 'works', 'does', 'will', 'do',
            'wrong', 'right', 'basic', 'simple', 'standard', 'common',
            'ordinary', 'regular', 'usual', 'typical', 'expected'
        }
        
        # Define neutral phrases that indicate a neutral sentiment
        self.neutral_phrases = [
            'as expected',
            'nothing special',
            'nothing wrong',
            'does the job',
            'gets the job done',
            'works as expected',
            'meets expectations',
            'what you would expect',
            'does what it says',
            'does what it will do',
            'works as intended',
            'functions as expected',
            'performs as expected',
            'does what it should',
            'does what it needs to do',
            'meets basic requirements',
            'fulfills its purpose',
            'serves its purpose',
            'does its job',
            'gets the job done'
        ]
    
    def _count_phrases(self, text: str, phrases: list) -> int:
        """Count occurrences of phrases in text."""
        count = 0
        for phrase in phrases:
            count += len(re.findall(r'\b' + re.escape(phrase) + r'\b', text.lower()))
        return count
    
    def _is_neutral_text(self, text: str) -> bool:
        """Check if the text is likely to be neutral."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count neutral words
        neutral_count = sum(1 for word in words if word in self.neutral_words)
        
        # Count neutral phrases
        neutral_phrase_count = self._count_phrases(text_lower, self.neutral_phrases)
        
        # Count strong sentiment words
        strong_positive_count = sum(1 for word in words if word in self.positive_words)
        strong_negative_count = sum(1 for word in words if word in self.strong_negative_words)
        
        # If there are neutral words/phrases and no strong sentiment words
        if (neutral_count > 0 or neutral_phrase_count > 0) and \
           strong_positive_count == 0 and strong_negative_count == 0:
            return True
            
        # If the text contains neutral phrases and no strong sentiment
        if neutral_phrase_count > 0 and \
           not any(word in text_lower for word in self.strong_negative_words) and \
           not any(word in text_lower for word in self.positive_words):
            return True
            
        # If the text contains multiple neutral indicators
        if neutral_count >= 2 or neutral_phrase_count >= 2:
            return True
            
        return False
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze the sentiment of the given text using a word and phrase-based approach."""
        # First check if the text is neutral
        if self._is_neutral_text(text):
            return {
                "positive": 0.5,
                "negative": 0.5
            }
        
        # Convert text to lowercase
        text_lower = text.lower()
        
        # Count positive words
        words = text_lower.split()
        positive_count = sum(1 for word in words if word in self.positive_words)
        
        # Count negative words with weights
        negative_count = sum(2 for word in words if word in self.negative_words)  # Regular negative words count double
        strong_negative_count = sum(5 for word in words if word in self.strong_negative_words)  # Strong negative words count 5x
        
        # Add negative phrases count (weighted)
        negative_phrases_count = self._count_phrases(text_lower, self.negative_phrases) * 5  # Phrases count 5x
        
        # Calculate total negative score
        total_negative = negative_count + strong_negative_count + negative_phrases_count
        
        # If there are no positive words and any negative indicators, return completely negative
        if positive_count == 0 and total_negative > 0:
            return {
                "positive": 0.0,
                "negative": 1.0
            }
        
        # If there are multiple strong negative indicators, return completely negative
        if strong_negative_count >= 5 or negative_phrases_count >= 5:
            return {
                "positive": 0.0,
                "negative": 1.0
            }
        
        # Calculate total sentiment words
        total_sentiment_words = positive_count + total_negative
        
        if total_sentiment_words == 0:
            # If no sentiment words found, return neutral scores
            return {
                "positive": 0.5,
                "negative": 0.5
            }
        
        # Calculate scores
        positive_score = positive_count / total_sentiment_words
        negative_score = total_negative / total_sentiment_words
        
        # Ensure scores are between 0 and 1
        positive_score = min(max(positive_score, 0.0), 1.0)
        negative_score = min(max(negative_score, 0.0), 1.0)
        
        # If negative score is very high, make it 1.0
        if negative_score > 0.8:
            return {
                "positive": 0.0,
                "negative": 1.0
            }
        
        # If the difference between scores is small, return neutral
        if abs(positive_score - negative_score) < 0.3:
            return {
                "positive": 0.5,
                "negative": 0.5
            }
        
        return {
            "positive": positive_score,
            "negative": negative_score
        }
    
    def get_sentiment(self, text: str) -> Literal["positive", "neutral", "negative"]:
        """Get the overall sentiment of the text."""
        scores = self.analyze(text)
        
        # If scores are exactly 0.5, it's neutral
        if scores["positive"] == 0.5 and scores["negative"] == 0.5:
            return "neutral"
        
        # If negative score is 1.0, it's definitely negative
        if scores["negative"] == 1.0:
            return "negative"
        
        # Define thresholds for sentiment classification
        POSITIVE_THRESHOLD = 0.6  # Need 60% positive words for positive sentiment
        NEGATIVE_THRESHOLD = 0.4  # Lowered threshold for negative sentiment
        
        # Check if the text has a strong positive or negative sentiment
        if scores["positive"] > POSITIVE_THRESHOLD and scores["positive"] > scores["negative"]:
            return "positive"
        elif scores["negative"] > NEGATIVE_THRESHOLD and scores["negative"] > scores["positive"]:
            return "negative"
        else:
            return "neutral" 