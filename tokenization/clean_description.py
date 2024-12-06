
import re
import unicodedata
import contractions
from typing import List
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, words
from nltk.stem import WordNetLemmatizer

class PodcastDescriptionCleaner:
    def __init__(self, text: str):
        """
        Initialize the podcast description cleaner with advanced filtering mechanisms.
        
        :param text: Raw podcast description text
        """
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('words', quiet=True)
        nltk.download('wordnet', quiet=True)

        self.text = text
        self.lemmatizer = WordNetLemmatizer()
        
        # Expanded and categorized promotional keywords
        self.promo_keywords = {
            'call_to_action': [
                'visit', 'follow', 'check out', 'learn', 'subscribe', 
                'click here', 'download', 'support', 'join', 'get', 
                'unlock', 'exclusive', 'sign up', 'register', 'sign'
            ],
            'commercial': [
                'sponsored', 'advertisement', 'merch', 'buy now', 'limited time', 
                'special offer', 'discount', 'promo', 'coupon', 'sale', 'deal', 
                'ad-free', 'new players', 'credits', 'deposit', 'match', 'episode',
            ],
            'contact': [
                'contact', 'inquiries', 'dm', 'message', 'email', 
                'find me', 'connect', 'reach out', 'requests', 'credits'
            ],
            'digital_platforms': [
                'patreon', 'instagram', 'tiktok', 'snapchat', 'facebook', 
                'twitter', 'youtube', 'linkedin', 'pinterest', 'discord', 
                'reddit', 'twitch', 'tik tok', 'spotify'
            ],
            'urgency_markers': [
                'now', 'today', 'hurry', 'fast', 'quick', 
                'immediately', 'limited', 'urgent', 'while supplies last'
            ],
            'support_solicitation': [
                'support my', 'help me', 'donate', 'tip', 'fund', 
                'crowdfund', 'patreon', 'contribute', 'sponsor'
            ],
            'access_modifiers': [
                'access', 'preview', 'early', 'bonus', 
                'premium', 'vip', 'exclusive', 'members only'
            ],
            'web_references': [
                'link', 'website', 'homepage', 'page', 'site', 
                'url', 'http', 'https', 'www'
            ]
        }

        # Flatten promo keywords for easy checking
        self.flat_promo_keywords = [
            keyword for category in self.promo_keywords.values() 
            for keyword in category
        ]

        # Stopwords and language setup
        self.stop_words = set(stopwords.words('english'))
        self.english_words = set(words.words())

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by removing accents, converting to lowercase, 
        and standardizing whitespace.
        
        :param text: Input text
        :return: Normalized text
        """
        # Remove accents
        text = ''.join(
            char for char in unicodedata.normalize('NFKD', text)
            if unicodedata.category(char) != 'Mn'
        )
        
        # Convert to lowercase and normalize whitespace
        text = re.sub(r'\s+', ' ', text.lower().strip())
        
        return text

    def _is_valid_token(self, token: str) -> bool:
        """
        Advanced token validation with more sophisticated checks.
        
        :param token: Input token
        :return: Boolean indicating token validity
        """
        # Lemmatize token for more robust checking
        lemmatized_token = self.lemmatizer.lemmatize(token)
        
        # Exclude tokens with non-alphanumeric characters
        if not re.match(r'^[a-zA-Z0-9]+$', lemmatized_token):
            return False
        
        # Exclude overly short or long tokens
        if len(lemmatized_token) < 3 or len(lemmatized_token) > 20:
            return False
        
        # Exclude stopwords
        if lemmatized_token in self.stop_words:
            return False
        
        # Exclude promo-related tokens
        if lemmatized_token in self.flat_promo_keywords:
            return False
        
        # Exclude non-dictionary words (optional)
        if lemmatized_token not in self.english_words:
            return False
        
        return True

    def _detect_promotional_density(self, sentence: str) -> float:
        """
        Calculate the promotional keyword density in a sentence.
        
        :param sentence: Input sentence
        :return: Percentage of promotional keywords
        """
        tokens = word_tokenize(sentence.lower())
        promo_count = sum(
            1 for token in tokens 
            if token in self.flat_promo_keywords
        )
        return (promo_count / len(tokens)) * 100 if tokens else 0

    def clean_description(self) -> List[str]:
        """
        Comprehensive cleaning of podcast description.
        
        :return: List of clean, valid tokens
        """
        # Expand contractions
        expanded_text = contractions.fix(self.text)
        
        # Normalize text
        normalized_text = self._normalize_text(expanded_text)
        
        # Tokenize sentences
        sentences = sent_tokenize(normalized_text)
        
        # Advanced sentence filtering
        cleaned_sentences = [
            sentence for sentence in sentences
            if (
                # Remove sentences with URLs
                not re.search(r'https?://\S+|www\.\S+', sentence) and
                # Remove sentences with high promotional density
                self._detect_promotional_density(sentence) < 40 and
                # Remove sentences dominated by promotional keywords
                len([
                    word for word in word_tokenize(sentence) 
                    if word.lower() in self.flat_promo_keywords
                ]) < len(word_tokenize(sentence)) * 0.5
            )
        ]
        
        # Rejoin cleaned sentences
        cleaned_text = ' '.join(cleaned_sentences)
        
        # Remove special characters except basic punctuation
        cleaned_text = re.sub(r'[^\w\s.,!?]', '', cleaned_text)
        
        # Tokenize and filter tokens
        tokens = word_tokenize(cleaned_text)
        
        # Validate tokens using is_valid_token
        valid_tokens = [
            token for token in tokens 
            if self._is_valid_token(token)
        ]
        
        return valid_tokens
