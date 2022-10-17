from telnetlib import EC
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import pandas as pd
import copy
from io import StringIO
from selenium.webdriver.support.wait import WebDriverWait

'''
class Settings():
    def __init__(self, login_url=r'http://class.seig.edu.cn:7001/sise/',
                 headers={"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'},
                 schedule_url ='http://class.seig.edu.cn:7001/sise/module/student_schedular/student_schedular.jsp',
                 book_url="http://class.seig.edu.cn:7001/sise/module/student_teaching_material_view/teaching_material_view.jsp",
                 result_file_name='./file/21网工6班无课表.csv',
                 check_member=None,  #限制人员名单
                 **login_data,
                 ):

        option = webdriver.FirefoxOptions()
        option.add_argument("--disable-gpu")
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--no-sandbox')
        option.add_argument('--headless')
        self.browser=webdriver.Firefox(options=option)
        self.headers={"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
        self.login_url='http://class.seig.edu.cn:7001/sise/'
        self.schedule_url='http://class.seig.edu.cn:7001/sise/module/student_schedular/student_schedular.jsp'#课表url
        self.book_url = "http://class.seig.edu.cn:7001/sise/module/student_teaching_material_view/teaching_material_view.jsp"#课本url
        self.result_file_name=result_file_name
        self.pattern_schedule=re.compile('(?<=\s{1})\d+')#匹配有课周
        self.pattern_person_info=re.compile('\s*学号:\s\d*|姓名:\s\w*|专业:.*')#匹配个人信息
        self.pandas_columns=['周一','周二','周三','周四','周五','周六','周日',]
        self.pandas_index=['1 - 2 节09:00 - 10:20','3 - 4 节10:40 - 12:00','5 - 6 节12:30 - 13:50','7 - 8 节14:00 - 15:20','9 - 10 节15:30 - 16:50','11 - 12 节17:00 - 18:20','13 - 14 节19:00 - 0:20','15 - 16 节20:30 - 21:50',]
        self.pandas_books_columns=["课程名称","ISBN(书号)","教材名称","版次","作者","出版社","原价","是否拥有"]
        self.full_week={i for i in range(1,19)}#满课集合
        if len(login_data)==0:
            self.login_data={'username':"1",'password':'1'}
        else:
            self.login_data=login_data
        self.book_data=[]#存放课本信息
        self.book_num=0#课本数量
        self.schedule_re=pd.DataFrame([["" for i in range(7)] for j in range(8)])#学生课表
        self.person_info={"姓名":'',"学号":'',"专业":""}#学生信息
        self.before_data=[]#之前的无课表信息
        self.now_data=[]#现在正在录入学生的无课表
        self.final_data=pd.DataFrame([["" for i in range(7)] for j in range(8)])#最后输出的无课表
        self.statues=''
        self.check_member=check_member
'''
'''
class sise_auto_gen_free_schedule(Settings):
    def __init__(self,**login_data):
        Settings.__init__(self,**login_data)
'''
class siseAutoGetInfomations():
    def __init__(self,
                 result_file_name='./file/21网工6班无课表.csv',
                 check_member=None,
                 **login_data):

        option = webdriver.FirefoxOptions()
        option.add_argument("--disable-gpu")
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--no-sandbox')
        option.add_argument('--headless')
        self.browser = webdriver.Firefox(options=option)

        self.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
        self.login_url = 'http://class.seig.edu.cn:7001/sise/'
        self.schedule_url = 'http://class.seig.edu.cn:7001/sise/module/student_schedular/student_schedular.jsp'  # 课表url
        self.book_url = "http://class.seig.edu.cn:7001/sise/module/student_teaching_material_view/teaching_material_view.jsp"  # 课本url
        self.pattern_schedule = re.compile('(?<=\s{1})\d+')  # 匹配有课周
        self.pattern_person_info = re.compile('\s*学号:\s\d*|姓名:\s\w*|专业:.*')  # 匹配个人信息
        self.pandas_columns = ['周一', '周二', '周三', '周四', '周五', '周六', '周日', ]
        self.pandas_index = ['1 - 2 节09:00 - 10:20', '3 - 4 节10:40 - 12:00', '5 - 6 节12:30 - 13:50',
                             '7 - 8 节14:00 - 15:20', '9 - 10 节15:30 - 16:50', '11 - 12 节17:00 - 18:20',
                             '13 - 14 节19:00 - 0:20', '15 - 16 节20:30 - 21:50', ]
        self.pandas_books_columns = ["课程名称", "ISBN(书号)", "教材名称", "版次", "作者", "出版社", "原价", "是否拥有"]
        if len(login_data) == 0:
            self.login_data = {'username': "1", 'password': '1'}
        else:
            self.login_data = login_data
        self.result_file_name = result_file_name
        self.book_data = []  # 存放课本信息
        self.book_num = 0  # 课本数量
        self.schedule_re = pd.DataFrame([["" for i in range(7)] for j in range(8)])  # 学生课表
        self.person_info = {"姓名": '', "学号": '', "专业": ""}  # 学生信息
        self.before_data = []  # 之前的无课表信息
        self.now_data = []  # 现在正在录入学生的无课表
        self.final_data = pd.DataFrame([["" for i in range(7)] for j in range(8)])  # 最后输出的无课表
        self.statues = ''#返回状态
        self.check_member = check_member#限制名单
        self.work_mode=2#无课表已存在名单获取方式。1win：.csv文件，2linux：数据库。int
        self.timeout=3

    #判断页面是否正常加载
    def page_statues(self,url=None,timeout=None):#headers=None,time_delay=2):
        if url==None:
            url=self.login_url
        if timeout==None:
            timeout=self.timeout
        self.browser.implicitly_wait(timeout)
        try:
            self.browser.get(url)
        except:
            self.statues = '学生信息管理系统维护中或服务器网络连接超时，请稍后再试'
            return 1
        return 0

    #登录信息的输入
    #data={"username":,"password":}
    def login(self,url=None,usernameId="username",passwordId="password",submitId="Submit",**data):
        if url==None:
            url=self.login_url
        if len(data)!=0:
            login_data=data
        else:
            login_data=self.login_data
        if self.page_statues(url):
            return 1
        #self.browser.get(url)
        username_post = self.browser.find_element(By.ID, usernameId)
        username_post.send_keys(login_data['username'])
        password_post = self.browser.find_element(By.ID, passwordId)
        password_post.send_keys(login_data['password'])
        login_button = self.browser.find_element(By.ID, submitId)
        login_button.submit()
        return 0

    #密码正确性检查
    def login_check(self,url=None,error_title='系统错误提示页面',timeout=None):
        if url==None:
            url=self.login_url
        if timeout==None:
            timeout=self.timeout
        #等待重定向
        wait = WebDriverWait(self.browser, timeout)
        try:
            wait.until(lambda driver: driver.current_url != url)
        except:
            self.statues = '服务器网路错误,请稍后重试'
            return 1
        if self.browser.title == error_title:
            self.statues = '账号或密码错误,请检查后重试'
            return 1
        return 0


    #获取课本数据
    #schoolyear=2021(年份) semester=1(1或2)
    def get_book_data(self,schoolyear=None,semester=None,url=None):
        if url==None:
            url=self.book_url
        if schoolyear and semester:
            url=f'{url}?schoolyear={schoolyear}&semester={semester}'

        if self.page_statues(url):
            self.statues="年份或学期错误!"
            return 1

        html=self.browser.page_source
        bs=BeautifulSoup(html,'lxml')
        book_raw=bs.findAll(name='td',attrs={"align": "center", "class": "font12","valign": "top"})
        book_data_temp=[]
        for e in book_raw:
            book_data_temp.append(e.get_text().replace("-",""))
        self.book_num=int(len(book_data_temp)/13)
        book_data_temp = np.array(book_data_temp).reshape(self.book_num, 13)
        book_data_temp=np.delete(book_data_temp,[0,2,9,11,12], axis=1)
        self.book_data=pd.DataFrame(book_data_temp)
        self.book_data.columns=self.pandas_books_columns
        return 0

    #获取课本、个人数据
    #get_schedule_f=1，获取课表;=0不获取
    #get_person_info_f=1，获取姓名学号；=0不获取
    def get_schedule_data(self,schoolyear=None,semester=None,url=None,get_schedule_f=1,get_person_info_f=1):
        if url==None:
            url=self.schedule_url
        if schoolyear and semester:
            url=f'{url}?schoolyear={schoolyear}&semester={semester}'

        if self.page_statues(url):
            self.statues = "年份或学期错误!"
            return 1

        html=self.browser.page_source
        bs = BeautifulSoup(html, 'lxml')
        if get_schedule_f:
            schedule_data_raw= bs.findAll(name='td', attrs={"align": "left", "class": "font12", 'width': "10%", "valign": "top"})
            for e in schedule_data_raw:
                self.now_data.append(e.get_text())
        if get_person_info_f:
            person_info= bs.find('span', {"class": 'style16', }).get_text()
            person_info=': '.join(re.findall(self.pattern_person_info,person_info)).split(": ")
            temp=copy.deepcopy(person_info)
            person_info = dict(zip(temp[0::2], temp[1::2]))
            self.person_info=person_info
        return 0

    #限制人员检测
    def check_class(self,check_member=None):
        if check_member==None:
            check_member=self.check_member
        if check_member and self.person_info["姓名"] not in check_member:
            self.statues = f'{self.person_info["姓名"]}不是该无课表的成员，请联系制作者添加或检查班级/组织码是否输错'
            return 1
        return 0

    #已创建无课表获取，若空则创建一个
    def get_exist_data(self,text=None,f=None):
        if f==None:
            f=self.work_mode

        if f==1:
            try:
                self.before_data= pd.read_csv(self.result_file_name, encoding='gbk', index_col=0)
            except:
                self.before_data= pd.DataFrame([["" for i in range(7)] for j in range(8)])
        if f==2:
            if self.strings_to_dataframe(text).empty:
                return 1
        return 0

    #重复录入检测
    def exist_name_check(self):
       if self.person_info['姓名'] in self.before_data.iloc[0,6]:
           self.statues=f'{self.person_info["姓名"]}已录入该无课表，无需重复录入'
           return 1
       return 0

    #无课表录入
    def deal_data(self):
        pattern=self.pattern_schedule
        full_week={i for i in range(1, 19)}
        name=self.person_info["姓名"]
        now_data=self.now_data
        final_data= pd.DataFrame([["" for i in range(7)] for j in range(8)])
        before_data=self.before_data
        for i in range(56):
            temp=now_data[i]
            j=i//7
            k=i%7
            if ')' in temp:
                schedule_week = re.findall(pattern, temp)
                schedule_week = list(map(int, schedule_week))
                schedule_week = set(schedule_week)
                re_week=''
                re_week_none = full_week - schedule_week
                if re_week_none!=set():
                    re_week = f'{name}{str(re_week_none)};'
            else:
                re_week = f'{name};'
            if re_week:
                final_data.iloc[j, k] = f'{str(before_data.iloc[j, k])}\n{str(re_week)}'
            else:
                final_data.iloc[j, k] = f'{str(before_data.iloc[j, k])}'
            self.final_data=final_data

    #获取我的课表
    def get_my_schedule(self):
        my_schedule=pd.DataFrame([["" for i in range(7)] for j in range(8)])
        for i in range(56):
            temp = self.now_data[i]
            j=i//7
            k=i%7
            my_schedule.iloc[j, k]=temp
        my_schedule.index=self.pandas_index
        my_schedule.columns = self.pandas_columns
        self.schedule_re=my_schedule

    #无课表数据输出
    def out_data(self,f=None):
        if f==None:
            f=self.work_mode
        if f==1:
            self.final_data.index = self.pandas_index
            self.final_data.columns = self.pandas_columns
            self.final_data.to_csv(self.result_file_name, encoding='gbk', mode='w')
        self.statues=f'{self.person_info["姓名"]}的无课表录入成功！'
        self.browser.quit()

    #无课表录入
    def run_input_free_schedule(self,text=None,schoolyear=None,semester=None,check_member=None,**data):
        if self.login(**data):
            return 1
        if self.login_check():
            return 1
        if self.get_schedule_data(schoolyear,semester):
            return 1
        if self.check_class(check_member):
            return 1
        self.get_exist_data(text)
        if self.exist_name_check():
            return 1
        self.deal_data()
        self.out_data()
        return 0

    #获取课本
    def run_book(self,schoolyear=None,semester=None,**data):
        if self.login(**data):
            return 1
        if self.login_check():
            return 1
        self.get_book_data(schoolyear,semester)
        return 0
    #获取课表
    def run_schedule(self,schoolyear=None,semester=None,**data):
        if self.login(**data):
            return 1
        if self.login_check():
            return 1
        if self.get_schedule_data(schoolyear,semester):
            return 1
        self.get_my_schedule()
        return 0

    def strings_to_dataframe(self, strings):
        try :
            re= pd.read_csv(StringIO(strings), sep=",", index_col=0)
            self.before_data=re.astype(str)
        except:
            return pd.DataFrame()
        return re

    def dataframe_to_strings(self,dataframe):
        try:
            temp = StringIO(dataframe.to_csv())
        except:
            return 1
        return temp.read()




'''
#流程：
    前端：
        1用户输入username,password
        2检查输入是否合法
        3点击提交
        4根据学号查找数据库该人若已录入
            结束
        5将username，password提交到后端
            后端ing
        6得到后端返回结果
    后端：
        1获取前端传进的username，password
        2login_url若不否可加载
            返回
        3进入login_url，username，password若不正确
            返回
        4进入课表页
        5抓取课表数据、个人信息。
        5.1检查是否为我班同学
        6生产数据
        7写入最终文件
        8将学号姓名配对加入已完成名单
            返回
'''
#数据：
    #无头浏览器
    #访问头
    #login_url
    #target_url
    #csv_name
    #username,password
    #pattern_schedule
    #pattern_person_info
    #pandas_columns
    #pandas_index
