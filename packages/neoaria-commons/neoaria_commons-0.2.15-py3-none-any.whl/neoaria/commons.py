import redis.asyncio as aioredis
from pydantic import BaseModel, ConfigDict, Field
from pymongo import MongoClient
from confluent_kafka import Consumer, Producer
from typing import Dict, Any, List, Optional
from enum import Enum
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import pysolr, yaml, mysql.connector, threading, requests

communicator = None

# 확장할 고려해 봅니다.
class SearchCondition(BaseModel):
    pass

class SpatialSearchCondition(SearchCondition):
    pass

class MoreLinkThisSearchCondition(SearchCondition):
    pass

class JoinSearchCondition(SearchCondition):
    pass

class FunctionSearchCondition(SearchCondition):
    pass

class LuceneSearchCondition(SearchCondition):
    pass

class StandardSearchCondition(SearchCondition):
    pass

# 추후에 확장할 수 있도록 조치합니다.  Solr 내 검색 엔진별로 파라메터가 다를 수 있으니 참고해 주세요.
class DisMaxSearchCondition(SearchCondition):
    fq: Optional[List[str]] = Field(None, description="Filter query")
    rows: Optional[int] = Field(10, ge=1, le=100, description="Number of results to return")
    start: Optional[int] = Field(0, ge=0, description="Start index for pagination")
    sort: Optional[str] = Field(None, description="Sort order")
    fl: Optional[str] = Field(None, description="Fields to return")
    qf: Optional[List[str]] = Field([], description="Query fields")
    df: Optional[str] = Field('title', description="default query fields")

class EDisMaxSearchCondition(SearchCondition):
    pass

class SolrSearchParams(BaseModel):
    q: Optional[str] = Field('*:*', description="Search query")
    condition: SearchCondition

class Config:
    config_yaml: Any = None

    def __init__(self, config_path: str):
        with open(config_path, 'r') as file:
            self.config_yaml = yaml.safe_load(file)

class DataSourceType(Enum):
    MONGODB = "mongodb"
    MARIADB = "mariadb"
    KAFKA = "kafka"
    SOLR = "solr"
    REDIS = "redis"

class DataSource:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_id = config['id']

class MongoDataSource(DataSource):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_type = DataSourceType.MONGODB
        self.source_client = MongoClient(config['uri'])
        self.source_db = self.source_client[config['database']]
        self.source_collection = self.source_db[config['collection']]

class MariaDBDataSource(DataSource):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_type = DataSourceType.MARIADB
        self.source_client = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        self.source_db = self.source_client

class KafkaDataSource(DataSource):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_type = DataSourceType.KAFKA

class SolrDataSource(DataSource):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_type = DataSourceType.SOLR
        self.source_client = pysolr.Solr(config['url'], always_commit=True)

class RedisDataSource(DataSource):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_type = DataSourceType.REDIS
        self.source_client = aioredis.from_url(config['url'], decode_responses=True)

class DataSourceFactory:
    @staticmethod
    def create_data_source(source_type: DataSourceType, config: Dict[str, Any]) -> DataSource:
        if source_type == DataSourceType.MONGODB:
            return MongoDataSource(config)
        elif source_type == DataSourceType.MARIADB:
            return MariaDBDataSource(config)
        elif source_type == DataSourceType.KAFKA:
            return KafkaDataSource(config)
        elif source_type == DataSourceType.SOLR:
            return SolrDataSource(config)
        elif source_type == DataSourceType.REDIS:
            return RedisDataSource(config)

class BusinessSession(BaseModel):
    id: str

class BusinessParameter(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    body: Dict[str, Any] = {}
    change: Dict[str, Any] = {}

class BusinessResponse(BaseModel):

    body: Dict[str, Any]

    def __getattr__(self, key):
        if key in self.body:
            return self.body[key]
        else:
            raise AttributeError(f"'{self.body.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        if key == 'body':
            super().__setattr__(key, value)
        else:
            self.body[key] = value

class business:
    @classmethod
    def permission(cls,
        default: dict = {'administrator': True,'manager': True,'operator': False, 'viewer': False,}, 
        custom: dict=None):
        
        def decorator(func):
            if not hasattr(func, '__permission_default__'):
                func.__annotations_default__ = {}
            func.__annotations_default__.update(default)

            if custom or not hasattr(func, '__permission_custom__'):
                func.__annotations_custom__ = {}
            func.__annotations_custom__.update(custom)

            return func
        
        return decorator

class CommonBusiness:

    sessions:BusinessSession = []

    def create(self, data: BusinessParameter):
        raise NotImplementedError

    def detail(self, data: BusinessParameter):
        raise NotImplementedError

    def update(self, data: BusinessParameter):
        raise NotImplementedError

    def delete(self, data: BusinessParameter):
        raise NotImplementedError

    def producer_flush(self):
        self.producer.flush()

    def producer_send_message(self, topic_index: int, message: str, call_back):
        self.producer.produce(
            self.producer_config['topics'][topic_index], 
            message.encode('utf-8'), callback=call_back)
        self.producer_flush()

    def __consumer_poll_messages(self, consumer: Consumer):
        try:
            while True:
                message = consumer.poll(timeout=1.0)
                if message is None:
                    continue
                if message.error():
                    self.consumer_receive_error(message)
                else:
                    self.consumer_receive(message)
        except Exception as e:
            pass
        finally:
            consumer.close()

    def consumer_receive_error(self, message):
        raise NotImplementedError

    def consumer_receive(self, message):    
        raise NotImplementedError

    def setupSolr(self, solr_datasource: SolrDataSource):
        self.solr = solr_datasource.source_client

    def solr_add(self, dict_data: dict):
        self.solr.add([dict_data])

    def solr_read(self, query: str):
        return self.solr.search(query)
    
    def solr_update(self, dict_data: dict):
        self.solr.add([dict_data])

    def solr_delete(self, query: str):
        self.solr.delete(q=query)
        self.solr.commit()
        self.solr.optimize()
    
    def solr_commit(self):
        self.solr.commit()

    def setupDataSource(self, config: dict):
    
        self.__load_config_yaml__()
        config_data = config['data']
        config_event = config['event']
        config_search = config['search']

        # setup mongodb data source
        self.config_yaml[config_data]['type']

        # setup mongodb data source
        self.source_data = self.__mongodb_data_source_config__(config_data)
        self.source_kafka = self.__kafka_data_source_config__(config_event)
        self.source_solr = self.__solr_data_source_config__(config_search)

    async def setWebsocket(self, websocket: WebSocket, websocket_process):
        self.websocket = websocket
        self.websocket_process = websocket_process

        await websocket.accept()

        try:
            while True:
                receive_data = await websocket.receive_text()
                await websocket_process(True, websocket, receive_data)
        except WebSocketDisconnect:
            await websocket_process(False, "WebSocket connection closed")

    def getDataSource(self):
        return self.source_data
    
    def getEventSource(self):
        return self.source_kafka
    
    def getSearchSource(self):
        return self.source_solr

    def __load_config_yaml__(self):
        with open('config/source.yaml', 'r') as file:
            self.config_yaml = yaml.safe_load(file)

    def __mongodb_data_source_config__(self, section_name:str) -> MongoDataSource:

        # setup mongodb data source
        data_section = self.config_yaml[section_name]['data']

        mongo_datasource_config = {}
        mongo_datasource_config['id'] = data_section['id']
        mongo_datasource_config['uri'] = data_section['uri']
        mongo_datasource_config['database'] = data_section['database']
        mongo_datasource_config['collection'] = data_section['collection']

        return MongoDataSource(mongo_datasource_config)
    
    def __kafka_data_source_config__(self, section_name:str) -> KafkaDataSource:

        # setup kafka data source
        data_section = self.config_yaml[section_name]['data']

        kafka_datasource_config = {}
        kafka_datasource_config['id'] = data_section['id']

        self.consumer_config = data_section['consumer']
        self.producer_config = data_section['producer']

        self.consumer = Consumer(data_section['consumer']['settings'])
        self.consumer.subscribe(data_section['consumer']['topics'])
        threading.Thread(target=self.__consumer_poll_messages, args=[self.consumer,]).start()

        # Kafka Producer
        self.producer = Producer(data_section['producer']['settings'])

        return KafkaDataSource(kafka_datasource_config)
    
    def __solr_data_source_config__(self, section_name:str) -> SolrDataSource:

        # setup solr data source
        data_section = self.config_yaml[section_name]['data']

        solr_datasource_config = {}
        solr_datasource_config['id'] = data_section['id']
        solr_datasource_config['url'] = data_section['url']

        return SolrDataSource(solr_datasource_config)

    def __transfer_common_attributes__(self, source_dict, target_dict):
        for key, value in source_dict.items():
            if key in target_dict:
                if isinstance(value, dict) and isinstance(target_dict[key], dict):
                    self.__transfer_common_attributes__(value, target_dict[key])
                else:
                    target_dict[key] = value

class CommunicatorStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"

class CommunicatorResult(BaseModel):
    status: str
    body: dict

class Communicator:

    def __init__(self, config:dict) -> None:
        self.config = config

    def invoke(self, business: CommonBusiness, data:dict) -> CommunicatorResult:
        global communicator

        if data['id'] in self.config:

            #TODO setup target service properties
            target_service = self.config[data['id']]
            target_service_info = self.config['services'][target_service['service']]
            target_service_host = target_service_info['host']
            target_service_port = target_service_info['port']
            target_service_path = target_service['api']
            target_service_method = target_service['method'].lower()
            target_service_data = data['body']

            if target_service_method == 'get' or 'delete':
                return_value = getattr(requests, target_service_method)(f"http://{target_service_host}:{target_service_port}/{target_service_path}")
            elif target_service_method == 'post' or 'put':
                return_value = getattr(requests, target_service_method)(f"http://{target_service_host}:{target_service_port}/{target_service_path}", json=target_service_data)

            return CommunicatorResult(status=CommunicatorStatus.SUCCESS.value, body={'message': 'success', 'body': return_value.json()})
        
        else:
            return CommunicatorResult(status=CommunicatorStatus.ERROR.value, body={"message": "id is not found"})

def build_router(business:CommonBusiness, prefix:str) -> APIRouter:
    
    methods = [getattr(business, method_name) for method_name in dir(business) if callable(getattr(business, method_name))]
    
    business_permissions = {
        'name': business.__class__.__qualname__,
        'methods': [],
    }

    for method in methods:

        method_desc = {
            'name': method.__qualname__,
            'default_permissions': {},
            'custom_permissions': {},
        }

        method_desc['default_permissions'] = getattr(method, '__permission_default__', {})
        method_desc['custom_permissions'] = getattr(method, '__permission_custom__', {})
        business_permissions['methods'].append(method_desc)

    #@TODO communication for permission check~!

    # setup router wtih default prefix
    return APIRouter(prefix=prefix)


def init_communicator(file_path: str):
    global communicator
    with open(file_path, 'r') as file:
        communicator = Communicator(yaml.safe_load(file))

init_communicator('config/communicator.yaml')