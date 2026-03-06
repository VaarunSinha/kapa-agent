import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 font-sans dark:bg-zinc-950">
      <main className="flex w-full max-w-2xl flex-col items-center gap-10 px-6 py-16 text-center">
        <div className="flex flex-col items-center gap-4">
          <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-5xl">
            Documentation coverage gaps
          </h1>
          <p className="max-w-lg text-lg leading-relaxed text-zinc-600 dark:text-zinc-400">
            Find where your docs are missing answers. This tool analyzes conversations,
            surfaces coverage gaps, and suggests what to document next—so your AI assistant
            can give complete, accurate answers.
          </p>
        </div>
        <Link
          href="/dashboard"
          className="inline-flex h-12 items-center justify-center gap-2 rounded-full bg-zinc-900 px-8 text-base font-medium text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          Go to Dashboard
        </Link>
      </main>
    </div>
  );
}
