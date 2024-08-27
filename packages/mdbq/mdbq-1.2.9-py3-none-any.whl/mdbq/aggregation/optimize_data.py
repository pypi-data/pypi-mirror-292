# -*- coding: UTF-8 –*-
from mdbq.mysql import mysql
from mdbq.config import get_myconf
"""
对指定数据库所有冗余数据进行清理
"""


def op_data(service_databases, days: int = 63):
    for service_database in service_databases:
        for service_name, database in service_database.items():
            username, password, host, port = get_myconf.select_config_values(target_service=service_name, database=database)
            s = mysql.OptimizeDatas(username=username, password=password, host=host, port=port)
            s.db_name_lists = [
                '聚合数据',
            ]
            s.days = days
            s.optimize_list()


if __name__ == '__main__':
    op_data(service_databases=[{'home_lx': 'mysql'}], days=3650)
