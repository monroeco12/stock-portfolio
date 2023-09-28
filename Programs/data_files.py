from datetime import datetime


def retrieve_sector_and_industry(stock_ticker, stock_dict):
    summary_data_file_path = f'Files/Stock_Data/{stock_ticker}/Summary_Data/summary_data.csv'

    summary_data_file = open(summary_data_file_path, 'r')
    summary_data_list = summary_data_file.readlines()[-1].split(',')
    summary_data_file.close()

    stock_dict[stock_ticker]['Sector'] = summary_data_list[1]
    stock_dict[stock_ticker]['Industry'] = summary_data_list[2]


def retrieve_stock_dividends(stock_ticker, stock_dict):
    dividend_data_file_path = f'Files/Stock_Data/{stock_ticker}/Dividend_Data/dividend_data.csv'

    stock_dict[stock_ticker]['Dividends'] = {'Ex_Dates': {}, 'Payment_Dates': {}}

    with open(dividend_data_file_path, 'r') as dividend_data_file:
        for index, line in enumerate(dividend_data_file):
            if index > 0:
                data_list = line.replace('\n', '').split(',')

                payment_date = datetime.strptime(data_list[0], '%Y-%m-%d')
                ex_date = data_list[2]
                record_date = data_list[3]
                amount = float(data_list[4])

                if ex_date != 'N/A' and record_date != 'N/A':
                    ex_date = datetime.strptime(ex_date, '%Y-%m-%d')
                    record_date = datetime.strptime(record_date, '%Y-%m-%d')

                    if ex_date < record_date < payment_date:
                        stock_dict[stock_ticker]['Dividends']['Ex_Dates'][ex_date] = \
                            [payment_date, record_date]
                        stock_dict[stock_ticker]['Dividends']['Payment_Dates'][payment_date] = \
                            [ex_date, record_date, amount]


def retrieve_earnings_dates(stock_ticker, stock_dict):
    earnings_data_file_path = f'Files/Stock_Data/{stock_ticker}/Earnings_Data/earnings_data.csv'

    stock_dict[stock_ticker]['Earnings'] = {'Report_Dates': {}}

    with open(earnings_data_file_path, 'r') as earnings_data_file:
        for index, line in enumerate(earnings_data_file):
            if index > 0:
                data_list = line.replace('\n', '').split(',')

                date_reported = data_list[1]
                next_announcement_date = data_list[5]

                if date_reported != 'N/A':
                    date_reported = datetime.strptime(date_reported, '%Y-%m-%d')
                    stock_dict[stock_ticker]['Earnings']['Report_Dates'][date_reported] = ''

                if next_announcement_date != 'N/A':
                    next_announcement_date = datetime.strptime(next_announcement_date, '%Y-%m-%d')
                    stock_dict[stock_ticker]['Earnings']['Report_Dates'][next_announcement_date] = ''
