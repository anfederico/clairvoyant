import copy

class OpenedTrade():
    def __init__(self, Type, Date):
        self.Type = Type
        self.Date = Date    
    def __str__(self):
        return "{0}\n{1}".format(self.Type, self.Date)

class ClosedTrade(OpenedTrade):
    def __init__(self, Type, Date, Shares, Entry, Exit):
        super().__init__(Type, Date)
        self.Shares = float(Shares)
        self.Entry  = float(Entry)
        self.Exit   = float(Exit)
    def __str__(self):
        return "{0}\n{1}\n{2}\n{3}\n{4}".format(self.Type, self.Date, self.Shares, self.Entry, self.Exit)

class Position:
    def __init__(self, No, EntryPrice, Shares, ExitPrice=0, StopLoss=0):
        self.No         = No
        self.Type       = "None"
        self.EntryPrice = float(EntryPrice)
        self.Shares     = float(Shares)
        self.ExitPrice  = float(ExitPrice)
        self.StopLoss   = float(StopLoss)   
    
    def Show(self):
        print("No. {0}".format(self.No))
        print("Type:   {0}".format(self.Type))
        print("Entry:  {0}".format(self.EntryPrice))
        print("Shares: {0}".format(self.Shares))
        print("Exit:   {0}".format(self.ExitPrice))
        print("Stop:   {0}\n".format(self.StopLoss))

class LongPosition(Position):
    def __init__(self, No, EntryPrice, Shares, ExitPrice=0, StopLoss=0):
        super().__init__(No, EntryPrice, Shares, ExitPrice, StopLoss)
        self.Type = 'Long'

    def Close(self, Percent, CurrentPrice):
        Shares = self.Shares
        self.Shares *= 1.0-Percent
        return Shares*Percent*CurrentPrice

class ShortPosition(Position):
    def __init__(self, No, EntryPrice, Shares, ExitPrice=0, StopLoss=0):
        super().__init__(No, EntryPrice, Shares, ExitPrice, StopLoss)
        self.Type = 'Short' 

    def Close(self, Percent, CurrentPrice):
        Entry = self.Shares*Percent*self.EntryPrice
        Exit = self.Shares*Percent*CurrentPrice
        self.Shares *= 1.0-Percent
        if Entry-Exit+Entry <= 0: return 0
        else: return Entry-Exit+Entry

class Account():
    def __init__(self, InitialCapital):
        self.InitialCapital = float(InitialCapital)
        self.BuyingPower    = float(InitialCapital)
        self.No             = 0
        self.Date           = None
        self.Equity         = []
        self.Positions      = []
        self.OpenedTrades   = []
        self.ClosedTrades   = []

    def EnterPosition(self, Type, EntryCapital, EntryPrice, ExitPrice=0, StopLoss=0):
        EntryCapital = float(EntryCapital)
        if EntryCapital < 0: raise ValueError("Error: Entry capital must be positive")          
        elif EntryPrice < 0: raise ValueError("Error: Entry price cannot be negative.")
        elif self.BuyingPower < EntryCapital: raise ValueError("Error: Not enough buying power to enter position")          
        else: 
            self.BuyingPower -= EntryCapital
            Shares = EntryCapital/EntryPrice 
            if Type == 'Long': self.Positions.append(LongPosition(self.No, EntryPrice, Shares, ExitPrice, StopLoss))
            elif Type == 'Short': self.Positions.append(ShortPosition(self.No, EntryPrice, Shares, ExitPrice, StopLoss))    
            else: raise TypeError("Error: Invalid position type.")

            self.OpenedTrades.append(OpenedTrade(Type, self.Date))
            self.No += 1    

    def ClosePosition(self, Position, Percent, CurrentPrice):
        if Percent > 1 or Percent < 0: 
            raise ValueError("Error: Percent must range between 0-1.")
        elif CurrentPrice < 0:
            raise ValueError("Error: Current price cannot be negative.")                
        else: 
            self.ClosedTrades.append(ClosedTrade(Position.Type, self.Date, Position.Shares*Percent, Position.EntryPrice, CurrentPrice))
            self.BuyingPower += Position.Close(Percent, CurrentPrice)

    def PurgePositions(self):
        self.Positions = [p for p in self.Positions if p.Shares > 0]        
            
    def ShowPositions(self):
        for p in self.Positions: p.Show()

    def TotalValue(self, CurrentPrice):
        Temporary = copy.deepcopy(self)
        for Position in Temporary.Positions:
            Temporary.ClosePosition(Position, 1.0, CurrentPrice)
        return Temporary.BuyingPower