import { Card, CardContent } from "../components/ui/card";
import { useNavigate } from "react-router-dom";

const ErrorPage = ({ error }: { error?: Error }) => {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-screen w-full bg-background p-6">
      <Card className="max-w-md w-full">
        <CardContent className="flex flex-col items-center justify-center text-center space-y-4 p-8">
          <div className="text-4xl">⚠️</div>
          <h3 className="text-lg font-semibold text-foreground">
            Application Error
          </h3>
          <p className="text-muted-foreground">
            {error?.message || "Something went wrong. Please try again later."}
          </p>
          <div className="flex flex-col gap-2 w-full">
            <button
              onClick={() => navigate("/default-portfolio")}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Go to Default Portfolio
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/90"
            >
              Try Again
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ErrorPage;
