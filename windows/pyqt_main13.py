# 네이버영화 UI실행
import json
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from json import * # 검색 결과를 json 타입으로 받음
import sys
import urllib.request # URL openAPI 검색위함
from urllib.parse import quote
import webbrowser # 웹 브라우저 열기위한 패키지

class MyApp(QWidget) :
    
    def __init__(self) :
        super(MyApp, self).__init__()
        self.initUI()

    def initUI(self) :
        uic.loadUi('./windows/ui/navermovie.ui', self)
        self.setWindowIcon(QIcon('naver_icon.png'))
        
        # 시그널 연결
        self.btnSearch.clicked.connect(self.btnSearchClicked)
        self.txtSearch.returnPressed.connect(self.btnSearchClicked)
        self.tblResult.itemSelectionChanged.connect(self.tblResultSelected)
        self.show()
    
    def tblResultSelected(self) :
        selected = self.tblResult.currentRow()  # 현재 선택된 열의 index
        url = self.tblResult.item(selected, 2).text()
        webbrowser.open(url)



    def btnSearchClicked(self) :
        jsonResult = []
        totalResult = []
        keyword = 'movie'
        search_word = self.txtSearch.text()
        display_count = 50
        jsonResult = self.getNaverSearch(keyword, search_word, 1, display_count)
        # print(jsonResult)
        for post in jsonResult['items'] :
            totalResult.append(self.getPostDate(post))

        self.makeTable(totalResult)

    def getPostDate(self, post) :
        temp = []
        title = post['title']
        link = post['link']
        subtitle = post['subtitle']
        pubDate = post['pubDate']
        
        temp.append({'title' : title, 'pubDate' : pubDate, 'subtitle' : subtitle, 'link' : link})
        return temp

    def strip_tag(self, title) :
        ret = title.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('<b>', '').replace('</b>', '')
        return ret

    def makeTable(self, result) :
        self.tblResult.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tblResult.setColumnCount(3)
        self.tblResult.setRowCount(len(result)) # 50
        self.tblResult.setHorizontalHeaderLabels(['영화제목', '상영년도', '링크'])
        self.tblResult.setColumnWidth(0, 250)
        self.tblResult.setColumnWidth(1, 50)
        self.tblResult.setColumnWidth(2, 100)
        self.tblResult.setEditTriggers(QAbstractItemView.NoEditTriggers) #readonly  # 테이블 위젯 설정 끝

        i = 0
        for item in result : # 50번 반복
            title = self.strip_tag(item[0]['title'])
            subtitle = item[0]['subtitle']
            self.tblResult.setItem(i, 0, QTableWidgetItem(f'{title} / {subtitle}'))
            self.tblResult.setItem(i, 1, QTableWidgetItem(item[0]['pubDate']))
            self.tblResult.setItem(i, 2, QTableWidgetItem(item[0]['link']))
            i += 1


    # 핵심함수
    def getNaverSearch(self, keyword, search, start, display) :
        url = f'https://openapi.naver.com/v1/search/movie' \
              f'?query={quote(search)}&start={start}&display={display}'
        req = urllib.request.Request(url)

        # 인증추가
        req.add_header('X-Naver-Client-Id', 'zpEoYq2IeMvVJNgZcTNT')
        req.add_header('X-Naver-Client-Secret', 'gH3wb4yB3f')
        res = urllib.request.urlopen(req) # request에 대한 response
        if res.getcode() == 200 :
            print('URL request success')
        else :
            print('URL request failed')

        ret = res.read().decode('UTF-8')
        if ret == None :
            return None
        else :
            return json.loads(ret)
            
if __name__ == '__main__' :
    app = QApplication(sys.argv)
    win = MyApp()
    app.exec_()