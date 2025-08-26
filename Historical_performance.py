import pandas as pd
import os
import matplotlib.pyplot as plt



def get_previous_non_zero(series, index):
    """Finds the nearest previous non-zero value from a given index."""
    while index >= 0 and series.iloc[index] == 0:
        index -= 1
    return index


def Filter1_ratio():
    path_to_files = "./Scrapped_data/daily"
    all_files = [
        os.path.join(path_to_files, file)
        for file in os.listdir(path_to_files)
        if file.endswith(".csv")
    ]
    tickers = [os.path.splitext(os.path.basename(file))[0] for file in all_files]
    take_profit_count = 0
    stop_loss_count = 0
    
    yearly_results = {}

    for tic in tickers:
        # Read data
        df = pd.read_csv(f"./Scrapped_data/daily/{tic}.csv")
        df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' is in datetime format
        df['year'] = df['date'].dt.year         # Extract year for yearly tracking
        df = df.reset_index(drop=True)          # Reset the index to avoid iloc issues

        # Calculating rolling standard deviation RSI of trade
        df['Rolling Std Dev trade'] = df['trade'].rolling(window=10).std()
        delta_std_trade = df['Rolling Std Dev trade'].diff()
        gain_std_trade = delta_std_trade.where(delta_std_trade > 0, 0)
        loss_std_trade = -delta_std_trade.where(delta_std_trade < 0, 0)
        avg_gain_std_trade = gain_std_trade.rolling(window=14, min_periods=1).mean()
        avg_loss_std_trade = loss_std_trade.rolling(window=14, min_periods=1).mean()
        rs_std_trade = avg_gain_std_trade / avg_loss_std_trade
        df['RSI of Rolling Std Dev trade'] = 100 - (100 / (1 + rs_std_trade))

        # RSI calculation for close price
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        in_trade = False
        entry_price = 0
        
        for i in range(3, len(df)):
            # Check if t-1 close is positive compared to t-2 close
            close_positive = df.iloc[i - 1]['close'] > df.iloc[i - 2]['close']
            
            # Calculate low differences
            idx1 = get_previous_non_zero(df['low'], i - 1)
            idx2 = get_previous_non_zero(df['low'], idx1 - 1)
            low_diff1 = abs((df['low'].iloc[idx1] - df['low'].iloc[idx2]) / df['low'].iloc[idx2])

            idx3 = get_previous_non_zero(df['low'], idx2 - 1)
            low_diff2 = abs((df['low'].iloc[idx2] - df['low'].iloc[idx3]) / df['low'].iloc[idx3])

            # Trading signal
            if (not in_trade and low_diff2 <= 0.001 and close_positive 
                and df['RSI of Rolling Std Dev trade'].iloc[i - 1] > 98 
                and df['RSI'].iloc[i - 1] > 98):
                in_trade = True
                entry_price = df.iloc[i]['close']
                buy_date = df.iloc[i]['date']
                current_year = pd.to_datetime(buy_date).year

            if in_trade:
                take_profit_price = entry_price * 1.15
                stop_loss_price = entry_price * 0.92

                if df.iloc[i]['close'] >= take_profit_price:
                    take_profit_count += 1
                    yearly_results.setdefault(current_year, {'Wins': 0, 'Losses': 0})
                    yearly_results[current_year]['Wins'] += 1
                    in_trade = False

                elif df.iloc[i]['close'] <= stop_loss_price:
                    stop_loss_count += 1
                    yearly_results.setdefault(current_year, {'Wins': 0, 'Losses': 0})
                    yearly_results[current_year]['Losses'] += 1
                    in_trade = False

    # Create a yearly summary DataFrame
    yearly_summary = []
    for year, data in yearly_results.items():
        wins = data['Wins']
        losses = data['Losses']
        ratio = wins / max(1, losses)  # Avoid division by zero
        yearly_summary.append({
            'Year': year,
            'Wins': wins,
            'Losses': losses,
            'Win-Loss Ratio': ratio
        })

    yearly_summary_df = pd.DataFrame(yearly_summary).sort_values(by='Year')
    
    res = yearly_summary_df # DataFrame with Year, Wins, Losses
    ax = res.set_index('Year')[['Wins','Losses']].plot(kind='bar')
    ax.set_title('Filter X — Yearly Wins/Losses')
    ax.set_xlabel('Year')
    ax.set_ylabel('Count')
    plt.show()

    # Display the results
    print(f'Total take profits = {yearly_summary_df["Wins"].sum()}')
    print(f'Total stop losses = {yearly_summary_df["Losses"].sum()}')
    print(f'Overall win-loss ratio = {yearly_summary_df["Wins"].sum() / max(1, yearly_summary_df["Losses"].sum())}')
    print("\nYearly Summary:")
    print(yearly_summary_df)

    


def Filter2_ratio():
    path_to_files = "./Scrapped_data/daily"
    all_files = [
        os.path.join(path_to_files, file)
        for file in os.listdir(path_to_files)
        if file.endswith(".csv")
    ]
    tickers = [os.path.splitext(os.path.basename(file))[0] for file in all_files]
    take_profit_count = 0
    stop_loss_count = 0
    
    yearly_results = {}

    for tic in tickers:
        # Read data
        df = pd.read_csv(f"./Scrapped_data/daily/{tic}.csv")
        df['date'] = pd.to_datetime(df['date'])  # Ensure the 'date' column is parsed correctly as datetime
        df['year'] = df['date'].dt.year         # Extract year from the date column

        # Calculate indicators
        df['vol_trade'] = df['volume'] / df['trade']
        df['price_sma'] = df['close'].rolling(window=10).mean()
        df['price_ema'] = df['close'].ewm(span=10, min_periods=0, adjust=False).mean()
        df['trade_sma'] = df['trade'].rolling(window=30).mean()
        df['trade_ema'] = df['trade'].ewm(span=20, min_periods=0, adjust=False).mean()
        df['Rolling Std Dev'] = df['close'].rolling(window=10).std()

        # RSI calculation for close price
        window_length = 14
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window_length, min_periods=1).mean()
        avg_loss = loss.rolling(window=window_length, min_periods=1).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # RSI for Rolling Standard Deviation
        delta_std = df['Rolling Std Dev'].diff()
        gain_std = delta_std.where(delta_std > 0, 0)
        loss_std = -delta_std.where(delta_std < 0, 0)
        avg_gain_std = gain_std.rolling(window=window_length, min_periods=1).mean()
        avg_loss_std = loss_std.rolling(window=window_length, min_periods=1).mean()
        rs_std = avg_gain_std / avg_loss_std
        df['RSI of Rolling Std Dev'] = 100 - (100 / (1 + rs_std))

        # RSI for vol_trade
        df['Rolling Std Dev vol_trade'] = df['vol_trade'].rolling(window=10).std()
        delta_vol_trade = df['Rolling Std Dev vol_trade'].diff()
        gain_vol_trade = delta_vol_trade.where(delta_vol_trade > 0, 0)
        loss_vol_trade = -delta_vol_trade.where(delta_vol_trade < 0, 0)
        avg_gain_vol_trade = gain_vol_trade.rolling(window=window_length, min_periods=1).mean()
        avg_loss_vol_trade = loss_vol_trade.rolling(window=window_length, min_periods=1).mean()
        rs_vol_trade = avg_gain_vol_trade / avg_loss_vol_trade
        df['RSI of Std vol_trade'] = 100 - (100 / (1 + rs_vol_trade))

        # MACD Parameters
        short_window = 20
        long_window = 40
        signal_window = 15
        df['EMA_20'] = df['close'].ewm(span=short_window, adjust=False).mean()
        df['EMA_40'] = df['close'].ewm(span=long_window, adjust=False).mean()
        df['MACD'] = df['EMA_20'] - df['EMA_40']
        df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
        
        in_trade = False
        entry_price = 0
        
        for i in range(3, len(df)):
            low_diff_1 = abs(df.iloc[i - 1]['low'] - df.iloc[i - 2]['low'])
            low_diff_criteria = (low_diff_1 / df.iloc[i - 2]['low'] <= 0.02)
            close_positive = df.iloc[i - 1]['close'] > df.iloc[i - 2]['close']
            signal_above_macd_15 = all(df['Signal_Line'].iloc[i-15:i-1] > df['MACD'].iloc[i-15:i-1])

            if (not in_trade and low_diff_criteria and signal_above_macd_15 and 
                close_positive and (df['Signal_Line'].iloc[i-1] > df["MACD"].iloc[i-1]) 
                and (df["RSI"].iloc[i-1] < 30) and df["open"].iloc[i-1] == df["low"].iloc[i-1] and 
                df["trade_ema"].iloc[i-1] > df["trade_sma"].iloc[i-1] and df['RSI of Rolling Std Dev'].iloc[i-1] < 30 
                and df['RSI of Std vol_trade'].iloc[i-1] < 70):
                in_trade = True
                entry_price = df.iloc[i]['close']
                buy_date = df.iloc[i]['date']
                current_year = pd.to_datetime(buy_date).year

            if in_trade:
                take_profit_price = entry_price * 1.40
                stop_loss_price = entry_price * 0.85

                if df.iloc[i]['close'] >= take_profit_price:
                    take_profit_count += 1
                    yearly_results.setdefault(current_year, {'Wins': 0, 'Losses': 0})
                    yearly_results[current_year]['Wins'] += 1
                    in_trade = False

                elif df.iloc[i]['close'] <= stop_loss_price:
                    stop_loss_count += 1
                    yearly_results.setdefault(current_year, {'Wins': 0, 'Losses': 0})
                    yearly_results[current_year]['Losses'] += 1
                    in_trade = False

    # Create a yearly summary DataFrame
    yearly_summary = []
    for year, data in yearly_results.items():
        wins = data['Wins']
        losses = data['Losses']
        ratio = wins / max(1, losses)  # Avoid division by zero
        yearly_summary.append({
            'Year': year,
            'Wins': wins,
            'Losses': losses,
            'Win-Loss Ratio': ratio
        })

    yearly_summary_df = pd.DataFrame(yearly_summary).sort_values(by='Year')
    res = yearly_summary_df # DataFrame with Year, Wins, Losses
    ax = res.set_index('Year')[['Wins','Losses']].plot(kind='bar')
    ax.set_title('Filter X — Yearly Wins/Losses')
    ax.set_xlabel('Year')
    ax.set_ylabel('Count')
    plt.show()

    # Display the results
    print(f'Total take profits = {yearly_summary_df["Wins"].sum()}')
    print(f'Total stop losses = {yearly_summary_df["Losses"].sum()}')
    print(f'Overall win-loss ratio = {yearly_summary_df["Wins"].sum() / max(1, yearly_summary_df["Losses"].sum())}')
    print("\nYearly Summary:")
    print(yearly_summary_df)

    
    
def Filter3_ratio():
    path_to_files = "./Scrapped_data/daily"
    all_files = [
        os.path.join(path_to_files, file)
        for file in os.listdir(path_to_files)
        if file.endswith(".csv")
    ]
    tickers = [os.path.splitext(os.path.basename(file))[0] for file in all_files]
    take_profit_count = 0
    stop_loss_count = 0

    # Initialize a list to store yearly results
    yearly_results = {}

    for tic in tickers:
        # Read data
        df = pd.read_csv(f"./Scrapped_data/daily/{tic}.csv")
        df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' is parsed as datetime
        df['Year'] = df['date'].dt.year  # Extract year for grouping
        
        df['vol_trade'] = df['volume'] / df['trade']
        df['price_sma'] = df['close'].rolling(window=10).mean()
        df['price_ema'] = df['close'].ewm(span=10, min_periods=0, adjust=False).mean()
        df['trade_sma'] = df['trade'].rolling(window=30).mean()
        df['trade_ema'] = df['trade'].ewm(span=20, min_periods=0, adjust=False).mean()
        df['Rolling Std Dev'] = df['close'].rolling(window=10).std()

        # Calculate RSI
        window_length = 14
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(alpha=1 / window_length, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / window_length, adjust=False).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # RSI of Rolling Std Dev
        delta_std = df['Rolling Std Dev'].diff()
        gain_std = delta_std.where(delta_std > 0, 0)
        loss_std = -delta_std.where(delta_std < 0, 0)
        avg_gain_std = gain_std.ewm(alpha=1 / window_length, adjust=False).mean()
        avg_loss_std = loss_std.ewm(alpha=1 / window_length, adjust=False).mean()
        rs_std = avg_gain_std / avg_loss_std
        df['RSI of Rolling Std Dev'] = 100 - (100 / (1 + rs_std))

        # RSI of vol_trade
        df['Rolling Std Dev vol_trade'] = df['vol_trade'].rolling(window=10).std()
        delta_vol_trade = df['Rolling Std Dev vol_trade'].diff()
        gain_vol_trade = delta_vol_trade.where(delta_vol_trade > 0, 0)
        loss_vol_trade = -delta_vol_trade.where(delta_vol_trade < 0, 0)
        avg_gain_vol_trade = gain_vol_trade.ewm(alpha=1 / window_length, adjust=False).mean()
        avg_loss_vol_trade = loss_vol_trade.ewm(alpha=1 / window_length, adjust=False).mean()
        rs_vol_trade = avg_gain_vol_trade / avg_loss_vol_trade
        df['RSI of Std vol_trade'] = 100 - (100 / (1 + rs_vol_trade))

        # MACD
        short_window = 20
        long_window = 40
        signal_window = 15
        df['EMA_20'] = df['close'].ewm(span=short_window, adjust=False).mean()
        df['EMA_40'] = df['close'].ewm(span=long_window, adjust=False).mean()
        df['MACD'] = df['EMA_20'] - df['EMA_40']
        df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
        
        in_trade = False
        entry_price = 0

        for i in range(3, len(df)):
            low_diff_1 = abs(df.iloc[i - 1]['low'] - df.iloc[i - 2]['low'])
            low_diff_criteria = (low_diff_1 / df.iloc[i - 2]['low'] <= 0.02)
            close_positive = df.iloc[i - 1]['close'] > df.iloc[i - 2]['close']
            signal_above_macd_15 = all(df['Signal_Line'].iloc[i-15:i-1] > df['MACD'].iloc[i-15:i-1])

            if (not in_trade and low_diff_criteria and signal_above_macd_15 and 
                close_positive and (df['Signal_Line'].iloc[i-1] > df["MACD"].iloc[i-1]) 
                and (df["RSI"].iloc[i-1] < 30) and df["open"].iloc[i-1] == df["low"].iloc[i-1] and 
                df["trade_ema"].iloc[i-1] > df["trade_sma"].iloc[i-1] and df['RSI of Rolling Std Dev'].iloc[i-1] < 70 
                and df['RSI of Std vol_trade'].iloc[i-1] < 30):
                in_trade = True
                entry_price = df.iloc[i]['close']
                buy_date = df.iloc[i]['date']
                current_year = pd.to_datetime(buy_date).year

            if in_trade:
                take_profit_price = entry_price * 1.15
                stop_loss_price = entry_price * 0.92

                if df.iloc[i]['close'] >= take_profit_price:
                    take_profit_count += 1
                    yearly_results.setdefault(current_year, {'Wins': 0, 'Losses': 0})
                    yearly_results[current_year]['Wins'] += 1
                    in_trade = False

                elif df.iloc[i]['close'] <= stop_loss_price:
                    stop_loss_count += 1
                    yearly_results.setdefault(current_year, {'Wins': 0, 'Losses': 0})
                    yearly_results[current_year]['Losses'] += 1
                    in_trade = False

    # Create a yearly summary DataFrame
    yearly_summary = []
    for year, data in yearly_results.items():
        wins = data['Wins']
        losses = data['Losses']
        ratio = wins / max(1, losses)  # Avoid division by zero
        yearly_summary.append({
            'Year': year,
            'Wins': wins,
            'Losses': losses,
            'Win-Loss Ratio': ratio
        })

    yearly_summary_df = pd.DataFrame(yearly_summary).sort_values(by='Year')
    res = yearly_summary_df # DataFrame with Year, Wins, Losses
    ax = res.set_index('Year')[['Wins','Losses']].plot(kind='bar')
    ax.set_title('Filter X — Yearly Wins/Losses')
    ax.set_xlabel('Year')
    ax.set_ylabel('Count')
    plt.show()

    # Display the results
    print(f'Total take profits = {yearly_summary_df["Wins"].sum()}')
    print(f'Total stop losses = {yearly_summary_df["Losses"].sum()}')
    print(f'Overall win-loss ratio = {yearly_summary_df["Wins"].sum() / max(1, yearly_summary_df["Losses"].sum())}')
    print("\nYearly Summary:")
    print(yearly_summary_df)
    

