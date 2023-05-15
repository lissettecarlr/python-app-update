
from PyQt5.QtWidgets import  QApplication,QMainWindow,QStatusBar
from PyQt5.QtCore import QLockFile,QTimer,pyqtSignal,QObject
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon


import os
import sys
import queue
import time
import configparser

from ui_main import Ui_MainWindow
from download import downloadThread
import utils

#import plan_api as version
import plan_github as version

class Signal(QObject):
    button_pressed = pyqtSignal()

class main_windows(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.confg = self.get_config()
        self.ui_init()
        self.version_init()

    def ui_init(self):
        self.setWindowTitle('软件更新')
        self.setWindowIcon(QIcon('./assets/logo.png'))

        # 进度条初始化
        self.ui.progressBar.hide()
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0, 100)

        # 文本框初始化
        self.ui.textEdit.setReadOnly(True)
        self.text_queue = queue.Queue()

        # 底部消息
        self.status_bar=QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('久远赛高',5000) 

        # 界面更新定时器
        self.update_ui_timer = QTimer()
        self.update_ui_timer.timeout.connect(self.update_ui)
        self.update_ui_timer.start(1000)

        # 按键
        self.ui.button_1.setEnabled(True)
        self.ui.button_2.setEnabled(False)

        self.ui.button_1.clicked.connect(self.button_exit)
        self.ui.button_2.clicked.connect(self.button_update)

        self.button_2_signal = Signal()
        self.button_2_signal.button_pressed.connect(self.button_update)
      
        self.ui.button_1.setText("跳过(退出)")

    # 版本检测
    def version_init(self):
        # 进行版本检测
        self.print_text("版本检测：开始")
        version.versionCheckThread(self.version_check).start()
    
    # 版本检测的回调
    # version_current 当前版本
    # version_upcoming 最新版本
    # version_url 最新版本下载地址
    def version_check(self,version_current,version_upcoming,version_url):
        self.print_text("版本检测：结束")
        self.version_upcoming = version_upcoming
        print(version_current)
        if version_current != None:
            try:
                if(version_current < version_upcoming ):
                    self.update_label("发现新版本，可以进行更新",version_upcoming,version_current)
                    refuse_auto_download = False
                else:
                    self.update_label("已是最新版本，无需更新",version_upcoming,version_current)
                    return
            except:
                self.print_text("版本格式不匹配！，请根据版本号自行判断是否需要更新！","red")
                self.update_label("自行判断版本",version_upcoming,version_current)
                refuse_auto_download = True
        else:
           self.update_label("未检出到当前版本，自行决定是否更新",version_upcoming,"")    
           refuse_auto_download = True


        self.ui.button_2.setEnabled(True)
        self.new_version_url = version_url
        # 提取链接中的文件名
        self.new_version_name = self.new_version_url.split("/")[-1]
        self.new_version_path = os.path.join(os.getcwd(),"temp",self.new_version_name)

        if(self.confg["FLAG"]["AUTO_DOWNLOAD"] == "ON" and refuse_auto_download == False):
            self.button_2_signal.button_pressed.emit()
            #self.button_update()

    def update_ui(self):
        self.update_text()

    def update_text(self):
        while(self.text_queue.empty() == False):
            txt = self.text_queue.get()
            self.ui.textEdit.append(txt)
            self.ui.textEdit.moveCursor(self.ui.textEdit.textCursor().End)        

    # 更新底部状态显示
    def update_status(self,per:int,rate,time):
        status = "下载速率 {} MB/s    剩余时间 {}秒".format(rate,time)
        self.status_bar.showMessage(status,5000)
        if not self.ui.progressBar.isVisible():
            self.ui.progressBar.show()
        self.ui.progressBar.setValue(per)

    # 更新提示、新版本号，当前版本号
    def update_label(self,l1:str,l2:str,l3:str):
        self.ui.label_1.setText(l1)
        self.ui.label_2.setText(l2)
        self.ui.label_4.setText(l3)

    # 文本框显示输入
    def print_text(self,txt,color="black"):
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" => "
        if(color == "black"):
            txt = "<font color='black'>"+ t + txt +"<font>"
        elif(color == "red"):
            txt = "<font color='red'>"+ t + txt +"<font>"
        else:
            txt = t + txt
        self.text_queue.put(txt)

    def button_exit(self):
        self.close()

    def button_update(self):
        self.print_text("开始下载新版本软件")
        self.ui.button_2.setEnabled(False)

        self.download_thread = downloadThread(self.new_version_url,self.update_over,self.new_version_path)
        self.download_thread.download_signal.connect(self.update_status)
        self.download_thread.start()
       
    # 下载后的回调   
    def update_over(self,result):
        self.ui.button_2.setEnabled(True)
        if(result == None):
            self.print_text("下载失败！")
        else:
            self.print_text("下载完成！")
            # 如果有更新方法则进行版本修改
            if hasattr(version.versionCheckThread, "set_version_current"):
                version.versionCheckThread.set_version_current(self.version_upcoming)           
            self.extra(result)
            
    def get_config(self):
        try:
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "config.ini"))
            return config
        except:
            return None

    # 额外操作 (根据自己需求改写)  file_path 下载的文件路径
    def extra(self,file_path):
        # 是否需要解压缩
        if(self.confg["FLAG"]["AUTO_UPDATE_OVER_UNZIP"] == "ON"):
            utils.unzip_file_windows(file_path)
            pass
        # 是否关闭应用软件
        if(self.confg["FLAG"]["AUTO_UPDATE_OVER_CLOSE_APP"] == "ON"):
            #utils.close_software_windows("软件名")
            pass
        # 替换原软件
        if(self.confg["FLAG"]["AUTO_UPDATE_OVER_REPLACE"] == "ON"):
            #utils.replace_software_windows()
            pass
        # 打开软件
        if(self.confg["FLAG"]["AUTO_UPDATE_OVER_OPEN_APP"] == "ON"):
            #utils.start_soft_windows()
            pass
        # 关闭更新软件
        if(self.confg["FLAG"]["AUTO_UPDATE_OVER_CLOSE"] == "ON"):
            #self.close()
            pass


def main(sys):
    app= QApplication(sys.argv)
    #防止多开
    lockFile = QLockFile("./autoUpdate.app.lock")

    if lockFile.tryLock(2000):
        base = os.path.dirname(os.path.realpath(sys.argv[0]))
        file = open(base + '/assets/qss/style.qss',"r", encoding="utf-8")
        qss = file.read().replace("$DataPath",".")
        app.setStyleSheet(qss)
        # 界面
        win = main_windows()
        win.show()
        sys.exit(app.exec_())
    else:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("重复开启")
        msg_box.setText("请不要重复开启本软件，注意托盘区域")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.addButton("确定", QMessageBox.YesRole)
        msg_box.exec()
        sys.exit(-1)

if __name__ == '__main__':
    main(sys)
   