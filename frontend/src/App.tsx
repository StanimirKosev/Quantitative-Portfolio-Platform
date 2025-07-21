import { useIsFetching } from "@tanstack/react-query";
import LoadingBar from "./components/LoadingBar";
import PortfolioCarousel from "./components/PortfolioCarousel";
import Header from "./components/Header";
import { useCustomPortfolioStore } from "./store/customPortfolioStore";
import { useMatch, useNavigate } from "react-router-dom";
import { useEffect } from "react";

const App = () => {
  const isFetching = useIsFetching();
  const navigate = useNavigate();
  const { customPortfolio, clearCustomPortfolio } = useCustomPortfolioStore();
  const isCustom = !!useMatch("/custom-portfolio");

  useEffect(() => {
    if (!isCustom) clearCustomPortfolio();
    if (isCustom && !customPortfolio) navigate("/default-portfolio");
  }, [isCustom, customPortfolio, clearCustomPortfolio, navigate]);

  if (isFetching > 0) {
    return <LoadingBar message="Loading..." />;
  }

  return (
    <div className="flex flex-col min-h-screen w-full bg-background">
      <Header />
      <PortfolioCarousel />
    </div>
  );
};

export default App;
