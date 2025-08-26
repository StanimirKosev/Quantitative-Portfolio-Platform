import {
  Carousel,
  CarouselContent,
  CarouselPrevious,
  CarouselNext,
} from "./ui/carousel";
import ChartsSlides from "./ChartsSlides";
import PortfolioOverviewSlide from "./PortfolioOverviewSlide";
import EfficientFrontierSlide from "./EfficientFrontierSlide";
import CarouselIndicator from "./CarouselIndicator";

const PortfolioCarousel = () => {
  return (
    <div className="w-full px-2 sm:px-4">
      <Carousel className="w-full max-w-7xl mx-auto">
        <CarouselContent>
          <PortfolioOverviewSlide />
          <EfficientFrontierSlide />
          <ChartsSlides />
        </CarouselContent>
        <CarouselPrevious className="left-2 sm:left-4" />
        <CarouselNext className="right-2 sm:right-4" />
        <CarouselIndicator />
      </Carousel>
    </div>
  );
};

export default PortfolioCarousel;
