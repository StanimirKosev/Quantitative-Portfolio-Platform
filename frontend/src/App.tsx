import PortfolioCarousel from "./components/PortfolioCarousel";
import Header from "./components/Header";
import { useCustomPortfolioStore } from "./store/customPortfolioStore";
import { useMatch } from "react-router-dom";
import { useEffect } from "react";
import PortfolioAnalysisLoader from "./components/PortfolioAnalysisLoader";

const appStyles = {
  container:
    "flex flex-col min-h-screen xl:h-screen w-full bg-background px-4 sm:px-6 lg:px-8 xl:overflow-hidden",
  main: "flex-1 flex flex-col items-center justify-start py-2 xl:overflow-hidden",
};

const App = () => {
  const { isCustomStateActive, clearCustomState } = useCustomPortfolioStore();
  const isDefaultMode = !!useMatch("/default-portfolio");

  useEffect(() => {
    if (isDefaultMode && isCustomStateActive()) clearCustomState();
  }, [isDefaultMode, isCustomStateActive, clearCustomState]);

  return (
    <div className={appStyles.container}>
      <Header />
      <PortfolioAnalysisLoader>
        <main className={appStyles.main}>
          <PortfolioCarousel />
        </main>
      </PortfolioAnalysisLoader>
    </div>
  );
};

export default App;
