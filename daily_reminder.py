import os
import json
import datetime
import asyncio
from astrbot.api import Plugin

class DailyReminder(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.config_path = os.path.join(os.path.dirname(__file__), "data", "config.json")
        self.tasks = []
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.tasks = json.load(f).get("tasks", [])
        else:
            self.logger.error("配置文件不存在: " + self.config_path)

    async def on_startup(self):
        self.bot.loop.create_task(self.reminder_loop())

    async def reminder_loop(self):
        while True:
            now_time = datetime.datetime.now().strftime("%H:%M")
            for task in self.tasks:
                if task["time"] == now_time:
                    await self.send_to_friend(task["qq"], task["message"])
            await asyncio.sleep(60)

    async def send_to_friend(self, qq, message):
        try:
            await self.bot.call_api(
                "send_private_msg",
                user_id=qq,
                message=message
            )
            self.logger.info(f"已向 {qq} 发送提醒: {message}")
        except Exception as e:
            self.logger.error(f"发送给 {qq} 失败: {e}")