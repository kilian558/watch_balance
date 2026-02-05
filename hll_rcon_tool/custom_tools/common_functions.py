"""
Minimal shared helpers for watch_balance.
"""

DISCORD_EMBED_AUTHOR_URL = "https://github.com/MarechJ/hll_rcon_tool"
DISCORD_EMBED_AUTHOR_ICON_URL = "https://raw.githubusercontent.com/MarechJ/hll_rcon_tool/master/logo.png"


def bold_the_highest(value1: int, value2: int) -> tuple[str, str]:
    if value1 > value2:
        return f"**{value1}**", str(value2)
    if value2 > value1:
        return str(value1), f"**{value2}**"
    return str(value1), str(value2)


def green_to_red(value: float, min_value: float = 1.0, max_value: float = 2.0) -> str:
    if max_value <= min_value:
        return "00ff00"
    ratio = (value - min_value) / (max_value - min_value)
    ratio = max(0.0, min(1.0, ratio))
    red = int(255 * ratio)
    green = int(255 * (1 - ratio))
    return f"{red:02x}{green:02x}00"
