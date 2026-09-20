# 天天俱乐部管理后台

Vue 3 + Vite + Element Plus。打包产物输出到 `../server/static/admin`，随 server 一起部署。

## 开发

先启动后端：

```bash
cd server
uvicorn app.main:app --reload --port 8000
```

再启动管理端：

```bash
cd admin
npm install
npm run dev
```

访问：http://127.0.0.1:5173/admin/

默认账号：`admin` / `admin123`

## 构建（写入 server）

```bash
cd admin
npm run build
```

完成后打开：http://127.0.0.1:8000/admin/
