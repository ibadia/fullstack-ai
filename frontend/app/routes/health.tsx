import { useEffect, useState } from "react";

export default function Health() {
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const [detail, setDetail] = useState<string>("");

  useEffect(() => {
    fetch("http://localhost:8000/healthcheck/")
      .then(async (res) => {
        const text = await res.text();
        setDetail(text);
        setStatus(res.ok ? "ok" : "error");
      })
      .catch((err) => {
        setDetail(err.message);
        setStatus("error");
      });
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-white px-4 dark:bg-gray-950">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm dark:border-gray-800 dark:bg-gray-900">
        <h1 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
          Backend health check
        </h1>
        <p
          className={
            "mb-4 text-sm font-medium " +
            (status === "ok"
              ? "text-green-600 dark:text-green-400"
              : status === "error"
              ? "text-red-600 dark:text-red-400"
              : "text-gray-500 dark:text-gray-400")
          }
        >
          {status === "loading" && "Checking..."}
          {status === "ok" && "✅ Backend is healthy"}
          {status === "error" && "❌ Backend unreachable"}
        </p>
        {detail && (
          <pre className="overflow-x-auto rounded-lg border border-gray-200 bg-gray-50 p-3 text-left text-xs text-gray-600 dark:border-gray-800 dark:bg-gray-950 dark:text-gray-400">
            {detail}
          </pre>
        )}
      </div>
    </div>
  );
}