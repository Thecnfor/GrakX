import requests
from session.session import generate_headers
import config

def post_class(course_id):
    """
    提交选课请求
    :param course_id: 课程ID
    :return: 选课结果
    """
    try:
        # 生成请求头
        headers = generate_headers(config.COOKIES)

        # 添加X-Requested-With头部，设置为XMLHttpRequest表示这是AJAX请求
        headers['X-Requested-With'] = 'XMLHttpRequest'

        # 更新Referer头部
        headers['Referer'] = config.BASE_URL + 'xsxkkc/comeInGgxxkxk'

        # 构建请求URL
        # jx0404id参数为课程ID，xkzy为空，trjf为空，cxxdlx=1表示选课类型
        url = f"{config.BASE_URL}xsxkkc/ggxxkxkOper?jx0404id={course_id}&xkzy=&trjf=&cxxdlx=1"

        # 发送GET请求
        response = requests.get(url, headers=headers, timeout=10)

        # 检查请求是否成功
        if response.status_code == 200:
            # 返回响应内容作为选课结果
            return {
                'success': True,
                'data': response.text,
                'course_id': course_id
            }
        else:
            return {
                'success': False,
                'error': f'请求失败，状态码：{response.status_code}',
                'course_id': course_id
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'course_id': course_id
        }
