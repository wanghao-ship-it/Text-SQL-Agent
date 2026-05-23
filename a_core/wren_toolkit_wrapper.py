from functools import lru_cache
from typing import List, Optional
from wren_langchain import WrenToolkit
from a_config.config import config


class WrenToolkitWrapper:
    """封装 WrenToolkit 的初始化与工具管理"""

    def __init__(self, project_path: Optional[str] = None, profile: Optional[str] = None):
        """
        Args:
            project_path: Wren 项目路径（如不提供，从 config 读取）
            profile: 连接配置文件名称（可选）
        """
        self.project_path = project_path or config.WREN_DATA_PATH
        self.profile = profile
        self._toolkit: Optional[WrenToolkit] = None
        self._tools: Optional[List] = None

    def _get_toolkit(self) -> WrenToolkit:
        """懒加载 WrenToolkit 实例"""
        if self._toolkit is None:
            try:
                self._toolkit = WrenToolkit.from_project(
                    self.project_path,
                    profile=self.profile
                )
                print(f"✅ WrenToolkit 初始化成功，项目路径: {self.project_path}")
            except Exception as e:
                raise RuntimeError(f"WrenToolkit 初始化失败: {e}") from e
        return self._toolkit

    def get_tools(self, include_memory_write: bool = False) -> List:
        """
        获取所有工具，并根据参数过滤。

        Args:
            include_memory_write: 是否包含 wren_store_query 工具（默认 False）

        Returns:
            工具列表
        """
        if self._tools is None:
            toolkit = self._get_toolkit()
            self._tools = toolkit.get_tools(
                include_memory_write=include_memory_write
            )
            # 可选：打印可用工具名
            tool_names = [t.name for t in self._tools]
            print(f"📦 已加载 {len(self._tools)} 个工具: {tool_names}")
        return self._tools

    def get_tool_by_name(self, name: str, include_memory_write: bool = False) -> Optional:
        """按名称获取单个工具"""
        tools = self.get_tools(include_memory_write=include_memory_write)
        for tool in tools:
            if tool.name == name:
                return tool
        return None

    def system_prompt(self) -> str:
        """获取系统提示词（委托给 toolkit）"""
        return self._get_toolkit().system_prompt()


# 为了方便全局使用，可以创建一个默认单例
_default_wrapper: Optional[WrenToolkitWrapper] = None


def get_wren_wrapper(
        project_path: Optional[str] = None,
        profile: Optional[str] = None,
        force_reload: bool = False
) -> WrenToolkitWrapper:
    """
    全局单例获取函数（推荐在节点中使用）。

    Args:
        project_path: 覆盖配置路径
        profile: 覆盖 profile
        force_reload: 强制重新创建 wrapper
    """
    global _default_wrapper
    if _default_wrapper is None or force_reload:
        _default_wrapper = WrenToolkitWrapper(
            project_path=project_path,
            profile=profile
        )
    return _default_wrapper