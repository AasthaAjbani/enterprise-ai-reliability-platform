"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  {
    name: "Home",
    href: "/",
  },
  {
    name: "Drift",
    href: "/drift",
  },
  {
    name: "Performance",
    href: "/performance",
  },
  {
    name: "Anomalies",
    href: "/anomalies",
  },
  {
    name: "Root Cause",
    href: "/root-cause",
  },
];


export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav
      className="
        fixed
        left-0
        top-0
        z-50
        w-full
        border-b
        border-white/[0.06]
        bg-black/20
        backdrop-blur-xl
      "
    >
      <div
        className="
          mx-auto
          flex
          max-w-[1600px]
          items-center
          justify-between
          px-6
          py-5
          md:px-10
          lg:px-14
        "
      >
        {/* BRAND */}

        <Link
          href="/"
          className="
            relative
            z-10
            text-sm
            font-semibold
            tracking-[0.28em]
            text-white
          "
        >
          RELIABILITY.AI
        </Link>


        {/* DESKTOP NAVIGATION */}

        <div
          className="
            absolute
            left-1/2
            hidden
            -translate-x-1/2
            items-center
            gap-8
            lg:flex
          "
        >
          {navigation.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  relative
                  text-sm
                  transition
                  duration-300
                  ${
                    active
                      ? "text-white"
                      : "text-white/45 hover:text-white"
                  }
                `}
              >
                {item.name}

                {active && (
                  <span
                    className="
                      absolute
                      -bottom-2
                      left-1/2
                      h-1
                      w-1
                      -translate-x-1/2
                      rounded-full
                      bg-white
                    "
                  />
                )}
              </Link>
            );
          })}
        </div>


        {/* DASHBOARD BUTTON */}

        <Link
          href="/dashboard"
          className={`
            relative
            z-10
            rounded-full
            border
            px-5
            py-2.5
            text-sm
            transition
            duration-300

            ${
              pathname === "/dashboard"
                ? `
                  border-white
                  bg-white
                  text-black
                `
                : `
                  border-white/25
                  text-white
                  hover:border-white
                  hover:bg-white
                  hover:text-black
                `
            }
          `}
        >
          Live Dashboard
        </Link>
      </div>
    </nav>
  );
}