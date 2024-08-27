import mt5_lib
import MetaTrader5 as mt5
import logging
import pandas as pd
import talib as ta
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



#functio nto retrieve data for strategy
def get_data(symbol, timeframe):
    """
        Function to retrieve data from MT5. Data is in the form of candlesticks
        :param symbol: string og the symbol to be retrieved
        :param timeframe:string of the timeframe to be retrieved
        : return dataframe
    """
    #retrieve data
    try:
        data = mt5_lib.get_candlesticks(
            symbol = symbol,
            timeframe= timeframe,
            number_of_candlesticks= 1000
        )
        if data.empty:
            logging.warning(f"No data retrieved for {symbol} on {timeframe}")
        return data
    except Exception as e:
        logging.error(f"Error retrieving data for {symbol}: {str(e)}")
        return None            
# hybrid strategy

def hybrid_strategy(symbol, timeframe):
    stop_loss_pips = 50
    take_profit_pips = 100
    deviation = 20
    amount_to_risk = 0.001
    risk_reward_ratio = 2
    # Get account balance
    account_info = mt5.account_info()
    account_balance = account_info.balance
    leverage = account_info.leverage
    print(f"account balance is: {account_balance}")
    
    #fetch recent market data
    # rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)
    df = get_data(symbol=symbol, timeframe=timeframe)

    
    #Calculate indicators for hybrid strategy
    
    # 1. EMA Crossover
    df['EMA_short'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_long'] = df['close'].ewm(span=26, adjust=False).mean()

    # 2. MACD Crossover
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # 3. RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    buy_signal = (
    df['EMA_short'].iloc[-1] > df['EMA_long'].iloc[-1] and
    df['MACD'].iloc[-1] > df['Signal'].iloc[-1] and
    df['RSI'].iloc[-1] < 50
    )

    sell_signal = (
        df['EMA_short'].iloc[-1] < df['EMA_long'].iloc[-1] and
        df['MACD'].iloc[-1] < df['Signal'].iloc[-1] and
        df['RSI'].iloc[-1] > 50
    )

    # Determine trade type based on signals
    if buy_signal:
        trade_type = mt5.ORDER_TYPE_BUY
        stop_loss_direction = -1
        take_profit_direction = 1
    elif sell_signal:
        trade_type = mt5.ORDER_TYPE_SELL
        stop_loss_direction = 1
        take_profit_direction = -1
    else:
        print("No clear trading signal")
        return
    
    
    
    if(buy_signal or sell_signal):
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        point = mt5.symbol_info(symbol).point
        #Retrieve symbol info to check for volume constraints
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logging.info(f"Symbol {symbol} not found")
            mt5.shutdown()
            exit()
        
        
        # Calculate pip value and volume based on risk management
        pip_value = mt5.symbol_info(symbol).trade_contract_size * point / leverage  # Value per pip (varies by symbol)
        risk_amount = account_balance * amount_to_risk
        
        #calculate position size based on risk and stop loss distance
        raw_position_size = risk_amount / (stop_loss_pips * pip_value)
        
        #Cap position size at max allowed volume
        position_size = min(symbol_info.volume_max, raw_position_size)
        
        #Round position size to the nearest valid stepsize
        position_size = max(symbol_info.volume_min, round(position_size / symbol_info.volume_step) * symbol_info.volume_step)
        
        # Calculate position size based on risk and stop loss distance
        
        # Calculate Stop Loss and Take Profit prices
        stop_loss_price = tick.ask + stop_loss_direction * stop_loss_pips * point
        take_profit_pips = stop_loss_pips * risk_reward_ratio
        take_profit_price = tick.ask + take_profit_direction * take_profit_pips * point

        # Prepare the trade request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": position_size,
            "type": trade_type,
            "price": tick.ask if trade_type == mt5.ORDER_TYPE_BUY else tick.bid,
            "sl": stop_loss_price,
            "tp": take_profit_price,
            "deviation": deviation,
            "magic": 234000,
            "comment": "Algorazo Trading Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Execute the trade
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.info(f"Order failed, retcode={result.retcode}")
        else:
            logging.info("Order executed successfully")
        
    

