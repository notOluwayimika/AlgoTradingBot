import json
import os
import pandas

#custom libs
import mt5_lib

#function to import settings from settings.jsom
def get_project_settings(importFilepath):
    #Check if file exists
    if os.path.exists(importFilepath):
        #open file
        f = open(importFilepath, "r")
        #Get file info
        project_settings = json.load(f)
        #close file
        f.close()
        #return project settings
        return project_settings
    else:
        return ImportError("Settings.json does not exist at the provided location")

#function to repeat startup procedures
def start_up(project_settings):
    """
    Function to manage start up procedures for App

    includes starting/testing
    initializing symbols and anything else to ensure successful app start
    :param project_settings: json object of settings 
    :return Boolean true is app start is successful
    
    """
    #start Metatrader 5
    startup = mt5_lib.start_mt5(project_settings=project_settings)
    #let user know if startup successful
    if startup: 
        print("Metatrader Startup Successful")
        #initialize symbols
        #extract symbols from project settings
        symbols = project_settings['mt5']['symbols']
        #iterate through symbols to enable
        for symbol in symbols:
            outcome = mt5_lib.initialize_symbol(symbol)
            #update the user
            if outcome is True:
                print(f"symbol {symbol} initialized")
            else:
                raise Exception(f"{symbol} not initialized")
        return True
    #default return false
    return False



# Main function
if __name__ == '__main__':
    print("This is an algorithmic Trading Bot")
    #Set up import file path
    import_filepath = "C:/Users/yimzi/Documents/AlgorithmicTradingBot/settings.json"
    #import project settings 
    project_settings = get_project_settings(import_filepath)


    #run start up procedure
    startup = start_up(project_settings=project_settings)
    #for each symbol, return a datafram of candles
    symbols = project_settings['mt5']['symbols']
    for sym in symbols:
        candlesticks = mt5_lib.get_candlesticks(
            symbol=sym,
            timeframe= project_settings['mt5']['timeframe'],
            number_of_candlesticks=1000
        )
        #make all columns show
        pandas.set_option('display.max_columns', None)
        print(candlesticks)
    

