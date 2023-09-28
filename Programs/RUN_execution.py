from datetime import datetime
import json
from Programs.portfolio_file import retrieve_stock_portfolio
from Programs.purchase_history_file import retrieve_purchase_history_dictionary
from Programs.stock_recommendations import retrieve_stock_recommendations


def run_execution(is_simulation, user_name, stock_ticker, algorithm_dict, stock_dict,
                  recommendation_dict, program_start_time):

    if is_simulation == "FALSE":
        top_algorithm_file_path = f'Files/Stock_Data/{stock_ticker}/algorithm.json'

        continue_on = True

        try:
            with open(top_algorithm_file_path, 'r') as json_dict:
                top_algorithm_dict = json.load(json_dict)

            for key in top_algorithm_dict:
                algorithm_dict[key] = top_algorithm_dict[key]

        except FileNotFoundError:
            continue_on = False

        if continue_on is True:
            portfolio_dict = retrieve_stock_portfolio(user_name=user_name)
            purchase_history_dict = retrieve_purchase_history_dictionary(user_name=user_name)

            recommendation = retrieve_stock_recommendations(is_simulation=is_simulation,
                                                            algorithm_dict=algorithm_dict,
                                                            stock_dict=stock_dict,
                                                            portfolio_dict=portfolio_dict,
                                                            purchase_history_dict=purchase_history_dict,
                                                            current_date=program_start_time)

            algorithm_value = top_algorithm_dict['Algorithm_Value']
            algorithm_date = datetime.strptime(top_algorithm_dict['Algorithm_Date'], '%Y-%m-%d')

            time_percentage = (program_start_time - algorithm_date).days / 300

            algorithm_value = round(algorithm_value - time_percentage, 4)

            for key in recommendation:
                for ticker in recommendation[key]:
                    recommendation_dict[key][ticker] = \
                        recommendation[key][ticker] + [algorithm_value]
