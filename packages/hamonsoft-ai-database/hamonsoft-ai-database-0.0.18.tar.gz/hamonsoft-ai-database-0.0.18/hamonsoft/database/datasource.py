import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import mysql.connector


class DatabaseSource(ABC):
    def __init__(self, use_pool: bool = True, pool_size: int = 5, pool_name: str = "default-pool"):
        self._single_connection = None
        self._pool = None

        self._use_pool = use_pool
        self._pool_size = pool_size
        self._pool_name = pool_name
        self._create_con_process()

    @abstractmethod
    def _create_pool_connector(self):
        """
        database의 connection pool을 만드는 로직
        :return:
        """
        pass

    @abstractmethod
    def _create_single_connector(self):
        """
        단일 connection을 만드는 로직
        :return:
        """
        pass

    @abstractmethod
    def get_connection(self):
        """
        최종적으로 사용자가 cursor 메소드만 호출하여 사용할 수 있는 단계로 리턴
        :return:
        """
        pass

    def _create_con_process(self, attempts: int = 3):
        """
        database 생성 시 재시도 로직
        :param attempts:
        :return:
        """
        attempt = 1
        while attempt < attempts + 1:
            try:
                if self._use_pool:
                    self._create_pool_connector()
                else:
                    self._create_single_connector()
                return
            except Exception as e:
                e_message = f"[retry: {attempt}/{attempts}] {str(e)}"
                if attempt == attempts:
                    logging.error(e_message)
                    import sys
                    sys.exit(1)
                logging.error(e_message)
                attempt += 1

    def _basic_exception_handler_with_retry(self, exception: BaseException):
        """
          기본 예외를 처리하고, 커넥션을 재시도
          일정 시간 대기 후에 새로운 데이터베이스 커넥션을 시도
          재시도가 필요한 경우나, 예외 상황에서 자동으로 복구를 시도할 때 사용

          :param exception: 처리할 예외 객체
          :return: 새로운 데이터베이스 커넥션 객체
          """
        import traceback, random
        err_id = random.randint(1000, 9999)

        if isinstance(exception, BaseException):
            logging.warning(f"{err_id}: {str(exception)}...retry... \n {traceback.format_stack()}")
            time.sleep(3)
            return self.get_connection()


class MySql(DatabaseSource):

    def __init__(self, use_pool: bool = False, **kwargs):
        self.kwargs = kwargs
        super().__init__(use_pool=use_pool, pool_size=kwargs.get('pool_size', 5), pool_name=kwargs.get('pool_name', "default-pool"))

    def _create_pool_connector(self):
        self._pool = mysql.connector.pooling.MySQLConnectionPool(**self.kwargs)
        logging.info(f"created connection pool. pool size: {self._pool_size}")

    def _create_single_connector(self):
        self._single_connection = mysql.connector.connect(**self.kwargs)
        logging.info("created a single connection")

    def get_connection(self):
        try:
            if self._use_pool:
                connect = self._pool.get_connection()
            else:
                connect = self._single_connection
            logging.debug(f"get connection: {connect.connection_id}")
            return connect
        except Exception as e:
            return self._basic_exception_handler_with_retry(e)

    @staticmethod
    def self_cursor(func):
        """
        커서를 열고 함수 실행 후 커서와 커넥션을 닫는 데코레이터
        함수에 cursor 객체를 전달
        """

        def wrapper(self, *args, **kwargs):
            self.connection = self.get_connection()
            if self.connection.is_closed():
                raise Exception(f"not connected to database. type: {func.__name__}")
            self.connection_id = self.connection.connection_id
            self.cursor = self.connection.cursor(dictionary=True)

            logging.debug(f"get connection id: {self.connection_id}")
            try:
                result = func(self, *args, **kwargs)
                return result
            except mysql.connector.errors.ProgrammingError as pe:
                self.connection.rollback()
                logging.error(f"error: {pe}")
            except Exception as e:
                self.connection.rollback()
                raise e
            finally:
                self.connection.commit()
                self.cursor.close()
                self.connection.close()
                logging.debug(f"close connection id: {self.connection_id}")

        return wrapper

    @staticmethod
    def self_connection(func):
        """
        커넥션을 열고 함수 실행 후 커넥션을 닫는 데코레이터
        함수에 connection 객체를 전달
        """

        def wrapper(self, *args, **kwargs):
            self.connection = self.get_connection()
            self.connection_id = self.connection.connection_id
            logging.debug(f"get connection id: {self.connection_id}")
            try:
                result = func(self, *args, **kwargs)
                return result
            finally:
                self.connection.close()
                logging.debug(f"close connection id: {self.connection_id}")

        return wrapper

    @staticmethod
    def make_sub_partition_syntax_date_format(start_datetime: datetime, extend_count: int, unit: str = "d") -> str:
        if unit.lower() == "d":
            fmt = "%Y%m%d"
            td = timedelta(days=1)
        elif unit.lower() == "h":
            fmt = "%Y%m%d%H"
            td = timedelta(hours=1)
        else:
            raise ValueError("Invalid unit. 'd' || 'h'")

        partition_list = []
        standard_datetime = start_datetime
        for i in range(extend_count):
            partition_name_str = standard_datetime.strftime(fmt)
            partition_value_str = (standard_datetime + td).strftime(fmt)
            partition_list.append(f"PARTITION p{partition_name_str} VALUES LESS THAN ({partition_value_str})")
            standard_datetime += td

        return ",\n".join(partition_list)
