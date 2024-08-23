from urllib3.util import Retry, Timeout
from urllib3.poolmanager import PoolManager
import json
import logging
from typing import List, Optional, Dict, Any
from contextlib import closing
from ..models.promptChain import VersionAndRulesWithPromptChainId
from ..models.dataset import DatasetEntry
from ..models.folder import Folder
from ..models.prompt import (Prompt, VersionAndRulesWithPromptId,
                             VersionsAndRules)

class ConnectionPool:
    def __init__(self):
        retries = Retry(connect=5,read=3,redirect=1,status=2,status_forcelist=frozenset({413, 429, 500, 502, 503, 504}))
        self.http = PoolManager(num_pools=2, maxsize=3, retries=retries, timeout=Timeout(connect=10, read=10))
    
    def get_connection(self):
        return self.http

class MaximAPI:
    connection_pool: ConnectionPool

    def __init__(self,base_url: str, api_key: str):
        self.connection_pool = ConnectionPool()
        self.base_url = base_url
        self.api_key = api_key
    
    def __make_network_call(self, method: str, endpoint: str, body: Optional[str] = None) -> bytes:
        headers = {"x-maxim-api-key": self.api_key}
        url = f"{self.base_url}{endpoint}"        
        response = self.connection_pool.get_connection().request(
            method,
            url,
            body=body,
            headers=headers
        )        
        if response.status != 200:
            raise Exception(f"Error: {response.status} - {response.reason}")        
        return response.data

    def getPrompt(self, id: str) -> VersionsAndRules:
        res = self.__make_network_call("GET", f"/api/sdk/v3/prompts?promptId={id}")         
        logging.debug(res.decode())
        return VersionsAndRules(**json.loads(res.decode()))

    def getPrompts(self) -> List[VersionAndRulesWithPromptId]:
        res = self.__make_network_call("GET", "/api/sdk/v3/prompts")
        return [VersionAndRulesWithPromptId.from_dict(data) for data in json.loads(res)['data']]
    
    def getPromptChain(self, id: str) -> VersionAndRulesWithPromptChainId:
        res = self.__make_network_call( "GET", f"/api/sdk/v3/prompt-chains?promptChainId={id}")
        json_response = json.loads(res.decode())
        return VersionAndRulesWithPromptChainId(**json_response['data'])
    
    def getPromptChains(self) -> List[VersionAndRulesWithPromptChainId]:
        res = self.__make_network_call( "GET", "/api/sdk/v3/prompt-chains")
        json_response = json.loads(res.decode())
        return [VersionAndRulesWithPromptChainId(**elem) for elem in json_response['data']]

    def getFolder(self, id: str) -> Folder:
        res = self.__make_network_call("GET", f"/api/sdk/v3/folders?folderId={id}")
        json_response = json.loads(res.decode())
        if 'tags' not in json_response:
            json_response['tags'] = {}
        return Folder(**json_response['data'])

    def getFolders(self) -> List[Folder]:
        res = self.__make_network_call("GET", "/api/sdk/v3/folders")
        json_response = json.loads(res.decode())
        for elem in json_response['data']:
            if 'tags' not in elem:
                elem['tags'] = {}
        return [Folder(**elem) for elem in json_response['data']]

    def addDatasetEntries(self,dataset_id: str, dataset_entries: List[DatasetEntry]) -> dict:
        res = self.__make_network_call("POST", "/api/sdk/v3/datasets/entries", json.dumps({"datasetId": dataset_id, "entries": [entry.to_json() for entry in dataset_entries]}))
        return json.loads(res.decode())

    def doesLogRepositoryExist(self, logger_id: str) -> bool:
        try:
            res = self.__make_network_call("GET", f"/api/sdk/v3/log-repositories?loggerId={logger_id}")
            json_response = json.loads(res.decode())
            if 'error' in json_response:
                return False
            return True
        except Exception as e:
            return False

    def pushLogs(self, repository_id: str, logs: str) -> None:
        try:
            res = self.__make_network_call("POST", f"/api/sdk/v3/log?id={repository_id}", logs)
            json_response = json.loads(res.decode())
            if 'error' in json_response:
                raise Exception(json_response['error'])
        except Exception as e:
            raise Exception(e)