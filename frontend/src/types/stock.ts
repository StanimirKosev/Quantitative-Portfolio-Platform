export interface StockQuote {
  id: string;
  price: number;
  time: string;
  exchange: string;
  quote_type: number;
  market_hours: number;
  change_percent: number;
  day_volume: string;
  change: number;
  last_size: string;
  price_hint: string;
}
