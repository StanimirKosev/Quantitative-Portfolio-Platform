import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "../App";
import ErrorPage from "./ErrorPage";
import ErrorBoundary from "./ErrorBoundary";

const Router = () => {
  const router = createBrowserRouter([
    {
      path: "/default-portfolio",
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
