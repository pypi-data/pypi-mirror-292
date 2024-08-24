from datetime import datetime,timezone


def actual_time():
    now = datetime.now(timezone.utc)
    return now.isoformat()

