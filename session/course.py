"""
课程模块：负责获取选课轮次信息和进入选课系统
"""
import re
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import config
from .session import generate_headers

# 选课列表URL
XKLC_LIST_URL = f"{config.BASE_URL}xsxk/xklc_list"
# 选课入口URL
XSK_INDEX_URL = f"{config.BASE_URL}xsxk/xsxk_index"


def get_xklc_list() -> List[Dict[str, str]]:
    """
    获取选课轮次列表

    Returns:
        list[dict]: 包含选课轮次信息的字典列表
        每个字典包含:
            - year_term: 学年学期
            - xk_name: 轮次名称
            - start_time: 开始时间
            - end_time: 结束时间
            - jx0502zbid: 子系统入口参数
    """
    try:
        headers = generate_headers(cookies=config.COOKIES)
        headers["Referer"] = f"{config.BASE_URL}xskb/xskb_list.do"

        resp = requests.get(XKLC_LIST_URL, headers=headers, timeout=10)
        resp.raise_for_status()  # 直接抛异常，避免返回无效内容
        resp.encoding = resp.apparent_encoding

        return _parse_xklc_list(resp.text)

    except Exception as e:
        print(f"获取选课轮次列表失败: {e}")
        return []


def _parse_xklc_list(html: str) -> List[Dict[str, str]]:
    """解析 HTML 并提取选课轮次信息"""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="Nsb_r_list")
    if not table:
        print("[_parse_xklc_list] 未找到选课轮次表格")
        return []

    rows = table.find_all("tr")[1:]  # 跳过表头
    return [_extract_xklc_row(row) for row in rows if row]


def _extract_xklc_row(row) -> Dict[str, str]:
    """从表格行中提取一条选课轮次信息"""
    cells = row.find_all("td")
    if len(cells) < 7:
        return {}

    # 基本字段
    year_term = cells[0].get_text(strip=True)
    xk_name = cells[1].get_text(strip=True)
    start_time = cells[4].get_text(strip=True)
    end_time = cells[5].get_text(strip=True)

    # jx0502zbid
    jx0502zbid = ""
    enter_link = cells[6].find("a", string=re.compile(r"进入选课"))
    if enter_link and enter_link.has_attr("href"):
        match = re.search(r"jx0502zbid=([^&]+)", enter_link["href"])
        if match:
            jx0502zbid = match.group(1)

    return {
        "year_term": year_term,
        "xk_name": xk_name,
        "start_time": start_time,
        "end_time": end_time,
        "jx0502zbid": jx0502zbid,
    }


def enter_xsk_system(jx0502zbid: Optional[str] = None) -> bool:
    """
    进入选课系统入口

    Args:
        jx0502zbid: 子系统入口参数，如果为None则尝试从选课轮次列表中获取

    Returns:
        bool: 是否成功进入选课系统
    """
    try:
        # 如果没有提供jx0502zbid参数，则从选课轮次列表中获取
        if jx0502zbid is None:
            xklc_list = get_xklc_list()

            # 提取第一个选课轮次的jx0502zbid参数
            if xklc_list:
                jx0502zbid = xklc_list[0].get("jx0502zbid", "")
            else:
                print("[enter_xsk_system] 未获取到选课轮次信息")
                return False

        # 构建URL
        url = f"{XSK_INDEX_URL}?jx0502zbid={jx0502zbid}"

        # 准备请求头
        headers = generate_headers(cookies=config.COOKIES)
        # 设置Referer
        headers["Referer"] = f"{config.BASE_URL}xsxk/xklc_list?Ves632DSdyV=NEW_XSD_PYGL"

        # 发送GET请求
        response = requests.get(url, headers=headers,
                                timeout=10, allow_redirects=True)
        print(f"进入选课系统成功，响应时间: {response.elapsed.total_seconds()} 秒")
        return True

    except Exception as e:
        print(f"进入选课系统失败: {e}")
        return False