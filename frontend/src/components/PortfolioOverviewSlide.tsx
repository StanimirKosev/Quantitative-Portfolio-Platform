import { CarouselItem } from "./ui/carousel";
import { Card, CardContent, CardDescription } from "./ui/card";
import PortfolioPieChart from "./PortfolioPieChart";
import PortfolioRadarChart from "./PortfolioRadarChart";
import LivePriceWidget from "./LivePriceWidget";
import { useQuery } from "@tanstack/react-query";
import type { PortfolioResponse } from "../types/portfolio";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";
import { API_BASE_URL } from "../lib/api";

const overviewSlideStyles = {
  carouselItem: "px-12 sm:px-16",
  card: "h-full bg-black",
  cardContent: "flex flex-col h-full px-2 sm:px-4 pb-2 sm:pb-4",
  widgetContainer: "flex justify-center items-center pt-8",
  analysisContainer: "flex justify-center",
  analysisText: "text-center text-xs sm:text-sm text-muted-foreground",
  chartsGrid:
    "flex flex-col lg:flex-row flex-1 gap-4 lg:gap-12 justify-center items-center -mt-4",
};

const PortfolioOverviewSlide = () => {
  const { customPortfolio, isCustomStateActive } = useCustomPortfolioStore();

  const { data: defaultPortfolio } = useQuery<PortfolioResponse>({
    queryKey: ["portfolio", "default"],
    queryFn: () =>
      fetch(`${API_BASE_URL}/api/portfolio/default`).then((res) => res.json()),
    enabled: !isCustomStateActive(),
  });

  const dataSources = customPortfolio || defaultPortfolio;
  const portfolioAssets = dataSources?.portfolio_assets;

  return (
    <CarouselItem className={overviewSlideStyles.carouselItem}>
      <Card className={overviewSlideStyles.card}>
        <CardContent className={overviewSlideStyles.cardContent}>
          <div className={overviewSlideStyles.widgetContainer}>
            <LivePriceWidget portfolioAssets={portfolioAssets} />
          </div>
          <div className={overviewSlideStyles.analysisContainer}>
            <CardDescription className={overviewSlideStyles.analysisText}>
              Analysis period: {dataSources?.start_date} -{" "}
              {dataSources?.end_date}
            </CardDescription>
          </div>
          <div className={overviewSlideStyles.chartsGrid}>
            <PortfolioPieChart portfolioAssets={portfolioAssets} />
            <PortfolioRadarChart />
          </div>
        </CardContent>
      </Card>
    </CarouselItem>
  );
};

export default PortfolioOverviewSlide;
