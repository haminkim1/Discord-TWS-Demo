class Options_Contract:
    def __init__(self, action, symbol, strike, right, expiry_date, analyst_name):
        self.action = action
        self.symbol = symbol
        self.strike = strike
        self.right = right
        self.expiry_date = expiry_date
        self.analyst_name = analyst_name
    
    def __str__(self):
        return f"Action: {self.action}\n" \
            f"Symbol: {self.symbol}\n" \
            f"Strike: {self.strike}\n" \
            f"Right: {self.right}\n" \
            f"Expiry: {self.expiry_date}\n" \
            f"Analyst Name: {self.analyst_name}"
            