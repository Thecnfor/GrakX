"""
会话确权
"""
import time
import requests
from session.ocr import verify_code
import config

# 鉴权URL
VERIFY_URL = config.BASE_URL + 'verifycode.servlet'
LOGINTO_URL = config.BASE_URL + 'xk/LoginToXkLdap'
# 主页面URL用于检查登录状态
MAIN_PAGE_URL = config.BASE_URL + 'framework/main.jsp'
# 全局变量，用于跟踪上一次的登录状态
_LAST_LOGIN_STATUS = None

# 用于POST请求的额外头部信息
POST_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://jwxt.gdufe.edu.cn'
}

# 定义基础请求头，这些是爬虫常用且相对固定的头部信息，针对该网站设置

BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
    'Cache-Control': 'max-age=0',
    'Host': 'jwxt.gdufe.edu.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://jwxt.gdufe.edu.cn/jsxsd/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0'
}

# 定义一个函数，用于生成完整的请求头，支持动态传入 Cookie 和自定义头部


def generate_headers(cookies: dict, is_post: bool = False, content_length=None):
    """
    生成完整的请求头，支持动态传入 Cookie 和自定义参数

    :param cookies: Cookie 字典，用于添加到请求头中
    :param is_post: 是否为 POST 请求，默认为 False
    :param content_length: 请求内容长度，若为 POST 请求且提供该参数，则添加到请求头中
    :return: 包含所有请求头信息的字典
    """
    # 使用基础请求头作为默认值
    final_headers = BASE_HEADERS.copy()

    # 如果是POST请求，添加POST特有的头部
    if is_post:
        final_headers.update(POST_HEADERS)
        # 如果提供了content_length，则添加Content-Length头部
        if content_length is not None:
            final_headers['Content-Length'] = str(content_length)

    # 若传入了cookies参数，则将其转换为字符串并添加到请求头中
    if cookies:
        # 将cookies字典转换为符合HTTP协议的Cookie字符串
        cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
        final_headers['Cookie'] = cookie_str

    # 打印生成的请求头，方便调试
    # print("生成的请求头:", final_headers)
    return final_headers


# 自动登录直到成功

def login():
    """
    自动登录函数，持续尝试登录直到成功。
    在每次尝试中，会获取验证码、调用 OCR 识别，然后使用识别结果进行登录请求。
    会根据响应结果判断登录是否成功，失败则继续尝试。
    """
    success = False
    attempt_count = 0

    while not success:
        attempt_count += 1
        # print(f"第{attempt_count}次尝试登录...")

        # 获取验证码
        headers = generate_headers(cookies=config.COOKIES)
        x = requests.get(VERIFY_URL, headers=headers, timeout=10)
        captcha_bytes = x.content

        # 获取用户输入的验证码+OCR识别
        try:
            # 调用OCR识别验证码（直接传递字节流）
            user_input_code = verify_code(img_bytes=captcha_bytes)
            # 去除用户输入中的空白字符
            user_input_code = user_input_code.strip()
        except Exception as e:
            print(f"获取验证码输入失败: {e}")
            # 如果输入失败，使用默认值
            user_input_code = ""
            # 继续下一次循环，重新尝试获取验证码
            continue

        # 设置表单数据，使用用户输入的验证码
        form_data = {
            'USERNAME': config.USERNAME,
            'PASSWORD': config.PASSWORD,
            'RANDOMCODE': user_input_code
        }
        # 计算表单数据的长度（这里是固定的59，也可以动态计算）
        content_length = 59
        # 生成POST请求头，包含正确的Content-Length
        post_headers = generate_headers(
            cookies=config.COOKIES, is_post=True, content_length=content_length)
        # 发送POST请求，包含表单数据
        p = requests.post(LOGINTO_URL, headers=post_headers,
                          data=form_data, timeout=10)
        # 打印响应状态码
        # print(f"请求响应状态码: {p.status_code}")

        # 验证是否登录成功的逻辑
        if p.status_code == 200:
            # 检查响应内容是否包含失败关键词
            if '验证码错误' in p.text or '用户名或密码错误' in p.text:
                print("登录失败：用户名、密码或验证码错误")
                # 继续循环，重新尝试登录
            # 检查是否存在重定向或成功关键词
            elif p.url != LOGINTO_URL or '欢迎' in p.text or '主页' in p.text:
                success = True
            else:
                # 如果无法明确判断，提供更多信息供用户检查
                print("登录结果不明确，请检查响应内容")
                # 继续循环，重新尝试登录
        else:
            print(f"登录失败：HTTP状态码异常 ({p.status_code})")
            # 继续循环，重新尝试登录

# 打印响应文本内容（可选，用于调试）
# print(p.text)


def check_login_status():
    """
    检查当前登录状态
    通过访问主页面并检查响应头的Content-Type编码来判断
    UTF-8编码表示已登录，GBK编码表示未登录
    只有在状态变化时才输出信息
    """
    global _LAST_LOGIN_STATUS

    try:
        # 使用session.py中已有的generate_headers函数生成请求头
        headers = generate_headers(cookies=config.COOKIES)

        # 发送HEAD请求只获取响应头，提高效率
        start_time = time.time()
        response = requests.head(
            MAIN_PAGE_URL, headers=headers, timeout=10, allow_redirects=True)
        response_time = time.time() - start_time

        # 获取Content-Type头
        content_type = response.headers.get('Content-Type', '')

        # 检查编码类型
        current_status = None
        if 'utf-8' in content_type.lower():
            current_status = True
        elif 'gbk' in content_type.lower():
            current_status = False
        else:
            current_status = False  # 如果无法确定编码类型，默认认为未登录

        # 只有在状态变化时才输出信息，或者是第一次检查
        if _LAST_LOGIN_STATUS is None or _LAST_LOGIN_STATUS != current_status:
            if current_status:
                print(f"已登录 [响应时间: {response_time:.2f}秒]")
            elif 'gbk' in content_type.lower():
                print(f"未登录 [响应时间: {response_time:.2f}秒]")
            else:
                print(
                    f"状态未知，Content-Type: {content_type} [响应时间: {response_time:.2f}秒]")

            # 更新上一次的状态
            _LAST_LOGIN_STATUS = current_status

        return current_status

    except (requests.RequestException, KeyError) as e:
        # 异常情况也认为是状态变化，需要输出信息
        print(f"检查状态错误: {str(e)}")
        _LAST_LOGIN_STATUS = None  # 重置状态，以便下次异常时仍能输出
        # 发生异常时默认认为需要重新登录
        return False
