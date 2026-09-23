"use client";

export default function Navbar() {
  return (
    <nav className="fixed left-0 top-0 z-50 flex w-full items-center justify-between px-8 py-6 md:px-14">
      <div className="text-sm font-semibold tracking-[0.28em] text-white">
        RELIABILITY.AI
      </div>

      <div className="hidden items-center gap-8 text-sm text-white/70 md:flex">
        <a href="#platform" className="transition hover:text-white">
          Platform
        </a>

        <a href="#monitoring" className="transition hover:text-white">
          Monitoring
        </a>

        <a href="#intelligence" className="transition hover:text-white">
          Intelligence
        </a>
      </div>

      <a
        href="#dashboard"
        className="rounded-full border border-white/30 px-5 py-2 text-sm text-white transition hover:bg-white hover:text-black"
      >
        Live Dashboard
      </a>
    </nav>
  );
}