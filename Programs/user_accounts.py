from datetime import datetime
import glob
import os
import pathlib
from Programs.investment_taxes import retrieve_stock_tax_type
from Programs.log_file import archive_log_file
from Programs.log_file import write_to_log_file
from Programs.print_styles import print_execution_time
import sys
from termcolor import colored


accounts_folder_path = 'Files/Accounts'


def retrieve_account_funds():
    is_accepted = False
    while is_accepted is False:
        available_funds_input = input(f'\t{"":25}+ Enter available funds --> $')

        if available_funds_input.isdigit() is True:
            return float(available_funds_input)

        else:
            print(f'\t{"":25}• Please enter a number.\n')


def create_account_files(user_name):
    portfolio_folder_path = f'{accounts_folder_path}/{user_name}/Portfolio/Backups/'
    purchase_history_folder_path = f'{accounts_folder_path}/{user_name}/Purchase_History/Backups/'

    pathlib.Path(portfolio_folder_path).mkdir(parents=True, exist_ok=True)
    pathlib.Path(purchase_history_folder_path).mkdir(parents=True, exist_ok=True)

    account_funds = retrieve_account_funds()

    overwrite_account_files(user_name=user_name,
                            account_funds=account_funds)


def overwrite_account_files(user_name, account_funds):
    portfolio_file_path = f'{accounts_folder_path}/{user_name}/Portfolio/portfolio.csv'
    purchase_history_file_path = f'{accounts_folder_path}/{user_name}/Purchase_History/purchase_history.csv'

    file_list = [[portfolio_file_path,
                  'Purchase_Date,Ticker,Sector,Industry,Shares,Price,Investment,Available_Funds\n',
                  f'--,--,--,--,--,--,--,{str(account_funds)}\n'],
                 [purchase_history_file_path,
                  'Transaction_Date,Type,Ticker,Shares,Price,Investment,Tax_Type\n',
                  '']]

    for file in file_list:
        with open(file[0], 'w') as account_file:
            account_file.write(file[1])
            account_file.write(file[2])

    if user_name != 'simulation':
        write_to_log_file(title='ACCOUNT FILES',
                          message=f'Account files have been created for user {user_name}.')


def manually_update_account_files(user_name, is_simulation):
    portfolio_file_path = f'{accounts_folder_path}/{user_name}/Portfolio/portfolio.csv'
    purchase_history_file_path = f'{accounts_folder_path}/{user_name}/Purchase_History/purchase_history.csv'

    with open(portfolio_file_path, 'r') as portfolio_file:
        portfolio_data_list = [line.replace('\n', '').split(',') for line in portfolio_file]

    available_funds = float(portfolio_data_list[-1][-1])

    if 'PENDING' in str(portfolio_data_list):
        print(f'\n\t{"":25}  {"–" * 44}\n\t{"":25}  | {"MANUAL ADJUSTMENTS":^40} |\n\t{"":25}  {"–" * 44}')
        print(f'\t{"":25}  | {"Transaction"}   {"Ticker"}   {"Adjustment":^16}  |\n\t{"":25}  {"–" * 44}')

    purchase_history_file = open(purchase_history_file_path, 'a')

    ignore_stock_list = []
    for data_list in portfolio_data_list:
        if 'PENDING_BUY' in data_list:
            print(f'\t{"":25}  {colored("BUY", "green"):^25}{data_list[1]:^6} | ', end='')
            input_shares = float(input('Shares #'))
            input_price = float(input(f'{"":52}  | Price  $'))
            print(f'\t{"":25}  {"–" * 44}')

            investment = round(input_shares * input_price, 4)
            available_funds -= investment

            data_list[0] = str(datetime.now()).split(' ')[0]
            data_list[4] = str(input_shares)
            data_list[5] = str(input_price)
            data_list[6] = str(investment)

            purchase_history_file.write(f'{data_list[0]},BUY,{data_list[1]},{",".join(data_list[4:7])},--\n')

        if 'PENDING_SELL' in data_list:
            print(f'\t{"":25}  {colored("SELL", "red"):^25}{data_list[1]:^6} | ', end='')
            input_price = float(input('Price  $'))
            print(f'\t{"":25}  {"–" * 44}')

            investment = round(float(data_list[4]) * input_price, 4)
            available_funds += investment

            tax_type = retrieve_stock_tax_type(is_simulation=is_simulation,
                                               portfolio_data_list=portfolio_data_list,
                                               stock_ticker=data_list[1],
                                               sell_date=data_list[0])

            data_list[0] = str(datetime.now()).split(' ')[0]
            data_list[5] = str(input_price)
            data_list[6] = str(investment)

            purchase_history_file.write(f'{data_list[0]},SELL,{data_list[1]},{",".join(data_list[4:7])},{tax_type}\n')
            ignore_stock_list.append(data_list[1])

    purchase_history_file.close()

    with open(portfolio_file_path, 'w') as portfolio_file:
        for data_list in portfolio_data_list:
            if data_list[1] not in ignore_stock_list:
                if 'Available_Funds' not in data_list:
                    data_list[-1] = str(round(available_funds, 2))
                portfolio_file.write(f'{",".join(data_list)}\n')


def backup_account_files(is_simulation, user_name):
    if is_simulation == "FALSE":
        portfolio_file_path = f'{accounts_folder_path}/{user_name}/Portfolio/portfolio.csv'
        portfolio_backups_folder_path = f'{accounts_folder_path}/{user_name}/Portfolio/Backups'
        purchase_history_file_path = f'{accounts_folder_path}/{user_name}/Purchase_History/purchase_history.csv'
        purchase_history_backups_folder_path = f'{accounts_folder_path}/{user_name}/Purchase_History/Backups'

        account_path_list = [[portfolio_backups_folder_path, portfolio_file_path],
                             [purchase_history_backups_folder_path, purchase_history_file_path]]
        for path_list in account_path_list:
            backup_file_path = f'{path_list[0]}/{str(datetime.now().replace(microsecond=0)).replace(" ", "_")}.csv'

            backup_file = open(backup_file_path, 'w')
            with open(path_list[1], 'r') as original_file:
                for line in original_file:
                    backup_file.write(line)
            backup_file.close()

            file_paths_list = sorted(glob.glob(path_list[0] + '/*.csv'), reverse=True)

            for index, file_path in enumerate(file_paths_list):
                if index > 9:
                    os.remove(file_path)

        write_to_log_file(title='ACCOUNT BACKUP',
                          message=f'{user_name} account file backups have been updated.')


def retrieve_user_name(is_simulation):
    user_name = ''

    if is_simulation == "FALSE":
        print()

        user_name_input = input(f'\t{"ENTER PORTFOLIO USERNAME":25}: ').lower()

        portfolio_file_path = f'{accounts_folder_path}/{user_name_input}/Portfolio/portfolio.csv'

        try:
            portfolio_file = open(portfolio_file_path, 'r')
            portfolio_file.close()

            manually_update_account_files(user_name=user_name_input,
                                          is_simulation=is_simulation)

            user_name = user_name_input

        except FileNotFoundError:
            is_accepted = False
            while is_accepted is False:
                unknown_user_name_input = input(f'\t{"":25}+ This username has not been seen before. '
                                                f'Would you like to continue? Y/N --> ').upper()

                if unknown_user_name_input == 'Y':
                    user_name = user_name_input
                    create_account_files(user_name=user_name)
                    is_accepted = True

                elif unknown_user_name_input == 'N':
                    print_execution_time('N/A')
                    archive_log_file()
                    sys.exit(1)

                else:
                    print(f'\t{"":25}• Please enter either Y or N.\n')

    else:
        user_name = 'simulation'

    write_to_log_file(title='CURRENT USER',
                      message=f'{user_name} user files have been accessed.')

    return user_name
