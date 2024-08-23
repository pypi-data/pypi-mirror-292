import json
import logging
import threading
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Union

from .models.promptChain import PromptChain, PromptChainVersion, PromptChainVersionsAndRules, VersionAndRulesWithPromptChainIdEncoder, PromptChainRuleGroupType

from .apis.maxim import MaximAPI
from .cache.cache import MaximCache
from .cache.inMemory import MaximInMemoryCache
from .filterObjects import (IncomingQuery, QueryObject, findAllMatches,
                            findBestMatch, parseIncomingQuery)
from .logger.logger import Logger, LoggerConfig
from .models.dataset import DatasetEntry
from .models.folder import Folder, FolderEncoder
from .models.prompt import (Prompt, PromptData, PromptVersion, RuleGroupType,
                            RuleType, VersionAndRulesWithPromptIdEncoder,
                            VersionsAndRules, VersionSpecificDeploymentConfig)
from .models.queryBuilder import QueryRule

maximLogger = logging.getLogger("MaximSDK")

@dataclass
class Config():
    apiKey: str
    baseUrl: Optional[str] = None
    cache: Optional[MaximCache] = None
    debug: Optional[bool] = False


EntityType = {
    "PROMPT": "PROMPT",
    "FOLDER": "FOLDER",
    "PROMPT_CHAIN": "PROMPT_CHAIN"
}


class Maxim:
    def __init__(self, config: Config):
        maximLogger.setLevel(logging.DEBUG if config.debug else logging.INFO)
        self.baseUrl = config.baseUrl or "https://app.getmaxim.ai"
        self.apiKey = config.apiKey
        self.is_running = True
        self.maxim_api = MaximAPI(self.baseUrl, self.apiKey)
        self.mutex = threading.Lock()
        self.__is_debug = config.debug or False
        self.__cache = config.cache or MaximInMemoryCache()
        self.__loggers: Dict[str, Logger] = {}
        self.__sync_thread = threading.Timer(60, self.__syncEntities)
        self.__sync_thread.start()
        self.__syncPrompts()
        self.__syncFolders()

    def __syncEntities(self):
        maximLogger.debug(" Syncing prompts and folders")
        if not self.is_running:
            return
        with self.mutex:
            self.__sync_thread = threading.Timer(60, self.__syncEntities)
            self.__sync_thread.start()
            self.__syncPrompts()
            self.__syncFolders()
            maximLogger.debug("Syncing completed")

    def __syncPrompts(self):
        maximLogger.debug("Syncing prompts")
        try:
            prompts = self.maxim_api.getPrompts()
            maximLogger.debug(f"Found {len(prompts)} prompts")
            for prompt in prompts:
                try:
                    self.__cache.set(self.__getCacheKey(
                        EntityType['PROMPT'], prompt.promptId), json.dumps(prompt, cls=VersionAndRulesWithPromptIdEncoder))
                except Exception as err:
                    maximLogger.error(err)
        except Exception as err:
            maximLogger.error(f"Error while syncing prompts: {err}")

    def __syncPromptChains(self):
        maximLogger.debug("Syncing prompt Chains")
        try:
            promptChains = self.maxim_api.getPromptChains()
            maximLogger.debug(f"Found {len(promptChains)} prompt chains")
            for promptChain in promptChains:
                try:
                    self.__cache.set(self.__getCacheKey(
                        EntityType['PROMPT_CHAIN'], promptChain.promptChainId), json.dumps(promptChain, cls=VersionAndRulesWithPromptChainIdEncoder))
                except Exception as err:
                    maximLogger.error(err)
        except Exception as err:
            maximLogger.error(f"Error while syncing prompts: {err}")

    def __syncFolders(self):
        maximLogger.debug("Syncing folders")
        try:
            folders = self.maxim_api.getFolders()
            maximLogger.debug(f"Found {len(folders)} folders")
            for folder in folders:
                try:
                    self.__cache.set(self.__getCacheKey(
                        EntityType['FOLDER'], folder.id), json.dumps(folder, cls=FolderEncoder))
                except Exception as err:
                    maximLogger.error(err)
        except Exception as err:
            maximLogger.error(f"Error while syncing folders: {err}")

    def __getCacheKey(self, entity: str, id: str) -> str:
        if entity == 'PROMPT':
            return f"prompt:{id}"
        else:
            return f"folder:{id}"

    def __getPromptFromCache(self, key: str) -> Optional[VersionsAndRules]:
        data = self.__cache.get(key)
        if not data:
            return None
        json_data = json.loads(data)
        if 'promptId' in json_data:
            json_data.pop('promptId')
        return VersionsAndRules.from_dict(json_data)

    def __getAllPromptsFromCache(self) -> Optional[List[VersionsAndRules]]:
        keys = self.__cache.getAllKeys()
        if not keys:
            return None
        data = [self.__cache.get(key)
                for key in keys if key.startswith("prompt:")]
        promptList = []
        for d in data:
            if d is not None:
                json_data = json.loads(d)
                if 'promptId' in json_data:
                    json_data.pop('promptId')
                promptList.append(VersionsAndRules.from_dict(json_data))
        return promptList
    
    def __getPromptChainFromCache(self, key: str) -> Optional[PromptChainVersionsAndRules]:
        data = self.__cache.get(key)
        if not data:
            return None

        parsed_data = json.loads(data)
        return PromptChainVersionsAndRules.from_dict(parsed_data)
    
    def __getAllPromptChainsFromCache(self) -> Optional[List[PromptChainVersionsAndRules]]:
        keys = self.__cache.getAllKeys()
        if not keys:
            return None
        data = [self.__cache.get(key)
                for key in keys if key.startswith("prompt_chain:")]
        promptChainList = []
        for d in data:
            if d is not None:
                json_data = json.loads(d)
                if 'promptChainId' in json_data:
                    json_data.pop('promptChainId')
                promptChainList.append(PromptChainVersionsAndRules.from_dict(json_data))
        return promptChainList


    def __getFolderFromCache(self, key: str) -> Optional[Folder]:
        data = self.__cache.get(key)
        if not data:
            return None
        json_data = json.loads(data)
        return Folder(**json_data)

    def __getAllFoldersFromCache(self) -> Optional[List[Folder]]:
        keys = self.__cache.getAllKeys()
        if not keys:
            return None
        data = [self.__cache.get(key)
                for key in keys if key.startswith("folder:")]
        return [Folder(**json.loads(d)) for d in data if d is not None]

    def __formatPrompt(self, prompt: PromptVersion) -> Prompt:
        json_data = {
            'promptId': prompt.promptId,
            'version': prompt.version,
            'versionId': prompt.id,
            'messages': prompt.config.messages if prompt.config else None,
            'modelParameters': prompt.config.modelParameters if prompt.config else None
        }
        return Prompt(**json_data)

    def __formatPromptChain(self, promptChainVersion: PromptChainVersion) -> PromptChain:
        json_data = {
            'promptChainId': promptChainVersion.promptChainId,
            'versionId': promptChainVersion.id,
            'versionId': promptChainVersion.version,
            'nodes': [n for n in promptChainVersion.config.nodes if hasattr(n, 'prompt') or (isinstance(n, dict) and 'prompt' in n)] if promptChainVersion.config else []
        }
        return PromptChain(**json_data)

    def __getPromptVersionForRule(self, promptVersionAndRules: VersionsAndRules, rule: Optional[QueryRule] = None) -> Optional[Prompt]:
        if rule:
            incomingQuery = IncomingQuery(
                query=rule.query, operator=rule.operator, exactMatch=rule.exactMatch)
            objects = []
            for versionId, versionRules in promptVersionAndRules.rules.items():
                for versionRule in versionRules:
                    if not versionRule.rules.query:
                        continue
                    if rule.scopes:
                        for key in rule.scopes.keys():
                            if key != "folder":
                                raise ValueError("Invalid scope added")
                    version = next(
                        (v for v in promptVersionAndRules.versions if v.id == versionId), None)
                    if not version:
                        continue
                    query = versionRule.rules.query
                    if version.config and version.config.tags:
                        parsedIncomingQuery = parseIncomingQuery(
                            incomingQuery.query)
                        tags = version.config.tags
                        for key, value in tags.items():
                            if value == None:
                                continue
                            if parsedIncomingQuery is None:
                                continue
                            incomingQueryFields = [
                                q.field for q in parsedIncomingQuery]
                            if key in incomingQueryFields:
                                query.rules.append(
                                    RuleType(field=key, operator='=', value=value))
                    objects.append(QueryObject(query=query, id=versionId))

            deployedVersionObject = findBestMatch(objects, incomingQuery)
            if deployedVersionObject:
                deployedVersion = next(
                    (v for v in promptVersionAndRules.versions if v.id == deployedVersionObject.id), None)
                if deployedVersion:
                    return self.__formatPrompt(deployedVersion)

        else:
            if promptVersionAndRules.rules:
                for versionId, versionRules in promptVersionAndRules.rules.items():
                    logging.debug(f"type: {type(versionRules[0].rules)}")
                    doesQueryExist = any(
                        ruleElm.rules.query != None for ruleElm in versionRules)
                    if doesQueryExist:
                        deployedVersion = next(
                            (v for v in promptVersionAndRules.versions if v.id == versionId), None)
                        if deployedVersion:
                            return self.__formatPrompt(deployedVersion)
            else:
                return self.__formatPrompt(promptVersionAndRules.versions[0])

        if promptVersionAndRules.fallbackVersion:
            maximLogger.info(
                f"************* FALLBACK TRIGGERED : VERSION : {promptVersionAndRules.fallbackVersion} *************")
            return self.__formatPrompt(promptVersionAndRules.fallbackVersion)
        return None

    def __getPromptChainVersionForRule(self, promptChainVersionsAndRules: PromptChainVersionsAndRules, rule: Optional[QueryRule] = None) -> Optional[PromptChain]:
        if rule:
            incomingQuery = IncomingQuery(
                query=rule.query, operator=rule.operator, exactMatch=rule.exactMatch)
            objects = []
            for versionId, versionRules in promptChainVersionsAndRules.rules.items():
                for versionRule in versionRules:
                    if not versionRule.rules.query:
                        continue
                    if rule.scopes:
                        for key in rule.scopes.keys():
                            if key != "folder":
                                raise ValueError("Invalid scope added")
                    version = next(
                        (v for v in promptChainVersionsAndRules.versions if v.id == versionId), None)
                    if not version:
                        continue

                    # query_data = versionRule.rules.query.__dict__

                    #tempfix
                    query = RuleGroupType(**versionRule.rules.query.__dict__)
                    objects.append(QueryObject(query=query, id=versionId))

            deployedVersionObject = findBestMatch(objects, incomingQuery)
            if deployedVersionObject:
                deployedVersion = next(
                    (v for v in promptChainVersionsAndRules.versions if v.id == deployedVersionObject.id), None)
                if deployedVersion:
                    return self.__formatPromptChain(deployedVersion)

        else:
            if promptChainVersionsAndRules.rules:
                for versionId, versionRules in promptChainVersionsAndRules.rules.items():
                    logging.debug(f"type: {type(versionRules[0].rules)}")
                    doesQueryExist = any(
                        ruleElm.rules.query != None for ruleElm in versionRules)
                    if doesQueryExist:
                        deployedVersion = next(
                            (v for v in promptChainVersionsAndRules.versions if v.id == versionId), None)
                        if deployedVersion:
                            return self.__formatPromptChain(deployedVersion)
            else:
                return self.__formatPromptChain(promptChainVersionsAndRules.versions[0])

        if promptChainVersionsAndRules.fallbackVersion:
            maximLogger.info(
                f"************* FALLBACK TRIGGERED : VERSION : {promptChainVersionsAndRules.fallbackVersion} *************")
            return self.__formatPromptChain(promptChainVersionsAndRules.fallbackVersion)
        return None

    def __getFoldersForRule(self, folders: List[Folder], rule: QueryRule) -> List[Folder]:
        incomingQuery = IncomingQuery(
            query=rule.query, operator=rule.operator, exactMatch=rule.exactMatch)
        objects = []
        for folder in folders:
            query = RuleGroupType(rules=[], combinator='AND')
            if not folder.tags:
                continue
            parsedIncomingQuery = parseIncomingQuery(incomingQuery.query)
            tags = folder.tags
            for key, value in tags.items():
                if key in [q.field for q in parsedIncomingQuery]:
                    # if not isinstance(value,None):
                    query.rules.append(
                        RuleType(field=key, operator='=', value=value))
            if not query.rules:
                continue
            objects.append(QueryObject(query=query, id=folder.id))

        folderObjects = findAllMatches(objects, incomingQuery)
        ids = [fo.id for fo in folderObjects]
        return [f for f in folders if f.id in ids]

    def getPrompt(self, id: str, rule: QueryRule) -> Optional[Prompt]:
        maximLogger.debug(f"getPrompt: id: {id} for rule: {rule}")
        key = self.__getCacheKey('PROMPT', id)
        versionAndRules = self.__getPromptFromCache(key)
        if versionAndRules is None:
            versionAndRules = self.maxim_api.getPrompt(id)
            if len(versionAndRules.versions) == 0:
                return None
            self.__cache.set(id, json.dumps(versionAndRules))
        if not versionAndRules:
            return None
        prompt = self.__getPromptVersionForRule(versionAndRules, rule)
        if not prompt:
            return None
        return prompt

    def getPrompts(self, rule: QueryRule) -> List[Prompt]:
        versionAndRules = self.__getAllPromptsFromCache()
        prompts = []
        if versionAndRules is None or len(versionAndRules) == 0:
            self.__syncEntities()
            versionAndRules = self.__getAllPromptsFromCache()
        if not versionAndRules:
            return []
        for v in versionAndRules:
            if rule.scopes:
                if 'folder' not in rule.scopes.keys():
                    return []
                else:
                    if rule.scopes['folder'] != v.folderId:
                        continue
            prompt = self.__getPromptVersionForRule(v, rule)
            if prompt != None:
                prompts.append(prompt)
        if len(prompts) == 0:
            return []
        return prompts

    def getPromptChain(self, id: str, rule: QueryRule) -> Optional[PromptChain]:
        key = self.__getCacheKey('PROMPT_CHAIN', id)
        versionAndRules = self.__getPromptChainFromCache(key)
        if versionAndRules is None:
            versionAndRules = self.maxim_api.getPromptChain(id)
            if len(versionAndRules.versions) == 0:
                return None
            self.__cache.set(id, json.dumps(versionAndRules))
        if not versionAndRules:
            return None
        promptChains = self.__getPromptChainVersionForRule(versionAndRules, rule)
        if not promptChains:
            return None
        return promptChains

    def getFolderById(self, id: str) -> Optional[Folder]:
        key = self.__getCacheKey('FOLDER', id)
        folder = self.__getFolderFromCache(key)
        if folder is None:
            try:
                folder = self.maxim_api.getFolder(id)
                if not folder:
                    return None
                self.__cache.set(key, json.dumps(folder))
            except Exception as e:
                return None
        return folder

    def getFolders(self, rule: QueryRule) -> List[Folder]:
        folders = self.__getAllFoldersFromCache()
        if folders is None or len(folders) == 0:
            self.__syncEntities()
            folders = self.__getAllFoldersFromCache()
        if not folders:
            return []
        return self.__getFoldersForRule(folders, rule)

    def logger(self, config: LoggerConfig):
        # Checking if this log repository exist on server
        exists = self.maxim_api.doesLogRepositoryExist(config.id)
        if not exists:
            if config.id:
                raise Exception("Log repository not found")
        if config.id in self.__loggers:
            return self.__loggers[config.id]
        logger = Logger(config=config, api_key=self.apiKey,
                        base_url=self.baseUrl, is_debug=self.__is_debug)
        self.__loggers[config.id] = logger
        return logger

    def cleanup(self):
        self.is_running = False
        self.__sync_thread.cancel()
        # Cleaning up all loggers
        for logger in self.__loggers.values():
            logger.cleanup()