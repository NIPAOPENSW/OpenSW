import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QByteArray, QXmlStreamReader, QXmlStreamWriter, QTextStream
from opensw_v3 import Ui_MainWindow as form_main
import requests, json
import xmltodict
import xml.etree.ElementTree as elemTree
import pandas as pd
from datetime import datetime
import time
# form_main = uic.loadUiType("opensw_v1.ui")[0]

class main_window(QMainWindow, QWidget, form_main):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
    
    def initUI(self):
        self.setupUi(self)
        # self.vertification_key_check_box.toggled.connect(self.vertification_toggled)
        self.send_button.clicked.connect(self.send_button_clicked)
        self.clear_button.clicked.connect(self.clear_button_clicked)
        # self.vertification_text.setEnabled(False)
        self.get_radiobutton.toggled.connect(self.get_toggled)
        self.get_radiobutton.setChecked(True)

        self.csv_radio_button.clicked.connect(self.result_method)
        self.html_radio_button.clicked.connect(self.result_method)
        self.json_radio_button.clicked.connect(self.result_method)
        self.text_radio_button.clicked.connect(self.result_method)
        self.xml_radio_button.clicked.connect(self.result_method)

        self.csv_array_1.setEnabled(False)
        self.csv_array_2.setEnabled(False)
        self.csv_array_3.setEnabled(False)
        self.csv_array_4.setEnabled(False)
        self.csv_array_5.setEnabled(False)

        self.download_button.clicked.connect(self.download_button_clicked)
        # self.text_radio_button.setChecked(True)
        
    # def vertification_toggled(self, checked):
    #     if checked:
    #         self.vertification_text.setEnabled(True)
    #     else:
    #         self.vertification_text.setEnabled(False)
    #         self.vertification_text.setText("")

    def get_toggled(self, checked):
        global SIGNAL_GET, SIGNAL_POST
        if checked:
            SIGNAL_GET = True
            SIGNAL_POST = False
        else:
            SIGNAL_GET = False
            SIGNAL_POST = True
    
    def result_method(self):
        global SIGNAL_CSV, SIGNAL_XML, SIGNAL_TEXT, SIGNAL_JSON, SIGNAL_HTML
        SIGNAL_CSV = False
        SIGNAL_XML = False
        SIGNAL_TEXT = False
        SIGNAL_JSON = False
        SIGNAL_HTML = False
        if self.csv_radio_button.isChecked():
            SIGNAL_CSV = True
            self.csv_array_1.setEnabled(True)
            self.csv_array_2.setEnabled(True)
            self.csv_array_3.setEnabled(True)
            self.csv_array_4.setEnabled(True)
            self.csv_array_5.setEnabled(True)
        elif self.html_radio_button.isChecked():
            SIGNAL_HTML = True
            self.csv_array_1.setEnabled(False)
            self.csv_array_2.setEnabled(False)
            self.csv_array_3.setEnabled(False)
            self.csv_array_4.setEnabled(False)
            self.csv_array_5.setEnabled(False)
        elif self.json_radio_button.isChecked():
            SIGNAL_JSON = True
            self.csv_array_1.setEnabled(False)
            self.csv_array_2.setEnabled(False)
            self.csv_array_3.setEnabled(False)
            self.csv_array_4.setEnabled(False)
            self.csv_array_5.setEnabled(False)
        elif self.text_radio_button.isChecked():
            SIGNAL_TEXT = True
            self.csv_array_1.setEnabled(False)
            self.csv_array_2.setEnabled(False)
            self.csv_array_3.setEnabled(False)
            self.csv_array_4.setEnabled(False)
            self.csv_array_5.setEnabled(False)
        elif self.xml_radio_button.isChecked():
            SIGNAL_XML = True
            self.csv_array_1.setEnabled(False)
            self.csv_array_2.setEnabled(False)
            self.csv_array_3.setEnabled(False)
            self.csv_array_4.setEnabled(False)
            self.csv_array_5.setEnabled(False)
    
    def send_button_clicked(self):
        global req_header
        
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
        global contents
        if SIGNAL_GET == True:
            if req_url.endswith("?"):
                req_url += params
            else:
                req_url += "?" + params
            start_time = time.time()
            resp = requests.get(headers = headers, url = req_url)
        else:
            start_time = time.time()
            resp = requests.post(headers = headers, url = req_url, data = params)
        
        # print(ET.fromstring(resp.text).text)
        # print(params)
        # xml_str = xmltodict.unparse(json.loads(resp.text), pretty = True)
        # self.result_json.setText(xml_str)
        if SIGNAL_TEXT:
            self.result_json.setText(resp.text)
            contents = resp.text
            end_time = time.time()

        elif SIGNAL_JSON:
            # xml_str = xmltodict.unparse(json.loads(resp.text), pretty = True)
            # self.result_json.setText(xml_str)
            try:
                json_str = json.loads(resp.text)
                json_text = json.dumps(json_str, indent=4, ensure_ascii=False)
                self.result_json.setText(json_text)
                contents = json_text
                end_time = time.time()
            except:
                try:
                    xml_str = xmltodict.parse(resp.text)
                    json_str = json.loads(json.dumps(xml_str))
                    json_text = json.dumps(json_str, indent=4, ensure_ascii=False)
                    self.result_json.setText(json_text)
                    contents = json_text
                    end_time = time.time()
                except:
                    self.result_json.setText(resp.text)
                    contents = resp.text
                    end_time = time.time()
                # print(json_str)
        elif SIGNAL_XML:
            try:
                byteArray = QByteArray()
                xmlReader = QXmlStreamReader(resp.text)
                xmlWriter = QXmlStreamWriter(byteArray)
                xmlWriter.setAutoFormatting(True)
                while (not xmlReader.atEnd()):
                    xmlReader.readNext()
                    if (not xmlReader.isWhitespace()):
                        xmlWriter.writeCurrentToken(xmlReader)

                stream = QTextStream(byteArray)
                stream.setCodec(xmlWriter.codec())
                self.result_json.setText(stream.readAll())
                contents = stream.readAll()
                end_time = time.time()
            except:
                self.result_json.setText(resp.text)
                contents = resp.text
                end_time = time.time()
        
        elif SIGNAL_HTML:
            try:
                byteArray = QByteArray()
                xmlReader = QXmlStreamReader(resp.text)
                xmlWriter = QXmlStreamWriter(byteArray)
                xmlWriter.setAutoFormatting(True)
                while (not xmlReader.atEnd()):
                    xmlReader.readNext();
                    if (not xmlReader.isWhitespace()):
                        xmlWriter.writeCurrentToken(xmlReader)

                stream = QTextStream(byteArray)
                stream.setCodec(xmlWriter.codec())
                self.result_json.setText(stream.readAll())
                contents = stream.readAll()
                end_time = time.time()
            except:
                self.result_json.setText(resp.text)
                contents = resp.text
                end_time = time.time()
        
        elif SIGNAL_CSV:
            try:
                try:
                    xml_str = xmltodict.parse(resp.text)
                    json_str = json.loads(json.dumps(xml_str))

                except:
                    json_str = json.loads(resp.text)
                    # json_text = json.dumps(json_str, indent=4, ensure_ascii=False)
                csv_param_1 = self.csv_array_1.toPlainText()
                csv_param_2 = self.csv_array_2.toPlainText()
                csv_param_3 = self.csv_array_3.toPlainText()
                csv_param_4 = self.csv_array_4.toPlainText()
                csv_param_5 = self.csv_array_5.toPlainText()

                if csv_param_1 == '':
                    df = pd.json_normalize(json_str)
                elif csv_param_2 == '':
                    df = pd.json_normalize(json_str[csv_param_1])
                elif csv_param_3 == '':
                    df = pd.json_normalize(json_str[csv_param_1][csv_param_2])
                elif csv_param_4 == '':
                    df = pd.json_normalize(json_str[csv_param_1][csv_param_2][csv_param_3])
                elif csv_param_5 == '':
                    df = pd.json_normalize(json_str[csv_param_1][csv_param_2][csv_param_3][csv_param_4])
                else:
                    df = pd.json_normalize(json_str[csv_param_1][csv_param_2][csv_param_3][csv_param_4][csv_param_5])

                self.result_csv.setRowCount(len(df.index))
                self.result_csv.setColumnCount(len(df.columns))
                self.result_csv.setHorizontalHeaderLabels(df.columns)

                for row_index, row in enumerate(df.index):
                    for col_index, column in enumerate(df.columns):
                        value = df.loc[row][column]
                        item = QTableWidgetItem(str(value))
                        self.result_csv.setItem(row_index, col_index, item)
                contents = df
                end_time = time.time()
            except:
                table = self.result_csv
                table.setColumnCount(1)
                table.setRowCount(1)
                table.setHorizontalHeaderLabels(["조회 결과"])
                table.setItem(0, 0, QTableWidgetItem("csv parameter 값을 확인해 주시기 바랍니다."))
                end_time = time.time()
        print(end_time - start_time)

    def download_button_clicked(self):
        global fname
        fname = QFileDialog.getExistingDirectory()
        file_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = fname + '/' + file_name
        if SIGNAL_TEXT:
            fname += ".txt"
            with open(fname, 'w', encoding = 'utf-8') as f:
                f.write(contents)
        elif SIGNAL_HTML:
            fname += ".html"
            with open(fname, 'w', encoding = 'utf-8') as f:
                f.write(contents)
        elif SIGNAL_JSON:
            fname += ".json"
            with open(fname, 'w', encoding = 'utf-8') as f:
                f.write(contents)
        elif SIGNAL_XML:
            fname += ".xml"
            with open(fname, 'w', encoding = 'utf-8') as f:
                f.write(contents)
        elif SIGNAL_CSV:
            fname += ".csv"
            contents.to_csv(fname, sep = ',', na_rep = "NaN", encoding = 'utf-8-sig')
    
    def clear_button_clicked(self):
        self.result_json.setText("")
        self.result_csv.setText("")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = main_window()
    sys.exit(app.exec_())