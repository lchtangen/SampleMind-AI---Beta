export default function LoadingSpinner({ size = 'md', text }: { size?: 'sm' | 'md' | 'lg'; text?: string }) {
  const sizes = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`${sizes[size]} animate-spin rounded-full border-4 border-solid border-[hsl(220,90%,60%)] border-r-transparent`}></div>
      {text && <p className="mt-4 text-[hsl(0,0%,98%)]">{text}</p>}
    </div>
  );
}
