#!/usr/bin/env python3
import os
import json

all_items = set()

def get_fixed_reward_items(record, max_column_count):
    items = []
    for i in range(max_column_count):
        item = record['RewardItem%02d' % i]
        item_id_final = item['Category'] * 10000 if item['ItemID'] == 0 else item['ItemID']
        all_items.add(item_id_final)
        items.append('{ %d, %d, %d }' % (item['Num'], item_id_final, item['SubjectType']))
    return items


def get_lottery_reward_items(record, max_column_count):
    items = []
    for i in range(max_column_count):
        item = record['RewardItem%02d' % i]
        flag = 'true' if item['RareItemFlag'] else 'false'
        if item['Category'] == 0:
            item_id_final = item['ItemID']
        elif item['Category'] == 1:
            item_id_final = 10000 if item['ItemID'] == 0 else item['ItemID']
        else:
            item_id_final = 20000 if item['ItemID'] == 0 else item['ItemID']
        all_items.add(item_id_final)
        items.append('{ %d, %d, %d, %s }' % (item['Num'], item_id_final, item['Rate'], flag))
    return items


def get_record(record, rate_total, item_fetcher, max_column_count):
    return '    { 0x%016X,%s { %s } },\n' % (record['TableName'], rate_total, ', '.join(item_fetcher(record, max_column_count)))


def get_used_coulmn_count(record, column_count):
    used_coulmn_count = 0
    for j in range(column_count):
        item = record['RewardItem%02d' % j]
        if item['Num'] != 0 or item['Category'] != 0 or item['ItemID'] != 0:
            used_coulmn_count = j + 1
    return used_coulmn_count


def get_max_used_column_count(rows, column_count):
    max_column_count = 0
    for record in rows:
        used_column_count = get_used_coulmn_count(record, column_count)
        if used_column_count > max_column_count:
            max_column_count = used_column_count
    return max_column_count


def write_cpp(type_name, variable_name, is_lottery, rows, path):
    item_fetcher = get_lottery_reward_items if is_lottery else get_fixed_reward_items
    column_count = 30 if is_lottery else 15
    max_column_count = get_max_used_column_count(rows, column_count)
    cpp = 'static const %s %s[] =\n{\n' % (type_name, variable_name)
    for record in rows:
        if get_used_coulmn_count(record, column_count) == 0:
            continue
        rate_total = 0
        if is_lottery:
            for i in range(column_count):
                rate_total += record['RewardItem%02d' % i]['Rate']
        cpp += get_record(record, ' %d,' % rate_total if rate_total > 0 else '', item_fetcher, max_column_count)
    cpp += '};\n'
    with open(path, 'w') as f:
        f.write(cpp)
    return max_column_count


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.realpath(__file__))
    events_dir = os.path.join(base_dir, 'events')
    events = [f.path for f in os.scandir(events_dir) if f.is_dir()]
    events.sort()
    with open(os.path.join(base_dir, 'base', 'fixed_reward_item_array.json'), 'r') as f:
        fixed = json.load(f)
    max_fixed_columns_base = get_max_used_column_count(fixed, 15)
    for event_path in events:
        with open(os.path.join(event_path, 'fixed_reward_item_array.json'), 'r') as f:
            fixed.extend(json.load(f)['Table'])
    with open(os.path.join(base_dir, 'base', 'lottery_reward_item_array.json'), 'r') as f:
        lottery = json.load(f)
    max_lottery_columns_base = get_max_used_column_count(lottery, 30)
    for event_path in events:
        with open(os.path.join(event_path, 'lottery_reward_item_array.json'), 'r') as f:
            lottery.extend(json.load(f)['Table'])

    raidcalc_dir = os.path.join(base_dir, '..', 'RaidCalc')
    max_fixed_columns_events = write_cpp('RaidFixedRewards', 'fixed_rewards', False, fixed, os.path.join(raidcalc_dir, 'RaidFixedRewards.inc.h'))
    max_lottery_columns_events = write_cpp('RaidLotteryRewards', 'lottery_rewards', True, lottery, os.path.join(raidcalc_dir, 'RaidLotteryRewards.inc.h'))
    print('Max fixed items columns (base): %d' % max_fixed_columns_base)
    print('Max lottery items columns (base): %d' % max_lottery_columns_base)
    print('Max fixed items columns (events): %d' % max_fixed_columns_events)
    print('Max lottery items columns (events): %d' % max_lottery_columns_events)
    items = list(all_items)
    items.sort()
    print('int[] possible_rewards = { %s };' % ', '.join([str(item) for item in items[1:]]))
