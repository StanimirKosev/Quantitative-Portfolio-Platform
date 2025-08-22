# Optimization Frontend Tasks

**OPT-F-001: Portfolio Carousel Integration**
Status: Completed
Priority: High

Add optimization support to the existing portfolio carousel interface with clean loading states and efficient frontier visualization.

## Acceptance Criteria

**Carousel Integration:**

- Add "Optimize Portfolio" button/tab to existing portfolio carousel
- Integrate with existing regime selection (Historical, Fiat Debasement, Geopolitical Crisis)
- Maintain consistency with current simulation carousel design patterns
- Support both default and custom portfolio optimization

**Loading State Management:**

- Simple loading spinner during optimization (should be quick ~2-5 seconds)
- Clean loading message: "Optimizing portfolio..."
- Disable user interactions during optimization process
- Error handling for optimization failures with user-friendly messages

## Technical Implementation

**State Management:**

- Use existing TanStack Query for optimization state management
- Track: `isLoading`, `optimizationResults`, `error`
- Integrate with existing `regimeStore` for regime selection

**API Integration:**

- Use existing TanStack Query patterns for optimization API calls
- POST to `/api/optimize/{regime}` or `/api/optimize/custom`
- Simple request/response pattern
- Error boundaries for optimization failures

---

**OPT-F-002: Efficient Frontier Visualization**
Status: Completed
Priority: High
Dependencies: OPT-F-001

Create interactive scatter plot visualization showing the efficient frontier curve with portfolio optimization results.

## Acceptance Criteria

**Main Visualization:**

- Scatter plot with connected line showing the efficient frontier curve
- X-axis: Risk (Volatility) - displayed as percentages (8%, 12%, 20%)
- Y-axis: Expected Return - displayed as percentages (4%, 8%, 12%)
- Special highlight: Max Sharpe ratio point with different color/larger dot

**Visual Elements:**

- Regular frontier points: Small blue dots connected by smooth curve
- Max Sharpe point: Larger orange/red dot with distinct styling
- Grid lines for easy reading
- Clean, professional styling matching existing charts
- Responsive design for different screen sizes

**Interactive Features:**

- Hover tooltips showing detailed portfolio information
- Smooth animations and transitions
- Zoom/pan capabilities for detailed analysis
- Click interactions for portfolio selection

## Tooltip Information

**Standard Frontier Point Hover:**

```
Expected Return: 8.5%
Risk (Volatility): 12.3%
Sharpe Ratio: 0.692
Portfolio Weights:
" BTC-EUR: 45.2%
" SPYL.DE: 32.8%
" 4GLD.DE: 22.0%
```

**Max Sharpe Point Hover:**

```
<� OPTIMAL PORTFOLIO
Expected Return: 9.2%
Risk (Volatility): 13.1%
Sharpe Ratio: 0.758 (Maximum)
Portfolio Weights:
" BTC-EUR: 38.5%
" SPYL.DE: 41.2%
" 4GLD.DE: 20.3%
```

## Chart Styling & Layout

**Title & Labels:**

- Title: "Efficient Frontier - Risk vs Return"
- Subtitle: "Each point represents an optimal portfolio for its risk level"
- X-axis label: "Risk (Volatility %)"
- Y-axis label: "Expected Return (%)"

**Legend:**

- Blue line: "Efficient Frontier"
- Orange dot: "Maximum Sharpe Ratio"

**Footer Information:**

- "Analysis period: [date range] | Risk-free rate: 2.5%"

## Technical Implementation

**Chart Library:**

- Use Recharts (consistent with existing visualizations)
- ScatterChart with Line overlay for frontier curve
- Custom dot components for Max Sharpe highlighting
- Custom tooltip components for detailed information

**Data Processing:**

- Transform API response from decimal to percentage format
- Sort frontier points by risk for smooth curve rendering
- Identify and flag Max Sharpe point for special styling
- Handle edge cases (single point, optimization failures)

**Responsive Design:**

- Mobile-friendly touch interactions
- Adaptive chart sizing
- Collapsible legends on small screens
- Optimized tooltip positioning

---

**OPT-F-003: Live Portfolio Ticker**
Status: Not Started
Priority: Medium

Add real-time asset price ticker using WebSocket connections to show live market data for portfolio assets in the header area.

## Acceptance Criteria

**Live Ticker Display:**

- Replace analysis period text with live price ticker: `🟢 LIVE • BTC +2.1% • SPYL -0.8% • 4GLD +0.3% • 5MVW +1.2% • Updated 10:34 AM`
- Show live price changes for portfolio assets only (not all possible assets)
- Color-coded price changes: green (+), red (-), gray (no change)
- Update frequency: Every 10-15 seconds during market hours
- "MARKET CLOSED" indicator outside trading hours instead of green dot

**Contextual Integration:**

- Shows live performance of assets visible in portfolio composition (first slide)
- Creates immediate connection: "I see BTC allocation → BTC is up 2.1% right now"
- Updates based on current portfolio context (default vs custom)
- Smooth transitions when switching between portfolios

**Visual Design:**

- Small, subtle typography that doesn't dominate the header
- Positioned in center-top where analysis period currently shows
- Gentle color transitions for price changes
- Optional pause updates on hover to prevent reading distraction
- Mobile-responsive: fewer tickers or scrolling on small screens

## Technical Implementation

**WebSocket Connection:**

- New endpoint: `/api/live/prices/ws`
- Send current portfolio tickers on connection
- Receive periodic price updates for those specific assets
- Handle connection failures with graceful fallback ("PRICES UNAVAILABLE")

**Data Processing:**

- Track price changes since market open (or last close)
- Format percentages with +/- indicators
- Handle market hours detection for different exchanges
- Cache last known prices for connection failures

**State Management:**

- New Zustand store: `useLivePricesStore`
- Track: `isConnected`, `assetPrices`, `lastUpdated`, `marketStatus`
- Integration with existing portfolio stores to get current asset list
- Auto-reconnect logic with exponential backoff

**Header Integration:**

- Replace current "Analysis period: 2022-01-01 - 2024-12-31" text
- Show compact date range on hover or in tooltip if needed
- Maintain clean header layout without crowding regime tabs or customize button

---
