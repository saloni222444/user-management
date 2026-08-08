function SkeletonRows({ count = 5 }) {
  return Array.from({ length: count }).map((_, i) => (
    <tr key={i} className="border-b border-white/10 last:border-0">
      {Array.from({ length: 4 }).map((__, j) => (
        <td key={j} className="px-5 py-4">
          <div className="h-4 w-full max-w-40 animate-pulse rounded bg-slate-300/40 dark:bg-slate-600/40" />
        </td>
      ))}
    </tr>
  ));
}

export default function UserTable({ users, loading, hasSearch }) {
  return (
    <div className="glass overflow-hidden rounded-2xl">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-left text-sm">
          <thead>
            <tr className="border-b border-white/10 text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
              <th className="px-5 py-3 font-medium">ID</th>
              <th className="px-5 py-3 font-medium">Name</th>
              <th className="px-5 py-3 font-medium">Email</th>
              <th className="px-5 py-3 font-medium">Role</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <SkeletonRows />
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-5 py-14 text-center">
                  <p className="text-3xl">{hasSearch ? "🔎" : "👥"}</p>
                  <p className="mt-2 font-medium text-slate-600 dark:text-slate-300">
                    {hasSearch ? "No users match your search" : "No users yet"}
                  </p>
                  <p className="mt-1 text-sm text-slate-400">
                    {hasSearch
                      ? "Try a different name or email."
                      : "Create the first user to get started."}
                  </p>
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr
                  key={user.id}
                  className="border-b border-white/10 last:border-0 transition hover:bg-white/30 dark:hover:bg-white/5"
                >
                  <td className="px-5 py-4 text-slate-500 dark:text-slate-400">#{user.id}</td>
                  <td className="px-5 py-4 font-medium text-slate-800 dark:text-slate-100">
                    {user.name}
                  </td>
                  <td className="px-5 py-4 text-slate-600 dark:text-slate-300">{user.email}</td>
                  <td className="px-5 py-4">
                    <span className="rounded-full bg-violet-500/15 px-3 py-1 text-xs font-medium text-violet-700 dark:text-violet-300">
                      {user.role}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
