from ast import expr_context
from typing import List

from pymongo import MongoClient
from mysql import connector

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo

from datetime import datetime
from functools import wraps

class CountInMemoryRepo(ObjectCountRepo):
    def __init__(self):
        self.store = dict()


    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())
        return [self.store.get(object_class) for object_class in object_classes]


    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):
    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database


    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col


    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts


    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


class CountMySQLDBRepo(ObjectCountRepo):
    def __init__(self, host, password, port, database):
        self.__host = host
        self.__port = port
        self.__password = password
        self.__database = database
        self.__cnx = None
        self.__cursor = None


    def _stablish_connection(self):
        open_connection_succesfull = True
        try:
            self.__cnx = connector.connect(user=self.__host, password=self.__password, database=self.__database)
            self.__cursor = self.__cnx.cursor()
        except Exception as err:
            #print // log err
            open_connection_succesfull = False
        return open_connection_succesfull


    def _close_connection(self):
        close_connection_succesfull = True
        try:
            self.__cursor.close()
            self.__cnx.close()
        except Exception as err:
            #print // log err
            close_connection_succesfull = False              
        return close_connection_succesfull    


    def manage_mysql_connection(target_func):
        @wraps(target_func)
        def managing_connection(*args, **kwargs):
            args[0]._stablish_connection()
            try:
                return target_func(*args, **kwargs)
            finally:
                args[0]._close_connection()
        return managing_connection             
             

    @manage_mysql_connection
    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        table_name = self.__database #TODO
        sql_query = (f"SELECT object_class, COUNT(object_class) FROM {table_name} GROUP BY object_class;") #same as mongo db the name of the db->tag its the same as the db->table
        self.__cursor.execute(sql_query)
        counters = self.__cursor.fetchall()

        object_counts = []
        for counter in counters:
            #position based indexing due to code standars
            object_counts.append(ObjectCount(counter[0], counter[1]))
        return object_counts


    def define_values_to_update(self, new_values: List[ObjectCount]):
        '''Create and define the new_values to be used on the subsequent update query'''
        image_timestamp = datetime.timestamp(datetime.now())
        values_to_insert = ""
        for value in new_values:
            for _ in range(0,value.count): #loop over how many of the same obj where found
                values_to_insert = values_to_insert + f"('{value.object_class}','{image_timestamp}') ," 
        
        values_to_insert = values_to_insert[:-1] #to remove last ','
        return values_to_insert


    @manage_mysql_connection
    def update_values(self, new_values: List[ObjectCount]):
        '''
        As we may identify several objects in the same picture we will create a new row for each obj identified \
        in the same image. 

        Example:
        If we find: [ObjectCount(object_class='cat', count=2)]
        
        The SQL command will be:
            INSERT INTO prod_counter(object_class, image)
            VALUES ('cat','image01'), ('cat','image01');
        '''
        table_name = self.__database #TODO
        sql_query_updated_values = self.define_values_to_update(new_values)
        sql_query = (f"INSERT INTO {table_name} (object_class , image) VALUES {sql_query_updated_values};")
        self.__cursor.execute(sql_query)
        self.__cnx.commit()