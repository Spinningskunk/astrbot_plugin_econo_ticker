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

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    class MarketPulsePlugin:
        def __init__(self, bot):
            super().__init__(bot)
            self.config_path = os.path.join(os.path.dirname(__file__), "data", "config.json")
            self.config = {}
            self.load_config()

        def load_config(self):
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.logger.error("配置文件不存在: " + self.config_path)
                # 默认配置，避免程序崩溃
                self.config = {
                    "admin_id": "",
                    "reminder_time": "09:00",
                    "message": "早上好，这是你的每日提醒！"
                }

        def save_config(self):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)

        @filter.command("MarketPulse")
        async def marketpulse(self, event: AstrMessageEvent):
            """每日行情提醒插件"""
            user_name = event.get_sender_name()
            message_str = event.message_str

            # 1. 匹配用户修改提醒时间的请求
            match = re.search(r"修改提示时间为\s*(\d{1,2}:\d{2})", message_str)
            if match:
                new_time = match.group(1)

                # 2. 校验时间格式 (24小时制)
                if re.match(r"^(?:[01]?\d|2[0-3]):[0-5]\d$", new_time):
                    self.config["reminder_time"] = new_time
                    self.save_config()
                    yield event.plain_result(f"✅ 已成功将提醒时间修改为 {new_time}")
                else:
                    yield event.plain_result("⚠️ 时间格式不正确，请使用 24 小时制，如 09:30 或 23:15")
                return

            # 3. 查询提醒时间
            if "查看提醒时间" in message_str:
                current_time = self.config.get("reminder_time", "09:00")
                yield event.plain_result(f"⏰ 当前提醒时间为 {current_time}")
                return

            # 默认响应
            yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
