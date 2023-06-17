import json
import pandas as pd


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


def to_excel(data):
    writer = pd.ExcelWriter('risk_generic_rules.xlsx')
    data.to_excel(writer, 'result')
    writer.save()

if __name__ == "__main__":
    with open("rule_fire_0704.json") as data_file:
        data = json.load(data_file)

    rule_map = {}

    for line in data:
        path = line['risk_path']
        count = line['count']
        if path != "":
            rule_id = line['ruleid']
            if rule_id not in rule_map:
                rule_map[rule_id] = []
            rule_map[rule_id].append({
                'path': path,
                'count': count
            })
        else:
            print("===============================")

    print('rule count: {}'.format(len(rule_map)))
    count = 0
    json_list = []
    for rule_id, data_list in rule_map.items():
        path_list = [item['path'] for item in data_list]
        path_fire_count_list = ["{} ({})".format(item['path'], item['count']) for item in data_list]

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
                "7_path_str": '\n'.join(path_fire_count_list)
            }
        )

    df = pd.DataFrame(json_list)
    df.to_csv("rule_fire_0704.csv")

    print('Can Move count: {}'.format(count))








