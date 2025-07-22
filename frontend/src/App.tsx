import { useIsFetching } from "@tanstack/react-query";
import LoadingBar from "./components/LoadingBar";
import PortfolioCarousel from "./components/PortfolioCarousel";
import Header from "./components/Header";
import { useCustomPortfolioStore } from "./store/customPortfolioStore";
import { useMatch } from "react-router-dom";
import { useEffect } from "react";

const App = () => {
  const isFetching = useIsFetching();
  const { isCustomStateActive, clearCustomState } = useCustomPortfolioStore();
  const isDefaultMode = !!useMatch("/default-portfolio");

  useEffect(() => {
    if (isDefaultMode && isCustomStateActive()) clearCustomState();
  }, [isDefaultMode, isCustomStateActive, clearCustomState]);

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
