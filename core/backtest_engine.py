import pandas as pd

class BacktestEngine:
    # Motora 'ticker' parametresi ekledik, böylece loglarda kimin işlemi olduğunu bileceğiz.
    def __init__(self, data, ticker="HİSSE", initial_balance=100.0, commission_rate=0.002, slippage_rate=0.001):
        self.data = data
        self.ticker = ticker  # Hangi hissede olduğumuzu hafızaya aldık
        self.initial_balance = initial_balance
        self.balance = initial_balance  
        self.position = 0               
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        self.trade_history = []         
        self.portfolio_values = []      

    def execute_trade(self, date, price, action, amount_ratio=1.0):
        date_str = date.strftime('%Y-%m-%d')
        slippage_factor = 1 + (self.slippage_rate if action == 'BUY' else -self.slippage_rate)
        execution_price = price * slippage_factor

        if action == 'BUY' and self.balance > 0:
            invest_amount = self.balance * amount_ratio
            commission = invest_amount * self.commission_rate
            net_invest_amount = invest_amount - commission
            shares_to_buy = net_invest_amount / execution_price 
            
            self.position += shares_to_buy
            self.balance -= invest_amount 
            
            self.trade_history.append({'date': date, 'action': 'BUY', 'price': execution_price, 'shares': shares_to_buy, 'commission': commission})
            
            # Ekrana basarken başına köşeli parantez ile HİSSE ADINI ekliyoruz
            print(f"  [{self.ticker}] [+] ALIM  | Tarih: {date_str} | Fiyat: {execution_price:8.2f} TL  | Adet: {shares_to_buy:8.2f} | Kalan: {self.balance:8.2f} TL")

        elif action == 'SELL' and self.position > 0:
            shares_to_sell = self.position * amount_ratio
            gross_revenue = shares_to_sell * execution_price
            commission = gross_revenue * self.commission_rate
            net_revenue = gross_revenue - commission
            
            self.position -= shares_to_sell
            self.balance += net_revenue
            
            self.trade_history.append({'date': date, 'action': 'SELL', 'price': execution_price, 'shares': shares_to_sell, 'commission': commission})
            
            print(f"  [{self.ticker}] [-] SATIM | Tarih: {date_str} | Fiyat: {execution_price:8.2f} TL  | Adet: {shares_to_sell:8.2f} | Kalan: {self.balance:8.2f} TL")

    def run(self, strategy):
        strategy.prepare_indicators(self.data)
        
        for i in range(len(self.data)):
            current_date = self.data.index[i]
            current_row = self.data.iloc[i]
            current_price = current_row['Close']
            
            action, amount_ratio = strategy.generate_signal(i, current_row)
            
            if action in ['BUY', 'SELL']:
                self.execute_trade(current_date, current_price, action, amount_ratio)
                
            current_portfolio_value = self.balance + (self.position * current_price)
            self.portfolio_values.append({'date': current_date, 'total_value': current_portfolio_value})
            
        final_value = self.balance + (self.position * self.data.iloc[-1]['Close'])
        return self.trade_history, pd.DataFrame(self.portfolio_values), final_value