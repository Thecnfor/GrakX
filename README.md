# GrakX - 高校自动抢课系统

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
2. （本地版）pyUI实现快速抢课
3. （移动版）计划结合Flutter开发移动应用