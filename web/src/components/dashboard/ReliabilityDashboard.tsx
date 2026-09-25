"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import type {
  ReactNode,
} from "react";

import Link from "next/link";

import {
  Activity,
  ArrowLeft,
  Database,
  Gauge,
  LoaderCircle,
  Radar,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

import SelfHealingStatusPanel
  from "@/components/dashboard/SelfHealingStatusPanel";

import {
  fetchReliabilityReport,
} from "@/lib/api";

import type {
  ReliabilityReport,
  ReliabilityStatus,
} from "@/types/reliability";


// =========================================================
// DASHBOARD
// =========================================================

export default function ReliabilityDashboard() {

  const [
    report,
    setReport,
  ] = useState<
    ReliabilityReport | null
  >(null);


  const [
    loading,
    setLoading,
  ] = useState(
    true
  );


  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);


  // =======================================================
  // LOAD REPORT
  // =======================================================

  async function loadReport() {

    try {

      setLoading(
        true
      );


      const data =
        await fetchReliabilityReport();


      setReport(
        data
      );


      setError(
        null
      );

    } catch (err) {

      console.error(
        err
      );


      setError(
        "Unable to load reliability data."
      );

    } finally {

      setLoading(
        false
      );

    }

  }


  useEffect(() => {

    loadReport();

  }, []);


  // =======================================================
  // DERIVED VALUES
  // =======================================================

  const driftCounts =
    useMemo(
      () => {

        if (!report) {

          return {
            high: 0,
            moderate: 0,
            low: 0,
          };

        }


        const features =
          report
            .data_drift
            .features;


        return {

          high:
            features.filter(
              (item) =>
                item.drift_level ===
                "HIGH"
            ).length,

          moderate:
            features.filter(
              (item) =>
                item.drift_level ===
                "MODERATE"
            ).length,

          low:
            features.filter(
              (item) =>
                item.drift_level ===
                "LOW"
            ).length,
        };

      },
      [report]
    );


  const topRootCause =
    useMemo(
      () => {

        if (
          !report
          ||
          report.root_causes.length === 0
        ) {

          return null;

        }


        return (
          report
            .root_causes
            .slice()
            .sort(
              (
                first,
                second
              ) =>
                second.root_cause_score
                -
                first.root_cause_score
            )[0]
        );

      },
      [report]
    );


  const rootCauseStatus:
    ReliabilityStatus =
      topRootCause
        ?.root_cause_priority
        ===
        "LOW"
        ?
        "HEALTHY"
        :
        "WARNING";


  const rootCauseBadge =
    topRootCause
      ?
      `${topRootCause.root_cause_priority} PRIORITY`
      :
      "NO PRIORITY";


  // =======================================================
  // LOADING
  // =======================================================

  if (loading) {

    return (
      <main
        className="
          flex
          min-h-screen
          items-center
          justify-center
          bg-[#080808]
          text-white
        "
      >

        <div
          className="
            flex
            items-center
            gap-3
            text-xs
            tracking-[0.18em]
            text-white/45
          "
        >

          <LoaderCircle
            className="
              h-4
              w-4
              animate-spin
            "
          />

          LOADING RELIABILITY DATA

        </div>

      </main>
    );
  }


  // =======================================================
  // ERROR
  // =======================================================

  if (
    error
    ||
    !report
  ) {

    return (
      <main
        className="
          flex
          min-h-screen
          items-center
          justify-center
          bg-[#080808]
          px-6
          text-white
        "
      >

        <div
          className="
            max-w-lg
            text-center
          "
        >

          <h1
            className="
              text-3xl
              font-semibold
            "
          >

            Reliability data unavailable

          </h1>


          <p
            className="
              mt-4
              text-white/45
            "
          >

            The frontend could not reach the
            monitoring API.

          </p>


          <button
            type="button"
            onClick={
              loadReport
            }
            className="
              mt-8
              rounded-full
              border
              border-white/20
              px-6
              py-3
              text-sm
              transition
              hover:bg-white
              hover:text-black
            "
          >

            Retry

          </button>

        </div>

      </main>
    );
  }


  // =======================================================
  // DASHBOARD
  // =======================================================

  return (
    <main
      className="
        min-h-screen
        bg-[#080808]
        text-white
      "
    >

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <header
        className="
          border-b
          border-white/10
          px-6
          py-5
          md:px-10
        "
      >

        <div
          className="
            mx-auto
            flex
            max-w-[1500px]
            items-center
            justify-between
          "
        >

          <div
            className="
              flex
              items-center
              gap-5
            "
          >

            <Link
              href="/"
              className="
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-full
                border
                border-white/15
                text-white/60
                transition
                hover:bg-white
                hover:text-black
              "
            >

              <ArrowLeft
                size={16}
              />

            </Link>


            <div>

              <p
                className="
                  text-[10px]
                  tracking-[0.3em]
                  text-white/35
                "
              >

                RELIABILITY.AI

              </p>


              <h1
                className="
                  mt-1
                  text-xl
                "
              >

                System Dashboard

              </h1>

            </div>

          </div>


          <div
            className="
              flex
              items-center
              gap-3
            "
          >

            <StatusBadge
              status={
                report.overall_status
              }
            />


            <button
              type="button"
              onClick={
                loadReport
              }
              className="
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-full
                border
                border-white/15
                text-white/60
                transition
                hover:border-white/30
                hover:text-white
              "
              aria-label="Refresh dashboard"
            >

              <RefreshCw
                size={15}
              />

            </button>

          </div>

        </div>

      </header>


      {/* ================================================= */}
      {/* CONTENT */}
      {/* ================================================= */}

      <div
        className="
          mx-auto
          max-w-[1500px]
          px-6
          py-10
          md:px-10
        "
      >

        {/* ================================================= */}
        {/* HERO STATUS */}
        {/* ================================================= */}

        <section
          className="
            mb-12
          "
        >

          <p
            className="
              mb-4
              text-[10px]
              uppercase
              tracking-[0.35em]
              text-white/35
            "
          >

            Current system state

          </p>


          <h2
            className="
              text-5xl
              font-semibold
              uppercase
              leading-[0.88]
              tracking-[-0.055em]
              md:text-7xl
              lg:text-8xl
            "
          >

            System reliability is{" "}

            <span
              className="
                text-white/35
              "
            >

              {
                report
                  .overall_status
                  .toLowerCase()
              }

            </span>

            .

          </h2>

        </section>


        {/* ================================================= */}
        {/* TOP STATUS CARDS */}
        {/* ================================================= */}

        <section
          className="
            grid
            gap-4
            md:grid-cols-2
            xl:grid-cols-4
          "
        >

          <StatusCard
            href="/drift"
            number="01"
            title="Data Drift"
            status={
              report
                .data_drift
                .status
            }
            description={
              `${driftCounts.high} high-risk features`
            }
            icon={
              <Database
                size={18}
              />
            }
          />


          <StatusCard
            href="/performance"
            number="02"
            title="Performance"
            status={
              report
                .model_performance
                .status
            }
            description={
              `F1 ${formatPercent(
                report
                  .model_performance
                  .production
                  .f1
              )}`
            }
            icon={
              <Gauge
                size={18}
              />
            }
          />


          <StatusCard
            href="/anomalies"
            number="03"
            title="Anomalies"
            status={
              report
                .anomaly_detection
                .status
            }
            description={
              `${report.anomaly_detection.anomaly_count} detected`
            }
            icon={
              <Radar
                size={18}
              />
            }
          />


          <StatusCard
            href="/root-cause"
            number="04"
            title="Root Cause"
            status={
              rootCauseStatus
            }
            badgeLabel={
              rootCauseBadge
            }
            description={
              topRootCause
                ?.feature
              ??
              "No dominant feature"
            }
            icon={
              <Activity
                size={18}
              />
            }
          />

        </section>


        {/* ================================================= */}
        {/* PERFORMANCE + DATA QUALITY */}
        {/* ================================================= */}

        <section
          className="
            mt-10
            grid
            gap-6
            xl:grid-cols-[1.4fr_0.6fr]
          "
        >

          {/* MODEL PERFORMANCE */}

          <div
            className="
              rounded-[28px]
              border
              border-white/10
              bg-white/[0.025]
              p-7
              md:p-9
            "
          >

            <div
              className="
                mb-8
                flex
                items-center
                justify-between
              "
            >

              <div>

                <p
                  className="
                    text-[10px]
                    uppercase
                    tracking-[0.28em]
                    text-white/30
                  "
                >

                  Model Performance

                </p>


                <h3
                  className="
                    mt-2
                    text-2xl
                    font-medium
                  "
                >

                  Baseline vs production

                </h3>

              </div>


              <Link
                href="/performance"
                className="
                  text-xs
                  text-white/40
                  transition
                  hover:text-white
                "
              >

                View details →

              </Link>

            </div>


            <div
              className="
                space-y-7
              "
            >

              <MetricComparison
                label="Accuracy"
                baseline={
                  report
                    .model_performance
                    .reference
                    .accuracy
                }
                production={
                  report
                    .model_performance
                    .production
                    .accuracy
                }
              />


              <MetricComparison
                label="Precision"
                baseline={
                  report
                    .model_performance
                    .reference
                    .precision
                }
                production={
                  report
                    .model_performance
                    .production
                    .precision
                }
              />


              <MetricComparison
                label="Recall"
                baseline={
                  report
                    .model_performance
                    .reference
                    .recall
                }
                production={
                  report
                    .model_performance
                    .production
                    .recall
                }
              />


              <MetricComparison
                label="F1 Score"
                baseline={
                  report
                    .model_performance
                    .reference
                    .f1
                }
                production={
                  report
                    .model_performance
                    .production
                    .f1
                }
              />

            </div>

          </div>


          {/* DATA QUALITY */}

          <div
            className="
              rounded-[28px]
              border
              border-white/10
              bg-white/[0.025]
              p-7
              md:p-9
            "
          >

            <div
              className="
                flex
                items-center
                gap-3
              "
            >

              <ShieldCheck
                size={19}
                className="
                  text-white/50
                "
              />


              <p
                className="
                  text-[10px]
                  uppercase
                  tracking-[0.28em]
                  text-white/30
                "
              >

                Data Quality

              </p>

            </div>


            <p
              className="
                mt-8
                text-7xl
                font-medium
                tracking-[-0.06em]
              "
            >

              {
                report
                  .data_quality
                  .score
                  .toFixed(1)
              }

            </p>


            <p
              className="
                mt-2
                text-sm
                text-white/35
              "
            >

              quality score / 100

            </p>


            <div
              className="
                mt-10
                border-t
                border-white/10
                pt-6
              "
            >

              <div
                className="
                  flex
                  justify-between
                  text-sm
                "
              >

                <span
                  className="
                    text-white/35
                  "
                >

                  Duplicate IDs

                </span>


                <span>

                  {
                    report
                      .data_quality
                      .duplicates
                  }

                </span>

              </div>

            </div>

          </div>

        </section>


        {/* ================================================= */}
        {/* DRIFT + ROOT CAUSE */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            grid
            gap-6
            lg:grid-cols-2
          "
        >

          {/* DRIFT */}

          <div
            className="
              rounded-[28px]
              border
              border-white/10
              bg-white/[0.025]
              p-7
              md:p-9
            "
          >

            <p
              className="
                text-[10px]
                uppercase
                tracking-[0.28em]
                text-white/30
              "
            >

              Drift Overview

            </p>


            <div
              className="
                mt-8
                grid
                grid-cols-3
                gap-3
              "
            >

              <CountBox
                value={
                  driftCounts.high
                }
                label="High"
              />


              <CountBox
                value={
                  driftCounts.moderate
                }
                label="Moderate"
              />


              <CountBox
                value={
                  driftCounts.low
                }
                label="Low"
              />

            </div>


            <Link
              href="/drift"
              className="
                mt-8
                inline-block
                text-sm
                text-white/40
                transition
                hover:text-white
              "
            >

              Analyze drift →

            </Link>

          </div>


          {/* ROOT CAUSE */}

          <div
            className="
              rounded-[28px]
              border
              border-white/10
              bg-white/[0.025]
              p-7
              md:p-9
            "
          >

            <div
              className="
                flex
                items-center
                justify-between
                gap-4
              "
            >

              <p
                className="
                  text-[10px]
                  uppercase
                  tracking-[0.28em]
                  text-white/30
                "
              >

                Highest Priority Cause

              </p>


              {topRootCause && (

                <PriorityBadge
                  priority={
                    topRootCause
                      .root_cause_priority
                  }
                />

              )}

            </div>


            <h3
              className="
                mt-7
                break-all
                font-mono
                text-2xl
                md:text-3xl
              "
            >

              {
                topRootCause
                  ?.feature
                ??
                "No dominant feature"
              }

            </h3>


            {topRootCause && (

              <>

                <div
                  className="
                    mt-7
                    grid
                    grid-cols-2
                    gap-4
                  "
                >

                  <SmallMetric
                    label="Drift score"
                    value={
                      topRootCause
                        .score
                        .toFixed(4)
                    }
                  />


                  <SmallMetric
                    label="Importance"
                    value={
                      topRootCause
                        .model_importance
                        .toFixed(4)
                    }
                  />

                </div>


                <Link
                  href="/root-cause"
                  className="
                    mt-8
                    inline-block
                    text-sm
                    text-white/40
                    transition
                    hover:text-white
                  "
                >

                  Investigate cause →

                </Link>

              </>

            )}

          </div>

        </section>


        {/* ================================================= */}
        {/* SELF-HEALING */}
        {/* ================================================= */}

        <SelfHealingStatusPanel />


        {/* ================================================= */}
        {/* RECOMMENDATION */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            rounded-[28px]
            bg-[#f1efe8]
            p-8
            text-black
            md:p-12
          "
        >

          <p
            className="
              text-[10px]
              uppercase
              tracking-[0.3em]
              text-black/40
            "
          >

            System Recommendation

          </p>


          <p
            className="
              mt-5
              max-w-5xl
              text-2xl
              font-medium
              leading-relaxed
              tracking-[-0.025em]
              md:text-3xl
            "
          >

            {
              report
                .recommendation
            }

          </p>

        </section>

      </div>

    </main>
  );
}


// =========================================================
// STATUS CARD
// =========================================================

function StatusCard({
  href,
  number,
  title,
  status,
  badgeLabel,
  description,
  icon,
}: {
  href: string;
  number: string;
  title: string;
  status: ReliabilityStatus;
  badgeLabel?: string;
  description: string;
  icon: ReactNode;
}) {

  return (
    <Link
      href={href}
      className="
        group
        rounded-[24px]
        border
        border-white/10
        bg-white/[0.025]
        p-6
        transition
        duration-300
        hover:-translate-y-1
        hover:border-white/20
        hover:bg-white/[0.045]
      "
    >

      <div
        className="
          flex
          items-center
          justify-between
        "
      >

        <span
          className="
            text-xs
            text-white/25
          "
        >

          {number}

        </span>


        <span
          className="
            text-white/35
            transition
            group-hover:text-white
          "
        >

          {icon}

        </span>

      </div>


      <h3
        className="
          mt-10
          text-2xl
          font-medium
        "
      >

        {title}

      </h3>


      <p
        className="
          mt-2
          text-sm
          text-white/35
        "
      >

        {description}

      </p>


      <div
        className="
          mt-7
        "
      >

        <StatusBadge
          status={
            status
          }
          label={
            badgeLabel
          }
        />

      </div>

    </Link>
  );
}


// =========================================================
// STATUS BADGE
// =========================================================

function StatusBadge({
  status,
  label,
}: {
  status: ReliabilityStatus;
  label?: string;
}) {

  const style =
    status === "CRITICAL"
      ?
      "border-red-400/25 bg-red-400/10 text-red-300"
      :
      status === "WARNING"
        ?
        "border-amber-400/25 bg-amber-400/10 text-amber-300"
        :
        "border-emerald-400/25 bg-emerald-400/10 text-emerald-300";


  return (
    <span
      className={`
        inline-flex
        rounded-full
        border
        px-3
        py-1.5
        text-[10px]
        font-medium
        tracking-[0.16em]
        ${style}
      `}
    >

      {
        label
        ??
        status
      }

    </span>
  );
}


// =========================================================
// ROOT CAUSE PRIORITY BADGE
// =========================================================

function PriorityBadge({
  priority,
}: {
  priority:
    | "LOW"
    | "MEDIUM"
    | "HIGH";
}) {

  const style =
    priority === "HIGH"
      ?
      "border-amber-400/25 bg-amber-400/10 text-amber-300"
      :
      priority === "MEDIUM"
        ?
        "border-yellow-400/20 bg-yellow-400/10 text-yellow-200"
        :
        "border-emerald-400/20 bg-emerald-400/10 text-emerald-300";


  return (
    <span
      className={`
        rounded-full
        border
        px-3
        py-1.5
        text-[9px]
        font-medium
        tracking-[0.15em]
        ${style}
      `}
    >

      {priority} PRIORITY

    </span>
  );
}


// =========================================================
// METRIC COMPARISON
// =========================================================

function MetricComparison({
  label,
  baseline,
  production,
}: {
  label: string;
  baseline: number;
  production: number;
}) {

  return (
    <div>

      <div
        className="
          mb-3
          flex
          items-center
          justify-between
        "
      >

        <span
          className="
            text-sm
            text-white/50
          "
        >

          {label}

        </span>


        <div
          className="
            flex
            gap-5
            font-mono
            text-xs
          "
        >

          <span
            className="
              text-white/30
            "
          >

            B {formatPercent(
              baseline
            )}

          </span>


          <span>

            P {formatPercent(
              production
            )}

          </span>

        </div>

      </div>


      <div
        className="
          relative
          h-2
          overflow-hidden
          rounded-full
          bg-white/[0.06]
        "
      >

        <div
          className="
            absolute
            inset-y-0
            left-0
            rounded-full
            bg-white/20
          "
          style={{
            width:
              `${Math.min(
                baseline * 100,
                100
              )}%`,
          }}
        />


        <div
          className="
            absolute
            inset-y-0
            left-0
            rounded-full
            bg-white
          "
          style={{
            width:
              `${Math.min(
                production * 100,
                100
              )}%`,
          }}
        />

      </div>

    </div>
  );
}


// =========================================================
// COUNT BOX
// =========================================================

function CountBox({
  value,
  label,
}: {
  value: number;
  label: string;
}) {

  return (
    <div
      className="
        rounded-2xl
        border
        border-white/10
        p-5
      "
    >

      <p
        className="
          text-3xl
          font-medium
        "
      >

        {value}

      </p>


      <p
        className="
          mt-2
          text-xs
          uppercase
          tracking-[0.18em]
          text-white/30
        "
      >

        {label}

      </p>

    </div>
  );
}


// =========================================================
// SMALL METRIC
// =========================================================

function SmallMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div
      className="
        rounded-2xl
        border
        border-white/10
        p-5
      "
    >

      <p
        className="
          text-xs
          text-white/30
        "
      >

        {label}

      </p>


      <p
        className="
          mt-2
          font-mono
          text-xl
        "
      >

        {value}

      </p>

    </div>
  );
}


// =========================================================
// FORMAT PERCENTAGE
// =========================================================

function formatPercent(
  value: number
) {

  return `${(
    value * 100
  ).toFixed(2)}%`;

}