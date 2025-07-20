import { useQuery } from "@tanstack/react-query";
import { CarouselItem } from "./ui/carousel";
import { useRegimeStore } from "../store/regimeStore";
import type { SimulateChartsResponse } from "../types/portfolio";

const ChartsSlides = () => {
  const { selectedRegime } = useRegimeStore();

  const apiUrl = import.meta.env.VITE_API_URL;

  const { data } = useQuery<SimulateChartsResponse>({
    queryKey: ["simulate", selectedRegime],
    queryFn: async () => {
      const res = await fetch(`${apiUrl}/api/simulate/${selectedRegime}`, {
        method: "POST",
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(`HTTP ${res.status}: ${errorData.detail}`);
      }
      return res.json();
    },
    enabled: !!selectedRegime,
  });

  const chartData = [
    {
      src: `${apiUrl}${data?.simulation_chart_path}`,
      alt: "Monte Carlo Simulation",
    },
    {
      src: `${apiUrl}${data?.correlation_matrix_chart_path}`,
      alt: "Correlation Matrix",
    },
    {
      src: `${apiUrl}${data?.risk_factors_chart_path}`,
      alt: "Risk Factor Analysis",
    },
  ];

  return (
    <>
      {chartData.map((chart, idx) => (
        <CarouselItem key={idx} className="flex flex-col items-center">
          <img
            src={chart.src}
            alt={chart.alt}
            className="w-full h-[85vh] object-contain rounded-lg shadow-md"
          />
        </CarouselItem>
      ))}
    </>
  );
};

export default ChartsSlides;
