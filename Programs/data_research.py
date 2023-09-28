from datetime import timedelta
import numpy as np
import pandas as pd
from Programs.data_files import retrieve_sector_and_industry, retrieve_stock_dividends, retrieve_earnings_dates
from Programs.log_file import write_to_log_file
from Programs.print_styles import print_progress_bar, print_error_message
from Programs.timestamps_file import check_timestamps_file
from random import randint
from stock_indicators import Quote, indicators


stock_data_folder_path = 'Files/Stock_Data'
indicators_file_path = 'Files/indicators.txt'


def retrieve_date_dict(algorithm_dict, program_start_time):
    date_dict = {'Initial_Research': [], 'Back_Test_Research': [], 'Earliest_Date': []}

    research_range_in_days = algorithm_dict['Research_Range_In_Days']
    back_test_count = algorithm_dict['Back_Test_Count']
    dataframe_range_in_years = algorithm_dict['Dataframe_Range_In_Years']

    initial_end_date = program_start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    initial_start_date = initial_end_date - timedelta(days=research_range_in_days)
    initial_date_list = \
        [initial_start_date + timedelta(days=x) for x in range(0, (initial_end_date - initial_start_date).days + 1)]
    date_dict['Initial_Research'].append(initial_date_list)

    # Calculate the dataframe range in days (adjusting it to be shorter than the actual dataframe)
    dataframe_days = round((dataframe_range_in_years - 1) * 365)

    upper_limit = initial_start_date
    lower_limit = initial_start_date - timedelta(days=dataframe_days)
    limit_length_in_days = (upper_limit - lower_limit).days
    for i in range(back_test_count):
        random_day_count = randint(0, limit_length_in_days)
        random_end_date = upper_limit - timedelta(days=random_day_count)
        random_start_date = random_end_date - timedelta(days=research_range_in_days)

        date_list = \
            [random_start_date + timedelta(days=x) for x in range(0, (random_end_date - random_start_date).days + 1)]

        date_dict['Back_Test_Research'].append(date_list)

        date_dict['Earliest_Date'].append(random_start_date)

    if back_test_count != 0:
        earliest_date = sorted(date_dict['Earliest_Date'])[0]
    else:
        earliest_date = initial_start_date

    date_dict['Earliest_Date'] = earliest_date

    return date_dict


def calculate_indicator(csv_dataframe, data_list, indicator_function, sub_function, column_name):
    if '+' in sub_function:
        values = indicator_function(quotes=data_list)
        sub_function_list = sub_function.split('+')
        # Calculate the sub functions separately
        csv_dataframe[sub_function_list[0]] = [getattr(i, sub_function_list[0]) for i in values]
        csv_dataframe[sub_function_list[1]] = [getattr(i, sub_function_list[1]) for i in values]
        # Add the sub function results together
        csv_dataframe[column_name] = csv_dataframe[sub_function_list[0]] + csv_dataframe[sub_function_list[1]]
        # Drop the temporary columns
        csv_dataframe.drop(columns=[sub_function_list[0], sub_function_list[1]], axis=1, inplace=True)

    else:
        csv_dataframe[column_name] = [getattr(i, sub_function) for i in indicator_function(quotes=data_list)]

    csv_dataframe[column_name] = np.array(csv_dataframe[column_name], dtype=np.float32)


def expand_dataframe(csv_dataframe, data_list, program_start_time):
    indicator_dict = {'macd': [indicators.get_macd, 'histogram'],
                      'rsi': [indicators.get_rsi, 'rsi'],
                      'aroon': [indicators.get_aroon, 'oscillator'],
                      'adx': [indicators.get_adx, 'adx'],
                      'bollinger': [indicators.get_bollinger_bands, 'percent_b'],
                      'stochastic': [indicators.get_stoch, 'percent_j'],
                      'chandelier': [indicators.get_chandelier, 'chandelier_exit'],
                      'pivots': [indicators.get_pivots, 'high_line'],
                      'adl': [indicators.get_adl, 'adl'],
                      'mfi': [indicators.get_mfi, 'mfi'],
                      'obv': [indicators.get_obv, 'obv'],
                      'pvo': [indicators.get_pvo, 'histogram'],
                      'zigzag': [indicators.get_zig_zag, 'zig_zag'],
                      'bop': [indicators.get_bop, 'bop'],
                      'elder': [indicators.get_elder_ray, 'bull_power+bear_power'],
                      'chop': [indicators.get_chop, 'chop']}

    for indicator in indicator_dict:
        calculate_indicator(csv_dataframe=csv_dataframe,
                            data_list=data_list,
                            indicator_function=indicator_dict[indicator][0],
                            sub_function=indicator_dict[indicator][1],
                            column_name=indicator)

    update_needed = check_timestamps_file(file_name='update_indicators_file.py',
                                          program_start_time=program_start_time)
    if update_needed is True:
        with open(indicators_file_path, 'w') as indicators_file:
            for key in indicator_dict:
                indicators_file.write(f'{key}\n')

        write_to_log_file(title='INDICATORS FILE',
                          message='/.../indicators.txt has been updated.')


def limit_dataframe(csv_dataframe, limit_date):
    csv_dataframe.reset_index(drop=True, inplace=True)

    index_list = []
    # Loop until a recognized date is found (20 loops maximum)
    adjustment_count = 0
    while len(index_list) == 0:
        index_list = csv_dataframe.index[csv_dataframe['date'] == limit_date].tolist()
        limit_date -= timedelta(days=1)

        adjustment_count += 1
        if adjustment_count >= 20:
            print()
            print_error_message(error='DATE NOT FOUND',
                                message=f'The limit date '
                                        f'{str(limit_date + timedelta(days=adjustment_count)).split(" ")[0]} '
                                        f'could not be found in the csv dataframe')

    if (index_list[0] - 200) < 0:
        print()
        print_error_message(error='NOT ENOUGH DATA',
                            message=f'The limit date '
                                    f'{str(limit_date + timedelta(days=adjustment_count)).split(" ")[0]} '
                                    f'will reach beyond the first known data')

    csv_dataframe = csv_dataframe.iloc[index_list[0] - 200:]

    return csv_dataframe


def create_csv_dataframe(file_path, stock_ticker, limit_date, stock_dict, algorithm_dict,
                         program_start_time):

    indicator_data_file_path = f'{stock_data_folder_path}/{stock_ticker}/Indicator_Data/indicator_data.csv'

    dataframe_range_in_years = algorithm_dict['Dataframe_Range_In_Years']
    # Calculate the minimum dataframe length (using 250 trading days per year on average)
    min_dataframe_length = dataframe_range_in_years * 250

    csv_dataframe = pd.read_csv(file_path)

    if len(csv_dataframe) >= min_dataframe_length:
        csv_dataframe = csv_dataframe.tail(min_dataframe_length)

        csv_dataframe['date'] = pd.to_datetime(csv_dataframe['date'])

        data_list = [Quote(d, o, h, l, c, v) for d, o, h, l, c, v
                     in zip(csv_dataframe['date'], csv_dataframe['open'], csv_dataframe['high'],
                            csv_dataframe['low'], csv_dataframe['close'], csv_dataframe['volume'])]

        expand_dataframe(csv_dataframe=csv_dataframe,
                         data_list=data_list,
                         program_start_time=program_start_time)

        csv_dataframe.to_csv(indicator_data_file_path, index=False)

        csv_dataframe = limit_dataframe(csv_dataframe=csv_dataframe,
                                        limit_date=limit_date)

        stock_dict[stock_ticker]['Dataframe'] = csv_dataframe

        write_to_log_file(title='CSV DATAFRAME',
                          message=f'/.../{stock_ticker}/.../indicator_data.csv has been created.')

    else:
        write_to_log_file(title='CSV DATAFRAME',
                          message=f'Not enough historical {stock_ticker} data for a csv dataframe.')


def research_stock_data(stock_ticker, limit_date, algorithm_dict, start_time, data_count, data_length):
    historical_data_file_path = f'{stock_data_folder_path}/{stock_ticker}/Historical_Data/historical_data.csv'

    stock_dict = {stock_ticker: {}}

    create_csv_dataframe(file_path=historical_data_file_path,
                         stock_ticker=stock_ticker,
                         limit_date=limit_date,
                         stock_dict=stock_dict,
                         algorithm_dict=algorithm_dict,
                         program_start_time=start_time)

    retrieve_sector_and_industry(stock_ticker=stock_ticker,
                                 stock_dict=stock_dict)

    retrieve_stock_dividends(stock_ticker=stock_ticker,
                             stock_dict=stock_dict)

    retrieve_earnings_dates(stock_ticker=stock_ticker,
                            stock_dict=stock_dict)

    print_progress_bar(title=f'RESEARCHING {stock_ticker} DATA',
                       index=data_count,
                       data_length=data_length)

    return stock_dict
