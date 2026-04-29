# 🎮 git-mood

> Analyze your git commits to visualize your coding mood, energy, and work patterns over time.

Ever wondered if your commit messages reveal your emotional state? **git-mood** thinks they do.

```bash
pip install git-mood
cd your-project
git-mood analyze
```

## ✨ What It Does

- **Mood Detection** — Analyzes commit messages for sentiment (frustration, excitement, urgency, etc.)
- **Energy Heatmap** — Visualize when you're most productive
- **Work Pattern Analysis** — Late night commits? Weekend warrior? git-mood knows
- **Team Insights** — Compare moods across contributors
- **ASCII Art Report** — Beautiful terminal output, no GUI needed

## 🚀 Quick Start

```bash
# Install
pip install git-mood

# Analyze current repo
git-mood analyze

# Analyze specific repo
git-mood analyze /path/to/repo

# Show contributor breakdown
git-mood analyze --contributors

# Export as JSON
git-mood analyze --format json --output mood.json

# Generate HTML report
git-mood analyze --format html --output report.html
```

## 📊 Example Output

```
╔════════════════════════════════════════════════════════════════╗
║  🎮 git-mood report for: my-awesome-project                   ║
║  Analyzing 247 commits over 30 days                           ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Overall Mood: 😊 Positive (0.72)                             ║
║  Energy Level: 🔥 High (0.85)                                 ║
║  Stress Index: 😰 Low (0.21)                                  ║
║                                                                ║
║  Peak Hour: 22:00 (Night Owl! 🦉)                             ║
║  Most Active Day: Wednesday                                   ║
║  Night Owl Score: 45%                                         ║
║  Weekend Warrior: 12%                                         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

## 🎯 Mood Categories

| Mood | Signals | Score |
|------|---------|-------|
| 🎉 Excited | "shipped", "finally!", "🚀" | +1.0 |
| 😊 Happy | "works", "done", "added" | +0.5 |
| 😐 Neutral | "update", "change", "refactor" | 0.0 |
| 😤 Frustrated | "wtf", "hack", "stupid" | -0.5 |
| 😰 Stressed | "hotfix", "urgent", "asap" | -0.7 |

## 🔧 CLI Reference

```
git-mood analyze [path]           # Analyze repo (default: current dir)
  --days N                        # Last N days (default: 30)
  --format text|json|html         # Output format
  --output FILE                   # Write to file
  --contributors                  # Show per-author breakdown
  --no-emoji                      # Disable emoji
  --llm                           # Use LLM for deeper analysis

git-mood trend [path]             # Show mood trend over time
git-mood compare alice bob        # Compare two contributors
git-mood report [path] -o out.html  # Full HTML report
```

## 🧠 How It Works

1. **Commit Collection** — Uses `git log` to gather commits
2. **Sentiment Analysis** — Rule-based scoring of commit messages
3. **Pattern Detection** — Identifies work patterns (late night, weekend, etc.)
4. **Visualization** — ASCII charts in terminal

**No API keys required** for basic usage.

## 📦 Installation

```bash
# From PyPI (when published)
pip install git-mood

# From source
git clone https://github.com/PHclaw/git-mood.git
cd git-mood
pip install -e .
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- New mood detection rules
- LLM integration for nuanced analysis
- Web dashboard
- Team comparison features

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Made with 😊 by [PHclaw](https://github.com/PHclaw)**

*Because your git history tells a story worth reading* 📖