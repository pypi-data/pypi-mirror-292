#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   get_data.py
@Time    :   2021/05/27
@Author  :   levonwoo
@Version :   0.2
@Contact :   
@License :   (C)Copyright 2020-2021
@Desc    :   获取数据模块
'''

import jqdatasdk as jq
import pandas as pd
from dateutil.parser import parse
from QuadQuanta import config
from QuadQuanta.const import *
from QuadQuanta.data.clickhouse_api import query_clickhouse, query_N_clickhouse
from QuadQuanta.data.data_trans import pd_to_tuplelist, tuplelist_to_np
from QuadQuanta.data.mongodb_api import query_mongodb
from QuadQuanta.utils.datetime_func import datetime_convert_stamp
from QuadQuanta.utils.logs import logger


def get_bars(code=None,
             start_time='1970-01-01',
             end_time='2100-01-01',
             frequency='daily',
             data_soure=DataSource.CLICKHOUSE,
             count=None,
             **kwargs):
    """
    通用K线获取接口，包括日线、分钟线、竞价。kwargs可选字段包括'client'：数据库连接,'format':返回数据类型

    Parameters
    ----------
    code : list or str, optional
        股票代码, by default None
    start_time : str, optional
        数据开始时间, by default '1970-01-01'
    end_time : str, optional
        数据结束时间, by default '2100-01-01'
    frequency : str, optional
        k线周期, by default 'daily'
    data_soure : str , optional
        数据源, by default DataSource.CLICKHOUSE
    count : int, optional
        时间序列个数, by default None
    kwargs: dict ,optional
        可选关键字有client:数据库连接,用于数据库后增量更新;format:指定返回值类型, np 或者 pd

    Returns
    -------
    pandas.DataFrame or numpy.ndarray 

    Raises
    ------
    NotImplementedError
        [description]
    """
    if data_soure == DataSource.JQDATA:
        return get_jq_bars(code, start_time, end_time, frequency, count,
                           **kwargs)
    elif data_soure == DataSource.CLICKHOUSE:
        return get_click_bars(code, start_time, end_time, frequency, count,
                              **kwargs)
    else:
        raise NotImplementedError


def get_jq_bars(code=None,
                start_time='1970-01-01',
                end_time='2100-01-01',
                frequency='daily',
                count=None,
                **kwargs):
    """
    从聚宽源获取起止时间内单个或多个聚宽股票并添加自定义字段

    Parameters
    ----------
    code : list or str, optional
        六位数字股票代码列表，如['000001'],['000001',...,'003039'],str会强制转换为list, by default None
    start_time : str, optional
        数据开始时间, by default '1970-01-01'
    end_time : str, optional
        数据结束时间, by default '2100-01-01'
    frequency : str, optional
        k线周期, by default 'daily'
    count : int, optional
        时间序列个数, by default None
    kwargs: dict ,optional
        可选关键字有client:数据库连接,用于数据库后增量更新;format:指定返回值类型, np 或者 pd

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    ValueError
        [description]
    NotImplementedError
        [description]
    NotImplementedError
        [description]
    Exception
        [description]
    """
    jq.auth(config.jqusername, config.jqpasswd)

    if isinstance(code, str):
        code = list(map(str.strip, code.split(',')))
    if len(code) == 0:
        raise ValueError('股票代码格式错误')

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

    if start_time < start_time[:10] + ' 09:00:00':
        start_time = start_time[:10] + ' 09:00:00'

    if end_time < end_time[:10] + ' 09:00:00':
        end_time = end_time[:10] + ' 17:00:00'

    columns = [
        'time', 'code', 'open', 'close', 'high', 'low', 'volume', 'money',
        'avg', 'high_limit', 'low_limit', 'pre_close'
    ]

    if frequency in ['d', 'day', 'daily']:
        frequency = 'daily'
    elif frequency in ['min', 'minute']:
        frequency = 'minute'
    elif frequency in ['call_auction', 'auction']:
        frequency = 'call_auction'
        columns = ['time', 'code', 'close', 'volume', 'amount']
    else:
        raise NotImplementedError

    empty_pd = pd.concat([pd.DataFrame({k: [] for k in columns}), None, None])

    _start_time = start_time
    if frequency in ['daily', 'minute']:
        if count:
            _start_time = None
            pd_data = jq.get_price(jq.normalize_code(code),
                                   start_date=_start_time,
                                   end_date=end_time,
                                   frequency=frequency,
                                   fields=[
                                       'open', 'close', 'high', 'low', 'volume',
                                       'money', 'avg', 'high_limit',
                                       'low_limit', 'pre_close'
                                   ],
                                   skip_paused=True,
                                   fq='none',
                                   count=count,
                                   panel=False)
        else:
            pd_data = jq.get_price(jq.normalize_code(code),
                                   start_date=_start_time,
                                   end_date=end_time,
                                   frequency=frequency,
                                   fields=[
                                       'open', 'close', 'high', 'low', 'volume',
                                       'money', 'avg', 'high_limit',
                                       'low_limit', 'pre_close'
                                   ],
                                   skip_paused=True,
                                   fq='none',
                                   count=None,
                                   panel=False)
        # TODO 有没有更优雅的方式
        pd_data['pre_close'].fillna(
            pd_data['open'], inplace=True)  # 新股上市首日分钟线没有pre_close数据，用当天开盘价填充

    elif frequency == 'call_auction':
        pd_data = jq.get_call_auction(jq.normalize_code(code),
                                      start_date=_start_time,
                                      end_date=end_time,
                                      fields=[
                                          'time',
                                          'current',
                                          'volume',
                                          'money',
                                      ])
    else:
        raise NotImplementedError
    pd_data = pd_data.dropna(axis=0, how='any')  # 删除包含NAN的行

    if len(pd_data) == 0:
        return empty_pd
    else:
        pd_data['datetime'] = pd_data['time']

        pd_data = pd_data.assign(
            amount=pd_data['money'],
            code=pd_data['code'].apply(lambda x: x[:6]),  # code列聚宽格式转为六位纯数字格式
            date=pd_data['datetime'].apply(lambda x: str(x)[0:10]),
            date_stamp=pd_data['datetime'].apply(
                lambda x: datetime_convert_stamp(x))).set_index('datetime',
                                                                drop=True,
                                                                inplace=False)
        if frequency == 'call_auction':
            pd_data = pd_data.assign(close=pd_data['current'])
        try:
            if kwargs['format'] in ['pd', 'pandas']:
                return pd_data
            elif kwargs['format'] in ['np', 'numpy']:
                return tuplelist_to_np(pd_to_tuplelist(pd_data, frequency),
                                       frequency)
        except:
            return pd_to_tuplelist(pd_data, frequency)


def get_click_bars(code=None,
                   start_time='1970-01-01',
                   end_time='2100-01-01',
                   frequency='daily',
                   count=None,
                   **kwargs):
    """
    从clickhouse数据库获取

    ----------
    code : list or str, optional
        六位数字股票代码列表，如['000001'],['000001',...,'003039'],str会强制转换为list, by default None
    start_time : str, optional
        数据开始时间, by default '1970-01-01'
    end_time : str, optional
        数据结束时间, by default '2100-01-01'
    frequency : str, optional
        k线周期, by default 'daily'
    count : int, optional
        时间序列个数, by default None
    kwargs: dict ,optional
        可选关键字有client:数据库连接,用于数据库后增量更新;format:指定返回值类型, np 或者 pd

    Returns
    -------
    [type]
        [description]
    """
    if count:
        res = query_N_clickhouse(count, code, start_time, end_time, frequency, **kwargs)
        try:
            if kwargs['format'] in ['pd', 'pandas']:
                return pd.DataFrame(res).set_index('datetime')
            else:
                return res
        except:
            return res
    else:
        res = query_clickhouse(code, start_time, end_time, frequency, **kwargs)
        try:
            if kwargs['format'] in ['pd', 'pandas']:
                return pd.DataFrame(res).set_index('datetime')
            else:
                return res
        except Exception as e:
            logger.debug(e)
            return res


def get_trade_days(start_time=None,
                   end_time=None,
                   datasource=DataSource.CLICKHOUSE,
                   **kwargs):
    """
    统一的交易日历获取函数, 默认从clickhouse数据库获取

    Parameters
    ----------
    start_time : str, optional
        开始时间, by default None
    end_time : str, optional
        结束时间, by default None
    datasource : DataSource, optional
        数据源, by default DataSource.CLICKHOUSE
    kwargs: dict, optional
        额外可选参数, 包括count:设置时间序列个数, database:设置clickhouse的database名称

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    NotImplementedError
        [description]
    """
    if datasource == DataSource.JQDATA:
        return get_jq_trade_days(start_time=start_time,
                                 end_time=end_time,
                                 **kwargs)
    elif datasource == DataSource.CLICKHOUSE:
        return get_click_trade_days(start_time=start_time,
                                    end_time=end_time,
                                    **kwargs)
    else:
        raise NotImplementedError


def get_jq_trade_days(start_time=None, end_time=None, **kwargs):
    """
    获取指定时间段内的聚宽交易日历

    Parameters
    ----------
    start_time : str, optional
        开始日期, by default None
    end_time : str, optional
        结束日期, by default None

    Returns
    -------
    DataFrame
        可通过format参数指定输出格式, 默认pandas.DataFrame
    """
    jq.auth(config.jqusername, config.jqpasswd)
    try:
        start_time = str(parse(start_time))
    except Exception as e:
        logger.error(e)
        logger.warning("非法的开始日期，获取2005-01-01作为开始日期")
        start_time = '2005-01-01'
    try:
        end_time = str(parse(end_time))
    except Exception as e:
        logger.error(e)
        logger.warning("非法的结束日期，使用2100-01-01作为结束日期")
        end_time = '2100-01-01'
    trade_days = jq.get_trade_days(start_time, end_time)

    pd_data = pd.DataFrame(trade_days, columns=['datetime'])
    return pd_data.assign(date=pd_data['datetime'].apply(lambda x: str(x)))


def get_click_trade_days(start_time=config.start_date,
                         end_time=None,
                         count=None,
                         **kwargs):
    """
    从clickhouse数据库获取指定时间段交易日历, 当count不为空时start_time变量无效

    Parameters
    ----------
    start_time : str, optional
        开始日期, by default None
    end_time : str, optional
        结束日期, by default None
    count : int, optional
        时间序列个数, by default None

    Returns
    -------
    np.ndarry
        返回字符串交易日期numpy列表
    """
    frequency = 'trade_days'
    if count:
        res = query_N_clickhouse(count=count,
                                 end_time=end_time,
                                 frequency=frequency,
                                 **kwargs)
        return res['date']
    else:
        res = query_clickhouse(start_time=start_time,
                               end_time=end_time,
                               frequency=frequency,
                               **kwargs)
        return res['date']


# TODO 获取复权因子
def get_adjust_factor(code,
                      start_date,
                      end_date,
                      adj_type='pre',
                      datasource=DataSource.JQDATA):
    """
    获取股票复权因子

    Parameters
    ----------
    code : list or str
        六位数字股票代码列表，如['000001'],['000001',...,'003039'],str会强制转换为list
    start_date : str
        开始日期
    end_date : str
        结束日期
    adj_type : str
        复权类型, 不复权为None, 前复权pre, 后复权post
    datasource : DataSource, optional
        数据源, by default DataSource.JQDATA

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    ValueError
        [description]
    NotImplementedError
        [description]
    """

    if isinstance(code, str):
        code = list(map(str.strip, code.split(',')))
    if len(code) == 0:
        raise ValueError('股票代码格式错误')

    if datasource == DataSource.JQDATA:
        jq.auth(config.jqusername, config.jqpasswd)
        return jq.get_price(jq.normalize_code(code),
                            start_date=start_date,
                            end_date=end_date,
                            fields=['factor'],
                            fq=adj_type)
    else:
        raise NotImplementedError


def get_securities_info(code: str = None,
                        db_name='jqdata',
                        coll_name='securities_info',
                        **kwargs):
    """
    从mongodb数据库获取标的概况

    Parameters
    ----------
    code : str, optional
        标的六位数字代码, by default None, 表示获取所有标的.
    db_name : str, optional
        数据库名, by default 'jqdata'
    coll_name : str, optional
        collum名, by default 'securities_info'

    Returns
    -------
    kwargs可指定返回值类型, 包括list和pandas结构
    """
    if code:
        sql = {"_id": code}
    else:
        sql = None
    return query_mongodb(db_name, coll_name, sql, **kwargs)


def get_jq_call_auction():
    """
    获取集合竞价数据
    Returns
    -------

    """
    pass


if __name__ == '__main__':
    # print(
    #     get_bars(['000001', '000002'],
    #              '2020-01-01',
    #              '2020-02-01',
    #              'daily',
    #              DataSource.CLICKHOUSE,
    #              format='pd'))
    print(get_jq_trade_days(None, '2020-01-02'))
    # print(get_trade_days('2020-01-01 09:00:00', '2020-02-03 17:00:00'))
    # print(
    #     get_adjust_factor(['000001'],
    #                       '2020-01-01',
    #                       '2020-02-01',
    #                       adj_type='pre'))
