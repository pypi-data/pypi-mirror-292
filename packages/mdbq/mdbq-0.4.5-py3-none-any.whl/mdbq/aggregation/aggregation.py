# -*- coding:utf-8 -*-
import warnings
import pandas as pd
import numpy as np
import chardet
import zipfile
from pandas.tseries.holiday import next_monday
from pyzipper import PyZipFile
import os
import platform
import json
from mdbq.mongo import mongo
from mdbq.mysql import mysql
from mdbq.config import get_myconf
from mdbq.config import set_support
from mdbq.dataframe import converter
import datetime
import time
import re
import shutil
import getpass

warnings.filterwarnings('ignore')
"""
1. DatabaseUpdate: 程序用于对爬虫下载的原始数据进行清洗并入库;
    数据清洗主要包括对字段名的非法字符处理，对 df 中的非法值进行预处理;
    数据入库时会较检并更新本地 json 文件的 dtypes 信息;
    若 json 缺失 dtypes 信息, 可用 update_dtypte 先更新, 或者手动修改添加本地 json 信息; 
2. DataTypes: 类用于将某个csv文件的 dtypes 信息存入本地 json 文件, 会调用 converter 对 df 预处理;
    作用于完善某个数据库 dtypes 信息，可以使用本函数更新;
3. update_dtypte: 函数将一个 csv 文件的 dtypes 信息更新至本地 json 文件;
4. upload: 函数将一个文件夹上传至数据库;
    如果本地 json 中确实这个数据库的 dtypes 信息, 请用 update_dtypte 更新 json 文件再执行数据上传;
"""


class DataTypes:
    """
    将某表的列信息添加到 json 示例:
    file = '/Users/xigua/Downloads/天猫直通车旧报表(未排重版本).csv'
    df = pd.read_csv(file, encoding='utf-8_sig', header=0, na_filter=False)
    d = DataTypes()
    d.read_dtypes(
        df=df,
        db_name='天猫数据2',
        collection_name='旧版报表',
        is_file_dtype=False,  # 关闭文件优先
    )
    d.dtypes_to_file()
    """
    def __init__(self):
        self.path = set_support.SetSupport(dirname='support').dirname
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.json_file = os.path.join(self.path, 'data_types.json')
        # self.datas = json.loads('{}')  # 等待写入 json 文件的 dtypes 数据
        self.datas = {'json统计': {'数据库量': 0, '集合数量': 0, '字段量': 0}}
        self.json_before()

    def json_before(self):
        """ 本地 json 文件的 dtypes 信息, 初始化更新给 self.datas """
        if os.path.isfile(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8_sig') as json_file:
                json_ = json.load(json_file)
                self.datas.update(json_)

    def load_dtypes(self, db_name, collection_name, ):
        return self.datas[db_name][collection_name]


    def read_dtypes(self, db_name, collection_name, df=pd.DataFrame(), is_file_dtype=True):
        """
        读取 df 的 dtypes, 并更新本地 json 文件
        期间会 清理不合规的列名, 并对数据类型进行转换(尝试将 object 类型转为 int 或 float)
        返回: df 的 dtypes, 后续使用示例: df = df.astype(dtypes, errors='ignore')
        is_file_dtype=True: 默认情况下以旧 json 优先, 即允许手动指定 json 文件里面的数据类型
        """
        if len(df) == 0:
            return
        cv = converter.DataFrameConverter()
        df = cv.convert_df_cols(df=df)  # 清理 dataframe 列名的不合规字符
        dtypes = df.dtypes.apply(str).to_dict()
        dtypes = {db_name: {collection_name: dtypes}}

        if not self.datas:  # 如果不存在本地 json 文件, 直接返回即可
            self.datas.update(dtypes)
            return self.datas[db_name][collection_name]
        else:  # 存在则读取，并更新 df 的 dtypes
            if db_name in list(self.datas.keys()):  # ['京东数据2', '天猫数据2', '生意参谋数据2', '生意经2']
                if collection_name in list(self.datas[db_name].keys()):
                    if is_file_dtype:  # 旧数据优先
                        # # 用 dtypes 更新, 允许手动指定 json 文件里面的数据类型
                        dtypes[db_name][collection_name].update(self.datas[db_name][collection_name])
                        # 将 dtypes 更新进去，使 self.datas 包含新旧信息
                        self.datas[db_name][collection_name].update(dtypes[db_name][collection_name])
                    else:  # 新数据优先
                        self.datas[db_name][collection_name].update(dtypes[db_name][collection_name])
                else:
                    if is_file_dtype:  # 旧数据优先
                        dtypes[db_name].update(self.datas[db_name])
                        self.datas[db_name].update(dtypes[db_name])
                    else:
                        self.datas[db_name].update(dtypes[db_name])
            else:
                # dtypes.update(self.datas)  # 可以注释掉, 因为旧数据 self.datas 是空的
                self.datas.update(dtypes)
            dbs = 0
            collections = 0
            cols = 0
            # self.datas.pop('json统计')
            for k, v in self.datas.items():
                if k == 'json统计':
                    continue
                dbs += 1
                for d, j in v.items():
                    collections += 1
                    for t, p in j.items():
                        cols += 1
            tips = {'json统计': {'数据库量': dbs, '集合数量': collections, '字段量': cols}}
            self.datas.update(tips)
            return self.datas[db_name][collection_name]  # 返回 df 的 dtypes

    def dtypes_to_file(self):
        """ 保存为本地 json 文件 """
        # print(self.datas)
        with open(self.json_file, 'w', encoding='utf-8_sig') as f:
            json.dump(self.datas, f, ensure_ascii=False, sort_keys=True, indent=4)
        time.sleep(1)


class DatabaseUpdate:
    def __init__(self, path):
        self.path = path  # 数据所在目录, 即: 下载文件夹
        self.datas: list = []  # 带更新进数据库的数据集合
        self.start_date = '2022-01-01'  # 日期表的起始日期

    def cleaning(self, is_move=True):
        """
        数据清洗, 返回包含 数据库名, 集合名称, 和 df 主体
        """
        if not os.path.exists(self.path):
            print(f'1.1.0 初始化时传入了不存在的目录: {self.path}')
            return

        json_data = DataTypes()  # json 文件, 包含数据的 dtypes 信息
        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                if '~$' in name or '.DS' in name or '.localized' in name or '.ini' in name or '$RECYCLE.BIN' in name or 'Icon' in name:
                    continue
                # 只针对 csv, xlsx 文件进行处理
                if not name.endswith('.csv') and not name.endswith('.xls') and not name.endswith('.xlsx'):
                    continue
                df = pd.DataFrame()
                encoding = self.get_encoding(file_path=os.path.join(root, name))  # 用于处理 csv 文件
                tg_names = ['账户报表', '计划报表', '单元报表', '关键词报表', '人群报表', '宝贝主体报表',
                            '其他主体报表',
                            '创意报表', '地域报表', '权益报表']
                for tg_name in tg_names:
                    if tg_name in name and '报表汇总' not in name and name.endswith('.csv'):  # 排除达摩盘报表: 人群报表汇总
                        pattern = re.findall(r'(.*_)\d{8}_\d{6}', name)
                        if not pattern:  # 说明已经转换过
                            continue
                        shop_name = re.findall(r'\d{8}_\d{6}_(.*)\W', name)
                        if shop_name:
                            shop_name = shop_name[0]
                        else:
                            shop_name = ''
                        df = pd.read_csv(os.path.join(root, name), encoding=encoding, header=0, na_filter=False)
                        if '地域' not in name:  # 除了地域报表, 检查数据的字段是否包含“场景名字”,如果没有,说明没有选“pbix” 模块
                            ck = df.columns.tolist()
                            if '场景名字' not in ck:
                                print(f'1.2.0 {name} 报表字段缺失, 请选择Pbix数据模板下载')
                                continue
                        if len(df) == 0:
                            print(f'1.3.0 {name} 报表是空的, 请重新下载')
                            continue
                        cols = df.columns.tolist()
                        if '日期' not in cols:
                            print(f'1.4.0 {name} 报表不包含分日数据, 已跳过')
                            continue
                        if '省' in cols:
                            if '市' not in cols:
                                print(f'1.5.0 {name} 请下载市级地域报表，而不是省报表')
                                continue
                        # df.replace(to_replace=['\\N'], value=0, regex=False, inplace=True)  # 替换掉特殊字符
                        # df.replace(to_replace=[''], value=0, regex=False, inplace=True)
                        # df.fillna(0, inplace=True)
                        db_name = '天猫数据2'
                        collection_name = f'推广数据_{tg_name}'
                if name.endswith('.csv') and '超级直播' in name:
                    # 超级直播
                    df = pd.read_csv(os.path.join(root, name), encoding=encoding, header=0, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    pattern = re.findall(r'(.*_)\d{8}_\d{6}', name)
                    if not pattern:  # 说明已经转换过
                        continue
                    shop_name = re.findall(r'\d{8}_\d{6}_(.*)\W', name)
                    if shop_name:
                        shop_name = shop_name[0]
                    else:
                        shop_name = ''
                    # df.replace(to_replace=['\\N'], value=0, regex=False, inplace=True)  # 替换掉特殊字符
                    # df.replace(to_replace=[''], value=0, regex=False, inplace=True)
                    db_name = '天猫数据2'
                    collection_name = '推广数据_超级直播'
                elif name.endswith('.xls') and '短直联投' in name:
                    # 短直联投
                    df = pd.read_excel(os.path.join(root, name), sheet_name=None, header=0)
                    df = pd.concat(df)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    # df.replace(to_replace=[''], value=0, regex=False, inplace=True)
                    db_name = '天猫数据2'
                    collection_name = '推广数据_短直联投'
                elif name.endswith('.xls') and '视频加速推广' in name:
                    # 超级短视频
                    df = pd.read_excel(os.path.join(root, name), sheet_name=None, header=0)
                    df = pd.concat(df)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    # df.replace(to_replace=[''], value=0, regex=False, inplace=True)
                    db_name = '天猫数据2'
                    collection_name = '推广数据_超级短视频'
                if '人群报表汇总' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=1, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    db_name = '天猫数据2'
                    collection_name = '天猫_达摩盘_DMP报表'
                # ----------------- 推广报表 分割线 -----------------
                # ----------------- 推广报表 分割线 -----------------
                date01 = re.findall(r'(\d{4}-\d{2}-\d{2})_\d{4}-\d{2}-\d{2}', str(name))
                date02 = re.findall(r'\d{4}-\d{2}-\d{2}_(\d{4}-\d{2}-\d{2})', str(name))
                attrib_pattern = re.findall(r'(\d+).xlsx', name)  # 天猫商品素材表格, 必不可少
                if name.endswith('.xls') and '生意参谋' in name and '无线店铺流量来源' in name:
                    # 无线店铺流量来源
                    df = pd.read_excel(os.path.join(root, name), header=5)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    # df.replace(to_replace=['-'], value=0, regex=False, inplace=True)
                    # df.replace(to_replace=[','], value='', regex=True, inplace=True)
                    if date01[0] != date02[0]:
                        data_lis = date01[0] + '_' + date02[0]
                        df.insert(loc=0, column='数据周期', value=data_lis)
                    df.insert(loc=0, column='日期', value=date01[0])
                    # 2024-2-19 官方更新了推广渠道来源名称
                    df['三级来源'] = df['三级来源'].apply(
                        lambda x: '精准人群推广' if x == '精准人群推广(原引力魔方)'
                        else '关键词推广' if x == '关键词推广(原直通车)'
                        else '智能场景' if x == '智能场景(原万相台)'
                        else x
                    )
                    db_name = '生意参谋数据2'
                    if '经营优势' in df['一级来源'].tolist():  # 新版流量
                        if '数据周期' in df.columns.tolist():
                            collection_name='店铺来源_月数据_新版'
                        else:
                            collection_name='店铺来源_日数据_新版'
                    else:  # 旧版流量
                        if '数据周期' in df.columns.tolist():
                            collection_name='店铺来源_月数据'
                        else:
                            collection_name='店铺来源_日数据'
                elif name.endswith('.xls') and '生意参谋' in name and '商品_全部' in name:
                    # 店铺商品排行
                    df = pd.read_excel(os.path.join(root, name), header=4)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    # df.replace(to_replace=['-'], value=0, regex=False, inplace=True)
                    # df.replace(to_replace=[','], value='', regex=True, inplace=True)
                    df.rename(columns={'统计日期': '日期', '商品ID': '商品id'}, inplace=True)
                    if date01[0] != date02[0]:
                        data_lis = date01[0] + '_' + date02[0]
                        df.insert(loc=1, column='数据周期', value=data_lis)
                    db_name = '生意参谋数据2'
                    collection_name = '商品排行'
                elif name.endswith('.xls') and '参谋店铺整体日报' in name:
                    # 自助取数，店铺日报
                    df = pd.read_excel(os.path.join(root, name), header=7)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={'统计日期': '日期'}, inplace=True)
                    db_name = '生意参谋数据2'
                    collection_name = '自助取数_整体日报'
                elif name.endswith('.xls') and '参谋每日流量_自助取数_新版' in name:
                    # 自助取数，每日流量
                    df = pd.read_excel(os.path.join(root, name), header=7)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={'统计日期': '日期'}, inplace=True)
                    # 2024-2-19 官方更新了推广渠道来源名称，自助取数没有更新，这里强制更改
                    df['三级来源'] = df['三级来源'].apply(
                        lambda x: '精准人群推广' if x == '引力魔方'
                        else '关键词推广' if x == '直通车'
                        else '智能场景' if x == '万相台'
                        else '精准人群推广' if x == '精准人群推广(原引力魔方)'
                        else '关键词推广' if x == '关键词推广(原直通车)'
                        else '智能场景' if x == '智能场景(原万相台)'
                        else x
                    )
                    db_name = '生意参谋数据2'
                    collection_name = '自助取数_每日流量'
                elif name.endswith('.xls') and '商品sku' in name:
                    # 自助取数，商品sku
                    df = pd.read_excel(os.path.join(root, name), header=7)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={
                        '统计日期': '日期',
                        '商品ID': '商品id',
                        'SKU ID': 'sku id',
                        '商品SKU': '商品sku',
                    }, inplace=True)
                    db_name = '生意参谋数据2'
                    collection_name = '自助取数_商品sku'
                elif name.endswith('.xls') and '参谋店铺流量来源（月）' in name:
                    # 自助取数，月店铺流量来源
                    df = pd.read_excel(os.path.join(root, name), header=7)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={'统计日期': '数据周期'}, inplace=True)
                    # 2024-2-19 官方更新了推广渠道来源名称，自助取数没有更新，这里强制更改
                    df['三级来源'] = df['三级来源'].apply(
                        lambda x: '精准人群推广' if x == '引力魔方'
                        else '关键词推广' if x == '直通车'
                        else '智能场景' if x == '万相台'
                        else '精准人群推广' if x == '精准人群推广(原引力魔方)'
                        else '关键词推广' if x == '关键词推广(原直通车)'
                        else '智能场景' if x == '智能场景(原万相台)'
                        else x
                    )
                    df['日期'] = df['数据周期'].apply(lambda x: re.findall('(.*) ~', x)[0])
                    db_name = '生意参谋数据2'
                    collection_name = '自助取数_店铺流量_月数据'
                elif name.endswith('.csv') and 'baobei' in name:
                    # 生意经宝贝指标日数据
                    date = re.findall(r's-(\d{4})(\d{2})(\d{2})\.', str(name))
                    if not date:  # 阻止月数据及已转换的表格
                        print(f'{name}  不支持或是已转换的表格')
                        # os.remove(os.path.join(root, name))  # 直接删掉，避免被分到原始文件, encoding 不同会引发错误
                        continue
                    df = pd.read_csv(os.path.join(root, name), encoding=encoding, header=0, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        os.remove(os.path.join(root, name))
                        continue
                    if '日期' in df.columns.tolist():
                        df.pop('日期')
                    new_date = '-'.join(date[0])
                    df.insert(loc=0, column='日期', value=new_date)
                    df.replace(to_replace=['--'], value='', regex=False, inplace=True)
                    db_name = '生意经2'
                    collection_name = '宝贝指标'
                elif name.endswith('.csv') and '店铺销售指标' in name:
                    # 生意经, 店铺指标，仅限月数据，实际日指标也可以
                    name_st = re.findall(r'(.*)\(分日', name)
                    if not name_st:
                        print(f'{name}  已转换的表格')
                        continue
                    df = pd.read_csv(os.path.join(root, name), encoding=encoding, header=0, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df['日期'] = df['日期'].astype(str).apply(
                        lambda x: '-'.join(re.findall(r'(\d{4})(\d{2})(\d{2})', x)[0]) if x else x)
                    df.replace(to_replace=['--'], value='', regex=False, inplace=True)
                    db_name = '生意经2'
                    collection_name = '店铺指标'
                elif name.endswith('csv') and '省份' in name:
                    # 生意经，地域分布, 仅限日数据
                    pattern = re.findall(r'(.*[\u4e00-\u9fa5])(\d{4})(\d{2})(\d{2})\.', name)
                    if not pattern or '省份城市分析2' not in name:
                        print(f'{name}  不支持或已转换的表格')
                        # os.remove(os.path.join(root, name))  # 直接删掉，避免被分到原始文件, encoding 不同会引发错误
                        continue
                    date = '-'.join(pattern[0][1:])
                    df = pd.read_csv(os.path.join(root, name), encoding=encoding, header=0, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df['省'] = df['省份'].apply(lambda x: x if ' ├─ ' not in x and ' └─ ' not in x else None)
                    df['城市'] = df[['省份', '省']].apply(lambda x: '汇总' if x['省'] else x['省份'], axis=1)
                    df['省'].fillna(method='ffill', inplace=True)
                    df['城市'].replace(to_replace=[' ├─ | └─ '], value='', regex=True, inplace=True)
                    pov = df.pop('省')
                    city = df.pop('城市')
                    df.insert(loc=1, column='城市', value=city)
                    df.insert(loc=0, column='日期', value=date)
                    df['省份'] = pov
                    df['省+市'] = df[['省份', '城市']].apply(lambda x: f'{x["省份"]}-{x["城市"]}', axis=1)
                    db_name = '生意经2'
                    collection_name = '地域分布_省份城市分析'
                elif name.endswith('csv') and 'order' in name:
                    # 生意经，订单数据，仅限月数据
                    pattern = re.findall(r'(.*)(\d{4})(\d{2})(\d{2})-(\d{4})(\d{2})(\d{2})', name)
                    if not pattern:
                        print(f'{name}  不支持或已转换的表格')
                        # os.remove(os.path.join(root, name))  # 直接删掉，避免被分到原始文件, encoding 不同会引发错误
                        continue
                    date1 = pattern[0][1:4]
                    date1 = '-'.join(date1)
                    date2 = pattern[0][4:]
                    date2 = '-'.join(date2)
                    date = f'{date1}_{date2}'
                    df = pd.read_csv(os.path.join(root, name), encoding='gb18030', header=0, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.insert(loc=0, column='日期', value=date1)
                    df.insert(loc=1, column='数据周期', value=date)
                    df['商品id'] = df['宝贝链接'].apply(
                        lambda x: re.sub('.*id=', '', x) if x else x)
                    df.rename(columns={'宝贝标题': '商品标题', '宝贝链接': '商品链接'}, inplace=True)
                    df['颜色编码'] = df['商家编码'].apply(
                        lambda x: ''.join(re.findall(r' .*(\d{4})$', str(x))) if x else x)
                    db_name = '生意经2'
                    collection_name = '订单数据'
                elif name.endswith('.xlsx') and '直播间成交订单明细' in name:
                    # 直播间成交订单明细
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={'场次ID': '场次id', '商品ID': '商品id'}, inplace=True)
                    df['日期'] = df['支付时间'].apply(lambda x: x.strftime('%Y-%m-%d'))
                    db_name = '生意参谋数据2'
                    collection_name = '直播间成交订单明细'
                elif name.endswith('.xlsx') and '直播间大盘数据' in name:
                    # 直播间大盘数据
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={'统计日期': '日期'}, inplace=True)
                    db_name = '生意参谋数据2'
                    collection_name = '直播间大盘数据'
                elif name.endswith('.xls') and '直播业绩-成交拆解' in name:
                    # 直播业绩-成交拆解
                    df = pd.read_excel(os.path.join(root, name), header=5)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={'统计日期': '日期'}, inplace=True)
                    db_name = '生意参谋数据2'
                    collection_name = '直播业绩'
                elif name.endswith('.csv') and '淘宝店铺数据' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    db_name = '市场数据2'
                    collection_name = '淘宝店铺数据'
                elif name.endswith('.csv') and '人群洞察' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    df.replace(to_replace=['--'], value='', regex=False, inplace=True)
                    df = df[df['人群规模'] != '']
                    if len(df) == 0:
                        continue
                    db_name = '天猫数据2'
                    collection_name = '万相台_人群洞察'
                elif name.endswith('.csv') and '客户_客户概况_画像' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    db_name = '生意参谋数据2'
                    collection_name = '客户_客户概况_画像'
                elif name.endswith('.csv') and '市场排行_店铺' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    db_name = '市场数据2'
                    collection_name = '市场排行_店铺'
                elif name.endswith('.csv') and '类目洞察_属性分析' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    db_name = '市场数据2'
                    collection_name = '类目洞察_属性分析'
                elif name.endswith('.csv') and '类目洞察_价格分析' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    db_name = '市场数据2'
                    collection_name = '类目洞察_价格分析'
                elif name.endswith('.csv') and '竞店分析-销售分析' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    db_name = '市场数据2'
                    collection_name = '竞店分析_销售分析'
                elif name.endswith('.csv') and '竞店分析-来源分析' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    db_name = '市场数据2'
                    collection_name = '竞店分析_来源分析'
                # ----------------------- 京东数据处理分界线 -----------------------
                # ----------------------- 京东数据处理分界线 -----------------------
                elif name.endswith('.xlsx') and '店铺来源_流量来源' in name:
                    # 京东店铺来源
                    if '按天' not in name:
                        print(f'{name} 京东流量请按天下载')
                        continue
                    date01 = re.findall(r'(\d{4})(\d{2})(\d{2})_(\d{4})(\d{2})(\d{2})', str(name))
                    new_date01 = f'{date01[0][0]}-{date01[0][1]}-{date01[0][2]}'
                    new_date02 = f'{date01[0][3]}-{date01[0][4]}-{date01[0][5]}'
                    new_date03 = f'{new_date01}_{new_date02}'
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.insert(loc=0, column='日期', value=new_date01)
                    if new_date01 != new_date02:
                        df.insert(loc=1, column='数据周期', value=new_date03)
                    cols = df.columns.tolist()
                    for col_2024 in cols:  # 京东这个表有字段加了去年日期，删除这些同比数据字段，不然列数量爆炸
                        if '20' in col_2024 and '流量来源' in name:
                            df.drop(col_2024, axis=1, inplace=True)
                    db_name = '京东数据2'
                    collection_name = '流量来源_日数据'
                elif name.endswith('.xlsx') and '全部渠道_商品明细' in name:
                    # 京东商品明细 文件转换
                    date1 = re.findall(r'_(\d{4})(\d{2})(\d{2})_全部', str(name))
                    if not date1[0]:
                        print(f'{name}: 仅支持日数据')
                        continue
                    if date1:
                        date1 = f'{date1[0][0]}-{date1[0][1]}-{date1[0][2]}'
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    if '10035975359247' in df['商品ID'].values or '10056642622343' in df['商品ID'].values:
                        new_name = f'sku_{date1}_全部渠道_商品明细.csv'
                    elif '10021440233518' in df['商品ID'].values or '10022867813485' in df['商品ID'].values:
                        new_name = f'spu_{date1}_全部渠道_商品明细.csv'
                    else:
                        new_name = f'未分类_{date1}_全部渠道_商品明细.csv'
                    df.rename(columns={'商品ID': '商品id'}, inplace=True)
                    df.insert(loc=0, column='日期', value=date1)
                    if 'sku' in new_name:
                        db_name = '京东数据2'
                        collection_name = 'sku_商品明细'
                    elif 'spu' in new_name:
                        db_name = '京东数据2'
                        collection_name = 'spu_商品明细'
                elif name.endswith('.xlsx') and '搜索分析-排名定位-商品词下排名' in name:
                    # 京东商品词下排名
                    df = pd.read_excel(os.path.join(root, name), header=0, engine='openpyxl')
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.rename(columns={'商品的ID': 'skuid'}, inplace=True)
                    for col in ['词人气', '搜索点击率']:
                        if col in df.columns.tolist():
                            df[col] = df[col].apply(lambda x: round(x, 6) if x else x)
                    db_name = '京东数据2'
                    collection_name = '商品词下排名'
                elif name.endswith('.xlsx') and '搜索分析-排名定位-商品排名' in name:
                    # 京东商品排名
                    date_in = re.findall(r'(\d{4}-\d{2}-\d{2})-搜索', str(name))[0]
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.insert(0, '日期', date_in)  # 插入新列
                    df.rename(columns={'SKU': 'skuid'}, inplace=True)
                    if '点击率' in df.columns.tolist():
                        df['点击率'] = df['点击率'].apply(lambda x: round(x, 6) if x else x)
                    db_name = '京东数据2'
                    collection_name = '商品排名'
                elif name.endswith('.xls') and '竞店概况_竞店详情' in name:
                    # 京东，竞争-竞店概况-竞店详情-全部渠道
                    date01 = re.findall(r'全部渠道_(\d{4})(\d{2})(\d{2})_(\d{4})(\d{2})(\d{2})', str(name))
                    start_date = f'{date01[0][0]}-{date01[0][1]}-{date01[0][2]}'
                    # end_date = f'{date01[0][3]}-{date01[0][4]}-{date01[0][5]}'
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df.insert(loc=0, column='日期', value=start_date)
                    db_name = '京东数据2'
                    collection_name = '竞店监控_日数据'
                elif name.endswith('.xls') and '店铺' in name:
                    # 京东 自助报表  店铺日报
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df['日期'] = df['日期'].apply(
                        lambda x: '-'.join(re.findall(r'(\d{4})(\d{2})(\d{2})', str(x))[0])
                    )
                    db_name = '京东数据2'
                    collection_name = '京东_自助取数_店铺日报'
                elif name.endswith('.xls') and '商家榜单_女包_整体' in name:
                    # 京东 行业 商家榜单
                    date2 = re.findall(r'_\d{8}-\d+', name)
                    if date2:
                        print(f'{name}: 请下载日数据，不支持其他周期')
                        # os.remove(os.path.join(root, name))  # 直接删掉，避免被分到原始文件, encoding 不同会引发错误
                        continue
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df['日期'] = df['日期'].astype(str).apply(lambda x: f'{x[:4]}-{x[4:6]}-{x[6:8]}')
                    df.insert(loc=0, column='类型', value='商家榜单')
                    db_name = '京东数据2'
                    collection_name = '商家榜单'
                elif name.endswith('.xlsx') and '批量SKU导出-批量任务' in name:
                    # 京东 sku 导出
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    d_time = datetime.datetime.today().strftime('%Y-%m-%d')
                    df.insert(loc=0, column='日期', value=d_time)
                    df['商品链接'] = df['商品链接'].apply(lambda x: f'https://{x}' if x else x)
                    db_name = '属性设置2'
                    collection_name = '京东sku商品信息'
                elif name.endswith('.xlsx') and '批量SPU导出-批量任务' in name:
                    # 京东 spu 导出
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    d_time = datetime.datetime.today().strftime('%Y-%m-%d')
                    df.insert(loc=0, column='日期', value=d_time)
                    db_name = '属性设置2'
                    collection_name = '京东spu商品信息'
                elif name.endswith('.csv') and '万里马箱包推广1_完整点击成交' in name:
                    # 京东推广数据
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df['日期'] = df['日期'].apply(lambda x: f'{str(x)[:4]}-{str(x)[4:6]}-{str(x)[6:8]}')
                    db_name = '京东数据2'
                    collection_name = '推广数据_京准通'
                elif name.endswith('.csv') and '万里马箱包推广1_京东推广搜索词_pbix同步不要' in name:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df['日期'] = df['日期'].apply(lambda x: f'{str(x)[:4]}-{str(x)[4:6]}-{str(x)[6:8]}')
                    df['是否品牌词'] = df['搜索词'].str.contains('万里马|wanlima', regex=True)
                    df['是否品牌词'] = df['是否品牌词'].apply(lambda x: '品牌词' if x else '')
                    db_name = '京东数据2'
                    collection_name = '推广数据_搜索词报表'
                elif name.endswith('.xlsx') and '零售明细统计' in name:
                    df = pd.read_excel(os.path.join(root, name), header=0)
                    if len(df) == 0:
                        print(f'{name} 报表数据为空')
                        continue
                    df = df[df['缩略图'] != '合计']
                    db_name = '生意经2'
                    collection_name = 'E3_零售明细统计'

                # 商品素材，必须保持放在最后处理
                elif name.endswith('xlsx'):
                    """从天猫商品素材库中下载的文件，将文件修改日期添加到DF 和文件名中"""
                    if  attrib_pattern:
                        df = pd.read_excel(os.path.join(root, name), header=0, engine='openpyxl')
                        cols = df.columns.tolist()
                        if '商品白底图' in cols and '方版场景图' in cols:
                            f_info = os.stat(os.path.join(root, name))  # 读取文件的 stat 信息
                            mtime = time.strftime('%Y-%m-%d', time.localtime(f_info.st_mtime))  # 读取文件创建日期
                            df['日期'] = mtime
                            df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')
                            df.rename(columns={'商品ID': '商品id'}, inplace=True)
                            sp_id = df['商品id'].tolist()
                            if 652737455554 in sp_id or 683449516249 in sp_id or 37114359548 in sp_id or 570735930393 in sp_id:
                                df.insert(0, '店铺名称', '万里马官方旗舰店')  # 插入新列
                            elif 704624764420 in sp_id or 701781021639 in sp_id or 520380314717 in sp_id:
                                df.insert(0, '店铺名称', '万里马官方企业店')  # 插入新列
                            else:
                                df.insert(0, '店铺名称', 'coome旗舰店')  # 插入新列
                            db_name = '属性设置2'
                            collection_name = '商品素材导出'

                if is_move:
                    try:
                        os.remove(os.path.join(root, name))  # 是否移除原文件
                    except Exception as e:
                        print(f'{name},  {e}')
                if len(df) > 0:
                    # 创建包含 dtypes 信息的 json 文件
                    json_data.read_dtypes(
                        df=df,
                        db_name=db_name,
                        collection_name=collection_name,
                        is_file_dtype=True,  # 默认本地文件优先: True
                    )
                    # 将数据传入 self.datas 等待更新进数据库
                    self.datas.append(
                        {
                            '数据库名': db_name,
                            '集合名称': collection_name,
                            '数据主体': df,
                        }
                    )
        json_data.dtypes_to_file()  # 写入 json 文件, 包含数据的 dtypes 信息

        # 品销宝一个表格里面包含多个 sheet, 最好是单独处理
        json_data = DataTypes()  # json 文件, 包含数据的 dtypes 信息
        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                if '~$' in name or '.DS' in name or '.localized' in name or '.jpg' in name or '.png' in name:
                    continue
                # df = pd.DataFrame()
                if name.endswith('.xlsx') and '明星店铺' in name:
                    # 品销宝
                    pattern = re.findall(r'_(\d{4}-\d{2}-\d{2})_', name)
                    if pattern:
                        continue
                    sheets4 = ['账户', '推广计划', '推广单元', '创意', '品牌流量包', '定向人群']  # 品销宝
                    file_name4 = os.path.splitext(name)[0]  # 明星店铺报表
                    for sheet4 in sheets4:
                        df = pd.read_excel(os.path.join(root, name), sheet_name=sheet4, header=0, engine='openpyxl')
                        df = df[df['搜索量'] > 0]
                        if len(df) < 1:
                            # print(f'{name}/{sheet4} 跳过')
                            continue
                        df.insert(loc=1, column='报表类型', value=sheet4)
                        db_name = '天猫数据2'
                        collection_name = f'推广数据_品销宝_{sheet4}'
                        json_data.read_dtypes(
                            df=df,
                            db_name=db_name,
                            collection_name=collection_name,
                            is_file_dtype=False,
                        )
                        self.datas.append(
                            {
                                '数据库名': db_name,
                                '集合名称': collection_name,
                                '数据主体': df,
                            }
                        )
                    if is_move:
                        os.remove(os.path.join(root, name))
        json_data.dtypes_to_file()  # 写入 json 文件, 包含数据的 dtypes 信息

        df = self.date_table()  # 创建一个日期表
        self.datas.append(
            {
                '数据库名': '聚合数据',
                '集合名称': '日期表',
                '数据主体': df,
            }
        )

    def upload_df(self, service_databases=[{}]):
        """
        将清洗后的 df 上传数据库
        """
        for service_database in service_databases:
            for service_name, database in service_database.items():
                # print(service_name, database)
                if database == 'mongodb':
                    username, password, host, port = get_myconf.select_config_values(
                        target_service=service_name,
                        database=database,
                    )
                    d = mongo.UploadMongo(
                        username=username,
                        password=password,
                        host=host,
                        port=port,
                        drop_duplicates=False,
                    )
                    for data in self.datas:
                        df, db_name, collection_name = data['数据主体'], data['数据库名'], data['集合名称']
                        d.df_to_mongo(df=df, db_name=db_name, collection_name=collection_name)

                elif database == 'mysql':
                    username, password, host, port = get_myconf.select_config_values(
                        target_service=service_name,
                        database=database,
                    )
                    m = mysql.MysqlUpload(
                        username=username,
                        password=password,
                        host=host,
                        port=port,
                    )
                    for data in self.datas:
                        df, db_name, collection_name = data['数据主体'], data['数据库名'], data['集合名称']
                        m.df_to_mysql(df=df, db_name=db_name, tabel_name=collection_name)

    def new_unzip(self, path=None, is_move=None):
        """
        {解压并移除zip文件}
        如果是京东的商品明细，处理过程：
        1. 读取 zip包的文件名
        2. 组合完整路径，判断文件夹下是否已经有同名文件
        3. 如果有，则将该同名文件改名，（从文件名中提取日期，重新拼接文件名）
        4. 然后解压 zip包
        5. 需要用 _jd_rename 继续重命名刚解压的文件
        is_move 参数,  是否移除 下载目录的所有zip 文件
        """
        if not path:
            path = self.path
        res_names = []  # 需要移除的压缩文件
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                if '~$' in name or 'DS_Store' in name or 'baidu' in name or 'xunlei' in name:
                    continue
                if name.endswith('.zip'):
                    old_file = os.path.join(root, name)
                    f = zipfile.ZipFile(old_file, 'r')
                    if len(f.namelist()) == 1:  # 压缩包只有一个文件的情况
                        for zip_name in f.namelist():  # 读取zip内的文件名称
                            # zip_name_1 = zip_name.encode('cp437').decode('utf-8')
                            try:
                                zip_name_1 = zip_name.encode('utf-8').decode('utf-8')
                            except:
                                zip_name_1 = zip_name.encode('cp437').decode('utf-8')
                            new_path = os.path.join(root, zip_name_1)  # 拼接解压后的文件路径
                            if os.path.isfile(new_path) and '全部渠道_商品明细' in new_path:  # 是否存在和包内同名的文件
                                # 专门处理京东文件
                                df = pd.read_excel(new_path)
                                try:
                                    pattern1 = re.findall(r'\d{8}_(\d{4})(\d{2})(\d{2})_全部渠道_商品明细',
                                                          name)
                                    pattern2 = re.findall(
                                        r'\d{8}_(\d{4})(\d{2})(\d{2})-(\d{4})(\d{2})(\d{2})_全部渠道_商品明细',
                                        name)
                                    if pattern1:
                                        year_date = '-'.join(list(pattern1[0])) + '_' + '-'.join(list(pattern1[0]))
                                    elif pattern2:
                                        year_date = '-'.join(list(pattern2[0])[0:3]) + '_' + '-'.join(
                                            list(pattern2[0])[3:7])
                                    else:
                                        year_date = '无法提取日期'
                                        print(f'{name} 无法从文件名中提取日期，请检查pattern或文件')
                                    if ('10035975359247' in df['商品ID'].values or '10056642622343' in
                                            df['商品ID'].values):
                                        os.rename(new_path,
                                                  os.path.join(root, 'sku_' + year_date + '_全部渠道_商品明细.xls'))
                                        f.extract(zip_name_1, root)
                                    elif ('10021440233518' in df['商品ID'].values or '10022867813485' in
                                          df['商品ID'].values):
                                        os.rename(new_path,
                                                  os.path.join(root, 'spu_' + year_date + '_全部渠道_商品明细.xls'))
                                        f.extract(zip_name_1, root)
                                    if is_move:
                                        os.remove(os.path.join(root, name))
                                except Exception as e:
                                    print(e)
                                    continue
                            else:
                                f.extract(zip_name, root)
                                if zip_name_1 != zip_name:
                                    os.rename(os.path.join(root, zip_name), os.path.join(root, zip_name_1))
                                if is_move:
                                    res_names.append(name)
                                    # os.remove(os.path.join(root, name))  # 这里不能移除，会提示文件被占用
                        f.close()
                    else:  # 压缩包内包含多个文件的情况
                        f.close()
                        self.unzip_all(path=old_file, save_path=path)

        if is_move:
            for name in res_names:
                os.remove(os.path.join(path, name))
                print(f'移除{os.path.join(path, name)}')

    def unzip_all(self, path, save_path):
        """
        遍历目录， 重命名有乱码的文件
        2. 如果压缩包是文件夹， 则保存到新文件夹，并删除有乱码的文件夹
        3. 删除MAC系统的临时文件夹__MACOSX
        """
        with PyZipFile(path) as _f:
            _f.extractall(save_path)
            _f.close()
        for _root, _dirs, _files in os.walk(save_path, topdown=False):
            for _name in _files:
                if '~$' in _name or 'DS_Store' in _name:
                    continue
                try:
                    _new_root = _root.encode('cp437').decode('utf-8')
                    _new_name = _name.encode('cp437').decode('utf-8')
                except:
                    _new_root = _root.encode('utf-8').decode('utf-8')
                    _new_name = _name.encode('utf-8').decode('utf-8')
                _old = os.path.join(_root, _name)
                _new = os.path.join(_new_root, _new_name)
                if _new_root != _root:  # 目录乱码，创建新目录
                    os.makedirs(_new_root, exist_ok=True)
                os.rename(_old, _new)
            try:
                _new_root = _root.encode('cp437').decode('utf-8')
            except:
                _new_root = _root.encode('utf-8').decode('utf-8')
            if _new_root != _root or '__MACOSX' in _root:
                shutil.rmtree(_root)

    def get_encoding(self, file_path):
        """
        获取文件的编码方式, 读取速度比较慢，非必要不要使用
        """
        with open(file_path, 'rb') as f:
            f1 = f.read()
            encod = chardet.detect(f1).get('encoding')
        return encod

    def date_table(self):
        """
        生成 pbix使用的日期表
        """
        yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
        dic = pd.date_range(start=self.start_date, end=yesterday)
        df = pd.DataFrame(dic, columns=['日期'])
        df.sort_values('日期', ascending=True, ignore_index=True, inplace=True)
        df.reset_index(inplace=True)
        # inplace 添加索引到 df
        p = df.pop('index')
        df['月2'] = df['日期']
        df['月2'] = df['月2'].dt.month
        df['日期'] = df['日期'].dt.date  # 日期格式保留年月日，去掉时分秒
        df['年'] = df['日期'].apply(lambda x: str(x).split('-')[0] + '年')
        df['月'] = df['月2'].apply(lambda x: str(x) + '月')
        # df.drop('月2', axis=1, inplace=True)
        mon = df.pop('月2')
        df['日'] = df['日期'].apply(lambda x: str(x).split('-')[2])
        df['年月'] = df.apply(lambda x: x['年'] + x['月'], axis=1)
        df['月日'] = df.apply(lambda x: x['月'] + x['日'] + '日', axis=1)
        df['第n周'] = df['日期'].apply(lambda x: x.strftime('第%W周'))
        df['索引'] = p
        df['月索引'] = mon
        df.sort_values('日期', ascending=False, ignore_index=True, inplace=True)
        return df

def update_dtypte():
    """ 更新一个文件的 dtype 信息到 json 文件 """
    file = '/Users/xigua/数据中心/原始文件2/月数据/流量来源/【生意参谋平台】无线店铺流量来源-2023-04-01_2023-04-30.csv'
    df = pd.read_csv(file, encoding='utf-8_sig', header=0, na_filter=False)
    d = DataTypes()
    d.read_dtypes(
        df=df,
        db_name='生意参谋数据2',
        collection_name='店铺来源_月数据',
        is_file_dtype=True,  # 日常需开启文件优先, 正常不要让新文件修改 json 已有的类型
    )
    d.dtypes_to_file()


def upload():
    """ 上传一个文件夹到数据库 """
    path = '/Users/xigua/数据中心/原始文件2/生意经/店铺指标'
    db_name = '生意经2'
    collection_name = '店铺指标'

    username, password, host, port = get_myconf.select_config_values(
        target_service='home_lx',
        database='mongodb',
    )
    d = mongo.UploadMongo(
        username=username,
        password=password,
        host=host,
        port=port,
        drop_duplicates=False,
    )
    username, password, host, port = get_myconf.select_config_values(
        target_service='home_lx',
        database='mysql',
    )
    m = mysql.MysqlUpload(
        username=username,
        password=password,
        host=host,
        port=port,
    )
    username, password, host, port = get_myconf.select_config_values(
        target_service='nas',
        database='mysql',
    )
    nas = mysql.MysqlUpload(
        username=username,
        password=password,
        host=host,
        port=port,
    )

    dt = DataTypes()
    dtypes = dt.load_dtypes(
        db_name=db_name,
        collection_name=collection_name,
    )
    # print(dtypes)
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if '~$' in name or '.DS' in name or '.localized' in name or 'baidu' in name:
                continue
            if name.endswith('.csv'):
                # print(name)
                try:
                    df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                    if len(df) == 0:
                        continue
                    cv = converter.DataFrameConverter()
                    df = cv.convert_df_cols(df=df)  # 清理列名和 df 中的非法字符
                    try:
                        df = df.astype(dtypes)
                    except Exception as e:
                        print(name, e)
                        old_dt = df.dtypes.apply(str).to_dict()  # 将 dataframe 数据类型转为字典形式
                        intersection_keys = dtypes.keys() & old_dt.keys()  # 获取两个字典键的交集
                        dtypes = {k: dtypes[k] for k in intersection_keys}  # 使用交集的键创建新字典
                        df = df.astype(dtypes)
                        # print(intersection_dict)
                    # print(df)

                    d.df_to_mongo(df=df, db_name=db_name, collection_name=collection_name)
                    m.df_to_mysql(df=df, db_name=db_name, tabel_name=collection_name)
                    nas.df_to_mysql(df=df, db_name=db_name, tabel_name=collection_name)
                except Exception as e:
                    print(name, e)
    if d.client:
        d.client.close()  # 必须手动关闭数据库连接


def main():
    d = DatabaseUpdate(path='/Users/xigua/Downloads')
    d.new_unzip(is_move=True)
    d.cleaning(is_move=False)
    d.upload_df(service_databases=[
        # {'home_lx': 'mongodb'},
        {'home_lx': 'mysql'}
    ]
    )
    # print(d.datas)


if __name__ == '__main__':
    # username, password, host, port = get_myconf.select_config_values(target_service='nas', database='mysql')
    # print(username, password, host, port)

    main()
    # upload()
