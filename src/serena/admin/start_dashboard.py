#!/usr/bin/env python3
"""
独立启动 Serena Admin Dashboard 的脚本
直接运行 Flask 服务器，无需 MCP 服务器
"""

import logging
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from serena.agent import SerenaAgent
from serena.config.serena_config import SerenaConfig
from serena.dashboard import SerenaDashboardAPI
from serena.util.logging import MemoryLogHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)


def main():
    """启动 Admin Dashboard"""
    log.info("=" * 60)
    log.info("Serena Admin Dashboard 启动中...")
    log.info("=" * 60)

    # 创建 MemoryLogHandler
    memory_log_handler = MemoryLogHandler(level=logging.INFO)

    try:
        # 初始化 Serena Agent
        log.info("初始化 Serena Agent...")
        config = SerenaConfig.from_config_file()
        agent = SerenaAgent(serena_config=config, memory_log_handler=memory_log_handler)

        # 获取工具名称
        tool_names = [tool.get_name_from_cls() for tool in agent._all_tools.values()]

        # 创建 Dashboard API
        log.info("创建 Dashboard API...")
        dashboard = SerenaDashboardAPI(
            memory_log_handler=memory_log_handler,
            tool_names=tool_names,
            agent=agent,
            tool_usage_stats=agent._tool_usage_stats
        )

        # 获取配置的监听地址和端口
        host = config.web_dashboard_listen_address
        if host == "0.0.0.0":
            display_host = "localhost"
        else:
            display_host = host

        # 查找可用端口 (从 24285 开始)
        port = SerenaDashboardAPI._find_first_free_port(24285, host)

        log.info("")
        log.info("=" * 60)
        log.info("Dashboard 已启动！")
        log.info("=" * 60)
        log.info(f"主 Dashboard: http://{display_host}:{port}/dashboard/index.html")
        log.info(f"Admin 管理: http://{display_host}:{port}/admin/")
        log.info("")
        log.info("按 Ctrl+C 停止服务器")
        log.info("=" * 60)
        log.info("")

        # 直接运行 Flask 应用 (非线程模式)
        dashboard.run(host=host, port=port)

    except KeyboardInterrupt:
        log.info("")
        log.info("=" * 60)
        log.info("正在停止 Dashboard...")
        log.info("=" * 60)
    except Exception as e:
        log.exception(f"启动 Dashboard 时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
