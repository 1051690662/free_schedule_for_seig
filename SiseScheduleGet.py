import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import pandas as pd
import copy
#D:\小程序\自在校园\cloud\django-db43\school\api\
class Settings():
    def __init__(self,login_url=r'http://class.seig.edu.cn:7001/sise/',
                 headers={"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'},
                 browserdriver_path=r'./chromedriver.exe',
                 target_url = 'http://class.seig.edu.cn:7001/sise/module/student_schedular/student_schedular.jsp',
                 result_file_name='./file/21网工6班无课表.csv',
                 check_member=None,
                 **login_data,
    ):
        self.browserdriver_path=browserdriver_path
        option = webdriver.ChromeOptions()
        option.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        option.add_argument('headless')
        self.browser=webdriver.Chrome(service=Service(executable_path=self.browserdriver_path),chrome_options=option)
        self.headers=headers
        self.login_url=login_url
        self.target_url=target_url
        self.result_file_name=result_file_name
        self.pattern_schedule=re.compile('(?<=\s{1})\d+')#匹配有课周
        self.pattern_person_info=re.compile('\s*学号:\s\d*|姓名:\s\w*')#匹配个人信息
        self.pandas_columns=['周一','周二','周三','周四','周五','周六','周日',]
        self.pandas_index=['1 - 2 节09:00 - 10:20','3 - 4 节10:40 - 12:00','5 - 6 节12:30 - 13:50','7 - 8 节14:00 - 15:20','9 - 10 节15:30 - 16:50','11 - 12 节17:00 - 18:20','13 - 14 节19:00 - 0:20','15 - 16 节20:30 - 21:50',]
        self.full_week={i for i in range(1,19)}
        if len(login_data)==0:
            self.login_data={'username':"1",'password':'1'}
        else:
            self.login_data=login_data
        self.schedule_raw=[]
        self.person_info={"姓名":'',"学号":''}
        self.before_data=[]
        self.now_data=[]
        self.final_data=pd.DataFrame([["" for i in range(7)] for j in range(8)])
        self.statues=''
        self.ok_number=0
        self.check_member=check_member

class sise_auto_gen_free_schedule(Settings):
    def __init__(self,**login_data):
        Settings.__init__(self,**login_data)

    def page_statues(self,url=None,headers=None,time_delay=2):
        if url==None:
            url=self.login_url
        if headers==None:
            headers=self.headers
        try:
            req=requests.get(url,headers=headers,timeout=time_delay)
        except:
            self.statues='学生信息管理系统维护中，请稍后再试'
            return 1
        return 0

    def login(self,url=None,**data):
        if url==None:
            url=self.login_url
        if len(data)!=0:
            self.login_data=data
        self.browser.get(url)
        username_post = self.browser.find_element(By.ID, "username")
        username_post.send_keys(self.login_data['username'])
        password_post = self.browser.find_element(By.ID, 'password')
        password_post.send_keys(self.login_data['password'])
        login_button = self.browser.find_element(By.ID, 'Submit')
        login_button.submit()

    def login_check(self,target_title='系统错误提示页面'):
        html = self.browser.page_source
        bs = BeautifulSoup(html, 'lxml')
        check = bs.find('title').get_text()
        if check == target_title:
            self.statues='账号或密码错误,请检查后重试'
            return 1
        return 0

    def get_target_url_data(self,url=None):
        if url==None:
            url=self.target_url
        self.browser.get(url)
        html=self.browser.page_source
        bs = BeautifulSoup(html, 'lxml')
        now_data_raw= bs.findAll(name='td', attrs={"align": "left", "class": "font12", 'width': "10%", "valign": "top"})
        for e in now_data_raw:
            self.now_data.append(e.get_text())
        self.person_info= bs.find('span', {"class": 'style16', }).get_text()
        self.person_info=': '.join(re.findall(self.pattern_person_info,self.person_info)).split(": ")
        temp=copy.deepcopy(self.person_info)
        self.person_info=dict(zip(temp[0::2],temp[1::2]))

    def check_class(self,check_member=None):
       # class_name='陈碧英陈巧巧黄梓潆王宝旭何宇蓝梁奕梅梁银英吴佳琳131陈俊宇134陈景韬光201杨志成211林鑫锐257丁志远257曾鸿林257招俊权258蔡思浩258黄学霖258赵潇宇258钟镇伟259高龙龙259刘绍广259麦境浩260顾博文260孟令辉260吴紫诚261岑绍聪261陈星宇261邓奕峰261钟草民262高才元262黄钅监斌262刘洪丞262谭俊朗264林志杰264唐远飞264谢栎耿264张泽野263谭俊火263张星宇263张祥263许诺257丁钿260刘炜259谢彬'
        if check_member==None:
            check_member=self.check_member
        if check_member and self.person_info["姓名"] not in check_member:
            self.statues = f'{self.person_info["姓名"]}不是该无课表的成员，请联系制作者添加或检查班级/组织码是否输错'
            return 1
        return 0

    def get_exist_data(self):
        try:
            self.before_data= pd.read_csv(self.result_file_name, encoding='gbk', index_col=0)
        except:
            self.before_data= pd.DataFrame([["" for i in range(7)] for j in range(8)])


    def exist_name_check(self):
       if self.person_info['姓名'] in self.before_data.iloc[0,6]:
           self.statues=f'{self.person_info["姓名"]}已录入该无课表，无需重复录入'
           return 1
       return 0
        

    def deal_data(self):
        pattern=self.pattern_schedule
        full_week=self.full_week
        name=self.person_info["姓名"]
        for i in range(56):
            temp = self.now_data[i]
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
                self.final_data.iloc[j, k] = f'{str(self.before_data.iloc[j, k])}\n{str(re_week)}'
            else:
                self.final_data.iloc[j, k] = f'{str(self.before_data.iloc[j, k])}'


    def out_data(self):

        self.final_data.index = self.pandas_index
        self.final_data.columns = self.pandas_columns
        self.final_data.to_csv(self.result_file_name, encoding='gbk', mode='w')
        #self.ok_number = self.final_data.iloc[0, 6].count(";")
        self.statues=f'{self.person_info["姓名"]}的无课表录入成功！'
        self.browser.quit()

    def run(self):
        if self.page_statues():
            return
        self.login()
        if self.login_check():
            return
        self.get_target_url_data()
        if self.check_class():
            return
        self.get_exist_data()
        if self.exist_name_check():
            return
        self.deal_data()
        self.out_data()







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
