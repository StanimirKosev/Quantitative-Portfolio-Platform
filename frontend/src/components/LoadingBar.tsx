import { useEffect, useState } from "react";
import { Progress } from "./ui/progress";

const LoadingBar = ({ message = "Loading..." }) => {
  const [value, setValue] = useState<number>(0);

  useEffect(() => {
    setValue(0);
    const start = Date.now();
    const duration = 600;
    const interval = setInterval(() => {
      const elapsed = Date.now() - start;
      const progress = Math.min((elapsed / duration) * 100, 100);
      setValue(progress);
      if (progress === 100) clearInterval(interval);
    }, 16);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`flex items-center justify-center min-h-screen w-full flex-col items-center gap-2`}
    >
      <Progress value={value} className="w-[260px]" />
      <span className="text-white font-semibold text-sm">{message}</span>
    </div>
  );
};

export default LoadingBar;
