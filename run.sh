#!/bin/bash

echo "🚀 [1/3] 正在启动 Codex API 代理服务..."
# 后台启动 adapter，将日志写入文件，避免污染终端
python codex_adapter.py > adapter.log 2>&1 &
ADAPTER_PID=$!

# 给代理一点时间启动完毕
sleep 2

# 检查代理是否成功运行
if kill -0 $ADAPTER_PID 2>/dev/null; then
    echo "✅ [2/3] 代理服务启动成功 (PID: $ADAPTER_PID)。"
else
    echo "❌ 代理服务启动失败，请查看 adapter.log"
    exit 1
fi

echo "🤖 [3/3] 唤醒 CrewAI 团队，开始执行任务..."
echo "============================================================"

# 运行主程序
python src/crewai_project/main.py

echo "============================================================"
echo "🎉 任务执行完毕！"

# 清理后台进程，不留隐患
echo "🧹 正在清理代理进程 (PID: $ADAPTER_PID)..."
kill $ADAPTER_PID
echo "👋 再见！"
