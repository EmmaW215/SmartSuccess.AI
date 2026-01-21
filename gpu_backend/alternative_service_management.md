# Systemd 替代方案

由于当前环境不支持 systemd，以下是替代的服务管理方案：

## 方案 1: 使用 nohup + 脚本（当前推荐）

### 启动脚本 (start_service.sh)
```bash
#!/bin/bash
cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
source /home/jovyan/miniconda3/etc/profile.d/conda.sh
conda activate gpu_backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > gpu_backend_service.log 2>&1 &
echo $! > gpu_backend.pid
echo "Service started with PID: $(cat gpu_backend.pid)"
```

### 停止脚本 (stop_service.sh)
```bash
#!/bin/bash
if [ -f gpu_backend.pid ]; then
    PID=$(cat gpu_backend.pid)
    kill $PID
    rm gpu_backend.pid
    echo "Service stopped"
else
    echo "Service not running"
fi
```

## 方案 2: 使用 supervisor（如果可用）

如果系统有 supervisor，可以配置它来管理服务。

## 方案 3: 使用 screen/tmux

使用 screen 或 tmux 在后台运行服务。

## 当前状态

服务文件已创建，但需要在支持 systemd 的环境中安装。
