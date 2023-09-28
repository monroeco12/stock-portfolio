def retrieve_stock_portfolio(user_name):
    portfolio_file_path = f'Files/Accounts/{user_name}/Portfolio/portfolio.csv'

    portfolio_dict = {'Available_Funds': 'N/A'}
    with open(portfolio_file_path, 'r') as portfolio_file:
        header_list = []
        for index, line in enumerate(portfolio_file):
            data_list = line.replace('\n', '').split(',')

            if index == 0:
                header_list = data_list[:-1]
            else:
                stock_ticker = data_list[1]
                portfolio_dict[stock_ticker] = {}
                for i in range(len(header_list)):
                    portfolio_dict[stock_ticker][header_list[i]] = data_list[i]

                portfolio_dict['Available_Funds'] = float(data_list[-1])

    return portfolio_dict


def update_portfolio_file(portfolio_file_path, portfolio_data_list, execution_dict, available_funds):
    with open(portfolio_file_path, 'w') as portfolio_file:
        portfolio_file.write(f'{",".join(portfolio_data_list[0])}\n')

        for data_list in portfolio_data_list[1:]:
            stock_ticker = data_list[1]
            if stock_ticker not in execution_dict['SELL'] and stock_ticker != '--':
                portfolio_file.write(f'{",".join(data_list[:-1])},{str(available_funds)}\n')
            if stock_ticker in execution_dict['SELL'] and execution_dict['SELL'][stock_ticker]['Investment'] == 0.00:
                portfolio_file.write(f'{",".join(data_list[:-1])},{str(available_funds)}\n')

        for stock_ticker in execution_dict['BUY']:
            ticker_dict = execution_dict['BUY'][stock_ticker]
            if ticker_dict['Investment'] == 0.00:
                ticker_dict['Investment'] = 'PENDING_BUY'

            for key in ticker_dict:
                portfolio_file.write(f'{str(ticker_dict[key])},')
            portfolio_file.write(f'{str(available_funds)}\n')

        for stock_ticker in execution_dict['SELL']:
            ticker_dict = execution_dict['SELL'][stock_ticker]
            if ticker_dict['Investment'] == 0.00:
                ticker_dict['Investment'] = 'PENDING_SELL'

                portfolio_file.write(f'{str(ticker_dict["Date"])},'
                                     f'{str(ticker_dict["Ticker"])},--,--,'
                                     f'{str(ticker_dict["Shares"])},'
                                     f'{str(ticker_dict["Price"])},'
                                     f'{str(ticker_dict["Investment"])},'
                                     f'{str(available_funds)}\n')

        portfolio_file.write(f'--,--,--,--,--,--,--,{str(available_funds)}\n')
