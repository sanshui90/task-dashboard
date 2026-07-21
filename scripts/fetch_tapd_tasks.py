#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAPD 任务数据拉取脚本
功能：从 TAPD API 获取任务数据，计算饱和度，输出 JSON 供前端使用
"""

import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import os

# TAPD API 配置
TAPD_API_TOKEN = os.environ.get('TAPD_API_TOKEN', 'b2193e4681b09f09729b99f45886bc4d180cc1db')
TAPD_API_BASE_URL = "https://api.tapd.cn"

# 项目池配置
WORKSPACES = {
    '交付池': '65152329',
    '产研池': '44949107'
}

def get_monday_of_week(date):
    """获取某日期所在周的周一"""
    weekday = date.weekday()
    return date - timedelta(days=weekday)

def get_date_range():
    """获取时间范围：上周 + 本周 + 下四周（共6周）"""
    today = datetime.now().date()
    this_monday = get_monday_of_week(today)
    last_monday = this_monday - timedelta(days=7)

    # 上周周一 到 下四周周五
    start_date = last_monday
    end_date = this_monday + timedelta(days=5 * 7 - 1)  # 下四周的周五

    return start_date, end_date, this_monday

def fetch_tasks(workspace_id, start_date, end_date):
    """从 TAPD API 获取任务数据（分页查询）"""
    headers = {
        "Authorization": f"Bearer {TAPD_API_TOKEN}"
    }

    # 构造日期范围字符串
    begin_range = f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}"

    # 获取任务列表（分页查询）
    url = f"{TAPD_API_BASE_URL}/tasks"
    all_tasks = []
    page = 1
    page_size = 100  # 每页100条
    
    while True:
        params = {
            "workspace_id": workspace_id,
            "begin": begin_range,
            "limit": page_size,
            "page": page,
            "fields": "id,name,owner,status,begin,due,effort,effort_completed,story_id,iteration_id,priority,workspace_id"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == 1:
                items = data.get("data", [])
                if not items:
                    break  # 没有更多数据了
                
                for item in items:
                    task = item.get("Task", {})
                    all_tasks.append(task)
                
                # 如果返回的数据少于页大小，说明已经是最后一页
                if len(items) < page_size:
                    break
                
                page += 1
            else:
                print(f"API 返回错误: {data}")
                break
        except Exception as e:
            print(f"获取任务失败: {e}")
            break
    
    return all_tasks

def calculate_saturation(hours):
    """计算饱和度状态"""
    if hours == 0:
        return "idle"  # 无颜色
    elif hours < 8:
        return "low"  # 灰色（不饱和）
    elif hours == 8:
        return "normal"  # 绿色（正常）
    elif hours <= 12:
        return "busy"  # 黄色（繁忙）
    else:
        return "overload"  # 红色（过载）

def determine_task_status(task, current_date):
    """判断任务状态"""
    status = task.get('status', '')
    begin = task.get('begin', '')

    # 已关闭
    if status == 'done':
        return 'done'

    # 超时未关闭：begin < 当前时间 && status != done
    if begin and begin < current_date.strftime('%Y-%m-%d'):
        return 'overdue'

    # 进行中
    if status in ['progress', 'in_progress', 'ongoing']:
        return 'in_progress'

    # 待处理
    return 'pending'

# 业务二组成员配置
TARGET_MEMBERS = ['云燕', '希希', '迷雾', '阿政', '翔宇', '千尘', '阿彭', '阿栋', '左耳', '时光', '盘古', '花洲', '大山', '奎克', '恒华']

# 成员展示顺序
MEMBER_ORDER = ['迷雾', '翔宇', '千尘', '阿栋', '左耳', '时光', '奎克', '阿彭', '云燕', '希希', '盘古', '阿政', '花洲', '大山', '恒华']

def get_member_order(member_name):
    """获取成员的排序位置"""
    clean_name = member_name.replace(';', '').replace('_', '').strip()
    for i, target in enumerate(MEMBER_ORDER):
        if target in clean_name or clean_name in target:
            return i
    return 999  # 未匹配的放最后

def is_target_member(member_name):
    """判断是否是业务二组成员"""
    clean_name = member_name.replace(';', '').replace('_', '').strip()
    for target in TARGET_MEMBERS:
        if target in clean_name or clean_name in target:
            return True
    return False

def process_tasks():
    """处理任务数据"""
    start_date, end_date, this_monday = get_date_range()
    current_date = datetime.now().date()

    print(f"📅 数据时间范围: {start_date} ~ {end_date}")
    print(f"📅 本周周一: {this_monday}")

    all_tasks = []

    # 从两个项目池获取任务
    for workspace_name, workspace_id in WORKSPACES.items():
        print(f"\n🔄 正在获取 {workspace_name} 任务...")
        tasks = fetch_tasks(workspace_id, start_date, end_date)
        print(f"✅ 获取到 {len(tasks)} 个任务")
        all_tasks.extend(tasks)

    print(f"\n📊 总共获取到 {len(all_tasks)} 个任务")

    # 筛选业务二组成员的任务
    filtered_tasks = [t for t in all_tasks if t.get('owner', '').strip() and is_target_member(t.get('owner', ''))]
    print(f"📊 业务二组成员任务: {len(filtered_tasks)} 个")

    # 按成员和日期分组
    member_tasks = defaultdict(list)
    daily_hours = defaultdict(lambda: defaultdict(float))
    daily_task_count = defaultdict(lambda: defaultdict(int))

    for task in filtered_tasks:
        owner = task.get('owner', '未知')
        begin = task.get('begin', '')
        effort = float(task.get('effort', 0) or 0)

        # 按成员分组
        member_tasks[owner].append(task)

        # 按日期统计工时
        if begin:
            daily_hours[owner][begin] += effort
            daily_task_count[owner][begin] += 1

    # 构建输出数据
    output = {
        "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "date_range": {
            "start": start_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d'),
            "this_monday": this_monday.strftime('%Y-%m-%d')
        },
        "members": [],
        "summary": {
            "total_tasks": len(filtered_tasks),
            "by_status": defaultdict(int),
            "by_week": defaultdict(int)
        }
    }

    # 统计任务状态
    for task in filtered_tasks:
        status = determine_task_status(task, current_date)
        output["summary"]["by_status"][status] += 1

    # 统计每周任务数
    for task in filtered_tasks:
        begin = task.get('begin', '')
        if begin:
            task_date = datetime.strptime(begin, '%Y-%m-%d').date()
            week_monday = get_monday_of_week(task_date)
            week_key = week_monday.strftime('%Y-%m-%d')
            output["summary"]["by_week"][week_key] += 1

    # 构建成员数据
    for owner, tasks in member_tasks.items():
        member_data = {
            "name": owner,
            "avatar": owner[0] if owner else '?',
            "task_count": len(tasks),
            "tasks": [],
            "daily_data": {}
        }

        # 按日期构建工时数据
        for date, hours in daily_hours[owner].items():
            member_data["daily_data"][date] = {
                "hours": hours,
                "task_count": daily_task_count[owner][date],
                "saturation": calculate_saturation(hours)
            }

        # 构建任务列表（按开始时间正序）
        sorted_tasks = sorted(tasks, key=lambda x: x.get('begin', ''))
        for task in sorted_tasks:
            task_data = {
                "id": task.get('id', ''),
                "name": task.get('name', ''),
                "status": determine_task_status(task, current_date),
                "begin": task.get('begin', ''),
                "due": task.get('due', ''),
                "effort": float(task.get('effort', 0) or 0),
                "effort_completed": float(task.get('effort_completed', 0) or 0),
                "story_id": task.get('story_id', ''),
                "workspace_id": task.get('workspace_id', ''),
                "owner": task.get('owner', '')
            }
            member_data["tasks"].append(task_data)

        output["members"].append(member_data)

    # 按照指定顺序排序成员
    output["members"].sort(key=lambda x: get_member_order(x["name"]))

    return output

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 TAPD 任务数据拉取脚本")
    print("=" * 60)

    # 处理任务数据
    output_data = process_tasks()

    # 输出 JSON 文件
    output_file = os.path.expanduser("~/.openclaw/workspace/data/tasks.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据已保存到: {output_file}")
    print(f"📊 业务二组成员: {len(output_data['members'])} 人")
    print(f"📊 任务总数: {output_data['summary']['total_tasks']}")
    print(f"📊 状态统计: {dict(output_data['summary']['by_status'])}")

if __name__ == "__main__":
    main()
