#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   clickhouse_api.py
@Time    :   2021/05/07
@Author  :   levonwoo
@Version :   0.2
@Contact :
@License :   (C)Copyright 2020-2021
@Desc    :   clickhouse接口
"""

from itertools import chain
from datetime import datetime
from dateutil.relativedelta import relativedelta
# here put the import lib
import numpy as np
# from clickhouse_driver import Client
from clickhouse_connect import get_client, driver
from dateutil.parser import parse
from QuadQuanta.config import config
from QuadQuanta.data.data_trans import list_to_tuplelist, split_strings_in_list, tuplelist_to_np
from QuadQuanta.utils.common import is_sorted, removeDuplicates
from QuadQuanta.utils.logs import logger


def create_clickhouse_database(database: str,
                               client: driver.client.Client):
    """
    数据库不存在则创建clickhouse数据库

    Parameters
    ----------
    database : str
        数据库名
    client : clickhouse_connect.driver.client.Client, optional
        clickhouse客户端连接
    """
    if not client:
        client = get_client(host=config.clickhouse_IP, port=8123,
                             username=config.clickhouse_user,
                             password=config.clickhouse_password)
    create_database_sql = 'CREATE DATABASE IF NOT EXISTS %s' % database
    client.command(create_database_sql)


def create_clickhouse_table(data_type: str,
                            client: driver.client.Client):
    """
    创建clickhouse数据表

    Parameters
    ----------
    data_type : str
        存储表类型,已完成的有日线（daily）,一分钟线(minute),开盘竞价,交易日历
    client : Client, optional
        clickhouse的客户端连接, by default Client(host='127.0.0.1', database='jqdata')

    Raises
    ------
    NotImplementedError
        [description]
    """
    if not client:
        client = get_client(host=config.clickhouse_IP, port=8123,
                             username=config.clickhouse_user,
                             password=config.clickhouse_password, database='jqdata')

    # 设置分区 PARTITION BY to YYYYMMDD(datetime)
    if data_type in ['min', 'minute', '1min']:
        create_table_sql = 'CREATE TABLE IF NOT EXISTS stock_min (datetime DateTime,code String, open Float32, \
                           close Float32,high Float32,low Float32, volume Float64, amount Float64,avg Float32,  \
                           high_limit Float32,low_limit Float32,pre_close Float32, date String, date_stamp Float64) \
                            ENGINE = MergeTree() PARTITION BY toYYYYMMDD(datetime) ORDER BY (datetime, code)'
    elif data_type in ['d', 'day', '1day', 'daily']:
        create_table_sql = 'CREATE TABLE IF NOT EXISTS stock_day (datetime DateTime,code String, open Float32, \
                           close Float32,high Float32,low Float32, volume Float64, amount Float64,avg Float32,  \
                           high_limit Float32,low_limit Float32,pre_close Float32, date String, date_stamp Float64) \
                            ENGINE = MergeTree() PARTITION BY toYYYYMM(datetime) ORDER BY (datetime, code)'
    # 原始日线数据
    elif data_type in ['rawDay']:
        create_table_sql = 'CREATE TABLE IF NOT EXISTS stock_raw_day (datetime DateTime,code String, open Float32, \
                           close Float32,high Float32,low Float32, volume Float64, amount Float64, date String, \
                            date_stamp Float64)  ENGINE = MergeTree() ORDER BY (datetime, code)'

    elif data_type in ['auction', 'call_auction']:
        create_table_sql = 'CREATE TABLE IF NOT EXISTS call_auction (datetime DateTime,code String, close Float32, \
                           volume Float64, amount Float64, date String, date_stamp Float64) ENGINE = MergeTree() ' \
                           'ORDER BY (datetime, code)'

    elif data_type in ['trade_days']:
        create_table_sql = 'CREATE TABLE IF NOT EXISTS trade_days (datetime Date, date String) ENGINE = MergeTree() ' \
                           'ORDER BY (datetime)'
    else:
        raise NotImplementedError
    client.command(create_table_sql)


def drop_click_table(table_name: str,
                     client: driver.client.Client):
    """
    丢弃clickhouse表

    Parameters
    ----------
    table_name : str
        要丢弃的表名
    client : clickhouse_connect.driver.client.Client, optional
        clickhouse的客户端连接, by default get_client(host='127.0.0.1', database='jqdata')
    """
    if not client:
        client = get_client(host=config.clickhouse_IP, port=8123,
                             username=config.clickhouse_user,
                             password=config.clickhouse_password, database='jqdata')
    drop_sql = "DROP TABLE IF EXISTS %s" % table_name
    client.command(drop_sql)


def insert_clickhouse(data,
                      data_type,
                      client: driver.client.Client):
    """
    将数据插入clickhouse数据库

    Parameters
    ----------
    data : tuple_list
        元组数组类型数据,每个元组为一行
    data_type : str
        存储表类型,已完成的有日线（daily）,一分钟线(minute),开盘竞价,交易日历
    client : clickhouse_connect.driver.client.Client, optional
        clickhouse的客户端连接, by default get_client(host='127.0.0.1', database='jqdata')

    Raises
    ------
    NotImplementedError
        [description]
    """
    if not client:
        client = get_client(host=config.clickhouse_IP, port=8123,
                             username=config.clickhouse_user,
                             password=config.clickhouse_password, database='jqdata')

    if data_type in ['min', 'minute', '1min']:
        insert_data_sql = 'INSERT INTO stock_min (datetime, code, open, close, high, low, volume, amount,\
             avg, high_limit, low_limit, pre_close, date, date_stamp) VALUES'

    elif data_type in ['d', 'day', '1day', 'daily']:
        insert_data_sql = 'INSERT INTO stock_day (datetime, code, open, close, high, low, volume, amount,\
             avg, high_limit, low_limit, pre_close, date, date_stamp) VALUES'

    elif data_type in ['rawDay']:
        insert_data_sql = 'INSERT INTO stock_raw_day (datetime, code, open, close, high, low, volume, amount,\
            date, date_stamp) VALUES'

    elif data_type in ['auction', 'call_auction']:
        insert_data_sql = 'INSERT INTO call_auction (datetime, code, close, volume, amount, date, date_stamp) VALUES'

    elif data_type in ['trade_days']:
        insert_data_sql = 'INSERT INTO trade_days (datetime, date) VALUES'
    else:
        raise NotImplementedError
    # TODO
    # client.command(da)
    # client.insert_df()
    # client.command(cmd=insert_data_sql, data=data)


def query_exist_max_datetime(code=None,
                             type='daily',
                             client: driver.client.Client = None):
    """
    查询clickhouse表中某个code已经存在的最大日期, code=None表示表中的所有code

    Parameters
    ----------
    code : list, optional
        六位数股票代码列表,如['000001'], ['000001',...,'689009'], by default None
    type : str, optional
        数据类型,已完成的有日线（daily）,一分钟线(minute),竞价(call_auction),交易日历(trade_days), by default 'daily'
    client : clickhouse_connect.driver.client.Client, optional
        clickhouse的客户端连接, by default get_client(host='127.0.0.1', database='jqdata')

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    NotImplementedError
        [description]
    """
    if not client:
        client = get_client(host=config.clickhouse_IP, port=8123,
                             username=config.clickhouse_user,
                             password=config.clickhouse_password, database='jqdata')

    if isinstance(code, str):
        code = list(map(str.strip, code.split(',')))

    if type in ['day', 'daily', 'd']:
        table_name = 'stock_day'
    elif type in ['min', 'minute', '1min']:
        table_name = 'stock_min'
    elif type in ['auction', 'call_auction']:
        table_name = 'call_auction'
    else:
        raise NotImplementedError
    if code:
        if isinstance(code, str):
            code = list(map(str.strip, code.split(',')))
        max_datetime_sql = 'SELECT max(datetime) FROM %s' % table_name + ' ' + 'WHERE `code` IN %(code)s'
        res = client.command(max_datetime_sql, {'code': code})
    else:
        max_datetime_sql = 'SELECT max(datetime) FROM %s' % table_name
        res = client.command(max_datetime_sql)

    return res


def query_exist_date(code=None,
                     start_time='2000-01-01',
                     end_time='2200-01-01',
                     frequency='daily',
                     client: driver.client.Client = None):
    """
    查询clickhouse表中code在指定日期区间内已保存数据的日期列表, code=None表示表中的所有code

    Parameters
    ----------
    code : list, optional
        六位数股票代码列表,如['000001'], ['000001',...,'689009'], by default None
    start_time : str, optional
        [description], by default '2000-01-01'
    end_time : str, optional
        [description], by default '2200-01-01'
    frequency : str, optional
        数据类型,已完成的有日线（daily）,一分钟线(minute),竞价(call_auction), by default 'daily'
    client : clickhouse_connect.driver.client.Client, optional
        clickhouse的客户端连接, by default get_client(host='127.0.0.1', database='jqdata')

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    NotImplementedError
        [description]
    ValueError
        [description]
    Exception
        [description]
    """
    if not client:
        client = get_client(host=config.clickhouse_IP, port=8123,
                             username=config.clickhouse_user,
                             password=config.clickhouse_password, database='jqdata')

    if frequency in ['day', 'daily', 'd']:
        table_name = 'stock_day'
    elif frequency in ['min', 'minute', '1min']:
        table_name = 'stock_min'
    elif frequency in ['auction', 'call_auction']:
        table_name = 'call_auction'
    elif frequency in ['limit']:
        table_name = 'stock_day_limit'
    else:
        raise NotImplementedError

    try:
        start_time = str(parse(start_time))[:10]
    except Exception as e:
        logger.error(e)
        logger.info("非法的开始日期，使用2005-01-01作为开始日期")
        start_time = '2005-01-01'

    try:
        end_time = str(parse(end_time))[:10]
    except Exception as e:
        logger.error(e)
        logger.info("非法的结束日期，使用2100-01-01作为结束日期")
        end_time = '2100-01-01'

    #  判断日期合法
    if start_time > end_time:
        raise ValueError('开始时间大于结束时间')

    if code:
        if isinstance(code, str):
            code = list(map(str.strip, code.split(',')))
        sql = "SELECT DISTINCT x.date FROM %s x" % table_name + \
              " WHERE `date` >= %(start_time)s AND `date` <= %(end_time)s AND `code` IN %(code)s ORDER BY (`date`)"
        # 查询,返回数据类型为字符串
        res_str: str = client.command(sql, {
            'start_time': start_time,
            'end_time': end_time,
            'code': code
        })
    else:
        sql = "SELECT DISTINCT x.date FROM %s x" % table_name + \
              " WHERE `date` >= %(start_time)s AND `date` <= %(end_time)s  ORDER BY (`date`)"
        res_str = client.command(sql, {
            'start_time': start_time,
            'end_time': end_time,
        })
        print(type(res_str))
    # str转list
    res = res_str.split('\n')
    return res


def query_clickhouse(code: list = None,
                     start_time: str = '1970-01-01',
                     end_time: str = '2200-01-01',
                     frequency='daily',
                     database='jqdata',
                     client: driver.client.Client = None,
                     **kwargs) -> np.ndarray:
    """
    clickhouse查询接口,默认为None的条件,返回所有数据

    Parameters
    ----------
    code : list or str, optional
        六位数字股票代码列表, by default None
    start_time : str, optional
        开始日期, by default None
    end_time : str, optional
        结束日期, by default None
    frequency : str, optional
        数据周期, by default 'daily'
    database : str, optional
        clickhouse数据库名,默认从聚宽数据查询, by default 'jqdata'
    client: driver.client.Client, optional
        clickhouse client
    Returns
    -------
    np.ndarray
        [description]
    Raises
    ------
    ValueError
        [description]
    NotImplementedError
        [description]
    """
    if frequency in ['day', 'daily', 'd']:
        table_name = 'stock_day'
    elif frequency in ['min', 'minute', '1min']:
        table_name = 'stock_min'
    elif frequency in ['auction', 'call_auction']:
        table_name = 'call_auction'
    elif frequency in ['trade_days']:
        table_name = 'trade_days'
    else:
        raise NotImplementedError

    # 解析日期是否合法，非法则使用默认日期
    try:
        start_time = str(parse(start_time))
    except Exception as e:
        logger.error(e)
        logger.info("非法的开始日期，使用2005-01-01作为开始日期")
        start_time = '2005-01-01'

    try:
        end_time = str(parse(end_time))
    except Exception as e:
        logger.error(e)
        logger.info("非法的结束日期，使用2100-01-01作为结束日期")
        end_time = '2100-01-01'

    if table_name == 'trade_days':
        start_time = start_time[:10]
        end_time = end_time[:10]
    else:
        if start_time < start_time[:10] + ' 09:00:00':
            start_time = start_time[:10] + ' 09:00:00'

        if end_time < end_time[:10] + ' 09:00:00':
            end_time = end_time[:10] + ' 17:00:00'

    #  判断起始日期合法
    if start_time > end_time:
        raise ValueError('开始时间大于结束时间')
    if not client:
        client = get_client(host=config.clickhouse_IP,
                            username=config.clickhouse_user,
                            password=config.clickhouse_password,
                            database=database)

    if code:
        if isinstance(code, str):
            # TODO 是否是有效的股票代码
            code = list(map(str.strip, code.split(',')))
        # 注意WHERE前的空格
        sql = "SELECT DISTINCT x.* FROM %s x" % table_name + " WHERE `datetime` >= %(start_time)s " \
                                                             " AND `datetime` <= %(end_time)s AND `code` IN %(code)s " \
                                                             "ORDER BY (`datetime`, `code`)"

        # 查询,返回数据类型为数组且含有'\n'
        res_list = client.command(sql, {
            'start_time': start_time,
            'end_time': end_time,
            'code': code
        })
    else:
        sql = "SELECT DISTINCT x.* FROM %s x" % table_name + " WHERE `datetime` >= %(start_time)s " \
                                                             "AND `datetime` <= %(end_time)s" \
                                                             " ORDER BY (`datetime`, `code`)"

        if table_name == 'trade_days':
            sql = "SELECT DISTINCT x.* FROM %s x" % table_name + " WHERE `datetime` >= %(start_time)s" \
                                                                 " AND `datetime` <= %(end_time)s " \
                                                                 "ORDER BY (`datetime`)"

        res_list = client.command(sql, {
            'start_time': start_time,
            'end_time': end_time
        })
    #  TODO clickhouse分片

    # 默认有序条件下删除res_tuple_list重复数据
    # if is_sorted(res_tuple_list):
    #     res_tuple_list = removeDuplicates(res_tuple_list)
    # else:
    #     raise Exception('clickhouse返回列表非有序')

    res_split_list = split_strings_in_list(res_list)
    res_tuple_list = list_to_tuplelist(res_split_list, table_name)
    # 元组数组通过numpy结构化,注意数据长度code:8字符 date:10字符.可能存在问题
    return tuplelist_to_np(res_tuple_list, table_name)


def query_N_clickhouse(count: int,
                       code: list = None,
                       start_time: str = None,
                       end_time: str = '2200-01-01',
                       frequency='daily',
                       database='jqdata',
                       client: driver.client.Client = None,
                       **kwargs) -> np.ndarray:
    """
    获取结束日期之前的N个时间序列数据

    Parameters
    ----------
    count : int
        时间序列个数
    code : list, optional
        股票代码列表, by default None
    start_time : str, optional
        结束时间, by default '2014-01-01'
    end_time : str, optional
        结束时间, by default '2200-01-01'
    frequency : str, optional
        k线周期, by default 'daily'
    database : str, optional
        clickhouse数据库名, by default 'jqdata'
    client: driver.client.Client, optional
        clickhouse client

    Returns
    -------
    np.ndarray
        [description]

    Raises
    ------
    NotImplementedError
        [description]
    """

    if frequency in ['day', 'daily', 'd']:
        table_name = 'stock_day'
    elif frequency in ['min', 'minute', '1min']:
        table_name = 'stock_min'
    elif frequency in ['auction', 'call_auction']:
        table_name = 'call_auction'
    elif frequency in ['trade_days']:
        table_name = 'trade_days'
    else:
        raise NotImplementedError

    try:
        end_time = str(parse(end_time))
    except Exception as e:
        logger.error(e)
        logger.info("非法的结束日期，使用2100-01-01作为结束日期")
        end_time = '2100-01-01'

    if table_name == 'trade_days':
        end_time = end_time[:10]
    else:
        if end_time < end_time[:10] + ' 09:00:00':
            end_time = end_time[:10] + ' 17:00:00'

    if not start_time:
        if table_name == 'stock_day':
            # 日线查询默认默认查询一个月之内
            start_date = (
                    datetime.strptime(end_time[:10], "%Y-%m-%d")  # 转换为 datetime 对象
                    - relativedelta(months=1)  # 向前推一个月
            ).strftime("%Y-%m-%d")
            start_time = start_date + ' 09:00:00'
        elif table_name == 'stock_min':
            # 分钟线查询默认查询一天内
            start_time = end_time[:10] + ' 09:00:00'
        else:
            # 从数据库保存的起点查询
            start_time = '2014-01-01'
    if not client:
        client = get_client(host=config.clickhouse_IP,
                            username=config.clickhouse_user,
                            password=config.clickhouse_password,
                            database=database)
    # DESC 降序 使 LIMIT 返回离 end_time 最近的数据
    if code:
        if isinstance(code, str):
            code = list(map(str.strip, code.split(',')))
        sql = "SELECT DISTINCT x.* FROM %s x" % table_name + " WHERE `datetime` >= %(start_time)s AND`datetime` <= %(end_time)s \
        AND `code` IN %(code)s ORDER BY (`datetime`, `code`) DESC LIMIT %(limit)s by `code`"

        # 查询,返回数据类型为数组
        res_list = client.command(sql, {
            'start_time': start_time,
            'end_time': end_time,
            'code': code,
            'limit': count,
        })
    else:
        sql = "SELECT DISTINCT x.* FROM %s x " % table_name + " WHERE `datetime` >= %(start_time)s AND`datetime` <= %(end_time)s \
        ORDER BY (`datetime`, `code`) DESC LIMIT %(limit)s by `code`"

        if table_name == 'trade_days':
            sql = "SELECT DISTINCT x.* FROM %s x" % table_name + " WHERE `datetime` >= %(start_time)s AND `datetime` <= %(end_time)s \
            ORDER BY (`datetime`) DESC LIMIT %(limit)s"

        res_list = client.command(sql, {
            'start_time': start_time,
            'end_time': end_time,
            'limit': count,
        })

    res_split_list = split_strings_in_list(res_list)
    # 元组数组通过numpy结构化,注意数据长度code:8字符 date:10字符.可能存在问题
    # 倒序列表翻转
    res_tuplelist = list_to_tuplelist(res_split_list, table_name)
    res_tuplelist.reverse()
    return tuplelist_to_np(res_tuplelist, table_name)


if __name__ == '__main__':
    clickclient = get_client(host=config.clickhouse_IP, port=8123,
                             username=config.clickhouse_user,
                             password=config.clickhouse_password, database='jqdata')
    create_clickhouse_table('min', client=clickclient)
    # drop_click_table('stock_min', clickclient)
    # clickclient = get_client(host=config.clickhouse_IP, port=8123,
    #                          username=config.clickhouse_user,
    #                          password=config.clickhouse_password, database='jqdata')
    # print((query_exist_date(code='000001',start_time='2020-01-01',
    #                                 end_time='2020-05-11',
    #                                 client=clickclient)))

    # print(query_exist_max_datetime(code=None, type='daily',
    #                                client=clickclient))
    # print((query_clickhouse(start_time='2014-05-20',
    #                         end_time='2014-05-22',
    #                         frequency='daily',
    #                         database='jqdata')))
    print((query_N_clickhouse(2, '000001', frequency='min', end_time='2024-05-20 15:00:00')))
    # insert_clickhouse()
