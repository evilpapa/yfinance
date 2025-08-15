import curl_cffi
from typing import Union
import warnings

from yfinance.const import _QUERY1_URL_, _SENTINEL_
from yfinance.data import YfData
from ..utils import dynamic_docstring, generate_list_table_from_dict_universal

from .query import EquityQuery as EqyQy
from .query import FundQuery as FndQy
from .query import QueryBase, EquityQuery, FundQuery

_SCREENER_URL_ = f"{_QUERY1_URL_}/v1/finance/screener"
_PREDEFINED_URL_ = f"{_SCREENER_URL_}/predefined/saved"

PREDEFINED_SCREENER_BODY_DEFAULTS = {
    "offset":0, "count":25, "userId":"","userIdType":"guid"
}

PREDEFINED_SCREENER_QUERIES = {
    'aggressive_small_caps': {"sortField":"eodvolume", "sortType":"desc",
                            "query": EqyQy('and', [EqyQy('is-in', ['exchange', 'NMS', 'NYQ']), EqyQy('lt', ["epsgrowth.lasttwelvemonths", 15])])},
    'day_gainers': {"sortField":"percentchange", "sortType":"DESC",
                    "query": EqyQy('and', [EqyQy('gt', ['percentchange', 3]), EqyQy('eq', ['region', 'us']), EqyQy('gte', ['intradaymarketcap', 2000000000]), EqyQy('gte', ['intradayprice', 5]), EqyQy('gt', ['dayvolume', 15000])])},
    'day_losers': {"sortField":"percentchange", "sortType":"ASC",
                    "query": EqyQy('and', [EqyQy('lt', ['percentchange', -2.5]), EqyQy('eq', ['region', 'us']), EqyQy('gte', ['intradaymarketcap', 2000000000]), EqyQy('gte', ['intradayprice', 5]), EqyQy('gt', ['dayvolume', 20000])])},
    'growth_technology_stocks': {"sortField":"eodvolume", "sortType":"desc",
                                "query": EqyQy('and', [EqyQy('gte', ['quarterlyrevenuegrowth.quarterly', 25]), EqyQy('gte', ['epsgrowth.lasttwelvemonths', 25]), EqyQy('eq', ['sector', 'Technology']), EqyQy('is-in', ['exchange', 'NMS', 'NYQ'])])},
    'most_actives': {"sortField":"dayvolume", "sortType":"DESC",
                    "query": EqyQy('and', [EqyQy('eq', ['region', 'us']), EqyQy('gte', ['intradaymarketcap', 2000000000]), EqyQy('gt', ['dayvolume', 5000000])])},
    'most_shorted_stocks': {"count":25, "offset":0, "sortField":"short_percentage_of_shares_outstanding.value", "sortType":"DESC", 
                            "query": EqyQy('and', [EqyQy('eq', ['region', 'us']), EqyQy('gt', ['intradayprice', 1]), EqyQy('gt', ['avgdailyvol3m', 200000])])},
    'small_cap_gainers': {"sortField":"eodvolume", "sortType":"desc", 
                        "query": EqyQy("and", [EqyQy("lt", ["intradaymarketcap",2000000000]), EqyQy("is-in", ["exchange", "NMS", "NYQ"])])},
    'undervalued_growth_stocks': {"sortType":"DESC", "sortField":"eodvolume", 
                                "query": EqyQy('and', [EqyQy('btwn', ['peratio.lasttwelvemonths', 0, 20]), EqyQy('lt', ['pegratio_5y', 1]), EqyQy('gte', ['epsgrowth.lasttwelvemonths', 25]), EqyQy('is-in', ['exchange', 'NMS', 'NYQ'])])},
    'undervalued_large_caps': {"sortField":"eodvolume", "sortType":"desc", 
                            "query": EqyQy('and', [EqyQy('btwn', ['peratio.lasttwelvemonths', 0, 20]), EqyQy('lt', ['pegratio_5y', 1]), EqyQy('btwn', ['intradaymarketcap', 10000000000, 100000000000]), EqyQy('is-in', ['exchange', 'NMS', 'NYQ'])])},
    'conservative_foreign_funds': {"sortType":"DESC", "sortField":"fundnetassets",
                                "query": FndQy('and', [FndQy('is-in', ['categoryname', 'Foreign Large Value', 'Foreign Large Blend', 'Foreign Large Growth', 'Foreign Small/Mid Growth', 'Foreign Small/Mid Blend', 'Foreign Small/Mid Value']), FndQy('is-in', ['performanceratingoverall', 4, 5]), FndQy('lt', ['initialinvestment', 100001]), FndQy('lt', ['annualreturnnavy1categoryrank', 50]), FndQy('is-in', ['riskratingoverall', 1, 2, 3]), FndQy('eq', ['exchange', 'NAS'])])},
    'high_yield_bond': {"sortType":"DESC", "sortField":"fundnetassets",
                        "query": FndQy('and', [FndQy('is-in', ['performanceratingoverall', 4, 5]), FndQy('lt', ['initialinvestment', 100001]), FndQy('lt', ['annualreturnnavy1categoryrank', 50]), FndQy('is-in', ['riskratingoverall', 1, 2, 3]), FndQy('eq', ['categoryname', 'High Yield Bond']), FndQy('eq', ['exchange', 'NAS'])])},
    'portfolio_anchors': {"sortType":"DESC", "sortField":"fundnetassets",
                        "query": FndQy('and', [FndQy('eq', ['categoryname', 'Large Blend']), FndQy('is-in', ['performanceratingoverall', 4, 5]), FndQy('lt', ['initialinvestment', 100001]), FndQy('lt', ['annualreturnnavy1categoryrank', 50]), FndQy('eq', ['exchange', 'NAS'])])},
    'solid_large_growth_funds': {"sortType":"DESC", "sortField":"fundnetassets",
                                "query": FndQy('and', [FndQy('eq', ['categoryname', 'Large Growth']), FndQy('is-in', ['performanceratingoverall', 4, 5]), FndQy('lt', ['initialinvestment', 100001]), FndQy('lt', ['annualreturnnavy1categoryrank', 50]), FndQy('eq', ['exchange', 'NAS'])])},
    'solid_midcap_growth_funds': {"sortType":"DESC", "sortField":"fundnetassets",
                                "query": FndQy('and', [FndQy('eq', ['categoryname', 'Mid-Cap Growth']), FndQy('is-in', ['performanceratingoverall', 4, 5]), FndQy('lt', ['initialinvestment', 100001]), FndQy('lt', ['annualreturnnavy1categoryrank', 50]), FndQy('eq', ['exchange', 'NAS'])])},
    'top_mutual_funds': {"sortType":"DESC", "sortField":"percentchange",
                        "query": FndQy('and', [FndQy('gt', ['intradayprice', 15]), FndQy('is-in', ['performanceratingoverall', 4, 5]), FndQy('gt', ['initialinvestment', 1000]), FndQy('eq', ['exchange', 'NAS'])])}
}

@dynamic_docstring({"predefined_screeners": generate_list_table_from_dict_universal(PREDEFINED_SCREENER_QUERIES, bullets=True, title='Predefined queries (Dec-2024)')})
def screen(query: Union[str, EquityQuery, FundQuery],
            offset: int = None, 
            size: int = None,
            count: int = None,
            sortField: str = None, 
            sortAsc: bool = None,
            userId: str = None, 
            userIdType: str = None, 
            session = None, proxy = _SENTINEL_):
    """
    运行筛选器：预定义查询或自定义查询。

    :参数:
        * 只有在 query = EquityQuery 或 FundQuery 时才应用默认值
        query : str | Query:
            要执行的查询，可以是预定义的名称或自定义查询。
        offset : int
            结果的偏移量。默认为0。
        size : int
            返回的结果数。默认为100，最大为250（Yahoo）。
            对预定义查询使用count。
        count : int
            返回的结果数。默认为25，最大为250（Yahoo）。
            对自定义查询使用size。
        sortField : str
            排序字段。默认为 "ticker"。
        sortAsc : bool
            是否升序排序？默认为False。
        userId : str
            用户ID。默认为空。
        userIdType : str
            用户ID类型（例如，"guid"）。默认为 "guid"。
    """

    if proxy is not _SENTINEL_:
        warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
        _data = YfData(session=session, proxy=proxy)
    else:
        _data = YfData(session=session)

    defaults = {
        'offset': 0,
        'count': 25,
        'sortField': 'ticker',
        'sortAsc': False,
        'userId': "",
        'userIdType': "guid"
    }

    if count is not None and count > 250:
        raise ValueError("Yahoo limits query count to 250, reduce count.")

    if size is not None and size > 250:
        raise ValueError("Yahoo limits query size to 250, reduce size.")

    if offset is not None and isinstance(query, str):
        post_query = PREDEFINED_SCREENER_QUERIES[query]
        query = post_query['query']
        if sortField is None:
            sortField = post_query['sortField']
        if sortAsc is None:
            sortAsc = post_query['sortType'].lower() == 'asc'
        defaults = {}

    fields = {'offset': offset, 'count': count, "size": size, 'sortField': sortField, 'sortAsc': sortAsc, 'userId': userId, 'userIdType': userIdType}

    params_dict = {"corsDomain": "finance.yahoo.com", "formatted": "false", "lang": "en-US", "region": "US"}

    post_query = None
    if isinstance(query, str):
        if size is not None:
            warnings.warn("Screen 'size' argument is deprecated for predefined screens, set 'count' instead.", DeprecationWarning, stacklevel=2)
            count = size
            size = None
            fields['count'] = fields['size']
            del fields['size']

        params_dict['scrIds'] = query
        for k,v in fields.items():
            if v is not None:
                params_dict[k] = v
        resp = _data.get(url=_PREDEFINED_URL_, params=params_dict)
        try:
            resp.raise_for_status()
        except curl_cffi.requests.exceptions.HTTPError:
            if query not in PREDEFINED_SCREENER_QUERIES:
                print(f"yfinance.screen: '{query}' is probably not a predefined query.")
            raise
        return resp.json()["finance"]["result"][0]

    elif isinstance(query, QueryBase):
        for k in defaults:
            if k not in fields or fields[k] is None:
                fields[k] = defaults[k]
        fields['sortType'] = 'ASC' if fields['sortAsc'] else 'DESC'
        del fields['sortAsc']

        post_query = fields
        post_query['query'] = query

    else:
        raise ValueError(f'Query must be type str or QueryBase, not "{type(query)}"')

    if query is None:
        raise ValueError('No query provided')

    if isinstance(post_query['query'], EqyQy):
        post_query['quoteType'] = 'EQUITY'
    elif isinstance(post_query['query'], FndQy):
        post_query['quoteType'] = 'MUTUALFUND'
    post_query['query'] = post_query['query'].to_dict()

    response = _data.post(_SCREENER_URL_, 
                            body=post_query, 
                            params=params_dict)
    response.raise_for_status()
    return response.json()['finance']['result'][0]
