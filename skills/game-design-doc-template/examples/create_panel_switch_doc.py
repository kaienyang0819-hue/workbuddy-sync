# -*- coding: utf-8 -*-
"""
示例：生成面板开关控制策划文档
"""

import sys
sys.path.insert(0, r'C:\Users\kaienyang\.workbuddy\skills\game-design-doc-template')

from scripts.generate_design_doc import (
    create_workbook, setup_column_widths,
    add_title_1, add_rule_title, add_label, add_content, add_single_line,
    add_doc_info, add_version_table, add_people_table,
    add_table, reset_auto_number,
)


def create_panel_switch_doc():
    """创建面板开关控制策划文档"""
    wb, ws1, ws2, ws3, ws4 = create_workbook()
    for ws in [ws1, ws2, ws3, ws4]:
        setup_column_widths(ws)

    # ==================== 页签1：文档信息 ====================
    row = 1
    row = add_title_1(ws1, row, '【面板开关控制】')
    row = add_doc_info(ws1, row, '功能定位', '通过面板开关控制各功能模块的显示与隐藏，支持PC和移动端差异化配置')

    row += 1
    row = add_version_table(ws1, row, [
        ('2026-03-26', 'V1.0', '初版文档', 'XXX'),
    ])

    row += 1
    row = add_doc_info(ws1, row, '文档状态', '评审中')

    row += 1
    row = add_people_table(ws1, row, [
        ('策划', 'XXX'),
    ])

    # ==================== 页签2：设计内容 ====================
    row = 1
    row = add_title_1(ws2, row, '【面板开关控制】')

    # 规则1
    row = add_rule_title(ws2, row, '规则1：资源清理触发弹窗开关控制')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '资源清理触发弹窗受此开关391095控制，该开关可控制移动和PC', auto_number=True)
    row = add_content(ws2, row, '开关功能：控制提醒清理的弹窗是否显示', auto_number=True)
    row = add_content(ws2, row, '0=不显示，1=正常显示；支持配置PC显示、移动配置显示', auto_number=True)
    row = add_label(ws2, row, '2、交互图')
    row = add_content(ws2, row, '[嵌入：资源清理弹窗开关控制流程图.png]', is_comment=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 面板开关配置表.switch_id字段（页签3-表1）', is_link=True)

    # 规则2
    row = add_rule_title(ws2, row, '规则2：一键清理（快速选择）开关控制')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '一键清理功能受此开关391094控制，该开关可控制移动和PC', auto_number=True)
    row = add_content(ws2, row, '0=不显示，1=正常显示；支持配置PC显示、移动不显示', auto_number=True)
    row = add_content(ws2, row, '开关关闭时，设置-资源清理-一键清理功能不展示', auto_number=True)
    row = add_content(ws2, row, '开关关闭时，点击资源触发清理的前往按钮仍一键勾选可清理的资源', auto_number=True)
    row = add_label(ws2, row, '2、交互图')
    row = add_content(ws2, row, '[嵌入：一键清理开关控制流程图.png]', is_comment=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 面板开关配置表.switch_id字段（页签3-表1）', is_link=True)

    # ==================== 页签3：数值表格设计 ====================
    row = 1
    row = add_title_1(ws3, row, '【数值表格设计】')
    row = add_table(ws3, row, '表1-面板开关配置表',
        headers=['字段名', '类型', '说明', '示例值'],
        data=[
            ['switch_id', 'int', '开关ID', '391095'],
            ['switch_name', 'string', '开关名称', '资源清理触发弹窗开关'],
            ['switch_type', 'int', '开关类型(1弹窗/2功能)', '1'],
            ['platform', 'string', '适用平台', 'PC,移动'],
            ['default_value', 'int', '默认值(0关/1开)', '1'],
            ['description', 'string', '开关说明', '控制提醒清理的弹窗是否显示'],
        ])

    # ==================== 页签4：tlog及打点设计 ====================
    row = 1
    row = add_title_1(ws4, row, '【tlog及打点设计】')
    row = add_table(ws4, row, '表1-面板开关操作事件',
        headers=['事件名', '事件类型', '触发时机', '关键参数'],
        data=[
            ['Panel_Switch_Change', '操作', '开关状态变更', 'switch_id, old_value, new_value'],
            ['Panel_Switch_View', '曝光', '查看开关状态', 'switch_id, current_value'],
        ])

    # 保存
    output_path = 'G:/project_output/面板开关控制策划文档.xlsx'
    wb.save(output_path)
    print(f'文档已生成: {output_path}')


if __name__ == '__main__':
    create_panel_switch_doc()
