"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import ScrollCore from "@/components/three/ScrollCore";

import {
  fetchReliabilityReport,
} from "@/lib/api";

import type {
  ReliabilityReport,
  RootCause,
} from "@/types/reliability";


export default function ScrollExperience() {

  const [
    data,
    setData,
  ] = useState<
    ReliabilityReport | null
  >(null);


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
  // LOAD LIVE BACKEND DATA
  // =====================================================

  useEffect(() => {

    async function loadData() {

      try {

        setLoading(true);

        const report =
          await fetchReliabilityReport();

        setData(
          report
        );

        setError(
          null
        );

      } catch (err) {

        console.error(
          err
        );

        setError(
          "Live reliability data is currently unavailable."
        );

      } finally {

        setLoading(
          false
        );

      }

    }


    loadData();

  }, []);



  // =====================================================
  // DERIVED VALUES
  // =====================================================

  const highestDrift =
    useMemo(
      () => {

        if (
          !data
          ||
          data.data_drift
            .features.length === 0
        ) {

          return null;

        }


        return [
          ...data
            .data_drift
            .features,
        ].sort(
          (
            first,
            second
          ) =>
            second.score
            -
            first.score
        )[0];

      },
      [data]
    );


  const topRootCauses =
    useMemo(
      () => {

        if (!data) {

          return [];

        }


        return data
          .root_causes
          .slice(
            0,
            3
          );

      },
      [data]
    );



  // =====================================================
  // FORMATTING
  // =====================================================

  function percentage(
    value?: number
  ) {

    if (
      value === undefined
      ||
      value === null
    ) {

      return "--";

    }


    return (
      `${(
        value
        *
        100
      ).toFixed(2)}%`
    );

  }



  return (
    <div
      className="
        relative
        bg-[#080808]
      "
    >


      {/* ================================================= */}
      {/* STICKY 3D WORLD */}
      {/* ================================================= */}

      <div
        className="
          sticky
          top-0
          z-0
          h-screen
          w-full
          overflow-hidden
        "
      >

        <ScrollCore />


        <div
          className="
            pointer-events-none
            absolute
            inset-0
            bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.18)_45%,rgba(0,0,0,0.88)_100%)]
          "
        />


        <div
          className="
            grid-background
            pointer-events-none
            absolute
            inset-0
            opacity-[0.06]
          "
        />

      </div>



      {/* ================================================= */}
      {/* STORY CONTENT */}
      {/* ================================================= */}

      <div
        className="
          relative
          z-10
          -mt-[100vh]
        "
      >


        {/* ================================================= */}
        {/* HERO */}
        {/* ================================================= */}

        <section
          id="hero"
          className="
            story-step
            flex
            min-h-screen
            items-center
            justify-center
            px-6
          "
        >

          <div
            className="
              mx-auto
              w-full
              max-w-[1500px]
              text-center
            "
          >

            <div
              className="
                mb-7
                flex
                items-center
                justify-center
                gap-3
              "
            >

              <span
                className="
                  h-2
                  w-2
                  rounded-full
                  bg-white/50
                "
              />


              <p
                className="
                  text-xs
                  font-medium
                  tracking-[0.5em]
                  text-white/45
                "
              >

                ENTERPRISE AI RELIABILITY

              </p>

            </div>


            <h1
              className="
                text-[17vw]
                font-semibold
                uppercase
                leading-[0.72]
                tracking-[-0.08em]
                text-white
                md:text-[10vw]
              "
            >

              TRUST

              <br />

              YOUR AI.

            </h1>


            <p
              className="
                mx-auto
                mt-10
                max-w-xl
                text-base
                leading-7
                text-white/55
                md:text-lg
              "
            >

              Know when your models drift,
              degrade or behave unexpectedly
              before your users do.

            </p>



            {/* LIVE STATUS */}

            <div
              className="
                mt-8
                flex
                justify-center
              "
            >

              {loading && (

                <span
                  className="
                    rounded-full
                    border
                    border-white/15
                    px-5
                    py-2
                    text-xs
                    tracking-[0.18em]
                    text-white/45
                  "
                >

                  CONNECTING TO LIVE MODEL...

                </span>

              )}


              {!loading && data && (

                <span
                  className="
                    rounded-full
                    border
                    border-white/20
                    bg-white/[0.04]
                    px-5
                    py-2
                    text-xs
                    tracking-[0.18em]
                    text-white/65
                    backdrop-blur
                  "
                >

                  LIVE SYSTEM STATUS ·{" "}

                  {data.overall_status}

                </span>

              )}


              {!loading && error && (

                <span
                  className="
                    rounded-full
                    border
                    border-white/15
                    px-5
                    py-2
                    text-xs
                    tracking-[0.14em]
                    text-white/40
                  "
                >

                  OFFLINE DEMO MODE

                </span>

              )}

            </div>


            <div
              className="
                mt-10
              "
            >

              <a
                href="#drift"
                className="
                  inline-flex
                  rounded-full
                  border
                  border-white/25
                  px-7
                  py-3
                  text-sm
                  text-white
                  transition
                  duration-300
                  hover:bg-white
                  hover:text-black
                "
              >

                Explore the system ↓

              </a>

            </div>

          </div>

        </section>



        {/* ================================================= */}
        {/* DATA DRIFT */}
        {/* ================================================= */}

        <section
          id="drift"
          className="
            story-step
            flex
            min-h-screen
            items-center
            px-7
            md:px-16
          "
        >

          <div
            className="
              mx-auto
              w-full
              max-w-[1500px]
            "
          >

            <div
              className="
                max-w-[720px]
              "
            >

              <p
                className="
                  mb-6
                  text-xs
                  tracking-[0.45em]
                  text-white/40
                "
              >

                01 / DATA DRIFT

              </p>


              <h2
                className="
                  text-6xl
                  font-semibold
                  uppercase
                  leading-[0.86]
                  tracking-[-0.06em]
                  text-white
                  md:text-8xl
                  lg:text-9xl
                "
              >

                DATA

                <br />

                CHANGES.

              </h2>


              <p
                className="
                  mt-10
                  max-w-lg
                  text-lg
                  leading-8
                  text-white/50
                "
              >

                Production behavior evolves.
                Your monitoring layer continuously
                compares incoming data against the
                reference distribution used to train
                the model.

              </p>


              <div
                className="
                  mt-12
                  max-w-lg
                  border-l
                  border-white/20
                  pl-6
                "
              >

                <p
                  className="
                    text-sm
                    text-white/35
                  "
                >

                  STRONGEST LIVE DRIFT

                </p>


                <p
                  className="
                    mt-2
                    break-words
                    text-2xl
                    text-white
                  "
                >

                  {highestDrift
                    ?.feature
                    ??
                    "Waiting for model data"}

                </p>


                <p
                  className="
                    mt-2
                    font-mono
                    text-sm
                    text-white/40
                  "
                >

                  Drift score{" "}

                  {highestDrift
                    ?
                    highestDrift
                      .score
                      .toFixed(
                        4
                      )
                    :
                    "--"}

                </p>


                {data && (

                  <p
                    className="
                      mt-4
                      text-xs
                      tracking-[0.18em]
                      text-white/30
                    "
                  >

                    STATUS ·{" "}

                    {
                      data
                        .data_drift
                        .status
                    }

                  </p>

                )}

              </div>

            </div>

          </div>

        </section>



        {/* ================================================= */}
        {/* MODEL PERFORMANCE */}
        {/* ================================================= */}

        <section
          id="performance"
          className="
            story-step
            flex
            min-h-screen
            items-center
            px-7
            md:px-16
          "
        >

          <div
            className="
              mx-auto
              flex
              w-full
              max-w-[1500px]
              justify-end
            "
          >

            <div
              className="
                max-w-[720px]
                text-right
              "
            >

              <p
                className="
                  mb-6
                  text-xs
                  tracking-[0.45em]
                  text-white/40
                "
              >

                02 / PERFORMANCE

              </p>


              <h2
                className="
                  text-6xl
                  font-semibold
                  uppercase
                  leading-[0.86]
                  tracking-[-0.06em]
                  text-white
                  md:text-8xl
                  lg:text-9xl
                "
              >

                MODELS

                <br />

                DEGRADE.

              </h2>


              <p
                className="
                  ml-auto
                  mt-10
                  max-w-lg
                  text-lg
                  leading-8
                  text-white/50
                "
              >

                Accuracy alone can hide failure.
                Precision, recall and F1 are compared
                against the model&apos;s held-out
                baseline.

              </p>


              <div
                className="
                  ml-auto
                  mt-12
                  max-w-sm
                  border-r
                  border-white/20
                  pr-6
                "
              >

                <p
                  className="
                    text-sm
                    text-white/35
                  "
                >

                  PRODUCTION F1

                </p>


                <p
                  className="
                    mt-2
                    text-5xl
                    font-medium
                    text-white
                  "
                >

                  {data
                    ?
                    percentage(
                      data
                        .model_performance
                        .production
                        .f1
                    )
                    :
                    "--"}

                </p>


                <p
                  className="
                    mt-2
                    text-sm
                    text-white/40
                  "
                >

                  Baseline{" "}

                  {data
                    ?
                    percentage(
                      data
                        .model_performance
                        .reference
                        .f1
                    )
                    :
                    "--"}

                </p>


                {data && (

                  <p
                    className="
                      mt-4
                      text-xs
                      tracking-[0.18em]
                      text-white/30
                    "
                  >

                    STATUS ·{" "}

                    {
                      data
                        .model_performance
                        .status
                    }

                  </p>

                )}

              </div>

            </div>

          </div>

        </section>



        {/* ================================================= */}
        {/* ANOMALIES */}
        {/* ================================================= */}

        <section
          id="anomalies"
          className="
            story-step
            flex
            min-h-screen
            items-center
            px-7
            md:px-16
          "
        >

          <div
            className="
              mx-auto
              w-full
              max-w-[1500px]
            "
          >

            <div
              className="
                max-w-[720px]
              "
            >

              <p
                className="
                  mb-6
                  text-xs
                  tracking-[0.45em]
                  text-white/40
                "
              >

                03 / ANOMALIES

              </p>


              <h2
                className="
                  text-6xl
                  font-semibold
                  uppercase
                  leading-[0.86]
                  tracking-[-0.06em]
                  text-white
                  md:text-8xl
                  lg:text-9xl
                "
              >

                FIND THE

                <br />

                OUTLIERS.

              </h2>


              <p
                className="
                  mt-10
                  max-w-lg
                  text-lg
                  leading-8
                  text-white/50
                "
              >

                Isolation Forest learns expected
                behavior and identifies individual
                production transactions that no longer
                resemble the reference population.

              </p>


              <div
                className="
                  mt-12
                  flex
                  flex-wrap
                  gap-3
                "
              >

                <MetricPill
                  label="ANOMALIES"
                  value={
                    data
                    ?
                    String(
                      data
                        .anomaly_detection
                        .anomaly_count
                    )
                    :
                    "--"
                  }
                />


                <MetricPill
                  label="RATE"
                  value={
                    data
                    ?
                    `${data
                      .anomaly_detection
                      .anomaly_percentage
                      .toFixed(
                        2
                      )}%`
                    :
                    "--"
                  }
                />


                <MetricPill
                  label="STATUS"
                  value={
                    data
                    ?
                    data
                      .anomaly_detection
                      .status
                    :
                    "--"
                  }
                />

              </div>

            </div>

          </div>

        </section>



        {/* ================================================= */}
        {/* ROOT CAUSE */}
        {/* ================================================= */}

        <section
          id="root-cause"
          className="
            story-step
            flex
            min-h-screen
            items-center
            px-7
            md:px-16
          "
        >

          <div
            className="
              mx-auto
              flex
              w-full
              max-w-[1500px]
              justify-end
            "
          >

            <div
              className="
                max-w-[760px]
                text-right
              "
            >

              <p
                className="
                  mb-6
                  text-xs
                  tracking-[0.45em]
                  text-white/40
                "
              >

                04 / ROOT CAUSE

              </p>


              <h2
                className="
                  text-6xl
                  font-semibold
                  uppercase
                  leading-[0.86]
                  tracking-[-0.06em]
                  text-white
                  md:text-8xl
                  lg:text-9xl
                "
              >

                WE FIND

                <br />

                WHY.

              </h2>


              <p
                className="
                  ml-auto
                  mt-10
                  max-w-lg
                  text-lg
                  leading-8
                  text-white/50
                "
              >

                Drift severity is combined with
                feature importance to prioritize the
                production changes most likely to
                affect model reliability.

              </p>


              <div
                className="
                  ml-auto
                  mt-12
                  max-w-md
                  space-y-1
                  text-left
                "
              >

                {topRootCauses.length > 0
                  ?
                  topRootCauses.map(
                    (
                      cause,
                      index
                    ) => (

                      <Cause
                        key={
                          cause.feature
                        }

                        number={
                          String(
                            index + 1
                          ).padStart(
                            2,
                            "0"
                          )
                        }

                        cause={
                          cause
                        }
                      />

                    )
                  )
                  :
                  (
                    <p
                      className="
                        text-sm
                        text-white/35
                      "
                    >

                      Waiting for root-cause analysis...

                    </p>
                  )}

              </div>

            </div>

          </div>

        </section>



        {/* ================================================= */}
        {/* FINAL CTA */}
        {/* ================================================= */}

        <section
          id="dashboard"
          className="
            relative
            flex
            min-h-screen
            items-center
            justify-center
            bg-[#f0eee7]
            px-6
            text-black
          "
        >

          <div
            className="
              max-w-5xl
              text-center
            "
          >

            <p
              className="
                mb-8
                text-xs
                tracking-[0.5em]
                text-black/45
              "
            >

              RELIABILITY INTELLIGENCE

            </p>


            <h2
              className="
                text-6xl
                font-semibold
                uppercase
                leading-[0.84]
                tracking-[-0.07em]
                md:text-8xl
                lg:text-9xl
              "
            >

              SEE WHAT YOUR

              <br />

              MODEL CAN&apos;T.

            </h2>


            <p
              className="
                mx-auto
                mt-10
                max-w-2xl
                text-lg
                leading-8
                text-black/55
              "
            >

              {data
                ?.recommendation
                ??
                "One platform for model drift, performance degradation, anomaly detection and root-cause intelligence."}

            </p>


            <div
              className="
                mt-12
                flex
                flex-wrap
                justify-center
                gap-4
              "
            >

              <a
                href="http://localhost:8501"
                target="_blank"
                rel="noreferrer"
                className="
                  rounded-full
                  bg-black
                  px-8
                  py-4
                  text-sm
                  font-medium
                  text-white
                  transition
                  duration-300
                  hover:scale-105
                "
              >

                Open Live Dashboard

              </a>


              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="
                  rounded-full
                  border
                  border-black/25
                  px-8
                  py-4
                  text-sm
                  font-medium
                  transition
                  duration-300
                  hover:bg-black
                  hover:text-white
                "
              >

                Explore API

              </a>

            </div>

          </div>

        </section>

      </div>

    </div>
  );
}



// =========================================================
// ROOT CAUSE ROW
// =========================================================

function Cause({
  number,
  cause,
}: {
  number: string;

  cause: RootCause;
}) {

  return (
    <div
      className="
        grid
        grid-cols-[40px_1fr_auto]
        items-center
        gap-4
        border-b
        border-white/15
        py-4
      "
    >

      <span
        className="
          text-xs
          text-white/30
        "
      >

        {number}

      </span>


      <span
        className="
          break-all
          font-mono
          text-sm
          text-white/75
        "
      >

        {cause.feature}

      </span>


      <span
        className="
          text-xs
          tracking-wider
          text-white/35
        "
      >

        {cause.root_cause_priority}

      </span>

    </div>
  );
}



// =========================================================
// METRIC PILL
// =========================================================

function MetricPill({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div
      className="
        min-w-[130px]
        rounded-full
        border
        border-white/20
        bg-white/[0.03]
        px-5
        py-3
        backdrop-blur
      "
    >

      <div
        className="
          text-[10px]
          tracking-[0.18em]
          text-white/30
        "
      >

        {label}

      </div>


      <div
        className="
          mt-1
          text-sm
          text-white/75
        "
      >

        {value}

      </div>

    </div>
  );
}