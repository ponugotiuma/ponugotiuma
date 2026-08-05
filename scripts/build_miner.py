import os
import requests
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

USERNAME = "ponugotiuma"
OUTPUT = "assets/contribution-miner.svg"

TOKEN = os.environ.get("GH_TOKEN")

if not TOKEN:
    raise RuntimeError("GH_TOKEN is missing")


# --------------------------------------------------
# 1. GET REAL GITHUB CONTRIBUTION DATA
# --------------------------------------------------

query = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
            contributionLevel
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": query,
        "variables": {"username": USERNAME}
    },
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
)

data = response.json()

if "errors" in data:
    raise RuntimeError(data["errors"])

weeks = data["data"]["user"]["contributionsCollection"][
    "contributionCalendar"
]["weeks"]


# --------------------------------------------------
# 2. CONVERT CONTRIBUTIONS INTO GAME MAP
# --------------------------------------------------

grid = []

for week in weeks:
    column = []

    for day in week["contributionDays"]:
        count = day["contributionCount"]

        if count == 0:
            level = 0
        elif count <= 2:
            level = 1
        elif count <= 5:
            level = 2
        elif count <= 10:
            level = 3
        else:
            level = 4

        column.append(level)

    grid.append(column)


# --------------------------------------------------
# 3. SVG SETTINGS
# --------------------------------------------------

CELL = 18
GAP = 3

WIDTH = len(grid) * (CELL + GAP) + 40
HEIGHT = 7 * (CELL + GAP) + 70

os.makedirs("assets", exist_ok=True)


# --------------------------------------------------
# 4. START SVG
# --------------------------------------------------

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{WIDTH}"
     height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}">

<style>

.title {{
    font-family: monospace;
    font-size: 18px;
    font-weight: bold;
}}

.cell {{
    rx: 4;
}}

.miner {{
    animation: mine 12s linear infinite;
}}

.pickup {{
    animation: collect 12s linear infinite;
}}

@keyframes mine {{

    0% {{
        transform: translate(0px, 0px);
    }}

    20% {{
        transform: translate(120px, 0px);
    }}

    40% {{
        transform: translate(240px, 0px);
    }}

    60% {{
        transform: translate(360px, 0px);
    }}

    80% {{
        transform: translate(480px, 0px);
    }}

    100% {{
        transform: translate(600px, 0px);
    }}
}}

@keyframes collect {{

    0%, 70% {{
        opacity: 1;
        transform: scale(1);
    }}

    75% {{
        opacity: 0;
        transform: scale(1.8);
    }}

    100% {{
        opacity: 0;
    }}
}}

</style>

<text x="20" y="25" class="title">
⛏️ UMA'S CONTRIBUTION MINING
</text>
"""


# --------------------------------------------------
# 5. DRAW REAL CONTRIBUTION GRID
# --------------------------------------------------

colors = {
    0: "#ebedf0",
    1: "#9be9a8",
    2: "#40c463",
    3: "#30a14e",
    4: "#216e39"
}

for x, column in enumerate(grid):

    for y, level in enumerate(column):

        px = 20 + x * (CELL + GAP)
        py = 40 + y * (CELL + GAP)

        svg += f"""
        <rect
            x="{px}"
            y="{py}"
            width="{CELL}"
            height="{CELL}"
            class="cell"
            fill="{colors[level]}"
        />
        """


# --------------------------------------------------
# 6. MINER
# --------------------------------------------------

svg += """
<g class="miner">

    <text x="20" y="135"
          font-size="22">
        👩‍🔧
    </text>

    <text x="20" y="155"
          font-size="18">
        🎒
    </text>

    <text x="45" y="155"
          font-size="18">
        ⛏️
    </text>

</g>
"""


# --------------------------------------------------
# 7. FINISH SVG
# --------------------------------------------------

svg += """
</svg>
"""

with open(OUTPUT, "w", encoding="utf-8") as file:
    file.write(svg)

print(f"Generated: {OUTPUT}")
