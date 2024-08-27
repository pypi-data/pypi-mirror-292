# `pylogfunctionusage`

## Project Description

**LogFunctionUsage** is a Python decorator designed to enhance the logging capabilities of your programs functions by wrapping functions in a `try:` block. It logs function usage, including calls, exceptions, and results, to an SQLite table, making it easier to monitor and debug your code.

## Purpose

This module was originally written to monitor complex calculations during a master's thesis project. The need for precise and efficient logging arose, leading to the development of a solution that integrates seamlessly with SQLite databases. This enables comprehensive monitoring and debugging without significant performance overhead.

## Features

- **Database Configuration**: Customize the SQLite database name used for logging.
- **Table Name Customization**: Specify the table name for storing logs.
- **Error Handling**: Choose whether the program continues or stops on an error.
- **Log Table Refresh**: Option to clear the log table with each program run.
- **Error Printing**: Configure whether errors are printed to the console.
- **Result Logging**: Optionally log the results of functions.
- **Robustness**: Choose between committing logs immediately or at the end of the program.
- **Live Monitoring**: Enable live monitoring of program execution.
- **Write-Ahead Logging (WAL)**: Significant speedup for massive function calls, but use with caution.

## Performance

**LogFunctionUsage** is optimized for speed by using pure SQL expressions, which contrasts with tools based on ORM systems like SQLAlchemy. This approach ensures faster logging. On laptop with simple functions:

- Adds approximately 0.7ms (0.0007s) to function run time in WAL mode.
- Adds approximately 3ms (0.003s) to function run time in normal mode.

### Limitations 
As this module relies on sqlite db it doesn't support async code.

## Difference Over the `logging` Module

While the Python `logging` module is versatile and powerful, **LogFunctionUsage** offers specific advantages for function-level logging:

- **Granular Control**: Logs detailed function execution data, including arguments, keyword arguments, results, and exceptions.
- **SQL Storage**: Logs are stored in an SQLite table, making them easily accessible for querying and integration with other tools.
- **Performance**: Faster logging performance due to direct SQL expressions.

## Integration with Visualization Tools

The sql table with logs can be plugged into any visualization or reporting tool, such as:

- **Dash**
- **PowerBI**
- **Tableau**


This flexibility allows for advanced analysis, monitoring and visualization of function execution data.

## Simplicity

Using this module is incredibly simple. All you need is to decorate your functions, and the logging is taken care of. No complex setup or extensive configuration is required.


## Installation

you can clone the repository and install it from source:

```bash
pip install pylogfunctionusage
```
```bash
git clone https://github.com/Ambroise-D/pylogfunctionusage.git
cd pylogfunctionusage
python setup.py install
```

or copy file pylogfunctionusage.py to your project and simply use it!

## Dependencies
**LogFunctionUsage** does not require any additional packages beyond the standard Python library. It uses built-in modules such as sqlite3, ensuring that you can use it without needing to install external dependencies.

## Usage
### Basic Usage
Create an instance of LogFunctionUsage and use it across your code:

```python
from pylogfunctionusage import LogFunctionUsage

log = LogFunctionUsage()

OR

log = LogFunctionUsage(db_name='your_database_name.db',
                       table_name='function_logs',
                       if_raise=False,
                       print_error=True,
                       refresh_log_table=True,
                       log_results=False,
                       robust=True,
                       live_monitor=False,
                       wal=False)


@log
def func_to_log(x, y="y"):
    return "some results"
```
### Error Handling Example
```python
@LogFunctionUsage(if_raise=True)
def function_to_log():
    print(1/0)  # This will throw an error due to 'if_raise = True'
```

## SQL Logging
Logs are saved to an SQLite table with the following columns: 
- **function_name:** Name of the function.
- **type:** Type of call (Start, End, or Except).
- **code_line:** Line of code that called the function.
- **timestamp:** Time of function call.
- **args:** Argument names passed to the function.
- **kwargs:** Keyword arguments passed to the function.
- **result:** Results and exceptions of the function.

#### Example log looks like:

| id  |      function_name      | type  | code_line |      timestamp      |      args       |    kwargs    |      result      |
|:---:|:-----------------------:|:-----:|:---------:|:-------------------:|:---------------:|:------------:|:----------------:|
|  1  |       func_to_log       | START |    42     | 2024-04-20 16:20:00 | "('some_str',)" | "{'y': 'y'}" |       None       | 
|  2  |       func_to_log       |  END  |    42     | 2024-04-20 16:20:42 | "('some_str',)" | "{'y': 'y'}" |  'some results'  | 

## Bugs report
Please submit an issue on GitHub.

## Contributing
We welcome contributions to the LogFunctionUsage project! If you have ideas, suggestions, or improvements, or if you want to participate in the development of this module, please feel free to open an issue or submit a pull request on our GitHub repository. Your contributions help us enhance the functionality and usability of the module, and we appreciate your input. 

## License
This project is licensed under the **MIT** License - see the LICENSE file for details.