import MetaTrader5 as mt5
import pandas

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
    mt5_pathway = project_settings['mt5']['mt5.pathway']
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
        return True
    #Default outcome
    return False 

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