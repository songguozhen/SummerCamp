#!/bin/bash
cd "$(dirname "$0")"

echo "=== 夏令营追踪器 启动中 ==="

# 检查是否已在运行
if [ -f .server.pid ] && kill -0 "$(cat .server.pid)" 2>/dev/null; then
    echo "服务器已在运行 (PID: $(cat .server.pid))，直接打开浏览器..."
    open http://localhost:8000
    exit 0
fi

# 激活 conda 环境
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate base

# 检查依赖
if ! python -c "import fastapi, uvicorn, openai" 2>/dev/null; then
    echo "安装依赖..."
    pip install -r requirements.txt -q
fi

# 后台启动服务器
nohup uvicorn main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
echo $! > .server.pid
echo "服务器已启动 (PID: $(cat .server.pid))"

# 等待服务器就绪
echo "等待服务器就绪..."
for i in {1..10}; do
    if curl -s http://localhost:8000/api/entries >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

open http://localhost:8000
echo "浏览器已打开 http://localhost:8000"
echo "关闭服务器请双击 stop.command"
