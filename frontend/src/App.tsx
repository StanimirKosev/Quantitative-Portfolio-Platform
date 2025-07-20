import { useIsFetching } from "@tanstack/react-query";
import RegimeSelector from "./components/RegimeSelector";
import LoadingBar from "./components/LoadingBar";
import PortfolioCarousel from "./components/PortfolioCarousel";

const App = () => {
  const isFetching = useIsFetching();
  if (isFetching > 0) {
    return <LoadingBar message="Loading..." />;
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full bg-background">
      <RegimeSelector />
      <PortfolioCarousel />
    </div>
  );
};

export default App;
