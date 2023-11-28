from datetime import datetime
from http import client
from main_final_ui import Ui_MainWindow as form_main
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QByteArray 
from PyQt5.QtCore import QXmlStreamReader
from PyQt5.QtCore import QXmlStreamWriter
from PyQt5.QtCore import QTextStream
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from urllib import parse
import json
import pandas as pd
import sys
import time
import xmltodict


class Thread(QThread):
    
    
    response_received = pyqtSignal(tuple)
    def __init__(self, parent=None, headers = None, req_url = None, params = None, isGet = None):
        super().__init__(parent)
        self.headers = headers
        self.req_url = req_url
        self.params = params
        self.isGet = isGet
    
    
    def run(self):
        url, endpoint, isHttps = self.urlParser(self.req_url)
        try:
            if self.isGet == True:
                if endpoint.endswith("?"):
                    endpoint += self.params
                else:
                    endpoint += "?" + self.params

                # 인증 검사 관련한 시간 Check 부분                
                start_time = time.time()
                if isHttps is False:
                    connection = client.HTTPConnection(url, 80)
                else:
                    connection = client.HTTPSConnection(url, 443)
                print("API Call Time :", start_time)
                connection.request("GET", endpoint, headers=self.headers)
                resp = connection.getresponse()
                complete_time = time.time()
                print("Call End Time :", complete_time)
            else:
                if self.headers['Content-Type'] == 'application/json':
                    request_body = json.dumps(self.params).encode('utf-8')
                elif self.headers['Content-Type'] == 'application/x-www-form-urlencoded':
                    request_body = parse.urlencode(self.params).encode('utf-8')
                else:
                    request_body = self.params
                
                start_time = time.time()
                if isHttps is False:
                    connection = client.HTTPConnection(url, 80)
                else:
                    connection = client.HTTPSConnection(url, 443)
                print("API Call Time :", start_time)
                connection.request("POST", endpoint, request_body, headers=self.headers)
                resp = connection.getresponse()
                complete_time = time.time()
                print("Call End Time :", complete_time)
            
            data = resp.read()
            decoded_data = data.decode("utf-8")
            to_emit = (decoded_data, start_time, complete_time)
            self.response_received.emit(to_emit)
            
        except BaseException as e:
            to_emit = (e, -1, -1)
            self.response_received.emit(to_emit)
            
            
    def urlParser(self, url):
        isHttps = False
        if "https://" in url:
            url = url.replace("https://", "")
            isHttps = True
        elif "http://" in url:
            url = url.replace("http://", "")
            isHttps = False
        parts = url.split('/')
        host = '/'.join(parts[:1])
        path = '/' + '/'.join(parts[1:])
        return host, path, isHttps
    
class MainWindow(QMainWindow, QWidget, form_main):


    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()
    
    
    # 화면 구성 시 필요한 기능 설정
    def initUI(self):
        self.setupUi(self)
        self.send_button.clicked.connect(self.send_button_clicked)
        self.clear_button.clicked.connect(self.clear_button_clicked)
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


    # Radio Box 선택 기능(Get, Post)
    def get_toggled(self, checked):
        global SIGNAL_GET, SIGNAL_POST
        if checked:
            SIGNAL_GET = True
            SIGNAL_POST = False
        else:
            SIGNAL_GET = False
            SIGNAL_POST = True
    
    
    # CSV 선택 시 옵션 넣을 수 있는 부분 기능 설정
    def result_method(self):
        global SIGNAL_CSV, SIGNAL_XML, SIGNAL_TEXT, SIGNAL_JSON, SIGNAL_HTML
        SIGNAL_CSV = False
        SIGNAL_XML = False
        SIGNAL_TEXT = False
        SIGNAL_JSON = False
        SIGNAL_HTML = False
        # csv radio 버튼 클릭 시 옵션 부분 활성화
        if self.csv_radio_button.isChecked():
            SIGNAL_CSV = True
            self.csv_array_1.setEnabled(True)
            self.csv_array_2.setEnabled(True)
            self.csv_array_3.setEnabled(True)
            self.csv_array_4.setEnabled(True)
            self.csv_array_5.setEnabled(True)
        
        # csv radio 버튼 이외의 버튼 클릭 시 옵션 부분 비활성화
        elif self.html_radio_button.isChecked():
            SIGNAL_HTML = True
            self.csv_array_1.setEnabled(False)
            self.csv_array_2.setEnabled(False)
            self.csv_array_3.setEnabled(False)
            self.csv_array_4.setEnabled(False)
            self.csv_array_5.setEnabled(False)

        elif self.json_radio_button.isChecked():
            SIGNAL_JSON = True
            self.csv_array_1.setEnabled(True)
            self.csv_array_2.setEnabled(True)
            self.csv_array_3.setEnabled(True)
            self.csv_array_4.setEnabled(True)
            self.csv_array_5.setEnabled(True)

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
    
    
    # Send 버튼 클릭 시 기능 동작 부분
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
        
        try:
            self.run(headers, req_url, params)
        except:
            self.result_json.setText("결과값을 확인할 수 있는 형식을 지정해 주세요.")
    
    
    # Request 시 header 부분 parsing 기능
    def header_process(self, str):
        headers = {}
        input_header = str.split("\n")
        for each_header in input_header:
            tmp = each_header.split("=")
            headers[tmp[0]] = tmp[1]
        return headers


    # Request 시 parameter 부분 parsing 기능
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
    
    
    def start_api_request(self, headers, req_url, params, isGet):
        self.result_json.setText("서버와 통신중입니다.")
        self.api_thread = Thread(self, headers, req_url, params, isGet)
        self.api_thread.response_received.connect(self.handle_api_response)
        self.api_thread.start()
        
        
    def handle_api_response(self, response):
        resp, start_time, complete_time = response
        
        if complete_time == -1:
            self.result_json.setText("서버와의 연결이 불안합니다. 잠시 후 다시 시도해주세요.\n\n" + str(resp))
            return
        global contents
        # 확인할 결과값을 TEXT로 설정 시 화면에 보이는 기능
        if SIGNAL_TEXT:
            self.result_json.setText(resp)
            contents = resp
            end_time = time.time()

        # 확인할 결과값을 JSON로 설정 시 화면에 보이는 기능
        # Response 된 부분이 TEXT일 수도 있고, XML일 수도 있기 때문에, 2가지 경우를 JSON 형태로 변환
        elif SIGNAL_JSON:
            try:
                json_str = json.loads(resp)
                
                data_len = self.getJsonLen(json_str)
                
                print("Nums Of Data:", data_len)
                
                json_text = json.dumps(json_str, indent=4, ensure_ascii=False)
                self.result_json.setText(json_text)
                contents = json_text
                end_time = time.time()
                
                # 인증 검사 관련한 전체 Rows Count 부분
                
            except:
                try:
                    xml_str = xmltodict.parse(resp)
                    json_str = json.loads(json.dumps(xml_str))
                    
                    data_len = self.getJsonLen(json_str)
                
                    print("Nums Of Data:", data_len)
                    
                    json_text = json.dumps(json_str, indent=4, ensure_ascii=False)
                    self.result_json.setText(json_text)
                    contents = json_text
                    end_time = time.time()
                except:
                    self.result_json.setText("서버와의 연결이 불안정합니다. 잠시 후 다시 시도해주세요.")
                    contents = resp
                    end_time = time.time()

        # 확인할 결과값을 XML로 설정 시 화면에 보이는 기능
        elif SIGNAL_XML:
            try:
                byteArray = QByteArray()
                xmlReader = QXmlStreamReader(resp)
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
                self.result_json.setText(resp)
                contents = resp
                end_time = time.time()
        
        # 확인할 결과값을 HTML로 설정 시 화면에 보이는 기능
        # XML과 HTML은 거의 같은 형식을 띄고 있으므로, 기능상 차이는 없음
        elif SIGNAL_HTML:
            try:
                byteArray = QByteArray()
                xmlReader = QXmlStreamReader(resp)
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
                self.result_json.setText(resp)
                contents = resp
                end_time = time.time()
        
        # 확인할 결과값을 CSV로 설정 시 화면에 보이는 기능
        # XML 형태 또는 JSON 형태로 CSV 변환 기능
        elif SIGNAL_CSV:
            try:
                try:
                    xml_str = xmltodict.parse(resp)
                    json_str = json.loads(json.dumps(xml_str))

                except:
                    json_str = json.loads(resp)
                
                df = self.parsingCsv(json_str)
                
                data_len = len(df.index)
                self.result_csv.setRowCount(data_len)
                self.result_csv.setColumnCount(len(df.columns))
                self.result_csv.setHorizontalHeaderLabels(df.columns)
                
                print("Nums Of Data:", data_len)
                
                for row_index, row in enumerate(df.index):
                    for col_index, column in enumerate(df.columns):
                        value = df.loc[row][column]
                        item = QTableWidgetItem(str(value))
                        self.result_csv.setItem(row_index, col_index, item)
                self.result_csv.setEditTriggers(QAbstractItemView.NoEditTriggers)
                contents = df
                end_time = time.time()
            except:
                table = self.result_csv
                table.setColumnCount(1)
                table.setRowCount(1)
                table.setHorizontalHeaderLabels(["조회 결과"])
                table.setItem(0, 0, QTableWidgetItem("csv parameter 값을 확인해 주시기 바랍니다."))
                end_time = time.time()
        
        # 인증 검사 관련한 시간 Check 부분
        print("Total Elapsed Time:", end_time - start_time)
        print("Data Processing Time:", end_time - complete_time)

    
    def getJsonLen(self, json_str):
        csv_param_1 = self.csv_array_1.toPlainText()
        csv_param_2 = self.csv_array_2.toPlainText()
        csv_param_3 = self.csv_array_3.toPlainText()
        csv_param_4 = self.csv_array_4.toPlainText()
        csv_param_5 = self.csv_array_5.toPlainText()

        # data의 길이를 확인하기 위해 json data에서 특정 데이터가 위치하고 있는 depth까지 내려감
        if csv_param_1 == '':
            data_len = len(json_str)
        elif csv_param_2 == '':
            data_len = len(json_str[csv_param_1])
        elif csv_param_3 == '':
            data_len = len(json_str[csv_param_1][csv_param_2])
        elif csv_param_4 == '':
            data_len = len(json_str[csv_param_1][csv_param_2][csv_param_3])
        elif csv_param_5 == '':
            data_len = len(json_str[csv_param_1][csv_param_2][csv_param_3][csv_param_4])
        else:
            data_len = len(json_str[csv_param_1][csv_param_2][csv_param_3][csv_param_4][csv_param_5])
        return data_len

    
    def parsingCsv(self, json_str):
        csv_param_1 = self.csv_array_1.toPlainText()
        csv_param_2 = self.csv_array_2.toPlainText()
        csv_param_3 = self.csv_array_3.toPlainText()
        csv_param_4 = self.csv_array_4.toPlainText()
        csv_param_5 = self.csv_array_5.toPlainText()

        # 만약 CSV 형태로 변환 시 Optional한 부분이 있다면, 해당 부분으로 선택하는 기능
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
        return df
    
    # Request 실행 부분, Main 기능
    def run(self, headers, req_url, params):
        self.start_api_request(headers, req_url, params, SIGNAL_GET)
        

    # 조회된 결과값을 다운로드 할 수 있는 기능
    # 다운로드 시 폴더를 지정하여 선택하면, 현재 날짜로 저장됨(ex: 20230919_195829.json)
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


    # 결과값 초기화 부분
    # header, request url, parameter는 초기화 되지 않음    
    def clear_button_clicked(self):
        self.result_json.setText("")
        self.result_csv.setRowCount(0)
        self.result_csv.setColumnCount(0)
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
