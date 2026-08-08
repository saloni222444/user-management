export default function StatCard({ label, value, icon }) {
  return (
    <div className="glass flex items-center gap-4 rounded-2xl px-6 py-5">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 text-xl text-white shadow-inner">
        {icon}
      </div>
      <div>
        <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
        <p className="text-2xl font-semibold text-slate-800 dark:text-slate-100">{value}</p>
      </div>
    </div>
  );
}
