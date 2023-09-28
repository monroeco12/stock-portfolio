from datetime import datetime, timedelta
from Programs.algorithm_file import randomize_algorithm, calculate_algorithm_value, save_top_algorithm
from Programs.long_term_research_file import update_long_term_research_file, backup_long_term_research_file
from Programs.portfolio_file import retrieve_stock_portfolio
from Programs.purchase_history_file import retrieve_purchase_history_dictionary, calculate_program_performance
from Programs.stock_executions import execute_stock_recommendations
from Programs.stock_recommendations import retrieve_stock_recommendations
from Programs.user_accounts import overwrite_account_files
from statistics import mean


def run_research(algorithm_dict, date_dict, stock_dict, stock_ticker, program_start_time):
    research_loop_minutes = algorithm_dict['Research_Loop_Minutes']
    simulation_funds = algorithm_dict['Sim_Funds']

    loop_start_time = datetime.now()
    loop_end_time = loop_start_time + timedelta(minutes=research_loop_minutes)
    while loop_start_time < loop_end_time:
        randomize_algorithm(algorithm_dict=algorithm_dict)

        algorithm_value_dict = {'Initial_Research': [], 'Back_Test_Research': [], 'Results': {}}

        for key in ['Initial_Research', 'Back_Test_Research']:
            for date_list in date_dict[key]:
                overwrite_account_files(user_name='simulation',
                                        account_funds=simulation_funds)

                for date in date_list:
                    portfolio_dict = retrieve_stock_portfolio(user_name='simulation')
                    purchase_history_dict = retrieve_purchase_history_dictionary(user_name='simulation')

                    recommendation_dict = retrieve_stock_recommendations(is_simulation="TRUE",
                                                                         algorithm_dict=algorithm_dict,
                                                                         stock_dict=stock_dict,
                                                                         portfolio_dict=portfolio_dict,
                                                                         purchase_history_dict=purchase_history_dict,
                                                                         current_date=date)

                    execute_stock_recommendations(is_simulation="TRUE",
                                                  user_name='simulation',
                                                  algorithm_dict=algorithm_dict,
                                                  stock_dict=stock_dict,
                                                  portfolio_dict=portfolio_dict,
                                                  purchase_history_dict=purchase_history_dict,
                                                  recommendation_dict=recommendation_dict,
                                                  current_date=date)

                results_dict = calculate_program_performance(user_name='simulation')
                if key == 'Initial_Research':
                    algorithm_value_dict['Results'] = results_dict

                algorithm_value = calculate_algorithm_value(purchase_count=results_dict['Purchase_Count'],
                                                            sell_count=results_dict['Sell_Count'],
                                                            income=results_dict['Total_Income'],
                                                            funds=simulation_funds)

                algorithm_value_dict[key].append(algorithm_value)

        if len(algorithm_value_dict['Back_Test_Research']) != 0:
            initial_sum = sum(algorithm_value_dict['Initial_Research'])
            back_test_mean = mean(algorithm_value_dict['Back_Test_Research'])
            true_algorithm_value = round(initial_sum + back_test_mean, 4)
        else:
            initial_sum = sum(algorithm_value_dict['Initial_Research'])
            true_algorithm_value = round(initial_sum, 4)

        update_long_term_research_file(algorithm_dict=algorithm_dict,
                                       stock_ticker=stock_ticker,
                                       start_date=date_dict['Initial_Research'][0][0],
                                       end_date=date_dict['Initial_Research'][0][-1],
                                       algorithm_value=true_algorithm_value,
                                       total_income=algorithm_value_dict['Results']['Total_Income'],
                                       total_investing=algorithm_value_dict['Results']['Total_Investing'],
                                       total_taxes=algorithm_value_dict['Results']['Total_Taxes'],
                                       purchase_count=algorithm_value_dict['Results']['Purchase_Count'],
                                       sell_count=algorithm_value_dict['Results']['Sell_Count'],
                                       div_count=algorithm_value_dict['Results']['Div_Count'])

        loop_start_time = datetime.now()

    save_top_algorithm(stock_ticker=stock_ticker,
                       program_start_time=program_start_time)

    backup_long_term_research_file(stock_ticker=stock_ticker)
