import csv
import os

'''
Args:
    1. Ticker (str): This is the stock you are reading and writing data for
                     Make sure infile is labeled  -> [Ticker]_RawData.csv
                     Expect outfile to be labeled -> [Ticker]_SSOvSSC_TrainingData.csv
                     Either can be changed
      
    2. InfilePath  (str): Path to infile
    3. OutfilePath (str): Path to outfile 
   
Assumptions: 
    Infile is present and labeled [Ticker]_RawData.csv 
    
Operations:
    This function will read/store the Slow Stochastic Oscillator (SSO) vs. Social Sentiment Close (SSC) values
    This function will also calculate the change in price the following day or Next Day Change (NDC)
    These three values will be written on a single line for each day in the order SSO, SSC, NDC to a CSV outfile
    
Returns: 
    Nothing

Note:
    Anybody using this will likely need to modify the function to suit their particular values of interest
'''

def MakeTraingingData(Ticker, InfilePath, OutfilePath):

    with open(os.path.join(InfilePath, '%s_RawData.csv' % Ticker), 'r') as infile:
        reader = csv.reader(infile)
    
        # Skip over header (or Header = next(reader))
        next(reader)
        Header = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'SSO', 'SMA', 'S-Open', 'S-High', 'S-Low', 'S-Close']
        
        RawData = []
        for row in reader:
            if row[7] != '' and row[12] != '':             
                TradingDay = {}                             
                i = 0                                     # Ensure SSO and S-Close values are available
                while i < len(row):                       # Organize each day into a dictionary
                    TradingDay[Header[i]] = row[i]        # Append each day to a list of all days
                    i += 1
                RawData.append(TradingDay)                      
           
    with open(os.path.join(OutfilePath, '%s_SSOvSSC_TrainingData.csv' % Ticker), 'w') as csvfile:
        fieldnames = ['SSO', 'SSC', 'NDC']
        outfile = csv.DictWriter(csvfile, fieldnames=fieldnames)
        NextDayChange = False
        for TradingDay in RawData[::-1]:
            if NextDayChange != False:
                SSO  = round(float(TradingDay['SSO']),2)
                SSC  = round(float(TradingDay['S-Close']),2)
                outfile.writerow({  
                                    'SSO': SSO,
                                    'SSC': SSC,
                                    'NDC': NextDayChange,
                                })    
            NextDayChange = round(100*(float(TradingDay['Close'])-float(TradingDay['Open']))/float(TradingDay['Open']),2)
        
'''
Example:
InfilePath  = 'path/to/RawData'
OutfilePath = 'path/to/TrainingData'
MakeTraingingData('TSLA', InfilePath, OutfilePath)
'''
