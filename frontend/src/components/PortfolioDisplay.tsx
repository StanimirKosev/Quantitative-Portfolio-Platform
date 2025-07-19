import { useQuery } from "@tanstack/react-query";
import { useRegimeStore } from "../store/regimeStore";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
} from "./ui/carousel";
import type { CarouselApi } from "./ui/carousel";
import { useEffect, useState } from "react";

const PortfolioDisplay = () => {
  const [api, setApi] = useState<CarouselApi>();
  const [current, setCurrent] = useState<number>(0);
  const [count, setCount] = useState<number>(0);
  const { selectedRegime } = useRegimeStore();

  const apiUrl = import.meta.env.VITE_API_URL;

  const { data } = useQuery({
    queryKey: ["simulate", selectedRegime],
    queryFn: () =>
      fetch(`${apiUrl}/api/simulate/${selectedRegime}`, {
        method: "POST",
      }).then((res) => res.json()),
    enabled: !!selectedRegime,
  });

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

  const chartData = [
    {
      src: `${apiUrl}${data?.charts.simulation_chart_path}`,
      alt: "Monte Carlo Simulation",
    },
    {
      src: `${apiUrl}${data?.charts.correlation_matrix_chart_path}`,
      alt: "Correlation Matrix",
    },
    {
      src: `${apiUrl}${data?.charts.risk_factors_chart_path}`,
      alt: "Risk Factor Analysis",
    },
  ];

  return (
    <Carousel className="w-full max-w-7xl mx-auto" setApi={setApi}>
      <CarouselContent>
        {chartData.map((chart, idx) => (
          <CarouselItem key={idx} className="flex flex-col items-center">
            <img
              src={chart.src}
              alt={chart.alt}
              className="w-full h-[85vh] object-contain rounded-lg shadow-md"
            />
          </CarouselItem>
        ))}
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

export default PortfolioDisplay;
