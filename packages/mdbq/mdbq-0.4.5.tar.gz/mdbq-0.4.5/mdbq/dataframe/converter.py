# -*- coding:utf-8 -*-
import pandas as pd
import numpy as np
import re


class DataFrameConverter(object):
    def __init__(self, df=pd.DataFrame({})):
        self.df = df

    def convert_df_cols(self, df=pd.DataFrame({})):
        """
        清理 dataframe 列名的不合规字符(mysql)
        对数据类型进行转换(尝试将 object 类型转为 int 或 float)
        """
        if len(df) == 0:
            df = self.df
            if len(df) == 0:
                return
        # dtypes = df.dtypes.apply(str).to_dict()  # 将 dataframe 数据类型转为字典形式
        df.replace([np.inf, -np.inf], 0, inplace=True)  # 清理一些非法值
        df.replace(to_replace=['\\N', '-', '--', '', 'nan'], value=0, regex=False, inplace=True)  # 替换掉特殊字符
        df.replace(to_replace=[','], value='', regex=True, inplace=True)
        df.replace(to_replace=['="'], value='', regex=True, inplace=True)  # ="和"不可以放在一起清洗, 因为有: id=86785565
        df.replace(to_replace=['"'], value='', regex=True, inplace=True)
        cols = df.columns.tolist()

        for col in cols:
            # df[col] = df[col].apply(lambda x: re.sub('[="]', '', str(x)) if '="' in str(x) else x)
            # 百分比在某些数据库中不兼容, 转换百分比为小数
            df[col] = df[col].apply(lambda x: float(float((str(x).rstrip("%"))) / 100) if str(x).endswith('%') and '~' not in str(x) else x)
            # 尝试转换合适的数据类型
            if df[col].dtype == 'object':
                try:
                    # df[col] = df[col].astype(int)  # 尝试转换 int
                    df[col] = df[col].apply(lambda x: int(x) if '_' not in str(x) else x)
                except:
                    # df[col] = df[col].astype('float64', errors='ignore')    # 尝试转换 float, 报错则忽略
                    try:
                        df[col] = df[col].apply(lambda x: float(x) if '_' not in str(x) else x)
                    except:
                        pass
            if df[col].dtype == 'float':  # 对于小数类型, 保留 6 位小数
                df[col] = df[col].apply(lambda x: round(float(x), 6) if x != 0 else x)
            # 清理列名, 在 mysql 里面列名不能含有某些特殊字符
            if '日期' in col or '时间' in col:
                try:
                    df[col] = df[col].apply(lambda x: pd.to_datetime(x))
                except:
                    pass
            new_col = col.lower()
            new_col = re.sub(r'[\',，（）()/=<>+\-*^"’\[\]~#|&% .;]', '_', new_col)
            new_col = re.sub(r'_+$', '', new_col)
            df.rename(columns={col: new_col}, inplace=True)
        df.fillna(0, inplace=True)
        return df


if __name__ == '__main__':
    # df = pd.DataFrame(np.random.randn(5, 3), columns=['a', 'b', 'c'])
    # converter = DataFrameConverter()
    # df = converter.convert_df_cols(df)
    # print(df['a'].dtype)
    # print(df)
    pattern = 'dfa_dfawr__'
    pattern = re.sub(r'_+$', '', pattern)
    print(pattern)