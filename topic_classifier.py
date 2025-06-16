from typing import Dict, List, Literal
import re

class TopicClassifier:
    def __init__(self):
        # Define topic categories and their associated keywords
        self.topic_keywords = {
            'product_quality': {
                'keywords': {
                    'quality', 'durability', 'material', 'build', 'construction',
                    'design', 'appearance', 'look', 'feel', 'texture', 'finish',
                    'performance', 'functionality', 'reliability', 'sturdiness',
                    'workmanship', 'craftsmanship', 'defect', 'flaw', 'issue'
                },
                'phrases': [
                    'product quality',
                    'build quality',
                    'material quality',
                    'how well it works',
                    'how it performs',
                    'how it functions',
                    'how it looks',
                    'how it feels'
                ]
            },
            'customer_service': {
                'keywords': {
                    'service', 'support', 'help', 'assistance', 'response',
                    'representative', 'agent', 'staff', 'team', 'personnel',
                    'communication', 'contact', 'interaction', 'experience',
                    'attitude', 'professionalism', 'courtesy', 'politeness'
                },
                'phrases': [
                    'customer service',
                    'customer support',
                    'technical support',
                    'help desk',
                    'service team',
                    'support staff',
                    'service experience',
                    'support experience'
                ]
            },
            'delivery': {
                'keywords': {
                    'delivery', 'shipping', 'arrival', 'package', 'parcel',
                    'tracking', 'carrier', 'courier', 'postal', 'mail',
                    'dispatch', 'transit', 'transport', 'logistics',
                    'delay', 'late', 'early', 'on time', 'damaged'
                },
                'phrases': [
                    'delivery time',
                    'shipping time',
                    'arrival time',
                    'package delivery',
                    'shipping experience',
                    'delivery experience',
                    'tracking information',
                    'shipping status'
                ]
            },
            'pricing': {
                'keywords': {
                    'price', 'cost', 'value', 'worth', 'expensive', 'cheap',
                    'affordable', 'budget', 'money', 'payment', 'discount',
                    'deal', 'offer', 'sale', 'purchase', 'buy', 'spend',
                    'overpriced', 'underpriced', 'reasonable', 'unreasonable'
                },
                'phrases': [
                    'price point',
                    'value for money',
                    'worth the price',
                    'price range',
                    'cost effective',
                    'price comparison',
                    'price tag',
                    'price point'
                ]
            },
            'usability': {
                'keywords': {
                    'use', 'usage', 'interface', 'controls', 'buttons',
                    'menu', 'navigation', 'setup', 'installation', 'configure',
                    'settings', 'options', 'features', 'functions', 'operation',
                    'user-friendly', 'intuitive', 'complicated', 'complex'
                },
                'phrases': [
                    'easy to use',
                    'user interface',
                    'user experience',
                    'how to use',
                    'setup process',
                    'installation process',
                    'learning curve',
                    'user manual'
                ]
            }
        }
    
    def _count_phrases(self, text: str, phrases: List[str]) -> int:
        """Count occurrences of phrases in text."""
        count = 0
        for phrase in phrases:
            count += len(re.findall(r'\b' + re.escape(phrase) + r'\b', text.lower()))
        return count
    
    def classify(self, text: str) -> Dict[str, float]:
        """
        Classify the main topics in the given text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, float]: A dictionary containing topic scores
        """
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Initialize scores for each topic
        topic_scores = {topic: 0.0 for topic in self.topic_keywords.keys()}
        
        # Calculate scores for each topic
        for topic, data in self.topic_keywords.items():
            # Count keyword matches
            keyword_matches = len(words.intersection(data['keywords']))
            
            # Count phrase matches (weighted more heavily)
            phrase_matches = self._count_phrases(text_lower, data['phrases']) * 2
            
            # Calculate total score
            total_matches = keyword_matches + phrase_matches
            
            # Normalize score
            if total_matches > 0:
                topic_scores[topic] = min(total_matches / 5, 1.0)  # Cap at 1.0
        
        return topic_scores
    
    def get_main_topic(self, text: str) -> str:
        """
        Get the main topic of the text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            str: The main topic
        """
        scores = self.classify(text)
        
        # Find the topic with the highest score
        max_score = max(scores.values())
        if max_score == 0:
            return "general"  # No specific topic detected
        
        # Return the topic with the highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def get_top_topics(self, text: str, n: int = 2) -> List[str]:
        """
        Get the top N topics from the text.
        
        Args:
            text (str): The text to analyze
            n (int): Number of top topics to return
            
        Returns:
            List[str]: List of top topics
        """
        scores = self.classify(text)
        
        # Sort topics by score in descending order
        sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N topics that have a score > 0
        return [topic for topic, score in sorted_topics if score > 0][:n] 