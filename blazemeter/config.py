import os
from requests.auth import HTTPBasicAuth

API_KEY = os.getenv("BLAZEMETER_API_KEY", "f50162ac4dc2e797ddf44672")
API_SECRET = os.getenv("BLAZEMETER_API_SECRET", "b25557098d5d87ab40c2e6aff8953e73604fcb03a9a52cb1e8e7b21977b00765f49e4dfb")
BASE_URL = "https://a.blazemeter.com/api/v4"
POLL_INTERVAL_SECONDS = 300

auth = HTTPBasicAuth(API_KEY, API_SECRET)