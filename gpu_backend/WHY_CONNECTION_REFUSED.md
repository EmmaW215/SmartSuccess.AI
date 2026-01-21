# 为什么出现 "Connection refused" 错误？

## 🔍 问题分析

### 错误信息：
```
curl: (7) Failed to connect to localhost port 8000 after 0 ms: Connection refused
```

### 原因：

1. **服务没有运行**
   - `ps aux | grep "uvicorn main:app"` 没有输出 → 服务未运行
   - 没有进程监听端口 8000

2. **启动失败的原因：**
   - ❌ conda 环境 `gpu_backend` 不存在
   - ❌ `uvicorn` 命令未找到（未安装）
   - ❌ 日志显示: `nohup: failed to run command 'uvicorn': No such file or directory`

---

## ✅ 解决方案

### 方法 1: 使用修复后的启动脚本（推荐）

```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
bash START_SERVICE_FIXED.sh
```

这个脚本会：
- ✅ 自动检查并安装 uvicorn（如果未安装）
- ✅ 使用 conda base 环境
- ✅ 正确启动服务
- ✅ 验证服务状态

---

### 方法 2: 手动安装依赖并启动

```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

# 1. 激活 conda base 环境
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate base

# 2. 安装 uvicorn（如果未安装）
pip install uvicorn[standard] fastapi

# 3. 启动服务
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
echo $! > gpu_backend.pid

# 4. 验证
sleep 3
ps aux | grep "uvicorn main:app" | grep -v grep
curl http://localhost:8000/health
```

---

### 方法 3: 安装所有依赖（完整安装）

```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

# 激活 conda base
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate base

# 安装所有依赖
pip install -r requirements.txt

# 启动服务
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
echo $! > gpu_backend.pid
```

---

## 🔍 验证服务已启动

### 检查 1: 进程
```bash
ps aux | grep "uvicorn main:app" | grep -v grep
```
**应该看到进程信息**

### 检查 2: 端口
```bash
netstat -tuln | grep 8000
# 或
ss -tuln | grep 8000
```
**应该看到端口 8000 在监听**

### 检查 3: 健康端点
```bash
curl http://localhost:8000/health
```
**应该返回 JSON 响应，而不是 "Connection refused"**

---

## 📋 快速修复命令（复制粘贴）

```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate base
pip install uvicorn[standard] fastapi pydantic pydantic-settings
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
echo $! > gpu_backend.pid
sleep 3
curl http://localhost:8000/health
```

---

## 📝 总结

**"Connection refused" 的原因：**
- 服务没有运行（因为启动失败）

**启动失败的原因：**
- uvicorn 未安装
- conda 环境配置问题

**解决方案：**
- 使用 `python -m uvicorn` 而不是直接 `uvicorn`
- 确保在正确的 conda 环境中
- 安装必要的依赖

---

## 🚀 下一步

启动服务后：
1. 验证服务运行: `curl http://localhost:8000/health`
2. 检查日志: `tail -f gpu_backend_service.log`
3. 在 Vercel 中设置环境变量
4. 测试 CORS 是否正常
