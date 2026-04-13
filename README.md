# BIST Algorithmic Trading & Backtest Simulation

This project is a modular backtesting engine developed from scratch to test various algorithmic trading strategies (Trend Following, Mean Reversion, DCA, etc.) on Borsa Istanbul (BIST) equities.

## Simulation Rules and Dynamics

The system is designed with strict parameters to simulate real market conditions accurately:

* Realistic Commission Calculation: A broker commission rate of 0.2% is automatically deducted from the balance for every buy and sell transaction. Unrealized, commission-free profits are excluded from the reports.
* No Lookahead Bias: The engine strictly progresses day-by-day in the time series. The algorithmic strategies cannot access the next day's price data when executing a decision.
* Strict Risk Management: To mitigate the financial risks of aggressive strategies such as DCA or Grid, Max Drawdown metrics are continuously monitored and logged.
* Modular Architecture: Data retrieval (Data Handler), simulation mechanics (Backtest Engine), and trading logics (Strategies) operate in completely isolated environments.

## Tracked Assets
THYAO, TUPRS, KCHOL, YEOTK, ASTOR, HEKTS, BIMAS, TCELL, AKBNK, YKBNK.