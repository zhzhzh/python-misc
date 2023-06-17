# from smarts_client import SmartClient
from prepare_compass_data import get_data_for_date
import json
from pprint import pprint

if __name__ == '__main__':
    date_str = '2017-07-17'
    data = get_data_for_date(date_str)
    print(data)

    project = 'Compass Backlog'
    decision = 'compass backlog decision'
    credential_file = 'credential.json'

    # client = SmartClient(project, decision, credential_file)
    #
    # rep = client.evaluate(data)
    # print('=========================================')
    # pprint(rep)
    # print('-----------------------------------------')
    # if rep['Success']:
    #     print("Get the result Successfully")
    #     pprint(rep['Body']['Documents'][0]['Outcome'])
    # print('=========================================')

    # client.disconnect()

