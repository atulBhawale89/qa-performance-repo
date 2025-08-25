from datetime import datetime, timezone, timedelta

def ts_to_ist_formatted(ts_seconds, fmt="%d-%b-%Y %I:%M:%S %p"):
    if ts_seconds is None:
        return None
    ist = timezone(timedelta(hours=5, minutes=30))
    dt = datetime.fromtimestamp(int(ts_seconds), ist)
    return dt.strftime(fmt)
