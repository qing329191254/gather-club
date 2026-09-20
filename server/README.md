# Gather Club 后端（微信云托管 / FastAPI）

## 本地运行

建议使用 **Python 3.11 / 3.12**（当前机器若默认是 3.14，请用 `py -3.12` 建虚拟环境）：

```bash
cd server
py -3.12 -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 接口文档：http://127.0.0.1:8000/api/docs
- 管理后台：http://127.0.0.1:8000/admin/ （需先构建 admin）
- 默认管理员：`admin` / `admin123`

## 构建并内嵌管理后台

```bash
cd admin
npm install
npm run build
```

产物输出到 `server/static/admin`，推送 `server` 目录到云托管即可同步后台页面。

## 云托管部署

1. 服务类型：自定义镜像 / Dockerfile
2. 监听端口：**80**（或按环境变量 `PORT`）
3. 环境变量配置 `DATABASE_URL` 指向云托管 MySQL，例如：

```
DATABASE_URL=mysql+pymysql://root:密码@内网地址:3306/gather?charset=utf8mb4
JWT_SECRET=请换成长随机串
ADMIN_PASSWORD=请改掉默认密码
```

4. 小程序调用：`wx.cloud.callContainer`，路径如 `/api/v1/home`

## 目录说明

- `app/routers/miniapp.py`：小程序接口 `/api/v1/*`
- `app/routers/admin_api.py`：后台接口 `/api/admin/*`
- `static/admin`：管理端打包产物
