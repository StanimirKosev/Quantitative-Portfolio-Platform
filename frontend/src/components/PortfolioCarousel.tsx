import {
  Carousel,
  CarouselContent,
  CarouselPrevious,
  CarouselNext,
} from "./ui/carousel";
import type { CarouselApi } from "./ui/carousel";
import { useEffect, useState } from "react";
import ChartsSlides from "./ChartsSlides";
import PortfolioOverviewSlide from "./PortfolioOverviewSlide";

const PortfolioCarousel = () => {
  const [api, setApi] = useState<CarouselApi>();
  const [current, setCurrent] = useState<number>(0);
  const [count, setCount] = useState<number>(0);

  useEffect(() => {
    if (!api) {
      return;
    }

    setCount(api.scrollSnapList().length);
    setCurrent(api.selectedScrollSnap() + 1);

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap() + 1);
    });
  }, [api]);

  return (
    <Carousel className="w-full max-w-7xl mx-auto" setApi={setApi}>
      <CarouselContent>
        <PortfolioOverviewSlide />
        <ChartsSlides />
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
      <div className="w-full flex justify-center mt-4">
        <span className="px-2 py-1 text-base font-medium">
          Slide {current} of {count}
        </span>
      </div>
    </Carousel>
  );
};

export default PortfolioCarousel;
