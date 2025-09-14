"""
此模块用于筛选不同类型课程的重要信息，
支持筛选专业选修、学科基础/专业必修和公共选修课程，
并可批量筛选所有课程类型的信息。
"""
from .xsxk import get_ggxxkxk_data, get_xxkxk_data, get_xxxkxk_data


def filter_zy_courses(courses_data=None):
    """筛选专业选修课程的重要信息

    Args:
        courses_data: 可选，已获取的专业选修课程数据，如果为None则自动获取

    Returns:
        筛选后的专业选修课程列表
    """
    # 如果没有提供数据，则调用数据获取函数
    if courses_data is None:
        courses_data = get_xxxkxk_data(verbose=False)

    filtered_courses = []
    total_count = len(courses_data)

    for course in courses_data:
        # 检查冲突情况和剩余人数，任一条件满足则跳过该课程
        conflict_status = course.get("ctsm", "")
        remaining_slots = course.get("syrs", "")

        # 筛选条件：只有同时满足以下两个条件才保留课程
        # 条件一：冲突情况为空字符串
        # 条件二：剩余人数不是0且不是负数
        skip = False
        if conflict_status != "":
            skip = True
        else:
            # 检查剩余人数是否为0或负数
            try:
                # 尝试将剩余人数转换为整数进行比较
                slots_num = int(remaining_slots)
                if slots_num <= 0:
                    skip = True
            except (ValueError, TypeError):
                # 如果无法转换为整数，检查字符串是否为"0"或表示负数的字符串
                if remaining_slots == "0" or (isinstance(remaining_slots, str) and remaining_slots.startswith('-')):
                    skip = True
        
        if skip:
            continue

        filtered_course = {
            "选课代码": course.get("jx0404id", ""),  # 最重要的字段
            "学分": course.get("xf", ""),
            "上课老师": course.get("skls", ""),
            "上课教室": course.get("skdd", ""),
            "上课时间": course.get("sksj", ""),
            "科目名称": course.get("kcmc", ""),
            "冲突情况": conflict_status,
            "剩余人数": remaining_slots
        }
        filtered_courses.append(filtered_course)
    
    available_count = len(filtered_courses)
    print(f"专业选修课课程: 总条数({total_count}) 可用条数({available_count})")

    return filtered_courses


def filter_bx_courses(courses_data=None):
    """筛选学科基础/专业必修课程的重要信息

    Args:
        courses_data: 可选，已获取的学科基础/专业必修课程数据，如果为None则自动获取

    Returns:
        筛选后的学科基础/专业必修课程列表
    """
    # 如果没有提供数据，则调用数据获取函数
    if courses_data is None:
        courses_data = get_xxkxk_data(verbose=False)

    filtered_courses = []
    total_count = len(courses_data)

    for course in courses_data:
        # 检查冲突情况和剩余人数，任一条件满足则跳过该课程
        conflict_status = course.get("ctsm", "")
        remaining_slots = course.get("syrs", "")

        # 筛选条件：只有同时满足以下两个条件才保留课程
        # 条件一：冲突情况为空字符串
        # 条件二：剩余人数不是0且不是负数
        skip = False
        if conflict_status != "":
            skip = True
        else:
            # 检查剩余人数是否为0或负数
            try:
                # 尝试将剩余人数转换为整数进行比较
                slots_num = int(remaining_slots)
                if slots_num <= 0:
                    skip = True
            except (ValueError, TypeError):
                # 如果无法转换为整数，检查字符串是否为"0"或表示负数的字符串
                if remaining_slots == "0" or (isinstance(remaining_slots, str) and remaining_slots.startswith('-')):
                    skip = True
        
        if skip:
            continue

        filtered_course = {
            "选课代码": course.get("jx0404id", ""),  # 重要字段
            "学分": course.get("xf", ""),
            "上课老师": course.get("skls", ""),
            "上课教室": course.get("skdd", ""),
            "上课时间": course.get("sksj", ""),
            "科目名称": course.get("kcmc", ""),
            "冲突情况": conflict_status,
            "剩余人数": remaining_slots
        }
        filtered_courses.append(filtered_course)
    
    available_count = len(filtered_courses)
    print(f"学科基础专业必修课课程: 总条数({total_count}) 可用条数({available_count})")

    return filtered_courses


def filter_ts_courses(courses_data=None):
    """筛选公共选修课程的重要信息

    Args:
        courses_data: 可选，已获取的公共选修课程数据，如果为None则自动获取

    Returns:
        筛选后的公共选修课程列表
    """
    # 如果没有提供数据，则调用数据获取函数
    if courses_data is None:
        courses_data = get_ggxxkxk_data(verbose=False)

    filtered_courses = []
    total_count = len(courses_data)

    for course in courses_data:
        # 检查冲突情况和剩余人数，任一条件满足则跳过该课程
        conflict_status = course.get("ctsm", "")
        remaining_slots = course.get("syrs", "")

        # 筛选条件：只有同时满足以下两个条件才保留课程
        # 条件一：冲突情况为空字符串
        # 条件二：剩余人数不是0且不是负数
        skip = False
        if conflict_status != "":
            skip = True
        else:
            # 检查剩余人数是否为0或负数
            try:
                # 尝试将剩余人数转换为整数进行比较
                slots_num = int(remaining_slots)
                if slots_num <= 0:
                    skip = True
            except (ValueError, TypeError):
                # 如果无法转换为整数，检查字符串是否为"0"或表示负数的字符串
                if remaining_slots == "0" or (isinstance(remaining_slots, str) and remaining_slots.startswith('-')):
                    skip = True
        
        if skip:
            continue

        filtered_course = {
            "选课代码": course.get("jx0404id", ""),  # 重要字段
            "学分": course.get("xf", ""),
            "上课老师": course.get("skls", ""),
            "上课教室": course.get("skdd", ""),
            "上课时间": course.get("sksj", ""),
            "科目名称": course.get("kcmc", ""),
            "冲突情况": conflict_status,
            "剩余人数": remaining_slots
        }
        filtered_courses.append(filtered_course)
    
    available_count = len(filtered_courses)
    print(f"公共选修课课程: 总条数({total_count}) 可用条数({available_count})")

    return filtered_courses


def filter_all_courses(futures=None):
    """批量筛选所有课程类型的重要信息

    Args:
        futures: 可选，包含三种课程数据的future对象元组，格式为(公共选修future, 学科基础/专业必修future, 专业选修future)
                 如果为None则自动创建并执行

    Returns:
        包含所有类型筛选后课程的字典
    """
    # 如果没有提供future对象，则直接使用各个筛选函数
    if futures is None:
        return {
            "专业选修课": filter_zy_courses(),
            "学科基础专业必修课": filter_bx_courses(),
            "公共选修课": filter_ts_courses()
        }

    # 如果提供了future对象，则从中获取数据
    try:
        # 正确解析futures元组：(公共选修future, 学科基础/专业必修future, 专业选修future)
        ggxxkxk_future, xxkxk_future, xxxkxk_future = futures

        # 获取所有future的结果
        ggxxkxk_data = ggxxkxk_future.result()  # 公共选修数据
        xxkxk_data = xxkxk_future.result()      # 学科基础/专业必修数据
        xxxkxk_data = xxxkxk_future.result()    # 专业选修数据

        return {
            "专业选修课": filter_zy_courses(xxxkxk_data),
            "学科基础专业必修课": filter_bx_courses(xxkxk_data),
            "公共选修课": filter_ts_courses(ggxxkxk_data)
        }
    except Exception as e:
        # 处理可能的异常，确保即使出现问题也能返回部分结果
        print(f"筛选课程数据时发生错误: {e}")
        # 回退到默认行为
        return {
            "专业选修课": filter_zy_courses(),
            "学科基础专业必修课": filter_bx_courses(),
            "公共选修课": filter_ts_courses()
        }
