import os
import subprocess
import shutil
import requests
import json
import pandas as pd
import numpy as np
import time
import datetime
import pyotp
from selenium import webdriver
from pandas import DataFrame
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from requests_toolbelt import MultipartEncoder

# pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)


def determine_google_drive():
    """判断谷歌驱动版本是否和谷歌浏览器版本一致"""
    # 谷歌浏览器可执行文件的完整路径
    chrome_path = r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

    # 指定谷歌驱动目标位置
    # folder_path = os.getcwd()
    folder_path = os.path.split(os.path.realpath(__file__))[0]
    # 驱动名称
    file_name = 'chromedriver.exe'
    # 路径拼接
    file_path = os.path.join(folder_path, file_name)

    if os.path.exists(file_path):
        # 获取chromedriver.exe版本(谷歌浏览器驱动)
        result = subprocess.run([file_path, '--version'], capture_output=True, text=True)
        driverversion = '.'.join(result.stdout.strip().split(' ')[1].split('.')[:-1])

        # 获取chrome.exe版本(谷歌浏览器)
        command = f'wmic datafile where name="{chrome_path}" get Version /value'
        result_a = subprocess.run(command, capture_output=True, text=True, shell=True)
        output = result_a.stdout.strip()
        chromeversion = '.'.join(output.split('=')[1].split('.')[0:3])

        # 判断版本是否一致，不一致就重新下载
        if driverversion != chromeversion:
            # 使用ChromeDriverManager安装ChromeDriver，并获取驱动程序的路径
            download_driver_path = ChromeDriverManager().install()
            # 复制文件到目标位置
            shutil.copy(download_driver_path, folder_path)
        # else:
        #     print("版本一致，无需重新下载！")

    else:
        download_driver_path = ChromeDriverManager().install()
        shutil.copy(download_driver_path, folder_path)

    return file_path


def determine_edge_drive():
    # EDGE浏览器可执行文件的完整路径
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

    # 指定EDGE驱动目标位置
    # folder_path = os.getcwd()
    folder_path = os.path.split(os.path.realpath(__file__))[0]
    # 驱动名称
    file_name = 'msedgedriver.exe'
    # 路径拼接
    file_path = os.path.join(folder_path, file_name)

    if os.path.exists(file_path):
        # 获取msedgedriver.exe版本(EDGE浏览器驱动)
        result = subprocess.run([file_path, '--version'], capture_output=True, text=True)
        driverversion = result.stdout.strip().split(' ')[3].strip()
        # 获取chrome.exe版本(谷歌浏览器)
        powershell = f'(Get-Item -Path "{edge_path}").VersionInfo.FileVersion'
        p = subprocess.Popen(["powershell.exe", powershell], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL,
                             shell=True)
        edgeversion = p.communicate()[0].decode().strip()
        if driverversion != edgeversion:
            download_driver_path = EdgeChromiumDriverManager().install()
            shutil.copy(download_driver_path, folder_path)
    else:
        download_driver_path = EdgeChromiumDriverManager().install()
        shutil.copy(download_driver_path, folder_path)
    return file_path


def sql_var_fill(sql, **kwargs):
    for ver in kwargs:
        sql = sql.replace('${%s}' % ver, kwargs[ver])
    return sql


class Csv2Sql:
    def __init__(self, csv_file_name, table_name=None):
        self.create_sql = None
        self.insert_sql = None
        self.cols = []
        self.csv_file_name = csv_file_name
        if table_name:
            self.table_name = table_name
        else:
            self.table_name = '.'.join([i for i in csv_file_name.split('.') if i != 'csv'])
        self.df = pd.read_csv(csv_file_name, dtype=str)
        self.cols = self.df.columns.values

    def get_create_table_sql(self, dorp_table=True):
        sql = ''
        drop_sql = 'drop table if exists %s;\n' % self.table_name
        if dorp_table:
            sql = sql + drop_sql
        col_sql = ','.join([i + ' string' for i in self.cols])
        create_sql = "CREATE table if not exists %s \n(%s);\n" % (
            self.table_name, col_sql)
        sql = sql + create_sql
        return sql

    def get_insert_sql(self, truncate=True, code_len=60000):
        sql = ''
        truncate_sql = 'truncate table %s;\n' % self.table_name
        if truncate:
            sql = sql + truncate_sql
        insert_sql = "insert into %s values" % self.table_name
        insert_sql_code_len = len(insert_sql.encode())
        insert_values = []
        for row in self.df.iterrows():
            vals = "'" + "','".join([str(i) for i in row[1].values]) + "'"
            insert_values.append("(%s)\n" % vals)
        para_code_len = insert_sql_code_len
        para = []
        for i in insert_values:
            row_code_len = len(i.encode()) + 1
            para_code_len = para_code_len + row_code_len
            if para_code_len >= code_len:
                para_sql = insert_sql + ','.join(para) + ";"
                sql = sql + para_sql
                para = [i]
                para_code_len = insert_sql_code_len + row_code_len
            else:
                para.append(i)
        if para:
            para_sql = insert_sql + ','.join(para) + ";"
            sql = sql + para_sql
        return sql


class Olap:
    class LoginError(Exception):
        pass

    def __init__(self, driver_path=None, token=None):
        # self.base_url = 'http://10.210.14.51/yh-olap-web'
        self.base_url = 'http://prokong.bigdata.yonghui.cn/yh-olap-web'
        self.driver_path = driver_path
        self.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        self.orgCode = 'bgzt000004'
        self.ContentType = 'application/json'
        if token:
            self.token = token
        self.token_get_time = None
        self.username = None

    def wait_for_page_load(self, driver, timeout=10):
        try:
            WebDriverWait(driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete")
        except TimeoutException:
            print("页面加载超时")

    def login(self, username, password, otp_key):
        try:
            option = webdriver.EdgeOptions()
            option.add_argument("--headless")
            option.add_argument("--disable-gpu")
            service = EdgeService(determine_edge_drive())
            driver = webdriver.Edge(service=service, options=option)
        except:
            option = webdriver.ChromeOptions()
            option.add_argument('headless')
            if self.driver_path:
                service = ChromeService(executable_path=self.driver_path)
            else:
                service = ChromeService(determine_google_drive())
            driver = webdriver.Chrome(service=service, options=option)
        driver.get(
            'http://o2o-support-prod.idaas-cas.gw.yonghui.cn/cas/login?service=http://10.208.134.65:32766/redirect?redirectUrl=http://bigdata.yonghui.cn/#/')
        self.wait_for_page_load(driver)
        username_text = driver.find_element(by=By.ID, value="username")
        username_text.send_keys(username)
        password_text = driver.find_element(by=By.ID, value="password")
        password_text.send_keys(password)
        submit_button = driver.find_element(by=By.NAME, value="submit")
        submit_button.click()
        self.wait_for_page_load(driver)
        cookies = driver.get_cookie('token')
        if cookies:
            token = cookies.get('value')
            if token.find('JSESSIONID') != -1:
                self.token = token
        else:
            for i in range(5):
                try:
                    dynamic_password_text = driver.find_element(by=By.ID, value="dynamicPassword")
                    break
                except:
                    time.sleep(1)
                    pass
            dynamic_password = pyotp.TOTP(otp_key).now()
            dynamic_password_text.send_keys(dynamic_password)
            for i in range(5):
                try:
                    dynamic_password_text = driver.find_element(by=By.ID, value="dynamicPassword")
                    dynamic_password = pyotp.TOTP(otp_key).now()
                    dynamic_password_text.send_keys(dynamic_password)
                except:
                    break
            cookies = driver.get_cookie('token')
            self.token = cookies.get('value')
        self.token_get_time = datetime.datetime.now()
        self.username = username
        driver.quit()

    def __run_sql(self, sql, Engine='impala', execute_configs={}, **kwargs):
        """运行sql"""
        engines = {'hive': {'engines': '1', 'dsId': 1},
                   'impala': {'engines': '2', 'dsId': 2},
                   'ck': {'engines': '3', 'dsId': 14004}}
        engine = engines[Engine]['engines']
        dsId = engines[Engine]['dsId']
        sql = sql_var_fill(sql, **kwargs)
        url = self.base_url + '/sql/manager/runSql'
        data = {'engine': engine, 'dsId': dsId, 'sql': sql, 'params': [], 'executeConfigs': execute_configs}
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        res = json.loads(requests.post(url=url, json=data, headers=headers).text)
        return res

    def __get_log_result(self, requestId):
        """查看运行结果"""
        url = self.base_url + '/sql/manager/getLogResult'
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        data = {'requestId': requestId}
        res = json.loads(requests.post(url=url, json=data, headers=headers).text)
        return res

    def __check_state(self, requestId):
        """查看运行结果"""
        url = self.base_url + '/sql/manager/checkState'
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        data = {'requestId': requestId}
        res = json.loads(requests.post(url=url, json=data, headers=headers).text)
        return res

    def __get_sql_result(self, requestId, page_size=200, page_no=1):
        url = self.base_url + '/sql/manager/getSqlResult'
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        data = {'requestId': requestId, 'pageSize': page_size, 'pageNo': page_no}
        res = json.loads(requests.post(url=url, json=data, headers=headers).text)
        return res

    def __create_download(self, requestId):
        """创建下载任务"""
        url = self.base_url + '/approval/createSkipDownloadOrder'
        data = {'requestId': requestId}
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        res = json.loads(requests.put(url=url, json=data, headers=headers).text)
        return res

    def __dlorder_detail(self, id):
        """查看下载任务明细"""
        url = self.base_url + '/approval/detail?approvalId=%s' % id
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        res = json.loads(requests.get(url=url, headers=headers).text)
        return res

    def __refresh(self, id):
        url = self.base_url + '/download/refresh?downloadId=%s' % id
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        data = data = {'downloadId': id}
        res = json.loads(requests.post(url=url, json=data, headers=headers).text)
        return res

    def __download_excel(self, requestId, ex_name=None):
        """下载excel"""
        if not ex_name:
            ex_name = requestId
        url = self.base_url + '/download/olapResult/%s' % requestId
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        res = requests.get(url=url, headers=headers)
        with open("%s.xlsx" % ex_name, 'wb') as f:
            f.write(res.content)

    def execute(self, sql, Engine='impala', execute_configs={}, get_log_sleep_time=None, **kwargs):
        sqlls = sql.split('\n')
        for s in sqlls:
            if s.strip()[0:6].lower() == 'select':
                state_fun = self.__get_log_result
                sleep_time = 1
                break
            elif s.strip()[0:4].lower() == 'drop':
                state_fun = self.__check_state
                sleep_time = 1
                break
            elif s.strip() == '':
                continue
            elif s.strip()[0:2].lower() == '--':
                continue
            else:
                state_fun = self.__check_state  # 忘记为什么用这个了 可能是hive创建表需要用
                sleep_time = 5
                break
        run_sql_req = self.__run_sql(sql, Engine=Engine, execute_configs=execute_configs, **kwargs)
        if run_sql_req.get('success'):
            ex_data = run_sql_req.get('data')
            executeId = ex_data.get('executeId')
        else:
            raise ValueError(run_sql_req.get('message'))
        while True:
            log_result_res = state_fun(executeId)
            if log_result_res.get('success'):
                data = log_result_res.get('data')
                if data.get('finish') == 'ok':
                    if data.get('errMsg'):
                        if data.get('errMsg').lower().find('error') != -1:
                            raise ValueError(data.get('errMsg'))
                        else:
                            break
                    elif data.get('error') > 0:
                        raise ValueError(log_result_res.get('message'))
                    else:
                        break
                elif data.get('finish') == 'run':
                    if get_log_sleep_time:
                        sleep_time = get_log_sleep_time
                    time.sleep(sleep_time)
                else:
                    raise ValueError(log_result_res.get('message'))
            else:
                raise ValueError(log_result_res.get('message'))
        return executeId

    def result(self, executeId, page_size=200, page_no=1):
        sql_result_res = self.__get_sql_result(requestId=executeId, page_size=page_size, page_no=page_no)
        if sql_result_res.get('success'):
            data = sql_result_res.get('data')
            cols = data.get('columnNameList')
            rows = data.get('list')
            df = DataFrame(rows, columns=cols)
        else:
            raise ValueError(sql_result_res.get('message'))
        df = df.replace('null', np.nan)
        return df

    def download_excel(self, executeId, ex_name=None, retry_num=0, interval=5):
        create_download_res = self.__create_download(executeId)
        if create_download_res.get('success'):
            data = create_download_res.get('data')
            if data.get('state') == 0:
                dlid = data.get('id')
            else:
                raise ValueError(data.get('stateName'))
        else:
            raise ValueError(create_download_res.get('message'))
        while True:
            dlorder_detail_res = self.__dlorder_detail(dlid)
            if dlorder_detail_res.get('success'):
                data = dlorder_detail_res.get('data')
                if data.get('taskState') == 1:  # 数据生成中 一秒后刷新
                    time.sleep(interval)
                elif data.get('taskState') == 2:  # 数据已生成 结束循环
                    requestId = data.get('requestId')
                    break
                elif data.get('taskState') == 3:  # 数据已生成 结束循环
                    retry_num -= 1
                    if retry_num < 0:
                        raise ValueError(data.get('taskStateName'))
                    else:
                        self.__refresh(dlid)
                        time.sleep(interval)
                else:
                    time.sleep(interval)
            else:
                raise ValueError(dlorder_detail_res.get('message'))
        if not ex_name:
            ex_name = executeId
        self.__download_excel(requestId, ex_name=ex_name)
        filename = '%s.xlsx' % executeId
        return filename

    def result_all(self, executeId):
        filename = self.download_excel(executeId=executeId)
        df = pd.read_excel(filename)
        os.remove(filename)
        return df

    def move_to_trash(self, *path):
        """

        :param path: csv文件路径
        :return:
        """
        url = 'https://prokongbigdata.yonghui.cn/yh-olap-web/hdfs/moveToTrash'
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        data = {'path': list(path)}
        res = json.loads(requests.post(url=url, json=data, headers=headers).text)
        return res

    def get_hdfs_dir(self, dir_path):
        url = 'https://prokongbigdata.yonghui.cn/yh-olap-web/hdfs/getHdfsDir'
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': self.ContentType}
        data = {'pageNum': 1, 'path': dir_path}
        res = json.loads(requests.post(url=url, json=data, headers=headers).text)
        return res

    def upload_single_file(self, hdfs_path, filepath):
        url = 'https://prokongbigdata.yonghui.cn/yh-olap-web/file/uploadSingleFile'
        file_name = os.path.basename(filepath)
        data = MultipartEncoder(
            fields={'hdfsPath': hdfs_path, 'file': (file_name, open(filepath, 'rb'), 'text/csv')})
        headers = {'User-Agent': self.UserAgent, 'token': self.token, 'orgCode': self.orgCode,
                   'Content-Type': data.content_type}
        result = requests.post(url=url, data=data, headers=headers)
        return json.loads(result.text)

    def invalidata_metadata(self, database_table):
        self.__run_sql('INVALIDATE METADATA %s' % database_table)
