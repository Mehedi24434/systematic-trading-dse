import pandas as pd
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")


def scrape_data_updater (last_day:str):
    
    update_date = last_day
    
    df_list = pd.read_html(f"https://www.dsebd.org/day_end_archive.php?startDate={last_day}&endDate={last_day}&inst=All%20Instrument&archive=data")     #use other than trading days
    # Access the last table in the list
    ohlcv_table = df_list[-2]
    ticker_list = ohlcv_table['TRADING CODE'].unique()
    len(ticker_list)
    mother_data = ohlcv_table
    mother_data['Date'] = update_date
    mother_data.rename(columns={
        'TRADING CODE': 'Scrip',
        'HIGH': 'High',
        'LOW': 'Low',
        'CLOSEP*': 'Close',
        'OPENP*': 'Open',
        'VOLUME': 'Volume',
        'TRADE' : 'Trade'
    }, inplace=True)
    writtable_tickers=[]
    # Iterate through ticker files and update them
    folder_path = './Scrapped_data/daily'  # ingestable file location
    csv_files = [file.split('.')[0] for file in os.listdir(folder_path) if file.endswith('.csv')]
    no_update_tickers = list(set(csv_files)-set(ticker_list))
    for ticker_name in ticker_list:
        ticker_file = os.path.join(folder_path, f'{ticker_name}.csv')

        if os.path.exists(ticker_file):
            ticker_data = pd.read_csv(ticker_file)
            

            # Update the last row of the ticker file with the modified date
            last_row_index = len(ticker_data) 
            
            ticker_data.at[last_row_index, 'date'] = mother_data['Date'].iloc[0]
        
            # Fill the ticker data from the mother file (convert column names to lowercase)
            matching_rows = mother_data[mother_data['Scrip'] == ticker_name]
            ticker_data.at[last_row_index,'open'] = matching_rows['Open'].values
            ticker_data.at[last_row_index,'high'] = matching_rows['High'].values
            ticker_data.at[last_row_index,'low'] = matching_rows['Low'].values
            ticker_data.at[last_row_index,'close'] = matching_rows['Close'].values
            ticker_data.at[last_row_index,'volume'] = matching_rows['Volume'].values
            ticker_data.at[last_row_index,'trade'] = matching_rows['Trade'].values
            # Save the updated ticker data back to the file
            ticker_data.to_csv(ticker_file, index=False)
            print(f'done for {ticker_name}')

        else:
            print(f"Ticker file not found for {ticker_name}: {ticker_file}")




    #for no updated tickers
    for ticker_name in no_update_tickers:
        ticker_file = os.path.join(folder_path, f'{ticker_name}.csv')

        if os.path.exists(ticker_file):
            ticker_data = pd.read_csv(ticker_file)
            latest_date=ticker_data['date'].iloc[-1]
            try:
                date1 = datetime.strptime(latest_date, '%Y-%m-%d')
                date2= datetime.strptime(mother_data['Date'].iloc[0], '%Y-%m-%d')
                d=(date2-date1).days
                if d<7:
                    writtable_tickers.append(ticker_name) #collecting the unupdated tickers
            except:
                pass
            
                
    #writting in the unupdated data
    for ticker_name in writtable_tickers:
        ticker_file = os.path.join(folder_path, f'{ticker_name}.csv')

        if os.path.exists(ticker_file):
            ticker_data = pd.read_csv(ticker_file)
            

            # Update the last row of the ticker file with the modified date
            last_row_index = len(ticker_data) 
            
            ticker_data.at[last_row_index, 'date'] = mother_data['Date'].iloc[0]
        
            # Fill the ticker data from the mother file (convert column names to lowercase)
            # matching_rows = mother_data[mother_data['Scrip'] == ticker_name]
            ticker_data.at[last_row_index,'open'] = ticker_data['close'].iloc[last_row_index-1]
            ticker_data.at[last_row_index,'high'] = ticker_data['close'].iloc[last_row_index-1]
            ticker_data.at[last_row_index,'low'] = ticker_data['close'].iloc[last_row_index-1]
            ticker_data.at[last_row_index,'close'] = ticker_data['close'].iloc[last_row_index-1]
            ticker_data.at[last_row_index,'volume'] = 0
            ticker_data.at[last_row_index,'trade'] = 0
            # Save the updated ticker data back to the file
            ticker_data.to_csv(ticker_file, index=False)
            print(f'done for {ticker_name}')


def replace_zero_with_close(folder_path):
    # Get all CSV files from the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            
            # Check if 'open', 'high', 'low', 'close' columns exist
            if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
                
                # Replace 0 values in 'open', 'high', or 'low' with 'close' value
                df['open'] = df.apply(lambda row: row['close'] if row['open'] == 0 else row['open'], axis=1)
                df['high'] = df.apply(lambda row: row['close'] if row['high'] == 0 else row['high'], axis=1)
                df['low'] = df.apply(lambda row: row['close'] if row['low'] == 0 else row['low'], axis=1)
                
                # Save the modified DataFrame back to the CSV file
                df.to_csv(file_path, index=False)
                print(f"Updated: {filename}")
            else:
                print(f"Missing required columns in {filename}")
                
                
                




