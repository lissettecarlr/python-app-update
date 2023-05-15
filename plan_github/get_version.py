import json
import requests
import threading
from loguru import logger

class versionCheckThread(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        with open('plan_github/config.json', 'r') as f:
            config = json.load(f)
            self.repository = config["repository"]
        self.url = "https://api.github.com/repos/{}/releases/latest".format(self.repository)

    @staticmethod
    def get_version_current():
        with open('plan_github/version.json', 'r') as f:
            config = json.load(f)
            version_current = config["current"]
        return version_current
    
    @staticmethod
    def set_version_current(version_current):
        with open('plan_github/version.json', 'w') as f:
            json.dump({"current":version_current},f)
        

    def run(self):
        #print(self.url)
        try:
            response = requests.get(self.url)
        except Exception as e:
            logger.warning(e)
            self.callback(None,None,None)
        
        if response.status_code != 200:
            logger.warning(e)
            self.callback(None,None,None)
        
        version_current = versionCheckThread.get_version_current()
        version_upcoming  = response.json()['tag_name'].replace('"', '').strip()
        release_info = response.json()
        assets = release_info['assets']
        version_url = assets[0]['browser_download_url']

        #logger.debug("当前版本：{}".format(version_current))
        self.callback(version_current,version_upcoming,version_url)

   








