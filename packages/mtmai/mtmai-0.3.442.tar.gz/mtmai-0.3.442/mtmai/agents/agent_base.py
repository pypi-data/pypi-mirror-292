import os
import time

from .utils.utils import sanitize_filename


class AgentBase:
    """agent 基类"""

    def __init__(
        self, task: dict, websocket=None, stream_output=None, tone=None, headers=None
    ):
        self.task = task
        self.websocket = websocket
        self.stream_output = stream_output
        self.tone = tone
        self.headers = headers
        self.task_id = self.generate_task_id()
        self.output_dir = self.create_output_dir()

    def generate_task_id(self) -> int:
        """(TODO)生成任务 ID"""
        return int(time.time())

    def create_output_dir(self) -> str:
        """(TODO)创建输出目录"""
        output_dir = "./outputs/" + sanitize_filename(
            f"run_{self.task_id}_{self.task.get('query', '')[0:40]}"
        )
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def log(self, message: str):
        """(TODO)"日志记录"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def run(self):
        """(TODO)运行代理任务"""
        raise NotImplementedError("子类必须实现此方法")

    def export_graphflow_image(self):
        """导出流程图图片"""
        raise NotImplementedError("子类必须实现此方法")
