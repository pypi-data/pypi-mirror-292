# encoding: utf-8
# module pylogfunctionsusage
"""

**LogFunctionUsage** is a Python decorator designed to enhance the logging capabilities of your programs functions by
 wrapping functions in a `try:` block. It logs function usage, including calls, exceptions, and results,
 to an SQLite table, making it easier to monitor and debug your code.

"""

import sqlite3
from sys import _getframe


class LogFunctionUsage:
    def __init__(self,
                 db_name: str = 'logs.db',
                 table_name: str = 'function_logs',
                 if_raise: bool = False,
                 print_error: bool = True,
                 refresh_log_table: bool = False,
                 log_results: bool = False,
                 robust: bool = True,
                 live_monitor: bool = False,
                 wal: bool = False):
        """Decorator that wrap function in 'try:' block and log functions usage to sqlite table. \n


        --------

        Params:
        --------

        **db_name: str , default 'logs.db'** \n
        You can specify sqlite3 database name for logs.\n
        It can be database used in your project \n\n

        **table_name: str , default 'function_logs'**\n
        You can specify name for table for storing logs.\n

        **if_raise: bool , default False** \n
        If False program will not throw an error,and it will cointinue. It only log it to db. \n
        If True it will stop, log an error and print out error \n

        **refresh_log_table: bool , default False** \n
        If False script will log all function runs. \n
        If True script clear sql table with every program run \n

        **print_error: bool, default True** \n
        If false, program will not print errors (exceptions). If true it will. \n

        **log_results: bool, default False** \n
        If false, program will not log results of functions, only exceptions will be in table in column results.
        If true it will log results of functions as string representation. \n

        **robust: bool, default True** \n
        If true, it commits to table logs of each function after its complete. \n
        If false it commits all logs at once after program ends. \n
        With false, it is MUCH faster, but use carefully. \n

        **live_monitor: bool, default False** \n
        If true, it commits to table each step of function run (start, end, etc.) \n
        It enable to live monitoring of program runing, but program might slow down. \n
        In some sense it overide robust setting

        **wal: bool , default False** USE CAREFULLY!\n
        If true it adds "PRAGMA journal_mode=WAL" to database, USE CAREFULLY!\n
        It can significant speedup loging in case of massive calling functions (it's about x5 times faster)\n
        but in case of system crash, data might be lost.\n
        Also it changes mode to whole database, DON'T USE THIS MODE WITH YOUR PRODUCTION DATABASE\n
        More information on how "Write-Ahead Log" works:  https://sqlite.org/wal.html

        Examples
        --------
        Create an instance of LogFunctionUsage called log and use it accros your code

        >>> from pylogfunctionusage import LogFunctionUsage
        ... log = LogFunctionUsage(db_name = 'your_database_name.db',
        ...                                  table_name = 'table_for_logs_name' ,
        ...                                  refresh_log_table=True,
        ...                                  if_raise = True)

        >>> @log
        ... def function_to_log():
        ...     print("some function")

        OR create new instance for each method in your code

        >>> @LogFunctionUsage()
        ... def function_to_log():
        ...     print("some function")

        other usage examples

        >>> @LogFunctionUsage(if_raise = True)
        ... def function_to_log():
        ...     print(1/0) # this will throw an error due to 'if_raise = True'



        GOOD practice(faster):

        >>> def function():
        ...     i = 1

        >>> @LogFunctionUsage()
        ... def loop():
        ...     [function() for i in range(1000)]

        BAD practice(slower):

        >>> @LogFunctionUsage()
        ... def function():
        ...     i = 1

        >>> def loop():
        ...     [function() for i in range(1000)]

        SQL:
        -----------

        It save to sqlite table: \n
        Time of function call. **Column: timestamp** \n
        Type of call: Start, End or Except. **Column: type** \n
        Name of function. **Column: function_name** \n
        Aruments names passed to function. **Column: args** \n
        Key-words arguments passed to function. **Column: kwargs** \n
        Results and exceptions of function. **Column: result** \n
        Line of code that call function. **Column: code_line** \n

        """
        self.db_name = db_name
        self.table_name = table_name
        self.conn = sqlite3.connect(self.db_name, timeout=100)
        self.cursor = self.conn.cursor()
        self.wal = wal
        self.varchar_len = 1000
        self.varchar_type_len = f"NVARCHAR({self.varchar_len})"
        if refresh_log_table:
            self.drop_log_table()
        self.create_db_and_log_table(self.table_name)
        self.if_raise = if_raise
        self.print_error = print_error
        self.log_results = log_results
        self.robust = robust
        self.live_monitor = live_monitor

    def create_db_and_log_table(self, table_name: str = 'function_logs'):
        """ Function for creating database and log table """
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           function_name VARCHAR(125),
                           type VARCHAR(10),
                           code_line INT,
                           timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                           args {self.varchar_type_len},
                           kwargs {self.varchar_type_len},
                           result NTEXT);''')
        if self.wal:
            self.cursor.execute(f'''PRAGMA journal_mode = WAL;''')
        self.conn.commit()

    def drop_log_table(self, table_name: str = 'function_logs'):
        """ Function for dropping table """
        self.cursor.execute(f'''DROP TABLE IF EXISTS {table_name}''')
        self.conn.commit()

    def log_start(self, *args):
        """ Log start of the function execution to table """
        self.cursor.execute(f'''INSERT INTO {self.table_name} (function_name,
                                                 type,
                                                 code_line,
                                                 args,
                                                 kwargs) 
                                                 VALUES (?, ?, ?, ?, ?)''', args)
        if self.live_monitor:
            self.conn.commit()

    def log_exception_or_end(self, *args):
        """ Log the exception or end of the function execution to table """
        query = f'''INSERT INTO {self.table_name} (function_name,
                                               type,
                                               code_line,
                                               args,
                                               kwargs,
                                               result)
                                               VALUES (?, ?, ?, ?, ?, ?)'''
        self.cursor.execute(query, args)
        if self.live_monitor:
            self.conn.commit()

    def __call__(self, func, *args, **kwargs):
        def wrapper(*args, **kwargs):
            # Convert arguments and keyword arguments to strings
            args_str = str(args)
            kwargs_str = str(kwargs)
            func_line = _getframe().f_back.f_lineno if hasattr(_getframe().f_back, "f_lineno") else None
            # Log start
            self.log_start(func.__name__, "START", func_line, args_str, kwargs_str)

            try:
                # Execute the original function and capture its result
                result = func(*args, **kwargs)
            except Exception as e:
                # Insert log entry for the exception
                self.log_exception_or_end(func.__name__, "ERROR", func_line, args_str, kwargs_str, str(e), )
                result = None
                if self.if_raise:
                    raise
                if self.print_error:
                    print(f'\033[91m{e} in {func.__name__} \033[0m')
            if not self.log_results:
                self.log_exception_or_end(func.__name__, "END", func_line, args_str, kwargs_str, None)
            else:
                self.log_exception_or_end(func.__name__, "END", func_line, args_str, kwargs_str, str(result))

            if not self.live_monitor:
                if self.robust:
                    self.conn.commit()

            # Return the result of the original function
            return result

        return wrapper

    def __del__(self):
        if not self.robust:
            self.conn.commit()
        self.conn.close()
