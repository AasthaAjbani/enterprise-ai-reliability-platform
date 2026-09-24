"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  Activity,
  Check,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
} from "lucide-react";

import {
  fetchSelfHealingStatus,
} from "@/lib/api";

import type {
  SelfHealingStatus,
} from "@/types/selfHealing";


export default function SelfHealingStatusPanel() {

  const [
    data,
    setData,
  ] = useState<SelfHealingStatus | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState(false);


  // =====================================================
  // LOAD DATA
  // =====================================================

  async function loadStatus() {

    try {

      setLoading(true);
      setError(false);

      const result =
        await fetchSelfHealingStatus();

      setData(result);

    } catch (err) {

      console.error(
        "Self-healing API unavailable:",
        err
      );

      setError(true);

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadStatus();

  }, []);



  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (
      <section
        className="
          mt-6
          rounded-[30px]
          border
          border-white/10
          bg-white/[0.02]
          p-8
          text-white
        "
      >

        <div
          className="
            flex
            items-center
            gap-3
            text-sm
            text-white/35
          "
        >

          <RefreshCw
            size={15}
            className="animate-spin"
          />

          Loading autonomous healing state...

        </div>

      </section>
    );

  }



  // =====================================================
  // ERROR
  // =====================================================

  if (
    error
    ||
    !data
  ) {

    return (
      <section
        className="
          mt-6
          rounded-[30px]
          border
          border-white/10
          bg-white/[0.02]
          p-8
          text-white
        "
      >

        <div
          className="
            flex
            items-center
            gap-3
            text-sm
            text-white/35
          "
        >

          <TriangleAlert size={16} />

          Autonomous healing status unavailable.

        </div>

      </section>
    );

  }



  const trigger =
    data.healing_trigger;


  const healthy =
    trigger?.status === "HEALTHY";


  // =====================================================
  // PAGE
  // =====================================================

  return (
    <section
      className="
        mt-6
        overflow-hidden
        rounded-[32px]
        border
        border-white/10
        bg-white/[0.02]
        text-white
      "
    >

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div
        className="
          flex
          flex-wrap
          items-start
          justify-between
          gap-8
          border-b
          border-white/10
          p-7
          md:p-10
          lg:p-12
        "
      >

        <div>

          <div
            className="
              flex
              items-center
              gap-3
            "
          >

            <Sparkles
              size={18}
              className="
                text-white/35
              "
            />


            <p
              className="
                text-[10px]
                uppercase
                tracking-[0.32em]
                text-white/30
              "
            >

              Autonomous Healing

            </p>

          </div>


          <h2
            className="
              mt-5
              text-4xl
              font-medium
              tracking-[-0.045em]
              md:text-6xl
            "
          >

            Know when
            <br />
            not to retrain.

          </h2>


          <p
            className="
              mt-6
              max-w-2xl
              text-sm
              leading-7
              text-white/40
            "
          >

            The active production model is evaluated
            before retraining begins. A challenger is
            created only when degradation crosses the
            configured critical threshold.

          </p>

        </div>


        <SystemBadge
          status={
            trigger?.status
            ??
            data.status
          }
        />

      </div>



      {/* ================================================= */}
      {/* CURRENT DECISION */}
      {/* ================================================= */}

      <div
        className="
          grid
          border-b
          border-white/10
          md:grid-cols-2
          xl:grid-cols-4
        "
      >

        <Metric
          label="Latest Decision"
          value={
            prettify(
              data.status
            )
          }
          description="Result of the latest pipeline run"
        />


        <Metric
          label="Active Champion"
          value={
            data.champion_version
              ?
              `V${data.champion_version}`
              :
              "—"
          }
          description="Model currently serving production"
        />


        <Metric
          label="Healing Trigger"
          value={
            data.healing_required
              ?
              "REQUIRED"
              :
              "NOT REQUIRED"
          }
          description="Whether retraining should begin"
        />


        <Metric
          label="Retraining"
          value={
            data.healing_required
              ?
              "TRIGGERED"
              :
              "SKIPPED"
          }
          description={
            data.healing_required
              ?
              "Recovery workflow activated"
              :
              "Healthy model preserved"
          }
        />

      </div>



      {/* ================================================= */}
      {/* HEALTH CHECK */}
      {/* ================================================= */}

      {trigger && (

        <div
          className="
            p-7
            md:p-10
            lg:p-12
          "
        >

          <div
            className="
              flex
              flex-wrap
              items-center
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

                Pre-Retraining Health Check

              </p>


              <h3
                className="
                  mt-2
                  text-2xl
                  font-medium
                "
              >

                Active model evaluation

              </h3>

            </div>


            <button
              onClick={loadStatus}
              className="
                flex
                items-center
                gap-2
                rounded-full
                border
                border-white/10
                px-4
                py-2
                text-xs
                text-white/40
                transition
                hover:border-white/25
                hover:text-white
              "
            >

              <RefreshCw size={13} />

              Refresh

            </button>

          </div>



          {/* PERFORMANCE */}

          <div
            className="
              mt-8
              grid
              gap-4
              md:grid-cols-2
            "
          >

            <PerformanceBlock
              title="Reference Baseline"
              f1={
                trigger
                  .baseline
                  .f1
              }
              recall={
                trigger
                  .baseline
                  .recall
              }
              precision={
                trigger
                  .baseline
                  .precision
              }
            />


            <PerformanceBlock
              title="Active Production Model"
              f1={
                trigger
                  .production
                  .f1
              }
              recall={
                trigger
                  .production
                  .recall
              }
              precision={
                trigger
                  .production
                  .precision
              }
              active
            />

          </div>



          {/* DEGRADATION */}

          <div
            className="
              mt-4
              grid
              gap-4
              md:grid-cols-2
              xl:grid-cols-4
            "
          >

            <SignalCard
              label="F1 Change"
              value={
                formatInverseDrop(
                  trigger
                    .degradation
                    .f1_drop
                )
              }
            />


            <SignalCard
              label="Recall Change"
              value={
                formatInverseDrop(
                  trigger
                    .degradation
                    .recall_drop
                )
              }
            />


            <SignalCard
              label="Warning Threshold"
              value={
                `${(
                  trigger
                    .thresholds
                    .warning_drop
                  *
                  100
                ).toFixed(0)} pp`
              }
            />


            <SignalCard
              label="Critical Threshold"
              value={
                `${(
                  trigger
                    .thresholds
                    .critical_drop
                  *
                  100
                ).toFixed(0)} pp`
              }
            />

          </div>



          {/* DECISION */}

          <div
            className={`
              mt-6
              rounded-[26px]
              border
              p-7
              md:p-9

              ${
                healthy
                  ?
                  "border-emerald-400/20 bg-emerald-400/[0.05]"
                  :
                  "border-amber-400/20 bg-amber-400/[0.05]"
              }
            `}
          >

            <div
              className="
                flex
                flex-wrap
                items-start
                gap-4
              "
            >

              <div
                className={`
                  flex
                  h-10
                  w-10
                  shrink-0
                  items-center
                  justify-center
                  rounded-full

                  ${
                    healthy
                      ?
                      "bg-emerald-400/10 text-emerald-300"
                      :
                      "bg-amber-400/10 text-amber-300"
                  }
                `}
              >

                {
                  healthy
                    ?
                    <ShieldCheck size={18} />
                    :
                    <Activity size={18} />
                }

              </div>


              <div>

                <p
                  className="
                    text-xs
                    uppercase
                    tracking-[0.18em]
                    text-white/30
                  "
                >

                  System Decision

                </p>


                <p
                  className="
                    mt-2
                    text-xl
                    font-medium
                  "
                >

                  {
                    trigger.reason
                  }

                </p>


                <p
                  className="
                    mt-3
                    max-w-3xl
                    text-sm
                    leading-6
                    text-white/35
                  "
                >

                  {
                    trigger.healing_required
                      ?
                      (
                        "The critical degradation threshold "
                        +
                        "was crossed, so the automated "
                        +
                        "recovery workflow may proceed."
                      )
                      :
                      (
                        "No challenger was trained, no new "
                        +
                        "MLflow version was created, and "
                        +
                        "the production model was left unchanged."
                      )
                  }

                </p>

              </div>

            </div>

          </div>



          {/* EXECUTION FLAGS */}

          <div
            className="
              mt-6
              grid
              gap-3
              md:grid-cols-3
            "
          >

            <ExecutionFlag
              label="Promotion Attempted"
              completed={
                data.promotion_attempted
              }
            />


            <ExecutionFlag
              label="Promotion Completed"
              completed={
                data.promotion_completed
              }
            />


            <ExecutionFlag
              label="Verification Completed"
              completed={
                data.verification_completed
              }
            />

          </div>



          {/* TIME */}

          <div
            className="
              mt-7
              flex
              flex-wrap
              gap-x-8
              gap-y-2
              text-xs
              text-white/25
            "
          >

            {
              data.completed_at
              &&
              (
                <span>

                  Last check:{" "}

                  {
                    formatDate(
                      data.completed_at
                    )
                  }

                </span>
              )
            }


            {
              data.duration_seconds
              !== undefined
              &&
              data.duration_seconds
              !== null
              &&
              (
                <span>

                  Runtime:{" "}

                  {
                    data.duration_seconds
                      .toFixed(2)
                  }s

                </span>
              )
            }

          </div>

        </div>

      )}

    </section>
  );
}


// =========================================================
// SYSTEM BADGE
// =========================================================

function SystemBadge({
  status,
}: {
  status: string;
}) {

  const healthy =
    status === "HEALTHY"
    ||
    status === "NO_HEALING_REQUIRED";


  return (
    <span
      className={`
        inline-flex
        items-center
        gap-2
        rounded-full
        border
        px-4
        py-2
        text-xs
        tracking-[0.12em]

        ${
          healthy
            ?
            "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
            :
            "border-amber-400/20 bg-amber-400/10 text-amber-300"
        }
      `}
    >

      {
        healthy
          ?
          <Check size={13} />
          :
          <Activity size={13} />
      }

      {status}

    </span>
  );
}


// =========================================================
// MAIN METRIC
// =========================================================

function Metric({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description: string;
}) {

  return (
    <div
      className="
        border-b
        border-white/10
        p-7
        md:p-8
        md:[&:nth-child(odd)]:border-r
        xl:border-b-0
        xl:border-r
        xl:last:border-r-0
      "
    >

      <p
        className="
          text-[10px]
          uppercase
          tracking-[0.18em]
          text-white/30
        "
      >

        {label}

      </p>


      <p
        className="
          mt-5
          text-2xl
          font-medium
          tracking-[-0.035em]
        "
      >

        {value}

      </p>


      <p
        className="
          mt-3
          text-xs
          leading-5
          text-white/30
        "
      >

        {description}

      </p>

    </div>
  );
}


// =========================================================
// PERFORMANCE BLOCK
// =========================================================

function PerformanceBlock({
  title,
  f1,
  recall,
  precision,
  active = false,
}: {
  title: string;
  f1: number;
  recall: number;
  precision: number;
  active?: boolean;
}) {

  return (
    <div
      className={`
        rounded-[24px]
        border
        p-6
        md:p-7

        ${
          active
            ?
            "border-emerald-400/20 bg-emerald-400/[0.04]"
            :
            "border-white/10 bg-white/[0.02]"
        }
      `}
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
            text-sm
            font-medium
          "
        >

          {title}

        </p>


        {
          active
          &&
          (
            <span
              className="
                text-[10px]
                tracking-[0.14em]
                text-emerald-300
              "
            >

              ACTIVE

            </span>
          )
        }

      </div>


      <div
        className="
          mt-7
          grid
          grid-cols-3
          gap-3
        "
      >

        <MiniMetric
          label="F1"
          value={
            formatPercent(f1)
          }
        />


        <MiniMetric
          label="Recall"
          value={
            formatPercent(recall)
          }
        />


        <MiniMetric
          label="Precision"
          value={
            formatPercent(precision)
          }
        />

      </div>

    </div>
  );
}


// =========================================================
// MINI METRIC
// =========================================================

function MiniMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div
      className="
        rounded-[16px]
        bg-black/20
        p-4
      "
    >

      <p
        className="
          font-mono
          text-lg
        "
      >

        {value}

      </p>


      <p
        className="
          mt-1
          text-[10px]
          uppercase
          tracking-[0.1em]
          text-white/25
        "
      >

        {label}

      </p>

    </div>
  );
}


// =========================================================
// SIGNAL
// =========================================================

function SignalCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div
      className="
        rounded-[18px]
        border
        border-white/10
        bg-white/[0.02]
        p-5
      "
    >

      <p
        className="
          font-mono
          text-xl
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
          text-white/25
        "
      >

        {label}

      </p>

    </div>
  );
}


// =========================================================
// EXECUTION FLAG
// =========================================================

function ExecutionFlag({
  label,
  completed,
}: {
  label: string;
  completed: boolean;
}) {

  return (
    <div
      className="
        flex
        items-center
        justify-between
        gap-4
        rounded-[18px]
        border
        border-white/10
        p-5
      "
    >

      <p
        className="
          text-xs
          text-white/40
        "
      >

        {label}

      </p>


      <span
        className={`
          text-[10px]
          tracking-[0.12em]

          ${
            completed
              ?
              "text-emerald-300"
              :
              "text-white/30"
          }
        `}
      >

        {
          completed
            ?
            "YES"
            :
            "NO"
        }

      </span>

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


function formatInverseDrop(
  drop: number
) {

  const change =
    -drop * 100;


  const prefix =
    change > 0
      ?
      "+"
      :
      "";


  return (
    `${prefix}${change.toFixed(2)} pp`
  );
}


function prettify(
  value: string
) {

  return value
    .replaceAll(
      "_",
      " "
    );
}


function formatDate(
  value: string
) {

  const date =
    new Date(value);


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {

    return value;

  }


  return new Intl.DateTimeFormat(
    "en-US",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(date);
}