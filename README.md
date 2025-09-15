# GrakX - 高校自动抢课系统 - api版本

### 项目介绍

适合web/flutter多用户
ps：写着玩的，因为学校教务系统老旧，基本没有渗透难度，练练手而已

## 快速开始

### 安装依赖

```bash
uv sync
```

### 配置用户信息

编辑 `main.py` 文件中的用户凭证信息：

```python
set_user_credentials(
    username='your_username',  # 替换为实际用户名
    password='your_password',  # 替换为实际密码
    cookies={'JSESSIONID': 'your_cookie'}  # 可选，替换为实际Cookie
)
```

### 运行程序

```bash
uv run main.py
```
## 未来规划

1. （Web版）计划结合FastAPI开发完全自动抢课*
2. （本地版）pyQT实现快速抢课
3. （移动版）计划结合Flutter开发移动应用

## 重要模板函数

1. set_user_credentials() # 设置用户凭证
2. auto_login(check_inter=1) # 自动登录，check_inter为检查登录状态的间隔时间，单位为秒
3. check_login_status() # 检查登录状态
4. get_and_filter_all_courses() # 可用课程
5. get_class() # 获取全部课程
6. post_class(course_id) # 选课，course_id为课程ID
