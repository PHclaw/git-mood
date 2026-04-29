"""Rule-based sentiment analysis for commit messages."""

import re
from typing import Optional
from collections import defaultdict

# Mood categories with associated keywords and scores
MOOD_PATTERNS = {
    # Positive moods
    "excited": {
        "keywords": ["shipped", "finally", "awesome", "amazing", "🎉", "🚀", "w00t", "woohoo", "yay", "done!", "complete"],
        "score": 1.0,
        "emoji": "🎉",
    },
    "happy": {
        "keywords": ["works", "fixed", "added", "improved", "done", "completed", "success", "working", "solved"],
        "score": 0.5,
        "emoji": "😊",
    },
    "proud": {
        "keywords": ["feat", "feature", "implement", "add support", "release", "v1", "v2", "launch"],
        "score": 0.4,
        "emoji": "💪",
    },
    
    # Neutral
    "neutral": {
        "keywords": ["update", "change", "modify", "refactor", "clean", "move", "rename", "bump"],
        "score": 0.0,
        "emoji": "😐",
    },
    
    # Negative moods
    "frustrated": {
        "keywords": ["wtf", "stupid", "hack", "ugly", "dirty", "crap", "damn", "wth", "omg"],
        "score": -0.5,
        "emoji": "😤",
    },
    "stressed": {
        "keywords": ["hotfix", "urgent", "asap", "critical", "emergency", "production", "broken", "crash", "bugfix", "patch"],
        "score": -0.7,
        "emoji": "😰",
    },
    "tired": {
        "keywords": ["wip", "cleanup", "typo", "minor", "small", "quick", "tmp", "temp"],
        "score": -0.2,
        "emoji": "😴",
    },
    "angry": {
        "keywords": ["fix again", "still broken", "doesn't work", "not working", "broken again", "fuck", "shit"],
        "score": -0.8,
        "emoji": "😡",
    },
}

# Negation words that flip sentiment
NEGATIONS = {"not", "no", "never", "don't", "doesn't", "didn't", "won't", "can't"}

# Intensifiers that amplify sentiment
INTENSIFIERS = {"very", "really", "so", "totally", "completely", "absolutely"}


def analyze_sentiment(message: str) -> tuple[float, str, dict[str, list[str]]]:
    """
    Analyze sentiment of a commit message.
    
    Returns:
        Tuple of (score, category, matched_words)
    """
    message_lower = message.lower()
    words = set(re.findall(r'\b\w+\b', message_lower))
    
    # Track matched words by category
    matched_words = defaultdict(list)
    total_score = 0.0
    matches = 0
    
    for category, data in MOOD_PATTERNS.items():
        for keyword in data["keywords"]:
            keyword_lower = keyword.lower()
            # Check for exact word or phrase
            if keyword_lower in message_lower:
                # Check for negation before the keyword
                if _has_negation_before(message_lower, keyword_lower):
                    # Negated sentiment, reduce or flip
                    total_score -= data["score"] * 0.5
                else:
                    # Check for intensifier
                    multiplier = _get_intensifier_multiplier(message_lower, keyword_lower)
                    total_score += data["score"] * multiplier
                matched_words[category].append(keyword)
                matches += 1
    
    # Normalize score
    if matches > 0:
        score = max(-1.0, min(1.0, total_score / max(matches, 1)))
    else:
        score = 0.0
    
    # Determine primary category
    category = _determine_category(score, matched_words)
    
    return score, category, dict(matched_words)


def _has_negation_before(text: str, keyword: str) -> bool:
    """Check if there's a negation word before the keyword."""
    idx = text.find(keyword)
    if idx == -1:
        return False
    
    # Get words before the keyword
    before = text[:idx]
    words_before = set(re.findall(r'\b\w+\b', before.lower()))
    
    return bool(words_before & NEGATIONS)


def _get_intensifier_multiplier(text: str, keyword: str) -> float:
    """Get sentiment multiplier based on intensifiers before keyword."""
    idx = text.find(keyword)
    if idx == -1:
        return 1.0
    
    before = text[:idx]
    words_before = set(re.findall(r'\b\w+\b', before.lower()))
    
    if words_before & INTENSIFIERS:
        return 1.5
    
    return 1.0


def _determine_category(score: float, matched_words: dict[str, list[str]]) -> str:
    """Determine the primary mood category based on score and matched words."""
    if score >= 0.5:
        return "excited"
    elif score >= 0.2:
        return "happy"
    elif score >= -0.2:
        return "neutral"
    elif score >= -0.5:
        return "frustrated"
    else:
        return "stressed"


def get_mood_emoji(score: float) -> str:
    """Get emoji for a mood score."""
    if score >= 0.5:
        return "🎉"
    elif score >= 0.2:
        return "😊"
    elif score >= -0.2:
        return "😐"
    elif score >= -0.5:
        return "😤"
    else:
        return "😰"


def analyze_mood_words(commits: list) -> dict[str, list[str]]:
    """
    Aggregate mood words from multiple commits.
    
    Returns:
        Dict mapping mood category to list of matched words.
    """
    all_words = defaultdict(set)
    
    for commit in commits:
        _, _, matched = analyze_sentiment(commit.message)
        for category, words in matched.items():
            all_words[category].update(words)
    
    # Convert sets to sorted lists
    return {cat: sorted(list(words))[:10] for cat, words in all_words.items()}
