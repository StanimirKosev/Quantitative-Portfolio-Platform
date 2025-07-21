import { useIsFetching } from "@tanstack/react-query";
import LoadingBar from "./components/LoadingBar";
import PortfolioCarousel from "./components/PortfolioCarousel";
import Header from "./components/Header";

const App = () => {
  const isFetching = useIsFetching();
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
