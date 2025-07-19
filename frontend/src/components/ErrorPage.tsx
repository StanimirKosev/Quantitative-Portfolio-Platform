const ErrorPage = ({ error }: { error?: Error }) => {
  return (
    <div className="flex items-center justify-center min-h-screen w-full">
      <span className="text-red-500 font-semibold text-lg">
        {error?.message || "Something went wrong. Please try again later."}
      </span>
    </div>
  );
};

export default ErrorPage;
