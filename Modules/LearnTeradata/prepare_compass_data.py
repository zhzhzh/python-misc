import teradata
import pandas as pd
import numpy as np
from pandas import DataFrame
import pandas.io.sql as sql
import json
from datetime import datetime, date, timedelta
from time_util import get_server_now


session = None


def get_connection():
    global session
    if session is None:
        udaExec = teradata.UdaExec()
        session = udaExec.connect("Simba")

    return session


def get_data_for_date(date_str):
    query = """
    select 
        name,
        "type",
        "value",
        mavg_7d,
        mdiff_2d,
        mdiff_2d_change,
        mavg_7d_change,
        mavg_7d_change_II,
        mavg_7d_change_rate,
        positive_negative_backlog,
        accu_trend 
    from pp_oap_xinglv1_t.compass_case_monitoring
    where datetime = '{date_str}'
    """.format(date_str=date_str)
    df = sql.read_sql(query, get_connection())
    df['type'] = df['type'].str.replace(r'PROJ:Compass Monitoring\|CAT:', '')
    df.set_index('type', inplace=True)

    if df.empty:
        return None
    else:
        return get_json_data(df, date_str)


# def save_to_excel(file_name, df):
#     writer = pd.ExcelWriter(file_name + '.xlsx')
#     df.to_excel(writer, 'Sheet1')
#     writer.save()


# def save_to_json(file_name, df):
#     file = file_name + '.json'
#     json_data = df.to_json()
#     print(type(json_data))
#     print(json_data)
#     with open(file, 'w') as outfile:
#         outfile.write('[' + df.to_json() + ']')
#         outfile.close()
#         print('close')


def get_json_data(df, date_str):
    backlog = {}
    drivers = []

    cols = df.columns
    for index, item in df.iterrows():
        if index == 'BacklogVol':
            backlog = {k: item[k] for k in cols}
            backlog['date'] = date_str
        else:
            driver = {k: item[k] for k in cols}
            driver['type'] = index
            drivers.append(driver)

    schema = {
        "Backlog": backlog,
        "Drivers": drivers,
        "Outcome": {
            "Alert": False,
            "Type": "NA",
            "Direction": "NA",
            "Reason": "NA",
            "Top_Drivers": [
                {
                    "driver": "NA",
                    "mavg7d_driver_share": 0.0001,
                    "mavg7d_change_rate": 0.0001,
                    "accu_trend": 0.0,
                    "accutrend_driver_share": 0.0001,
                    "accutrend_change_rate": 0.0001,
                    "reason": "NA",
                }
            ]
        }
    }
    # print(schema)
    return schema


def save_json_to_file(file_name, obj):
    file = file_name + '.json'
    with open(file, 'w') as outfile:
        outfile.write(json.dumps(obj))
        outfile.close()
        print('close')


def prepare_schema(date_str):
    data_list = []
    data = get_data_for_date(date_str)
    data_list.append(data)

    file_name = 'compass_backlog_{date}_form'.format(date=date_str)
    save_json_to_file(file_name, [data_list])


def prepare_documents(from_date, to_date):
    dd = from_date
    data_list = []
    while dd <= to_date:
        print(dd)
        data = get_data_for_date(str(dd))
        if data is not None:
            data_list.append(data)

        dd += timedelta(days=1)
    if len(data_list) > 0:
        file_name = 'compass_backlog_{from_date}_{to_date}'.format(from_date=from_date, to_date=to_date)
        save_json_to_file(file_name, data_list)


if __name__ == '__main__':
    now = get_server_now()
    now_date = now.date()

    now_date_str = '2017-07-17'
    prepare_schema(now_date_str)

    date_start = date(year=2017, month=7, day=1)
    date_end = date(year=2017, month=9, day=1)
    prepare_documents(date_start, now_date)

    session.close()
