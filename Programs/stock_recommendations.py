from datetime import datetime, timedelta
import numpy as np
import scipy
from statistics import median


def determine_trend_line(index_array, data_array):
    x = index_array
    y = data_array

    # Calculate the linear regression of the x and y data
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)

    linear_regression_list = intercept + (slope * x)

    if linear_regression_list[0] != 0:
        percent_change = \
            (linear_regression_list[-1] - linear_regression_list[0]) / abs(linear_regression_list[0])
    else:
        percent_change = 0

    # Avoid value errors
    if percent_change == float('inf') or percent_change == float('-inf') or str(percent_change) == 'nan':
        percent_change = 0

    # Determine if the trend line is increasing or decreasing
    if percent_change > 0:
        return ['I', percent_change]
    elif percent_change < 0:
        return ['D', percent_change]
    else:
        return ['S', percent_change]


def make_signal_determination(algorithm_dict, is_simulation, csv_dataframe, current_date,
                              pattern, holding_stock, last_purchase_price):

    market_open = True
    if current_date not in csv_dataframe['date'].tolist() and is_simulation == "TRUE":
        market_open = False

    if market_open is True:

        if is_simulation == "TRUE":
            next_open_price = float(csv_dataframe[csv_dataframe['date'] == current_date]['open'])
            csv_dataframe = csv_dataframe[csv_dataframe['date'] < current_date]
        else:
            next_open_price = 'N/A'

        recent_close_price = csv_dataframe['close'].iloc[-1]

        past_periods = algorithm_dict['Past_Periods']
        indicator_list = algorithm_dict['Indicator_List']
        indicator_strength = algorithm_dict['Indicator_Strength']
        sell_profit = algorithm_dict['Sell_Profit']
        sell_loss = algorithm_dict['Sell_Loss']

        index_array = np.arange(0, past_periods)
        close_array = csv_dataframe['close'].to_numpy()

        close_trend = determine_trend_line(index_array=index_array,
                                           data_array=close_array[-past_periods:])

        trend_line = [close_trend[0]]
        trend_strength = []
        for indicator in indicator_list:
            indicator_trend = determine_trend_line(index_array=index_array,
                                                   data_array=csv_dataframe[indicator].to_numpy()[-past_periods:])
            trend_line.append(indicator_trend[0])
            trend_strength.append(abs(close_trend[1] - indicator_trend[1]))

        trend_line_string = f'{"/".join(trend_line)}/{str(round(median(trend_strength)))}'

        stock_percent_change = 0
        if holding_stock is True:
            stock_percent_change = \
                round((recent_close_price - last_purchase_price) / last_purchase_price, 3)

        buy_pattern_string = f'{pattern.split("+")[0]}/{str(indicator_strength)}'
        sell_pattern_string = f'{pattern.split("+")[1]}/{str(indicator_strength)}'

        signal = 'N/A'
        if buy_pattern_string == trend_line_string:
            signal = 'BUY'

        if stock_percent_change >= sell_profit \
                or stock_percent_change <= sell_loss \
                or sell_pattern_string == trend_line_string:
            signal = 'SELL'

        # Update the inferred next open price if not running a simulation
        if is_simulation != "TRUE":
            next_open_price = recent_close_price

        return [signal, next_open_price]

    else:
        return ['CLOSED', 'CLOSED']


def wash_sale_check(is_simulation, signal, stock_ticker, purchase_history_dict, current_date):
    wait_for_wash_sales = False

    if signal == 'BUY' and stock_ticker in purchase_history_dict:
        # Adjust the current date for simulation accuracy
        if is_simulation == "TRUE":
            current_date -= timedelta(days=1)

        # Retrieve the stock's most recent buy and sell transactions
        transaction_list = purchase_history_dict[stock_ticker][-2:]

        # If there was a complete transaction, continue
        if len(transaction_list) == 2:
            buy_check = transaction_list[0][1]
            sell_check = transaction_list[-1][1]

            if buy_check == 'BUY' and sell_check == 'SELL':
                buy_investment = float(transaction_list[0][4])
                sell_investment = float(transaction_list[-1][4])

                wash_sale_prevention_days = 35
                sell_date = datetime.strptime(transaction_list[-1][0], '%Y-%m-%d')
                # If the investment was net negative, continue
                if sell_investment < buy_investment:
                    # If the sell date happened within the wash sale prevention limit, continue
                    if (current_date - timedelta(days=wash_sale_prevention_days)) < sell_date:
                        wait_for_wash_sales = True

    return wait_for_wash_sales


def retrieve_stock_recommendations(is_simulation, algorithm_dict, stock_dict, portfolio_dict,
                                   purchase_history_dict, current_date):

    buy_pattern = algorithm_dict['Buy_Pattern']
    sell_pattern = algorithm_dict['Sell_Pattern']

    pattern = f'{buy_pattern}+{sell_pattern}'

    recommendation_dict = {'BUY': {}, 'SELL': {}}
    for stock_ticker in stock_dict:
        if 'Dataframe' in stock_dict[stock_ticker]:
            csv_dataframe = stock_dict[stock_ticker]['Dataframe']

            holding_stock = False
            last_purchase_price = 0
            if stock_ticker in portfolio_dict:
                holding_stock = True
                last_purchase_price = float(portfolio_dict[stock_ticker]['Price'])

            signal_list = make_signal_determination(algorithm_dict=algorithm_dict,
                                                    is_simulation=is_simulation,
                                                    csv_dataframe=csv_dataframe,
                                                    current_date=current_date,
                                                    pattern=pattern,
                                                    holding_stock=holding_stock,
                                                    last_purchase_price=last_purchase_price)

            wait_for_wash_sales = wash_sale_check(is_simulation=is_simulation,
                                                  signal=signal_list[0],
                                                  stock_ticker=stock_ticker,
                                                  purchase_history_dict=purchase_history_dict,
                                                  current_date=current_date,)

            if holding_stock is False \
                    and wait_for_wash_sales is False \
                    and signal_list[0] == 'BUY':
                recommendation_dict['BUY'][stock_ticker] = signal_list

            if holding_stock is True and signal_list[0] == 'SELL':
                recommendation_dict['SELL'][stock_ticker] = signal_list

    return recommendation_dict
