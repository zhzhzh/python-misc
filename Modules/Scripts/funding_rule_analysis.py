import requests
from pandas import DataFrame
import csv
import pandas as pd
from functools import reduce


def get_rules(folder_start='Risk'):
    if folder_start == 'Risk':
        folder_map = {
            'Risk.GenericOnline': 'online',
            'Risk.GenericRisk': 'GR'
        }
    elif folder_start == 'common':
        folder_map = {
            "pre-common": 'pre-common',
            "common-infra": 'common-infra',
            "common": 'common'
        }
    else:
        return None

    url = 'http://hyperlvs55.qa.paypal.com:8055/ruleapp/analyze/riskplanningdecisionserv/20170703_123553/'
    resp = requests.get(url)
    if resp.status_code != 200:
        return None

    json_data = resp.json()
    if json_data.get('result') != 'OK':
        return None

    data = json_data.get('data')
    df_all = DataFrame(data.get('rules'))

    df_1 = df_all[['rule_id', 'folder']]

    ret_map = {}
    for folder in folder_map:
        df_rules = df_1[df_1['folder'].map(lambda s: s.startswith(folder))]
        rules = df_rules['rule_id'].unique()
        ret_map.update({rule_id: folder_map[folder] for rule_id in rules})

    return ret_map


def get_rule_data(input_file, rules):
    rule_map = {}
    with open(input_file, 'r') as csv_file:
        data = csv.reader(csv_file)

        for row in data:
            rule_id, path, count = row
            path = path.strip('|')
            task = rules.get(rule_id, None)
            if task is not None:
                path_list = path.split('|')
                if task in path_list:
                    path = '|'.join(path_list[:path_list.index(task)])

            if rule_id not in rule_map:
                rule_map[rule_id] = {}

            if path not in rule_map[rule_id]:
                rule_map[rule_id][path] = 0
            rule_map[rule_id][path] += int(count)

            # rule_map[rule_id].append({
            #     'path': path,
            #     'count': count
            # })
    ret_map = {}
    for rule_id, path_map in rule_map.items():
        ret_map[rule_id] = [{
            'path': path,
            'count': count,
        } for path, count in path_map.items()]

    return ret_map


def get_common_path(path1, path2):
    if path1 is None:
        return path2
    if path2 is None:
        return path1

    pl1 = path1.split('|')
    pl2 = path2.split('|')

    common = [task for task in pl1 if task in pl2]
    # print('======[{}] & [{}] => {}'.format(path1, path2, common))
    return '|'.join(common)


def process_rule_data(rule_map, include_rules, output_file):
    print('rule count: {}'.format(len(rule_map)))
    count = 0
    json_list = []
    for rule_id, data_list in rule_map.items():
        path_list = [item['path'] for item in data_list]
        path_fire_count_list = ["{} ({})".format(item['path'], item['count']) for item in data_list]
        fire_count = reduce(lambda x,y: x+y, [item['count'] for item in data_list])

        path_count = len(path_list)
        can_move = False
        has_common = False
        common_path = None
        move_to = None

        if path_count == 1:
            path_str = path_list[0]
            common_path = path_str
            has_common = True

        else:
            path_str = ";".join(path_list)
            for path in path_list:
                common_path = get_common_path(common_path, path)
            if common_path is not None and common_path != "":
                has_common = True

                # print('{}\t{}\t{}\t{}'.format(rule_id, has_common, common_path, path_str))

        if has_common:
            can_move = True
            count += 1

            tmp_path_list = common_path.split('|')
            move_to = tmp_path_list[0]

        json_list.append(
            {
                "1_rule_id": rule_id,
                "2_path_count": path_count,
                "3_can_move": can_move,
                "4_move_to": move_to,
                "5_has_common": has_common,
                "6_common_path": common_path,
                "7_path_str": '\n'.join(path_fire_count_list),
                "8_in_task": include_rules.get(rule_id, '-'),
                "9_fire_volume": fire_count,
            }
        )

    df = pd.DataFrame(json_list)
    df_rule = df.set_index("1_rule_id").sort_index()
    df_rule.to_csv(output_file)
    print('Can Move count: {}'.format(count))


if __name__ == '__main__':
    rules = get_rules('common')
    rule_map = get_rule_data('rule_04_10.csv', rules)

    print(len(rule_map))
    if len(rule_map) > 0:
        process_rule_data(rule_map, rules, 'out_04_10_dd.csv')





