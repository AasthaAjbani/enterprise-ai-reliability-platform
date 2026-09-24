"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import Link from "next/link";

import {
  ArrowLeft,
  Database,
  RefreshCw,
  TriangleAlert,
} from "lucide-react";

import {
  fetchReliabilityReport,
} from "@/lib/api";

import type {
  DriftFeature,
  ReliabilityReport,
} from "@/types/reliability";


const severityOrder = {
  HIGH: 3,
  MODERATE: 2,
  LOW: 1,
};


export default function DriftAnalysis() {

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


  // =====================================================
  // LOAD LIVE DATA
  // =====================================================

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
        "Unable to load drift analysis."
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadReport();

  }, []);



  // =====================================================
  // SORT FEATURES
  // =====================================================

  const sortedFeatures =
    useMemo(() => {

      if (!report) {
        return [];
      }


      return [
        ...report.data_drift.features,
      ].sort(
        (
          first,
          second
        ) => {

          const severityDifference =
            severityOrder[
              second.drift_level
            ]
            -
            severityOrder[
              first.drift_level
            ];


          if (
            severityDifference !== 0
          ) {

            return severityDifference;

          }


          return (
            second.score
            -
            first.score
          );

        }
      );

    }, [report]);



  const counts =
    useMemo(() => {

      return {

        high:
          sortedFeatures.filter(
            (feature) =>
              feature.drift_level
              === "HIGH"
          ).length,

        moderate:
          sortedFeatures.filter(
            (feature) =>
              feature.drift_level
              === "MODERATE"
          ).length,

        low:
          sortedFeatures.filter(
            (feature) =>
              feature.drift_level
              === "LOW"
          ).length,

      };

    }, [sortedFeatures]);



  const highestDrift =
    sortedFeatures[0];



  // =====================================================
  // LOADING
  // =====================================================

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

          ANALYZING DISTRIBUTIONS

        </div>

      </main>
    );

  }



  // =====================================================
  // ERROR
  // =====================================================

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

        <div className="text-center">

          <TriangleAlert
            className="
              mx-auto
              mb-5
              text-white/40
            "
            size={38}
          />

          <h1
            className="
              text-3xl
              font-medium
            "
          >
            Drift data unavailable
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



  // =====================================================
  // PAGE
  // =====================================================

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
        {/* HEADER */}
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

            <ArrowLeft size={15} />

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

            <RefreshCw size={13} />

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

              <Database
                size={17}
                className="text-white/35"
              />

              <p
                className="
                  text-xs
                  uppercase
                  tracking-[0.35em]
                  text-white/35
                "
              >

                Distribution Monitoring

              </p>

            </div>


            <h1
              className="
                max-w-4xl
                text-6xl
                font-semibold
                uppercase
                leading-[0.84]
                tracking-[-0.065em]
                md:text-8xl
                lg:text-9xl
              "
            >

              Data
              <br />
              Drift.

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

              Compare production feature distributions
              against the reference data used by the model
              and identify where behavior has changed.

            </p>

          </div>



          {/* OVERALL STATUS */}

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

              Drift Status

            </p>


            <p
              className="
                mt-5
                text-4xl
                font-medium
              "
            >

              {
                report
                  .data_drift
                  .status
              }

            </p>


            <p
              className="
                mt-3
                text-sm
                leading-6
                text-white/40
              "
            >

              {
                counts.high
              } high-risk features and{" "}

              {
                counts.moderate
              } moderate features detected.

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
            label="High Drift"
            value={
              String(
                counts.high
              )
            }
          />

          <SummaryCard
            label="Moderate"
            value={
              String(
                counts.moderate
              )
            }
          />

          <SummaryCard
            label="Low Drift"
            value={
              String(
                counts.low
              )
            }
          />

          <SummaryCard
            label="Features Monitored"
            value={
              String(
                sortedFeatures.length
              )
            }
          />

        </section>



        {/* ================================================= */}
        {/* STRONGEST DRIFT */}
        {/* ================================================= */}

        {highestDrift && (

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

              Strongest Distribution Shift

            </p>


            <div
              className="
                mt-7
                grid
                gap-8
                lg:grid-cols-[1fr_auto]
                lg:items-end
              "
            >

              <div>

                <h2
                  className="
                    break-words
                    font-mono
                    text-4xl
                    font-medium
                    tracking-[-0.04em]
                    md:text-6xl
                  "
                >

                  {
                    highestDrift.feature
                  }

                </h2>


                <p
                  className="
                    mt-4
                    max-w-2xl
                    text-sm
                    leading-6
                    text-black/50
                  "
                >

                  {
                    highestDrift.feature_type
                    === "numerical"
                      ?
                      "Measured using the Kolmogorov–Smirnov statistic."
                      :
                      "Measured using Total Variation Distance."
                  }

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

                  Drift score

                </p>


                <p
                  className="
                    mt-1
                    font-mono
                    text-5xl
                    tracking-[-0.05em]
                  "
                >

                  {
                    highestDrift
                      .score
                      .toFixed(4)
                  }

                </p>

              </div>

            </div>

          </section>

        )}



        {/* ================================================= */}
        {/* VISUAL RANKING */}
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
              mb-10
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

              Drift Ranking

            </p>


            <h2
              className="
                mt-2
                text-2xl
                font-medium
              "
            >

              Feature distribution change

            </h2>

          </div>


          <div
            className="
              space-y-7
            "
          >

            {
              sortedFeatures.map(
                (feature) => (

                  <DriftBar
                    key={feature.feature}
                    feature={feature}
                  />

                )
              )
            }

          </div>

        </section>



        {/* ================================================= */}
        {/* TABLE */}
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

              Full Feature Analysis

            </p>


            <h2
              className="
                mt-2
                text-2xl
                font-medium
              "
            >

              Statistical drift report

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
                min-w-[850px]
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
                    tracking-[0.2em]
                    text-white/25
                  "
                >

                  <th className="px-8 py-5">
                    Feature
                  </th>

                  <th className="px-8 py-5">
                    Type
                  </th>

                  <th className="px-8 py-5">
                    Method
                  </th>

                  <th className="px-8 py-5">
                    Score
                  </th>

                  <th className="px-8 py-5">
                    P-value
                  </th>

                  <th className="px-8 py-5">
                    Level
                  </th>

                </tr>

              </thead>


              <tbody>

                {
                  sortedFeatures.map(
                    (feature) => (

                      <FeatureRow
                        key={
                          feature.feature
                        }
                        feature={
                          feature
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
        {/* EXPLANATION */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            grid
            gap-4
            lg:grid-cols-2
          "
        >

          <MethodCard
            title="Numerical Features"
            method="Kolmogorov–Smirnov Test"
            description="
              Measures the maximum separation between
              the cumulative distributions of reference
              and production data.
            "
          />


          <MethodCard
            title="Categorical Features"
            method="Total Variation Distance"
            description="
              Measures how much the category probability
              distribution changed between reference and
              production data.
            "
          />

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
// DRIFT BAR
// =========================================================

function DriftBar({
  feature,
}: {
  feature: DriftFeature;
}) {

  const percentage =
    Math.min(
      feature.score * 100,
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

        <div>

          <p
            className="
              break-all
              font-mono
              text-sm
              text-white/75
            "
          >

            {feature.feature}

          </p>


          <p
            className="
              mt-1
              text-xs
              text-white/25
            "
          >

            {
              feature.feature_type
            }

          </p>

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
              feature.score
                .toFixed(4)
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
              feature.drift_level
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
            bg-white/70
          "
          style={{
            width:
              `${percentage}%`,
          }}
        />

      </div>

    </div>
  );
}



// =========================================================
// TABLE ROW
// =========================================================

function FeatureRow({
  feature,
}: {
  feature: DriftFeature;
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
          px-8
          py-6
          font-mono
          text-sm
          text-white/80
        "
      >

        {feature.feature}

      </td>


      <td
        className="
          px-8
          py-6
          text-sm
          text-white/40
        "
      >

        {feature.feature_type}

      </td>


      <td
        className="
          px-8
          py-6
          text-sm
          text-white/40
        "
      >

        {
          feature.feature_type
          === "numerical"
            ?
            "KS Test"
            :
            "TVD"
        }

      </td>


      <td
        className="
          px-8
          py-6
          font-mono
          text-sm
        "
      >

        {
          feature
            .score
            .toFixed(4)
        }

      </td>


      <td
        className="
          px-8
          py-6
          font-mono
          text-sm
          text-white/40
        "
      >

        {
          feature.p_value
          === null
            ?
            "—"
            :
            formatPValue(
              feature.p_value
            )
        }

      </td>


      <td
        className="
          px-8
          py-6
        "
      >

        <DriftBadge
          level={
            feature.drift_level
          }
        />

      </td>

    </tr>
  );
}



// =========================================================
// BADGE
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
        tracking-[0.15em]
        ${style}
      `}
    >

      {level}

    </span>
  );
}



// =========================================================
// METHOD CARD
// =========================================================

function MethodCard({
  title,
  method,
  description,
}: {
  title: string;
  method: string;
  description: string;
}) {

  return (
    <div
      className="
        rounded-[26px]
        border
        border-white/10
        p-7
        md:p-9
      "
    >

      <p
        className="
          text-xs
          uppercase
          tracking-[0.18em]
          text-white/30
        "
      >

        {title}

      </p>


      <h3
        className="
          mt-4
          text-xl
          font-medium
        "
      >

        {method}

      </h3>


      <p
        className="
          mt-4
          max-w-xl
          text-sm
          leading-7
          text-white/40
        "
      >

        {description}

      </p>

    </div>
  );
}



// =========================================================
// P-VALUE FORMATTER
// =========================================================

function formatPValue(
  value: number
) {

  if (
    value < 0.0001
  ) {

    return value.toExponential(2);

  }


  return value.toFixed(4);
}