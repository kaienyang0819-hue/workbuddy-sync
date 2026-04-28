# -*- coding: utf-8 -*-
"""
示例：使用系统策划文档标准格式生成器（基础示例）
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


def create_sample_doc():
    """创建示例策划文档"""
    wb, ws1, ws2, ws3, ws4 = create_workbook()
    for ws in [ws1, ws2, ws3, ws4]:
        setup_column_widths(ws)

    # ==================== 页签1：文档信息 ====================
    row = 1
    row = add_title_1(ws1, row, '【示例系统】')
    row = add_doc_info(ws1, row, '功能定位', '这是一个示例系统，展示标准格式策划文档的生成方法')

    row += 1
    row = add_version_table(ws1, row, [
        ('2026-03-27', 'V1.0', '初版文档', 'XXX'),
    ])

    row += 1
    row = add_doc_info(ws1, row, '文档状态', '评审中    预计上线：2026-Q2')

    row += 1
    row = add_people_table(ws1, row, [
        ('策划', 'XXX'),
        ('程序', 'XXX'),
        ('测试', 'XXX'),
    ])

    row += 1
    row = add_doc_info(ws1, row, '关联文档', '示例需求文档.md')

    # ==================== 页签2：设计内容 ====================
    row = 1

    # 设计目的
    row = add_title_1(ws2, row, '【设计目的】')
    row = add_single_line(ws2, row, '目标1：展示标准格式策划文档的生成方法')
    row = add_single_line(ws2, row, '目标2：提供统一的样式规范和视觉标准')

    row += 1

    # 系统流程
    row = add_title_1(ws2, row, '【系统流程】')
    row = add_title_3(ws2, row, '1、功能一：用户触发')

    row = add_rule_title(ws2, row, '规则1：用户点击按钮触发功能')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '用户在界面点击按钮，触发对应功能', auto_number=True)
    row = add_content(ws2, row, '系统校验用户权限后执行逻辑', auto_number=True)
    row = add_label(ws2, row, '2、交互图')
    row = add_content(ws2, row, '[嵌入：按钮触发流程图.png]', is_comment=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 按钮配置表.button_id字段（页签3-表1）', is_link=True)

    row = add_rule_title(ws2, row, '规则2：系统响应')
    row = add_label(ws2, row, '1、规则说明')
    reset_auto_number()
    row = add_content(ws2, row, '系统接收触发事件，执行对应逻辑', auto_number=True)
    row = add_content(ws2, row, '执行完成后返回结果给用户', auto_number=True)
    row = add_label(ws2, row, '2、交互图')
    row = add_content(ws2, row, '[嵌入：系统响应流程图.png]', is_comment=True)
    row = add_label(ws2, row, '3、表格配置')
    row = add_content(ws2, row, '→ 系统配置表.response字段（页签3-表2）', is_link=True)

    row += 1

    # 待决策项
    row = add_title_1(ws2, row, '【待决策项汇总】')
    row = add_pending_item(ws2, row, '待决策1：按钮样式是否统一？')
    row = add_pending_item(ws2, row, '待决策2：触发频率限制？')

    # ==================== 页签3：数值表格设计 ====================
    row = 1
    row = add_title_1(ws3, row, '【数值表格设计】')
    row = add_table(ws3, row, '表1-按钮配置表',
        headers=['字段名', '类型', '说明', '示例值'],
        data=[
            ['button_id', 'int', '按钮唯一ID', '1001'],
            ['button_name', 'string', '按钮名称', '确认'],
        ])

    # ==================== 页签4：tlog及打点设计 ====================
    row = 1
    row = add_title_1(ws4, row, '【tlog及打点设计】')
    row = add_table(ws4, row, '表1-按钮触发事件',
        headers=['事件名', '事件类型', '触发时机', '关键参数'],
        data=[
            ['Button_Click', '点击', '用户点击按钮', 'button_id, user_id'],
            ['Button_Response', '响应', '系统响应成功', 'button_id, response_code'],
        ])

    # 保存
    output_path = 'G:/project_output/示例策划文档.xlsx'
    wb.save(output_path)
    print(f'文档已生成: {output_path}')


if __name__ == '__main__':
    create_sample_doc()
