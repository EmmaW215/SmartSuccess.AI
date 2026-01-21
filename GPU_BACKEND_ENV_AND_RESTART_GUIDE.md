# GPU 后端 .env 文件配置和服务重启指南

## 📍 GPU 后端位置

**GPU 后端目录路径:**
```
/home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
```

---

## 📝 步骤 1: 创建/更新 .env 文件

### 方法 1: 使用命令行创建（推荐）

1. **进入 GPU 后端目录:**
   ```bash
   cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
   ```

2. **检查 .env 文件是否存在:**
   ```bash
   ls -la .env
   ```
   - 如果文件存在，继续下一步
   - 如果文件不存在，需要创建它

3. **创建或更新 .env 文件:**
   
   **如果 .env 文件不存在，创建它:**
   ```bash
   cat > .env << 'EOF'
   # Application
   APP_NAME=SmartSuccess.AI GPU Backend
   APP_VERSION=1.0.0
   DEBUG=false
   ENVIRONMENT=production
   
   # Server
   HOST=0.0.0.0
   PORT=8000
   WORKERS=4
   
   # CORS - 重要！必须包含你的 Vercel 域名
   ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]
   
   # Render backend for fallback
   RENDER_BACKEND_URL=https://smartsuccess-ai.onrender.com
   
   # Optional: API keys
   OPENAI_API_KEY=
   GROQ_API_KEY=
   XAI_API_KEY=
   
   # Data paths
   DATA_DIR=./data
   PRERAG_DIR=./data/pre_rag
   USER_RAG_DIR=./data/user_rag
   VOICE_PRESETS_DIR=./data/voice_presets
   
   # GPU settings
   GPU_DEVICE=cuda
   GPU_MEMORY_FRACTION=0.9
   EOF
   ```

   **如果 .env 文件已存在，更新 CORS 配置:**
   ```bash
   # 备份现有文件
   cp .env .env.backup
   
   # 使用 nano 编辑器编辑
   nano .env
   ```
   
   找到 `ALLOWED_ORIGINS` 这一行，确保它包含：
   ```
   ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]
   ```

4. **验证 .env 文件内容:**
   ```bash
   cat .env | grep ALLOWED_ORIGINS
   ```
   应该看到包含所有 Vercel 域名的配置。

---

### 方法 2: 使用 Python 脚本更新（如果文件已存在）

```bash
cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend

# 创建更新脚本
cat > update_cors.py << 'EOF'
import os
import re

env_file = '.env'
backup_file = '.env.backup'

# 备份
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        content = f.read()
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ Backed up to {backup_file}")

# 读取或创建
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        lines = f.readlines()
else:
    lines = []

# 更新或添加 ALLOWED_ORIGINS
new_cors = 'ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]\n'

found = False
for i, line in enumerate(lines):
    if line.startswith('ALLOWED_ORIGINS='):
        lines[i] = new_cors
        found = True
        break

if not found:
    lines.append(new_cors)

# 写入
with open(env_file, 'w') as f:
    f.writelines(lines)

print(f"✅ Updated {env_file}")
print(f"   ALLOWED_ORIGINS={new_cors.strip()}")
EOF

# 运行脚本
python3 update_cors.py

# 验证
cat .env | grep ALLOWED_ORIGINS
```

---

## 🔄 步骤 2: 重启 GPU 后端服务

### 方法 1: 使用提供的脚本（推荐）

1. **检查服务状态:**
   ```bash
   cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
   ./status_service.sh
   ```

2. **停止服务:**
   ```bash
   ./stop_service.sh
   ```
   应该看到: `✅ Service stopped`

3. **等待几秒:**
   ```bash
   sleep 3
   ```

4. **启动服务:**
   ```bash
   ./start_service.sh
   ```
   应该看到: `✅ Service started with PID: xxxxx`

5. **验证服务运行:**
   ```bash
   ./status_service.sh
   ```
   应该看到:
   - ✅ Service is running
   - ✅ Health check passed

---

### 方法 2: 手动重启

1. **停止服务:**
   ```bash
   cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
   
   # 查找运行中的进程
   ps aux | grep "uvicorn main:app"
   
   # 停止进程（替换 PID 为实际进程 ID）
   kill <PID>
   
   # 或者强制停止所有相关进程
   pkill -f "uvicorn main:app"
   ```

2. **启动服务:**
   ```bash
   cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
   
   # 激活 conda 环境
   source /home/jovyan/miniconda3/etc/profile.d/conda.sh
   conda activate gpu_backend
   
   # 启动服务（后台运行）
   nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
   
   # 保存进程 ID
   echo $! > gpu_backend.pid
   ```

3. **验证:**
   ```bash
   # 检查进程
   ps aux | grep "uvicorn main:app"
   
   # 检查健康端点
   curl http://localhost:8000/health
   ```

---

## ✅ 步骤 3: 验证配置

### 1. 验证 .env 文件

```bash
cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
cat .env | grep ALLOWED_ORIGINS
```

**期望输出:**
```
ALLOWED_ORIGINS=["https://smart-success-ai.vercel.app","https://smartsuccess-ai.vercel.app","https://matchwise-ai.vercel.app","http://localhost:3000","http://localhost:3001"]
```

### 2. 验证服务运行

```bash
./status_service.sh
```

**期望输出:**
```
✅ Service is running (PID: xxxxx)
✅ Health check passed
```

### 3. 测试 CORS 配置

在浏览器控制台（从 Vercel 网站）测试:
```javascript
fetch('https://your-port-8000-url.cluster3.service-inference.ai/health')
  .then(r => {
    console.log('Status:', r.status);
    console.log('CORS Header:', r.headers.get('access-control-allow-origin'));
    return r.json();
  })
  .then(data => console.log('Data:', data))
  .catch(error => console.error('Error:', error));
```

**期望结果:**
- Status: 200
- CORS Header: `https://smart-success-ai.vercel.app` (或匹配的域名)
- Data: `{"status": "healthy", ...}`

---

## 🔍 故障排除

### 问题 1: .env 文件找不到

**解决方案:**
```bash
cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
ls -la .env
# 如果不存在，使用上面的方法创建
```

### 问题 2: 服务无法启动

**检查:**
```bash
# 检查 conda 环境
conda env list | grep gpu_backend

# 检查端口是否被占用
netstat -tuln | grep 8000
# 或
ss -tuln | grep 8000

# 查看日志
tail -50 gpu_backend_service.log
```

### 问题 3: CORS 仍然失败

**检查:**
1. 确认 .env 文件中的 `ALLOWED_ORIGINS` 包含正确的域名
2. 确认服务已重启（配置更改需要重启才能生效）
3. 检查 GPU 后端日志:
   ```bash
   tail -100 gpu_backend_service.log | grep -i cors
   ```

---

## 📋 快速操作清单

- [ ] 1. 进入 GPU 后端目录: `cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend`
- [ ] 2. 检查 .env 文件是否存在: `ls -la .env`
- [ ] 3. 创建或更新 .env 文件，确保包含正确的 `ALLOWED_ORIGINS`
- [ ] 4. 验证 .env 文件内容: `cat .env | grep ALLOWED_ORIGINS`
- [ ] 5. 停止服务: `./stop_service.sh`
- [ ] 6. 启动服务: `./start_service.sh`
- [ ] 7. 检查状态: `./status_service.sh`
- [ ] 8. 测试健康端点: `curl http://localhost:8000/health`
- [ ] 9. 在浏览器中测试 CORS

---

## 📝 重要提示

1. **.env 文件位置**: `/home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend/.env`
2. **配置更改后必须重启**: 修改 .env 文件后，必须重启服务才能生效
3. **CORS 配置格式**: 必须是 JSON 数组格式，用双引号
4. **域名必须完全匹配**: 包括 `https://` 和域名，不能有尾随斜杠

---

## 🔗 相关文件

- GPU 后端目录: `/home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend`
- .env 文件: `/home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend/.env`
- 启动脚本: `./start_service.sh`
- 停止脚本: `./stop_service.sh`
- 状态脚本: `./status_service.sh`
- 服务日志: `gpu_backend_service.log`
