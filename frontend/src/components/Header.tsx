import { useNavigate } from "react-router-dom";
import RegimeSelector from "./RegimeSelector";
import { Button } from "./ui/button";

const Header = () => {
  const navigate = useNavigate();

  return (
    <header className="flex items-center justify-between w-full px-6">
      <div className="flex-1">
        {/* Left side - empty for now, will show breadcrumb in custom mode */}
      </div>

      <div className="flex-1 flex justify-center">
        <RegimeSelector />
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
