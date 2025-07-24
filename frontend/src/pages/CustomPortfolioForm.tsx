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
import { useEffect, useReducer, useState } from "react";
import { Input } from "../components/ui/input";
import { Skeleton } from "../components/ui/skeleton";
import { set, isEqual, omit, cloneDeep } from "lodash";
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";
import { API_BASE_URL } from "../lib/api";
import { Switch } from "../components/ui/switch";
import { Collapsible, CollapsibleContent } from "../components/ui/collapsible";
import type {
  RegimeParametersResponse,
  RegimeParameter,
} from "../types/regime";

export type CustomPortfolioFormData = PortfolioResponse & {
  portfolio_factors: RegimeParametersResponse["parameters"];
};

type FormFieldPath =
  | keyof CustomPortfolioFormData
  | `portfolio_assets.${number}.${keyof PortfolioAsset}`
  | `portfolio_factors.${number}.${keyof RegimeParameter}`;

type FormFieldValue =
  | CustomPortfolioFormData[keyof CustomPortfolioFormData]
  | PortfolioAsset[keyof PortfolioAsset]
  | RegimeParameter[keyof RegimeParameter];

type FormAction =
  | {
      type: "INITIALIZE_FORM";
      payload: CustomPortfolioFormData;
    }
  | {
      type: "UPDATE_FIELD";
      payload: {
        field: FormFieldPath;
        value: FormFieldValue | null;
      };
    }
  | { type: "ADD_ASSET" }
  | { type: "REMOVE_ASSET"; payload: { index: number } };

const initialState: CustomPortfolioFormData = {
  portfolio_assets: [],
  start_date: "",
  end_date: "",
  portfolio_factors: [],
};

function formReducer(
  formState: CustomPortfolioFormData,
  action: FormAction
): CustomPortfolioFormData {
  switch (action.type) {
    case "INITIALIZE_FORM":
      return {
        ...formState,
        portfolio_assets: cloneDeep(action.payload.portfolio_assets),
        start_date: action.payload.start_date,
        end_date: action.payload.end_date,
        portfolio_factors: cloneDeep(action.payload.portfolio_factors),
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
        portfolio_factors: [
          ...formState.portfolio_factors,
          {
            ticker: "",
            mean_factor: 1.0,
            vol_factor: 1.0,
            correlation_move_pct: 0,
          },
        ],
      };
    case "REMOVE_ASSET":
      return {
        ...formState,
        portfolio_assets: formState.portfolio_assets.filter(
          (_, index) => index !== action.payload.index
        ),
        portfolio_factors: formState.portfolio_factors.filter(
          (_, index) => index !== action.payload.index
        ),
      };
    default:
      return formState;
  }
}

const doCustomPortfolioRequest = async (
  formState: CustomPortfolioFormData,
  url: string
) => {
  const payload: PortfolioRequestPayload = {
    tickers: formState.portfolio_assets.map((a) => a.ticker || ""),
    weights: formState.portfolio_assets.map(
      (a) => Number(a.weight_pct) / 100 || 0
    ),
    regime_factors: {
      ...Object.fromEntries(
        formState.portfolio_factors.map(
          ({ ticker, mean_factor, vol_factor }) => [
            ticker,
            {
              mean_factor: mean_factor == null ? null : Number(mean_factor),
              vol_factor: vol_factor == null ? null : Number(vol_factor),
            },
          ]
        )
      ),
      correlation_move_pct:
        formState.portfolio_factors[0]?.correlation_move_pct == null
          ? null
          : Number(formState.portfolio_factors[0].correlation_move_pct),
    },
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

const validatePortfolio = async (formState: CustomPortfolioFormData) => {
  return doCustomPortfolioRequest(formState, "portfolio/validate");
};

const simulatePortfolio = async (formState: CustomPortfolioFormData) => {
  return doCustomPortfolioRequest(formState, "simulate/custom");
};

const CustomPortfolioForm = () => {
  const navigate = useNavigate();
  const [isPowerUserMode, setIsPowerUserMode] = useState<boolean>(false);
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
    CustomPortfolioFormData
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
  } = useMutation<ValidationResponse, Error, CustomPortfolioFormData>({
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

  const { data: defaultPortfolioFactors } = useQuery<RegimeParametersResponse>({
    queryKey: ["historical", "parameters"],
    queryFn: () =>
      fetch(`${API_BASE_URL}/api/regimes/historical/parameters`).then((res) =>
        res.json()
      ),
    enabled: !isCustomStateActive(),
  });

  useEffect(() => {
    const portfolioData =
      customPortfolio ||
      (defaultPortfolio &&
        defaultPortfolioFactors && {
          ...defaultPortfolio,
          portfolio_factors: defaultPortfolioFactors.parameters,
        });
    if (!portfolioData) return;

    dispatch({
      type: "INITIALIZE_FORM",
      payload: portfolioData,
    });
  }, [defaultPortfolio, customPortfolio, defaultPortfolioFactors]);

  const totalWeight = formState.portfolio_assets.reduce(
    (sum, asset) => sum + (Number(asset.weight_pct) || 0),
    0
  );

  const onNumberFieldChange = (
    val: string,
    path: FormFieldPath,
    decimalPlaces: number
  ) => {
    // Simple regex: allow intermediate typing states
    if (
      /^-?(\d*\.?\d*)$/.test(val) &&
      (val === "-" || val.endsWith(".") || val === "-0")
    ) {
      // Store intermediate states as string
      dispatch({
        type: "UPDATE_FIELD",
        payload: {
          field: path,
          value: val,
        },
      });
      return;
    }

    const parsed = parseFloat(val);
    if (val === "" || isNaN(parsed)) {
      dispatch({
        type: "UPDATE_FIELD",
        payload: {
          field: path,
          value: null,
        },
      });
      return;
    }

    const multiplier = Math.pow(10, decimalPlaces);
    const rounded = Math.round(parsed * multiplier) / multiplier;

    dispatch({
      type: "UPDATE_FIELD",
      payload: {
        field: path,
        value: rounded,
      },
    });
  };

  const getFactorValue = (index: number, field: keyof RegimeParameter) => {
    const value = formState.portfolio_factors?.[index]?.[field];
    return value == null ? "" : String(value);
  };

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
            <div className="flex items-center gap-4">
              <CardTitle>Portfolio Assets</CardTitle>
              <div className="flex items-center gap-2">
                <Switch
                  id="power-user-mode"
                  checked={isPowerUserMode}
                  onCheckedChange={setIsPowerUserMode}
                />
                <label htmlFor="power-user-mode" className="text-sm">
                  Power User
                </label>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Progress value={totalWeight} className="w-24" />
              <Badge
                variant={totalWeight === 100 ? "secondary" : "destructive"}
              >
                {totalWeight.toFixed(1)}%
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0 px-6">
          <div className="space-y-2">
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
                  className="grid grid-cols-[1fr_120px_40px] gap-x-4 gap-y-2 items-center"
                >
                  <Input
                    placeholder="Enter ticker (e.g., BTC-EUR)"
                    value={asset.ticker}
                    onChange={(e) => {
                      dispatch({
                        type: "UPDATE_FIELD",
                        payload: {
                          field: `portfolio_assets.${index}.ticker`,
                          value: e.target.value,
                        },
                      });

                      dispatch({
                        type: "UPDATE_FIELD",
                        payload: {
                          field: `portfolio_factors.${index}.ticker`,
                          value: e.target.value,
                        },
                      });
                    }}
                  />
                  <div className="relative">
                    <Input
                      type="number"
                      value={
                        asset.weight_pct == null ? "" : String(asset.weight_pct)
                      }
                      onChange={(e) =>
                        onNumberFieldChange(
                          e.target.value,
                          `portfolio_assets.${index}.weight_pct`,
                          1
                        )
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

                  <Collapsible open={isPowerUserMode}>
                    <CollapsibleContent className="overflow-hidden data-[state=open]:animate-in data-[state=open]:slide-in-from-top-2 data-[state=open]:fade-in data-[state=open]:duration-300 data-[state=closed]:animate-out data-[state=closed]:slide-out-to-top-2 data-[state=closed]:fade-out data-[state=closed]:duration-200">
                      <div className="pb-3">
                        <div className="grid grid-cols-2 gap-x-4 gap-y-0 pl-4 border-l-2 border-muted">
                          <div className="space-y-1">
                            <label
                              htmlFor={`mean-factor-${index}`}
                              className="text-xs font-medium"
                            >
                              Mean Factor
                            </label>
                            <Input
                              id={`mean-factor-${index}`}
                              type="number"
                              className="h-8 [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                              value={getFactorValue(index, "mean_factor")}
                              onChange={(e) =>
                                onNumberFieldChange(
                                  e.target.value,
                                  `portfolio_factors.${index}.mean_factor`,
                                  2
                                )
                              }
                            />
                          </div>

                          <div className="space-y-1">
                            <label
                              htmlFor={`vol-factor-${index}`}
                              className="text-xs font-medium"
                            >
                              Vol Factor
                            </label>
                            <Input
                              id={`vol-factor-${index}`}
                              type="number"
                              className="h-8 [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                              value={getFactorValue(index, "vol_factor")}
                              onChange={(e) =>
                                onNumberFieldChange(
                                  e.target.value,
                                  `portfolio_factors.${index}.vol_factor`,
                                  2
                                )
                              }
                            />
                          </div>
                        </div>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                </div>
              ))
            )}
            <Button
              onClick={() => dispatch({ type: "ADD_ASSET" })}
              variant="outline"
              className="w-full"
            >
              + Add Asset
            </Button>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col items-start gap-4 pt-2">
          <Collapsible open={isPowerUserMode}>
            <CollapsibleContent>
              <div className="flex items-center gap-1">
                <label
                  htmlFor="correlation-move"
                  className="text-sm font-medium whitespace-nowrap text-muted-foreground"
                >
                  Correlation Move
                </label>

                <Input
                  id="correlation-move"
                  type="number"
                  className="w-32 [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  value={getFactorValue(0, "correlation_move_pct")}
                  onChange={(e) =>
                    onNumberFieldChange(
                      e.target.value,
                      `portfolio_factors.0.correlation_move_pct`,
                      2
                    )
                  }
                />
              </div>
            </CollapsibleContent>
          </Collapsible>
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
          </div>
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
