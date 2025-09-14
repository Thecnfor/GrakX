"""
获取课程模块
"""
from .xsxk import get_ggxxkxk_data, get_xxkxk_data, get_xxxkxk_data, GLOBAL_THREAD_POOL
from .filter import filter_zy_courses, filter_bx_courses, filter_ts_courses, filter_all_courses


def get_class():
    """
    并行获取三种课程数据
    
    Returns:
        包含三种课程数据的future对象元组，格式为(公共选修future, 学科基础/专业必修future, 专业选修future)
    """
    # 使用全局线程池并行获取三种课程数据
    future1 = GLOBAL_THREAD_POOL.submit(get_ggxxkxk_data, verbose=False)
    future2 = GLOBAL_THREAD_POOL.submit(get_xxkxk_data, verbose=False)
    future3 = GLOBAL_THREAD_POOL.submit(get_xxxkxk_data, verbose=False)
    return future1, future2, future3


def get_and_filter_all_courses():
    """
    并行获取并筛选所有课程数据
    
    Returns:
        包含所有类型筛选后课程的字典
    """
    # 并行获取所有课程数据
    futures = get_class()
    # 使用获取的数据进行筛选
    return filter_all_courses(futures)

__all__ = [
    "get_ggxxkxk_data",
    "get_xxkxk_data",
    "get_xxxkxk_data",
    "GLOBAL_THREAD_POOL",
    "get_class",
    "get_and_filter_all_courses",
    "filter_zy_courses",
    "filter_bx_courses",
    "filter_ts_courses",
    "filter_all_courses"
]
