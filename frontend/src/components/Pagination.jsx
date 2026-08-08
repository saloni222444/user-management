export default function Pagination({ page, pages, total, onPageChange }) {
  if (total === 0) return null;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 px-1 text-sm text-slate-500 dark:text-slate-400">
      <p>
        Page <span className="font-medium text-slate-700 dark:text-slate-200">{page}</span> of{" "}
        <span className="font-medium text-slate-700 dark:text-slate-200">{pages}</span> ·{" "}
        {total} user{total === 1 ? "" : "s"} total
      </p>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          className="glass rounded-lg px-3 py-1.5 font-medium transition hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100"
        >
          ← Prev
        </button>
        <button
          type="button"
          disabled={page >= pages}
          onClick={() => onPageChange(page + 1)}
          className="glass rounded-lg px-3 py-1.5 font-medium transition hover:scale-105 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
