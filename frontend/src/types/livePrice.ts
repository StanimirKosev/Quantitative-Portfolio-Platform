export interface StockQuote {
  id: string; // ticker
  price: number;
  time: string;
  exchange: string;
  quote_type: number;
  market_hours: number | undefined; // 1 - market open; undefined - market closed
  change_percent: number | undefined; // number - change since last close; undefined - market closed
  day_volume: string;
  change: number;
  last_size: string;
  price_hint: string;
}
