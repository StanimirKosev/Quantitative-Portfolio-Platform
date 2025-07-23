import { CarouselItem } from "./ui/carousel";
import { Card, CardContent } from "./ui/card";
import PortfolioPieChart from "./PortfolioPieChart";
import PortfolioRadarChart from "./PortfolioRadarChart";

const PortfolioOverviewSlide = () => {
  return (
    <CarouselItem className="px-2 sm:px-4">
      <Card className="flex flex-col h-full bg-black">
        <CardContent className="flex flex-col lg:flex-row flex-1 pb-0 p-2 sm:p-4 gap-4 lg:gap-2 justify-center items-center">
          <PortfolioPieChart />
          <PortfolioRadarChart />
        </CardContent>
      </Card>
    </CarouselItem>
  );
};

export default PortfolioOverviewSlide;
