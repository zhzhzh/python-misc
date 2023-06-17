import requests
import sys

url = 'https://paypaltest.service-now.com/api/payp2/table/change_request'
username = 'api_risk_rom'
password = 'Riskrom@2016'

headers = {'Content-Type': 'application/json'}

payload = {
    "short_description": "Enable Pluto Rules",
    "description": "Enable Pluto Rule 205816  in admin per request from Zhang, Suning",
    "u_service_category": "PP-ROM",
    "u_category_type": "Code Push",
    "u_category_subtype": "Risk Rules",
    "u_deployment_category": "Config",
    "u_atb_cust_impact": "0",
    "u_impacted_site": "PayPal",
    "u_environment": "Production",
    "assignment_group": "ROM",
    "assigned_to": "api_risk_rom",
    "requested_by": "api_risk_rom",
    "u_modified_by": "api_risk_rom",
    "implementation_plan": "Enable rule 205816 in PayPal Admin site",
    "u_site_components": "riskauthenticationserv",
    "test_plan": "Monitor in Rule360",
    "backout_plan": "Disable rule in Admin again",
    "justification": "risk mitigation, customer experience",
    "u_site_impact": "No impact",
    "risk": "Low",
    "start_date": "2017-01-26 00:55:00",
    "u_duration": "60",
    "u_availability_zone": "SLCA",
    "priority": "4 - Low",
    "u_generate_az_tasks": "false",
    "u_change_environment": "None of the listed environments",
    "type": "Standard",
    "state": "closed"
}

ret = requests.post(url, headers=headers, auth=(username, password), json=payload)
print(url)
print(payload)
if ret.status_code != 201:
    print(ret.status_code)
    print(ret.json())
    sys.exit(1)

json_data = ret.json()
sys_id = json_data['result']['sys_id']
number = json_data['result']['record_id']


url = 'https://paypaltest.service-now.com/api/payp2/table/change_request/{}'.format(sys_id)
print(url)
ret = requests.get(url, auth=(username, password))
if ret.status_code != 200:
    print(ret.status_code)
    print(ret.json())
else:
    print(ret.json())

url = 'https://paypaltest.service-now.com/api/payp2/table/change_request/number/{}'.format(number)
print(url)
ret = requests.get(url, auth=(username, password))
if ret.status_code != 200:
    print(ret.status_code)
    print(ret.json())
else:
    print(ret.json())



