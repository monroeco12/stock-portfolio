from datetime import datetime, timedelta


def retrieve_stock_tax_type(is_simulation, portfolio_data_list, stock_ticker, sell_date):
    for data_list in portfolio_data_list:
        if stock_ticker == data_list[1] and 'PENDING_SELL' != data_list[6]:
            # Adjust the buy date for accurate holding day count
            buy_date = datetime.strptime(data_list[0], '%Y-%m-%d') + timedelta(days=1)

            if is_simulation == "FALSE":
                sell_date = datetime.now()

            if (sell_date - buy_date) >= timedelta(days=365):
                tax_type = 'Long-Term'
            else:
                tax_type = 'Short-Term'

            return tax_type


def retrieve_dividend_tax_type(date_acquired, date_sold, current_date, ex_date):
    tax_type = 'Ordinary'

    if date_sold == '':
        date_sold = current_date

    # Update the date acquired for accurate holding day count
    date_acquired += timedelta(days=1)

    # Calculate the qualified tax range
    period_start = ex_date - timedelta(days=60)
    period_end = ex_date + timedelta(days=60)

    if date_acquired < period_start:
        date_acquired = period_start

    if (date_sold - date_acquired) >= timedelta(days=61) and date_sold <= period_end:
        tax_type = 'Qualified'

    return tax_type


def retrieve_tax_rate_dictionary():
    tax_rate_dict = {'Long-Term': {.00: [0, 44625],
                                   .15: [44626, 492300],
                                   .20: [492301, 1000000000]},

                     'Short-Term': {.10: [0, 11000],
                                    .12: [11001, 44725],
                                    .22: [44726, 95375],
                                    .24: [95376, 182100],
                                    .32: [182101, 231250],
                                    .35: [231251, 578125],
                                    .37: [578126, 1000000000]},

                     'Qualified': {.00: [0, 44625],
                                   .15: [44626, 492300],
                                   .20: [492301, 1000000000]},

                     'Ordinary': {.10: [0, 11000],
                                  .12: [11001, 44725],
                                  .22: [44726, 95375],
                                  .24: [95376, 182100],
                                  .32: [182101, 231250],
                                  .35: [231251, 578125],
                                  .37: [578126, 1000000000]},

                     'Net': {.038: [200000, 1000000000]},

                     'CA': {.010: [0, 10099],
                            .020: [10100, 23942],
                            .040: [23943, 37788],
                            .060: [37789, 52455],
                            .080: [52456, 66295],
                            .093: [66296, 338639],
                            .103: [338640, 406364],
                            .113: [406365, 677275],
                            .123: [677276, 1000000000]}}

    return tax_rate_dict
