#!/bin/bash
cd "$(dirname "$0")"

echo "=== 夏令营追踪器 关闭中 ==="

if [ -f .server.pid ]; then
    PID=$(cat .server.pid)
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "服务器已关闭 (PID: $PID)"
    else
        echo "进程 $PID 不存在（可能已关闭）"
    fi
    rm -f .server.pid
else
    # 尝试按端口查找并关闭
    PID=$(lsof -ti :8000 2>/dev/null)
    if [ -n "$PID" ]; then
        kill $PID
        echo "服务器已关闭 (PID: $PID)"
    else
        echo "未找到运行中的服务器"
    fi
fi
