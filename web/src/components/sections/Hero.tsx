"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

import AICore from "@/components/three/AICore";


export default function Hero() {
  const heroRef = useRef<HTMLElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const subRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const context = gsap.context(() => {
      const timeline = gsap.timeline();

      timeline
        .from(headingRef.current, {
          y: 120,
          opacity: 0,
          duration: 1.2,
          ease: "power4.out",
        })
        .from(
          subRef.current,
          {
            y: 40,
            opacity: 0,
            duration: 0.8,
            ease: "power3.out",
          },
          "-=0.6"
        );
    }, heroRef);

    return () => context.revert();
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#080808]"
    >
      <div className="absolute inset-0 z-0">
        <AICore />
      </div>

      <div className="pointer-events-none absolute inset-0 z-10 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.15)_40%,rgba(0,0,0,0.8)_100%)]" />

      <div className="relative z-20 mx-auto flex w-full max-w-[1500px] flex-col items-center px-6 text-center">
        <p className="mb-6 text-xs tracking-[0.45em] text-white/50">
          ENTERPRISE AI RELIABILITY
        </p>

        <h1
          ref={headingRef}
          className="max-w-6xl text-[15vw] font-semibold uppercase leading-[0.78] tracking-[-0.075em] text-white md:text-[9vw]"
        >
          TRUST
          <br />
          YOUR AI.
        </h1>

        <p
          ref={subRef}
          className="mt-10 max-w-xl text-base leading-relaxed text-white/60 md:text-lg"
        >
          Monitor drift, performance, anomalies and model health
          before unreliable AI reaches production.
        </p>

        <div className="mt-12 flex gap-4">
          <a
            href="#platform"
            className="pointer-events-auto rounded-full bg-white px-7 py-3 text-sm font-medium text-black transition hover:scale-105"
          >
            Explore Platform
          </a>

          <a
            href="http://localhost:8501"
            target="_blank"
            className="pointer-events-auto rounded-full border border-white/30 px-7 py-3 text-sm text-white transition hover:border-white"
          >
            Open Dashboard
          </a>
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 z-20 -translate-x-1/2 text-center">
        <div className="mb-2 text-[10px] tracking-[0.3em] text-white/40">
          SCROLL
        </div>

        <div className="mx-auto h-12 w-px bg-gradient-to-b from-white/60 to-transparent" />
      </div>
    </section>
  );
}