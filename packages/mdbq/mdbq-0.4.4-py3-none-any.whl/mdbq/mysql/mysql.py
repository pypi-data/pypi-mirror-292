# -*- coding:utf-8 -*-
import datetime
import platform
import getpass
import re
import time
from functools import wraps
import warnings
import pymysql
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import os
import calendar
from mdbq.config import get_myconf
from mdbq.config import set_support
from mdbq.dataframe import converter
from mdbq.mysql import data_types

warnings.filterwarnings('ignore')


class MysqlUpload:
    def __init__(self, username: str, password: str, host: str, port: int, charset: str = 'utf8mb4'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.config = {
            'host': self.host,
            'port': self.port,
            'user': self.username,
            'password': self.password,
            'charset': charset,  # utf8mb4 支持存储四字节的UTF-8字符集
            'cursorclass': pymysql.cursors.DictCursor,
        }
        self.conn = None

    @staticmethod
    def try_except(func):  # 在类内部定义一个异常处理方法
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'{func.__name__}, {e}')  # 将异常信息返回

        return wrapper

    def _conn(self):
        self.config = {
            'host': self.host,
            'port': int(self.port),
            'user': self.username,
            'password': self.password,
            'charset': 'utf8mb4',  # utf8mb4 支持存储四字节的UTF-8字符集
            'cursorclass': pymysql.cursors.DictCursor,
        }
        try:
            self.conn = pymysql.connect(**self.config)  # 连接数据库
            return True
        except:
            return False

    # @try_except
    def df_to_mysql(self, df, tabel_name, db_name='远程数据源'):
        """
        将 df 写入数据库
        db_name: 数据库名称
        tabel_name: 集合/表名称
        """
        db_name = re.sub(r'[\',，（）()/=<>+\-*^"’\[\]~#|&% .]', '_', db_name)
        tabel_name = re.sub(r'[\',，（）()/=<>+\-*^"’\[\]~#|&% .]', '_', tabel_name)
        cv = converter.DataFrameConverter()
        df = cv.convert_df_cols(df=df)  # 清理列名中的不合规字符

        connection = pymysql.connect(**self.config)  # 连接数据库
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
                database_exists = cursor.fetchone()
                if not database_exists:
                    # 如果数据库不存在，则新建
                    if '8.138.27' in str(self.host) or platform.system() == "Linux":  # 阿里云 mysql 低版本不支持 0900
                        cursor.execute(f"CREATE DATABASE {db_name} COLLATE utf8mb4_unicode_ci")
                        self.config.update({'charset': 'utf8mb4_unicode_ci'})
                    if '192.168.1.100' in str(self.host):
                        cursor.execute(f"CREATE DATABASE {db_name}")
                    else:
                        cursor.execute(f"CREATE DATABASE {db_name} COLLATE utf8mb4_0900_ai_ci")
                    # cursor.execute(f"CREATE DATABASE {db_name}")
                    connection.commit()
                    print(f"创建Database: {db_name}")
        except Exception as e:
            print(e)
            return
        finally:
            connection.close()  # 这里要断开连接
            time.sleep(0.2)

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = pymysql.connect(**self.config)  # 重新连接数据库
        try:
            with connection.cursor() as cursor:
                tabel_name = tabel_name.replace('-', '_')
                # 1. 查询表, 不存在则创建一个空表
                cursor.execute(f"SHOW TABLES LIKE '{tabel_name}'")
                if not cursor.fetchone():
                    sql = f'CREATE TABLE IF NOT EXISTS {tabel_name} (id INT AUTO_INCREMENT PRIMARY KEY)'
                    cursor.execute(sql)
                    print(f'创建 mysql 表: {tabel_name}')

                # # 2. 列数据类型转换
                # cols = df.columns.tolist()
                # dtypes = df.dtypes.apply(str).to_dict()  # 将 dataframe 数据类型转为字典形式
                # # 转换为 mysql 的数据类型
                # dtypes.update({col: self.convert_dtype_to_sql(df=df, col=col, dtype=dtypes[col]) for col in cols})
                dtypes = self.convert_dtypes(df=df, db_name=db_name, tabel_name=tabel_name)

                # 3. 检查列, 不存在则添加新列
                cols = df.columns.tolist()
                for col in cols:
                    sql = ('SELECT 1 FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND '
                           'column_name = %s')
                    cursor.execute(sql, (db_name, {tabel_name}, col))
                    if cursor.fetchone() is None:  # 如果列不存在，添加新列
                        print(f"添加列: {col}({dtypes[col]})")  # 添加列并指定数据类型
                        # if col == '日期':
                        #     sql = f"ALTER TABLE {tabel_name} ADD COLUMN {col} DATE default NULL;"
                        # else:
                        #     sql = f"ALTER TABLE {tabel_name} ADD COLUMN {col} mediumtext default NULL;"
                        sql = f"ALTER TABLE {tabel_name} ADD COLUMN {col} {dtypes[col]} default NULL;"
                        cursor.execute(sql)

                    if col == '日期':
                        cursor.execute(f"SHOW INDEXES FROM `{tabel_name}` WHERE Column_name = %s", ({col},))
                        result = cursor.fetchone()  # 检查索引是否存在
                        if not result:
                            # print(f'创建索引: {col}')
                            cursor.execute(f"CREATE INDEX index_name ON {tabel_name}({col})")
                connection.commit()  # 提交事务

                # # 4. 移除指定日期范围内的数据, 避免重复插入
                # dates = df['日期'].values.tolist()
                # start_date = pd.to_datetime(min(dates)).strftime('%Y-%m-%d')
                # end_date = (pd.to_datetime(max(dates)) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                # sql = f"DELETE FROM {tabel_name} WHERE {'日期'} BETWEEN '%s' AND '%s'" % (start_date, end_date)
                # cursor.execute(sql)
                # connection.commit()

                # 5. 更新插入数据
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                print(f'{now}正在更新 mysql ({self.host}:{self.port}) {db_name}/{tabel_name}')
                if str(self.host) == '192.168.1.100':  # 群晖服务器
                    try:
                        datas = df.to_dict('records')
                        for data in datas:
                            cols = ', '.join(data.keys())
                            values = ', '.join([f'"{v}"' for v in data.values()])
                            sql = f"INSERT INTO {tabel_name} ({cols}) VALUES ({values})"
                            cursor.execute(sql)
                        connection.commit()
                    except Exception as e:
                        print(e)
                        connection.rollback()
                else:  # 其他服务器
                    try:
                        engine = create_engine(
                            f'mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{db_name}'
                        )
                        df.to_sql(tabel_name, con=engine, if_exists='append', index=False)
                    except Exception as e:  # 如果异常则回滚
                        try:
                            connection.rollback()
                            print(f'{e}, 发生异常，正在重试...')
                            # df = df.replace([np.inf, -np.inf], 0)
                            df.to_sql(tabel_name, con=engine, if_exists='append', index=False)
                        except Exception as e:
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                            print(f'{now}{db_name}/{tabel_name}数据异常, 正在回滚: {e}')
                            connection.rollback()
        finally:
            connection.close()

    def convert_dtypes(self, df, db_name, tabel_name):
        """
        根据本地已经存在的记录着 mysql dtypes 的 json 文件转换 df 的类型为 mysql 专有的数据类型
        允许通过 json 文件指定列的数据类型
        以下两种情况已经兼容:
        1. 可能不存在本地 json 文件 (利用 convert_dtype_to_sql 函数按指定规则转换全部列)
        2. json 文件中没有或者缺失部分列信息(利用 convert_dtype_to_sql 函数按指定规则转换缺失列)
        """
        cols = df.columns.tolist()
        path = set_support.SetSupport(dirname='support').dirname
        # json_file = os.path.join(path, 'mysql_types.json')
        # if os.path.isfile(json_file):
        d = data_types.DataTypes()
        # 从本地文件中读取 dtype 信息
        dtypes = d.load_dtypes(cl='mysql', db_name=db_name, collection_name=tabel_name, path=path)
        # 可能会因为没有 json 文件, 返回 None
        if dtypes:
            # 按照文件记录更新 dtypes
            dtypes.update({col: dtypes[col] for col in cols if col in dtypes.keys()})
            # 可能存在部分列不在文件记录中
            col_not_exist = [col for col in cols if col not in dtypes.keys()]
            # 这些列不存在于 df 中, 必须移除
            [dtypes.pop(col) for col in list(dtypes.keys()) if col not in cols]
        else:
            dtypes = df.dtypes.apply(str).to_dict()  # 将 dataframe 数据类型转为字典形式
            col_not_exist = cols
        # 对文件不存在的列信息进行数据类型转换(按指定规则)
        dtypes.update({col: self.convert_dtype_to_sql(df=df, col=col, dtype=df[col].dtype) for col in col_not_exist})
        # 至此 df 中全部列类型已经转换完成
        # 返回结果, 示例: {'上市年份': 'mediumtext', '商品id': 'mediumtext', '平台': 'mediumtext'}
        return dtypes

    def convert_dtype_to_sql(self, df, col, dtype):
        """ 按照以下规则转换DataFrame列的数据类型为 MYSQL 专有的数据类型 """
        # 最优先处理 ID 类型, 在 mysql 里面, 有些列数字过长不能存储为 int 类型
        if 'id' in col or 'ID' in col or 'Id' in col or '摘要' in col or '商家编码' in col or '单号' in col or '款号' in col:
            return 'mediumtext'
        if '商品编码' in col:  # 京东sku/spu商品信息
            return 'mediumtext'
        if '文件大小' in col:  # bw 程序
            return 'mediumtext'
        elif '日期' in col or '时间' in col:
            try:
                k = pd.to_datetime(df[col].tolist()[0])  # 检查是否可以转为日期
                return 'DATE'
            except:
                return 'mediumtext'
        elif dtype == 'datetime64[ns]':  # 日期可能显示为数字, 因为放在判断 int 的前面
            return 'DATE'
        elif dtype == 'int32':
            if len(str(max(df[col].tolist()))) >= 10:  # 数值长度超限转为 mediumtext
                return 'mediumtext'
            return 'INT'
        elif dtype == 'int64':
            if len(str(max(df[col].tolist()))) >= 10:
                return 'mediumtext'
            return 'INT'
        elif dtype == 'float64':
            return 'FLOAT'
        elif dtype == 'object':
            return 'mediumtext'
        else:
            return 'mediumtext'

    def upload_pandas(self, update_path, db_name, days=None):
        """
        专门用来上传 pandas数据源的全部文件,  跳过 '其他数据'  or '京东数据集'
        db_name: 数据库名: pandas数据源
        update_path: pandas数据源所在路径
        days: 更新近期数据，单位: 天, 不设置则全部更新
        """
        if days:
            today = datetime.date.today()
            start_date = pd.to_datetime(today - datetime.timedelta(days=days))
        else:
            start_date = pd.to_datetime('2000-01-01')

        root_files = os.listdir(update_path)
        for root_file in root_files:
            if '其他数据' in root_file or '年.csv' in root_file or '京东数据集' in root_file:
                continue  # 跳过的文件夹
            f_path = os.path.join(update_path, root_file)

            if os.path.isdir(f_path):
                for root, dirs, files in os.walk(f_path, topdown=False):
                    for name in files:
                        if name.endswith('.csv') and 'baidu' not in name:
                            df = pd.read_csv(os.path.join(root, name), encoding='utf-8_sig', header=0, na_filter=False)
                            # if '日期' not in df.columns.tolist():
                            #     now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                            #     print(f'{now}{root_file} 缺少日期列, 不支持上传 mysql')
                            #     continue
                            if '日期' in df.columns.tolist():
                                df['日期'] = df['日期'].apply(lambda x: pd.to_datetime(x) if x else x)
                                df = df[df['日期'] >= start_date]
                            if len(df) == 0:
                                continue
                            self.df_to_mysql(df=df, db_name=db_name, tabel_name=root_file)
            elif os.path.isfile(f_path):
                if f_path.endswith('.csv') and 'baidu' not in f_path:
                    df = pd.read_csv(f_path, encoding='utf-8_sig', header=0, na_filter=False)
                    # if '日期' not in df.columns.tolist():
                    #     now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                    #     print(f'{now}{root_file} 缺少日期列, 不支持上传 mysql')
                    #     continue
                    if '日期' not in df.columns.tolist():
                        df['日期'] = df['日期'].apply(lambda x: pd.to_datetime(x) if x else x)
                        df = df[df['日期'] >= start_date]
                    if len(df) == 0:
                        continue
                    table = f'{os.path.splitext(root_file)[0]}_f'  # 这里定义了文件表会加 _f 后缀
                    self.df_to_mysql(df=df, db_name=db_name, tabel_name=table)

    # @try_except
    def read_mysql(self, tabel_name, start_date, end_date, db_name='远程数据源', ):
        start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        df = pd.DataFrame()

        connection = pymysql.connect(**self.config)  # 连接数据库
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
                database_exists = cursor.fetchone()
                if not database_exists:
                    print(f"Database {db_name} 数据库不存在")
                    return df
                else:
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                    print(f'{now}mysql 正在查询表: {tabel_name}, 范围: {start_date}~{end_date}')
        except:
            return df
        finally:
            connection.close()  # 断开连接

        before_time = time.time()
        # 读取数据
        self.config.update({'database': db_name})
        connection = pymysql.connect(**self.config)  # 重新连接数据库
        try:
            with connection.cursor() as cursor:
                # 获取指定日期范围的数据
                sql = f"SELECT * FROM {db_name}.{tabel_name} WHERE {'日期'} BETWEEN '%s' AND '%s'" % (start_date, end_date)
                cursor.execute(sql)
                rows = cursor.fetchall()  # 获取查询结果
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)  # 转为 df
        except Exception as e:
            print(f'{e} {db_name} -> {tabel_name} 表不存在')
            return df
        finally:
            connection.close()

        if len(df) == 0:
            print(f'database: {db_name}, table: {tabel_name} 查询的数据为空')
        else:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
            cost_time = int(time.time() - before_time)
            if cost_time < 1:
                cost_time = round(time.time() - before_time, 2)
            print(f'{now}mysql ({self.host}) 表: {tabel_name} 获取数据长度: {len(df)}, 用时: {cost_time} 秒')
        return df


class OptimizeDatas:
    """
    数据维护 删除 mysql 的冗余数据
    更新过程:
    1. 读取所有数据表
    2. 遍历表, 遍历列, 如果存在日期列则按天遍历所有日期, 不存在则全表读取
    3. 按天删除所有冗余数据(存在日期列时)
    tips: 查找冗余数据的方式是创建一个临时迭代器, 逐行读取数据并添加到迭代器, 出现重复时将重复数据的 id 添加到临时列表, 按列表 id 执行删除
    """
    def __init__(self, username: str, password: str, host: str, port: int, charset: str = 'utf8mb4'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port  # 默认端口, 此后可能更新，不作为必传参数
        self.charset = charset
        self.config = {
            'host': self.host,
            'port': self.port,
            'user': self.username,
            'password': self.password,
            'charset': self.charset,  # utf8mb4 支持存储四字节的UTF-8字符集
            'cursorclass': pymysql.cursors.DictCursor,
        }
        self.db_name_lists: list = []  # 更新多个数据库 删除重复数据
        self.db_name = None
        self.days: int = 63  # 对近 N 天的数据进行排重
        self.end_date = None
        self.start_date = None
        self.connection = None

    @staticmethod
    def try_except(func):  # 在类内部定义一个异常处理方法
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'{func.__name__}, {e}')  # 将异常信息返回

        return wrapper

    def optimize_list(self):
        """
        更新多个数据库 移除冗余数据
        需要设置 self.db_name_lists
        """
        if not self.db_name_lists:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
            print(f'{now}尚未设置参数: self.db_name_lists')
            return
        for db_name in self.db_name_lists:
            self.db_name = db_name
            self.optimize()

    def optimize(self):
        """ 更新一个数据库 移除冗余数据 """
        if not self.db_name:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
            print(f'{now}尚未设置参数: self.db_name')
            return
        tables = self.table_list(db_name=self.db_name)
        if not tables:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
            print(f'{now}{self.db_name} -> 数据表不存在')
            return

        # 日期初始化
        if not self.end_date:
            self.end_date = pd.to_datetime(datetime.datetime.today())
        else:
            self.end_date = pd.to_datetime(self.end_date)
        if self.days:
            self.start_date = pd.to_datetime(self.end_date - datetime.timedelta(days=self.days))
        if not self.start_date:
            self.start_date = self.end_date
        else:
            self.start_date = pd.to_datetime(self.start_date)
        start_date_before = self.start_date
        end_date_before = self.end_date

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
        print(f'{now}mysql({self.host}: {self.port}) {self.db_name} 数据库优化中(日期长度: {self.days} 天)...')
        for table_dict in tables:
            for key, table_name in table_dict.items():
                # if '店铺指标' not in table_name:
                #     continue
                self.config.update({'database': self.db_name})  # 添加更新 config 字段
                self.connection = pymysql.connect(**self.config)
                with self.connection.cursor() as cursor:
                    sql = f"SELECT 1 FROM {table_name} LIMIT 1"
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if not result:
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                        print(f'{now}数据表: {table_name}, 数据长度为 0')
                        continue  # 检查数据表是否为空

                    cursor.execute(f"SHOW FULL COLUMNS FROM {table_name}")  # 查询数据表的列信息
                    columns = cursor.fetchall()
                    date_exist = False
                    for col in columns:  # 遍历列信息，检查是否存在类型为日期的列
                        if col['Field'] == '日期' and (col['Type'] == 'date' or col['Type'].startswith('datetime')):
                            date_exist = True
                            break
                    if date_exist:  # 存在日期列
                        sql_max = f"SELECT MAX(日期) AS max_date FROM {table_name}"
                        sql_min = f"SELECT MIN(日期) AS min_date FROM {table_name}"
                        cursor.execute(sql_max)
                        max_result = cursor.fetchone()
                        cursor.execute(sql_min)
                        min_result = cursor.fetchone()
                        # print(min_result['min_date'], max_result['max_date'])
                        # 匹配修改为合适的起始和结束日期
                        if self.start_date < pd.to_datetime(min_result['min_date']):
                            self.start_date = pd.to_datetime(min_result['min_date'])
                        if self.end_date > pd.to_datetime(max_result['max_date']):
                            self.end_date = pd.to_datetime(max_result['max_date'])
                        dates_list = self.day_list(start_date=self.start_date, end_date=self.end_date)
                        for date in dates_list:
                            self.delete_duplicate(table_name=table_name, date=date)
                        self.start_date = start_date_before  # 重置，不然日期错乱
                        self.end_date = end_date_before
                    else:  # 不存在日期列的情况
                        self.delete_duplicate2(table_name=table_name)

                    # 5. 重置自增列 (id 列)
                    try:
                        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE 'id'")
                        result = cursor.fetchone()
                        if result:
                            cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN id;")  # 删除 id  列
                        cursor.execute(
                            f"ALTER TABLE {table_name} ADD column id INT AUTO_INCREMENT PRIMARY KEY FIRST;")
                        cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")  # 设置自增从 1 开始
                    except Exception as e:
                        print(f'{e}')
                        self.connection.rollback()
                self.connection.close()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
        print(f'{now}mysql({self.host}: {self.port}) {self.db_name} 数据库优化完成!')

    def delete_duplicate(self, table_name, date):
        datas = self.table_datas(db_name=self.db_name, table_name=str(table_name), date=date)
        if not datas:
            return
        duplicate_id = []  # 出现重复的 id
        all_datas = []  # 迭代器
        for data in datas:
            delete_id = data['id']
            del data['id']
            data = re.sub(r'\.0+\', ', '\', ', str(data))  # 统一移除小数点后面的 0
            if data in all_datas:  # 数据出现重复时
                duplicate_id.append(delete_id)  # 添加 id 到 duplicate_id
                continue
            all_datas.append(data)  # 数据没有重复
        del all_datas

        if not duplicate_id:  # 如果没有重复数据，则跳过该数据表
            return

        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(duplicate_id))
                # 移除冗余数据
                sql = f"DELETE FROM {table_name} WHERE id IN ({placeholders})"
                cursor.execute(sql, duplicate_id)
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                print(f"{now}{table_name} -> {date.strftime('%Y-%m-%d')} before: {len(datas)}, remove: {cursor.rowcount}")
            self.connection.commit()  # 提交事务
        except Exception as e:
            print(f'{self.db_name}/{table_name}, {e}')
            self.connection.rollback()  # 异常则回滚

    def delete_duplicate2(self, table_name):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * FROM {table_name}"  # 如果不包含日期列，则获取全部数据
            cursor.execute(sql)
            datas = cursor.fetchall()
        if not datas:
            return
        duplicate_id = []  # 出现重复的 id
        all_datas = []  # 迭代器
        for data in datas:
            delete_id = data['id']
            del data['id']
            data = re.sub(r'\.0+\', ', '\', ', str(data))  # 统一移除小数点后面的 0
            if data in all_datas:  # 数据出现重复时
                duplicate_id.append(delete_id)  # 添加 id 到 duplicate_id
                continue
            all_datas.append(data)  # 数据没有重复
        del all_datas

        if not duplicate_id:  # 如果没有重复数据，则跳过该数据表
            return

        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(duplicate_id))
                # 移除冗余数据
                sql = f"DELETE FROM {table_name} WHERE id IN ({placeholders})"
                cursor.execute(sql, duplicate_id)
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                print(f"{now}{table_name} -> before: {len(datas)}, "
                      f"remove: {cursor.rowcount}")
            self.connection.commit()  # 提交事务
        except Exception as e:
            print(f'{self.db_name}/{table_name}, {e}')
            self.connection.rollback()  # 异常则回滚

    def database_list(self):
        """ 获取所有数据库 """
        connection = pymysql.connect(**self.config)  # 连接数据库
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()  # 获取所有数据库的结果
        connection.close()
        return databases

    def table_list(self, db_name):
        """ 获取指定数据库的所有数据表 """
        connection = pymysql.connect(**self.config)  # 连接数据库
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
                database_exists = cursor.fetchone()
                if not database_exists:
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
                    print(f'{now}{db_name}: 数据表不存在!')
                    return
        except Exception as e:
            print(f'002 {e}')
            return
        finally:
            connection.close()  # 断开连接

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = pymysql.connect(**self.config)  # 重新连接数据库
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()  # 获取所有数据表
        connection.close()
        return tables

    def table_datas(self, db_name, table_name, date):
        """
        获取指定数据表的数据, 按天获取
        """
        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = pymysql.connect(**self.config)
        try:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM {table_name} WHERE {'日期'} BETWEEN '%s' AND '%s'" % (date, date)
                cursor.execute(sql)
                results = cursor.fetchall()
        except Exception as e:
            print(f'001 {e}')
        finally:
            connection.close()
        return results

    def day_list(self, start_date, end_date):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        date_list = []
        while start_date <= end_date:
            date_list.append(pd.to_datetime(start_date.date()))
            start_date += datetime.timedelta(days=1)
        return date_list

    def rename_column(self):
        """ 批量修改数据库的列名 """
        """
        # for db_name in ['京东数据2', '天猫数据2', '市场数据2', '生意参谋数据2', '生意经2', '属性设置2',]:
        #     s = OptimizeDatas(username=username, password=password, host=host, port=port)
        #     s.db_name = db_name
        #     s.rename_column()
        """
        tables = self.table_list(db_name=self.db_name)
        for table_dict in tables:
            for key, table_name in table_dict.items():
                self.config.update({'database': self.db_name})  # 添加更新 config 字段
                self.connection = pymysql.connect(**self.config)
                with self.connection.cursor() as cursor:
                    cursor.execute(f"SHOW FULL COLUMNS FROM {table_name}")  # 查询数据表的列信息
                    columns = cursor.fetchall()
                    columns = [{column['Field']: column['Type']} for column in columns]
                    for column in columns:
                        for key, value in column.items():
                            if key.endswith('_'):
                                new_name = re.sub(r'_+$', '', key)
                                sql = f"ALTER TABLE {table_name} CHANGE COLUMN {key} {new_name} {value}"
                                cursor.execute(sql)
                self.connection.commit()
        if self.connection:
            self.connection.close()


def year_month_day(start_date, end_date):
    """
    使用date_range函数和DataFrame来获取从start_date至end_date之间的所有年月日
    calendar.monthrange： 获取当月第一个工作日的星期值(0,6) 以及当月天数
    """
    # 替换年月日中的日, 以便即使传入当月日期也有返回值
    try:
        start_date = f'{pd.to_datetime(start_date).year}-{pd.to_datetime(start_date).month}-01'
    except Exception as e:
        print(e)
        return []
    # 使用pandas的date_range创建一个日期范围，频率为'MS'代表每月开始
    date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
    # 转换格式
    year_months = date_range.strftime('%Y-%m').drop_duplicates().sort_values()

    results = []
    for year_month in year_months:
        year = re.findall(r'(\d{4})', year_month)[0]
        month = re.findall(r'\d{4}-(\d{2})', year_month)[0]
        s, d = calendar.monthrange(int(year), int(month))
        results.append({'起始日期': f'{year_month}-01', '结束日期': f'{year_month}-{d}'})

    return results  # start_date至end_date之间的所有年月日


def download_datas(tabel_name, save_path, start_date):
    username, password, host, port = get_myconf.select_config_values(target_service='home_lx', database='mysql')
    print(username, password, host, port)
    m = MysqlUpload(username=username, password=password, host=host, port=port)
    m.port = port
    results = year_month_day(start_date=start_date, end_date='today')
    # print(results)
    for result in results:
        start_date = result['起始日期']
        end_date = result['结束日期']
        # print(start_date, end_date)
        df = m.read_mysql(db_name='天猫数据1', tabel_name=tabel_name, start_date=start_date, end_date=end_date)
        if len(df) == 0:
            continue
        path = os.path.join(save_path, f'{tabel_name}_{str(start_date)}_{str(end_date)}.csv')
        df['日期'] = df['日期'].apply(lambda x: re.sub(' .*', '', str(x)))
        df.to_csv(path, index=False, encoding='utf-8_sig', header=True)


if __name__ == '__main__':
    username, password, host, port = get_myconf.select_config_values(target_service='home_lx', database='mysql')
    print(username, password, host, port)



