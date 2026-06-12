from typing import Any, ClassVar
from datetime import datetime, timedelta
import aiohttp
import json
import os

from maibot_sdk import (
    MaiBotPlugin,
    Tool,
    Command,
    PluginConfigBase,
    Field,
)
from maibot_sdk.types import ToolParameterInfo, ToolParamType


# LLM 扩展提示词（无换行）
LLM_EXPAND_PROMPT = (
    "你是一个日期信息助手。将以下日期信息整理成自然语言。原始信息: {raw_info}。"
    "输出时必须包含昨天今天明天三天的日期、星期几和节假日。调休工作日需特别说明。"
    "直接输出内容，不要JSON。"
)

# 节假日数据 URL 模板
HOLIDAY_URL_TEMPLATE = "https://unpkg.com/holiday-calendar@1.3.0/data/CN/{year}.json"

# 内置备用节假日（固定节日）
FIXED_HOLIDAYS = {
    "01-01": "元旦",
    "02-14": "情人节",
    "03-08": "妇女节",
    "04-01": "愚人节",
    "05-01": "劳动节",
    "05-04": "青年节",
    "06-01": "儿童节",
    "07-01": "建党节",
    "08-01": "建军节",
    "09-10": "教师节",
    "10-01": "国庆节",
    "12-25": "圣诞节",
}

# 缓存目录
CACHE_DIR = "data/holidays"


def get_weekday_cn(date: datetime) -> str:
    """获取中文星期几"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return weekdays[date.weekday()]


def format_date_short(date: datetime) -> str:
    """格式化为 '1月2日' 格式"""
    return f"{date.month}月{date.day}日"


def get_holiday_name(date_str: str, holiday_map: dict[str, Any]) -> str:
    """从缓存中获取节假日名称"""
    if date_str in holiday_map:
        info = holiday_map[date_str]
        name = info.get("name_cn", "")
        holiday_type = info.get("type", "")
        if holiday_type == "transfer_workday":
            return f"{name}（调休）"
        return name
    # 备用：检查固定节日
    month_day = date_str[5:]  # 格式: "01-01"
    return FIXED_HOLIDAYS.get(month_day, "")


async def download_holiday_data(year: int) -> dict[str, Any]:
    """下载指定年份的节假日数据"""
    url = HOLIDAY_URL_TEMPLATE.format(year=year)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # 转换为字典格式，方便查询
                    holiday_map = {}
                    for item in data.get("dates", []):
                        holiday_map[item["date"]] = item
                    return holiday_map
                else:
                    return {}
    except Exception:
        return {}


def load_cached_holiday(year: int) -> dict[str, Any]:
    """从本地缓存加载节假日数据"""
    cache_file = os.path.join(CACHE_DIR, f"{year}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cached_holiday(year: int, data: dict[str, Any]) -> None:
    """保存节假日数据到本地缓存"""
    cache_file = os.path.join(CACHE_DIR, f"{year}.json")
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


async def get_holiday_map(year: int) -> dict[str, Any]:
    """获取节假日数据（优先本地缓存，无则下载）"""
    # 先尝试加载缓存
    holiday_map = load_cached_holiday(year)
    if holiday_map:
        return holiday_map

    # 下载并缓存
    holiday_map = await download_holiday_data(year)
    if holiday_map:
        save_cached_holiday(year, holiday_map)

    return holiday_map


def get_three_days_raw_info() -> dict[str, dict[str, str]]:
    """获取昨天、今天、明天的基础信息（不含节假日）"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    return {
        "yesterday": {
            "date_str": yesterday.strftime("%Y-%m-%d"),
            "date_short": format_date_short(yesterday),
            "weekday": get_weekday_cn(yesterday),
        },
        "today": {
            "date_str": today.strftime("%Y-%m-%d"),
            "date_short": format_date_short(today),
            "weekday": get_weekday_cn(today),
        },
        "tomorrow": {
            "date_str": tomorrow.strftime("%Y-%m-%d"),
            "date_short": format_date_short(tomorrow),
            "weekday": get_weekday_cn(tomorrow),
        },
    }


async def get_three_days_info() -> str:
    """获取三天完整信息，格式化为字符串"""
    today = datetime.now()
    year = today.year

    # 获取节假日数据
    holiday_map = await get_holiday_map(year)

    # 获取基础信息
    base_info = get_three_days_raw_info()

    # 构建输出（竖线分隔格式，更清晰）
    lines = []
    for day_name, info in [("昨天", base_info["yesterday"]), ("今天", base_info["today"]), ("明天", base_info["tomorrow"])]:
        date_str = info["date_str"]
        holiday = get_holiday_name(date_str, holiday_map)
        if holiday:
            line = f"{day_name} | {info['date_short']} {info['weekday']}【{holiday}】"
        else:
            line = f"{day_name} | {info['date_short']} {info['weekday']}"
        lines.append(line)

    return "\n".join(lines)


class DateAwarePluginConfig(PluginConfigBase):
    """日期感知插件配置"""
    enabled: bool = Field(default=True, description="是否启用插件")
    enable_llm_expand: bool = Field(default=False, description="是否启用 LLM 扩展日期信息")
    llm_model: str = Field(default="replyer", description="使用的模型名称")


class DateAwarePlugin(MaiBotPlugin):
    """日期感知插件 - 让 Bot 能够感知并展示日期信息"""

    config_model = DateAwarePluginConfig

    async def on_load(self) -> None:
        """插件加载时初始化"""
        self.ctx.logger.info("日期感知插件已加载")

    async def on_unload(self) -> None:
        """插件卸载时清理资源"""
        self.ctx.logger.info("日期感知插件正在卸载")

    async def on_config_update(self, scope: str, config_data: dict[str, Any], version: str) -> None:
        """处理配置热更新"""
        if scope == "self":
            self.ctx.logger.info("插件配置已更新: version=%s", version)

    @Tool(
        "get_date_info",
        brief_description="获取昨天、今天、明天的日期、星期几和节假日信息",
        detailed_description="获取日期信息工具。LLM 可根据需要调用此工具来获取当前日期上下文。",
    )
    async def handle_get_date_info(self, **kwargs) -> dict[str, Any]:
        """执行获取日期信息"""
        try:
            info = await get_three_days_info()
            return {
                "content": info,
                "description": "日期信息已获取",
            }
        except Exception as e:
            self.ctx.logger.error(f"获取日期信息失败: {e}")
            return {"content": "", "error": str(e)}

    @Command("date", pattern=r"^/date$")
    async def handle_date_query(self, **kwargs) -> tuple[bool, str, int]:
        """执行日期查询"""
        try:
            stream_id = kwargs.get("stream_id", "")
            # 获取原始日期信息
            raw_info = await get_three_days_info()

            # 检查是否需要 LLM 扩展
            if self.config.enable_llm_expand:
                try:
                    prompt = LLM_EXPAND_PROMPT.format(raw_info=raw_info)
                    result = await self.ctx.llm.generate_text(prompt)
                    if result:
                        message = result.strip()
                    else:
                        message = raw_info
                except Exception:
                    message = raw_info
            else:
                message = raw_info

            await self.ctx.send.text(message, stream_id)

            return True, f"显示了日期信息: {message}", 2
        except Exception as e:
            self.ctx.logger.error(f"日期查询失败: {e}")
            stream_id = kwargs.get("stream_id", "")
            await self.ctx.send.text("查询日期信息失败，请稍后再试", stream_id)
            return True, f"查询失败: {e}", 1


def create_plugin():
    return DateAwarePlugin()
