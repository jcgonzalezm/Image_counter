import os

from counter.adapters.count_repo import ObjectCountRepo, CountMongoDBRepo, CountMySQLDBRepo, CountInMemoryRepo
from counter.adapters.object_detector import AIFrameworkDetector, TFSObjectDetector, FakeObjectDetector, ModelScoringOrchestrator, PTObjectDetector
from counter.domain.ports import Enviroment
from counter.domain.models import Models


class DevelopmentEnviroment(Enviroment):
    def define_database_type() -> ObjectCountRepo:
        return CountInMemoryRepo()


    def define_AI_framework() -> AIFrameworkDetector:
        return ModelScoringOrchestrator({Models.OBJECT_IDENTIFIER: FakeObjectDetector()})


class ProductionEnviroment(Enviroment):
    def define_database_type() -> ObjectCountRepo:
        '''
        Define which type of database we will use to send our information to.
        Notes: Based on code structure we are only manaigng 1 database at the time.
        '''
        db_type = os.environ.get('DB_TYPE', 'mysql')
        if db_type == 'mysql':
            mysql_host  = os.environ.get('MYSQL_HOST' , 'root')
            mysql_psw   = os.environ.get('MYSQL_PSW' , 'secret')
            mysql_port  = os.environ.get('MYSQL_PORT' , '3306')
            mysql_db    = os.environ.get('MYSQL_DB', 'prod_counter')        
            return CountMySQLDBRepo(host=mysql_host, password=mysql_psw, port=mysql_port, database=mysql_db)
        
        if db_type == 'mongo':
            mongo_host  = os.environ.get('MONGO_HOST', 'localhost')
            mongo_port  = os.environ.get('MONGO_PORT', 27017)
            mongo_db    = os.environ.get('MONGO_DB', 'prod_counter')
            return CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db)


    def define_AI_framework() -> AIFrameworkDetector:
        '''
        Define which type of AI Framework we will use.
        Notes: Based on usual ML projects structure we are only manaigng 1 framework at the time.
        '''
        AI_framework_type = os.environ.get('AI_FRAMEWORK' , 'torch')
        if AI_framework_type == 'tensor':
            tfs_host    = os.environ.get('TFS_HOST', 'localhost')
            tfs_port    = os.environ.get('TFS_PORT', 8501)        
            return ModelScoringOrchestrator(models = {Models.OBJECT_IDENTIFIER  : TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                                      Models.CAT_BREED          : TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                                      Models.CAT_BREED_COLOR    : TFSObjectDetector(tfs_host, tfs_port, 'rfcn')})  

        if AI_framework_type == 'torch':
            fasterrcnn_host = os.environ.get('FASTERRCNN_HOST', 'localhost')
            fasterrcnn_port = os.environ.get('FASTERRCNN_PORT', 8080)
            return ModelScoringOrchestrator(models = {Models.OBJECT_IDENTIFIER  : PTObjectDetector(fasterrcnn_host, fasterrcnn_port, 'object_count'),
                                                      Models.CAT_BREED          : PTObjectDetector(fasterrcnn_host, fasterrcnn_port, 'object_count')})       