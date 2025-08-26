import { useNavigate } from "react-router-dom";
import RegimeSelector from "./RegimeSelector";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { useCustomPortfolioStore } from "../store/customPortfolioStore";
import { ButtonWithLoggingOnClick } from "./withLoggingOnClick";

const headerStyles = {
  header:
    "flex flex-col lg:flex-row items-center w-full py-4 gap-4 lg:gap-0 min-h-[115px]",
  leftSection:
    "w-full lg:w-1/4 flex justify-center lg:justify-start items-center",
  centerSection:
    "w-full lg:w-1/2 flex justify-center h-14 items-center order-first lg:order-none",
  rightSection:
    "w-full lg:w-1/4 flex justify-center lg:justify-end items-center",
  button: "w-full sm:w-auto",
  buttonIcon: "h-4 w-4 sm:h-6 sm:w-6 mr-1 sm:mr-2",
  buttonText: "text-sm sm:text-base",
  title:
    "text-lg sm:text-xl lg:text-2xl font-semibold text-foreground text-center",
};

const Header = () => {
  const navigate = useNavigate();
  const { isCustomStateActive } = useCustomPortfolioStore();

  const customStateActive = isCustomStateActive();

  return (
    <header className={headerStyles.header}>
      <div className={headerStyles.leftSection}>
        {customStateActive ? (
          <ButtonWithLoggingOnClick
            onClick={() => navigate("/default-portfolio")}
            variant="secondary"
            className={headerStyles.button}
            logData={{
              event: "navigation_to_default_portfolio",
              route: window.location.pathname,
              context: {
                from_page: "custom-portfolio",
                navigation_direction: "back_to_default",
              },
            }}
          >
            <ArrowLeft className={headerStyles.buttonIcon} />
            <span className={headerStyles.buttonText}>Default Portfolio</span>
          </ButtonWithLoggingOnClick>
        ) : (
          <RegimeSelector />
        )}
      </div>

      <div className={headerStyles.centerSection}>
        <h1 className={headerStyles.title}>
          {customStateActive
            ? "Custom Portfolio Analysis"
            : "Default Portfolio Analysis"}
        </h1>
      </div>

      <div className={headerStyles.rightSection}>
        <ButtonWithLoggingOnClick
          onClick={() => navigate("/custom-portfolio-form")}
          variant="secondary"
          className={headerStyles.button}
          logData={{
            event: "navigation_to_custom_portfolio_form",
            route: window.location.pathname,
            context: {
              from_page: "default-portfolio",
              navigation_direction: "to_custom_portfolio_form",
            },
          }}
        >
          <span className={headerStyles.buttonText}>Customize Portfolio</span>
          <ArrowRight className={headerStyles.buttonIcon} />
        </ButtonWithLoggingOnClick>
      </div>
    </header>
  );
};

export default Header;
