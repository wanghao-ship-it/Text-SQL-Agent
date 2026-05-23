"""
交互式运行器：处理用户输入、调用图执行、中断恢复、输出结果。
"""

import sys
import time
import traceback
from typing import Any, Dict

from langgraph.types import Command

from a_graph.builder import build_graph


class WrenRunner:
    """Wren SQL Agent 交互运行器"""

    def __init__(self, thread_id: str = "default_session"):
        self.thread_id = thread_id
        self.config = {"configurable": {"thread_id": thread_id}}
        self.app = None

    def _ensure_app(self):
        """懒加载编译好的图（带 checkpointer）"""
        if self.app is None:
            self.app = build_graph()

    def run_interactive(self):
        """启动交互式对话循环"""
        self._ensure_app()
        print("💬 已进入 SQL 助手对话模式（输入 'exit' 退出）")

        while True:
            user_input = input("\n请输入你的问题: ").strip()
            if not user_input:
                print("问题不能为空")
                continue
            if user_input.lower() in ["exit", "quit", "退出"]:
                print("👋 对话结束")
                break

            # 执行一次查询
            self._run_query(user_input)

    def _run_query(self, question: str):
        """执行单次查询，处理中断和结果"""
        start_time = time.perf_counter()

        try:
            # 初始调用
            result = self.app.invoke(
                {"question": question},
                self.config,
                version="v2"
            )

            # 处理中断（可恢复的）
            while result.interrupts:
                interrupt_obj = result.interrupts[-1]
                payload = interrupt_obj.value  # 是一个字典 {"instruction": ..., "content": ...}

                print(f"\n⚠️ {payload['instruction']}")

                # 获取用户输入
                human_input = input("请输入修正后的 SQL（或输入 'skip' 放弃）：").strip()
                if human_input.lower() == "skip":
                    print("用户跳过，流程终止。")
                    break

                # 只更新尝试次数，不更新 generated_sql（节点自己会更新）
                current_state = self.app.get_state(self.config).values
                old_attempt = current_state.get("dry_plan_attempts", 0)
                self.app.update_state(
                    self.config,
                    {"dry_plan_attempts": old_attempt + 1}
                    # 注意：这里不写 generated_sql
                )

                # 恢复执行：将用户输入作为 resume 值传回
                result = self.app.invoke(
                    Command(resume={interrupt_obj.id: human_input}),
                    self.config,
                    version="v2"
                )

            # 正常结束：result.interrupts 为空，result.value 是最终状态
            final_state = result if isinstance(result, dict) else result.value

            elapsed = time.perf_counter() - start_time
            print(f"\n本次回答耗时: {elapsed:.2f} 秒")

            # 输出最终答案
            final_answer = final_state.get("final_answer")
            if final_answer:
                print(f"\n答案：{final_answer}")
            else:
                sql = final_state.get("generated_sql") or final_state.get("dry_plan_result")
                if sql:
                    print(f"\n📝 生成的 SQL: {sql}")
                else:
                    print("\n⚠️ 未生成有效回答，请检查输入或日志")

        except Exception as e:
            print(f"\n❌ 执行出错: {e}")
            traceback.print_exc()


def run():
    """便捷函数：使用默认会话启动交互模式"""
    runner = WrenRunner(thread_id="user_session_017")
    runner.run_interactive()


if __name__ == "__main__":
    run()