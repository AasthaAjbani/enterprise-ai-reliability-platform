"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  Check,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
} from "lucide-react";

import {
  fetchDeploymentState,
  fetchSelfHealingState,
} from "@/lib/api";

import type {
  DeploymentState,
  MetricSet,
} from "@/types/deployment";

import type {
  SelfHealingState,
} from "@/types/selfHealing";


export default function SelfHealingStatusPanel() {

  const [
    deployment,
    setDeployment,
  ] = useState<DeploymentState | null>(
    null
  );


  const [
    healing,
    setHealing,
  ] = useState<SelfHealingState | null>(
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


  useEffect(() => {

    async function load() {

      try {

        setLoading(true);


        const [
          deploymentData,
          healingData,
        ] = await Promise.all([
          fetchDeploymentState(),
          fetchSelfHealingState(),
        ]);


        setDeployment(
          deploymentData
        );


        setHealing(
          healingData
        );


        setError(
          null
        );

      } catch (err) {

        console.error(
          err
        );


        setError(
          "Self-healing lifecycle data unavailable."
        );

      } finally {

        setLoading(
          false
        );

      }

    }


    load();

  }, []);


  if (loading) {

    return (
      <section
        className="
          mt-6
          rounded-[28px]
          border
          border-white/10
          bg-white/[0.025]
          p-8
        "
      >

        <div
          className="
            flex
            items-center
            gap-3
            text-sm
            text-white/40
          "
        >

          <RefreshCw
            size={16}
            className="animate-spin"
          />

          Loading self-healing lifecycle...

        </div>

      </section>
    );
  }


  if (
    error
    ||
    !deployment
    ||
    !healing
  ) {

    return (
      <section
        className="
          mt-6
          rounded-[28px]
          border
          border-white/10
          bg-white/[0.025]
          p-8
          text-sm
          text-white/40
        "
      >

        {error}

      </section>
    );
  }


  const trigger =
    healing.healing_trigger;


  const qualityGate =
    deployment.quality_gate;


  const previousModel =
    deployment
      .validation
      .previous_model;


  const promotedModel =
    deployment
      .validation
      .promoted_model;


  return (
    <section
      className="
        mt-6
        overflow-hidden
        rounded-[28px]
        border
        border-white/10
        bg-white/[0.025]
      "
    >

      {/* HEADER */}

      <div
        className="
          flex
          flex-col
          gap-6
          border-b
          border-white/10
          p-7
          md:p-9
          lg:flex-row
          lg:items-center
          lg:justify-between
        "
      >

        <div>

          <p
            className="
              text-[10px]
              uppercase
              tracking-[0.3em]
              text-white/30
            "
          >

            Autonomous Recovery

          </p>


          <h3
            className="
              mt-3
              text-3xl
              font-medium
              tracking-[-0.04em]
              md:text-4xl
            "
          >

            Self-healing lifecycle

          </h3>


          <p
            className="
              mt-3
              max-w-2xl
              text-sm
              leading-6
              text-white/35
            "
          >

            Critical degradation triggered challenger
            training, quality-gate validation, promotion
            and deployment verification.

          </p>

        </div>


        <div
          className="
            inline-flex
            w-fit
            items-center
            gap-2
            rounded-full
            border
            border-emerald-400/20
            bg-emerald-400/10
            px-4
            py-2
            text-[10px]
            font-medium
            tracking-[0.15em]
            text-emerald-300
          "
        >

          <ShieldCheck size={14} />

          {healing.status}

        </div>

      </div>


      {/* DEPLOYMENT SUMMARY */}

      <div
        className="
          grid
          border-b
          border-white/10
          md:grid-cols-2
          xl:grid-cols-4
        "
      >

        <SummaryMetric
          label="Active champion"
          value={`V${deployment.champion_version}`}
        />


        <SummaryMetric
          label="Previous champion"
          value={
            deployment.previous_champion_version
              ?
              `V${deployment.previous_champion_version}`
              :
              "—"
          }
        />


        <SummaryMetric
          label="Rollback"
          value={
            deployment.rollback_available
              ?
              "AVAILABLE"
              :
              "UNAVAILABLE"
          }
        />


        <SummaryMetric
          label="Recovery time"
          value={
            healing.duration_seconds !== null
              ?
              `${healing.duration_seconds.toFixed(2)}s`
              :
              "—"
          }
        />

      </div>


      {/* RECOVERY SEQUENCE */}

      <div
        className="
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

          Recovery sequence

        </p>


        <div
          className="
            mt-7
            grid
            gap-3
            md:grid-cols-2
            xl:grid-cols-4
          "
        >

          <LifecycleStep
            number="01"
            title="Degradation detected"
            description="Champion V2 breached the critical F1 / recall degradation threshold."
            complete={
              healing.healing_required
            }
          />


          <LifecycleStep
            number="02"
            title="Challenger qualified"
            description="V3 passed the predefined F1, recall and precision promotion gate."
            complete={
              qualityGate.eligible
            }
          />


          <LifecycleStep
            number="03"
            title="Champion promoted"
            description="The challenger artifact replaced the active production champion."
            complete={
              healing.promotion_completed
            }
          />


          <LifecycleStep
            number="04"
            title="Deployment verified"
            description="The active artifact was validated after promotion with rollback preserved."
            complete={
              healing.verification_completed
            }
          />

        </div>


        {/* EVIDENCE */}

        <div
          className="
            mt-8
            grid
            gap-5
            xl:grid-cols-2
          "
        >

          <div
            className="
              rounded-[24px]
              border
              border-white/10
              bg-black/20
              p-6
            "
          >

            <p
              className="
                text-[10px]
                uppercase
                tracking-[0.24em]
                text-white/30
              "
            >

              Trigger evidence

            </p>


            {trigger ? (

              <div
                className="
                  mt-6
                  grid
                  gap-4
                  sm:grid-cols-2
                "
              >

                <ChangeMetric
                  label="F1"
                  before={
                    trigger.baseline.f1
                  }
                  after={
                    trigger.production.f1
                  }
                />


                <ChangeMetric
                  label="Recall"
                  before={
                    trigger.baseline.recall
                  }
                  after={
                    trigger.production.recall
                  }
                />

              </div>

            ) : (

              <p
                className="
                  mt-5
                  text-sm
                  text-white/35
                "
              >

                No trigger evidence recorded.

              </p>

            )}

          </div>


          <div
            className="
              rounded-[24px]
              border
              border-emerald-400/15
              bg-emerald-400/[0.035]
              p-6
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
                  tracking-[0.24em]
                  text-white/30
                "
              >

                Promotion validation

              </p>


              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-[10px]
                  tracking-[0.12em]
                  text-emerald-300
                "
              >

                <Check size={13} />

                VERIFIED

              </div>

            </div>


            <div
              className="
                mt-6
                grid
                gap-4
                sm:grid-cols-2
              "
            >

              <ModelEvidence
                title={`V${deployment.previous_champion_version}`}
                metrics={
                  previousModel
                }
              />


              <ModelEvidence
                title={`V${deployment.champion_version}`}
                metrics={
                  promotedModel
                }
                promoted
              />

            </div>

          </div>

        </div>


        {/* QUALITY GATE IMPROVEMENTS */}

        <div
          className="
            mt-5
            grid
            gap-3
            md:grid-cols-3
          "
        >

          <Improvement
            label="F1 improvement"
            value={
              formatPointChange(
                qualityGate.f1_improvement
              )
            }
          />


          <Improvement
            label="Recall improvement"
            value={
              formatPointChange(
                qualityGate.recall_improvement
              )
            }
          />


          <Improvement
            label="Precision change"
            value={
              formatPointChange(
                qualityGate.precision_change
              )
            }
          />

        </div>


        {deployment.rollback_available && (

          <div
            className="
              mt-6
              flex
              items-center
              gap-3
              text-xs
              text-white/35
            "
          >

            <RotateCcw size={15} />

            Previous champion V{
              deployment.previous_champion_version
            } remains available for rollback.

          </div>

        )}

      </div>

    </section>
  );
}


// =========================================================
// SUMMARY METRIC
// =========================================================

function SummaryMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div
      className="
        border-b
        border-white/10
        p-6
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
          tracking-[0.2em]
          text-white/30
        "
      >

        {label}

      </p>


      <p
        className="
          mt-4
          text-2xl
          font-medium
          tracking-[-0.04em]
        "
      >

        {value}

      </p>

    </div>
  );
}


// =========================================================
// LIFECYCLE STEP
// =========================================================

function LifecycleStep({
  number,
  title,
  description,
  complete,
}: {
  number: string;
  title: string;
  description: string;
  complete: boolean;
}) {

  return (
    <div
      className={`
        rounded-[22px]
        border
        p-5
        ${
          complete
            ?
            "border-emerald-400/20 bg-emerald-400/[0.035]"
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


        {complete && (

          <ShieldCheck
            size={15}
            className="text-emerald-300"
          />

        )}

      </div>


      <p
        className="
          mt-7
          text-lg
          font-medium
        "
      >

        {title}

      </p>


      <p
        className="
          mt-2
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
// CHANGE METRIC
// =========================================================

function ChangeMetric({
  label,
  before,
  after,
}: {
  label: string;
  before: number;
  after: number;
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


      <div
        className="
          mt-3
          flex
          items-center
          gap-3
          font-mono
        "
      >

        <span
          className="
            text-white/45
          "
        >

          {formatPercent(before)}

        </span>


        <span
          className="
            text-white/20
          "
        >

          →

        </span>


        <span>

          {formatPercent(after)}

        </span>

      </div>

    </div>
  );
}


// =========================================================
// MODEL EVIDENCE
// =========================================================

function ModelEvidence({
  title,
  metrics,
  promoted = false,
}: {
  title: string;
  metrics: MetricSet;
  promoted?: boolean;
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

      <div
        className="
          flex
          items-center
          justify-between
        "
      >

        <span
          className="
            font-medium
          "
        >

          {title}

        </span>


        {promoted && (

          <span
            className="
              rounded-full
              bg-emerald-400/10
              px-3
              py-1
              text-[9px]
              tracking-[0.14em]
              text-emerald-300
            "
          >

            PROMOTED

          </span>

        )}

      </div>


      <div
        className="
          mt-5
          grid
          grid-cols-2
          gap-3
        "
      >

        <EvidenceMetric
          label="F1"
          value={
            formatPercent(
              metrics.f1
            )
          }
        />


        <EvidenceMetric
          label="Recall"
          value={
            formatPercent(
              metrics.recall
            )
          }
        />

      </div>

    </div>
  );
}


// =========================================================
// EVIDENCE METRIC
// =========================================================

function EvidenceMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div
      className="
        rounded-xl
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
          text-[9px]
          uppercase
          tracking-[0.14em]
          text-white/25
        "
      >

        {label}

      </p>

    </div>
  );
}


// =========================================================
// IMPROVEMENT
// =========================================================

function Improvement({
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
          tracking-[0.14em]
          text-white/30
        "
      >

        {label}

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


function formatPointChange(
  value: number
) {

  const points =
    value * 100;


  const prefix =
    points > 0
      ?
      "+"
      :
      "";


  return `${prefix}${points.toFixed(2)} pp`;
}