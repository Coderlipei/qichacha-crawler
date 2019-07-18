import os
import requests
import pandas as pd
import openpyxl
import pickle
from bs4 import BeautifulSoup
from urllib import parse
from tqdm import tqdm_notebook
from typing import List
from glob import glob

def get_firm_uid(header_uids: dict, name_list: list) -> List[str]:
    
    # define the request url for getting company uid
    uid_request_url_list = ["https://www.qichacha.com/search?key={}"\
                            .format(parse.quote(name)) for name in name_list]
    uid_list = []
    for url in tqdm_notebook(uid_request_url_list):
        response = requests.get(url, headers=header_uids)
        soup = BeautifulSoup(response.content)
        uid_list.append(soup.select_one("#searchlist table.m_srchList "\
                                        "tbody#search-result tr.frtrt "\
                                        "td.checktd label.text-dark-lter "\
                                        "input").get('value'))
    return uid_list


def get_basic_info_soup(header_basic_info: dict, \
                        uid_list: list) -> List[BeautifulSoup]:
    
    # generate basic information request url
    basic_info_request_url_list = ["https://www.qichacha.com/firm_{}.html"\
                                   .format(uid) for uid in uid_list]
    
    basic_soup_list = []
    for url in tqdm_notebook(basic_info_request_url_list):
        response = requests.get(url, headers=header_basic_info)
        basic_soup_list.append(BeautifulSoup(response.content))
    
    return basic_soup_list

def parse_basic_info(basic_soup: BeautifulSoup) -> dict:
    
    info_dict = {}
    
    # a helper function 
    def _helper_fun_get_key_value_add_to_dict(_row, info_dict):
        _key = _row.find_all('td')[0].text.strip()
        _value = _row.find_all('td')[1].text.strip()
        info_dict[_key] = _value
        _key = _row.find_all('td')[2].text.strip()
        _value = _row.find_all('td')[3].text.strip()
        info_dict[_key] = _value
        return info_dict

    #
    # 主要信息 - 网站
    #
    
    panel = basic_soup.select_one("#company-top")
    info_dict['网站'] = panel.find('div', {'class': 'row'})\
                            .find('div', {'class': 'dcontent'})\
                            .find("div", {'class': 'row'})\
                            .find_all('a', href=True)[-1]\
                            .text.strip()
    
    #
    # 工商信息
    #
    panel = basic_soup.select_one("#base_div #Cominfo")
    table1 = panel.select("table")[0]
    table2 = panel.select("table")[1]
    
    # 法定代表人信息
    info_dict["法定代表人信息"] = table1.find("h2", {'class': 'seo font-20'}).text
    
    # 注册资本, 实缴资本
    _row = table2.find_all('tr')[0]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 经营状态, 成立日期
    _row = table2.find_all('tr')[1]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 统一社会信用代码, 纳税人识别号
    _row = table2.find_all('tr')[2]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 注册号, 组织机构代码
    _row = table2.find_all('tr')[3]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 企业类型, 所属行业
    _row = table2.find_all('tr')[4]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 核准日期, 登记机关
    _row = table2.find_all('tr')[5]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 所属地区, 英文名
    _row = table2.find_all('tr')[6]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 曾用名, 参保人数
    _row = table2.find_all('tr')[7]
    _key = _row.find_all('td')[0].text.strip()
    _value = ', '.join(_row.find_all('td')[1].text.strip().split())
    info_dict[_key] = _value
    _key = _row.find_all('td')[2].text.strip()
    _value = _row.find_all('td')[3].text.strip()
    info_dict[_key] = _value
    
    # 人员规模, 营业期限
    _row = table2.find_all('tr')[8]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 企业地址
    _row = table2.find_all('tr')[9]
    _key = _row.find_all('td')[0].text.strip()
    _value = _row.find_all('td')[1].text.strip().split('\n')[0]
    info_dict[_key] = _value
    
    # 经营范围
    _row = table2.find_all('tr')[10]
    _key = _row.find_all('td')[0].text.strip()
    _value = _row.find_all('td')[1].text.strip()
    info_dict[_key] = _value
    
    #
    # 对外投资
    #
    panel = basic_soup.select_one("#base_div #touzilist")
    # 对外投资数量
    if panel == None:
        info_dict["对外投资数量"] = 'None'
    else:
        info_dict["对外投资数量"] \
        = panel.select_one("div").find("span", {'class': 'tbadge'}).text
    
    #
    # 分支机构
    #
    panel = basic_soup.select_one("#base_div #branchelist")
    # 分支机构数量
    if panel == None:
        info_dict["分支机构数量"] = 'None'
    else:
        info_dict["分支机构数量"] \
        = panel.select_one("div").find("span", {'class': 'tbadge'}).text
    
    return info_dict

def get_dev_info_soup(header_dev_info: dict, \
                      uid_list: list) -> List[BeautifulSoup]:

    # generate header for getting development information
    header_dev_info_list = [dict(header_dev_info, \
                             **{"Referer": "https://www.qichacha.com/firm_{}.html"\
                                .format(uid)}) for uid in uid_list]

    # # generate the request url for getting development information
    dev_request_url_list = ["https://www.qichacha.com/company_getinfos?"\
                            "unique={0}&"\
                            "companyname={1}&"\
                            "tab=report".format(uid, parse.quote(name)) \
                            for uid, name in zip(uid_list, company_list)]
    
    soup_dev_info_list = []
    for header, url in tqdm_notebook(zip(header_dev_info_list, dev_request_url_list), \
                                     total=len(header_dev_info_list)):
        response = requests.get(url, headers=header)
        soup_dev_info_list.append(BeautifulSoup(response.content))
    
    return soup_dev_info_list

def parse_dev_info(dev_soup: BeautifulSoup) -> dict:
    
    info_dict = {}
    
    # a helper function 
    def _helper_fun_get_key_value_add_to_dict(_row, info_dict):
        _key = _row.find_all('td')[0].text.strip()
        _value = _row.find_all('td')[1].text.strip()
        info_dict[_key] = _value
        _key = _row.find_all('td')[2].text.strip()
        _value = _row.find_all('td')[3].text.strip()
        info_dict[_key] = _value
        return info_dict
    
    main_panel = dev_soup.find("div", {'id': 0})
    
    #
    # 企业基本信息
    #
    panel = main_panel.find_all('table')[0]
    
    # 注册号, 统一社会信用代码
    _row = panel.find_all('tr')[0]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 企业经营状态, 企业联系电话
    _row = panel.find_all('tr')[1]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 从业人数, 邮政编码
    _row = panel.find_all('tr')[2]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 有限责任公司本年度是否发生股东股权转让, 企业是否有投资信息或购买其他公司股权
    _row = panel.find_all('tr')[3]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 电子邮箱
    _row = panel.find_all('tr')[4]
    _key = _row.find_all('td')[0].text.strip()
    _value = _row.find_all('td')[1].text.strip()
    info_dict[_key] = _value
    
    # 企业通讯地址
    _row = panel.find_all('tr')[5]
    _key = _row.find_all('td')[0].text.strip()
    _value = _row.find_all('td')[1].text.strip().split('\n')[0]
    info_dict[_key] = _value
    
    #
    # 企业资产状况信息
    #
    
    # first we get the index of the table 
    table_names \
    = [name.text.strip().split()[0] \
       for name in main_panel.find_all('div')]
    table_index = table_names.index("企业资产状况信息")
    panel = main_panel.find_all('table')[table_index]
    
    # 资产总额, 所有者权益合计
    _row = panel.find_all('tr')[0]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 营业总收入, 利润总额
    _row = panel.find_all('tr')[1]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 营业总收入中主营业务收入, 净利润
    _row = panel.find_all('tr')[2]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 纳税总额, 负债总额
    _row = panel.find_all('tr')[3]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    #
    # 社保信息
    #

    # first we get the index of the table 
    table_names \
    = [name.text.strip().split()[0] \
       for name in main_panel.find_all('div')]
    table_index = table_names.index("社保信息")
    panel = main_panel.find_all('table')[table_index]
    
    # 城镇职工基本养老保险, 职工基本医疗保险
    _row = panel.find_all('tr')[0]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 生育保险, 失业保险
    _row = panel.find_all('tr')[1]
    info_dict = _helper_fun_get_key_value_add_to_dict(_row, info_dict)
    
    # 工伤保险
    _row = panel.find_all('tr')[2]
    _key = _row.find_all('td')[0].text.strip()
    _value = _row.find_all('td')[1].text.strip().split('\n')[0]
    info_dict[_key] = _value

    return info_dict

def fill_excel(path_to_sample_file: str, \
               output_dir: str, \
               all_df: pd.DataFrame) -> None:
    
    # traversal each company, which is a row in dataframe
    total = len(all_df)
    for _, row in tqdm_notebook(all_df.iterrows(), total=total):        
        # get sheet
        workbook = openpyxl.load_workbook(path_to_sample_file)
        sheet = workbook['sheet1']

        #
        # 基础信息
        #
        # 企业名称 C3
        sheet['C3'] = row['name']
        # 统一社会信用代码 C4
        sheet['C4'] = row['统一社会信用代码']
        # 法定代表人 C5
        sheet['C5'] = row['法定代表人信息']
        # 注册资本 C6
        sheet['C6'] = row['注册资本']
        # 成立日期 C7
        sheet['C7'] = row['成立日期']
        # 企业经营地址 C8
        sheet['C8'] = row['企业地址']
        # 公司联系人 C10
        sheet['C10'] = row['法定代表人信息']
        # 联系电话 C11
        sheet['C11'] = row['企业联系电话']
        # 企业类型 E3
        sheet['E3'] = row['企业类型']
        # 主营业务活动 E4
        sheet['E4'] = row['经营范围']
        # 公司网站 E5
        sheet['E5'] = row['网站']
        # 企业分支机构名称 E6
        sheet['E6'] = row['分支机构数量']
        # 分支机构经营地址 E7
        sheet['E7'] = row['所属地区']
        # 对华投资情况 E10
        sheet['E10'] = row['对外投资数量']
        # 邮箱 E11
        sheet['E11'] = row['电子邮箱']

        #
        # 经营信息
        #
        # 从业人数 C14
        sheet['C14'] = row['从业人数'] \
            if row['从业人数'] != '企业选择不公示' else row['城镇职工基本养老保险'] 
        # 上一年度营业收入 C15
        sheet['C15'] = row['营业总收入']
        # 上一年度利润总和 C16
        sheet['C16'] = row['利润总额']
        # 上一年度纳税总额 C17
        sheet['C17'] = row['纳税总额']

        # save xlsx file
        output_file_name = '{0}-招商目标企业信息收集-{1}.xlsx'.format(row['id'], row['name'])
        workbook.save(os.path.join(output_dir, output_file_name))