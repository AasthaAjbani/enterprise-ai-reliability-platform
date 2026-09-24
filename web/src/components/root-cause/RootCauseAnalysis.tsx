"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import Link from "next/link";

import {
  Activity,
  ArrowLeft,
  BrainCircuit,
  RefreshCw,
  TriangleAlert,
} from "lucide-react";

import {
  fetchReliabilityReport,
} from "@/lib/api";

import type {
  ReliabilityReport,
  RootCause,
} from "@/types/reliability";


const priorityOrder = {
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
};


// =========================================================
// PAGE
// =========================================================

export default function RootCauseAnalysis() {

  const [
    report,
    setReport,
  ] = useState<ReliabilityReport | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );


  // =======================================================
  // LOAD DATA
  // =======================================================

  async function loadReport() {

    try {

      setLoading(true);
      setError(null);

      const data =
        await fetchReliabilityReport();

      setReport(
        data
      );

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load root-cause analysis."
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadReport();

  }, []);



  // =======================================================
  // SORT ROOT CAUSES
  // =======================================================

  const rootCauses =
    useMemo(() => {

      if (!report) {
        return [];
      }


      return [
        ...report.root_causes,
      ].sort(
        (
          first,
          second
        ) => {

          const priorityDifference =
            priorityOrder[
              second.root_cause_priority
            ]
            -
            priorityOrder[
              first.root_cause_priority
            ];


          if (
            priorityDifference !== 0
          ) {

            return priorityDifference;

          }


          return (
            second.root_cause_score
            -
            first.root_cause_score
          );

        }
      );

    }, [report]);


  const topCause =
    rootCauses[0];


  const counts =
    useMemo(() => {

      return {

        high:
          rootCauses.filter(
            (cause) =>
              cause.root_cause_priority
              === "HIGH"
          ).length,

        medium:
          rootCauses.filter(
            (cause) =>
              cause.root_cause_priority
              === "MEDIUM"
          ).length,

        low:
          rootCauses.filter(
            (cause) =>
              cause.root_cause_priority
              === "LOW"
          ).length,

      };

    }, [rootCauses]);



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
          bg-[#070707]
          text-white
        "
      >

        <div
          className="
            flex
            items-center
            gap-4
            text-xs
            tracking-[0.2em]
            text-white/40
          "
        >

          <RefreshCw
            size={16}
            className="animate-spin"
          />

          ANALYZING ROOT CAUSES

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
          bg-[#070707]
          px-6
          text-white
        "
      >

        <div
          className="
            max-w-xl
            text-center
          "
        >

          <TriangleAlert
            size={40}
            className="
              mx-auto
              mb-6
              text-white/40
            "
          />


          <h1
            className="
              text-3xl
              font-medium
            "
          >

            Root-cause data unavailable

          </h1>


          <p
            className="
              mt-3
              text-white/40
            "
          >

            The monitoring API could not be reached.

          </p>


          <button
            onClick={loadReport}
            className="
              mt-7
              rounded-full
              bg-white
              px-6
              py-3
              text-sm
              text-black
            "
          >

            Try again

          </button>

        </div>

      </main>
    );

  }



  // =======================================================
  // PAGE
  // =======================================================

  return (
    <main
      className="
        min-h-screen
        bg-[#070707]
        px-6
        pb-24
        pt-32
        text-white
        md:px-10
        lg:px-14
      "
    >

      <div
        className="
          mx-auto
          max-w-[1500px]
        "
      >


        {/* ================================================= */}
        {/* TOP */}
        {/* ================================================= */}

        <div
          className="
            mb-14
            flex
            flex-wrap
            items-center
            justify-between
            gap-6
          "
        >

          <Link
            href="/dashboard"
            className="
              inline-flex
              items-center
              gap-2
              text-sm
              text-white/40
              transition
              hover:text-white
            "
          >

            <ArrowLeft
              size={15}
            />

            Dashboard

          </Link>


          <button
            onClick={loadReport}
            className="
              flex
              items-center
              gap-2
              rounded-full
              border
              border-white/15
              px-4
              py-2
              text-xs
              text-white/50
              transition
              hover:border-white/30
              hover:text-white
            "
          >

            <RefreshCw
              size={13}
            />

            Refresh

          </button>

        </div>



        {/* ================================================= */}
        {/* HERO */}
        {/* ================================================= */}

        <section
          className="
            grid
            gap-12
            lg:grid-cols-[1.25fr_0.75fr]
            lg:items-end
          "
        >

          <div>

            <div
              className="
                mb-6
                flex
                items-center
                gap-3
              "
            >

              <BrainCircuit
                size={18}
                className="
                  text-white/35
                "
              />


              <p
                className="
                  text-xs
                  uppercase
                  tracking-[0.35em]
                  text-white/35
                "
              >

                Reliability Intelligence

              </p>

            </div>


            <h1
              className="
                max-w-5xl
                text-6xl
                font-semibold
                uppercase
                leading-[0.84]
                tracking-[-0.065em]
                md:text-8xl
                lg:text-9xl
              "
            >

              We find
              <br />
              why.

            </h1>


            <p
              className="
                mt-8
                max-w-2xl
                text-lg
                leading-8
                text-white/45
              "
            >

              Combine production drift with model
              feature importance to prioritize which
              changes deserve investigation first.

            </p>

          </div>



          {/* STATUS */}

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

              Overall Reliability

            </p>


            <p
              className="
                mt-5
                text-4xl
                font-medium
              "
            >

              {
                report.overall_status
              }

            </p>


            <p
              className="
                mt-4
                text-sm
                leading-6
                text-white/40
              "
            >

              Root-cause ranking highlights
              features that should be investigated
              first. It does not prove causation.

            </p>

          </div>

        </section>



        {/* ================================================= */}
        {/* SUMMARY */}
        {/* ================================================= */}

        <section
          className="
            mt-16
            grid
            gap-4
            sm:grid-cols-2
            xl:grid-cols-4
          "
        >

          <SummaryCard
            label="High Priority"
            value={
              String(
                counts.high
              )
            }
          />


          <SummaryCard
            label="Medium Priority"
            value={
              String(
                counts.medium
              )
            }
          />


          <SummaryCard
            label="Low Priority"
            value={
              String(
                counts.low
              )
            }
          />


          <SummaryCard
            label="Features Evaluated"
            value={
              String(
                rootCauses.length
              )
            }
          />

        </section>



        {/* ================================================= */}
        {/* TOP CAUSE */}
        {/* ================================================= */}

        {topCause && (

          <section
            className="
              mt-6
              rounded-[30px]
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

              Highest Priority Investigation

            </p>


            <div
              className="
                mt-8
                grid
                gap-10
                lg:grid-cols-[1fr_auto]
                lg:items-end
              "
            >

              <div>

                <h2
                  className="
                    break-all
                    font-mono
                    text-4xl
                    font-medium
                    tracking-[-0.045em]
                    md:text-6xl
                  "
                >

                  {
                    topCause.feature
                  }

                </h2>


                <p
                  className="
                    mt-5
                    max-w-2xl
                    text-sm
                    leading-7
                    text-black/50
                  "
                >

                  This feature combines a meaningful
                  production distribution shift with
                  model influence, making it one of the
                  strongest candidates for investigation.

                </p>

              </div>


              <div
                className="
                  lg:text-right
                "
              >

                <p
                  className="
                    text-sm
                    text-black/40
                  "
                >

                  Root-cause score

                </p>


                <p
                  className="
                    mt-2
                    font-mono
                    text-5xl
                    tracking-[-0.05em]
                  "
                >

                  {
                    topCause
                      .root_cause_score
                      .toFixed(2)
                  }

                </p>


                <p
                  className="
                    mt-3
                    text-xs
                    font-medium
                    tracking-[0.16em]
                  "
                >

                  {
                    topCause
                      .root_cause_priority
                  } PRIORITY

                </p>

              </div>

            </div>

          </section>

        )}



        {/* ================================================= */}
        {/* FORMULA */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            rounded-[30px]
            border
            border-white/10
            bg-white/[0.02]
            p-7
            md:p-10
          "
        >

          <div
            className="
              flex
              items-center
              gap-3
            "
          >

            <Activity
              size={17}
              className="
                text-white/35
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

              Root-Cause Heuristic

            </p>

          </div>


          <div
            className="
              mt-9
              grid
              gap-4
              md:grid-cols-[1fr_auto_1fr_auto_1fr]
              md:items-center
            "
          >

            <FormulaBox
              title="Drift"
              description="How much production changed"
            />


            <FormulaSymbol>
              ×
            </FormulaSymbol>


            <FormulaBox
              title="Importance"
              description="How much the model uses it"
            />


            <FormulaSymbol>
              =
            </FormulaSymbol>


            <FormulaBox
              title="Priority"
              description="Where to investigate first"
            />

          </div>


          <p
            className="
              mt-8
              max-w-3xl
              text-sm
              leading-7
              text-white/35
            "
          >

            The current implementation calculates a
            heuristic score from drift magnitude and
            model feature importance. A higher score
            means stronger evidence for investigation,
            not proof that the feature caused the
            performance degradation.

          </p>

        </section>



        {/* ================================================= */}
        {/* RANKING */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            rounded-[30px]
            border
            border-white/10
            bg-white/[0.02]
            p-7
            md:p-10
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

            Investigation Ranking

          </p>


          <h2
            className="
              mt-2
              text-2xl
              font-medium
            "
          >

            Root-cause score by feature

          </h2>


          <div
            className="
              mt-10
              space-y-8
            "
          >

            {
              rootCauses.map(
                (
                  cause,
                  index
                ) => (

                  <CauseBar
                    key={
                      cause.feature
                    }
                    cause={
                      cause
                    }
                    rank={
                      index + 1
                    }
                  />

                )
              )
            }

          </div>

        </section>



        {/* ================================================= */}
        {/* DETAIL TABLE */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            overflow-hidden
            rounded-[30px]
            border
            border-white/10
            bg-white/[0.02]
          "
        >

          <div
            className="
              border-b
              border-white/10
              p-7
              md:p-10
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

              Feature Evidence

            </p>


            <h2
              className="
                mt-2
                text-2xl
                font-medium
              "
            >

              Complete root-cause analysis

            </h2>

          </div>


          <div
            className="
              overflow-x-auto
            "
          >

            <table
              className="
                w-full
                min-w-[1100px]
                border-collapse
                text-left
              "
            >

              <thead>

                <tr
                  className="
                    border-b
                    border-white/10
                    text-[10px]
                    uppercase
                    tracking-[0.16em]
                    text-white/25
                  "
                >

                  <th className="px-7 py-5">
                    Rank
                  </th>

                  <th className="px-7 py-5">
                    Feature
                  </th>

                  <th className="px-7 py-5">
                    Drift Level
                  </th>

                  <th className="px-7 py-5">
                    Drift Score
                  </th>

                  <th className="px-7 py-5">
                    Importance
                  </th>

                  <th className="px-7 py-5">
                    Root-Cause Score
                  </th>

                  <th className="px-7 py-5">
                    Priority
                  </th>

                </tr>

              </thead>


              <tbody>

                {
                  rootCauses.map(
                    (
                      cause,
                      index
                    ) => (

                      <CauseRow
                        key={
                          cause.feature
                        }
                        cause={
                          cause
                        }
                        rank={
                          index + 1
                        }
                      />

                    )
                  )
                }

              </tbody>

            </table>

          </div>

        </section>



        {/* ================================================= */}
        {/* RECOMMENDATION */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            rounded-[30px]
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
              report.recommendation
            }

          </p>

        </section>

      </div>

    </main>
  );
}


// =========================================================
// SUMMARY CARD
// =========================================================

function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div
      className="
        rounded-[24px]
        border
        border-white/10
        bg-white/[0.025]
        p-6
      "
    >

      <p
        className="
          text-4xl
          font-medium
          tracking-[-0.04em]
        "
      >

        {value}

      </p>


      <p
        className="
          mt-3
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
// FORMULA
// =========================================================

function FormulaBox({
  title,
  description,
}: {
  title: string;
  description: string;
}) {

  return (
    <div
      className="
        rounded-[22px]
        border
        border-white/10
        bg-white/[0.025]
        p-6
      "
    >

      <p
        className="
          text-xl
          font-medium
        "
      >

        {title}

      </p>


      <p
        className="
          mt-2
          text-sm
          leading-6
          text-white/35
        "
      >

        {description}

      </p>

    </div>
  );
}


function FormulaSymbol({
  children,
}: {
  children: React.ReactNode;
}) {

  return (
    <div
      className="
        text-center
        text-3xl
        text-white/25
      "
    >

      {children}

    </div>
  );
}


// =========================================================
// BAR
// =========================================================

function CauseBar({
  cause,
  rank,
}: {
  cause: RootCause;
  rank: number;
}) {

  const width =
    Math.min(
      Math.max(
        cause.root_cause_score,
        0
      ),
      100
    );


  return (
    <div>

      <div
        className="
          mb-3
          flex
          items-end
          justify-between
          gap-5
        "
      >

        <div
          className="
            flex
            items-center
            gap-4
          "
        >

          <span
            className="
              text-xs
              text-white/25
            "
          >

            {
              String(rank)
                .padStart(
                  2,
                  "0"
                )
            }

          </span>


          <div>

            <p
              className="
                break-all
                font-mono
                text-sm
                text-white/75
              "
            >

              {cause.feature}

            </p>


            <p
              className="
                mt-1
                text-xs
                text-white/25
              "
            >

              {
                cause.drift_level
              } drift

            </p>

          </div>

        </div>


        <div
          className="
            text-right
          "
        >

          <p
            className="
              font-mono
              text-sm
            "
          >

            {
              cause
                .root_cause_score
                .toFixed(2)
            }

          </p>


          <p
            className="
              mt-1
              text-[10px]
              tracking-[0.15em]
              text-white/30
            "
          >

            {
              cause
                .root_cause_priority
            }

          </p>

        </div>

      </div>


      <div
        className="
          h-2
          overflow-hidden
          rounded-full
          bg-white/[0.06]
        "
      >

        <div
          className="
            h-full
            rounded-full
            bg-white/75
          "
          style={{
            width:
              `${width}%`,
          }}
        />

      </div>

    </div>
  );
}


// =========================================================
// TABLE
// =========================================================

function CauseRow({
  cause,
  rank,
}: {
  cause: RootCause;
  rank: number;
}) {

  return (
    <tr
      className="
        border-b
        border-white/[0.06]
        transition
        hover:bg-white/[0.025]
      "
    >

      <td
        className="
          px-7
          py-6
          text-sm
          text-white/25
        "
      >

        {
          String(rank)
            .padStart(
              2,
              "0"
            )
        }

      </td>


      <td
        className="
          px-7
          py-6
          font-mono
          text-sm
          text-white/80
        "
      >

        {cause.feature}

      </td>


      <td
        className="
          px-7
          py-6
        "
      >

        <DriftBadge
          level={
            cause.drift_level
          }
        />

      </td>


      <td
        className="
          px-7
          py-6
          font-mono
          text-sm
          text-white/60
        "
      >

        {
          cause
            .score
            .toFixed(4)
        }

      </td>


      <td
        className="
          px-7
          py-6
          font-mono
          text-sm
          text-white/60
        "
      >

        {
          cause
            .model_importance
            .toFixed(4)
        }

      </td>


      <td
        className="
          px-7
          py-6
          font-mono
          text-sm
        "
      >

        {
          cause
            .root_cause_score
            .toFixed(2)
        }

      </td>


      <td
        className="
          px-7
          py-6
        "
      >

        <PriorityBadge
          priority={
            cause
              .root_cause_priority
          }
        />

      </td>

    </tr>
  );
}


// =========================================================
// BADGES
// =========================================================

function DriftBadge({
  level,
}: {
  level:
    | "LOW"
    | "MODERATE"
    | "HIGH";
}) {

  const style =
    level === "HIGH"
      ?
      "border-red-400/25 bg-red-400/10 text-red-300"
      :
      level === "MODERATE"
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
        tracking-[0.14em]
        ${style}
      `}
    >

      {level}

    </span>
  );
}


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
      "border-red-400/25 bg-red-400/10 text-red-300"
      :
      priority === "MEDIUM"
        ?
        "border-amber-400/25 bg-amber-400/10 text-amber-300"
        :
        "border-white/10 bg-white/[0.03] text-white/40";


  return (
    <span
      className={`
        inline-flex
        rounded-full
        border
        px-3
        py-1.5
        text-[10px]
        tracking-[0.14em]
        ${style}
      `}
    >

      {priority}

    </span>
  );
}