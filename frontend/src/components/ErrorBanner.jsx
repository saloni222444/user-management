export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="glass flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-rose-300/40 px-5 py-4 text-sm">
      <div className="flex items-center gap-3">
        <span className="text-xl">⚠️</span>
        <div>
          <p className="font-medium text-rose-600 dark:text-rose-300">Something went wrong</p>
          <p className="text-slate-500 dark:text-slate-400">{message}</p>
        </div>
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-lg bg-rose-500/10 px-4 py-2 font-medium text-rose-600 transition hover:bg-rose-500/20 dark:text-rose-300"
        >
          Retry
        </button>
      )}
    </div>
  );
}
