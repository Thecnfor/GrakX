"""
自动登录模块
"""
import time
import config
from .session import login, check_login_status
from .course import get_xklc_list, enter_xsk_system


def auto_login(check_inter=18000):
    """
    自动登录函数，负责初始化登录并循环检查登录状态。
    程序会以指定的时间间隔检查登录状态，若未登录则重新登录，
    可通过键盘中断（Ctrl+C）退出程序。
    """
    print("登录维护线程启动...")
    print(f"目标系统: {config.BASE_URL}")

    check_interval = check_inter  # 检查间隔，单位：秒
    while True:
        # 检查登录状态
        if not check_login_status():
            # 如果未登录，立即执行login()函数
            login()
            enter_xsk_system()

        # 等待下一次检查
        time.sleep(check_interval)


__all__ = [
    "login",
    "check_login_status",
    "auto_login",
    "get_xklc_list",
    "enter_xsk_system"
]
