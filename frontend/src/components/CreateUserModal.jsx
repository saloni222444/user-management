import { useEffect, useState } from "react";
import { createUser } from "../api";

const EMPTY_FORM = { name: "", email: "", role: "" };

export default function CreateUserModal({ onClose, onCreated }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleEscape = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [onClose]);

  function updateField(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      // The API is the single source of truth for validation (required
      // fields, email format, duplicate emails) - this form just displays
      // whatever error message it returns.
      const result = await createUser(form);
      onCreated(result.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="glass w-full max-w-md rounded-2xl p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">
            Create User
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1 text-slate-400 transition hover:bg-white/30 hover:text-slate-600 dark:hover:text-slate-200"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-xl border border-rose-300/50 bg-rose-500/10 px-4 py-2.5 text-sm text-rose-600 dark:text-rose-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Name">
            <input
              type="text"
              value={form.name}
              onChange={updateField("name")}
              className="glass w-full rounded-lg px-3 py-2 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-violet-400 dark:text-slate-100"
              placeholder="Saloni"
            />
          </Field>
          <Field label="Email">
            <input
              type="text"
              value={form.email}
              onChange={updateField("email")}
              className="glass w-full rounded-lg px-3 py-2 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-violet-400 dark:text-slate-100"
              placeholder="saloni@example.com"
            />
          </Field>
          <Field label="Role">
            <input
              type="text"
              value={form.role}
              onChange={updateField("role")}
              className="glass w-full rounded-lg px-3 py-2 text-sm text-slate-800 outline-none focus:ring-2 focus:ring-violet-400 dark:text-slate-100"
              placeholder="Developer"
            />
          </Field>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-500 transition hover:bg-white/30 dark:text-slate-400"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-gradient-to-r from-violet-500 to-fuchsia-500 px-5 py-2 text-sm font-medium text-white shadow transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Creating…" : "Create User"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </span>
      {children}
    </label>
  );
}
