"""
此模块用于获取公共选修课数据，
包含数据获取、分页处理和数据解析等功能。
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import config
from session.session import generate_headers

# 创建包全局线程池
# 线程池大小根据系统资源和API并发限制设置，这里设置为10个线程
GLOBAL_THREAD_POOL = ThreadPoolExecutor(
    max_workers=50, thread_name_prefix="MathX")

# 通用的并行页面获取函数
def _fetch_pages_concurrently(url, form_template, headers, total_pages, start_page=1, verbose=True):
    """
    并行获取指定URL的多个页面数据

    Args:
        url: 请求URL
        form_template: 表单模板
        headers: 请求头
        total_pages: 总页数
        start_page: 起始页码，默认为1
        verbose: 是否显示详细信息

    Returns:
        所有页面的合并数据列表
    """
    all_data = []
    futures = []

    # 定义单个页面获取函数
    def fetch_single_page(page_num):
        try:
            # 设置当前页的参数
            current_form = form_template.copy()
            current_form['sEcho'] = str(page_num)
            current_form['iDisplayStart'] = str((page_num - 1) * 15)

            # 生成请求体字符串
            form_data_str = '&'.join(
                [f'{k}={v}' for k, v in current_form.items()])

            # 发送POST请求
            if verbose:
                print(f"正在并行获取第{page_num}页数据...")
            response = requests.post(
                url,
                headers=headers,
                data=form_data_str,
                timeout=10
            )

            # 检查响应状态并解析JSON
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if 'aaData' in json_data and len(json_data['aaData']) > 0:
                        return json_data['aaData']
                except Exception as e:
                    if verbose:
                        print(f"第{page_num}页数据解析失败: {str(e)}")
        except Exception as e:
            if verbose:
                print(f"获取第{page_num}页数据时发生错误: {str(e)}")
        return []

    # 提交页面获取任务（从start_page开始）
    for page in range(start_page, total_pages + 1):
        futures.append(GLOBAL_THREAD_POOL.submit(fetch_single_page, page))
        # 添加短暂延迟避免请求过于集中
        time.sleep(0.1)

    # 收集结果
    for future in as_completed(futures):
        try:
            page_data = future.result()
            if page_data:
                all_data.extend(page_data)
        except Exception as e:
            if verbose:
                print(f"处理页面数据时发生错误: {str(e)}")

    return all_data

# 通识课
def get_ggxxkxk_data(verbose: bool = True):
    """
    获取公共选修课数据，包括多页内容

    :param verbose: 是否输出详细日志信息，默认为True
    :return: 所有页面的课程数据列表
    """
    # 目标URL
    target_url = config.BASE_URL + \
        'xsxkkc/xsxkGgxxkxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false&szjylb=&xq=&szkclb='

    # 表单参数模板
    form_template = {
        'iColumns': '15',
        'sColumns': '',
        'iDisplayLength': '15',
        'mDataProp_0': 'kch',
        'mDataProp_1': 'kcmc',
        'mDataProp_2': 'xf',
        'mDataProp_3': 'skls',
        'mDataProp_4': 'xqid',
        'mDataProp_5': 'sksj',
        'mDataProp_6': 'skdd',
        'mDataProp_7': 'xxrs',
        'mDataProp_8': 'xkrs',
        'mDataProp_9': 'czrs',
        'mDataProp_10': 'syrs',
        'mDataProp_11': 'bj',
        'mDataProp_12': 'ctsm',
        'mDataProp_13': 'szkcflmc',
        'mDataProp_14': 'czOper'
    }

    all_data = []

    if verbose:
        print("开始获取公共选修课数据...")

    try:
        # 先获取第一页数据以确定总页数
        current_form = form_template.copy()
        current_form['sEcho'] = '1'
        current_form['iDisplayStart'] = '0'

        # 生成请求体字符串
        form_data_str = '&'.join([f'{k}={v}' for k, v in current_form.items()])
        content_length = len(form_data_str.encode('utf-8'))

        # 生成请求头
        headers = generate_headers(
            cookies=config.COOKIES,
            is_post=True,
            content_length=content_length
        )
        # 添加特定的头部
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['Referer'] = 'http://jwxt.gdufe.edu.cn/jsxsd/xsxk/xsxkGgxxkxk'
        headers['Accept'] = '*/*'

        # 发送POST请求
        if verbose:
            print("正在获取第1页数据以确定总页数...")
        response = requests.post(
            target_url,
            headers=headers,
            data=form_data_str,
            timeout=10
        )

        # 检查响应状态
        if response.status_code == 200:
            # 解析JSON响应
            try:
                json_data = response.json()
                # 提取课程数据
                if 'aaData' in json_data:
                    all_data.extend(json_data['aaData'])

                    # 计算总页数
                    total_records = json_data.get('iTotalRecords', 0)
                    total_pages = (total_records + 14) // 15  # 向上取整

                    if verbose:
                        print(f"找到{total_records}条记录，共{total_pages}页")

                    # 如果有多于1页的数据，并行获取剩余页面
                    if total_pages > 1:
                        # 并行获取第2到第total_pages页的数据
                        additional_data = _fetch_pages_concurrently(
                            target_url, form_template, headers, total_pages, start_page=2, verbose=verbose
                        )
                        all_data.extend(additional_data)
            except Exception as e:
                if verbose:
                    print(f"数据解析失败: {str(e)}")
        else:
            if verbose:
                print(f"请求失败，状态码：{response.status_code}")
    except Exception as e:
        if verbose:
            print(f"获取数据时发生错误：{str(e)}")

    if verbose:
        print(f"数据获取完成，共获取{len(all_data)}条课程记录")
    return all_data

# 专业选修
def get_xxxkxk_data(verbose: bool = True):
    """
    获取专业选修数据，包括多页内容

    :param verbose: 是否输出详细日志信息，默认为True
    :return: 所有页面的课程数据列表
    """
    # 目标URL
    target_url = config.BASE_URL + 'xsxkkc/xsxkXxxk'

    # 表单参数模板
    form_template = {
        'iColumns': '14',
        'sColumns': '',
        'iDisplayLength': '15',
        'mDataProp_0': 'kch',
        'mDataProp_1': 'kcmc',
        'mDataProp_2': 'xf',
        'mDataProp_3': 'skls',
        'mDataProp_4': 'xqid',
        'mDataProp_5': 'sksj',
        'mDataProp_6': 'skdd',
        'mDataProp_7': 'xxrs',
        'mDataProp_8': 'xkrs',
        'mDataProp_9': 'czrs',
        'mDataProp_10': 'syrs',
        'mDataProp_11': 'bj',
        'mDataProp_12': 'ctsm',
        'mDataProp_13': 'czOper'
    }

    all_data = []

    if verbose:
        print("开始获取专业选修课程数据...")

    try:
        # 先获取第一页数据以确定总页数
        current_form = form_template.copy()
        current_form['sEcho'] = '1'
        current_form['iDisplayStart'] = '0'

        # 生成请求体字符串
        form_data_str = '&'.join([f'{k}={v}' for k, v in current_form.items()])
        content_length = len(form_data_str.encode('utf-8'))

        # 生成请求头
        headers = generate_headers(
            cookies=config.COOKIES,
            is_post=True,
            content_length=content_length
        )
        # 添加特定的头部
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['Referer'] = 'http://jwxt.gdufe.edu.cn/jsxsd/xsxkkc/comeInXxxk'
        headers['Accept'] = '*/*'

        # 发送POST请求
        if verbose:
            print("正在获取第1页数据以确定总页数...")
        response = requests.post(
            target_url,
            headers=headers,
            data=form_data_str,
            timeout=10
        )

        # 检查响应状态
        if response.status_code == 200:
            # 解析JSON响应
            try:
                json_data = response.json()
                # 提取课程数据
                if 'aaData' in json_data:
                    all_data.extend(json_data['aaData'])

                    # 计算总页数
                    total_records = json_data.get('iTotalRecords', 0)
                    total_pages = (total_records + 14) // 15  # 向上取整

                    if verbose:
                        print(f"找到{total_records}条记录，共{total_pages}页")

                    # 如果有多于1页的数据，并行获取剩余页面
                    if total_pages > 1:
                        # 并行获取第2到第total_pages页的数据
                        additional_data = _fetch_pages_concurrently(
                            target_url, form_template, headers, total_pages, start_page=2, verbose=verbose
                        )
                        all_data.extend(additional_data)
            except Exception as e:
                if verbose:
                    print(f"数据解析失败: {str(e)}")
        else:
            if verbose:
                print(f"请求失败，状态码：{response.status_code}")
    except Exception as e:
        if verbose:
            print(f"获取数据时发生错误：{str(e)}")

    if verbose:
        print(f"数据获取完成，共获取{len(all_data)}条课程记录")
    return all_data

# 学科基础，专业必修
def get_xxkxk_data(verbose: bool = True):
    """
    获取学科基础，专业必修数据，包括多页内容

    :param verbose: 是否输出详细日志信息，默认为True
    :return: 所有页面的课程数据列表
    """
    # 目标URL
    target_url = config.BASE_URL + 'xsxkkc/xsxkBxxk'

    # 表单参数模板
    form_template = {
        'iColumns': '14',
        'sColumns': '',
        'iDisplayLength': '15',
        'mDataProp_0': 'kch',
        'mDataProp_1': 'kcmc',
        'mDataProp_2': 'xf',
        'mDataProp_3': 'skls',
        'mDataProp_4': 'xqid',
        'mDataProp_5': 'sksj',
        'mDataProp_6': 'skdd',
        'mDataProp_7': 'xxrs',
        'mDataProp_8': 'xkrs',
        'mDataProp_9': 'czrs',
        'mDataProp_10': 'syrs',
        'mDataProp_11': 'bj',
        'mDataProp_12': 'ctsm',
        'mDataProp_13': 'czOper'
    }

    all_data = []

    if verbose:
        print("开始获取学科基础、专业必修课程数据...")

    try:
        # 先获取第一页数据以确定总页数
        current_form = form_template.copy()
        current_form['sEcho'] = '1'
        current_form['iDisplayStart'] = '0'

        # 生成请求体字符串
        form_data_str = '&'.join([f'{k}={v}' for k, v in current_form.items()])
        content_length = len(form_data_str.encode('utf-8'))

        # 生成请求头
        headers = generate_headers(
            cookies=config.COOKIES,
            is_post=True,
            content_length=content_length
        )
        # 添加特定的头部
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['Referer'] = 'http://jwxt.gdufe.edu.cn/jsxsd/xsxkkc/comeInBxxk'
        headers['Accept'] = '*/*'

        # 发送POST请求
        if verbose:
            print("正在获取第1页数据以确定总页数...")
        response = requests.post(
            target_url,
            headers=headers,
            data=form_data_str,
            timeout=10
        )

        # 检查响应状态
        if response.status_code == 200:
            # 解析JSON响应
            try:
                json_data = response.json()
                # 提取课程数据
                if 'aaData' in json_data:
                    all_data.extend(json_data['aaData'])

                    # 计算总页数
                    total_records = json_data.get('iTotalRecords', 0)
                    total_pages = (total_records + 14) // 15  # 向上取整

                    if verbose:
                        print(f"找到{total_records}条记录，共{total_pages}页")

                    # 如果有多于1页的数据，并行获取剩余页面
                    if total_pages > 1:
                        # 并行获取第2到第total_pages页的数据
                        additional_data = _fetch_pages_concurrently(
                            target_url, form_template, headers, total_pages, start_page=2, verbose=verbose
                        )
                        all_data.extend(additional_data)
            except Exception as e:
                if verbose:
                    print(f"数据解析失败: {str(e)}")
        else:
            if verbose:
                print(f"请求失败，状态码：{response.status_code}")
    except Exception as e:
        if verbose:
            print(f"获取数据时发生错误：{str(e)}")

    if verbose:
        print(f"数据获取完成，共获取{len(all_data)}条课程记录")
    return all_data
