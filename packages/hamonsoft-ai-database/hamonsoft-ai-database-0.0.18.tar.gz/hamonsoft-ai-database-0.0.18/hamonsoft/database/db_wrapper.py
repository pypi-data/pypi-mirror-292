from abc import ABCMeta, abstractmethod


class DBWrapper(metaclass=ABCMeta):
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.database = None
        self.port = None

        self.connection = None
        self.cursor = None
        self.bindValue = {}

    def __del__(self):
        pass

    @abstractmethod
    def connect(self, *args, **kwargs):
        pass

    @abstractmethod
    def reconnect(self):
        pass

    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def select_org(self, query, bindValue=None):
        pass

    @abstractmethod
    def select(self, query, bindValue=None):
        pass

    @abstractmethod
    def execute(self, query, bindValue=None):
        pass

    @abstractmethod
    def add_bind(self, key, value):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def clear_bind(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
