from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import re
import json
import os

@register("MarketPulse", "ikun", "updating...", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config_path = os.path.join(os.path.dirname(__file__), "data", "config.json")
        self.config = {}
        self.load_config()

    async def initialize(self):
        """异步初始化（如果需要）"""

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"读取 config.json 失败: {e}")
                # 兜底默认配置
                self.config = {
                    "admin_id": "2536684724",
                    "reminder_time": "09:00",
                    "message": "早上好，这是你的每日提醒！"
                }
        else:
            self.logger.warning("配置文件不存在，使用默认配置并创建文件: " + self.config_path)
            self.config = {
                "admin_id": "2536684724",
                "reminder_time": "09:00",
                "message": "早上好，这是你的每日提醒！"
            }
            self.save_config()

    def save_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    @filter.command("MarketPulse")
    async def marketpulse(self, event: AstrMessageEvent):
        user_name = event.get_sender_name()
        message_str = event.message_str
        logger.info(message_str)
        match = re.search(r"修改提示时间为\s*(\d{1,2}:\d{2})", message_str)
        if match:
            new_time = match.group(1)
            if re.match(r"^(?:[01]?\d|2[0-3]):[0-5]\d$", new_time):
                self.config['reminder_time'] = new_time
                self.save_config()
                yield event.plain_result(f"✅ 已成功将提醒时间修改为 {new_time}")
            else:
                yield event.plain_result("⚠️ 时间格式不正确，请使用 24 小时制，如 09:30 或 23:15")
            return

        if "查看提醒时间" in message_str:
            current_time = self.config.get("reminder_time", "09:00")
            yield event.plain_result(f"⏰ 当前提醒时间为 {current_time}")
            return

        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
