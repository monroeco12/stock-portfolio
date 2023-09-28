from datetime import datetime
import pathlib
from Programs.log_file import write_to_log_file
from Programs.print_styles import print_progress_bar
from Programs.timestamps_file import check_timestamps_file
import requests
import time
import urllib3.exceptions


stock_data_folder_path = 'Files/Stock_Data'
accounts_folder_path = 'Files/Accounts'


def create_data_files(stock_ticker):
    folder_and_file_tuple = \
        (['Historical_Data',
          'historical_data.csv',
          'date,close,volume,open,high,low\n'],
         ['Summary_Data',
          'summary_data.csv',
          ''],
         ['Dividend_Data',
          'dividend_data.csv',
          'Payment_Date,Declaration_Date,Ex_Date,Record_Date,Cash_Amount\n'],
         ['Earnings_Data',
          'earnings_data.csv',
          'Fiscal_Quarter_End,Date_Reported,Earnings_Per_Share,Earnings_Per_Share_Forecast,'
          'Percent_Surprise,Next_Announcement_Date\n'],
         ['Indicator_Data',
          'indicator_data.csv',
          ''])

    for item in folder_and_file_tuple:
        try:
            folder_path = f'{stock_data_folder_path}/{stock_ticker}/{item[0]}'
            pathlib.Path(folder_path).mkdir(parents=True, exist_ok=False)

            with open(f'{folder_path}/{item[1]}', 'w') as data_file:
                data_file.write(item[2])

        except FileExistsError:
            continue


def retrieve_historical_data(session, stock_ticker, insufficient_data_list):
    file_path = f'{stock_data_folder_path}/{stock_ticker}/Historical_Data/historical_data.csv'

    # Create a start date 10 years before today
    start_date = f'{str(int(datetime.today().year) - 10)}-01-01'
    end_date = str(datetime.today().date())
    date_update_count = 0

    with open(file_path, 'r') as historical_data_file:
        scraped_dates_list = [i.split(',')[0] for i in historical_data_file if 'date' not in i]

    if len(scraped_dates_list) != 0:
        start_date = scraped_dates_list[-1]

    try:
        url_data_list = []

        acceptable_date = False
        while acceptable_date is False:
            try:
                url = f'https://api.nasdaq.com/api/quote/{stock_ticker.replace("-", "%25sl%25")}/' \
                      f'historical?assetclass=stocks&fromdate={start_date}&limit=100000&todate={end_date}'
                url_data_list = list(reversed(session.get(url, timeout=30).json()['data']['tradesTable']['rows']))

                acceptable_date = True

            except (TypeError, requests.exceptions.JSONDecodeError):

                if len(scraped_dates_list) != 0:
                    new_year = str(int(start_date.split("-")[0]) - 1)
                else:
                    new_year = str(int(start_date.split("-")[0]) + 1)

                start_date = f'{new_year}-01-01'

                date_update_count += 1
                if date_update_count > 3:
                    insufficient_data_list.append((stock_ticker, 'Historical'))

                    write_to_log_file(title='DATE NOT FOUND',
                                      message=f'A data scraping start date for {stock_ticker} was not found.')
                    acceptable_date = True

                else:
                    write_to_log_file(title='DATE UPDATED',
                                      message=f'The data scraping start date for {stock_ticker} is now {start_date}.')

                time.sleep(1.10)

        with open(file_path, 'a') as historical_data_file:
            for data_dict in url_data_list:
                date_list = data_dict['date'].split('/')
                date = f'{date_list[2]}-{date_list[0]}-{date_list[1]}'

                if date not in scraped_dates_list:
                    historical_data_file.write(f'{date}')
                    for key in ['close', 'volume', 'open', 'high', 'low']:
                        historical_data_file.write(f',{data_dict[key].replace("$", "").replace(",", "")}')
                    historical_data_file.write(f'\n')

    except (TimeoutError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        insufficient_data_list.append((stock_ticker, 'Historical'))


def retrieve_summary_data(session, stock_ticker, insufficient_data_list):
    file_path = f'{stock_data_folder_path}/{stock_ticker}/Summary_Data/summary_data.csv'

    status = ''

    try:
        url = f'https://api.nasdaq.com/api/quote/{stock_ticker.replace("-", "%25sl%25")}/summary?assetclass=stocks'
        response = session.get(url, timeout=30).json()
        status = str(response['status']['rCode'])
        url_data_dict = response['data']['summaryData']

        with open(file_path, 'w') as summary_data_file:
            labels_list = []
            values_list = []

            for key in url_data_dict:
                label = url_data_dict[key]['label']
                value = url_data_dict[key]['value']

                label = str(label).replace(',', '').replace(' ', '_'). replace("'s", '').\
                    replace('.', '').replace('(EPS)', '')
                if 'High/Low' in label:
                    label = f'{label.replace("High/Low", "")}High,{label.replace("High/Low", "")}Low'
                labels_list.append(label)

                value = str(value).replace(',', '')
                if 'Date' in key and value != 'N/A':
                    value = str(datetime.strptime(value, '%b %d %Y')).split(' ')[0]
                if '/' in value and value != 'N/A' and label not in ['Exchange', 'Sector', 'Industry']:
                    value = f'{value[:value.index("/")]},{value[value.index("/") + 1:]}'
                values_list.append(value)

            summary_data_file.write(f'{",".join(labels_list)}\n')
            summary_data_file.write(f'{",".join(values_list)}\n')

    except (TypeError, TimeoutError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        if status != '200':
            insufficient_data_list.append((stock_ticker, 'Summary'))


def retrieve_dividend_data(session, stock_ticker, insufficient_data_list):
    file_path = f'{stock_data_folder_path}/{stock_ticker}/Dividend_Data/dividend_data.csv'

    with open(file_path, 'r') as dividend_data_file:
        scraped_dates_list = [i.split(',')[0] for i in dividend_data_file if 'Payment_Date' not in i]

    status = ''

    try:
        url = f'https://api.nasdaq.com/api/quote/{stock_ticker.replace("-", "%25sl%25")}/dividends?assetclass=stocks'
        response = session.get(url, timeout=30).json()
        status = str(response['status']['rCode'])
        url_data_list = list(reversed(response['data']['dividends']['rows']))

        with open(file_path, 'a') as dividend_data_file:
            for data_dict in url_data_list:
                if data_dict['paymentDate'] != 'N/A':
                    # Convert the date format to YYYY-MM-DD
                    payment_date_list = data_dict['paymentDate'].split('/')
                    payment_date = f'{payment_date_list[2]}-{payment_date_list[0]}-{payment_date_list[1]}'

                    if payment_date not in scraped_dates_list:
                        dividend_data_file.write(f'{payment_date}')
                        for key in ['declarationDate', 'exOrEffDate', 'recordDate', 'amount']:
                            if key != 'amount' and data_dict[key] != 'N/A':
                                date_list = data_dict[key].split('/')
                                date = f'{date_list[2]}-{date_list[0]}-{date_list[1]}'
                                dividend_data_file.write(f',{date}')
                            if key != 'amount' and data_dict[key] == 'N/A':
                                dividend_data_file.write(f',{data_dict[key]}')
                            if key == 'amount':
                                dividend_data_file.write(f',{data_dict[key].replace("$", "").replace(",", "")}')
                        dividend_data_file.write(f'\n')

    except (TypeError, TimeoutError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        if status != '200':
            insufficient_data_list.append((stock_ticker, 'Dividend'))


def retrieve_earnings_data(session, stock_ticker, insufficient_data_list):
    file_path = f'{stock_data_folder_path}/{stock_ticker}/Earnings_Data/earnings_data.csv'

    with open(file_path, 'r') as earnings_data_file:
        scraped_dates_list = [i.split(',')[0] for i in earnings_data_file if 'Fiscal_Quarter_End' not in i]

    status = ''

    try:
        url = f'https://api.nasdaq.com/api/analyst/{stock_ticker.replace("-", "%25sl%25")}/earnings-date'
        response = session.get(url, timeout=30).json()
        status = str(response['status']['rCode'])
        url_data_dict = response['data']['announcement']

        try:
            # Convert the date format to YYYY-MM-DD
            next_announcement_date = \
                str(datetime.strptime(url_data_dict.split(': ')[1], '%b %d, %Y')).split(' ')[0]

            with open(file_path, 'r') as earnings_data_file:
                original_lines = []
                for index, line in enumerate(earnings_data_file):
                    if index > 0:
                        line = f'{",".join(line.split(",")[:-1])},{next_announcement_date}\n'
                    original_lines.append(line)

            with open(file_path, 'w') as earnings_data_file:
                for line in original_lines:
                    earnings_data_file.write(line)

        except ValueError:
            next_announcement_date = 'N/A'

        url = f'https://api.nasdaq.com/api/company/{stock_ticker.replace("-", "%25sl%25")}/earnings-surprise'
        response = session.get(url, timeout=30).json()
        status = str(response['status']['rCode'])
        url_data_list = list(reversed(response['data']['earningsSurpriseTable']['rows']))

        with open(file_path, 'a') as earnings_data_file:
            for data_dict in url_data_list:
                # Convert the date format to YYYY-MM-DD
                fiscal_quarter_end_date = str(datetime.strptime(data_dict['fiscalQtrEnd'], '%b %Y')).split(' ')[0]

                if fiscal_quarter_end_date not in scraped_dates_list:
                    earnings_data_file.write(f'{fiscal_quarter_end_date}')
                    for key in ['dateReported', 'eps', 'consensusForecast', 'percentageSurprise']:
                        if 'date' in key:
                            date_list = data_dict[key].split('/')
                            date = f'{date_list[2]}-{date_list[0]}-{date_list[1]}'
                            earnings_data_file.write(f',{date}')
                        else:
                            earnings_data_file.write(f',{str(data_dict[key])}')
                    earnings_data_file.write(f',{next_announcement_date}\n')

    except (TypeError, TimeoutError, KeyError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        if status != '200':
            insufficient_data_list.append((stock_ticker, 'Earnings'))


def scrape_stock_data(stock_ticker, program_start_time, data_count, data_length):
    continue_on = check_timestamps_file(file_name=f'scrape_{stock_ticker}_data.py',
                                        program_start_time=program_start_time)

    if continue_on is True:
        headers = {'Accept': 'application/json, text/plain, */*',
                   'Origin': 'https://www.nasdaq.com',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Host': 'api.nasdaq.com',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
                                 '(KHTML, like Gecko) Version/15.4 Safari/605.1.15',
                   'Accept-Language': 'en-US,en;q=0.9',
                   'Referer': 'https://www.nasdaq.com/',
                   'Connection': 'keep-alive'}

        with requests.session() as session:
            session.headers.update(headers)

            create_data_files(stock_ticker=stock_ticker)

            function_dict = {'Historical': retrieve_historical_data,
                             'Summary': retrieve_summary_data,
                             'Dividend': retrieve_dividend_data,
                             'Earnings': retrieve_earnings_data}

            insufficient_data_list = []
            for key in function_dict:
                function_dict[key](session=session,
                                   stock_ticker=stock_ticker,
                                   insufficient_data_list=insufficient_data_list)
                time.sleep(1.10)

            print_progress_bar(title=f'SCRAPING {stock_ticker} DATA',
                               index=data_count,
                               data_length=data_length)

            list_length = len(insufficient_data_list)

            for index, (stock_ticker, function_name) in enumerate(insufficient_data_list):
                function_dict[function_name](session=session,
                                             stock_ticker=stock_ticker,
                                             insufficient_data_list=[])
                time.sleep(1.10)

                print_progress_bar(title=f'RE-SCRAPING {stock_ticker} DATA',
                                   index=data_count,
                                   data_length=data_length)

        write_to_log_file(title='SCRAPED DATA',
                          message=f'/.../scrape_{stock_ticker}_data.py has completed with {list_length} re-scrapes.')
