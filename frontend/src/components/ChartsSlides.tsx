import { useQuery } from "@tanstack/react-query";
import { CarouselItem } from "./ui/carousel";
import { useRegimeStore } from "../store/regimeStore";
import type { SimulateChartsResponse } from "../types/portfolio";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";
import { API_BASE_URL } from "../lib/api";

const ChartsSlides = () => {
  const { selectedRegime } = useRegimeStore();
  const { customPortfolioCharts, isCustomStateActive } =
    useCustomPortfolioStore();

  const { data: defaultPortfolioCharts } = useQuery<SimulateChartsResponse>({
    queryKey: ["simulate", "default", selectedRegime],
    queryFn: async () => {
      const res = await fetch(
        `${API_BASE_URL}/api/simulate/${selectedRegime}`,
        {
          method: "POST",
        }
      );
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(`HTTP ${res.status}: ${errorData.detail}`);
      }
      return res.json();
    },
    enabled: !!selectedRegime && !isCustomStateActive(),
  });

  const dataSources = customPortfolioCharts || defaultPortfolioCharts;

  const chartsData = [
    {
      src: `${API_BASE_URL}${dataSources?.simulation_chart_path}`,
      alt: "Monte Carlo Simulation",
    },
    {
      src: `${API_BASE_URL}${dataSources?.correlation_matrix_chart_path}`,
      alt: "Correlation Matrix",
    },
    {
      src: `${API_BASE_URL}${dataSources?.risk_factors_chart_path}`,
      alt: "Risk Factor Analysis",
    },
  ];

  return (
    <>
      {chartsData.map((chart, idx) => (
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
