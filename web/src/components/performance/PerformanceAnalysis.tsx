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
  Gauge,
  RefreshCw,
  TrendingDown,
  TriangleAlert,
} from "lucide-react";

import {
  fetchReliabilityReport,
} from "@/lib/api";

import type {
  ReliabilityReport,
} from "@/types/reliability";


// =========================================================
// PAGE
// =========================================================

export default function PerformanceAnalysis() {

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
  // LOAD LIVE DATA
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
        "Unable to load model performance data."
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadReport();

  }, []);



  // =======================================================
  // DERIVED DATA
  // =======================================================

  const metrics =
    useMemo(() => {

      if (!report) {
        return [];
      }


      const performance =
        report.model_performance;


      return [
        {
          name: "Accuracy",
          baseline:
            performance.reference.accuracy,
          production:
            performance.production.accuracy,
          drop:
            performance.performance_drop.accuracy,
        },

        {
          name: "Precision",
          baseline:
            performance.reference.precision,
          production:
            performance.production.precision,
          drop:
            performance.performance_drop.precision,
        },

        {
          name: "Recall",
          baseline:
            performance.reference.recall,
          production:
            performance.production.recall,
          drop:
            performance.performance_drop.recall,
        },

        {
          name: "F1 Score",
          baseline:
            performance.reference.f1,
          production:
            performance.production.f1,
          drop:
            performance.performance_drop.f1,
        },
      ];

    }, [report]);


  const largestDrop =
    useMemo(() => {

      if (
        metrics.length === 0
      ) {
        return null;
      }


      return [
        ...metrics,
      ].sort(
        (
          first,
          second
        ) =>
          second.drop
          -
          first.drop
      )[0];

    }, [metrics]);


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

          EVALUATING MODEL PERFORMANCE

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

            Performance data unavailable

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



  const performance =
    report.model_performance;


  const matrix =
    performance
      .production
      .confusion_matrix;


  const tn =
    matrix?.[0]?.[0] ?? 0;

  const fp =
    matrix?.[0]?.[1] ?? 0;

  const fn =
    matrix?.[1]?.[0] ?? 0;

  const tp =
    matrix?.[1]?.[1] ?? 0;



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
        {/* TOP NAVIGATION */}
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
            lg:grid-cols-[1.3fr_0.7fr]
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

              <Gauge
                size={17}
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

                Model Monitoring

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

              Model
              <br />
              Performance.

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

              Compare live production performance
              against the model&apos;s trusted held-out
              baseline and detect degradation before
              unreliable predictions become normal.

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

              Performance Status

            </p>


            <p
              className="
                mt-5
                text-4xl
                font-medium
              "
            >

              {
                performance.status
              }

            </p>


            <p
              className="
                mt-4
                max-w-sm
                text-sm
                leading-6
                text-white/40
              "
            >

              Production metrics are evaluated
              against the baseline generated from
              held-out reference data.

            </p>

          </div>

        </section>



        {/* ================================================= */}
        {/* METRIC CARDS */}
        {/* ================================================= */}

        <section
          className="
            mt-16
            grid
            gap-4
            md:grid-cols-2
            xl:grid-cols-4
          "
        >

          {
            metrics.map(
              (metric) => (

                <MetricCard
                  key={
                    metric.name
                  }
                  name={
                    metric.name
                  }
                  baseline={
                    metric.baseline
                  }
                  production={
                    metric.production
                  }
                  drop={
                    metric.drop
                  }
                />

              )
            )
          }

        </section>



        {/* ================================================= */}
        {/* LARGEST DEGRADATION */}
        {/* ================================================= */}

        {largestDrop && (

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

            <div
              className="
                flex
                items-center
                gap-3
              "
            >

              <TrendingDown
                size={18}
                className="
                  text-black/50
                "
              />

              <p
                className="
                  text-[10px]
                  uppercase
                  tracking-[0.3em]
                  text-black/40
                "
              >

                Largest Performance Degradation

              </p>

            </div>


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
                    text-5xl
                    font-semibold
                    uppercase
                    tracking-[-0.055em]
                    md:text-7xl
                  "
                >

                  {
                    largestDrop.name
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

                  This metric currently shows the
                  largest difference between the
                  reference baseline and live
                  production performance.

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

                  Performance drop

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
                    formatDrop(
                      largestDrop.drop
                    )
                  }

                </p>

              </div>

            </div>

          </section>

        )}



        {/* ================================================= */}
        {/* BASELINE VS PRODUCTION */}
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
              flex
              flex-wrap
              items-end
              justify-between
              gap-5
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

                Metric Comparison

              </p>


              <h2
                className="
                  mt-2
                  text-2xl
                  font-medium
                "
              >

                Baseline vs production

              </h2>

            </div>


            <div
              className="
                flex
                gap-5
                text-xs
                text-white/35
              "
            >

              <span
                className="
                  flex
                  items-center
                  gap-2
                "
              >

                <span
                  className="
                    h-2
                    w-2
                    rounded-full
                    bg-white/25
                  "
                />

                Baseline

              </span>


              <span
                className="
                  flex
                  items-center
                  gap-2
                "
              >

                <span
                  className="
                    h-2
                    w-2
                    rounded-full
                    bg-white
                  "
                />

                Production

              </span>

            </div>

          </div>


          <div
            className="
              space-y-10
            "
          >

            {
              metrics.map(
                (metric) => (

                  <ComparisonBar
                    key={
                      metric.name
                    }
                    name={
                      metric.name
                    }
                    baseline={
                      metric.baseline
                    }
                    production={
                      metric.production
                    }
                  />

                )
              )
            }

          </div>

        </section>



        {/* ================================================= */}
        {/* CONFUSION MATRIX */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            grid
            gap-6
            lg:grid-cols-[0.9fr_1.1fr]
          "
        >

          <div
            className="
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

                Production Classification

              </p>

            </div>


            <h2
              className="
                mt-3
                text-2xl
                font-medium
              "
            >

              Confusion matrix

            </h2>


            <p
              className="
                mt-4
                max-w-lg
                text-sm
                leading-7
                text-white/40
              "
            >

              Shows how the production model
              classifications compare with the
              actual production labels.

            </p>

          </div>



          <div
            className="
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
                grid
                grid-cols-[90px_1fr_1fr]
                gap-2
                text-center
              "
            >

              <div />


              <MatrixHeader>
                Predicted Normal
              </MatrixHeader>


              <MatrixHeader>
                Predicted Fraud
              </MatrixHeader>


              <MatrixHeader>
                Actual Normal
              </MatrixHeader>


              <MatrixCell
                value={tn}
                label="True Negative"
              />


              <MatrixCell
                value={fp}
                label="False Positive"
              />


              <MatrixHeader>
                Actual Fraud
              </MatrixHeader>


              <MatrixCell
                value={fn}
                label="False Negative"
              />


              <MatrixCell
                value={tp}
                label="True Positive"
              />

            </div>

          </div>

        </section>



        {/* ================================================= */}
        {/* METRIC EXPLANATIONS */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            grid
            gap-4
            md:grid-cols-2
            xl:grid-cols-4
          "
        >

          <ExplanationCard
            title="Accuracy"
            description="
              Fraction of all predictions that
              were classified correctly.
            "
          />


          <ExplanationCard
            title="Precision"
            description="
              Among transactions predicted as
              fraud, how many were actually fraud.
            "
          />


          <ExplanationCard
            title="Recall"
            description="
              Among actual fraud transactions,
              how many the model successfully found.
            "
          />


          <ExplanationCard
            title="F1 Score"
            description="
              Harmonic balance between precision
              and recall.
            "
          />

        </section>

      </div>

    </main>
  );
}



// =========================================================
// METRIC CARD
// =========================================================

function MetricCard({
  name,
  baseline,
  production,
  drop,
}: {
  name: string;
  baseline: number;
  production: number;
  drop: number;
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
          text-xs
          uppercase
          tracking-[0.18em]
          text-white/30
        "
      >

        {name}

      </p>


      <p
        className="
          mt-6
          text-4xl
          font-medium
          tracking-[-0.04em]
        "
      >

        {
          formatPercent(
            production
          )
        }

      </p>


      <p
        className="
          mt-2
          text-xs
          text-white/30
        "
      >

        baseline{" "}

        {
          formatPercent(
            baseline
          )
        }

      </p>


      <div
        className="
          mt-6
          border-t
          border-white/10
          pt-4
        "
      >

        <span
          className="
            font-mono
            text-xs
            text-white/50
          "
        >

          {
            formatDrop(
              drop
            )
          }

        </span>

      </div>

    </div>
  );
}



// =========================================================
// COMPARISON BAR
// =========================================================

function ComparisonBar({
  name,
  baseline,
  production,
}: {
  name: string;
  baseline: number;
  production: number;
}) {

  const baselineWidth =
    Math.min(
      Math.max(
        baseline * 100,
        0
      ),
      100
    );


  const productionWidth =
    Math.min(
      Math.max(
        production * 100,
        0
      ),
      100
    );


  return (
    <div>

      <div
        className="
          mb-4
          flex
          items-end
          justify-between
          gap-5
        "
      >

        <p
          className="
            text-sm
            text-white/60
          "
        >

          {name}

        </p>


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

            B{" "}

            {
              formatPercent(
                baseline
              )
            }

          </span>


          <span>

            P{" "}

            {
              formatPercent(
                production
              )
            }

          </span>

        </div>

      </div>


      {/* BASELINE */}

      <div
        className="
          mb-2
          h-2
          overflow-hidden
          rounded-full
          bg-white/[0.05]
        "
      >

        <div
          className="
            h-full
            rounded-full
            bg-white/25
          "
          style={{
            width:
              `${baselineWidth}%`,
          }}
        />

      </div>


      {/* PRODUCTION */}

      <div
        className="
          h-2
          overflow-hidden
          rounded-full
          bg-white/[0.05]
        "
      >

        <div
          className="
            h-full
            rounded-full
            bg-white
          "
          style={{
            width:
              `${productionWidth}%`,
          }}
        />

      </div>

    </div>
  );
}



// =========================================================
// MATRIX
// =========================================================

function MatrixHeader({
  children,
}: {
  children: React.ReactNode;
}) {

  return (
    <div
      className="
        flex
        min-h-[70px]
        items-center
        justify-center
        rounded-xl
        px-2
        text-[10px]
        uppercase
        tracking-[0.12em]
        text-white/30
      "
    >

      {children}

    </div>
  );
}


function MatrixCell({
  value,
  label,
}: {
  value: number;
  label: string;
}) {

  return (
    <div
      className="
        flex
        min-h-[120px]
        flex-col
        items-center
        justify-center
        rounded-2xl
        border
        border-white/10
        bg-white/[0.025]
        p-4
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
          text-[10px]
          uppercase
          tracking-[0.12em]
          text-white/30
        "
      >

        {label}

      </p>

    </div>
  );
}



// =========================================================
// EXPLANATION CARD
// =========================================================

function ExplanationCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {

  return (
    <div
      className="
        rounded-[24px]
        border
        border-white/10
        p-6
      "
    >

      <h3
        className="
          text-lg
          font-medium
        "
      >

        {title}

      </h3>


      <p
        className="
          mt-3
          text-sm
          leading-6
          text-white/40
        "
      >

        {description}

      </p>

    </div>
  );
}



// =========================================================
// FORMATTERS
// =========================================================

function formatPercent(
  value: number
) {

  return `${(
    value * 100
  ).toFixed(2)}%`;

}


function formatDrop(
  value: number
) {

  const points =
    Math.abs(
      value * 100
    ).toFixed(2);


  if (
    value > 0
  ) {

    return `-${points} pp`;

  }


  if (
    value < 0
  ) {

    return `+${points} pp`;

  }


  return "0.00 pp";
}