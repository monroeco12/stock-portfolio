from datetime import datetime
import glob
import os
import pathlib
from Programs.log_file import write_to_log_file
from statistics import mean, median


def update_long_term_research_file(algorithm_dict, stock_ticker, start_date, end_date, algorithm_value,
                                   total_income, total_investing, total_taxes, purchase_count,
                                   sell_count, div_count):

    long_term_research_folder_path = f'Files/Stock_Data/{stock_ticker}/Long_Term_Research'

    funds = algorithm_dict['Sim_Funds']

    if len(total_income) != 0:
        income = round(sum(total_income), 2)
        mean_income = round(mean(total_income), 2)
        median_income = round(median(total_income), 2)
    else:
        income = 0
        mean_income = 0
        median_income = 0

    value_list = []
    ignore_list = ['Simulation', 'Sim_Funds', 'Research_Loop_Minutes', 'Algorithm_Value', 'Algorithm_Date']
    for key in algorithm_dict:
        if key not in ignore_list:
            if key in ['Indicator_List']:
                if len(algorithm_dict[key]) != 0:
                    value = '/'.join(algorithm_dict[key])
                else:
                    value = 'N/A'
            else:
                value = algorithm_dict[key]
            value_list.append(str(value))

    algorithm_string = f'{str(start_date).split(" ")[0]},' \
                       f'{str(end_date).split(" ")[0]},' \
                       f'{algorithm_value},' \
                       f'{funds},' \
                       f'{round(total_investing, 2)},' \
                       f'{income},' \
                       f'{round(total_taxes, 2)},' \
                       f'{purchase_count},' \
                       f'{sell_count},' \
                       f'{div_count},' \
                       f'{mean_income},' \
                       f'{median_income},' \
                       f'{",".join(value_list)}\n'

    # Ignore uneventful research
    if purchase_count > 0 and income > 0:
        long_term_research_file_path = f'{long_term_research_folder_path}/long_term_research.csv'

        try:
            with open(long_term_research_file_path, 'a') as long_term_research_file:
                long_term_research_file.write(algorithm_string)

        except FileNotFoundError:
            pathlib.Path(f'{long_term_research_folder_path}/Backups/').mkdir(parents=True, exist_ok=True)

            header = 'Sim_Start_Date,Sim_End_Date,Algorithm_Value,Funds,Investing,Income,Taxes,Purchase_Count,' \
                     'Sell_Count,Div_Count,Average_Income,Median_Income,Back_Test_Count,Research_Range_In_Days,' \
                     'Dataframe_Range_In_Years,Past_Periods,Indicator_List,Indicator_Strength,Buy_Pattern,' \
                     'Sell_Pattern,Sell_Profit,Sell_Loss,Max_Stock_Count,Max_Stock_Percent,Max_Sector_Percent\n'

            with open(long_term_research_file_path, 'a') as long_term_research_file:
                long_term_research_file.write(header)
                long_term_research_file.write(algorithm_string)

            write_to_log_file(title='LONG TERM RESEARCH',
                              message=f'/.../{stock_ticker}/.../long_term_research.csv has been created.')


def backup_long_term_research_file(stock_ticker):
    long_term_research_folder_path = f'Files/Stock_Data/{stock_ticker}/Long_Term_Research'
    backups_folder_path = f'{long_term_research_folder_path}/Backups'
    long_term_research_file_path = f'{long_term_research_folder_path}/long_term_research.csv'

    try:
        backup_file_path = f'{backups_folder_path}/{str(datetime.now().replace(microsecond=0)).replace(" ", "_")}.csv'

        backup_file = open(backup_file_path, 'w')
        with open(long_term_research_file_path, 'r') as long_term_research_file:
            for line in long_term_research_file:
                backup_file.write(line)
        backup_file.close()

        file_paths_list = sorted(glob.glob(backups_folder_path + '/*.csv'), reverse=True)

        for index, file_path in enumerate(file_paths_list):
            if index > 9:
                os.remove(file_path)

        write_to_log_file(title='RESEARCH BACKUP',
                          message=f'{stock_ticker} long term research backups have been updated.')

    except FileNotFoundError:
        pass
