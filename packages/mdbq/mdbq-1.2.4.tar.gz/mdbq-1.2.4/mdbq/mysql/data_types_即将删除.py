# -*- coding:utf-8 -*-
import warnings
import pandas as pd
import numpy as np
import chardet
import zipfile

from numpy import dtype
from pandas.tseries.holiday import next_monday
from pyzipper import PyZipFile
import os
import platform
import json
import pymysql
from mdbq.mongo import mongo
from mdbq.mysql import mysql
from mdbq.mysql import s_query
from mdbq.config import get_myconf
from mdbq.config import set_support
from mdbq.dataframe import converter
import datetime
import time
import re
import shutil
import getpass

from sqlalchemy.dialects.postgresql.pg_catalog import pg_get_serial_sequence

warnings.filterwarnings('ignore')
"""
1. 记录 dataframe 或者数据库的列信息(dtypes)
2. 更新 mysql 中所有数据库的 dtypes 信息到本地 json
"""


class DataTypes:
    """
     数据简介: 记录 dataframe 或者数据库的列信息(dtypes)，可以记录其信息或者加载相关信息用于入库使用，
     第一字段为分类(如 dataframe/mysql)，第二字段为数据库名，第三字段为集合名，第四段列名及其数据类型
    """
    def __init__(self):
        self.datas = {
            '_json统计':
                {
                    '分类': 0,
                    '数据库量': 0,
                    '集合数量': 0,
                    '字段量': 0,
                    '数据简介': '记录 dataframe 或者数据库的列信息(dtypes)',
                }
        }
        self.path = set_support.SetSupport(dirname='support').dirname
        self.json_file = os.path.join(self.path, 'mysql_types.json')
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        if not os.path.isfile(self.json_file):
            with open(self.json_file, 'w', encoding='utf-8_sig') as f:
                json.dump(self.datas, f, ensure_ascii=False, sort_keys=True, indent=4)

    def json_before(self):
        """ 本地 json 文件的 dtypes 信息, 初始化更新给 self.datas """
        with open(self.json_file, 'r', encoding='utf-8_sig') as f:
            json_ = json.load(f)
            self.datas.update(json_)

    def df_dtypes_to_json(self, db_name, collection_name, path, df=pd.DataFrame(), is_file_dtype=True):
        if len(df) == 0:
            return
        cv = converter.DataFrameConverter()
        df = cv.convert_df_cols(df=df)  # 清理 dataframe 列名的不合规字符
        dtypes = df.dtypes.apply(str).to_dict()
        dtypes = {'dataframe': {db_name: {collection_name: dtypes}}}
        self.dtypes_to_json(dtypes=dtypes, cl='dataframe', db_name=db_name, collection_name=collection_name, path=path, is_file_dtype=is_file_dtype)

    def dtypes_to_json(self, cl, dtypes, db_name, collection_name, path, is_file_dtype, ):
        """ 更新 dataframe 的 dtypes 信息到 json 文件 """
        if not os.path.exists(path):
            os.makedirs(path)
        json_file = os.path.join(path, 'mysql_types.json')
        if os.path.isfile(json_file):
            self.json_before(json_file=json_file)  # 更新本地json信息到 self.datas

        if not os.path.isfile(json_file):  # 如果不存在本地 json 文件, 直接返回即可
            self.datas.update(dtypes)
            with open(json_file, 'w', encoding='utf-8_sig') as f:
                json.dump(self.datas, f, ensure_ascii=False, sort_keys=True, indent=4)
        else:  # 存在则读取，并更新 df 的 dtypes
            if cl in self.datas.keys():
                if db_name in list(self.datas[cl].keys()):  # ['京东数据2', '天猫数据2', '生意参谋数据2', '生意经2']
                    if collection_name in list(self.datas[cl][db_name].keys()):
                        if is_file_dtype:  # 旧数据优先
                            # # 用 dtypes 更新, 允许手动指定 json 文件里面的数据类型
                            dtypes[cl][db_name][collection_name].update(self.datas[cl][db_name][collection_name])
                            # 将 dtypes 更新进去，使 self.datas 包含新旧信息
                            self.datas[cl][db_name][collection_name].update(dtypes[cl][db_name][collection_name])
                        else:  # 新数据优先
                            self.datas[cl][db_name][collection_name].update(dtypes[cl][db_name][collection_name])
                    else:
                        if is_file_dtype:  # 旧数据优先
                            dtypes[cl][db_name].update(self.datas[cl][db_name])
                            self.datas[cl][db_name].update(dtypes[cl][db_name])
                        else:
                            self.datas[cl][db_name].update(dtypes[cl][db_name])
                else:
                    # dtypes.update(self.datas)  # 可以注释掉, 因为旧数据 self.datas 是空的
                    self.datas[cl].update(dtypes[cl])
            else:
                self.datas.update(dtypes)

        cif = 0  # 分类
        dbs = 0  # 数据库
        collections = 0  # 集合
        cols = 0  # 字段
        for k, v in self.datas.items():
            if k == '_json统计':
                continue  # 不统计头信息
            cif += 1
            for t, g in v.items():
                dbs += 1
                for d, j in g.items():
                    collections += 1
                    for t, p in j.items():
                        cols += 1
        tips = {'分类': cif, '数据库量': dbs, '集合数量': collections, '字段量': cols}
        self.datas['_json统计'].update(tips)
        with open(json_file, 'w', encoding='utf-8_sig') as f:
            json.dump(
                self.datas,
                f,
                ensure_ascii=False,  # 默认True，非ASCII字符将被转义。如为False，则非ASCII字符会以\uXXXX输出
                sort_keys=True,  # 默认为False。如果为True，则字典的输出将按键排序。
                indent=4,
            )

    def mysql_dtypes_to_json(self, db_name, tabel_name, path, is_file_dtype=True):
        username, password, host, port = get_myconf.select_config_values(
            target_service='home_lx',
            database='mysql',
        )
        sq = s_query.QueryDatas(username=username, password=password, host=host, port=port)
        name_type = sq.dtypes_to_list(db_name=db_name, tabel_name=tabel_name)
        if name_type:
            dtypes = {item['COLUMN_NAME']: item['COLUMN_TYPE'] for item in name_type}
            dtypes = {'mysql': {db_name: {tabel_name: dtypes}}}
            self.dtypes_to_json(dtypes=dtypes, cl='mysql', db_name=db_name, collection_name=tabel_name, path=path, is_file_dtype=is_file_dtype)
        else:
            print(f'数据库回传数据(name_type)为空')

    def load_dtypes(self, db_name, collection_name, path, cl='dataframe', ):
        if os.path.isfile(path):
            self.json_before(json_file=path)  # 更新本地json信息到 self.datas
        elif os.path.isdir(path):
            json_file = os.path.join(path, 'mysql_types.json')
            if os.path.isfile(json_file):
                self.json_before(json_file=json_file)
            else:
                # 如果不存在，则新建文件
                with open(json_file, 'w', encoding='utf-8_sig') as f:
                    json.dump(self.datas, f, ensure_ascii=False, sort_keys=True, indent=4)
                # print(f'不存在的文件: {json_file}')
                return

        if cl in self.datas.keys():
            if db_name in list(self.datas[cl].keys()):
                if collection_name in list(self.datas[cl][db_name].keys()):
                    return self.datas[cl][db_name][collection_name]
                else:
                    print(f'不存在的集合名信息: {collection_name}, 文件位置: {json_file}')
                    return {}
            else:
                print(f'不存在的数据库信息: {db_name}, 文件位置: {json_file}')
                return {}
        else:
            print(f'不存在的数据分类: {cl}, 文件位置: {json_file}')
            return {}


def mysql_all_dtypes(path=None):
    """
    更新笔记本 mysql 中所有数据库的 dtypes 信息到本地 json
    """
    if not path:
        path = set_support.SetSupport(dirname='support').dirname

    username, password, host, port = get_myconf.select_config_values(target_service='home_lx', database='mysql')
    config = {
        'host': host,
        'port': port,
        'user': username,
        'password': password,
        'charset': 'utf8mb4',  # utf8mb4 支持存储四字节的UTF-8字符集
        'cursorclass': pymysql.cursors.DictCursor,
    }

    connection = pymysql.connect(**config)  # 连接数据库
    with connection.cursor() as cursor:
        sql = "SHOW DATABASES;"
        cursor.execute(sql)
        db_name_lists = cursor.fetchall()
        db_name_lists = [item['Database'] for item in db_name_lists]
        connection.close()

    sys_lists = ['information_schema', 'mysql', 'performance_schema', 'sakila', 'sys']
    db_name_lists = [item for item in db_name_lists if item not in sys_lists]

    # db_name_lists = [
    #     '京东数据2',
    #     '天猫数据2',
    #     '市场数据2',
    #     '生意参谋数据2',
    #     '生意经2',
    #     '属性设置2',
    #     '聚合数据',
    # ]
    results = []
    for db_name in db_name_lists:
        config.update({'database': db_name})  # 添加更新 config 字段
        connection = pymysql.connect(**config)  # 连接数据库
        try:
            with connection.cursor() as cursor:
                sql = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{db_name}';"
                sql = "SHOW TABLES;"
                cursor.execute(sql)
                table_name = cursor.fetchall()
                for table in table_name:
                    for k, v in table.items():
                        results.append({db_name: v})
        except:
            pass
        finally:
            connection.close()
        time.sleep(0.5)

    d = DataTypes()
    for result in results:
        for k, v in result.items():
            d.mysql_dtypes_to_json(db_name=k, tabel_name=v, path=path)


if __name__ == '__main__':
    # mysql_all_dtypes()  # 更新 mysql 中所有数据库的 dtypes 信息到本地 json
    d = DataTypes()

