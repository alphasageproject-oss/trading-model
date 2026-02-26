# Fundamental Data Model

class FundamentalData:
    def __init__(self, company_name, revenue, earnings, assets, liabilities):
        self.company_name = company_name
        self.revenue = revenue
        self.earnings = earnings
        self.assets = assets
        self.liabilities = liabilities

    def financial_health(self):
        return self.assets - self.liabilities
    
    def profit_margin(self):
        if self.revenue > 0:
            return self.earnings / self.revenue
        return 0.0
    
    def __str__(self):
        return f"{self.company_name} - Revenue: {self.revenue}, Earnings: {self.earnings}
