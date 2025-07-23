const LoadingBar = ({ message = "Loading..." }) => {
  return (
    <div className="flex items-center justify-center min-h-screen w-full flex-col gap-4">
      <span className="text-foreground font-medium text-lg">{message}</span>
      
      {/* Indeterminate progress bar */}
      <div className="w-64 h-2 bg-muted rounded-full overflow-hidden">
        <div className="h-full bg-primary rounded-full" 
             style={{ 
               animation: 'indeterminate 2s infinite linear',
               background: 'linear-gradient(90deg, transparent, hsl(var(--primary)), transparent)'
             }} 
        />
      </div>
    </div>
  );
};

export default LoadingBar;
