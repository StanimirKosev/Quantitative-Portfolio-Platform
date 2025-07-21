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
} from "../types/portfolio";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useReducer } from "react";
import { Input } from "../components/ui/input";
import { Skeleton } from "../components/ui/skeleton";
import { set } from "lodash";
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";

export interface FormState {
  assets: Partial<PortfolioAsset>[];
  startDate: string;
  endDate: string;
}

type FormAction =
  | {
      type: "INITIALIZE_FORM";
      payload: PortfolioResponse;
    }
  | {
      type: "UPDATE_FIELD";
      payload: {
        field: keyof FormState | `assets.${number}.${keyof PortfolioAsset}`;
        value:
          | FormState[keyof FormState]
          | PortfolioAsset[keyof PortfolioAsset];
      };
    }
  | { type: "ADD_ASSET" }
  | { type: "REMOVE_ASSET"; payload: { index: number } };

const initialState: FormState = {
  assets: [],
  startDate: "",
  endDate: "",
};

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case "INITIALIZE_FORM":
      return {
        ...state,
        assets: JSON.parse(JSON.stringify(action.payload.portfolio_assets)),
        startDate: action.payload.start_date,
        endDate: action.payload.end_date,
      };
    case "UPDATE_FIELD":
      return set({ ...state }, action.payload.field, action.payload.value);
    case "ADD_ASSET":
      return {
        ...state,
        assets: [...state.assets, { ticker: "", weight_pct: 0 }],
      };
    case "REMOVE_ASSET":
      return {
        ...state,
        assets: state.assets.filter(
          (_, index) => index !== action.payload.index
        ),
      };
    default:
      return state;
  }
}

const validatePortfolio = async (formState: FormState) => {
  const apiUrl = import.meta.env.VITE_API_URL;

  const payload = {
    tickers: formState.assets.map((a) => a.ticker),
    weights: formState.assets.map((a) => Number(a.weight_pct) / 100 || 0),
    start_date: formState.startDate,
    end_date: formState.endDate,
  };

  const res = await fetch(`${apiUrl}/api/portfolio/validate`, {
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

const CustomPortfolioForm = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();
  const [state, dispatch] = useReducer(formReducer, initialState);
  const { customPortfolio, setCustomPortfolio } = useCustomPortfolioStore();
  const {
    mutate,
    data: validationData,
    isPending,
  } = useMutation<ValidationResponse, Error, FormState>({
    mutationFn: validatePortfolio,
    onSuccess: (mutationData) => {
      if (mutationData?.success) {
        setCustomPortfolio(state);
        navigate("/custom-portfolio");
      }
    },
  });

  const { data, isLoading } = useQuery<PortfolioResponse>({
    queryKey: ["portfolio", "default"],
    queryFn: () =>
      fetch(`${apiUrl}/api/portfolio/default`).then((res) => res.json()),
    enabled: !customPortfolio,
  });

  useEffect(() => {
    dispatch({
      type: "INITIALIZE_FORM",
      payload: (customPortfolio || data) as PortfolioResponse,
    });
  }, [data, customPortfolio]);

  const totalWeight = state.assets.reduce(
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
              state.assets.map((asset, index) => (
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
                          field: `assets.${index}.ticker`,
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
                      onChange={(e) =>
                        dispatch({
                          type: "UPDATE_FIELD",
                          payload: {
                            field: `assets.${index}.weight_pct`,
                            value: parseFloat(e.target.value),
                          },
                        })
                      }
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
              value={state.startDate}
              onChange={(e) =>
                dispatch({
                  type: "UPDATE_FIELD",
                  payload: { field: "startDate", value: e.target.value },
                })
              }
              className="w-32"
            />
            <span className="text-muted-foreground text-sm">to</span>
            <Input
              type="text"
              value={state.endDate}
              onChange={(e) =>
                dispatch({
                  type: "UPDATE_FIELD",
                  payload: { field: "endDate", value: e.target.value },
                })
              }
              className="w-32"
            />
          </div>
          <Button
            variant="secondary"
            onClick={() => mutate(state)}
            disabled={isPending}
            className="min-w-[9rem] px-4 py-2 flex items-center justify-center"
          >
            {isPending ? (
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
