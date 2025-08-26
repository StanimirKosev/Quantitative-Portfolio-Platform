import { Card, CardContent } from "./ui/card";
import { CarouselItem } from "./ui/carousel";

const slideStyles = {
  carouselItem: "px-12 sm:px-16",
  card: "h-full bg-black",
  cardContent: "flex flex-col h-full px-2 sm:px-4 pb-2 sm:pb-4",
};

const SlideErrorFallback = () => {
  return (
    <CarouselItem className={slideStyles.carouselItem}>
      <Card className={slideStyles.card}>
        <CardContent className={slideStyles.cardContent}>
          <div className="flex flex-col items-center justify-center flex-1 text-center space-y-4">
            <div className="text-4xl">⚠️</div>
            <h3 className="text-lg font-semibold text-foreground">
              Slide Error
            </h3>
            <p className="text-muted-foreground">This slide failed to load</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Try Again
            </button>
          </div>
        </CardContent>
      </Card>
    </CarouselItem>
  );
};

export default SlideErrorFallback;
