from datetime import datetime
import glob
import json
from Programs.log_file import write_to_log_file
from random import randint, randrange, choice


algorithm_file_path = 'Files/algorithm.json'
indicators_file_path = 'Files/indicators.txt'
accounts_folder_path = 'Files/Accounts'


def retrieve_algorithm_dict():
    with open(algorithm_file_path, 'r') as json_dict:
        algorithm_dict = json.load(json_dict)
        for key in ['Simulation']:
            algorithm_dict[key] = algorithm_dict[key].upper()

    return algorithm_dict


def randomize_algorithm(algorithm_dict):
    with open(indicators_file_path, 'r') as indicators_file:
        current_indicators_list = [i.replace('\n', '') for i in indicators_file]

    indicator_count = randint(1, 5)

    indicator_list = []
    buy_pattern_string = choice(['I', 'D'])
    sell_pattern_string = choice(['I', 'D', 'IGNORE'])
    for i in range(indicator_count):
        index = randint(0, len(current_indicators_list) - 1)
        indicator_list.append(current_indicators_list[index])

        current_indicators_list.pop(index)

        buy_pattern_string += '/' + choice(['I', 'D'])
        if sell_pattern_string != 'IGNORE':
            sell_pattern_string += '/' + choice(['I', 'D'])

    algorithm_dict['Past_Periods'] = randrange(5, 205, 5)
    algorithm_dict['Indicator_List'] = indicator_list
    algorithm_dict['Indicator_Strength'] = randint(0, 5)
    algorithm_dict['Buy_Pattern'] = buy_pattern_string
    algorithm_dict['Sell_Pattern'] = sell_pattern_string
    algorithm_dict['Sell_Profit'] = round(randrange(5, 105, 5) * .001, 3)
    algorithm_dict['Sell_Loss'] = round(randrange(1, 31, 1) * -.01, 2)
    algorithm_dict['Max_Stock_Count'] = 1
    algorithm_dict['Max_Stock_Percent'] = 1
    algorithm_dict['Max_Sector_Percent'] = 1


def calculate_algorithm_value(purchase_count, sell_count, funds, income):
    if purchase_count > 0:
        sell_percentage = sell_count / purchase_count
        income_percentage = (((funds + sum(income)) - funds) / abs(funds)) * 10

        algorithm_value = income_percentage + sell_percentage

    else:
        algorithm_value = 0

    return algorithm_value


def save_top_algorithm(stock_ticker, program_start_time):
    long_term_research_file_path = f'Files/Stock_Data/{stock_ticker}/' \
                                   f'Long_Term_Research/long_term_research.csv'
    top_algorithm_file_path = f'Files/Stock_Data/{stock_ticker}/algorithm.json'

    owned_ticker_set = set()
    for file_path in glob.glob(f'{accounts_folder_path}/*/Portfolio/portfolio.csv'):
        if 'simulation' not in file_path:
            with open(file_path, 'r') as portfolio_file:
                for index, line in enumerate(portfolio_file):
                    if index > 0:
                        owned_ticker_set.add(line.split(',')[1])

    current_date = program_start_time

    try:
        research_list = []
        algorithm_value_list = []

        with open(long_term_research_file_path, 'r') as research_file:
            for index, line in enumerate(research_file):
                if index > 0:
                    data_list = line.replace('\n', '').split(',')

                    end_date = datetime.strptime(data_list[1], '%Y-%m-%d')
                    research_algorithm_value = float(data_list[2])

                    time_percentage = (current_date - end_date).days / 300

                    algorithm_value = round(research_algorithm_value - time_percentage, 4)

                    if algorithm_value not in algorithm_value_list:
                        research_list.append([data_list, algorithm_value])
                        algorithm_value_list.append(algorithm_value)

        research_list.sort(key=lambda x: x[1], reverse=True)

        top_algorithm = research_list[0][0]
        top_algorithm_value = research_list[0][1]

        try:
            with open(top_algorithm_file_path, 'r') as json_dict:
                top_algorithm_dict = json.load(json_dict)

            current_top_algorithm_value = top_algorithm_dict['Algorithm_Value']
            current_top_algorithm_date = datetime.strptime(top_algorithm_dict['Algorithm_Date'], '%Y-%m-%d')

            time_percentage = (current_date - current_top_algorithm_date).days / 300

            current_top_algorithm_value = round(current_top_algorithm_value - time_percentage, 4)

        except (KeyError, FileNotFoundError):
            current_top_algorithm_value = 0

        if stock_ticker not in owned_ticker_set:

            if top_algorithm_value > current_top_algorithm_value:
                with open(top_algorithm_file_path, 'w') as top_algorithm_file:
                    top_algorithm_file.write(f'{"{"}\n')
                    top_algorithm_file.write(f'  "Past_Periods": {top_algorithm[15]},\n')
                    top_algorithm_file.write\
                        ('  "Indicator_List": [' + str(top_algorithm[16].split("/")).replace("'", '"')[1:-1] + '],\n')
                    top_algorithm_file.write(f'  "Indicator_Strength": {top_algorithm[17]},\n')
                    top_algorithm_file.write(f'  "Buy_Pattern": "{top_algorithm[18]}",\n')
                    top_algorithm_file.write(f'  "Sell_Pattern": "{top_algorithm[19]}",\n')
                    top_algorithm_file.write(f'  "Sell_Profit": {top_algorithm[20]},\n')
                    top_algorithm_file.write(f'  "Sell_Loss": {top_algorithm[21]},\n')
                    top_algorithm_file.write(f'\n')
                    top_algorithm_file.write(f'  "Algorithm_Value": {top_algorithm[2]},\n')
                    top_algorithm_file.write(f'  "Algorithm_Date": "{top_algorithm[1]}"\n')
                    top_algorithm_file.write(f'{"}"}\n')

                write_to_log_file(title='NEW ALGORITHM',
                                  message=f'/.../{stock_ticker}/algorithm.json has been updated.')

        else:
            write_to_log_file(title='ALGORITHM PAUSE',
                              message=f'/.../{stock_ticker}/algorithm.json update paused due to stock ownership.')

    except FileNotFoundError:
        pass
