"""Data models for git-mood."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class Commit:
    """Represents a single git commit."""
    hash: str
    message: str
    author: str
    timestamp: datetime
    mood_score: float = 0.0
    mood_category: str = "neutral"
    
    @property
    def short_hash(self) -> str:
        return self.hash[:7]
    
    @property
    def hour(self) -> int:
        return self.timestamp.hour
    
    @property
    def day_of_week(self) -> int:
        return self.timestamp.weekday()  # 0=Monday, 6=Sunday
    
    @property
    def is_weekend(self) -> bool:
        return self.day_of_week >= 5
    
    @property
    def is_night(self) -> bool:
        return self.hour >= 22 or self.hour < 6


@dataclass
class DayMood:
    """Mood summary for a single day."""
    date: str  # YYYY-MM-DD
    commits: list[Commit] = field(default_factory=list)
    mood_score: float = 0.0
    mood_emoji: str = "😐"
    
    @property
    def commit_count(self) -> int:
        return len(self.commits)


@dataclass
class AuthorMood:
    """Mood summary for a single author."""
    author: str
    commits: list[Commit] = field(default_factory=list)
    mood_score: float = 0.0
    mood_emoji: str = "😐"
    
    @property
    def commit_count(self) -> int:
        return len(self.commits)


@dataclass
class MoodReport:
    """Full mood analysis report."""
    repo_name: str
    total_commits: int
    days_analyzed: int
    overall_mood: float  # -1.0 to 1.0
    mood_emoji: str
    energy_level: float  # 0.0 to 1.0
    stress_index: float  # 0.0 to 1.0
    peak_hour: int
    peak_day: str
    daily_moods: list[DayMood] = field(default_factory=list)
    author_moods: list[AuthorMood] = field(default_factory=list)
    mood_words: dict[str, list[str]] = field(default_factory=dict)
    top_commits: list[Commit] = field(default_factory=list)
    night_owl_score: float = 0.0
    weekend_warrior_score: float = 0.0
    
    def to_text(self, show_contributors: bool = False) -> str:
        """Generate ASCII text report."""
        lines = []
        lines.append("╔" + "═" * 58 + "╗")
        lines.append(f"║  🎮 git-mood report for: {self.repo_name:<30} ║")
        lines.append(f"║  Analyzing {self.total_commits} commits over {self.days_analyzed} days{' ' * (22 - len(str(self.total_commits)) - len(str(self.days_analyzed)))}║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("║                                                                ║")
        lines.append(f"║  Overall Mood: {self.mood_emoji} {self._mood_label():<10} ({self.overall_mood:+.2f}){' ' * 18}║")
        lines.append(f"║  Energy Level: {'🔥' if self.energy_level > 0.6 else '⚡' if self.energy_level > 0.3 else '😴'} {'High' if self.energy_level > 0.6 else 'Medium' if self.energy_level > 0.3 else 'Low':<10} ({self.energy_level:.0%}){' ' * 19}║")
        lines.append(f"║  Stress Index: {'😰' if self.stress_index > 0.5 else '😊' if self.stress_index < 0.3 else '😐'} {'High' if self.stress_index > 0.5 else 'Low' if self.stress_index < 0.3 else 'Medium':<10} ({self.stress_index:.0%}){' ' * 19}║")
        lines.append("║                                                                ║")
        lines.append(f"║  Peak Hour: {self.peak_hour}:00 ({'Night Owl! 🦉' if self.peak_hour >= 22 or self.peak_hour < 6 else 'Early Bird 🐦' if self.peak_hour < 9 else 'Standard Hours'}){' ' * max(0, 20 - len(str(self.peak_hour)))}║")
        lines.append(f"║  Most Active Day: {self.peak_day:<15}{' ' * 25}║")
        lines.append(f"║  Night Owl Score: {self.night_owl_score:.0%}{' ' * 31}║")
        lines.append(f"║  Weekend Warrior: {self.weekend_warrior_score:.0%}{' ' * 31}║")
        lines.append("║                                                                ║")
        
        # Hourly heatmap (simplified)
        lines.append("║  Commits by Hour:                                              ║")
        lines.append("║   0  2  4  6  8  10 12 14 16 18 20 22                          ║")
        lines.append("║   " + self._hourly_bar() + "                          ║")
        lines.append("║                                                                ║")
        
        # Day heatmap
        lines.append("║  Commits by Day:                                               ║")
        lines.append("║   Mo  Tu  We  Th  Fr  Sa  Su                                   ║")
        lines.append("║   " + self._daily_bar() + "                                   ║")
        lines.append("║                                                                ║")
        
        # Top mood words
        if self.mood_words:
            lines.append("║  Top Mood Words:                                               ║")
            for category, words in list(self.mood_words.items())[:4]:
                words_str = ", ".join(words[:5]) if words else "none"
                lines.append(f"║    {category}: {words_str[:45]:<45}║")
            lines.append("║                                                                ║")
        
        # Recent interesting commits
        if self.top_commits:
            lines.append("║  Notable Commits:                                              ║")
            for commit in self.top_commits[:5]:
                msg = commit.message.split('\n')[0][:40]
                emoji = "😊" if commit.mood_score > 0.3 else "😤" if commit.mood_score < -0.3 else "😐"
                lines.append(f"║    {emoji} {commit.short_hash} {msg:<40}║")
            lines.append("║                                                                ║")
        
        # Contributor breakdown
        if show_contributors and self.author_moods:
            lines.append("║  By Contributor:                                               ║")
            for am in sorted(self.author_moods, key=lambda x: x.commit_count, reverse=True)[:5]:
                name = am.author.split('<')[0].strip()[:20]
                lines.append(f"║    {am.mood_emoji} {name:<20} {am.commit_count:>4} commits ({am.mood_score:+.2f}){' ' * max(0, 8)}║")
            lines.append("║                                                                ║")
        
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        lines.append("Made with 😊 by PHclaw | https://github.com/PHclaw/git-mood")
        
        return "\n".join(lines)
    
    def _mood_label(self) -> str:
        if self.overall_mood > 0.5:
            return "Positive"
        elif self.overall_mood > 0.2:
            return "Good"
        elif self.overall_mood > -0.2:
            return "Neutral"
        elif self.overall_mood > -0.5:
            return "Stressed"
        else:
            return "Frustrated"
    
    def _hourly_bar(self) -> str:
        """Generate hourly activity bar."""
        # Simplified: just show relative activity
        bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        # This is a placeholder - actual implementation would use real data
        return "▃  ▂  ▁  ▄  ▆  ▇  █  ▆  ▅  ▄  ▃  ▅"
    
    def _daily_bar(self) -> str:
        """Generate daily activity bar."""
        bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        # Placeholder
        return "▄  ▅  ▆  ▇  █  ▃  ▂"
    
    def to_json(self) -> str:
        """Export as JSON."""
        data = {
            "repo_name": self.repo_name,
            "total_commits": self.total_commits,
            "days_analyzed": self.days_analyzed,
            "overall_mood": self.overall_mood,
            "mood_emoji": self.mood_emoji,
            "energy_level": self.energy_level,
            "stress_index": self.stress_index,
            "peak_hour": self.peak_hour,
            "peak_day": self.peak_day,
            "night_owl_score": self.night_owl_score,
            "weekend_warrior_score": self.weekend_warrior_score,
            "daily_moods": [
                {"date": d.date, "commits": d.commit_count, "mood_score": d.mood_score}
                for d in self.daily_moods
            ],
            "author_moods": [
                {"author": a.author, "commits": a.commit_count, "mood_score": a.mood_score}
                for a in self.author_moods
            ],
            "mood_words": self.mood_words,
        }
        return json.dumps(data, indent=2)
    
    def to_html(self) -> str:
        """Export as standalone HTML report."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>git-mood report: {self.repo_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            background: #0f0f0f; color: #e5e5e5;
            padding: 40px; max-width: 800px; margin: 0 auto;
        }}
        h1 {{ color: #22c55e; margin-bottom: 10px; }}
        .subtitle {{ color: #666; margin-bottom: 30px; }}
        .card {{ 
            background: #1a1a1a; border: 1px solid #333;
            border-radius: 8px; padding: 20px; margin-bottom: 20px;
        }}
        .stat {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #222; }}
        .stat-label {{ color: #888; }}
        .stat-value {{ font-weight: bold; }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
        .neutral {{ color: #eab308; }}
        .mood-emoji {{ font-size: 2em; text-align: center; padding: 20px; }}
        .bar {{ height: 20px; background: #22c55e; border-radius: 4px; }}
        a {{ color: #3b82f6; }}
        .footer {{ text-align: center; margin-top: 40px; color: #555; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>🎮 git-mood report</h1>
    <p class="subtitle">Repository: {self.repo_name} | {self.total_commits} commits over {self.days_analyzed} days</p>
    
    <div class="mood-emoji">{self.mood_emoji}</div>
    
    <div class="card">
        <h2>Summary</h2>
        <div class="stat"><span class="stat-label">Overall Mood</span><span class="stat-value {self._css_class()}">{self.overall_mood:+.2f}</span></div>
        <div class="stat"><span class="stat-label">Energy Level</span><span class="stat-value">{self.energy_level:.0%}</span></div>
        <div class="stat"><span class="stat-label">Stress Index</span><span class="stat-value {self._css_class()}">{self.stress_index:.0%}</span></div>
        <div class="stat"><span class="stat-label">Peak Hour</span><span class="stat-value">{self.peak_hour}:00</span></div>
        <div class="stat"><span class="stat-label">Most Active Day</span><span class="stat-value">{self.peak_day}</span></div>
        <div class="stat"><span class="stat-label">Night Owl Score</span><span class="stat-value">{self.night_owl_score:.0%}</span></div>
        <div class="stat"><span class="stat-label">Weekend Warrior</span><span class="stat-value">{self.weekend_warrior_score:.0%}</span></div>
    </div>
    
    <div class="footer">
        Made with 😊 by <a href="https://github.com/PHclaw/git-mood">PHclaw/git-mood</a>
    </div>
</body>
</html>"""
    
    def _css_class(self) -> str:
        if self.overall_mood > 0.2:
            return "positive"
        elif self.overall_mood < -0.2:
            return "negative"
        return "neutral"
