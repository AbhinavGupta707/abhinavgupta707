#!/usr/bin/env python3
"""Generate a GitHub-style 4-axis activity overview cross-radar SVG.

Fetches contribution-type breakdown for a user via GraphQL, then renders
a Tokyo-Night-themed SVG that matches the look of GitHub's native
'Activity overview' chart (commits / code review / issues / pull requests).
"""
import json
import os
import sys
from urllib.request import Request, urlopen

USERNAME = os.environ.get("USERNAME", "AbhinavGupta707")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = os.environ.get("OUTPUT", "assets/activity-radar.svg")

QUERY = """
query($user: String!) {
  user(login: $user) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
    }
  }
}
"""

req = Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"user": USERNAME}}).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "activity-radar-builder",
    },
)
with urlopen(req, timeout=30) as resp:
    data = json.load(resp)

if "errors" in data:
    sys.exit(f"GraphQL error: {data['errors']}")

stats = data["data"]["user"]["contributionsCollection"]
commits = stats["totalCommitContributions"]
prs = stats["totalPullRequestContributions"]
issues = stats["totalIssueContributions"]
reviews = stats["totalPullRequestReviewContributions"]
total = commits + prs + issues + reviews or 1

def pct(x: int) -> int:
    return round(100 * x / total)

c, p, i, r = pct(commits), pct(prs), pct(issues), pct(reviews)

# Canvas: 480 wide, 320 tall, center (240, 160)
# Arm lengths chosen so the longest data line stays inside the labels
CX, CY = 240, 160
ARM_H = 150   # horizontal arm (commits left, issues right)
ARM_V = 105   # vertical arm   (review up,    PRs down)

commits_x = CX - int(c / 100 * ARM_H)
issues_x  = CX + int(i / 100 * ARM_H)
review_y  = CY - int(r / 100 * ARM_V)
prs_y     = CY + int(p / 100 * ARM_V)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 320" width="480" height="320" role="img" aria-label="Activity overview: {c}% commits, {r}% code review, {i}% issues, {p}% pull requests">
  <defs>
    <linearGradient id="armGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#bb9af7"/>
      <stop offset="100%" stop-color="#7dcfff"/>
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" fill="#1a1b26" rx="10"/>

  <!-- gridlines (faint cross showing scale) -->
  <line x1="{CX - ARM_H}" y1="{CY}" x2="{CX + ARM_H}" y2="{CY}" stroke="#414868" stroke-width="1"/>
  <line x1="{CX}" y1="{CY - ARM_V}" x2="{CX}" y2="{CY + ARM_V}" stroke="#414868" stroke-width="1"/>

  <!-- ticks at 50% along each arm -->
  <circle cx="{CX - ARM_H // 2}" cy="{CY}" r="1.5" fill="#414868"/>
  <circle cx="{CX + ARM_H // 2}" cy="{CY}" r="1.5" fill="#414868"/>
  <circle cx="{CX}" cy="{CY - ARM_V // 2}" r="1.5" fill="#414868"/>
  <circle cx="{CX}" cy="{CY + ARM_V // 2}" r="1.5" fill="#414868"/>

  <!-- data arms (from center to each percentage point) -->
  <line x1="{CX}" y1="{CY}" x2="{commits_x}" y2="{CY}" stroke="url(#armGrad)" stroke-width="3" stroke-linecap="round"/>
  <line x1="{CX}" y1="{CY}" x2="{issues_x}"  y2="{CY}" stroke="url(#armGrad)" stroke-width="3" stroke-linecap="round"/>
  <line x1="{CX}" y1="{CY}" x2="{CX}" y2="{review_y}"  stroke="url(#armGrad)" stroke-width="3" stroke-linecap="round"/>
  <line x1="{CX}" y1="{CY}" x2="{CX}" y2="{prs_y}"     stroke="url(#armGrad)" stroke-width="3" stroke-linecap="round"/>

  <!-- data points -->
  <circle cx="{commits_x}" cy="{CY}" r="5.5" fill="#bb9af7"/>
  <circle cx="{issues_x}"  cy="{CY}" r="5.5" fill="#bb9af7"/>
  <circle cx="{CX}" cy="{review_y}"  r="5.5" fill="#bb9af7"/>
  <circle cx="{CX}" cy="{prs_y}"     r="5.5" fill="#bb9af7"/>

  <!-- center dot -->
  <circle cx="{CX}" cy="{CY}" r="3.5" fill="#c0caf5"/>

  <!-- Labels (axis name + percentage) -->
  <!-- top: Code review -->
  <text x="{CX}" y="35" text-anchor="middle" fill="#c0caf5" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="14" font-weight="500">Code review</text>
  <text x="{CX}" y="19" text-anchor="middle" fill="#7aa2f7" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="13" font-weight="600">{r}%</text>

  <!-- right: Issues -->
  <text x="405" y="{CY + 5}" text-anchor="start" fill="#c0caf5" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="14" font-weight="500">Issues</text>
  <text x="405" y="{CY - 12}" text-anchor="start" fill="#7aa2f7" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="13" font-weight="600">{i}%</text>

  <!-- bottom: Pull requests -->
  <text x="{CX}" y="290" text-anchor="middle" fill="#c0caf5" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="14" font-weight="500">Pull requests</text>
  <text x="{CX}" y="307" text-anchor="middle" fill="#7aa2f7" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="13" font-weight="600">{p}%</text>

  <!-- left: Commits -->
  <text x="75" y="{CY + 5}" text-anchor="end" fill="#c0caf5" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="14" font-weight="500">Commits</text>
  <text x="75" y="{CY - 12}" text-anchor="end" fill="#7aa2f7" font-family="-apple-system, ui-sans-serif, system-ui, Segoe UI, sans-serif" font-size="13" font-weight="600">{c}%</text>
</svg>
'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}: commits={c}%, review={r}%, issues={i}%, prs={p}%")
print(f"raw: commits={commits}, prs={prs}, issues={issues}, reviews={reviews}")
