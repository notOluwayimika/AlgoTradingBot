import json
import os
import pandas
import ema_cross_strategy
import time
import logging
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading

class LogWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bot Logs")
        self.geometry("600x400")
        
        #Create a scrolled Text Widget
        self.text_area=ScrolledText(self,wrap=tk.WORD, state='disabled')
        self.text_area.pack(fill=tk.BOTH, expand = True)
        
    def write_log(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message)
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')
        
def run_bot(log_window):
    process = subprocess.Popen(['python', 'main.py'], stdout= subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = process.stdout.readline()
        if output:
            log_window.write_log(output)
        elif process.poll() is not None:
            break
        
def start_bot():
    log_window = LogWindow()
    threading.Thread(target=run_bot, args=(log_window,)).start()
    log_window.mainloop()


#custom libs
import mt5_lib


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#function to import settings from settings.jsom
def get_project_settings(filepath):
    #Check if file exists
    # if os.path.exists(importFilepath):
    #     f = open(importFilepath, "r")
    #     project_settings = json.load(f)
    #     f.close()
    #     return project_settings
    # else:
    #     return ImportError("Settings.json does not exist at the provided location")
    with open(filepath, 'r') as file:
        return json.load(file)

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
    if startup[0]: 
        logging.info("Metatrader Startup Successful")
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
        return [True]
    #default return false
    return [False]

def setup_gui():
    def save_settings():
        # Collect data from the user input fields
        mt5_settings = {
            "username": username_entry.get(),
            "password": password_entry.get(),
            "server": server_entry.get(),
            "mt5Pathway": filedialog.askopenfilename(title="Select MT5 Terminal"),
            "symbols": [symbols_entry.get()],
            "timeframe": timeframe_entry.get(),
            "pip_size": float(pip_size_entry.get())
        }    
        settings = {
            "mt5": mt5_settings
        }
        save_path = filedialog.asksaveasfilename(defaultextension=".json", title="Save Settings")
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Saved", "Settings Saved Succesfully")
            root.destroy()
            # Run bot with save settings
            run_strategy(settings)
    root = tk.Tk()
    root.title("Trading Bot Settings")

    # Username
    tk.Label(root, text="MT5 Username:").grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(root)
    username_entry.grid(row=0, column=1, padx=10, pady=5)

    # Password
    tk.Label(root, text="MT5 Password:").grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(root, show='*')
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    # Server
    tk.Label(root, text="MT5 Server:").grid(row=2, column=0, padx=10, pady=5)
    server_entry = tk.Entry(root)
    server_entry.grid(row=2, column=1, padx=10, pady=5)
    

    # Symbols
    tk.Label(root, text="Symbols (comma-separated):").grid(row=3, column=0, padx=10, pady=5)
    symbols_entry = tk.Entry(root)
    symbols_entry.grid(row=3, column=1, padx=10, pady=5)

    # Timeframe
    tk.Label(root, text="Timeframe:").grid(row=4, column=0, padx=10, pady=5)
    timeframe_entry = tk.Entry(root)
    timeframe_entry.grid(row=4, column=1, padx=10, pady=5)

    # Pip size
    tk.Label(root, text="Pip Size:").grid(row=5, column=0, padx=10, pady=5)
    pip_size_entry = tk.Entry(root)
    pip_size_entry.grid(row=5, column=1, padx=10, pady=5)

    # Save button
    save_button = tk.Button(root, text="Save Settings and Start Bot", command=save_settings)
    save_button.grid(row=6, column=0, columnspan=2, pady=20)

    root.mainloop()
    
# GUI function to start the bot and show terminal logs
def start_bot_gui(project_settings):
    root = tk.Tk()
    root.title("Trading Bot - Logs")

    # Create a frame for the logs
    log_frame = tk.Frame(root)
    log_frame.pack(fill=tk.BOTH, expand=True)

    # Create a scrolled text widget for displaying logs
    log_text = ScrolledText(log_frame, wrap=tk.WORD, state='disabled', height=20)
    log_text.pack(fill=tk.BOTH, expand=True)

    # Exit button
    def on_exit():
        root.quit()
        root.destroy()
        
    def close_trades():
        mt5_lib.close_trade(symbol= project_settings["mt5"]["symbols"][0])
        
    def get_trades():
        mt5_lib.get_all_open_orders(symbol=project_settings["mt5"]["symbols"][0])

    exit_button = tk.Button(root, text="Exit", command=on_exit)
    exit_button.pack(pady=10)
    
    close_trade_button = tk.Button(root, text="Close Trades", command=close_trades)
    close_trade_button.pack(padx=5, pady=10)
    
    get_button =  tk.Button(root, text="Get Open Positions", command=get_trades)
    get_button.pack(padx=5, pady=10)
    # Logger to display messages in the GUI
    class GuiLogger(logging.Handler):
        def __init__(self, widget):
            super().__init__()
            self.widget = widget

        def emit(self, record):
            msg = self.format(record)
            self.widget.config(state='normal')
            self.widget.insert(tk.END, msg + '\n')
            self.widget.config(state='disabled')
            self.widget.yview(tk.END)

    # Set up the logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    gui_logger = GuiLogger(log_text)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    gui_logger.setFormatter(formatter)
    logger.addHandler(gui_logger)

    def bot_logic():
        print("This is an Algorithmich Trading Bot")
        symbols = project_settings['mt5']['symbols']
        #run start up procedure
        startup = start_up(project_settings=project_settings)
        #if startup successful, start trading while loop
        if startup[0]:
            #Set a variable for the current time
            current_time = 0
            #set a variable for previous time
            previous_time = 0
            #specify startup time frame
            timeframe= project_settings['mt5']['timeframe']

            while 1:
                #Get a value for current time,  use BTCUSD as it trades 24/7
                time_candle = mt5_lib.get_candlesticks(
                    symbol="BTCUSD",
                    timeframe=timeframe,
                    number_of_candlesticks=1
                )
                #Extract the time
                current_time = time_candle['time'][0]
                
                #compare current time with previous time
                if current_time != previous_time:
                    #this means that a new candle has occured
                    print("New Candle, Trade time")
                    #Update previous time so that it is given the new current time
                    previous_time = current_time
                    strategy = run_strategy(project_settings=project_settings)
                    # print(strategy)
                    
                else:
                    #No new candle has occured
                    print("No new candle, sleeping")
                    time.sleep(61)
        for symbol in symbols:
            logging.info(f"Running strategy for {symbol}")
            # Implement strategy logic here...
            # Simulate bot running by sleeping
            for i in range(10):
                logging.info(f"Processing {symbol} - step {i + 1}")
                time.sleep(1)

    # Run the bot logic in a separate thread to keep the GUI responsive
    bot_thread = threading.Thread(target=bot_logic, daemon=True)
    bot_thread.start()

    root.protocol("WM_DELETE_WINDOW", on_exit)
    root.mainloop()

#function to run the strategy
def run_strategy(project_settings):
    """
        Function to run the strategy for trading bot
    """
    #Extract the symbols to be traded
    symbols = project_settings['mt5']['symbols']
    #extract the timeframe
    timeframe = project_settings['mt5']['timeframe']
    #strategy risk management
    
    #run through the strategy of the specified symbols
    #iterate through each of the symbols
    for sym in symbols:
        # strategy risk management
        #Generate comment string
        comment_string = f"Hybrid_strategy_{sym}"

        #Trade Strategy
        data = ema_cross_strategy.hybrid_strategy(
            symbol = sym,
            timeframe= timeframe,
        )

    return True




# Main function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Check if settings file is provided as an argument
    settings_filepath = "./settings.json"
    Settings=True
    while Settings:
        if os.path.exists(settings_filepath):
            import_filepath = "settings.json"
            project_settings = get_project_settings(import_filepath)
            Settings=False
            start_bot_gui(project_settings=project_settings)      
        else:
            # No settings file provided, launch the settings GUI
            setup_gui()
            Settings=True
    # #Set up import file path
    # # import_filepath = "C:/Users/yimzi/Documents/AlgorithmicTradingBot/settings.json"
    # import_filepath = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/yimzi/Documents/AlgorithmicTradingBot/settings.json"
    # #import project settings 
    # project_settings = get_project_settings(import_filepath)


    # #run start up procedure
    # startup = start_up(project_settings=project_settings)
    # #for each symbol, return a dataframe of candles
    # symbols = project_settings['mt5']['symbols']
    
    # #make all columns show
    # pandas.set_option('display.max_columns', None)
    # #if startup successful, start trading while loop
    # if startup[0]:
    #     #Set a variable for the current time
    #     current_time = 0
    #     #set a variable for previous time
    #     previous_time = 0
    #     #specify startup time frame
    #     timeframe= project_settings['mt5']['timeframe']
    #     #start while loop
    #     balance = startup[1]

    #     while 1:
    #         #Get a value for current time,  use BTCUSD as it trades 24/7
    #         time_candle = mt5_lib.get_candlesticks(
    #             symbol="BTCUSD",
    #             timeframe=timeframe,
    #             number_of_candlesticks=1
    #         )
    #         #Extract the time
    #         current_time = time_candle['time'][0]
            
    #         #compare current time with previous time
    #         if current_time != previous_time:
    #             #this means that a new candle has occured
    #             print("New Candle, Trade time")
    #             #Update previous time so that it is given the new current time
    #             previous_time = current_time
    #             strategy = run_strategy(project_settings=project_settings)
    #             # print(strategy)
    #             close = mt5_lib.close_trade(symbol=symbols[0])
                
    #         else:
    #             #No new candle has occured
    #             print("No new candle, sleeping")
    #             time.sleep(61)


        
        

