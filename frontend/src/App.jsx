import { useCallback, useEffect, useState } from "react";
import { getUsers } from "./api";
import ThemeToggle from "./components/ThemeToggle";
import StatCard from "./components/StatCard";
import SearchBar from "./components/SearchBar";
import UserTable from "./components/UserTable";
import Pagination from "./components/Pagination";
import CreateUserModal from "./components/CreateUserModal";
import ErrorBanner from "./components/ErrorBanner";

const LIMIT = 8;
const SEARCH_DEBOUNCE_MS = 350;

export default function App() {
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const [users, setUsers] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, limit: LIMIT, total: 0, pages: 0 });
  const [totalUsers, setTotalUsers] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  // The overall user count, independent of the current search/page - a
  // cheap request (limit=1) just to read `pagination.total` unfiltered.
  const fetchTotalUsers = useCallback(async () => {
    try {
      const result = await getUsers({ page: 1, limit: 1 });
      setTotalUsers(result.pagination.total);
    } catch {
      // Non-critical - the stat card just falls back to "—".
    }
  }, []);

  useEffect(() => {
    fetchTotalUsers();
  }, [fetchTotalUsers]);

  // Debounce the raw input before it drives a request, and reset to page 1
  // whenever the search term changes.
  useEffect(() => {
    const id = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(id);
  }, [searchInput]);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getUsers({ search, page, limit: LIMIT });
      setUsers(result.data);
      setPagination(result.pagination);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  function handleUserCreated() {
    setModalOpen(false);
    fetchTotalUsers();
    // Jump back to page 1 so the newly created user is visible even if
    // the current view was on a later page.
    if (page !== 1) {
      setPage(1);
    } else {
      fetchUsers();
    }
  }

  return (
    <div className="min-h-screen px-4 py-8 sm:px-8">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-800 dark:text-slate-100">
              User Management
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              A simple dashboard on top of the Flask + MySQL API.
            </p>
          </div>
          <ThemeToggle />
        </header>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <StatCard label="Total Users" value={totalUsers ?? "—"} icon="👥" />
          <StatCard
            label="Current Page"
            value={pagination.total === 0 ? "—" : `${pagination.page} / ${pagination.pages}`}
            icon="📄"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <SearchBar value={searchInput} onChange={setSearchInput} />
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            className="rounded-xl bg-gradient-to-r from-violet-500 to-fuchsia-500 px-5 py-2.5 text-sm font-medium text-white shadow transition hover:opacity-90"
          >
            + Create User
          </button>
        </div>

        {error ? (
          <ErrorBanner message={error} onRetry={fetchUsers} />
        ) : (
          <>
            <UserTable users={users} loading={loading} hasSearch={Boolean(search)} />
            <Pagination
              page={pagination.page}
              pages={pagination.pages}
              total={pagination.total}
              onPageChange={setPage}
            />
          </>
        )}
      </div>

      {modalOpen && (
        <CreateUserModal onClose={() => setModalOpen(false)} onCreated={handleUserCreated} />
      )}
    </div>
  );
}
