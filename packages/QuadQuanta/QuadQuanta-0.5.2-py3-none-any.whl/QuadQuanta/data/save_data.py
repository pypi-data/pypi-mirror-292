#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   fetch_jqdata.py
@Time    :   2021/05/07
@Author  :   levonwoo
@Version :   0.1
@Contact :
@License :   (C)Copyright 2020-2021
@Desc    :   None
"""

import datetime
import re
import time
import os
import numpy as np

import jqdatasdk as jq
import pandas as pd
# from clickhouse_driver import Client
from clickhouse_connect import get_client, driver
from dateutil.parser import parse
from QuadQuanta.config import config
from QuadQuanta.data.clickhouse_api import (create_clickhouse_database,
                                            create_clickhouse_table,
                                            drop_click_table, insert_clickhouse,
                                            query_exist_date,
                                            query_exist_max_datetime)
from QuadQuanta.data.data_trans import pd_to_tuplelist
from QuadQuanta.data.get_data import (get_jq_bars, get_jq_trade_days,
                                      get_trade_days)
from QuadQuanta.data.mongodb_api import save_mongodb
from QuadQuanta.utils.logs import logger
from tqdm import tqdm


def save_bars(start_time=config.start_date,
              end_time='2014-01-10',
              frequency='daily',
              database='jqdata',
              continued=True):
    """
    保存起始时间内所有聚宽股票数据到clickhouse

    Parameters
    ----------
    start_time : str, optional
        开始时间, by default config.start_date
    end_time : str, optional
        结束时间, by default '2014-01-10'
    frequency : str, optional
        数据频率, by default 'daily'
    database : str, optional
        数据库名, by default 'jqdata'
    continued : bool, optional
        是否接着最大日期更新, by default True

    Raises
    ------
    Exception
        [description]
    Exception
        [description]
    """
    # 解析日期是否合法，非法则使用默认日期
    try:
        start_time = str(parse(start_time))
    except Exception as e:
        logger.error(e)
        logger.warning("非法的开始日期，使用2005-01-01作为开始日期")
        start_time = '2005-01-01'

    try:
        end_time = str(parse(end_time))
    except Exception as e:
        logger.error(e)
        logger.warning("非法的结束日期，使用2100-01-01作为结束日期")
        end_time = '2100-01-01'

    if start_time < start_time[:10] + ' 09:00:00':
        start_time = start_time[:10] + ' 09:00:00'

    if end_time < end_time[:10] + ' 09:00:00':
        end_time = end_time[:10] + ' 17:00:00'

    if start_time > end_time:
        raise Exception('开始日期大于结束日期')

    # 强制转换start_time, end_time时间改为9:00:00和17:00
    client = get_client(host=config.clickhouse_IP,
                        username=config.clickhouse_user,
                        password=config.clickhouse_password)
    create_clickhouse_database(database, client)
    client = get_client(host=config.clickhouse_IP,
                        username=config.clickhouse_user,
                        password=config.clickhouse_password,
                        database=database)

    current_hour = datetime.datetime.now().hour
    today = datetime.datetime.today()
    # 交易日收盘前更新,只更新到昨日数据
    if str(today)[:10] <= end_time[:10]:
        end_time = str(today)[:10]
        if current_hour < 16:
            end_time = str(today - datetime.timedelta(1))[:10]

    # 统一日期格式
    try:
        time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        start_time = start_time + ' 09:00:00'
    try:
        time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        end_time = end_time + ' 17:00:00'
    jq.auth(config.jqusername, config.jqpasswd)
    # 表不存在则创建相应表
    create_clickhouse_table(frequency, client)
    # 这种方式获取股票列表会有NAN数据，且需要转换股票代码格式
    stock_pd = jq.get_all_securities().assign(code=lambda x: x.index)
    code_list = stock_pd['code'].apply(lambda x: str(x)[:6]).unique().tolist()

    if continued:
        exist_max_datetime = query_exist_max_datetime(code_list, frequency,
                                                      client)[0][0]

        # 从最大datetime的次日开始
        if str(exist_max_datetime) > config.start_date:  # 默认'2014-01-01'
            start_time = str(exist_max_datetime + datetime.timedelta(hours=18))
        else:
            if start_time <= config.start_date:  # 默认'2014-01-01'
                start_time = config.start_date + ' 9:00:00'
            start_time = start_time

    if start_time <= end_time:
        date_range = get_trade_days(start_time, end_time)
        exist_date_range = query_exist_date(start_time=start_time,
                                            end_time=end_time,
                                            frequency=frequency,
                                            client=client)
        for i in tqdm(range(len(date_range))):
            time.sleep(0.05)
            if date_range[i] not in exist_date_range:
                # 分钟数据查询剩余流量
                if frequency in ['min', 'minute']:
                    spare_jqdata = jq.get_query_count()['spare']
                    if spare_jqdata // (240 * len(code_list)) < 1:
                        raise Exception('保存分钟数据流量不足')

                try:
                    insert_clickhouse(
                        get_jq_bars(code_list,
                                    str(date_range[i])[:10],
                                    str(date_range[i])[:10], frequency),
                        frequency, client)
                except Exception as e:
                    logger.warning(f"{date_range[i]}:error:{e}")
                    # raise Exception('Insert acution error', str(date_range[i])[:10])
                    continue
    else:
        logger.warning('日期段数据已保存')


def save_bars_from_json(filename,
                        frequency='daily',
                        database='jqdata',
                        continued=True):
    """
    从文件保存聚宽股票数据到clickhouse

    Parameters
    ----------
    filename : 文件名称
        文件名：默认以日期+json后缀组成
    frequency : str, optional
        数据频率, by default 'daily'
    database : str, optional
        数据库名, by default 'jqdata'
    continued : bool, optional
        是否接着最大日期更新,防止重复插入数据, by default True

    Raises
    ------
    Exception
        [description]
    Exception
        [description]
    """
    try:
        # 默认表为空
        table_name = ''
        # 判断文件是否存在
        if not (os.path.exists(filename)):
            raise FileNotFoundError("未找到文件")

        # 提取filename中的日期信息
        current_date_str = re.search(r"\d{4}-\d{2}-\d{2}", filename).group()
        current_date = datetime.datetime.strptime(current_date_str, "%Y-%m-%d")

        client = get_client(host=config.clickhouse_IP,
                            username=config.clickhouse_user,
                            password=config.clickhouse_password)
        create_clickhouse_database(database, client)
        client = get_client(host=config.clickhouse_IP,
                            username=config.clickhouse_user,
                            password=config.clickhouse_password,
                            database=database)

        if continued:
            exist_max_datetime = query_exist_max_datetime(None, frequency,
                                                          client)[:10]
            exist_max_datetime = datetime.datetime.strptime(exist_max_datetime, "%Y-%m-%d")
            if exist_max_datetime > current_date:
                raise Exception("当前日期已保存")
        pd_data = pd.read_json(filename)
        pd_data = pd_data.dropna(axis=0, how='any')  # 删除包含NAN的行
        if len(pd_data) > 1000:
            pd_data['datetime'] = pd_data['time'].apply(lambda x: x / 1000)
            pd_data = pd_data.assign(
                amount=pd_data['money'],
                code=pd_data['code'].apply(lambda x: x[:6]),  # code列聚宽格式转为六位纯数字格式
                date=pd_data['datetime'].apply(
                    lambda x: str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x)))[0:10]),
                date_stamp=pd_data['datetime']).set_index('datetime',
                                                          drop=False,
                                                          inplace=False)
            if frequency in ['d', 'day', '1day', 'daily']:
                table_name = 'stock_day'
                # datetime时间戳转Datetime,# 加上7个小时时间戳，表示收盘UTC+8的15：00
                pd_data['datetime'] = pd_data['datetime'].map(
                    lambda x: datetime.datetime.utcfromtimestamp(x + 3600 * 7))

            elif frequency in ['min', 'minute', '1min']:
                table_name = 'stock_min'
                # datetime时间戳转Datetime,# 减去8小时时间戳。从utc时间转为UTC+8
                pd_data['datetime'] = pd_data['datetime'].map(
                    lambda x: datetime.datetime.utcfromtimestamp(x - 3600 * 8))
                pd_data['date_stamp'] = pd_data['date_stamp'].map(
                    lambda x: x - 3600 * 8)

            else:
                raise NotImplementedError

            pd_data.drop(columns=['time', 'money'], inplace=True)

            base_keys_list = [
                'datetime', 'code', 'open', 'close', 'high', 'low', 'volume', 'amount',
                'avg', 'high_limit', 'low_limit', 'pre_close', 'date', 'date_stamp'
            ]
            # 更改列顺序匹配clichhouse表
            pd_data = pd_data.reindex(columns=base_keys_list)
            create_clickhouse_table(frequency, client)
            client.insert_df(table_name, pd_data)
        else:
            raise Exception("数据不足，请检查json文件")
    except Exception as e:
        logger.error(e)


def save_trade_days(database='jqdata'):
    # TODO 待更新更改了clickhouse-connect后需要测试
    """
    从聚宽数据源更新交易日历

    Parameters
    ----------
    database : str, optional
        database名称, by default 'jqdata'
    """
    # 强制转换start_time, end_time时间改为9:00:00和17:00
    client = get_client(host=config.clickhouse_IP,
                        username=config.clickhouse_user,
                        password=config.clickhouse_password)
    create_clickhouse_database(database, client)
    client = get_client(host=config.clickhouse_IP,
                        username=config.clickhouse_user,
                        password=config.clickhouse_password,
                        database=database)

    # 删除原表, 重新更新
    drop_click_table('trade_days', client)
    create_clickhouse_table('trade_days', client)
    insert_clickhouse(pd_to_tuplelist(get_jq_trade_days(), 'trade_days'),
                      'trade_days', client)


def save_securities_info(code: str = None,
                         db_name='jqdata',
                         coll_name='securities_info'):
    """
    保存股票概况到mongodb数据库, 主键存在则更新,不存在则插入

    Parameters
    ----------
    code : str, optional
        标的六位数字代码, by default None, 表示获取所有标的.
    db_name : str, optional
        数据库名, by default 'jqdata'
    coll_name : str, optional
        collum名, by default 'securities_info'
    """
    jq.auth(config.jqusername, config.jqpasswd)
    if code:
        security_info = jq.get_security_info(jq.normalize_code(code))
        security_info_dict = security_info.__dict__

        security_info_dict['_id'] = security_info_dict['code'][:6]
        security_info_dict['start_date'] = str(security_info_dict['start_date'])
        security_info_dict['end_date'] = str(security_info_dict['end_date'])

        # 删除多余键值对
        del security_info_dict['code']
        del security_info_dict['parent']
        save_mongodb(db_name=db_name,
                     coll_name=coll_name,
                     document=security_info_dict)

    else:
        securities_info_pd = jq.get_all_securities()
        # 建立mongodb索引
        securities_info_pd['_id'] = securities_info_pd.index
        # 去除jqdata股票代码的后缀
        securities_info_pd['_id'] = securities_info_pd['_id'].apply(
            lambda x: x[:6])
        securities_info_pd['start_date'] = securities_info_pd[
            'start_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        securities_info_pd['end_date'] = securities_info_pd['end_date'].apply(
            lambda x: x.strftime('%Y-%m-%d'))
        documents = securities_info_pd.to_dict('records')
        for i in tqdm(range(len(documents))):
            item = documents[i]
            save_mongodb(db_name=db_name, coll_name=coll_name, document=item)


def get_workdays_np(start_date, end_date):
    dates = np.arange(start_date, end_date, dtype='datetime64[D]')
    weekdays = np.is_busday(dates)
    workdays = dates[weekdays]
    return workdays


def save_data_from_json(start_date, end_date, frequency='daily', database='jqdata', prefix='./',continued=True):
    """

    Parameters
    ----------
    start_date
    end_date
    frequency
    database
    prefix : 文件名前缀
    continued : bool, optional
        是否接着最大日期更新,防止重复插入数据, by default True
    Returns
    -------

    """

    trade_days = get_workdays_np(start_date, end_date)
    for day in trade_days:
        if frequency in ['d', 'day', 'daily']:
            # 当从其他文件调用时，相对路径就不对了
            # current_filename = f"../qstrategy/data/day/{str(day)}.json"
            current_filename = f"{prefix}{str(day)}.json"

            logger.info(current_filename)
            save_bars_from_json(current_filename, frequency=frequency, database=database, continued=continued)
        elif frequency in ['min', 'minute']:
            day = str(day)
            month = day[:7]
            for i in range(10):
                current_filename = f"{prefix}{month}/{day}/min{day}-{str(i)}.json"
                logger.info(current_filename)
                save_bars_from_json(current_filename, frequency=frequency, database=database, continued=continued)
        else:
            raise NotImplementedError


if __name__ == '__main__':
    # save_all_jqdata('2014-01-01 09:00:00',
    #                 '2021-05-08 17:00:00',
    #                 frequency='daily')
    # save_bars('2014-01-01 09:00:00',
    #           '2015-01-01 17:00:00',
    #           frequency='auction',
    #           database='test')
    # save_bars('2020-05-01 09:00:00',
    #           '2021-01-01 17:00:00',
    #           frequency='minute',
    #           database='jqdata_test',
    #           continued=False)
    # save_securities_info()
    # save_trade_days()
    # save_bars_from_json('../qstrategy/replay/daily_replay/json/2024-08-15.json', database="jqtest", continued=False)


    today_date = "2024-08-12"
    trade_days = get_workdays_np('2023-10-01', '2024-01-01')
    for day in reversed(trade_days):
        day = str(day)
        month = day[:7]
        for i in range(10):
            file_name = f"../../../../BackUp/DATA/{month}/{day}/min{day}-{str(i)}.json"

            # file_name = f"../qstrategy/data/min/{day}/min{day}-{str(i)}.json"
            logger.info(f"file name: {file_name}")
            save_bars_from_json(file_name, frequency='min', database="jqdata",
                                continued=False)

# save_data_from_json('2024-07-28', '2024-07-31')
