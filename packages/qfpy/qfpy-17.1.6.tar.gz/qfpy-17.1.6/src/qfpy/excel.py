"""
def include(df: DataFrame, col_name: str, value_list: list[Any])

def include_batch(df: DataFrame, col_value_dict: dict[str, list[Any]])

def exclude(df: DataFrame, col_name: str, value_list: list[Any])

def exclude_batch(df: DataFrame, col_value_dict: dict[str, list[Any]])
"""

from typing import Any

from pandas import DataFrame


def include(df: DataFrame, col_name: str, value_list: list[Any]):
    """
    描述：筛选「包括」指定列的数据
    """
    return df[df[col_name].isin(value_list)]

def include_batch(df: DataFrame, col_value_dict: dict[str, list[Any]]):
    """
    描述：「批量」筛选「包括」指定列的数据
    """
    for col_name, value_list in col_value_dict.items():
        df = include(df, col_name, value_list)
    return df

def exclude(df: DataFrame, col_name: str, value_list: list[Any]):
    """
    描述：筛选「排除」指定列的数据
    """
    return df[~df[col_name].isin(value_list)]

def exclude_batch(df: DataFrame, col_value_dict: dict[str, list[Any]]):
    """
    描述：「批量」筛选「排除」指定列的数据
    """
    for col_name, value_list in col_value_dict.items():
        df = exclude(df, col_name, value_list)
    return df