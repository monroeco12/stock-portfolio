from datetime import datetime
from Programs.algorithm_file import retrieve_algorithm_dict
from Programs.data_research import retrieve_date_dict, research_stock_data
from Programs.data_scrapers import scrape_stock_data
from Programs.data_verification import verify_scraped_data
from Programs.log_file import overwrite_log_file, archive_log_file
from Programs.portfolio_file import retrieve_stock_portfolio
from Programs.preferred_stocks import retrieve_preferred_stocks_list
from Programs.print_styles import print_greeting, print_execution_time
from Programs.purchase_history_file import retrieve_purchase_history_dictionary, calculate_program_performance
from Programs.RUN_execution import run_execution
from Programs.RUN_research import run_research
from Programs.stock_executions import execute_stock_recommendations
from Programs.user_accounts import retrieve_user_name, backup_account_files


program_start_time = datetime.now()

overwrite_log_file()

algorithm_dict = retrieve_algorithm_dict()
is_simulation = algorithm_dict['Simulation']

print_greeting()

user_name = retrieve_user_name(is_simulation=is_simulation)

preferred_stocks_list = retrieve_preferred_stocks_list(program_start_time=program_start_time)

print()

# Create progress bar variables
data_count = 1
data_length = len(preferred_stocks_list)

recommendation_dict = {'BUY': {}, 'SELL': {}}
complete_stock_dict = {}
for stock_ticker in preferred_stocks_list:
    scrape_stock_data(stock_ticker=stock_ticker,
                      program_start_time=program_start_time,
                      data_count=data_count,
                      data_length=data_length)

    verify_scraped_data(stock_ticker=stock_ticker,
                        current_date=program_start_time,
                        data_count=data_count,
                        data_length=data_length)

    date_dict = retrieve_date_dict(algorithm_dict=algorithm_dict,
                                   program_start_time=program_start_time)

    stock_dict = research_stock_data(stock_ticker=stock_ticker,
                                     limit_date=date_dict['Earliest_Date'],
                                     algorithm_dict=algorithm_dict,
                                     start_time=program_start_time,
                                     data_count=data_count,
                                     data_length=data_length)

    run_research(algorithm_dict=algorithm_dict,
                 date_dict=date_dict,
                 stock_dict=stock_dict,
                 stock_ticker=stock_ticker,
                 program_start_time=program_start_time)

    run_execution(is_simulation=is_simulation,
                  user_name=user_name,
                  stock_ticker=stock_ticker,
                  algorithm_dict=algorithm_dict,
                  stock_dict=stock_dict,
                  recommendation_dict=recommendation_dict,
                  program_start_time=program_start_time.replace(hour=0, minute=0, second=0, microsecond=0))

    complete_stock_dict[stock_ticker] = stock_dict[stock_ticker]

    data_count += 1

if is_simulation == "FALSE":
    algorithm_dict = retrieve_algorithm_dict()

    # Sort the buy recommendation dictionary by algorithm values, greatest to least
    sorted_buy = sorted(recommendation_dict['BUY'].items(), key=lambda item: item[1][2], reverse=True)

    recommendation_dict['BUY'] = {}
    for buy_item in sorted_buy:
        recommendation_dict['BUY'][buy_item[0]] = buy_item[1]

    portfolio_dict = retrieve_stock_portfolio(user_name=user_name)
    purchase_history_dict = retrieve_purchase_history_dictionary(user_name=user_name)

    execute_stock_recommendations(is_simulation=is_simulation,
                                  user_name=user_name,
                                  algorithm_dict=algorithm_dict,
                                  stock_dict=complete_stock_dict,
                                  portfolio_dict=portfolio_dict,
                                  purchase_history_dict=purchase_history_dict,
                                  recommendation_dict=recommendation_dict,
                                  current_date=program_start_time.replace(hour=0, minute=0, second=0, microsecond=0))

    calculate_program_performance(user_name=user_name)

    backup_account_files(is_simulation=is_simulation,
                         user_name=user_name)

else:
    print()

print_execution_time(start_time=program_start_time)

archive_log_file()
