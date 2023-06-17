import requests
from urllib.parse import urlencode
from urllib.parse import quote
import hmac
import hashlib
import base64
import datetime
import json
import os.path


class SmartClient:
    key = b'SeEUKpWHvCbRjFSBwRQpYIgd+sgqBAI4+Jf0JlRQ'
    appId = "5E91C5E6537E7C90059E7E24871A4CE631056377"
    workspaceId = "Top/Auto"

    # host = "bluepen.qa.paypal.com"
    connectResource = "/DecisionServer/decision-services/deployments/connect"
    disconnectResource = "/DecisionServer/decision-services/deployments/disconnect"
    evaluateResource = "/DecisionServer/decision-services/deployments/evaluate"

    def __init__(self, project, decision, credential_file, host='bluepen.qa.paypal.com'):
        self.host = host
        self.hostUri = "http://" + host
        self.credential_file = credential_file
        self.project = project
        self.decision = decision

        self.userId = None
        self.pwd = None

        if os.path.isfile(credential_file):
            with open('credential.json', 'r') as f:
                json_data = f.read()
                credentials = json.loads(json_data)
                self.userId = credentials['username']
                self.pwd = credentials['password']

        self.session_id = None

    # ===================
    # Convenience Methods
    # ===================
    @staticmethod
    def __get_connection_request(operationId, deploymentId, deploymentReleaseId=''):
        return {
            'OperationId': operationId,
            'Header': {
                'DeploymentId': deploymentId,
                'DeploymentReleaseId': deploymentReleaseId
            }
        }

    @staticmethod
    def __get_evaluation_request(operationId, sessionId, decisionId, document):
        return {
            'OperationId': operationId,
            'Header': {
                'SessionId': sessionId,
                'DecisionId': decisionId
            },
            'Body': {
                'Documents': [document]
            }
        }

    @staticmethod
    def __sign_query(method, host, endpointUri, key, qryParameters):
        qryParameters['reqTime'] = datetime.datetime.now().isoformat()
        dataStr = '{method}\n{host}\n{endpoint}\n{encode}'.format(
            method=method,
            host=host,
            endpoint=endpointUri,
            encode=urlencode(sorted(qryParameters.items()),quote_via=quote)
        )
        # print (dataStr)
        data = dataStr.encode()
        digest = hmac.new(key, msg=data, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode()
        qryParameters['sign'] = signature

    @staticmethod
    def __post_request(hostUri, resource, signedParameters):
        r = requests.post(hostUri + resource, data=signedParameters)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        response = r.json()
        # print (response)
        if response['Success'] == False:
            print(response['ErrorInfo']['ErrorCode'], ': ', response['ErrorInfo']['ErrorMessage'], sep='')
            exit()
        return response

    def connect(self):
        reqData = self.__get_connection_request(1, self.project)

        qryParameters = {
            'appId': SmartClient.appId,
            'userId': self.userId,
            'pwd': self.pwd,
            'workspaceId': SmartClient.workspaceId,
            'reqData': json.dumps(reqData)
        }

        SmartClient.__sign_query('POST', self.host, SmartClient.connectResource, SmartClient.key, qryParameters)
        response = SmartClient.__post_request(self.hostUri, SmartClient.connectResource, qryParameters)
        sessionId = response['Header']['SessionId']
        if sessionId is not None:
            self.session_id = sessionId
        print('Connected with session ID:', self.session_id)
        return self.session_id

    def evaluate(self, document, session_id=None):
        if session_id is not None:
            use_session_id = session_id
        else:
            if self.session_id is not None:
                use_session_id = self.session_id
            else:
                use_session_id = self.connect()

        reqData = SmartClient.__get_evaluation_request(2, use_session_id, self.decision, document)
        qryParameters = {
            'appId': SmartClient.appId,
            'session': use_session_id,
            'reqData': json.dumps(reqData)
        }
        SmartClient.__sign_query('POST', self.host, SmartClient.evaluateResource, SmartClient.key, qryParameters)
        response = SmartClient.__post_request(self.hostUri, SmartClient.evaluateResource, qryParameters)
        return response

    def disconnect(self):
        if self.session_id is None:
            print('Session ID is None, no need to disconnect')
            return

        qryParameters = {
            'appId': SmartClient.appId,
            'session': self.session_id
        }

        SmartClient.__sign_query('POST', self.host, SmartClient.disconnectResource, SmartClient.key, qryParameters)
        response = SmartClient.__post_request(self.hostUri, SmartClient.disconnectResource, qryParameters)
        print('Successfully disconnected')
        return response


if __name__ == '__main__':
    project = 'jzhang14 test'
    decision = 'Rule Review Demo'
    credential_file = 'credential.json'
    input_json_file = 'json_data/rule_form.json'
    client = SmartClient(project, decision, credential_file)

    with open(input_json_file) as f:
        json_data = f.read()[1:-1].strip()
    document = json.loads(json_data)

    ret = client.evaluate(document)

    print('===========================================================================')
    print(type(ret))
    print('===========================================================================')
    print(ret)
    print('===========================================================================')
    print(json.dumps(ret))
    print('===========================================================================')
    print('Processed document, Results:', ret['Body']['Documents'][0]['Results'])
    print('===========================================================================')


    client.disconnect()




