# 快速修复 CORS 问题 - 简化版

## 🎯 GPU 后端位置

**目录路径:**
```
/home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
```

---

## ⚡ 方法 1: 使用自动化脚本（最简单）

### 一步完成所有操作:

```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
./update_cors_and_restart.sh
```

这个脚本会自动：
1. ✅ 创建或更新 .env 文件
2. ✅ 配置正确的 CORS 设置
3. ✅ 停止旧服务
4. ✅ 启动新服务
5. ✅ 验证服务状态

---

## 📝 方法 2: 手动操作（如果脚本不可用）

### 步骤 1: 进入 GPU 后端目录

```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
```

### 步骤 2: 创建或更新 .env 文件

**如果 .env 文件不存在，创建它:**
```bash
cat > .env << 'EOF'
ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]
EOF
```

**如果 .env 文件已存在，更新它:**
```bash
# 备份
cp .env .env.backup

# 编辑文件
nano .env
# 或使用其他编辑器: vi .env
```

找到 `ALLOWED_ORIGINS` 这一行，确保它包含：
```
ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]
```

### 步骤 3: 重启服务

**使用提供的脚本:**
```bash
./stop_service.sh
sleep 2
./start_service.sh
```

**或手动操作:**
```bash
# 停止服务
pkill -f "uvicorn main:app"

# 等待几秒
sleep 3

# 启动服务
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate gpu_backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
echo $! > gpu_backend.pid
```

### 步骤 4: 验证

```bash
# 检查服务状态
./status_service.sh

# 或手动检查
curl http://localhost:8000/health
```

---

## ✅ 验证清单

完成以上步骤后，检查：

- [ ] .env 文件存在: `ls -la .env`
- [ ] CORS 配置正确: `cat .env | grep ALLOWED_ORIGINS`
- [ ] 服务正在运行: `./status_service.sh` 或 `ps aux | grep uvicorn`
- [ ] 健康检查通过: `curl http://localhost:8000/health`

---

## 🔍 如果遇到问题

### 问题: 找不到 .env 文件
```bash
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
ls -la .env
# 如果不存在，使用上面的方法创建
```

### 问题: 服务无法启动
```bash
# 查看日志
tail -50 gpu_backend_service.log

# 检查端口
netstat -tuln | grep 8000
```

### 问题: 脚本没有执行权限
```bash
chmod +x update_cors_and_restart.sh
chmod +x start_service.sh
chmod +x stop_service.sh
chmod +x status_service.sh
```

---

## 📋 完整命令序列（复制粘贴）

```bash
# 1. 进入目录
cd /home/jovyan/work/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

# 2. 运行自动化脚本（推荐）
./update_cors_and_restart.sh

# 或者手动操作:
# 3. 创建/更新 .env
cat > .env << 'EOF'
ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]
EOF

# 4. 重启服务
./stop_service.sh && sleep 2 && ./start_service.sh

# 5. 验证
./status_service.sh
```

---

## 🎯 下一步

完成 GPU 后端配置后：

1. **在 Vercel 中设置环境变量:**
   - Key: `NEXT_PUBLIC_GPU_BACKEND_URL`
   - Value: `https://your-port-8000-url.cluster3.service-inference.ai`

2. **重新部署 Vercel 应用**

3. **在浏览器中测试:**
   ```javascript
   fetch('https://your-port-8000-url.cluster3.service-inference.ai/health')
     .then(r => r.json())
     .then(console.log)
   ```

---

## 📚 详细文档

完整指南请查看: `GPU_BACKEND_ENV_AND_RESTART_GUIDE.md`
