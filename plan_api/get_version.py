import json
import requests
import threading

class versionCheckThread(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        with open('plan_api/config.json', 'r') as f:
            config = json.load(f)
            self.id = config["id"]
            self.url = config["url"]

    def run(self):
        try:
            response = requests.get(self.url + self.id)
            if response.status_code == 200:
                result  = json.loads(response.text)["data"]
        except:
            result = None
        version_current = result["versionCurrent"]
        version_upcoming = result["versionUpcoming"]
        version_url = result["versionUrl"]
        self.callback(version_current,version_upcoming,version_url)

   