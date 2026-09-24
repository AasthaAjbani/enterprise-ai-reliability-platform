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
  ArrowRight,
  BrainCircuit,
  Check,
  Database,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
  Workflow,
} from "lucide-react";

import {
  fetchDeploymentStatus,
  fetchReliabilityReport,
} from "@/lib/api";

import type {
  ReliabilityReport,
  ReliabilityStatus,
} from "@/types/reliability";

import type {
  DeploymentStatus,
} from "@/types/deployment";

import SelfHealingStatusPanel
  from "@/components/dashboard/SelfHealingStatusPanel";


// =========================================================
// DASHBOARD
// =========================================================

export default function ReliabilityDashboard() {

  const [
    report,
    setReport,
  ] = useState<ReliabilityReport | null>(
    null
  );


  const [
    deployment,
    setDeployment,
  ] = useState<DeploymentStatus | null>(
    null
  );


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    refreshing,
    setRefreshing,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );


  // =======================================================
  // LOAD DASHBOARD
  // =======================================================

  async function loadDashboard(
    isRefresh = false
  ) {

    try {

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }


      setError(null);


      const [
        reliabilityResult,
        deploymentResult,
      ] = await Promise.allSettled([
        fetchReliabilityReport(),
        fetchDeploymentStatus(),
      ]);


      if (
        reliabilityResult.status
        === "rejected"
      ) {

        throw new Error(
          "Reliability API unavailable."
        );

      }


      setReport(
        reliabilityResult.value
      );


      if (
        deploymentResult.status
        === "fulfilled"
      ) {

        setDeployment(
          deploymentResult.value
        );

      } else {

        console.warn(
          "Deployment API unavailable:",
          deploymentResult.reason
        );

        setDeployment(null);

      }

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load reliability dashboard."
      );

    } finally {

      setLoading(false);
      setRefreshing(false);

    }

  }


  useEffect(() => {

    loadDashboard();

  }, []);



  // =======================================================
  // DRIFT COUNTS
  // =======================================================

  const driftCounts =
    useMemo(() => {

      if (!report) {

        return {
          high: 0,
          moderate: 0,
          low: 0,
        };

      }


      return {

        high:
          report
            .data_drift
            .features
            .filter(
              (feature) =>
                feature.drift_level
                === "HIGH"
            )
            .length,

        moderate:
          report
            .data_drift
            .features
            .filter(
              (feature) =>
                feature.drift_level
                === "MODERATE"
            )
            .length,

        low:
          report
            .data_drift
            .features
            .filter(
              (feature) =>
                feature.drift_level
                === "LOW"
            )
            .length,

      };

    }, [report]);



  // =======================================================
  // TOP ROOT CAUSE
  // =======================================================

  const topRootCause =
    useMemo(() => {

      if (
        !report
        ||
        report.root_causes.length === 0
      ) {

        return null;

      }


      return [
        ...report.root_causes,
      ].sort(
        (
          first,
          second
        ) =>
          second.root_cause_score
          -
          first.root_cause_score
      )[0];

    }, [report]);



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

          LOADING RELIABILITY SYSTEM

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
            size={42}
            className="
              mx-auto
              mb-6
              text-white/35
            "
          />


          <h1
            className="
              text-3xl
              font-medium
            "
          >

            Reliability system unavailable

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
            onClick={() =>
              loadDashboard()
            }
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
            href="/"
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

            Home

          </Link>


          <button
            onClick={() =>
              loadDashboard(true)
            }
            disabled={refreshing}
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
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >

            <RefreshCw
              size={13}
              className={
                refreshing
                  ? "animate-spin"
                  : ""
              }
            />

            {
              refreshing
                ? "Refreshing"
                : "Refresh System"
            }

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

            <p
              className="
                text-xs
                uppercase
                tracking-[0.35em]
                text-white/30
              "
            >

              Enterprise AI Reliability

            </p>


            <h1
              className="
                mt-6
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

              Your model
              <br />
              is{" "}

              <span className="text-white/40">

                {
                  report
                    .overall_status
                    .toLowerCase()
                }.

              </span>

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

              One control plane for production data quality,
              drift, model performance, anomalies,
              root-cause analysis and automated model
              recovery.

            </p>

          </div>



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
                tracking-[0.3em]
                text-white/30
              "
            >

              System State

            </p>


            <div
              className="
                mt-6
                flex
                items-center
                justify-between
                gap-5
              "
            >

              <p
                className="
                  text-4xl
                  font-medium
                "
              >

                {
                  report.overall_status
                }

              </p>


              <StatusDot
                status={
                  report.overall_status
                }
              />

            </div>


            <p
              className="
                mt-5
                text-sm
                leading-6
                text-white/40
              "
            >

              Generated from live production
              reliability signals.

            </p>

          </div>

        </section>



        {/* ================================================= */}
        {/* MONITORING CARDS */}
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

          <StatusCard
            href="/drift"
            icon={
              <Database size={19} />
            }
            title="Data Drift"
            status={
              report.data_drift.status
            }
            value={
              `${driftCounts.high} high-risk`
            }
          />


          <StatusCard
            href="/performance"
            icon={
              <Activity size={19} />
            }
            title="Performance"
            status={
              performance.status
            }
            value={
              `F1 ${formatPercent(
                performance
                  .production
                  .f1
              )}`
            }
          />


          <StatusCard
            href="/anomalies"
            icon={
              <Sparkles size={19} />
            }
            title="Anomalies"
            status={
              report
                .anomaly_detection
                .status
            }
            value={
              `${report
                .anomaly_detection
                .anomaly_percentage
                .toFixed(2)}%`
            }
          />


          <StatusCard
            href="/root-cause"
            icon={
              <BrainCircuit size={19} />
            }
            title="Root Cause"
            status={
              report.overall_status
            }
            value={
              topRootCause
                ? topRootCause.feature
                : "No signal"
            }
          />

        </section>



        {/* ================================================= */}
        {/* DEPLOYMENT / PROMOTION HISTORY */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            overflow-hidden
            rounded-[32px]
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
              lg:p-12
            "
          >

            <div
              className="
                flex
                flex-wrap
                items-start
                justify-between
                gap-8
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

                  <Workflow
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

                    Self-Healing Lifecycle

                  </p>

                </div>


                <h2
                  className="
                    mt-5
                    max-w-3xl
                    text-4xl
                    font-medium
                    tracking-[-0.045em]
                    md:text-6xl
                  "
                >

                  From degradation
                  <br />
                  to recovery.

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

                  The platform can identify model
                  degradation, train a challenger,
                  evaluate it against the current model
                  on held-out production data, and
                  promote it only after the quality gate
                  passes.

                </p>

              </div>



              {
                deployment
                  ?
                  (
                    <DeploymentBadge
                      status={
                        deployment.status
                      }
                    />
                  )
                  :
                  (
                    <span
                      className="
                        rounded-full
                        border
                        border-white/10
                        px-4
                        py-2
                        text-xs
                        text-white/30
                      "
                    >

                      Deployment data unavailable

                    </span>
                  )
              }

            </div>

          </div>



          {
            deployment
            &&
            deployment.status
            !== "NOT_DEPLOYED"
              ?
              (
                <>

                  {/* MODEL VERSION CARDS */}

                  <div
                    className="
                      grid
                      border-b
                      border-white/10
                      md:grid-cols-2
                      xl:grid-cols-4
                    "
                  >

                    <DeploymentMetric
                      label="Active Champion"
                      value={
                        deployment
                          .champion_version
                          ?
                          `V${deployment.champion_version}`
                          :
                          "—"
                      }
                      description="Current production model"
                    />


                    <DeploymentMetric
                      label="Previous Champion"
                      value={
                        deployment
                          .previous_champion_version
                          ?
                          `V${deployment.previous_champion_version}`
                          :
                          "—"
                      }
                      description="Previous production version"
                    />


                    <DeploymentMetric
                      label="Quality Gate"
                      value={
                        deployment
                          .quality_gate
                          ?.eligible
                          ?
                          "PASSED"
                          :
                          "BLOCKED"
                      }
                      description={
                        deployment
                          .quality_gate
                          ?.decision
                          ??
                          "No decision available"
                      }
                    />


                    <DeploymentMetric
                      label="Rollback"
                      value={
                        deployment
                          .rollback_available
                          ?
                          "AVAILABLE"
                          :
                          "UNAVAILABLE"
                      }
                      description={
                        deployment
                          .rollback_available
                          ?
                          "Previous model can be restored"
                          :
                          "No rollback artifact available"
                      }
                    />

                  </div>



                  {/* IMPROVEMENT METRICS */}

                  <div
                    className="
                      grid
                      gap-4
                      border-b
                      border-white/10
                      p-7
                      md:grid-cols-3
                      md:p-10
                      lg:p-12
                    "
                  >

                    <ImprovementCard
                      label="F1 Improvement"
                      value={
                        formatPointChange(
                          deployment
                            .quality_gate
                            ?.f1_improvement
                        )
                      }
                    />


                    <ImprovementCard
                      label="Recall Improvement"
                      value={
                        formatPointChange(
                          deployment
                            .quality_gate
                            ?.recall_improvement
                        )
                      }
                    />


                    <ImprovementCard
                      label="Precision Change"
                      value={
                        formatPointChange(
                          deployment
                            .quality_gate
                            ?.precision_change
                        )
                      }
                    />

                  </div>



                  {/* PIPELINE */}

                  <div
                    className="
                      p-7
                      md:p-10
                      lg:p-12
                    "
                  >

                    <p
                      className="
                        text-[10px]
                        uppercase
                        tracking-[0.3em]
                        text-white/30
                      "
                    >

                      Recovery Pipeline

                    </p>


                    <div
                      className="
                        mt-8
                        grid
                        gap-3
                        lg:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr]
                        lg:items-center
                      "
                    >

                      <LifecycleStep
                        number="01"
                        title="Degradation"
                        description="Production reliability drops"
                      />


                      <LifecycleArrow />


                      <LifecycleStep
                        number="02"
                        title="Challenger"
                        description="Recent labeled data retrains model"
                      />


                      <LifecycleArrow />


                      <LifecycleStep
                        number="03"
                        title="Quality Gate"
                        description="Same held-out data evaluates both"
                      />


                      <LifecycleArrow />


                      <LifecycleStep
                        number="04"
                        title="Promotion"
                        description={
                          deployment.status
                          === "PROMOTED"
                            ?
                            `Version ${deployment.champion_version} activated`
                            :
                            "Previous champion restored"
                        }
                        complete
                      />

                    </div>



                    {/* PROMOTION EVIDENCE */}

                    {
                      deployment.validation
                      &&
                      deployment
                        .validation
                        .previous_model
                      &&
                      deployment
                        .validation
                        .promoted_model
                      &&
                      (
                        <div
                          className="
                            mt-12
                            rounded-[26px]
                            border
                            border-white/10
                            bg-black/20
                            p-6
                            md:p-8
                          "
                        >

                          <div
                            className="
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
                                  tracking-[0.25em]
                                  text-white/30
                                "
                              >

                                Promotion Evidence

                              </p>


                              <h3
                                className="
                                  mt-2
                                  text-2xl
                                  font-medium
                                "
                              >

                                Held-out production validation

                              </h3>

                            </div>


                            <p
                              className="
                                max-w-xl
                                text-xs
                                leading-5
                                text-white/30
                              "
                            >

                              {
                                deployment
                                  .validation
                                  .strategy
                              }

                            </p>

                          </div>


                          <div
                            className="
                              mt-8
                              grid
                              gap-6
                              lg:grid-cols-2
                            "
                          >

                            <ModelEvidence
                              title={
                                `Previous Champion V${
                                  deployment
                                    .previous_champion_version
                                  ??
                                  "—"
                                }`
                              }
                              metrics={
                                deployment
                                  .validation
                                  .previous_model
                              }
                            />


                            <ModelEvidence
                              title={
                                `Promoted Champion V${
                                  deployment
                                    .champion_version
                                  ??
                                  "—"
                                }`
                              }
                              metrics={
                                deployment
                                  .validation
                                  .promoted_model
                              }
                              promoted
                            />

                          </div>

                        </div>
                      )
                    }



                    {
                      deployment.promoted_at
                      &&
                      (
                        <p
                          className="
                            mt-7
                            text-xs
                            text-white/25
                          "
                        >

                          Last promotion:{" "}

                          {
                            formatDate(
                              deployment.promoted_at
                            )
                          }

                        </p>
                      )
                    }

                  </div>

                </>
              )
              :
              (
                <div
                  className="
                    p-10
                    text-sm
                    text-white/35
                  "
                >

                  No model promotion has been recorded yet.

                </div>
              )
          }

        </section>



        {/* ================================================= */}
        {/* LATEST AUTONOMOUS SELF-HEALING CHECK */}
        {/* ================================================= */}

        <SelfHealingStatusPanel />



        {/* ================================================= */}
        {/* PERFORMANCE COMPARISON */}
        {/* ================================================= */}

        <section
          className="
            mt-6
            grid
            gap-6
            xl:grid-cols-[1.4fr_0.6fr]
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

            <p
              className="
                text-[10px]
                uppercase
                tracking-[0.28em]
                text-white/30
              "
            >

              Current Model

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


            <div
              className="
                mt-10
                space-y-8
              "
            >

              <MetricComparison
                label="Accuracy"
                baseline={
                  performance
                    .reference
                    .accuracy
                }
                production={
                  performance
                    .production
                    .accuracy
                }
              />


              <MetricComparison
                label="Precision"
                baseline={
                  performance
                    .reference
                    .precision
                }
                production={
                  performance
                    .production
                    .precision
                }
              />


              <MetricComparison
                label="Recall"
                baseline={
                  performance
                    .reference
                    .recall
                }
                production={
                  performance
                    .production
                    .recall
                }
              />


              <MetricComparison
                label="F1 Score"
                baseline={
                  performance
                    .reference
                    .f1
                }
                production={
                  performance
                    .production
                    .f1
                }
              />

            </div>


            <Link
              href="/performance"
              className="
                mt-9
                inline-flex
                items-center
                gap-2
                text-sm
                text-white/45
                transition
                hover:text-white
              "
            >

              Explore performance

              <ArrowRight size={15} />

            </Link>

          </div>



          {/* DATA QUALITY */}

          <div
            className="
              rounded-[30px]
              bg-[#f1efe8]
              p-7
              text-black
              md:p-10
            "
          >

            <ShieldCheck
              size={22}
              className="
                text-black/35
              "
            />


            <p
              className="
                mt-8
                text-[10px]
                uppercase
                tracking-[0.28em]
                text-black/35
              "
            >

              Data Quality

            </p>


            <p
              className="
                mt-3
                text-6xl
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
                text-black/40
              "
            >

              quality score / 100

            </p>


            <div
              className="
                mt-10
                border-t
                border-black/10
                pt-6
              "
            >

              <SmallMetric
                label="Status"
                value={
                  report
                    .data_quality
                    .status
                }
              />


              <SmallMetric
                label="Duplicates"
                value={
                  String(
                    report
                      .data_quality
                      .duplicates
                  )
                }
              />

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

            <p
              className="
                text-[10px]
                uppercase
                tracking-[0.28em]
                text-white/30
              "
            >

              Drift Breakdown

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
                inline-flex
                items-center
                gap-2
                text-sm
                text-white/45
                transition
                hover:text-white
              "
            >

              View drift analysis

              <ArrowRight size={15} />

            </Link>

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

            <p
              className="
                text-[10px]
                uppercase
                tracking-[0.28em]
                text-white/30
              "
            >

              Highest Priority Signal

            </p>


            {
              topRootCause
                ?
                (
                  <>

                    <p
                      className="
                        mt-8
                        break-all
                        font-mono
                        text-2xl
                      "
                    >

                      {
                        topRootCause.feature
                      }

                    </p>


                    <div
                      className="
                        mt-8
                        grid
                        grid-cols-2
                        gap-3
                      "
                    >

                      <SmallDarkMetric
                        label="Root-Cause Score"
                        value={
                          topRootCause
                            .root_cause_score
                            .toFixed(2)
                        }
                      />


                      <SmallDarkMetric
                        label="Model Importance"
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
                        inline-flex
                        items-center
                        gap-2
                        text-sm
                        text-white/45
                        transition
                        hover:text-white
                      "
                    >

                      Investigate root cause

                      <ArrowRight size={15} />

                    </Link>

                  </>
                )
                :
                (
                  <p
                    className="
                      mt-8
                      text-sm
                      text-white/35
                    "
                  >

                    No root-cause candidates available.

                  </p>
                )
            }

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

            Reliability Recommendation

          </p>


          <p
            className="
              mt-6
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
// STATUS CARD
// =========================================================

function StatusCard({
  href,
  icon,
  title,
  status,
  value,
}: {
  href: string;
  icon: ReactNode;
  title: string;
  status: ReliabilityStatus;
  value: string;
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
        hover:border-white/20
        hover:bg-white/[0.045]
      "
    >

      <div
        className="
          flex
          items-start
          justify-between
          gap-5
        "
      >

        <div
          className="
            text-white/35
            transition
            group-hover:text-white
          "
        >

          {icon}

        </div>


        <StatusDot
          status={status}
        />

      </div>


      <p
        className="
          mt-10
          text-xs
          uppercase
          tracking-[0.18em]
          text-white/30
        "
      >

        {title}

      </p>


      <p
        className="
          mt-2
          truncate
          text-xl
          font-medium
        "
      >

        {value}

      </p>


      <p
        className="
          mt-2
          text-xs
          text-white/30
        "
      >

        {status}

      </p>

    </Link>
  );
}


// =========================================================
// STATUS DOT
// =========================================================

function StatusDot({
  status,
}: {
  status: ReliabilityStatus;
}) {

  const style =
    status === "CRITICAL"
      ?
      "bg-red-400 shadow-[0_0_20px_rgba(248,113,113,0.6)]"
      :
      status === "WARNING"
        ?
        "bg-amber-300 shadow-[0_0_20px_rgba(252,211,77,0.45)]"
        :
        "bg-emerald-300 shadow-[0_0_20px_rgba(110,231,183,0.45)]";


  return (
    <span
      className={`
        h-2.5
        w-2.5
        rounded-full
        ${style}
      `}
    />
  );
}


// =========================================================
// DEPLOYMENT BADGE
// =========================================================

function DeploymentBadge({
  status,
}: {
  status:
    | "PROMOTED"
    | "ROLLED_BACK"
    | "NOT_DEPLOYED";
}) {

  const promoted =
    status === "PROMOTED";


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
          promoted
            ?
            "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
            :
            "border-amber-400/20 bg-amber-400/10 text-amber-300"
        }
      `}
    >

      {
        promoted
          ?
          <Check size={13} />
          :
          <RotateCcw size={13} />
      }

      {status}

    </span>
  );
}


// =========================================================
// DEPLOYMENT METRIC
// =========================================================

function DeploymentMetric({
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
          tracking-[0.2em]
          text-white/30
        "
      >

        {label}

      </p>


      <p
        className="
          mt-5
          break-words
          text-3xl
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
// IMPROVEMENT
// =========================================================

function ImprovementCard({
  label,
  value,
}: {
  label: string;
  value: string;
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
          text-3xl
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
          tracking-[0.16em]
          text-white/30
        "
      >

        {label}

      </p>

    </div>
  );
}


// =========================================================
// LIFECYCLE
// =========================================================

function LifecycleStep({
  number,
  title,
  description,
  complete = false,
}: {
  number: string;
  title: string;
  description: string;
  complete?: boolean;
}) {

  return (
    <div
      className={`
        rounded-[22px]
        border
        p-6

        ${
          complete
            ?
            "border-emerald-400/20 bg-emerald-400/[0.06]"
            :
            "border-white/10 bg-white/[0.025]"
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

        <span
          className="
            text-xs
            text-white/25
          "
        >

          {number}

        </span>


        {
          complete
          &&
          (
            <ShieldCheck
              size={15}
              className="
                text-emerald-300
              "
            />
          )
        }

      </div>


      <p
        className="
          mt-8
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


function LifecycleArrow() {

  return (
    <div
      className="
        hidden
        justify-center
        text-white/20
        lg:flex
      "
    >

      <ArrowRight
        size={18}
      />

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
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1: number;
  };
  promoted?: boolean;
}) {

  return (
    <div
      className={`
        rounded-[22px]
        border
        p-6

        ${
          promoted
            ?
            "border-emerald-400/20 bg-emerald-400/[0.05]"
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
          gap-5
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
          promoted
          &&
          (
            <span
              className="
                rounded-full
                bg-emerald-400/10
                px-3
                py-1
                text-[10px]
                tracking-[0.12em]
                text-emerald-300
              "
            >

              PROMOTED

            </span>
          )
        }

      </div>


      <div
        className="
          mt-7
          grid
          grid-cols-2
          gap-3
        "
      >

        <EvidenceMetric
          label="Accuracy"
          value={
            formatPercent(
              metrics.accuracy
            )
          }
        />


        <EvidenceMetric
          label="Precision"
          value={
            formatPercent(
              metrics.precision
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


        <EvidenceMetric
          label="F1"
          value={
            formatPercent(
              metrics.f1
            )
          }
        />

      </div>

    </div>
  );
}


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
          mb-3
          flex
          items-end
          justify-between
          gap-5
        "
      >

        <p
          className="
            text-sm
            text-white/50
          "
        >

          {label}

        </p>


        <div
          className="
            flex
            gap-4
            font-mono
            text-xs
          "
        >

          <span
            className="
              text-white/25
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
            bg-white/20
          "
          style={{
            width:
              `${baselineWidth}%`,
          }}
        />

      </div>


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
        rounded-[18px]
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
          text-white/30
        "
      >

        {label}

      </p>

    </div>
  );
}


// =========================================================
// SMALL METRICS
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
        flex
        items-center
        justify-between
        gap-5
        py-2
        text-sm
      "
    >

      <span
        className="
          text-black/40
        "
      >

        {label}

      </span>


      <span
        className="
          font-medium
        "
      >

        {value}

      </span>

    </div>
  );
}


function SmallDarkMetric({
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
  value:
    | number
    | null
    | undefined
) {

  if (
    value === null
    ||
    value === undefined
  ) {

    return "—";

  }


  const points =
    value * 100;


  const prefix =
    points > 0
      ?
      "+"
      :
      "";


  return (
    `${prefix}${points.toFixed(2)} pp`
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
  ).format(
    date
  );
}