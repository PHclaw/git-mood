"""Core MoodAnalyzer class."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from .git import parse_git_log, get_repo_name, get_all_authors
from .models import Commit, DayMood, AuthorMood, MoodReport
from .sentiment import analyze_sentiment, get_mood_emoji, analyze_mood_words


class MoodAnalyzer:
    """
    Analyze git commit history for mood patterns.
    
    Usage:
        analyzer = MoodAnalyzer("/path/to/repo", days=30)
        report = analyzer.analyze()
        print(report.to_text())
    """
    
    def __init__(
        self,
        repo_path: str = ".",
        days: int = 30,
        use_llm: bool = False,
        show_emoji: bool = True,
        use_color: bool = True,
        verbose: bool = False,
    ):
        self.repo_path = Path(repo_path).resolve()
        self.days = days
        self.use_llm = use_llm
        self.show_emoji = show_emoji
        self.use_color = use_color
        self.verbose = verbose
        
        self._commits: list[Commit] = []
        self._repo_name: str = ""
    
    def analyze(self) -> MoodReport:
        """
        Perform full mood analysis.
        
        Returns:
            MoodReport with all analysis results.
        """
        # Load commits
        if self.verbose:
            print(f"Loading commits from {self.repo_path}...")
        
        self._commits = parse_git_log(str(self.repo_path), days=self.days)
        self._repo_name = get_repo_name(str(self.repo_path))
        
        if not self._commits:
            return MoodReport(
                repo_name=self._repo_name,
                total_commits=0,
                days_analyzed=self.days,
                overall_mood=0.0,
                mood_emoji="😐",
                energy_level=0.0,
                stress_index=0.0,
                peak_hour=12,
                peak_day="N/A",
            )
        
        # Analyze sentiment for each commit
        for commit in self._commits:
            score, category, _ = analyze_sentiment(commit.message)
            commit.mood_score = score
            commit.mood_category = category
        
        # Calculate aggregates
        overall_mood = self._calculate_overall_mood()
        energy_level = self._calculate_energy_level()
        stress_index = self._calculate_stress_index()
        peak_hour = self._find_peak_hour()
        peak_day = self._find_peak_day()
        night_owl = self._calculate_night_owl()
        weekend_warrior = self._calculate_weekend_warrior()
        
        # Daily breakdown
        daily_moods = self._calculate_daily_moods()
        
        # Author breakdown
        author_moods = self._calculate_author_moods()
        
        # Mood words
        mood_words = analyze_mood_words(self._commits)
        
        # Top commits (most positive and negative)
        top_commits = self._find_notable_commits()
        
        return MoodReport(
            repo_name=self._repo_name,
            total_commits=len(self._commits),
            days_analyzed=self.days,
            overall_mood=overall_mood,
            mood_emoji=get_mood_emoji(overall_mood),
            energy_level=energy_level,
            stress_index=stress_index,
            peak_hour=peak_hour,
            peak_day=peak_day,
            daily_moods=daily_moods,
            author_moods=author_moods,
            mood_words=mood_words,
            top_commits=top_commits,
            night_owl_score=night_owl,
            weekend_warrior_score=weekend_warrior,
        )
    
    def trend(self):
        """Analyze mood trend over time."""
        # TODO: Implement trend analysis
        return self.analyze()
    
    def full_report(self):
        """Generate full report (same as analyze)."""
        return self.analyze()
    
    def _calculate_overall_mood(self) -> float:
        """Calculate overall mood score from all commits."""
        if not self._commits:
            return 0.0
        
        total = sum(c.mood_score for c in self._commits)
        return total / len(self._commits)
    
    def _calculate_energy_level(self) -> float:
        """
        Calculate energy level based on commit frequency and patterns.
        
        High energy = frequent commits, consistent activity
        Low energy = sparse commits, irregular patterns
        """
        if not self._commits:
            return 0.0
        
        # Commits per day
        commits_per_day = len(self._commits) / max(self.days, 1)
        
        # Normalize: 5 commits/day = 100% energy
        energy = min(1.0, commits_per_day / 5.0)
        
        # Boost for consistency (multiple days with commits)
        unique_days = len(set(c.timestamp.date() for c in self._commits))
        consistency_bonus = min(0.2, unique_days / self.days * 0.2)
        
        return min(1.0, energy + consistency_bonus)
    
    def _calculate_stress_index(self) -> float:
        """
        Calculate stress index based on:
        - Ratio of hotfix/urgent commits
        - Late night commits
        - Commit message negativity
        """
        if not self._commits:
            return 0.0
        
        # Count negative indicators
        negative_commits = sum(1 for c in self._commits if c.mood_score < -0.3)
        night_commits = sum(1 for c in self._commits if c.is_night)
        weekend_commits = sum(1 for c in self._commits if c.is_weekend)
        
        total = len(self._commits)
        
        # Weight factors
        negative_ratio = negative_commits / total
        night_ratio = night_commits / total
        weekend_ratio = weekend_commits / total
        
        # Combined stress index
        stress = (negative_ratio * 0.5 + night_ratio * 0.3 + weekend_ratio * 0.2)
        
        return min(1.0, stress)
    
    def _find_peak_hour(self) -> int:
        """Find the hour with most commits."""
        if not self._commits:
            return 12
        
        hour_counts = defaultdict(int)
        for commit in self._commits:
            hour_counts[commit.hour] += 1
        
        return max(hour_counts, key=hour_counts.get)
    
    def _find_peak_day(self) -> str:
        """Find the day of week with most commits."""
        if not self._commits:
            return "Monday"
        
        day_counts = defaultdict(int)
        for commit in self._commits:
            day_counts[commit.day_of_week] += 1
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        peak = max(day_counts, key=day_counts.get)
        return days[peak]
    
    def _calculate_night_owl(self) -> float:
        """Calculate night owl score (ratio of night commits)."""
        if not self._commits:
            return 0.0
        
        night_commits = sum(1 for c in self._commits if c.is_night)
        return night_commits / len(self._commits)
    
    def _calculate_weekend_warrior(self) -> float:
        """Calculate weekend warrior score (ratio of weekend commits)."""
        if not self._commits:
            return 0.0
        
        weekend_commits = sum(1 for c in self._commits if c.is_weekend)
        return weekend_commits / len(self._commits)
    
    def _calculate_daily_moods(self) -> list[DayMood]:
        """Calculate mood for each day."""
        days = defaultdict(list)
        
        for commit in self._commits:
            date_str = commit.timestamp.strftime("%Y-%m-%d")
            days[date_str].append(commit)
        
        daily_moods = []
        for date_str, commits in sorted(days.items()):
            avg_mood = sum(c.mood_score for c in commits) / len(commits)
            daily_moods.append(DayMood(
                date=date_str,
                commits=commits,
                mood_score=avg_mood,
                mood_emoji=get_mood_emoji(avg_mood),
            ))
        
        return daily_moods[-30:]  # Last 30 days
    
    def _calculate_author_moods(self) -> list[AuthorMood]:
        """Calculate mood per author."""
        authors = defaultdict(list)
        
        for commit in self._commits:
            # Extract name from "Name <email>" format
            name = commit.author.split('<')[0].strip()
            authors[name].append(commit)
        
        author_moods = []
        for name, commits in authors.items():
            avg_mood = sum(c.mood_score for c in commits) / len(commits)
            author_moods.append(AuthorMood(
                author=name,
                commits=commits,
                mood_score=avg_mood,
                mood_emoji=get_mood_emoji(avg_mood),
            ))
        
        return author_moods
    
    def _find_notable_commits(self) -> list[Commit]:
        """Find most notable commits (extreme moods)."""
        sorted_commits = sorted(self._commits, key=lambda c: c.mood_score)
        
        # Get most negative and most positive
        notable = []
        if sorted_commits:
            # Most negative
            notable.append(sorted_commits[0])
            # Most positive
            if len(sorted_commits) > 1:
                notable.append(sorted_commits[-1])
        
        return notable
