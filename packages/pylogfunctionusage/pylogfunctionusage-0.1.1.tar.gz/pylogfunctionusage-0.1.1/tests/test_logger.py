from src.pylogfunctionusage.pylogfunctionusage import LogFunctionUsage
import sqlite3
from time import time


class TestsLogger:
    def __init__(self):
        self.conn = sqlite3.connect('test_logs.db')
        self.cursor = self.conn.cursor()

    def print_ok(self, func_name):
        print(f'\033[92m {func_name}: OK\033[0m')

    def check_count_start_and_end_in_loop(self):
        self.cursor.execute("SELECT COUNT(*) FROM function_logs WHERE function_name = 'my_func' AND type = 'START'")
        count_start = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM function_logs WHERE function_name = 'my_func' AND type = 'END'")
        count_end = self.cursor.fetchone()[0]

        assert count_start == 1000
        assert count_end == 1000
        self.print_ok("check_count_start_and_end_in_loop")

    def check_errors_zero_division(self):
        self.cursor.execute("SELECT COUNT(*) FROM function_logs WHERE Type = 'ERROR'")
        count_error = self.cursor.fetchone()[0]

        assert count_error == 1
        self.print_ok("check_errors_zero_division")

    def check_return_results(self, return_results):
        self.cursor.execute(f"SELECT COUNT(*) FROM function_logs WHERE result = '{return_results}'")
        count_results = self.cursor.fetchone()[0]

        assert count_results == 1
        self.print_ok("check_return_results")

    def check_args_and_kwargs(self, args, kwargs="kwarg"):
        self.cursor.execute(f"""SELECT COUNT(*) FROM function_logs WHERE args LIKE '%{args}%'""")
        count_args = self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM function_logs WHERE kwargs LIKE '%{kwargs}%'")
        count_kwargs = self.cursor.fetchone()[0]
        assert count_args == 2
        assert count_kwargs == 2
        self.print_ok("check_args_and_kwargs")

    def __del__(self):
        self.conn.close()


log = LogFunctionUsage(db_name='test_logs.db', refresh_log_table=True, robust=True, log_results=True)
test = TestsLogger()


@log
def my_func():
    i = 1
    return ["i", f"{i}"]


def loop(range2):
    for i in range(range2):
        my_func()


loop(1000)
test.check_count_start_and_end_in_loop()


@log
def zero_division():
    """An example function for error"""
    print("test zero division")
    print(2 / 0)


zero_division()
test.check_errors_zero_division()


@log
def return_results():
    return "TESTTESTTESTTESTTESTTESTTESTTESTTEST"


results = return_results()
test.check_return_results(results)


@log
def args_and_kwargs(args, kwargs="kwarg"):
    return args, kwargs


args_and_kwargs("test_args", kwargs="kwargs")
test.check_args_and_kwargs("args", kwargs="kwargs")

log_if_raise = LogFunctionUsage(db_name='test_logs.db', refresh_log_table=True, if_raise=True)
test_if_raise = TestsLogger()

@log_if_raise
def error_func():
    print(2 / 0)

try:
    error_func()
except ZeroDivisionError:
    test.print_ok("test_if_raise")
else:
    print(f'\033[91m test_if_raise: FAILED \033[0m')





def time_test(loop_exe=10000):
    """Checks run time added by using logger module"""
    ts = time()

    def function_long(i):
        i = i + 1
        return i

    def loop_long(range_i):
        for i in range(range_i):
            function_long(i)

    loop_long(loop_exe)
    te = (time() - ts)

    ts = time()

    @log_if_raise
    def function_long2(i):
        i = i + 1
        return i

    def loop_long2(range_i):
        for i in range(range_i):
            function_long2(i)

    loop_long2(loop_exe)
    te2 = (time() - ts)

    print(f"On average it add {(te2 - te) / loop_exe}s to function run time")


time_test()

# it adds 0.7ms to func witch is 0.0007s in wal mode
#  3ms , 0.003s in normal mode
