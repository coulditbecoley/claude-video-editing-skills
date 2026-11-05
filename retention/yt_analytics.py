"""Read-only YouTube Analytics for @coulditbecoley, on Hermes' OAuth client with its own token.

  python yt_analytics.py auth                 one-time consent (opens the browser; you click Allow)
  python yt_analytics.py videos [days]        per-video views, engaged views, avg % viewed, avg duration
  python yt_analytics.py retention ID [ID..]  100-point retention curve per video -> raw/<ID>.retention.json
"""
import json, os, sys, datetime as dt
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CLIENT = os.path.expandvars(r"%LOCALAPPDATA%\hermes\google_client_secret.json")  # shared client, read only
TOKEN = os.path.expandvars(r"%LOCALAPPDATA%\yt-analytics\token.json")            # own token; Hermes' untouched
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly",
          "https://www.googleapis.com/auth/youtube.readonly"]
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")


def creds():
    c = Credentials.from_authorized_user_file(TOKEN, SCOPES) if os.path.exists(TOKEN) else None
    if c and c.expired and c.refresh_token:
        c.refresh(Request())
        open(TOKEN, "w").write(c.to_json())
    if not c or not c.valid:
        sys.exit("No valid token: run  python yt_analytics.py auth")
    return c


def report(**kw):
    today = dt.date.today()
    kw.setdefault("startDate", "2020-01-01")
    kw.setdefault("endDate", today.isoformat())
    return build("youtubeAnalytics", "v2", credentials=creds()).reports().query(ids="channel==MINE", **kw).execute()


def main(cmd, *args):
    if cmd == "auth":
        os.makedirs(os.path.dirname(TOKEN), exist_ok=True)
        c = InstalledAppFlow.from_client_secrets_file(CLIENT, SCOPES).run_local_server(port=0, open_browser=True)
        open(TOKEN, "w").write(c.to_json())
        ch = build("youtube", "v3", credentials=c).channels().list(part="snippet", mine=True).execute()
        print("authorized:", [i["snippet"]["title"] for i in ch.get("items", [])])
    elif cmd == "videos":
        days = int(args[0]) if args else 90
        start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
        r = report(startDate=start, dimensions="video", sort="-views", maxResults=50,
                   metrics="views,engagedViews,averageViewPercentage,averageViewDuration")
        for row in r.get("rows", []):
            print(*row, sep="\t")
    elif cmd == "retention":
        os.makedirs(RAW, exist_ok=True)
        for vid in args:
            r = report(dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}",
                       metrics="audienceWatchRatio,relativeRetentionPerformance")
            json.dump(r, open(os.path.join(RAW, f"{vid}.retention.json"), "w"), indent=1)
            print(vid, len(r.get("rows", [])), "points")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["help"]))
