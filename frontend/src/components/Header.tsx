import { useMatch, useNavigate } from "react-router-dom";
import RegimeSelector from "./RegimeSelector";
import { Button } from "./ui/button";
import { ArrowLeft } from "lucide-react";

const Header = () => {
  const navigate = useNavigate();
  const isCustom = !!useMatch("/custom-portfolio");

  return (
    <header className="flex items-center justify-between w-full px-6">
      <div className="flex-1">
        {isCustom && (
          <Button
            onClick={() => navigate("/default-portfolio")}
            variant="secondary"
          >
            <ArrowLeft className="h-6 w-6 mr-2" />
            Default Portfolio
          </Button>
        )}
      </div>

      <div className="flex-1 flex justify-center h-14 items-center">
        {!isCustom && <RegimeSelector />}
      </div>

      <div className="flex-1 flex justify-end">
        <Button
          onClick={() => navigate("/custom-portfolio-form")}
          variant="secondary"
        >
          Customize Portfolio
        </Button>
      </div>
    </header>
  );
};

export default Header;
