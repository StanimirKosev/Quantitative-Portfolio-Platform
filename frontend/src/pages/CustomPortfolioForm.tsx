import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { ArrowLeft, Loader2, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type {
  PortfolioAsset,
  PortfolioResponse,
  ValidationResponse,
  PortfolioRequestPayload,
  SimulateChartsResponse,
} from "../types/portfolio";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useReducer } from "react";
import { Input } from "../components/ui/input";
import { Skeleton } from "../components/ui/skeleton";
import { set, isEqual, omit, cloneDeep } from "lodash";
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";
import { API_BASE_URL } from "../lib/api";

type FormAction =
  | {
      type: "INITIALIZE_FORM";
      payload: PortfolioResponse;
    }
  | {
      type: "UPDATE_FIELD";
      payload: {
        field:
          | keyof PortfolioResponse
          | `portfolio_assets.${number}.${keyof PortfolioAsset}`;
        value:
          | PortfolioResponse[keyof PortfolioResponse]
          | PortfolioAsset[keyof PortfolioAsset];
      };
    }
  | { type: "ADD_ASSET" }
  | { type: "REMOVE_ASSET"; payload: { index: number } };

const initialState: PortfolioResponse = {
  portfolio_assets: [],
  start_date: "",
  end_date: "",
};

function formReducer(
  formState: PortfolioResponse,
  action: FormAction
): PortfolioResponse {
  switch (action.type) {
    case "INITIALIZE_FORM":
      return {
        ...formState,
        portfolio_assets: cloneDeep(action.payload.portfolio_assets),
        start_date: action.payload.start_date,
        end_date: action.payload.end_date,
      };
    case "UPDATE_FIELD":
      return set({ ...formState }, action.payload.field, action.payload.value);
    case "ADD_ASSET":
      return {
        ...formState,
        portfolio_assets: [
          ...formState.portfolio_assets,
          { ticker: "", weight_pct: 0 },
        ],
      };
    case "REMOVE_ASSET":
      return {
        ...formState,
        portfolio_assets: formState.portfolio_assets.filter(
          (_, index) => index !== action.payload.index
        ),
      };
    default:
      return formState;
  }
}

const doCustomPortfolioRequest = async (
  formState: PortfolioResponse,
  url: string
) => {
  const payload: PortfolioRequestPayload = {
    tickers: formState.portfolio_assets.map((a) => a.ticker || ""),
    weights: formState.portfolio_assets.map(
      (a) => Number(a.weight_pct) / 100 || 0
    ),
    start_date: formState.start_date,
    end_date: formState.end_date,
  };

  const res = await fetch(`${API_BASE_URL}/api/${url}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(`HTTP ${res.status}: ${errorData.detail}`);
  }
  return res.json();
};

const validatePortfolio = async (formState: PortfolioResponse) => {
  return doCustomPortfolioRequest(formState, "portfolio/validate");
};

const simulatePortfolio = async (formState: PortfolioResponse) => {
  return doCustomPortfolioRequest(formState, "simulate/custom");
};

const CustomPortfolioForm = () => {
  const navigate = useNavigate();
  const [formState, dispatch] = useReducer(formReducer, initialState);
  const {
    customPortfolio,
    setCustomPortfolio,
    setCustomPortfolioCharts,
    isCustomStateActive,
  } = useCustomPortfolioStore();

  const { mutate: simulate, isPending: isSimulating } = useMutation<
    SimulateChartsResponse,
    Error,
    PortfolioResponse
  >({
    mutationFn: simulatePortfolio,
    onSuccess: (chartData) => {
      setCustomPortfolioCharts(chartData);
      setCustomPortfolio(formState);
      navigate("/custom-portfolio");
    },
  });

  const {
    mutate: validate,
    data: validationData,
    isPending: isValidating,
  } = useMutation<ValidationResponse, Error, PortfolioResponse>({
    mutationFn: validatePortfolio,
    onSuccess: (validationData) => {
      if (!validationData.success) return;
      simulate(formState);
    },
  });

  const handleSubmit = () => {
    if (isEqual(customPortfolio, formState)) {
      navigate("/custom-portfolio");
      return;
    }

    validate(formState);
  };

  const { data: defaultPortfolio, isLoading } = useQuery<PortfolioResponse>({
    queryKey: ["portfolio", "default"],
    queryFn: () =>
      fetch(`${API_BASE_URL}/api/portfolio/default`).then((res) => res.json()),
    select: (data) => ({
      ...data,
      portfolio_assets: data.portfolio_assets.map((asset) =>
        omit(asset, "description")
      ),
    }),
    enabled: !isCustomStateActive(),
  });

  useEffect(() => {
    const portfolioData = customPortfolio || defaultPortfolio;
    if (!portfolioData) return;

    dispatch({
      type: "INITIALIZE_FORM",
      payload: portfolioData,
    });
  }, [defaultPortfolio, customPortfolio]);

  const totalWeight = formState.portfolio_assets.reduce(
    (sum, asset) => sum + (asset.weight_pct || 0),
    0
  );

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="w-full mb-8">
        <div className="grid grid-cols-[1fr_auto_1fr] items-center">
          <div className="justify-self-start">
            <Button variant="secondary" onClick={() => navigate(-1)}>
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
          <div className="flex justify-between items-center">
            <CardTitle>Portfolio Assets</CardTitle>
            <div className="flex items-center gap-2 w-1/3">
              <Progress value={totalWeight} />
              <span className="text-sm text-muted-foreground whitespace-nowrap">
                <Badge
                  variant={totalWeight === 100 ? "secondary" : "destructive"}
                >
                  {totalWeight.toFixed(1)}%
                </Badge>
              </span>
            </div>
          </div>
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
              formState.portfolio_assets.map((asset, index) => (
                <div
                  key={index}
                  className="grid grid-cols-[1fr_120px_40px] gap-4 items-center"
                >
                  <Input
                    placeholder="Enter ticker (e.g., BTC-EUR)"
                    value={asset.ticker}
                    onChange={(e) =>
                      dispatch({
                        type: "UPDATE_FIELD",
                        payload: {
                          field: `portfolio_assets.${index}.ticker`,
                          value: e.target.value,
                        },
                      })
                    }
                  />
                  <div className="relative">
                    <Input
                      type="number"
                      value={
                        Number.isFinite(asset.weight_pct)
                          ? asset.weight_pct
                          : ""
                      }
                      onChange={(e) => {
                        const value = parseFloat(e.target.value);
                        const rounded = Math.round(value * 10) / 10;

                        dispatch({
                          type: "UPDATE_FIELD",
                          payload: {
                            field: `portfolio_assets.${index}.weight_pct`,
                            value: rounded,
                          },
                        });
                      }}
                      className="pr-8 [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                      %
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() =>
                      dispatch({ type: "REMOVE_ASSET", payload: { index } })
                    }
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))
            )}
            <Button
              onClick={() => dispatch({ type: "ADD_ASSET" })}
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
              value={formState.start_date}
              onChange={(e) =>
                dispatch({
                  type: "UPDATE_FIELD",
                  payload: { field: "start_date", value: e.target.value },
                })
              }
              className="w-32"
            />
            <span className="text-muted-foreground text-sm">to</span>
            <Input
              type="text"
              value={formState.end_date}
              onChange={(e) =>
                dispatch({
                  type: "UPDATE_FIELD",
                  payload: { field: "end_date", value: e.target.value },
                })
              }
              className="w-32"
            />
          </div>
          <Button
            variant="secondary"
            onClick={handleSubmit}
            disabled={isValidating || isSimulating}
            className="min-w-[9rem] px-4 py-2 flex items-center justify-center"
          >
            {isValidating || isSimulating ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              "Analyze Portfolio"
            )}
          </Button>
        </CardFooter>
      </Card>

      {validationData?.errors && (
        <div className="mt-4 p-4 max-w-2xl mx-auto rounded-lg bg-destructive/15 border border-destructive/30">
          <ul className="list-disc list-inside space-y-1">
            {validationData.errors.map((error: string, index: number) => (
              <li key={index} className="text-base text-red-500 font-medium">
                {error}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CustomPortfolioForm;
