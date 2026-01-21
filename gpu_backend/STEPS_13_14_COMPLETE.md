# 步骤 13-14: Systemd 服务配置与验证 - 完成报告

## ✅ 步骤 13: 配置 Systemd 服务

### 服务文件已创建

**文件**: `smartsuccess-gpu.service`

**配置内容**（已适配当前环境）:
```ini
[Unit]
Description=SmartSuccess.AI GPU Backend
After=network.target

[Service]
Type=simple
User=jovyan
WorkingDirectory=/home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
Environment="PATH=/home/jovyan/miniconda3/envs/gpu_backend/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/jovyan/miniconda3/envs/gpu_backend/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 安装步骤

#### 方法 1: 使用安装脚本（推荐）

```bash
cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
./install_systemd_service.sh
```

#### 方法 2: 手动安装

```bash
# 1. 复制服务文件
sudo cp smartsuccess-gpu.service /etc/systemd/system/

# 2. 重新加载 systemd
sudo systemctl daemon-reload

# 3. 启用服务（开机自启）
sudo systemctl enable smartsuccess-gpu

# 4. 启动服务
sudo systemctl start smartsuccess-gpu

# 5. 检查状态
sudo systemctl status smartsuccess-gpu
```

### 关键配置说明

- **User**: `jovyan` (当前用户)
- **WorkingDirectory**: `/home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend`
- **ExecStart**: 使用 conda 环境的 uvicorn
- **Workers**: 4 个工作进程（可在 .env 中配置）
- **Restart**: 自动重启（服务崩溃时）

## ✅ 步骤 14: 验证部署

### 验证脚本

运行验证脚本：
```bash
./verify_deployment.sh
```

### 手动验证步骤

#### 1. 检查服务状态

```bash
sudo systemctl status smartsuccess-gpu
```

**预期输出**:
```
● smartsuccess-gpu.service - SmartSuccess.AI GPU Backend
   Loaded: loaded (/etc/systemd/system/smartsuccess-gpu.service; enabled)
   Active: active (running) since ...
```

#### 2. 检查健康状态

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

**预期响应**:
```json
{
    "status": "healthy",
    "gpu_available": true,
    "gpu_memory_free": 47.23,
    "gpu_memory_total": 47.99,
    "models_loaded": {
        "embedding": true,
        "prerag": true
    },
    "version": "1.0.0"
}
```

#### 3. 查看日志

```bash
# 实时日志
sudo journalctl -u smartsuccess-gpu -f

# 最近 50 行
sudo journalctl -u smartsuccess-gpu -n 50

# 今天的日志
sudo journalctl -u smartsuccess-gpu --since today
```

## 📋 Systemd 服务管理命令

### 基本操作

```bash
# 启动服务
sudo systemctl start smartsuccess-gpu

# 停止服务
sudo systemctl stop smartsuccess-gpu

# 重启服务
sudo systemctl restart smartsuccess-gpu

# 重新加载配置（不中断服务）
sudo systemctl reload smartsuccess-gpu

# 查看状态
sudo systemctl status smartsuccess-gpu

# 查看日志
sudo journalctl -u smartsuccess-gpu -f
```

### 开机自启管理

```bash
# 启用开机自启
sudo systemctl enable smartsuccess-gpu

# 禁用开机自启
sudo systemctl disable smartsuccess-gpu

# 检查是否启用
systemctl is-enabled smartsuccess-gpu
```

## 🔍 故障排除

### 如果服务无法启动

1. **查看详细日志**:
   ```bash
   sudo journalctl -u smartsuccess-gpu -n 100 --no-pager
   ```

2. **检查配置文件**:
   ```bash
   sudo systemctl cat smartsuccess-gpu
   ```

3. **测试手动启动**:
   ```bash
   cd /home/jovyan/smartsuccess-gpu/SmartSuccess.AI/gpu_backend
   source /home/jovyan/miniconda3/etc/profile.d/conda.sh
   conda activate gpu_backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **检查端口占用**:
   ```bash
   sudo lsof -i :8000
   ```

### 常见问题

#### 问题 1: 权限错误
**解决方案**: 确保 User 设置为正确的用户（jovyan）

#### 问题 2: 路径错误
**解决方案**: 检查 WorkingDirectory 和 ExecStart 路径是否正确

#### 问题 3: Conda 环境未激活
**解决方案**: 在 ExecStart 中直接使用 conda 环境的完整路径

## ✅ 验证清单

- [x] Systemd 服务文件已创建
- [x] 安装脚本已创建
- [x] 验证脚本已创建
- [ ] 服务已安装到 systemd（需要运行安装脚本）
- [ ] 服务已启动
- [ ] 健康检查通过
- [ ] 日志正常记录

## 📝 注意事项

1. **需要 sudo 权限**: 安装 systemd 服务需要管理员权限
2. **端口冲突**: 确保 8000 端口未被其他服务占用
3. **防火墙**: 如果需要外部访问，确保防火墙允许 8000 端口
4. **日志**: 服务日志会记录到 systemd journal，可以使用 journalctl 查看

## 🚀 下一步

1. 运行安装脚本安装服务：
   ```bash
   ./install_systemd_service.sh
   ```

2. 运行验证脚本检查部署：
   ```bash
   ./verify_deployment.sh
   ```

3. 配置防火墙（如需要）:
   ```bash
   sudo ufw allow 8000/tcp
   ```

4. 配置反向代理（可选，如 nginx）

## ⚠️ 环境说明

当前环境不支持 systemd（可能是容器环境）。已创建替代的服务管理方案：

### 替代方案（当前使用）

#### 启动服务
```bash
./start_service.sh
```

#### 停止服务
```bash
./stop_service.sh
```

#### 查看状态
```bash
./status_service.sh
```

### 文件说明

1. **smartsuccess-gpu.service** - Systemd 服务文件（供支持 systemd 的环境使用）
2. **start_service.sh** - 启动脚本（使用 nohup）
3. **stop_service.sh** - 停止脚本
4. **status_service.sh** - 状态检查脚本

### 当前部署状态

✅ **服务正在运行**
- PID: 从 `gpu_backend.pid` 文件查看
- 日志: `gpu_backend_service.log`
- 健康检查: http://localhost:8000/health

### 验证结果

✅ **所有验证通过**
- 服务进程运行中
- 健康检查返回 healthy
- GPU 可用并正常工作
- API 文档可访问
- 所有模型已加载

---
**完成时间**: 2026-01-21
**状态**: ✅ 服务已部署并运行（使用替代方案）
**注意**: 如果环境支持 systemd，可以使用 `smartsuccess-gpu.service` 文件
