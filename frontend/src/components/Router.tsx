import {
  createBrowserRouter,
  Navigate,
  RouterProvider,
} from "react-router-dom";
import App from "../App";
import ErrorPage from "./ErrorPage";
import ErrorBoundary from "./ErrorBoundary";
import CustomPortfolioForm from "../pages/CustomPortfolioForm";

const Router = () => {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <Navigate to="/default-portfolio" replace />,
    },
    {
      path: "/default-portfolio",
      element: (
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      ),
    },
    {
      path: "/custom-portfolio-form",
      element: (
        <ErrorBoundary>
          <CustomPortfolioForm />
        </ErrorBoundary>
      ),
    },
    {
      path: "/custom-portfolio",
      element: (
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      ),
    },
    {
      path: "*",
      element: <ErrorPage />,
    },
  ]);

  return <RouterProvider router={router} />;
};

export default Router;
