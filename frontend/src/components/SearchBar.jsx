export default function SearchBar({ value, onChange }) {
  return (
    <div className="relative flex-1">
      <span className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-slate-400">
        🔍
      </span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search by name or email..."
        className="glass w-full rounded-xl py-2.5 pl-11 pr-4 text-sm text-slate-800 placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-violet-400 dark:text-slate-100"
      />
    </div>
  );
}
