
import os
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

USERNAME = "prasadthosar"

query = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
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

response = requests.post(
    "https://api.github.com/graphql",
    headers={
        "Authorization": f"Bearer {os.environ['GH_TOKEN']}"
    },
    json={
        "query": query,
        "variables": {"username": USERNAME}
    },
    timeout=30,
)
response.raise_for_status()
payload = response.json()

if payload.get("errors"):
    raise RuntimeError(payload["errors"])

user = payload["data"]["user"]
if user is None:
    raise RuntimeError("GitHub user not found")

weeks = user["contributionsCollection"][
    "contributionCalendar"
]["weeks"]

daily = {
    date.fromisoformat(day["date"]): day["contributionCount"]
    for week in weeks
    for day in week["contributionDays"]
}

# Group contributions into seven-day periods.
days = sorted(daily)
start = days[0]
end = days[-1]

labels = []
counts = []

current = start
while current <= end:
    period_end = min(current + timedelta(days=6), end)
    total = sum(
        daily.get(current + timedelta(days=i), 0)
        for i in range((period_end - current).days + 1)
    )
    labels.append(current)
    counts.append(total)
    current = period_end + timedelta(days=1)

fig, ax = plt.subplots(figsize=(12, 3.5))

fig.patch.set_facecolor("#0D1117")
ax.set_facecolor("#0D1117")

ax.plot(
    labels,
    counts,
    color="#00C9A7",
    linewidth=2.5,
)
ax.fill_between(
    labels,
    counts,
    color="#00C9A7",
    alpha=0.15,
)

ax.set_title(
    "GitHub Contribution Activity",
    color="white",
    fontsize=16,
    pad=20,
)

ax.tick_params(colors="#8B949E")
ax.grid(alpha=0.12)
ax.set_ylabel("Contributions / 7 days", color="#8B949E")

for spine in ax.spines.values():
    spine.set_visible(False)

fig.autofmt_xdate()
fig.tight_layout()

os.makedirs("dist", exist_ok=True)
fig.savefig(
    "dist/contribution-line-chart.svg",
    format="svg",
    facecolor=fig.get_facecolor(),
    bbox_inches="tight",
)
plt.close(fig)
