# 手动重启 GPU 后端服务 - 当前情况说明

## 🔍 当前状态分析

### ✅ 已完成：
1. **.env 文件已创建** - CORS 配置正确
   - 位置: `/home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend/.env`
   - 配置: `ALLOWED_ORIGINS` 已包含所有 Vercel 域名 ✅

### ❌ 遇到的问题：
1. **脚本执行错误**: `bad interpreter: Permission denied`
   - 原因: 脚本中的路径错误（使用了 `/home/jovyan/smartsuccess-gpu/` 而不是 `/home/jovyan/work/smartsuccess-gpu/`）
   - 脚本无法执行

2. **GPU 后端服务未运行**
   - 当前没有运行中的 `uvicorn main:app` 进程

### 📍 你当前的位置：
- 你在 `~` 目录（用户主目录）
- 需要进入 GPU 后端目录

---

## 🚀 手动重启服务（不使用脚本）

### 步骤 1: 进入正确的目录

```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
```

### 步骤 2: 检查是否有运行中的服务并停止

```bash
# 查找运行中的进程
ps aux | grep "uvicorn main:app" | grep -v grep

# 如果有进程，停止它
pkill -f "uvicorn main:app"

# 等待几秒
sleep 2
```

### 步骤 3: 激活 conda 环境并启动服务

```bash
# 激活 conda 环境
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate gpu_backend

# 启动服务（后台运行）
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &

# 保存进程 ID
echo $! > gpu_backend.pid

# 显示进程 ID
echo "✅ GPU 后端已启动，PID: $(cat gpu_backend.pid)"
```

### 步骤 4: 验证服务运行

```bash
# 等待几秒让服务启动
sleep 3

# 检查进程
ps aux | grep "uvicorn main:app" | grep -v grep

# 测试健康端点
curl http://localhost:8000/health

# 查看日志（最后几行）
tail -20 gpu_backend_service.log
```

---

## 📋 完整命令序列（复制粘贴）

```bash
# 1. 进入目录
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

# 2. 停止旧服务（如果有）
pkill -f "uvicorn main:app"
sleep 2

# 3. 激活环境并启动
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate gpu_backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
echo $! > gpu_backend.pid

# 4. 验证
sleep 3
ps aux | grep "uvicorn main:app" | grep -v grep
curl http://localhost:8000/health
```

---

## ✅ 验证清单

完成后检查：

- [ ] 进程正在运行: `ps aux | grep uvicorn` 应该显示进程
- [ ] 健康检查通过: `curl http://localhost:8000/health` 返回 JSON
- [ ] 日志文件存在: `ls -la gpu_backend_service.log`
- [ ] PID 文件存在: `cat gpu_backend.pid` 显示进程 ID

---

## 🔧 如果遇到问题

### 问题: conda 环境不存在
```bash
# 检查环境
conda env list | grep gpu_backend

# 如果不存在，需要创建（参考之前的设置文档）
```

### 问题: 端口 8000 被占用
```bash
# 检查端口
netstat -tuln | grep 8000
# 或
ss -tuln | grep 8000

# 如果被占用，找到进程并停止
lsof -i :8000
```

### 问题: 服务启动失败
```bash
# 查看详细日志
tail -50 gpu_backend_service.log

# 尝试前台运行查看错误
conda activate gpu_backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📝 下一步

服务启动后：

1. **在 Vercel 中设置环境变量**（如果还没设置）:
   - `NEXT_PUBLIC_GPU_BACKEND_URL` = `https://your-port-8000-url.cluster3.service-inference.ai`

2. **重新部署 Vercel 应用**

3. **在浏览器中测试**:
   ```javascript
   fetch('https://your-port-8000-url.cluster3.service-inference.ai/health')
     .then(r => r.json())
     .then(console.log)
   ```
