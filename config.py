"""
配置文件
"""

BASE_URL = 'http://jwxt.gdufe.edu.cn/jsxsd/'

USERNAME = None
PASSWORD = None
COOKIES = None


def set_user_credentials(username=None, password=None, cookies=None):
    """
    动态设置用户凭证信息

    :param username: 用户名，如果为None则不更新
    :param password: 密码，如果为None则不更新
    :param cookies: Cookie字典，如果为None则不更新
    """
    global USERNAME, PASSWORD, COOKIES

    if username is not None:
        USERNAME = username

    if password is not None:
        PASSWORD = password

    if cookies is not None:
        COOKIES = cookies
