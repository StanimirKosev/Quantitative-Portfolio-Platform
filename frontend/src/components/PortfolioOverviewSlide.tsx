import { CarouselItem } from "./ui/carousel";
import { Card, CardContent } from "./ui/card";
import PortfolioPieChart from "./PortfolioPieChart";
import PortfolioRadarChart from "./PortfolioRadarChart";

const PortfolioOverviewSlide = () => {
  return (
    <CarouselItem>
      <Card className="flex flex-col h-full bg-black">
        <CardContent className="flex flex-row flex-1 pb-0 p-2 gap-2 justify-center items-center">
          <PortfolioPieChart />
          <PortfolioRadarChart />
        </CardContent>
      </Card>
    </CarouselItem>
  );
};

export default PortfolioOverviewSlide;
