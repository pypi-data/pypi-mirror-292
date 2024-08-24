import requests
from web3 import Web3
from decimal import Decimal
from w3ai_sdk.const import *

class W3AIClient:
    def __init__(self, apiKey: str, endpoint = None):
        self.apiKey = apiKey
        if endpoint == None :
            self.endpoint = DEFAULT_SERVER_ENDPOINT
        else:
            self.endpoint = endpoint
        self.headers = {
            'accept': 'application/json',
            'x-api-key': self.apiKey,
            'Content-Type': 'application/json'
        }

    def makeRequest(self, routing, method, payload, apiKey):
        url = f"{self.endpoint}{routing}"
        response = requests.Response()
        try:
            if method==GET_METHOD:
                response = requests.get(url, headers=self.headers, verify=False)
            elif method == POST_METHOD:
                response = requests.post(url,json=payload, headers=self.headers, verify=False)
            response.raise_for_status()  # Raises an HTTPError if the status is 4xx or 5xx
            if response.status_code == STATUS_CODE :
                rawResponse = response.json()
                rawResponse[STATUS_RESPONSE_KEY] = SUCCESS_RESPONSE_VALUE
                return rawResponse
            else:
                rawResponse = response.json()
                rawResponse[STATUS_RESPONSE_KEY] = FAILED_RESPONSE_VALUE
                return rawResponse
        except requests.exceptions.RequestException as err:
            errorMessage ={STATUS_RESPONSE_KEY: ERROR_RESPONSE_VALUE, MESSAGE_RESPONSE_KEY : str(err)}
            return errorMessage

    def getBalance(self):
        def converToUsd(balanceJson, debtJson,freeBalanceJson,priceJson):
            aiozBalance = Web3.from_wei(Decimal(balanceJson),'ether') 
            aiozDebt = Web3.from_wei(Decimal(debtJson),'ether') 
            aiozFreeBalance = Web3.from_wei(Decimal(freeBalanceJson),'ether') 
            return float(aiozBalance+aiozDebt+aiozFreeBalance)*priceJson
        
        routing=f"api/v1/api-key/balance"
        priceRouting=f"api/v1/public/token/price"
        balanceResult = self.makeRequest(routing,GET_METHOD,None, self.apiKey)
        aiozPriceResult = self.makeRequest(priceRouting,GET_METHOD, None, self.apiKey)
        if balanceResult[STATUS_RESPONSE_KEY] ==SUCCESS_RESPONSE_VALUE and aiozPriceResult[STATUS_RESPONSE_KEY]== SUCCESS_RESPONSE_VALUE:
            usdBalance = converToUsd(balanceResult['data']['balance'],balanceResult['data']['debt'], balanceResult['data']['free_balance'], aiozPriceResult['data']['current_price'])
            originbalanceResult = balanceResult
            originbalanceResult['data']['usd_balance'] = str(usdBalance)
            return originbalanceResult
        else :
            if balanceResult[STATUS_RESPONSE_KEY] ==FAILED_RESPONSE_VALUE :
                return balanceResult
            elif aiozPriceResult[STATUS_RESPONSE_KEY] ==FAILED_RESPONSE_VALUE:
                return aiozPriceResult
            elif aiozPriceResult[STATUS_RESPONSE_KEY] ==ERROR_RESPONSE_VALUE:
                return aiozPriceResult[MESSAGE_RESPONSE_KEY]
            elif balanceResult[STATUS_RESPONSE_KEY] ==ERROR_RESPONSE_VALUE:
                return balanceResult[MESSAGE_RESPONSE_KEY]
            else :
                return "Unknow error"

    def apiKeyGetModelInfo(self, modelId:str):
        routing=f"api/v1/api-key/balance"
        res = self.makeRequest(routing,GET_METHOD, None, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def apiKeyGetModelServings(self, modelId:str):
        routing=f"api/v1/api-key/model/{modelId}/serving"
        res = self.makeRequest(routing,GET_METHOD, None, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def apiKeyGetModelStatistic(self, modelId:str, dateFrom:str, dateTo:str):
        routing=f"api/v1/api-key/model/{modelId}/statistics"
        data = {
            'from': dateFrom,
            'to': dateTo
        }
        res = self.makeRequest(routing,POST_METHOD, data, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def apiKeyGetModelCost(self, modelId:str):
        routing=f"api/v1/api-key/model/{modelId}/task/cost"
        res = self.makeRequest(routing,GET_METHOD, None, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def checkApiKeyPermission(self,apiKeyTarget:str):
        routing=f"api/v1/api-key/permission"
        res = self.makeRequest(routing,GET_METHOD, None, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def getModelStatistics(self, dateFrom:str, dateTo:str):
        routing=f"api/v1/api-key/statistics"
        data = {
            'from': dateFrom,
            'to': dateTo
        }
        res = self.makeRequest(routing,POST_METHOD, data, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def getTaskHistory(self, limit:str, offset:str):
        routing=f"api/v1/api-key/task/histories?limit={limit}&offset={offset}"
        res = self.makeRequest(routing,GET_METHOD, None, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def getTaskResult(self, taskId:str):
        routing=f"api/v1/api-key/task/{taskId}/result"
        res = self.makeRequest(routing,GET_METHOD, None, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res

    def createTask(self,fileList:list,inputParam:dict, modelId:str):
        data = {
            'files': fileList,
            'input_params': inputParam,
            'model_id': modelId
        }
        routing=f"api/v1/api-key/task"
        res = self.makeRequest(routing,POST_METHOD, data, self.apiKey)
        if res[STATUS_RESPONSE_KEY] == ERROR_RESPONSE_VALUE :
            return res[MESSAGE_RESPONSE_KEY]
        else:
            return res