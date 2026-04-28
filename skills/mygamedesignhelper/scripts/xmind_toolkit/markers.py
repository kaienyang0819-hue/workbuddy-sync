"""
标记图标双向映射表

XMind 内部 marker ID ↔ 人类可读 emoji/文本 的双向转换。
AI 在解析和生成时都依赖此表。

使用方式:
    from xmind_toolkit.markers import marker_to_emoji, emoji_to_marker

    # XMind → 展示
    marker_to_emoji('priority-1')  # → '🔴P1'

    # 展示 → XMind
    emoji_to_marker('🔴P1')       # → 'priority-1'
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# XMind marker ID → 人类可读文本
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MARKER_TO_EMOJI = {
    # 优先级
    'priority-1': '🔴P1',
    'priority-2': '🟠P2',
    'priority-3': '🟡P3',
    'priority-4': '🟢P4',
    'priority-5': '🔵P5',
    'priority-6': '🟣P6',
    'priority-7': '⚪P7',
    'priority-8': '⚫P8',
    'priority-9': '🔘P9',

    # 符号
    'symbol-wrong':    '❌',
    'symbol-right':    '✅',
    'symbol-exclam':   '⚠️',
    'symbol-attention': '⚠️',
    'symbol-question': '❓',
    'symbol-info':     'ℹ️',
    'symbol-plus':     '➕',
    'symbol-minus':    '➖',
    'symbol-pause':    '⏸️',

    # 自定义符号 (c_symbol_*)
    'c_symbol_like':          '👍',
    'c_symbol_dislike':       '👎',
    'c_symbol_heart':         '❤️',
    'c_symbol_money':         '💰',
    'c_symbol_trophy':        '🏆',
    'c_symbol_medals':        '🏅',
    'c_symbol_pen':           '🖊️',
    'c_symbol_music':         '🎵',
    'c_symbol_telephone':     '📞',
    'c_symbol_shopping_cart': '🛒',
    'c_symbol_flight':        '✈️',
    'c_symbol_exercise':      '🏃',
    'c_symbol_drink':         '🍹',
    'c_symbol_thermometer':   '🌡️',
    'c_symbol_bar_chart':     '📊',
    'c_symbol_pie_chart':     '🥧',
    'c_symbol_line_graph':    '📈',
    'c_symbol_contact':       '👤',
    'c_symbol_idea':          '💡',

    # 星标
    'star-orange': '⭐',
    'star-red':    '🌟',
    'star-yellow': '💛',
    'star-blue':   '💙',
    'star-green':  '💚',
    'star-purple': '💜',

    # 任务进度
    'task-done':    '✅完成',
    'task-half':    '🔄进行中',
    'task-start':   '🔲待开始',
    'task-oct':     '⬜12.5%',
    'task-quarter': '⬜25%',
    'task-3oct':    '⬜37.5%',
    'task-5oct':    '⬜62.5%',
    'task-3quar':   '⬜75%',
    'task-7oct':    '⬜87.5%',
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 人类可读文本 → XMind marker ID (反向映射)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMOJI_TO_MARKER = {v: k for k, v in MARKER_TO_EMOJI.items()}

# 补充一些常见的 AI 可能生成的变体写法
EMOJI_TO_MARKER.update({
    # 简写优先级
    'P1': 'priority-1',  'P2': 'priority-2',  'P3': 'priority-3',
    'P4': 'priority-4',  'P5': 'priority-5',

    # 纯 emoji 也能匹配
    '✅': 'symbol-right',
    '❌': 'symbol-wrong',
    '⚠️': 'symbol-exclam',
    '❓': 'symbol-question',
    'ℹ️': 'symbol-info',
    '⭐': 'star-orange',
    '🌟': 'star-red',
    '👍': 'c_symbol_like',
    '💡': 'c_symbol_idea',

    # 任务进度的中文写法
    '完成': 'task-done',
    '进行中': 'task-half',
    '待开始': 'task-start',
})


def marker_to_emoji(marker_id: str) -> str:
    """将 XMind marker ID 转为人类可读的 emoji 文本。
    
    Args:
        marker_id: XMind 内部 marker 标识符，如 'priority-1'
    
    Returns:
        对应的 emoji 文本，如 '🔴P1'；未知 marker 返回 '[marker_id]'
    """
    return MARKER_TO_EMOJI.get(marker_id, f'[{marker_id}]')


def emoji_to_marker(text: str) -> str | None:
    """将 emoji/文本 转回 XMind marker ID。
    
    Args:
        text: 人类可读文本，如 '🔴P1' 或 '✅完成'
    
    Returns:
        XMind marker ID，如 'priority-1'；无匹配返回 None
    """
    return EMOJI_TO_MARKER.get(text.strip())
