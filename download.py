from PyQt5.QtCore import QThread, pyqtSignal
import os
import time
import requests

class downloadThread(QThread):
    download_signal = pyqtSignal(int,str,str) # 进度 下载速度 剩余时间

    def __init__(self, url,callback,path=None):
        super(downloadThread, self).__init__()
        if(path == None):
            # 默认下载地址为./temp
            self.download_path = os.path.join(os.getcwd(), "temp")
            # 文件名为下载地址中的文件名
            self.download_filename = url.split("/")[-1]
            # 合并
            self.download_file_path = os.path.join(self.download_path, self.download_filename)

            # if os.path.exists(self.download_path):
            #     os.remove(self.download_path)
        else:
            self.download_file_path = path

        self.url = url
        self.callback = callback

        # 绑定线程结束事件
        self.finished.connect(self.finish)

    def run(self):
        if self.url == None or self.url == "":
            self.res = False
            return
        self.res = self.download(self.url)
       

    def download(self,url):
        # try:
            start_time = time.time()
            r = requests.get(url, stream=True)
            with open(self.download_file_path, 'wb') as f:
                total_length = int(r.headers.get('content-length'))
                # 获取百分比 并调用回调函数
                for chunk in r.iter_content(chunk_size=10 * 1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        per = int(f.tell() * 100 / total_length)  #进度百分比
                        downloaded = f.tell() / 1024 / 1024 # 已下载文件大小
                        size = total_length / 1024 / 1024 #文件大小MB

                        rate = downloaded/ ( time.time() - start_time) # 下载速率

                        runtime = int((size - downloaded)/rate)
                       
                        downloaded = round(downloaded,2)
                        rate = round(rate,2)
                        size = round(size,2)
                        runtime = round(runtime,2)

                        self.download_signal.emit(per, str(rate), str(runtime))
                               
            return True
        # except Exception as e:
        #     return False

    def finish(self):
        if self.res == True:
            self.callback(self.download_file_path)
        else:
            self.callback(None)