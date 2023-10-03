import glob
from Programs.log_file import write_to_log_file
import shutil
from termcolor import colored


preferred_stocks_file_path = 'Files/preferred_stocks.txt'
stock_data_folder_path = 'Files/Stock_Data'
accounts_folder_path = 'Files/Accounts'


def purge_outdated_stocks(preferred_stocks_list):
    scraped_ticker_list = [i.split('/')[2] for i in glob.glob(f'{stock_data_folder_path}/*')]

    owned_ticker_set = set()
    for file_path in glob.glob(f'{accounts_folder_path}/*/Portfolio/portfolio.csv'):
        if 'simulation' not in file_path:
            with open(file_path, 'r') as portfolio_file:
                for index, line in enumerate(portfolio_file):
                    if index > 0:
                        owned_ticker_set.add(line.split(',')[1])

    delete_list = []
    for stock_ticker in scraped_ticker_list:
        if stock_ticker not in preferred_stocks_list and stock_ticker not in owned_ticker_set:
            delete_list.append(f'{stock_data_folder_path}/{stock_ticker}/')

    if len(delete_list) > 0:
        is_accepted = False
        while is_accepted is False:
            print()

            confirmation_input = input(f'\t{colored("DELETE DATA", "red"):34}: Are you sure you want to delete '
                                       f'{len(delete_list)} of the stock data folders? Y/N --> ').upper()

            if confirmation_input == 'Y':
                for folder_path in delete_list:
                    shutil.rmtree(folder_path)
                    write_to_log_file(title='PURGED DATA',
                                      message=f'/.../{folder_path.split("/")[-2]}/ is outdated and has been deleted.')
                is_accepted = True

            elif confirmation_input == 'N':
                is_accepted = True

            else:
                print(f'\t{"":25}• Please enter either Y or N.')

    return owned_ticker_set


def retrieve_preferred_stocks_list(program_start_time):
    current_date = program_start_time

    with open(preferred_stocks_file_path, 'r') as preferred_stocks_file:
        preferred_stocks_list = [line.replace('\n', '').replace('/', '-') for line in preferred_stocks_file]

    owned_ticker_set = purge_outdated_stocks(preferred_stocks_list=preferred_stocks_list,
                                             current_date=current_date)

    for stock_ticker in owned_ticker_set:
        if stock_ticker not in preferred_stocks_list and stock_ticker != '--':
            preferred_stocks_list.append(stock_ticker)

    return preferred_stocks_list
