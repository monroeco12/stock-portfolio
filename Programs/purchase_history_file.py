from Programs.investment_taxes import retrieve_tax_rate_dictionary
from termcolor import colored


def retrieve_purchase_history_dictionary(user_name):
    purchase_history_file_path = f'Files/Accounts/{user_name}/Purchase_History/purchase_history.csv'

    purchase_history_dict = {}
    with open(purchase_history_file_path, 'r') as purchase_history_file:
        for index, line in enumerate(purchase_history_file):
            data_list = line.replace('\n', '').split(',')

            if index > 0:
                transaction_type = data_list[1]
                if transaction_type != 'DIV':

                    stock_ticker = data_list[2]
                    if stock_ticker not in purchase_history_dict:
                        purchase_history_dict[stock_ticker] = [data_list[:2] + data_list[3:]]
                    else:
                        purchase_history_dict[stock_ticker].append(data_list[:2] + data_list[3:])

    return purchase_history_dict


def update_purchase_history_file(purchase_history_file_path, execution_dict):
    with open(purchase_history_file_path, 'a') as purchase_history_file:

        for transaction_type in execution_dict:
            for stock_ticker in execution_dict[transaction_type]:
                ticker_dict = execution_dict[transaction_type][stock_ticker]

                if transaction_type == 'SELL':
                    if ticker_dict['Investment'] != 'PENDING_SELL':
                        purchase_history_file.write(f'{ticker_dict["Date"]},'
                                                    f'{transaction_type},'
                                                    f'{ticker_dict["Ticker"]},'
                                                    f'{ticker_dict["Shares"]},'
                                                    f'{ticker_dict["Price"]},'
                                                    f'{ticker_dict["Investment"]},'
                                                    f'{ticker_dict["Tax_Type"]}\n')

                if transaction_type == 'BUY':
                    if ticker_dict['Investment'] != 'PENDING_BUY':
                        purchase_history_file.write(f'{ticker_dict["Date"]},'
                                                    f'{transaction_type},'
                                                    f'{ticker_dict["Ticker"]},'
                                                    f'{ticker_dict["Shares"]},'
                                                    f'{ticker_dict["Price"]},'
                                                    f'{ticker_dict["Investment"]},'
                                                    f'--\n')

                if transaction_type == 'DIV':
                    purchase_history_file.write(f'{ticker_dict["Date"]},'
                                                f'{transaction_type},'
                                                f'{ticker_dict["Ticker"]},'
                                                f'{ticker_dict["Shares"]},'
                                                f'{ticker_dict["Price"]},'
                                                f'{ticker_dict["Investment"]},'
                                                f'{ticker_dict["Tax_Type"]}\n')


def calculate_program_performance(user_name):
    purchase_history_file_path = f'Files/Accounts/{user_name}/Purchase_History/purchase_history.csv'

    performance_dict = {}
    with open(purchase_history_file_path, 'r') as purchase_history_file:
        purchase_count, sell_count, div_count = 0, 0, 0
        for index, line in enumerate(purchase_history_file):
            if index > 0:
                data_list = line.replace('\n', '').split(',')

                current_year = data_list[0].split('-')[0]
                transaction_type = data_list[1]
                stock_ticker = data_list[2]
                investment = float(data_list[5])
                tax_type = data_list[6]

                if current_year not in performance_dict:
                    performance_dict[current_year] = {'Holding': {},
                                                      'Total_Profit': [],
                                                      'Stocks':
                                                          {'Long-Term': {'Profit': [], 'Loss': []},
                                                           'Short-Term': {'Profit': [], 'Loss': []}},
                                                      'Dividends':
                                                          {'Qualified': {'Profit': []},
                                                           'Ordinary': {'Profit': []}}}

                if transaction_type == 'BUY':
                    performance_dict[current_year]['Holding'][stock_ticker] = investment

                    purchase_count += 1

                if transaction_type == 'SELL':
                    purchase_year = current_year

                    year_found = False
                    while year_found is False:
                        try:
                            sale_profit = investment - performance_dict[purchase_year]['Holding'][stock_ticker]

                            performance_dict[current_year]['Total_Profit'].append(sale_profit)
                            if sale_profit >= 0:
                                performance_dict[current_year]['Stocks'][tax_type]['Profit'].append(sale_profit)
                            else:
                                performance_dict[current_year]['Stocks'][tax_type]['Loss'].append(sale_profit)

                            performance_dict[purchase_year]['Holding'].pop(stock_ticker)

                            year_found = True
                        except KeyError:
                            purchase_year = str(int(purchase_year) - 1)

                    sell_count += 1

                if transaction_type == 'DIV':
                    performance_dict[current_year]['Total_Profit'].append(investment)
                    performance_dict[current_year]['Dividends'][tax_type]['Profit'].append(investment)

                    div_count += 1

    tax_rate_dict = retrieve_tax_rate_dictionary()

    if user_name != 'simulation' and purchase_count > 0:
        print(f'\n\t{"ACCOUNT PERFORMANCE":25}:', end='')

    total_taxes = 0
    total_income = []
    total_investing = 0
    for year in performance_dict:
        taxes = 0

        income = sum(performance_dict[year]['Total_Profit'])
        investing = sum([i for i in performance_dict[year]['Holding'].values()])

        if income >= 0:
            for tax_type in ['CA', 'Net']:
                for rate in tax_rate_dict[tax_type]:
                    # Retrieve the income range for the rate
                    lower_limit = tax_rate_dict[tax_type][rate][0]
                    upper_limit = tax_rate_dict[tax_type][rate][1]
                    if income > upper_limit:
                        taxable_amount = upper_limit - lower_limit
                    elif lower_limit <= income <= upper_limit:
                        taxable_amount = income - lower_limit
                    else:
                        taxable_amount = 0
                    taxes += (taxable_amount * rate)

            stock_dict = performance_dict[year]['Stocks']

            offset_overflow = {}
            for tax_type in stock_dict:
                profit = sum(stock_dict[tax_type]['Profit'])
                loss = sum(stock_dict[tax_type]['Loss'])
                net_profit = profit + loss
                offset_overflow[tax_type] = {'Net_Profit': net_profit, 'Offset': 0}
                if net_profit < 0:
                    offset_overflow[tax_type]['Offset'] = net_profit

            for tax_type in stock_dict:
                net_profit = offset_overflow[tax_type]['Net_Profit']

                if net_profit >= 0:
                    # Adjust the net profit with losses from other tax types
                    for key in offset_overflow:
                        if key != tax_type:
                            net_profit += offset_overflow[key]['Offset']

                    for rate in tax_rate_dict[tax_type]:
                        # Retrieve the income range for the rate
                        lower_limit = tax_rate_dict[tax_type][rate][0]
                        upper_limit = tax_rate_dict[tax_type][rate][1]
                        if lower_limit <= income <= upper_limit:
                            taxes += (net_profit * rate)

            dividend_dict = performance_dict[year]['Dividends']

            for tax_type in dividend_dict:
                profit = sum(dividend_dict[tax_type]['Profit'])

                for rate in tax_rate_dict[tax_type]:
                    # Retrieve the income range for the rate
                    lower_limit = tax_rate_dict[tax_type][rate][0]
                    upper_limit = tax_rate_dict[tax_type][rate][1]
                    if lower_limit <= income <= upper_limit:
                        taxes += (profit * rate)

        total_taxes += taxes
        total_income += performance_dict[year]['Total_Profit']
        total_investing += investing

        if user_name != 'simulation':
            taxes_string = colored(str(round(taxes, 2)), 'red')
            investing_string = str(round(float(investing), 2))
            if income >= 0:
                income_string = colored(str(round(income, 2)), 'green')
            else:
                income_string = colored(str(round(income, 2)), 'red')

            print(f' {year} ['
                  f'Investing: $ {investing_string:12} || '
                  f'Profit: $ {income_string:20} || '
                  f'Taxes: $ {taxes_string:19} ]', end=f'\n\t{"":25} ')

    if user_name == 'simulation':
        results_dict = {'Purchase_Count': purchase_count,
                        'Sell_Count': sell_count,
                        'Div_Count': div_count,
                        'Total_Taxes': total_taxes,
                        'Total_Income': total_income,
                        'Total_Investing': total_investing}

        return results_dict
