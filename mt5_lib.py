import MetaTrader5 as mt5
import pandas
import logging

# Function to Start Metatrader 5
def start_mt5(project_settings):
    """
        # Function to start metatrader 5
        # :param project_settings: json object with username, password, server, file location
        # :return: Boolean True = started, False = not started
    """ 
    # Ensure that all variables are set/formatted to the correct type
    username = project_settings['mt5']['username']
    username = int(username)
    password = project_settings['mt5']['password']
    password = str(password)
    server = project_settings['mt5']['server']
    server = str(server)
    mt5_pathway = project_settings['mt5']['mt5Pathway']
    mt5_pathway = str(mt5_pathway)

    #Attempt to initialize MT5
    mt5_init = False
    try:
        mt5_init = mt5.initialize(
            login = username,
            password = password,
            server = server,
            path = mt5_pathway
        )

    #handle any errors
    except Exception as e:
        print(f"Error initializing Metatrader 5: {e}")
        #return false
        mt5_init = False

    #if mt5 initialized attempt to login to mt5
    mt5_login = False
    if mt5_init:
        #attempt login
        try: 
            mt5_login = mt5.login(
                login = username,
                password = password,
                server = server
            )
            #Handle exception
        except Exception as e:
            print(f"Error logging into MetaTrader 5: {e}")
            mt5_login = False

    #Return the outcome to the user

    if mt5_login:
        account_info = mt5.account_info()
        balance = account_info.balance
        return [True, balance]
    #Default outcome
    return [False] 

#function to initialize symbol
def initialize_symbol(symbol):
    """
    Function to initializae a symbol on MT5. Assumes that MT5 has already been started
    :param symbol: string of symbol. 
    :return Boolean. true if initialized false if not
    """
    #step 1: check if symbol exists on MT5
    all_symbols = mt5.symbols_get()
    #create a list to store all symbol names
    symbol_names = []
    #all all symbol names to the list
    for sym in all_symbols:
        symbol_names.append(sym.name)
    #check if symbol is in list of symbols
    if symbol in symbol_names:
        #if symbol exists attempt to initialize
        try:
            mt5.symbol_select(symbol, True) #Arguments cant be declaresd here
            return True
        except Exception as e:
            print(f"Error enabling {symbol}. Error: {e}")
            return False
    else: 
        print(f"Symbol {symbol} doesn't not exist on this version")  
        return False  
    
#function to query historic candlesticks data from MT5
def get_candlesticks(symbol, timeframe, number_of_candlesticks):
    """
    Function to retrieve a user defined number of candlesticks from MT5
    Initialize upper range set at 50k as more requires changes to Metatrader 5 default
    :param symbol L string of the sumbol being retrieved
    :param timeframe: string of th etimeframe being retrieved
    :param number of candlesticks: integer number of candles to retrieve limited to 50k
    :return: dataframe of the candlesticks
    """
    #check that the number of candlesticks is <=50k
    if number_of_candlesticks >50000:
        raise ValueError("No more than 50000 candles can be retrieved at this time")
    #convert the timeframe into mt5 friendly format
    mt5_timeframe = set_query_timeframe(timeframe=timeframe)
    #retrieve the data
    candles = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 1, number_of_candlesticks)
    #convert to a dataframe
    dataframe = pandas.DataFrame(candles)
    return dataframe

#function to convert mt5 timeframe string into mt5 object
def set_query_timeframe(timeframe):
    """
    function to implement a conversion from a user friendly timeframe string into a mt5 friendly object
    function implements pseudo switch as version < 3.10 do not contains switch functionality
    """
    # Implement a Pseudo Switch statement. Note that Python 3.10 implements match / case but have kept it this way for
    # backwards integration
    if timeframe == "M1":
        return mt5.TIMEFRAME_M1
    elif timeframe == "M2":
        return mt5.TIMEFRAME_M2
    elif timeframe == "M3":
        return mt5.TIMEFRAME_M3
    elif timeframe == "M4":
        return mt5.TIMEFRAME_M4
    elif timeframe == "M5":
        return mt5.TIMEFRAME_M5
    elif timeframe == "M6":
        return mt5.TIMEFRAME_M6
    elif timeframe == "M10":
        return mt5.TIMEFRAME_M10
    elif timeframe == "M12":
        return mt5.TIMEFRAME_M12
    elif timeframe == "M15":
        return mt5.TIMEFRAME_M15
    elif timeframe == "M20":
        return mt5.TIMEFRAME_M20
    elif timeframe == "M30":
        return mt5.TIMEFRAME_M30
    elif timeframe == "H1":
        return mt5.TIMEFRAME_H1
    elif timeframe == "H2":
        return mt5.TIMEFRAME_H2
    elif timeframe == "H3":
        return mt5.TIMEFRAME_H3
    elif timeframe == "H4":
        return mt5.TIMEFRAME_H4
    elif timeframe == "H6":
        return mt5.TIMEFRAME_H6
    elif timeframe == "H8":
        return mt5.TIMEFRAME_H8
    elif timeframe == "H12":
        return mt5.TIMEFRAME_H12
    elif timeframe == "D1":
        return mt5.TIMEFRAME_D1
    elif timeframe == "W1":
        return mt5.TIMEFRAME_W1
    elif timeframe == "MN1":
        return mt5.TIMEFRAME_MN1
    else:
        print(f"Incorrect timeframe provided. {timeframe}")
        raise ValueError("Input the correct timeframe")
    
#function to place an order on metatrader 5
def place_order(order_type, symbol, volume, stop_loss, take_profit, comment, stop_price, direct=False):
    #options are sell_stop/ buy_stop
    print("Placing order")

    #make sure volume, stop_loss, take_profit and stop prices are in the correct format
    volume = float(volume)
    volume = round(volume, 2)

    #stop loss
    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, 4)
    
    stop_price = float(stop_price)
    stop_price = round(stop_price, 4)

    #set up the order request dictionary object
    request = {
        "symbol" : symbol,
        "volume":volume,
        "sl": stop_loss,
        "tp": take_profit,
        "type_time": mt5.ORDER_TIME_GTC,
        "comment":comment
    }
    #Create order type based on values
    if order_type == "SELL_STOP":
        #update request
        request['type'] = mt5.ORDER_TYPE_SELL_STOP
        request['action'] = mt5.TRADE_ACTION_PENDING
        request['type_filling'] = mt5.ORDER_FILLING_RETURN
        if stop_price <= 0:
            raise ValueError("Stop price cannot be zero")
        else:
            request['price'] = stop_price
    elif order_type == "BUY_STOP": 
        #update request
        request['type'] = mt5.ORDER_TYPE_BUY_STOP
        request['action'] = mt5.TRADE_ACTION_PENDING
        request['type_filling'] = mt5.ORDER_FILLING_RETURN
        if stop_price <= 0:
            raise ValueError("Stop price cannot be zero")
        else:
            request['price'] = stop_price
    else:
        #an order wtype which is not part of current functionality
        raise ValueError(f"Unsupported order type {order_type} provided")
    
    #if direct = true go straight to add order
    if direct: 
        #send the order to mt5
        order_result = mt5.order_send(request)
        #notify based on the return outcomes
        if order_result[0] == 10009:
            print(f"Order for {symbol} successful")
            return order_result[2]
        #Notify the user if autotrading has been left on in metatrader 5
        elif order_result[0] ==10027:
            print("Turn off AlgoTrading on MT5 Terminal")
            raise Exception("Turn off ALgo Trading on MT5 terminal")
        elif order_result[0] == 10015:
            print(f"invalid price for {symbol}. Price: {stop_price}")
        elif order_result[0] == 10016:
            print(f"Invalid stops for {symbol}. Stop Loss: {stop_loss}")
        elif order_result[0] == 10014:
            print(f"Invalid volume for {symbol}. Volume: {volume}")
        #default
        else:
            print(f"Error logging order for {symbol}, Error code: {order_result[0]} Order Details: {order_result}")
            raise Exception(f"Unknown error logging order for symbol {symbol}")
    else:
        #Check the order
        result = mt5.order_check(request)
        #if check passes, place an order
        if result[0] == 0:
            print(f"Order check for {symbol} successful. Placing an order")
            #place the order using recursion
            place_order(
                order_type= order_type,
                symbol= symbol,
                volume=volume,
                stop_price=stop_price,
                stop_loss= stop_loss,
                take_profit= take_profit,
                comment=comment,
                direct=True
            )
        #let user know an invalid price has been passed
        elif result[0] == 100015:
            print(f"Invalid price for {symbol}. Price:{stop_price}")
        else:
            print(f"Order check failed. Details: {result}")


#function to cancel an order on MT5
def cancel_order(order_number):
    """
        Function to cancel an order identified by an order number
        :param order_number: int representing the order number from MT5
        :return: True == cancelled. False == Not canceled 
    """
    #Create the request
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order":order_number,
        "comment":"order removed"
    }
    #Attempt to send the order to mt5
    try:
        order_result = mt5.order_send(request)
        print(order_result)
        if order_result[0] == 10009:
            print(f"Order {order_number} successfully cancelled")
            return True
        else:
            print (f"Order {order_number} unable to be cancelled")
            return False
    except Exception as e:
        #This represents an issue with MT5 terminal
        print(f"Error cancelling order {order_number}. Error: {e}")
        raise Exception
    

    # Function to retrieve all currently open orders on MT5


#function to retrieve a filtered list of open orders from MT5
def get_filtered_list_of_orders(symbol, comment):
    """
    Function to retrieve a filtered list of open orders from MT5.
    """
    # Retrieve a list of open orders, filtered by symbol
    open_orders_by_symbol = mt5.orders_get(symbol)
    #check if any orders were retrieved
    if open_orders_by_symbol is None or len(open_orders_by_symbol) == 0:
        return []
    #convert the retrieved orders into a dataframe
    open_orders_dataframe = pandas.DataFrame(
        list(open_orders_by_symbol),
        columns= open_orders_by_symbol[0]._asdict().keys
    )
    #From the open orders dataframe, filter orders by comment
    open_orders_dataframe = open_orders_dataframe[open_orders_dataframe['comment'] == comment]
    #create a list to store the open order numbers
    open_orders = []
    #iterate through the dataframe and add order numbers to the list
    for order in open_orders_dataframe['ticket']:
        open_orders.append(order)
    # Return the open orders
    return open_orders

#function to cancel orders based upon filters
def cancel_filtered_orders(symbol, comment):
    """
    function to cancel a list of filtered orders. Based upon two filters: symbol and comment
    """
    #Retrieve a list of orders based on filters
    orders = get_filtered_list_of_orders(symbol=symbol, comment=comment)
    if len(orders) > 0 :
        #iterate throug hand cancel
        for order in orders:
            cancel_outcome = cancel_order(order)
            if cancel_outcome is not True:
                return False
        #At conclusion of iteration, return True
        return True

    else:
        return True
    
    
def get_all_open_orders(symbol):
    """
    Function to retrieve all open orders from MT5
    """
    logging.info("Retrieving all Open Orders")
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for position in positions:
            logging.info(f"Open position ID: {position.ticket}, Profit: {position.profit}")
    else:
        logging.info(f"No open positions for symbol {symbol}")        
    return positions
    
def close_trade(symbol):
    print(f"Closing Orders for: {symbol}")
    positions = mt5.positions_get(symbol=symbol)
    
    if positions:
        for position in positions:
            # logging.info(f"Open position: {position.ticket}, Profit: {position.profit} , {position.volume} lots")
            
            #Close trade if its a buy and price is above a certain level
            current_price = mt5.symbol_info_tick(symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
            
            if (position.profit>0):
                    logging.info(f"Closing Position ID:{position.ticket}, made on:{position.time},  Profit Gained:{position.profit}")
                    # Create a close request
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "position": position.ticket,  # Ticket number of the position to close
                        "price": current_price,
                        "deviation": 20,
                        "magic": 234000,
                        "comment": "Python script close order",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    # Send the close order
                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        print(f"Failed to close position {position.ticket}, retcode={result.retcode}")
                    else:
                        print(f"Position {position.ticket} closed successfully")
        else:
            print("No open positions to close")