import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from opensw_v1 import Ui_MainWindow as form_main
import requests, json
import xmltodict
# form_main = uic.loadUiType("opensw_v1.ui")[0]

class main_window(QMainWindow, QWidget, form_main):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
    
    def initUI(self):
        self.setupUi(self)
        self.vertification_key_check_box.toggled.connect(self.vertification_toggled)
        self.send_button.clicked.connect(self.send_button_clicked)
        self.vertification_text.setEnabled(False)
        self.get_radiobutton.toggled.connect(self.get_toggled)
        self.get_radiobutton.setChecked(True)

        
    def vertification_toggled(self, checked):
        if checked:
            self.vertification_text.setEnabled(True)
        else:
            self.vertification_text.setEnabled(False)
            self.vertification_text.setText("")

    def get_toggled(self, checked):
        global SIGNAL_GET, SIGNAL_POST
        if checked:
            SIGNAL_GET = True
            SIGNAL_POST = False
        else:
            SIGNAL_GET = False
            SIGNAL_POST = True
    
    def send_button_clicked(self):
        global api_key, req_header
        
        # 인증키 부분
        if self.vertification_key_check_box.isChecked():
            api_key = self.vertification_text.toPlainText()
        else:
            api_key = ""
        
        # Request 헤더 부분
        if self.header_text.toPlainText() != "":
            headers = self.header_process(self.header_text.toPlainText())

        # URL 부분
        if self.url_text.toPlainText() != "":
            req_url = self.url_text.toPlainText()

        # Parameter 부분
        if self.parameter_text.toPlainText() != "":
            params = self.params_process(self.parameter_text.toPlainText())
        
        self.run(headers, req_url, params)
        
    def header_process(self, str):
        headers = {}
        input_header = str.split("\n")
        for each_header in input_header:
            tmp = each_header.split("=")
            headers[tmp[0]] = tmp[1]
        return headers

    def params_process(self, str):
        if SIGNAL_POST == True:
            params = {}
            input_params = str.split("\n")
            for each_params in input_params:
                tmp = each_params.split("=")
                params[tmp[0]] = tmp[1]
        else:
            params = str.replace("\n", "&")
        return params
    
    def run(self, headers, req_url, params):
        if SIGNAL_GET == True:
            if req_url.endswith("?"):
                req_url += params
            else:
                req_url += "?" + params
            resp = requests.get(headers = headers, url = req_url)
            # resp = requests.get(url = req_url)
        else:
            resp = requests.post(headers = headers, url = req_url, data = params)
        
        # print(ET.fromstring(resp.text).text)
        # print(params)
        # xml_str = xmltodict.unparse(json.loads(resp.text), pretty = True)
        # self.result_text.setText(xml_str)
        self.result_text.setText(resp.text)

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = main_window()
    sys.exit(app.exec_())