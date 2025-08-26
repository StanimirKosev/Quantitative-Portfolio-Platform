import { useContext, useEffect, useState, useCallback } from "react";
import { CarouselContext } from "./ui/carousel";

const CarouselIndicator = () => {
  const context = useContext(CarouselContext);
  const [current, setCurrent] = useState<number>(0);
  const [count, setCount] = useState<number>(0);

  const handleSelect = useCallback(() => {
    if (context?.api) {
      setCurrent(context.api.selectedScrollSnap() + 1);
    }
  }, [context?.api]);

  useEffect(() => {
    if (!context?.api) {
      return;
    }

    const api = context.api;

    setCount(api.scrollSnapList().length);
    setCurrent(api.selectedScrollSnap() + 1);

    api.on("select", handleSelect);

    return () => {
      api.off("select", handleSelect);
    };
  }, [context?.api, handleSelect]);

  if (!context) {
    return null;
  }

  return (
    <div className="w-full flex justify-center mt-1">
      <span className="px-2 py-1 text-sm font-medium">
        Slide {current} of {count}
      </span>
    </div>
  );
};

export default CarouselIndicator;
