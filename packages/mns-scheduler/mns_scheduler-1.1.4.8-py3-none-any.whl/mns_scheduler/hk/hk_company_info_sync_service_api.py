import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import mns_common.api.em.east_money_stock_hk_api as east_money_stock_hk_api
import akshare as ak
import mns_common.constant.db_name_constant as db_name_constant
from mns_common.db.MongodbUtil import MongodbUtil
from functools import lru_cache

mongodb_util = MongodbUtil('27017')


# 获取陆股通的列表
@lru_cache(maxsize=None)
def get_hk_ggt_component():
    stock_hk_ggt_components_em_df = ak.stock_hk_ggt_components_em()
    stock_hk_ggt_components_em_df = stock_hk_ggt_components_em_df.rename(columns={
        "序号": "index",
        "代码": "symbol",
        "名称": "name"
    })
    return stock_hk_ggt_components_em_df


# 获取em cookie
@lru_cache(maxsize=None)
def get_em_cookie():
    query = {"type": "em_cookie"}
    stock_account_info = mongodb_util.find_query_data(db_name_constant.STOCK_ACCOUNT_INFO, query)
    cookie = list(stock_account_info['cookie'])[0]
    return cookie


# https://quote.eastmoney.com/center/gridlist.html#hk_stocks
def sync_hk_company_info():
    cookie = get_em_cookie()
    hk_real_time_df = east_money_stock_hk_api.hk_real_time_quotes(cookie)

    hk_real_time_df = hk_real_time_df[[
        "symbol",
        "name",
        "chg",
        "total_mv",
        "flow_mv",
        "list_date",
        "industry",
        "amount",
        "now_price"
    ]]
    # 排除基金
    hk_real_time_df = hk_real_time_df.loc[hk_real_time_df['total_mv'] != '-']

    stock_hk_ggt_components_em_df = get_hk_ggt_component()
    stock_hk_ggt_components_symbol_list = list(stock_hk_ggt_components_em_df['symbol'])
    hk_real_time_df['hk_ggt'] = False
    hk_real_time_df.loc[hk_real_time_df['symbol'].isin(stock_hk_ggt_components_symbol_list), 'hk_ggt'] = True
    hk_real_time_df.loc[hk_real_time_df['industry'] == '-', 'industry'] = '其他'

    hk_real_time_df['_id'] = hk_real_time_df['symbol']

    hk_real_time_df.fillna(0, inplace=True)

    mongodb_util.save_mongo(hk_real_time_df, db_name_constant.COMPANY_INFO_HK)


if __name__ == '__main__':
    sync_hk_company_info()
