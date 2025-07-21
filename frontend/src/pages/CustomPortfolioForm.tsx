import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { ArrowLeft, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type {
  PortfolioAsset,
  DefaultPortfolioResponse,
} from "../types/portfolio";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Input } from "../components/ui/input";
import { Skeleton } from "../components/ui/skeleton";

const CustomPortfolioForm = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();
  const [assets, setAssets] = useState<Partial<PortfolioAsset>[]>([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { data, isLoading } = useQuery<DefaultPortfolioResponse>({
    queryKey: ["portfolio", "default"],
    queryFn: () =>
      fetch(`${apiUrl}/api/portfolio/default`).then((res) => res.json()),
  });

  useEffect(() => {
    if (data) {
      setAssets(data.default_portfolio_assets);
      setStartDate(data.start_date);
      setEndDate(data.end_date);
    }
  }, [data]);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="w-full mb-8">
        <div className="grid grid-cols-[1fr_auto_1fr] items-center">
          <div className="justify-self-start">
            <Button
              variant="secondary"
              onClick={() => navigate("/default-portfolio")}
            >
              <ArrowLeft className="h-6 w-6 mr-2" />
              Back
            </Button>
          </div>

          <h1 className="text-3xl font-bold whitespace-nowrap text-center">
            Custom Portfolio Builder
          </h1>

          <div />
        </div>
        <p className="text-muted-foreground text-center mt-2">
          Define your assets and their weights to create a custom portfolio.
        </p>
      </div>

      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Portfolio Assets</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isLoading ? (
              <>
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </>
            ) : (
              assets.map((asset, index) => (
                <div
                  key={index}
                  className="grid grid-cols-[1fr_120px_40px] gap-4 items-center"
                >
                  <Input
                    placeholder="Enter ticker (e.g., BTC-EUR)"
                    value={asset.ticker}
                    onChange={() => {}} // Functionality disabled for now
                  />
                  <div className="relative">
                    <Input
                      type="number"
                      value={asset.weight_pct}
                      onChange={() => {}} // Functionality disabled for now
                      className="pr-8"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                      %
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {}} // Functionality disabled for now
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))
            )}
            <Button
              onClick={() => {}} // Functionality disabled for now
              variant="outline"
              className="w-full mt-4"
            >
              + Add Asset
            </Button>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <CardDescription className="text-sm font-medium whitespace-nowrap">
              Analysis Period
            </CardDescription>
            <Input
              type="text"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-32"
            />
            <span className="text-muted-foreground text-sm">to</span>
            <Input
              type="text"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-32"
            />
          </div>
          <Button variant="secondary">Save Portfolio</Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default CustomPortfolioForm;
