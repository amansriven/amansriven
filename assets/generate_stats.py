"""Builds assets/stats.svg: all-time contributions, current streak and longest streak.
Reads the contribution calendar from GitHub's GraphQL API; needs GITHUB_TOKEN in the env."""
from datetime import date, datetime, timedelta, timezone
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_assets import LINE, TEXT, MUTED, DIM, RED, OUT, card, prompt, style  # noqa: E402

USER = os.environ.get("GITHUB_USER", "amansriven")


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    body = json.load(urllib.request.urlopen(req))
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]


def contribution_days():
    """{date: count} for every day since the account was created.
    The API caps each contributionsCollection at one year, so walk it a year at a time."""
    created = gql("query($u:String!){user(login:$u){createdAt}}", u=USER)["user"]["createdAt"]
    start = datetime.fromisoformat(created.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    days = {}
    while start < now:
        end = min(start + timedelta(days=365), now)
        weeks = gql("""query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){
                        contributionsCollection(from:$f,to:$t){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}""",
                    u=USER, f=start.isoformat(), t=end.isoformat())
        for w in weeks["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[date.fromisoformat(d["date"])] = d["contributionCount"]
        start = end
    return days


def streaks(days):
    """-> (current, current_start, longest, longest_start, longest_end).
    A streak still counts as current if today has no contributions yet."""
    ordered = sorted(days)
    longest = (0, None, None)
    run, run_start = 0, None
    for d in ordered:
        if days[d]:
            run, run_start = run + 1, run_start or d
            if run > longest[0]:
                longest = (run, run_start, d)
        else:
            run, run_start = 0, None

    today = ordered[-1]
    d = today if days[today] else today - timedelta(days=1)
    current, current_start = 0, None
    while days.get(d):
        current, current_start = current + 1, d
        d -= timedelta(days=1)
    return current, current_start, *longest


def fmt(d, year=False):
    return d.strftime("%b %-d, %Y" if year else "%b %-d").lower() if d else "—"


def stats_svg(days):
    total = sum(days.values())
    current, cur_start, longest, long_start, long_end = streaks(days)
    first = min(days)
    W, H = 1200, 236
    col = W / 3
    cols = [
        (f"{total:,}", "total contributions", f"{fmt(first, True)} — present", TEXT),
        (f"{current}", "current streak", f"{fmt(cur_start)} — today" if current else "start one today", RED),
        (f"{longest}", "longest streak", f"{fmt(long_start)} — {fmt(long_end, True)}" if longest else "—", TEXT),
    ]
    body = []
    for i, (num, label, sub, color) in enumerate(cols):
        cx = col * i + col / 2
        unit = "" if i == 0 else f'<tspan font-size="20" font-weight="400" fill="{DIM}"> day{"" if num == "1" else "s"}</tspan>'
        body.append(f'''
  <text x="{cx:.0f}" y="146" text-anchor="middle" font-size="46" font-weight="700" fill="{color}">{num}{unit}</text>
  <text x="{cx:.0f}" y="180" text-anchor="middle" font-size="17" fill="{MUTED}">{label}</text>
  <text x="{cx:.0f}" y="208" text-anchor="middle" font-size="15" fill="{DIM}">{sub}</text>''')
        if i:
            body.append(f'<line x1="{col * i:.0f}" y1="98" x2="{col * i:.0f}" y2="{H - 30}" stroke="{LINE}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total:,} total contributions, {current} day current streak, {longest} day longest streak">
  {style()}
  {card(W, H)}
  {prompt("gh stats --all-time")}{"".join(body)}
</svg>'''


if __name__ == "__main__":
    days = contribution_days()
    open(f"{OUT}/stats.svg", "w").write(stats_svg(days))
    print(f"{sum(days.values())} contributions, streaks {streaks(days)[0]} current / {streaks(days)[2]} longest")
