from datetime import datetime
from Programs.log_file import write_to_log_file, archive_log_file
import sys
from termcolor import colored


def print_greeting():
    print(f'{"–" * 112}')
    print(f'|{"S T O C K S":^110}|')
    print(f'{"–" * 112}')

    current_hour = datetime.now().hour

    message = 'STOCK RESEARCH & RECOMMENDATION'

    if 3 <= int(current_hour) < 12:
        print(f'\n\tGood Morning!\n\n\t{"PROGRAM INITIALIZED":25}: {colored(message, "green")}')
    elif 12 <= int(current_hour) < 16:
        print(f'\n\tGood Afternoon!\n\n\t{"PROGRAM INITIALIZED":25}: {colored(message, "green")}')
    else:
        print(f'\n\tGood Evening!\n\n\t{"PROGRAM INITIALIZED":25}: {colored(message, "green")}')


def print_execution_time(start_time):
    if start_time != 'N/A':
        execution_time = str(datetime.now() - start_time)

        print(f'\n{"–" * 112}')
        print(f'|\t{"PROGRAM EXECUTION TIME":25}: {colored(execution_time, "green"):89}|')
        print(f'{"–" * 112}')

        write_to_log_file(title='PROGRAM COMPLETED',
                          message='/.../RUN.py has completed with an execution time of ' +
                                  execution_time + '.')
    else:
        print(f'\n{"–" * 112}')
        print(f'|\t{"PROGRAM TERMINATED":25}: {colored("--:--:--.----", "red"):89}|')
        print(f'{"–" * 112}')

        write_to_log_file(title='PROGRAM TERMINATED',
                          message='/.../RUN.py has been terminated.')


def print_progress_bar(title, index, data_length):
    bar = colored('\u2588 \u2588 \u2588 ', 'green')
    progress_dict = {0.0: ['10', 1], .10: ['20', 2], .20: ['30', 3], .30: ['40', 4], .40: ['50', 5],
                     .50: ['60', 6], .60: ['70', 7], .70: ['80', 8], .80: ['90', 9], .90: ['100', 10],
                     1.0: ['100', 10]}

    percent = round(index / data_length, 1)

    if percent in progress_dict:
        print(f'\r\t{title:25}: {bar * progress_dict[percent][1]}{progress_dict[percent][0]}%', end='')


def print_error_message(error, message):
    print(f'\n\t{colored(error, "red"):34}: {message}')

    write_to_log_file(title=error,
                      message=f'{message}.')

    print_execution_time(start_time='N/A')

    archive_log_file()

    sys.exit(1)


def print_stock_recommendations(is_simulation, execution_dict):

    if is_simulation == "FALSE":
        print()

        if execution_dict['BUY'] != {} or execution_dict['SELL'] != {}:

            print(f'\n\t{"":25}  {"–" * 64}\n\t{"":25}  | {"STOCK RECOMMENDATIONS":^60} |'
                  f'\n\t{"":25}  {"–" * 64}')
            print(f'\t{"":25}  | {"Transaction":12}   {"Ticker":10}   {"Shares":14}   {"Price":14}  |'
                  f'\n\t{"":25}  {"–" * 64}')

            for transaction_type in execution_dict:

                if transaction_type in ['BUY', 'SELL']:
                    transaction_dict = execution_dict[transaction_type]

                    for stock_ticker in transaction_dict:
                        shares = str(transaction_dict[stock_ticker]['Shares'])
                        price = str(transaction_dict[stock_ticker]['Price'])

                        if transaction_type == 'BUY':
                            transaction_string = colored(transaction_type, 'green')
                        else:
                            transaction_string = colored(transaction_type, 'red')

                        print(f'\t{"":25}  '
                              f'| {transaction_string:21} | {stock_ticker:10} | #{shares:13} | ${price:13}  |'
                              f'\n\t{"":25}  {"–" * 64}')
