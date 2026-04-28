# -*- coding: utf-8 -*-
"""
示例：签到系统策划文档（中等复杂度）
展示多模块、子层级、三件套简化、图片嵌入、多配置表的综合用法。
"""

import sys
sys.path.insert(0, r'C:\Users\kaienyang\.workbuddy\skills\game-design-doc-template')

from scripts.generate_design_doc import (
    create_workbook, setup_column_widths,
    add_title_1, add_title_2, add_title_3,
    add_rule_title, add_label, add_content, add_single_line,
    add_pending_item, add_doc_info, add_version_table, add_people_table,
    add_table, reset_auto_number,
)


def create_signin_doc():
    """创建签到系统策划文档"""
    wb, ws1, ws2, ws3, ws4 = create_workbook()
    for ws in [ws1, ws2, ws3, ws4]:
        setup_column_widths(ws)

    # ==================== 页签1：文档信息 ====================
    row = 1
    row = add_title_1(ws1, row, '【每日签到系统】')
    row = add_doc_info(ws1, row, '功能定位', '通过每日签到奖励提升用户留存率，支持普通签到+累计签到双轨制')

    row += 1
    row = add_version_table(ws1, row, [
        ('2026-03-27', 'V1.0', '初版文档', 'AI生成'),
    ])

    row += 1
    row = add_doc_info(ws1, row, '文档状态', '评审中')

    row += 1
    row = add_people_table(ws1, row, [
        ('策划', 'XXX'),
        ('程序', 'XXX'),
        ('美术', 'XXX'),
        ('测试', 'XXX'),
    ])

    row += 1
    row = add_doc_info(ws1, row, '关联文档', '活动系统设计.xlsx、奖励产出规划.md')

    # ==================== 页签2：设计内容 ====================
    row = 1

    # ===== 模块1: 需求背景（概述结构） =====
    row = add_title_1(ws2, row, '【需求背景】')
    row = add_title_2(ws2, row, '现状与痛点')
    row = add_single_line(ws2, row, '当前版本缺少每日活跃激励手段，次日留存率较同类产品低8%')
    row = add_single_line(ws2, row, '竞品分析：主流FPS均已上线签到系统，且签到是DAU的重要组成部分')
    row = add_title_2(ws2, row, '设计目标')
    row = add_single_line(ws2, row, '目标1：提升次日留存率5%+')
    row = add_single_line(ws2, row, '目标2：提供稳定的每日奖励产出渠道')
    row = add_single_line(ws2, row, '目标3：通过累计签到提供长线追求目标')
    row += 1

    # ===== 模块2: 系统概述（概述结构） =====
    row = add_title_1(ws2, row, '【系统概述】')
    row = add_single_line(ws2, row, '签到系统分为两个子模块：')
    row = add_single_line(ws2, row, '1. 每日签到 — 每天登录即可领取当日奖励')
    row = add_single_line(ws2, row, '2. 累计签到 — 累计签到天数达到里程碑可领取额外大奖')
    row += 1

    # ===== 模块3: 界面入口（规则结构，简化三件套） =====
    row = add_title_1(ws2, row, '【界面入口】')

    row = add_rule_title(ws2, row, '规则1：大厅入口显示')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '大厅左侧活动栏 - 签到icon', auto_number=True)
    row = add_content(ws2, row, '有未领取奖励时显示红点', auto_number=True)
    row = add_content(ws2, row, '首次上线自动弹出签到界面（每日仅弹1次）', auto_number=True)
    # 纯逻辑规则，无交互图和配置表 → 简化三件套，只写规则说明

    row = add_rule_title(ws2, row, '规则2：功能开启条件')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '账号等级 ≥ 3级开放签到功能', auto_number=True)
    row = add_content(ws2, row, '未达等级时icon置灰，点击提示：等级达到3级后开放', auto_number=True, is_highlight=True)
    row += 1

    # ===== 模块4: 每日签到（规则结构，完整三件套） =====
    row = add_title_1(ws2, row, '【每日签到】')

    row = add_rule_title(ws2, row, '规则1：签到规则与奖励')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '每日0:00刷新签到状态', auto_number=True)
    row = add_content(ws2, row, '点击签到按钮即可领取当日奖励', auto_number=True)
    row = add_content(ws2, row, '签到奖励按周循环，每7天为一个周期', auto_number=True)
    row = add_content(ws2, row, '奖励品质逐日递增：', auto_number=True)
    # 子层级展示
    row = add_content(ws2, row, '周一~周三：普通奖励（经验+银币）', is_sub=True)
    row = add_content(ws2, row, '周四~周五：稀有奖励（经验+银币+道具碎片）', is_sub=True)
    row = add_content(ws2, row, '周六：史诗奖励（宝箱x1）', is_sub=True)
    row = add_content(ws2, row, '周日：传说奖励（自选宝箱x1）', is_sub=True)
    row = add_content(ws2, row, '当日未签到不可补签（后续版本可开放补签卡）', auto_number=True)
    row = add_label(ws2, row, '2、交互图')
    row = add_content(ws2, row, '[嵌入：每日签到界面截图]', is_comment=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 每日签到奖励配置表（页签3-表1）', is_link=True)

    row = add_rule_title(ws2, row, '规则2：签到动画与反馈')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '点击签到后播放领取动画（0.5s）', auto_number=True)
    row = add_content(ws2, row, '动画结束后展示奖励弹窗：获得XXX x{数量}', auto_number=True, is_highlight=True)
    row = add_content(ws2, row, '奖励弹窗3s后自动关闭，点击任意处也可关闭', auto_number=True)
    row = add_label(ws2, row, '2、交互图')
    row = add_content(ws2, row, '[嵌入：签到动画流程图]', is_comment=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 动画配置', is_link=True)
    row += 1

    # ===== 模块5: 累计签到（规则结构） =====
    row = add_title_1(ws2, row, '【累计签到】')

    row = add_rule_title(ws2, row, '规则1：累计里程碑奖励')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '累计签到天数达到里程碑时，解锁额外奖励', auto_number=True)
    row = add_content(ws2, row, '里程碑节点：7天/14天/28天/60天/100天', auto_number=True)
    row = add_content(ws2, row, '里程碑奖励需手动点击领取', auto_number=True)
    row = add_content(ws2, row, '已解锁未领取的里程碑显示"可领取"标记', auto_number=True)
    row = add_content(ws2, row, '100天为赛季最终大奖，赛季结束后重置累计天数', auto_number=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 累计签到里程碑配置表（页签3-表2）', is_link=True)
    row += 1

    # ===== 模块6: 面板开关控制（规则结构，简化） =====
    row = add_title_1(ws2, row, '【面板开关控制】')
    row = add_rule_title(ws2, row, '规则1：开关体系')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '总开关：控制签到系统整体显隐', auto_number=True)
    row = add_content(ws2, row, '每日签到开关：单独控制每日签到模块', auto_number=True)
    row = add_content(ws2, row, '累计签到开关：单独控制累计签到模块', auto_number=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 开关配置表（页签3-表3）', is_link=True)
    row += 1

    # ===== 模块7: 待决策项 =====
    row = add_title_1(ws2, row, '【待决策项汇总】')
    row = add_pending_item(ws2, row, '待决策1：是否支持补签卡？补签卡的获取途径？')
    row = add_pending_item(ws2, row, '待决策2：赛季周期多长？和排位赛季同步还是独立？')
    row = add_pending_item(ws2, row, '待决策3：累计100天大奖的具体内容？')

    # ==================== 页签3：数值表格设计 ====================
    row = 1
    row = add_title_1(ws3, row, '【数值表格设计】')

    row = add_table(ws3, row, '表1-每日签到奖励配置表',
        headers=['天序', '品质', '奖励类型', '奖励内容', '数量', '说明'],
        data=[
            ['周一', '普通', '经验+银币', '经验100+银币200', '1', '基础奖励'],
            ['周二', '普通', '经验+银币', '经验120+银币250', '1', '基础奖励'],
            ['周三', '普通', '经验+银币', '经验150+银币300', '1', '基础奖励'],
            ['周四', '稀有', '经验+银币+碎片', '经验200+银币400+碎片x5', '1', '递增奖励'],
            ['周五', '稀有', '经验+银币+碎片', '经验250+银币500+碎片x8', '1', '递增奖励'],
            ['周六', '史诗', '宝箱', '普通宝箱x1', '1', '周末大奖'],
            ['周日', '传说', '自选宝箱', '自选宝箱x1', '1', '周末大奖'],
        ])
    row += 1

    row = add_table(ws3, row, '表2-累计签到里程碑配置表',
        headers=['里程碑ID', '累计天数', '奖励类型', '奖励内容', '数量'],
        data=[
            ['M001', '7', '道具', '补签卡', '1'],
            ['M002', '14', '货币', '钻石x100', '1'],
            ['M003', '28', '装扮', '限定头像框', '1'],
            ['M004', '60', '装扮', '限定称号', '1'],
            ['M005', '100', '自选', '赛季终极大奖自选', '1'],
        ])
    row += 1

    row = add_table(ws3, row, '表3-开关配置表',
        headers=['开关ID', '开关名称', '默认值', '说明'],
        data=[
            ['SW101', '签到系统总开关', '1(开)', '控制整个签到系统'],
            ['SW102', '每日签到开关', '1(开)', '控制每日签到模块'],
            ['SW103', '累计签到开关', '1(开)', '控制累计签到模块'],
        ])

    # ==================== 页签4：tlog及打点设计 ====================
    row = 1
    row = add_title_1(ws4, row, '【tlog及打点设计】')

    row = add_table(ws4, row, '表1-签到事件打点',
        headers=['事件名', '事件类型', '触发时机', '关键参数', '优先级'],
        data=[
            ['signin_enter', '入口', '进入签到界面', 'user_id', 'P0'],
            ['signin_daily', '操作', '完成每日签到', 'user_id, day_seq, reward_id', 'P0'],
            ['signin_milestone', '操作', '领取累计里程碑奖励', 'user_id, milestone_id, reward_id', 'P0'],
            ['signin_popup_show', '曝光', '签到弹窗自动弹出', 'user_id', 'P1'],
            ['signin_popup_close', '操作', '关闭签到弹窗', 'user_id, close_type(手动/自动)', 'P1'],
        ])

    # 保存
    output_path = 'G:/project_output/签到系统策划文档_示例.xlsx'
    wb.save(output_path)
    print(f'文档已生成: {output_path}')


if __name__ == '__main__':
    create_signin_doc()
