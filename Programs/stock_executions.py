from datetime import datetime
from Programs.investment_taxes import retrieve_stock_tax_type, retrieve_dividend_tax_type
from Programs.portfolio_file import update_portfolio_file
from Programs.print_styles import print_stock_recommendations
from Programs.purchase_history_file import update_purchase_history_file


accounts_folder_path = 'Files/Accounts'


def execute_sell_recommendations(is_simulation, recommendation_dict, portfolio_dict, execution_dict,
                                 portfolio_data_list, current_date):

    for stock_ticker in recommendation_dict:
        next_open_price = recommendation_dict[stock_ticker][1]
        shares = float(portfolio_dict[stock_ticker]['Shares'])

        if is_simulation == "TRUE":
            transaction = round(shares * next_open_price, 4)
            tax_type = retrieve_stock_tax_type(is_simulation=is_simulation,
                                               portfolio_data_list=portfolio_data_list,
                                               stock_ticker=stock_ticker,
                                               sell_date=current_date)
        else:
            transaction = 0.00
            tax_type = 'N/A'

        execution_dict['SELL'][stock_ticker] = {'Date': str(current_date).split(' ')[0],
                                                'Ticker': stock_ticker,
                                                'Shares': shares,
                                                'Price': next_open_price,
                                                'Investment': transaction,
                                                'Tax_Type': tax_type}


def calculate_max_investment(buy_count, stock_limit, max_stock_percent, available_funds, total_funds):
    max_dollar = 0
    max_percent = 0
    if buy_count != 0 and stock_limit != 0:
        if buy_count < stock_limit:
            max_dollar = available_funds // buy_count
        else:
            max_dollar = available_funds // stock_limit

        max_percent = max_stock_percent * total_funds

    if max_dollar < max_percent:
        return max_dollar
    else:
        return max_percent


def create_sector_limit_dictionary(buy_count, stock_limit, max_sector_percent, portfolio_dict, execution_dict):
    sector_limit_dict = {}
    if buy_count != 0 and stock_limit != 0:
        current_sectors = [portfolio_dict[i]['Sector'] for i in portfolio_dict
                           if i not in ['Available_Funds', '--']
                           and i not in execution_dict['SELL']]

        for sector in current_sectors:
            if sector not in sector_limit_dict:
                initial_percent = current_sectors.count(sector) / (len(current_sectors) + stock_limit)

                stock_count = 0
                if initial_percent < max_sector_percent:
                    continue_on = True
                    while continue_on is True:
                        stock_count += 1
                        new_percent = \
                            (current_sectors.count(sector) + stock_count) / (len(current_sectors) + stock_limit)
                        if new_percent > max_sector_percent:
                            continue_on = False
                            stock_count -= 1
                        if new_percent == max_sector_percent:
                            continue_on = False

                sector_limit_dict[sector] = stock_count

    return sector_limit_dict


def execute_buy_recommendations(is_simulation, algorithm_dict, stock_dict, recommendation_dict, portfolio_dict,
                                execution_dict, available_funds, total_funds, current_date):

    max_stock_count = algorithm_dict['Max_Stock_Count']
    max_stock_percent = algorithm_dict['Max_Stock_Percent']
    max_sector_percent = algorithm_dict['Max_Sector_Percent']

    stock_limit = (max_stock_count - (len(portfolio_dict) - 2)) + len(execution_dict['SELL'])
    unknown_sector_limit = int((stock_limit + (len(portfolio_dict) - 2)) * max_sector_percent)

    max_investment = calculate_max_investment(buy_count=len(recommendation_dict),
                                              stock_limit=stock_limit,
                                              max_stock_percent=max_stock_percent,
                                              available_funds=available_funds,
                                              total_funds=total_funds)

    sector_limit_dict = create_sector_limit_dictionary(buy_count=len(recommendation_dict),
                                                       stock_limit=stock_limit,
                                                       max_sector_percent=max_sector_percent,
                                                       portfolio_dict=portfolio_dict,
                                                       execution_dict=execution_dict)

    approved_stocks = []
    for stock_ticker in recommendation_dict:
        next_open_price = recommendation_dict[stock_ticker][1]

        if len(approved_stocks) < stock_limit:
            sector = stock_dict[stock_ticker]['Sector']
            if sector not in sector_limit_dict:
                sector_limit_dict[sector] = unknown_sector_limit

            if sector_limit_dict[sector] > 0:

                shares = round(max_investment / next_open_price, 4)
                investment = round(max_investment, 4)

                if investment >= 1 and shares > 0:

                    if is_simulation == "FALSE":
                        investment = 0.00

                    execution_dict['BUY'][stock_ticker] = {'Date': str(current_date).split(' ')[0],
                                                           'Ticker': stock_ticker,
                                                           'Sector': sector,
                                                           'Industry': stock_dict[stock_ticker]['Industry'],
                                                           'Shares': shares,
                                                           'Price': next_open_price,
                                                           'Investment': investment}

                    approved_stocks.append(stock_ticker)
                    sector_limit_dict[sector] -= 1


def acquire_dividends(stock_dict, purchase_history_dict, execution_dict, current_date):
    for stock_ticker in purchase_history_dict:
        payment_dates_list = list(stock_dict[stock_ticker]['Dividends']['Payment_Dates'])

        if current_date in payment_dates_list:
            ex_date = stock_dict[stock_ticker]['Dividends']['Payment_Dates'][current_date][0]
            amount = stock_dict[stock_ticker]['Dividends']['Payment_Dates'][current_date][2]

            transaction_list = purchase_history_dict[stock_ticker]

            total_shares = 0
            date_acquired = ''
            date_sold = ''
            for transaction in transaction_list:
                if date_acquired == '' or date_sold == '':
                    transaction_date = datetime.strptime(transaction[0], '%Y-%m-%d')
                    transaction_type = transaction[1]
                    shares = float(transaction[2])

                    if transaction_date < ex_date and transaction_type == 'BUY':
                        total_shares += shares
                        date_acquired = transaction_date

                    if transaction_date < ex_date and transaction_type == 'SELL':
                        total_shares -= shares
                        date_acquired = ''

                    if transaction_date >= ex_date and transaction_type == 'SELL':
                        date_sold = transaction_date

            if total_shares != 0:
                tax_type = retrieve_dividend_tax_type(date_acquired=date_acquired,
                                                      date_sold=date_sold,
                                                      current_date=current_date,
                                                      ex_date=ex_date)

                dividend_amount = round(amount * total_shares, 4)

                execution_dict['DIV'][stock_ticker] = {'Date': str(current_date).split(' ')[0],
                                                       'Ticker': stock_ticker,
                                                       'Shares': total_shares,
                                                       'Price': amount,
                                                       'Investment': dividend_amount,
                                                       'Tax_Type': tax_type}


def update_available_funds(execution_dict, available_funds):
    sell_amount = sum([float(execution_dict['SELL'][i]['Investment']) for i in execution_dict['SELL']])
    buy_amount = sum([float(execution_dict['BUY'][i]['Investment']) for i in execution_dict['BUY']])
    div_amount = sum([float(execution_dict['DIV'][i]['Investment']) for i in execution_dict['DIV']])

    available_funds = round((available_funds + sell_amount + div_amount) - buy_amount, 4)

    return available_funds


def execute_stock_recommendations(is_simulation, user_name, algorithm_dict, stock_dict, portfolio_dict,
                                  purchase_history_dict, recommendation_dict, current_date):

    portfolio_file_path = f'{accounts_folder_path}/{user_name}/Portfolio/portfolio.csv'
    purchase_history_file_path = f'{accounts_folder_path}/{user_name}/Purchase_History/purchase_history.csv'

    with open(portfolio_file_path, 'r') as portfolio_file:
        portfolio_data_list = [line.replace('\n', '').split(',') for line in portfolio_file]

    available_funds = float(portfolio_dict['Available_Funds'])

    total_funds = available_funds + sum([float(portfolio_dict[i]['Investment']) for i in portfolio_dict
                                         if i not in ['Available_Funds', '--']])

    execution_dict = {'SELL': {}, 'BUY': {}, 'DIV': {}}
    execute_sell_recommendations(is_simulation=is_simulation,
                                 recommendation_dict=recommendation_dict['SELL'],
                                 portfolio_dict=portfolio_dict,
                                 execution_dict=execution_dict,
                                 portfolio_data_list=portfolio_data_list,
                                 current_date=current_date)

    execute_buy_recommendations(is_simulation=is_simulation,
                                algorithm_dict=algorithm_dict,
                                stock_dict=stock_dict,
                                recommendation_dict=recommendation_dict['BUY'],
                                portfolio_dict=portfolio_dict,
                                execution_dict=execution_dict,
                                available_funds=available_funds,
                                total_funds=total_funds,
                                current_date=current_date)

    acquire_dividends(stock_dict=stock_dict,
                      purchase_history_dict=purchase_history_dict,
                      execution_dict=execution_dict,
                      current_date=current_date)

    available_funds = update_available_funds(execution_dict=execution_dict,
                                             available_funds=available_funds)

    update_portfolio_file(portfolio_file_path=portfolio_file_path,
                          portfolio_data_list=portfolio_data_list,
                          execution_dict=execution_dict,
                          available_funds=available_funds)

    update_purchase_history_file(purchase_history_file_path=purchase_history_file_path,
                                 execution_dict=execution_dict)

    print_stock_recommendations(is_simulation=is_simulation,
                                execution_dict=execution_dict)
