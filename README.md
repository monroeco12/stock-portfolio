# stock-portfolio
A versatile stock portfolio management tool that accesses real-time Nasdaq data, utilizes technical analysis for predictive modeling, and generates accurate investment assessments for multiple unique user profiles.

**Required Packages:** numpy // pandas // requests // scipy // stock-indicators // termcolor

# Prerequisites
Before you begin using this program, please ensure that you have the following prerequisites installed:
1. **Python 3:** This program is written in Python 3. You can download and install it from the official [Python website](https://www.python.org/downloads/).
2. **numpy:** Handles arrays and numeric tasks for data analysis.
3. **pandas:** Manipulates, analyzes, and processes stock market data.
4. **requests:** Interacts with the Nasdaq API to obtain individual stock information.
5. **scipy:** Utilizes linear regression to discern trends in stock movement.
6. **stock-indicators:** Applies various financial indicators to historical stock data for analysis.
7. **termcolor:** Integrates colored text into terminal output.

You can easily install these required packages by running the following command: 
   - *pip install numpy pandas requests scipy stock-indicators termcolor*

# Configuration
You can tailor the **algorithm.json** file located in the **Files** directory to align with your preferences before executing the program. Adjustments can be made for the following:
1. **Simulation Configuration:**
   - 'Simulation': Set this to **True** if you want to enable simulation mode, or **False** to disable it.
   - 'Sim_Funds': Specify the initial amount of simulated funds available for trading simulations. The default is 3000.
2. **Back-Testing Configuration:**
   - 'Back_Test_Count': Set the number of back-tests you want to perform for each trading strategy. The default is 10.
   - 'Research_Range_In_Days': Determine the range (in days) of historical data you want to use for research purposes. The default is 28.
   - 'Dataframe_Range_In_Years': Define the range (in years) of historical data you want to load into the stock dataframes. The default is 5.
3. **Research Loop Configuration:**
   - 'Research_Loop_Minutes': Set the time interval (in minutes) for the research loop of each individual stock. The default is 3 minutes.
4. **Portfolio Management Configuration:**
   - 'Max_Stock_Count': Set the maximum number of stocks allowed in your portfolio. The default is 100.
   - 'Max_Stock_Percent': Define the maximum percentage of your total portfolio value that can be invested in a single stock. The default is 0.04 (4%).
   - 'Max_Sector_Percent': Define the maximum percentage of your total portfolio value that can be invested in a single sector (e.g., technology, healthcare). The default is 1.00 (100%).
