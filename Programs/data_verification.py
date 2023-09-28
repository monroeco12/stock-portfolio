from datetime import datetime
import glob
import numpy as np
import pandas as pd
from Programs.log_file import write_to_log_file
from Programs.print_styles import print_error_message, print_progress_bar
from Programs.timestamps_file import check_timestamps_file


stock_data_folder_path = 'Files/Stock_Data'


def verify_historical_data(csv_file_path, stock_ticker, current_date, incomplete_data_set):
    dataframe = pd.read_csv(csv_file_path, keep_default_na=False)

    if (dataframe.iloc[-1]['date'] == datetime.strftime(current_date, '%Y-%m-%d')) is True:

        pre_length = len(dataframe)
        dataframe = dataframe.drop_duplicates()
        post_length = len(dataframe)

        unique_dates = dataframe['date'].is_unique
        if unique_dates is False:
            print_error_message(error='UNEXPECTED DATA',
                                message=f'Duplicate dates found in /.../{stock_ticker}/.../historical_data.csv')

        value_comparison = np.where(dataframe['high'] >= dataframe['low'], "True", "False")
        if "False" in value_comparison:
            value_location = str(np.argwhere(value_comparison == "False")[0][0] + 2)
            print_error_message(error='UNEXPECTED DATA',
                                message=f'Incorrect low data at line {value_location} in '
                                        f'/.../{stock_ticker}/.../historical_data.csv')

        in_order = dataframe['date'].is_monotonic_increasing

        if in_order is False or pre_length != post_length:
            dataframe = dataframe.sort_values(by=['date'])
            dataframe.to_csv(csv_file_path, index=False)

            write_to_log_file(title='HISTORICAL DATA FILE',
                              message=f'/.../{stock_ticker}/.../historical_data.csv has been verified and edited.')
    else:
        incomplete_data_set.add(stock_ticker)


def verify_dividend_data(csv_file_path, stock_ticker):
    dataframe = pd.read_csv(csv_file_path, keep_default_na=False)

    in_order = dataframe['Payment_Date'].is_monotonic_increasing

    if in_order is False:
        dataframe = dataframe.sort_values(by=['Payment_Date'])
        dataframe.to_csv(csv_file_path, index=False)

        write_to_log_file(title='DIVIDEND DATA FILE',
                          message=f'/.../{stock_ticker}/.../dividend_data.csv has been verified and edited.')


def verify_earnings_data(csv_file_path, stock_ticker):
    dataframe = pd.read_csv(csv_file_path, keep_default_na=False)

    pre_length = len(dataframe)
    dataframe = dataframe.drop_duplicates()
    post_length = len(dataframe)

    unique_dates = dataframe['Fiscal_Quarter_End'].is_unique
    if unique_dates is False:
        print_error_message(error='UNEXPECTED DATA',
                            message=f'Duplicate dates found in /.../{stock_ticker}/.../earnings_data.csv')

    value_comparison = np.where(dataframe['Date_Reported'] >= dataframe['Fiscal_Quarter_End'], "True", "False")
    if "False" in value_comparison:
        value_location = str(np.argwhere(value_comparison == "False")[0][0] + 2)
        print_error_message(error='UNEXPECTED DATA',
                            message=f'Incorrect date data found at line {value_location} in '
                                    f'/.../{stock_ticker}/.../earnings_data.csv')

    edited_df = \
        dataframe[['Earnings_Per_Share', 'Earnings_Per_Share_Forecast', 'Percent_Surprise']][
            (dataframe['Earnings_Per_Share'] != 'N/A') &
            (dataframe['Earnings_Per_Share_Forecast'] != 'N/A') &
            (dataframe['Percent_Surprise'] != 'N/A')].astype(float)

    value_comparison = np.where(
        ((edited_df['Earnings_Per_Share'] >= edited_df['Earnings_Per_Share_Forecast'])
            & (edited_df['Percent_Surprise'] >= 0)) |
        ((edited_df['Earnings_Per_Share'] < edited_df['Earnings_Per_Share_Forecast'])
            & (edited_df['Percent_Surprise'] < 0)), "True", "False")
    if "False" in value_comparison:
        value_location = str(np.argwhere(value_comparison == "False")[0][0] + (2 + (len(dataframe) - len(edited_df))))
        print_error_message(error='UNEXPECTED DATA',
                            message=f'Incorrect EPS data found at line {value_location} in '
                                    f'/.../{stock_ticker}/.../earnings_data.csv')

    in_order = dataframe['Fiscal_Quarter_End'].is_monotonic_increasing

    if in_order is False or pre_length != post_length:
        dataframe = dataframe.sort_values(by=['Fiscal_Quarter_End'])
        dataframe.to_csv(csv_file_path, index=False)

        write_to_log_file(title='EARNINGS DATA FILE',
                          message=f'/.../{stock_ticker}/.../earnings_data.csv has been verified and edited.')


def verify_summary_data(csv_file_path, stock_ticker):
    with open(csv_file_path, 'r') as summary_data_file:
        if len(tuple(summary_data_file)) == 1:
            write_to_log_file(title='SUMMARY DATA FILE',
                              message=f'/.../{stock_ticker}/.../summary_data.csv was not scraped.')


def verify_scraped_data(stock_ticker, current_date, data_count, data_length):
    continue_on = check_timestamps_file(file_name=f'verify_{stock_ticker}_data.py',
                                        program_start_time=current_date)

    if continue_on is True:
        file_path_list = glob.glob(f'{stock_data_folder_path}/{stock_ticker}/*/*.csv')

        incomplete_data_set = set()
        for index, csv_file_path in enumerate(file_path_list):

            if 'Historical_Data' in csv_file_path:
                verify_historical_data(csv_file_path=csv_file_path,
                                       stock_ticker=stock_ticker,
                                       current_date=current_date,
                                       incomplete_data_set=incomplete_data_set)

            if 'Dividend_Data' in csv_file_path:
                verify_dividend_data(csv_file_path=csv_file_path,
                                     stock_ticker=stock_ticker)

            if 'Earnings_Data' in csv_file_path:
                verify_earnings_data(csv_file_path=csv_file_path,
                                     stock_ticker=stock_ticker)

            if 'Summary_Data' in csv_file_path:
                verify_summary_data(csv_file_path=csv_file_path,
                                    stock_ticker=stock_ticker)

            print_progress_bar(title=f'VERIFYING {stock_ticker} DATA',
                               index=data_count,
                               data_length=data_length)

        if len(incomplete_data_set) > 0:
            incomplete_data_string = ''.join([f'\n\t{"":25}• {i}' for i in incomplete_data_set])

            print(f'\n\n\t{"":25}+ Please manually scrape data for the following stocks: '
                  f'\n\t{"":25}{incomplete_data_string.lstrip()}')

            print_error_message(error='INCOMPLETE DATA',
                                message='Data was only partially scraped for certain stocks')

        write_to_log_file(title='VERIFIED SCRAPED DATA',
                          message=f'/.../verify_{stock_ticker}_data.py has completed.')
