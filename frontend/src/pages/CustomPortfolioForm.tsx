import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { ArrowLeft, Loader2, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type {
  PortfolioAsset,
  PortfolioResponse,
  ValidationResponse,
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
import {
  doCustomPortfolioRequest,
  processNumberInput,
  calculateTotalWeight,
  DEFAULT_ASSET_VALUES,
  DEFAULT_REGIME_FACTOR_VALUES,
  DECIMAL_PRECISION,
  getRegimeFactorValue,
  type CustomPortfolioFormData,
} from "../lib/portfolioUtils";
import { ButtonWithLoggingOnClick } from "../components/withLoggingOnClick";
import type { PortfolioOptimizationResponse } from "../types/optimization";

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
  currentFormData: CustomPortfolioFormData,
  action: FormAction
): CustomPortfolioFormData {
  switch (action.type) {
    case "INITIALIZE_FORM":
      return {
        ...currentFormData,
        portfolio_assets: cloneDeep(action.payload.portfolio_assets),
        start_date: action.payload.start_date,
        end_date: action.payload.end_date,
        portfolio_factors: cloneDeep(action.payload.portfolio_factors),
      };
    case "UPDATE_FIELD":
      return set(
        { ...currentFormData },
        action.payload.field,
        action.payload.value
      );
    case "ADD_ASSET":
      return {
        ...currentFormData,
        portfolio_assets: [
          ...currentFormData.portfolio_assets,
          { ...DEFAULT_ASSET_VALUES },
        ],
        portfolio_factors: [
          ...currentFormData.portfolio_factors,
          { ...DEFAULT_REGIME_FACTOR_VALUES },
        ],
      };
    case "REMOVE_ASSET":
      return {
        ...currentFormData,
        portfolio_assets: currentFormData.portfolio_assets.filter(
          (_, index) => index !== action.payload.index
        ),
        portfolio_factors: currentFormData.portfolio_factors.filter(
          (_, index) => index !== action.payload.index
        ),
      };
    default:
      return currentFormData;
  }
}

const validatePortfolio = async (
  formState: CustomPortfolioFormData
): Promise<ValidationResponse> => {
  return doCustomPortfolioRequest<ValidationResponse>(
    formState,
    "portfolio/validate"
  );
};

const simulatePortfolio = async (
  formState: CustomPortfolioFormData
): Promise<SimulateChartsResponse> => {
  return doCustomPortfolioRequest<SimulateChartsResponse>(
    formState,
    "simulate/custom"
  );
};

const optimizePortfolio = async (
  formState: CustomPortfolioFormData
): Promise<PortfolioOptimizationResponse> => {
  return doCustomPortfolioRequest<PortfolioOptimizationResponse>(
    formState,
    "optimize/custom"
  );
};

const CustomPortfolioForm = () => {
  const navigate = useNavigate();
  const [isPowerUserMode, setIsPowerUserMode] = useState<boolean>(false);
  const [formState, dispatch] = useReducer(formReducer, initialState);
  const {
    customPortfolio,
    setCustomPortfolio,
    setCustomPortfolioCharts,
    setCustomPortfolioOptimization,
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

  const { mutate: optimize, isPending: isOptimizing } = useMutation<
    PortfolioOptimizationResponse,
    Error,
    CustomPortfolioFormData
  >({
    mutationFn: optimizePortfolio,
    onSuccess: (portfolioOptimization) => {
      setCustomPortfolioOptimization(portfolioOptimization);
      simulate(formState);
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
      optimize(formState);
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

  const totalWeight = calculateTotalWeight(formState.portfolio_assets);

  const handleNumberFieldChange = (
    inputValue: string,
    fieldPath: FormFieldPath,
    decimalPlaces: number
  ) => {
    const processedValue = processNumberInput(inputValue, decimalPlaces);

    dispatch({
      type: "UPDATE_FIELD",
      payload: {
        field: fieldPath,
        value: processedValue,
      },
    });
  };

  const getFactorDisplayValue = (
    index: number,
    field: keyof RegimeParameter
  ) => {
    return getRegimeFactorValue(formState.portfolio_factors, index, field);
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="w-full mb-8">
        <div className="grid grid-cols-[1fr_auto_1fr] items-center">
          <div className="justify-self-start">
            <ButtonWithLoggingOnClick
              variant="secondary"
              onClick={() => navigate(-1)}
              logData={{
                event: "navigation_back_from_form",
                route: window.location.pathname,
                context: {
                  from_page: "custom-portfolio-form",
                  navigation_direction: "back",
                  form_completed: false,
                },
              }}
            >
              <ArrowLeft className="h-6 w-6 mr-2" />
              Back
            </ButtonWithLoggingOnClick>
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
                        handleNumberFieldChange(
                          e.target.value,
                          `portfolio_assets.${index}.weight_pct`,
                          DECIMAL_PRECISION.WEIGHT
                        )
                      }
                      className="pr-8 [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                      %
                    </span>
                  </div>
                  <ButtonWithLoggingOnClick
                    variant="ghost"
                    size="icon"
                    onClick={() =>
                      dispatch({ type: "REMOVE_ASSET", payload: { index } })
                    }
                    logData={{
                      event: "remove_asset_from_portfolio",
                      route: window.location.pathname,
                      context: {
                        asset_index: index,
                        asset_ticker: asset.ticker,
                        total_assets: formState.portfolio_assets.length,
                      },
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </ButtonWithLoggingOnClick>

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
                              value={getFactorDisplayValue(
                                index,
                                "mean_factor"
                              )}
                              onChange={(e) =>
                                handleNumberFieldChange(
                                  e.target.value,
                                  `portfolio_factors.${index}.mean_factor`,
                                  DECIMAL_PRECISION.FACTOR
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
                              value={getFactorDisplayValue(index, "vol_factor")}
                              onChange={(e) =>
                                handleNumberFieldChange(
                                  e.target.value,
                                  `portfolio_factors.${index}.vol_factor`,
                                  DECIMAL_PRECISION.FACTOR
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
            <ButtonWithLoggingOnClick
              onClick={() => dispatch({ type: "ADD_ASSET" })}
              variant="outline"
              className="w-full"
              logData={{
                event: "add_asset_to_portfolio",
                route: window.location.pathname,
                context: {
                  current_asset_count: formState.portfolio_assets.length,
                  total_weight: totalWeight,
                },
              }}
            >
              + Add Asset
            </ButtonWithLoggingOnClick>
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
                  value={getFactorDisplayValue(0, "correlation_move_pct")}
                  onChange={(e) =>
                    handleNumberFieldChange(
                      e.target.value,
                      `portfolio_factors.0.correlation_move_pct`,
                      DECIMAL_PRECISION.FACTOR
                    )
                  }
                />
              </div>
            </CollapsibleContent>
          </Collapsible>
          <div className="flex flex-col md:flex-row items-center gap-3">
            <CardDescription className="text-sm font-medium whitespace-nowrap">
              Analysis Period
            </CardDescription>
            <div className="flex items-center gap-2">
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
            <ButtonWithLoggingOnClick
              variant="secondary"
              onClick={handleSubmit}
              disabled={isValidating || isSimulating || isOptimizing}
              className="min-w-[9rem] px-4 py-2 flex items-center justify-center mt-2 md:mt-0"
              logData={{
                event: "submit_custom_portfolio_form",
                route: window.location.pathname,
                context: {
                  assets: formState.portfolio_assets,
                  factors: formState.portfolio_factors,
                  date_range: `${formState.start_date}-${formState.end_date}`,
                },
              }}
            >
              {isValidating || isSimulating || isOptimizing ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                "Analyze Portfolio"
              )}
            </ButtonWithLoggingOnClick>
          </div>
        </CardFooter>
      </Card>

      {validationData?.errors ? (
        <div className="mt-4 p-4 max-w-2xl mx-auto rounded-lg bg-destructive/15 border border-destructive/30">
          <ul className="list-disc list-inside space-y-1">
            {validationData.errors.map((error: string, index: number) => (
              <li key={index} className="text-base text-red-500 font-medium">
                {error}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
};

export default CustomPortfolioForm;
