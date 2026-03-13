from ..finance.twelvedata import historical_data as hd


def register_finance_tools(mcp) -> None:
    @mcp.tool()
    def historical_data(symbol: str, start_date: str, end_date: str, interval: str) -> str:
        """Historical Stock Market Valuations

        Args:
            symbol: asset symbol
            start_date: start date
            end_date: end date
            interval: 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 8h, 1day, 1week, 1month
        """
        data = hd.shoot(symbol, start_date, end_date, interval)
        return data