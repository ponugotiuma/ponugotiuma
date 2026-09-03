import os
import requests
from datetime import date, timedelta
from calendar import monthrange

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_USERNAME = os.environ["GITHUB_USERNAME"]

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    GRAPHQL_URL,
    json={
        "query": QUERY,
        "variables": {
            "login": GITHUB_USERNAME
        }
    },
    headers=headers
)

response.raise_for_status()

data = response.json()

if "errors" in data:
    raise Exception(data["errors"])

calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

total_contributions = calendar["totalContributions"]

days = []

for week in calendar["weeks"]:
    for contribution_day in week["contributionDays"]:
        days.append({
            "date": contribution_day["date"],
            "count": contribution_day["contributionCount"]
        })

days.sort(key=lambda x: x["date"])


# ---------------------------------------------------------
# CURRENT STREAK
# ---------------------------------------------------------

from datetime import datetime, timezone, timedelta

# GitHub contribution dates
contribution_dates = {
    date.fromisoformat(day["date"])
    for day in days
    if day["count"] > 0
}

# Use UTC because GitHub contribution dates are UTC-based
today = datetime.now(timezone.utc).date()

current_streak = 0

# Find the most recent contribution day that is
# today or yesterday.
if today in contribution_dates:
    streak_day = today

elif (today - timedelta(days=1)) in contribution_dates:
    streak_day = today - timedelta(days=1)

else:
    streak_day = None


# Count consecutive contribution days
if streak_day is not None:

    while streak_day in contribution_dates:

        current_streak += 1

        streak_day -= timedelta(days=1)

# ---------------------------------------------------------
# CURRENT MONTH CONTRIBUTIONS
# ---------------------------------------------------------

monthly_contributions = sum(
    day["count"]
    for day in days
    if date.fromisoformat(day["date"]).year == today.year
    and date.fromisoformat(day["date"]).month == today.month
)

month_name = today.strftime("%B %Y")


# ---------------------------------------------------------
# SVG GENERATION
# ---------------------------------------------------------

svg = f"""<svg width="1000" height="230"
xmlns="http://www.w3.org/2000/svg">

<rect width="1000" height="230" rx="20"
fill="#0d1117"
stroke="#30363d"/>

<!-- TITLE -->

<text x="500" y="40"
font-family="Arial, sans-serif"
font-size="18"
font-weight="bold"
fill="#ffffff"
text-anchor="middle">
GitHub Activity
</text>


<!-- DIVIDERS -->

<line x1="333" y1="65" x2="333" y2="200"
stroke="#30363d"/>

<line x1="666" y1="65" x2="666" y2="200"
stroke="#30363d"/>


<!-- TOTAL CONTRIBUTIONS -->

<text x="166" y="105"
font-family="Arial, sans-serif"
font-size="42"
font-weight="bold"
fill="#ffffff"
text-anchor="middle">
{total_contributions}
</text>

<text x="166" y="135"
font-family="Arial, sans-serif"
font-size="15"
fill="#8b949e"
text-anchor="middle">
Total Contributions
</text>

<text x="166" y="160"
font-family="Arial, sans-serif"
font-size="12"
fill="#6e7681"
text-anchor="middle">
All Time
</text>


<!-- CURRENT STREAK -->

<text x="500" y="105"
font-family="Arial, sans-serif"
font-size="42"
font-weight="bold"
fill="#ffffff"
text-anchor="middle">
🔥 {current_streak}
</text>

<text x="500" y="135"
font-family="Arial, sans-serif"
font-size="15"
fill="#8b949e"
text-anchor="middle">
Current Streak
</text>

<text x="500" y="160"
font-family="Arial, sans-serif"
font-size="12"
fill="#6e7681"
text-anchor="middle">
Consecutive Days
</text>


<!-- MONTHLY CONTRIBUTIONS -->

<text x="833" y="105"
font-family="Arial, sans-serif"
font-size="42"
font-weight="bold"
fill="#ffffff"
text-anchor="middle">
{monthly_contributions}
</text>

<text x="833" y="135"
font-family="Arial, sans-serif"
font-size="15"
fill="#8b949e"
text-anchor="middle">
Monthly Contributions
</text>

<text x="833" y="160"
font-family="Arial, sans-serif"
font-size="12"
fill="#6e7681"
text-anchor="middle">
{month_name}
</text>


<!-- FOOTER -->

<text x="500" y="205"
font-family="Arial, sans-serif"
font-size="10"
fill="#6e7681"
text-anchor="middle">
Automatically updated from GitHub contribution activity
</text>

</svg>
"""

with open("github-stats.svg", "w", encoding="utf-8") as file:
    file.write(svg)

print("GitHub statistics updated successfully.")
print(f"Total Contributions: {total_contributions}")
print(f"Current Streak: {current_streak}")
print(f"Monthly Contributions: {monthly_contributions}")
