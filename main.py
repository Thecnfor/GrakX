"""
自动抢课系统
"""
import threading
import time
from config import set_user_credentials
from session import auto_login, check_login_status
from get_class import get_and_filter_all_courses
from api import post_class


def main():
    """TODO: 每个函数增加用户识别参数
    主函数，用于调用自动登录功能并获取选课轮次信息、课程数据。
    """
    # 设置用户凭证信息
    # 可以根据需要传入不同的参数，None表示不更新该参数
    set_user_credentials(
        username='',  # 替换为实际用户名
        password='',  # 替换为实际密码
        cookies={'JSESSIONID': ''}  # 替换为实际Cookie
    )

    # 创建并启动登录维护线程
    threading.Thread(target=auto_login, daemon=True).start()
    # 等待登录完成
    while not check_login_status():
        print("等待登录完成...")
        time.sleep(1)

    while True:
        try:
            if check_login_status():
                # 获取课程
                # all_courses = get_and_filter_all_courses()
                # course_id = "202520261007196"
                # a=post_class(course_id)
                # print(a)
                """
                'success': True, 'data': '{"success":false,"message":"选课失败：与已选中课程‘体育养生 ’冲突"}\r\n', 'course_id': '202520261007196'}
                """
            else:
                print("登录失效，等待重新登录...")
                auto_login(check_inter=1)
        except KeyboardInterrupt:
            print('用户手动中断程序')
            break


if __name__ == "__main__":
    main()
