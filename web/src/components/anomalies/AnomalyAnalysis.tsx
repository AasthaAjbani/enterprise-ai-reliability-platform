"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import Link from "next/link";

import {
  ArrowLeft,
  Radar,
  RefreshCw,
  Search,
  TriangleAlert,
} from "lucide-react";

import {
  fetchReliabilityReport,
} from "@/lib/api";

import type {
  AnomalyTransaction,
  ReliabilityReport,
} from "@/types/reliability";


export default function AnomalyAnalysis() {

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

  const [
    search,
    setSearch,
  ] = useState("");


  // =====================================================
  // FETCH LIVE DATA
  // =====================================================

  async function loadReport() {

    try {

      setLoading(true);
      setError(null);

      const data =
        await fetchReliabilityReport();

      setReport(data);

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load anomaly detection data."
      );

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {
    loadReport();
  }, []);


  // =====================================================
  // FILTER TOP ANOMALIES
  // =====================================================

  const anomalies =
    useMemo(() => {

      if (!report) {
        return [];
      }

      const rows =
        report
          .anomaly_detection
          .top_anomalies ?? [];


      if (!search.trim()) {
        return rows;
      }


      const query =
        search.toLowerCase();


      return rows.filter(
        (row) => {

          const searchable =
            [
              row.transaction_id,
              row.payment_method,
              row.device_type,
              row.customer_location,
              row.transaction_amount,
            ]
              .filter(
                (value) =>
                  value !== undefined
                  &&
                  value !== null
              )
              .join(" ")
              .toLowerCase();


          return searchable.includes(
            query
          );

        }
      );

    }, [
      report,
      search,
    ]);


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

          DETECTING ANOMALIES

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

            Anomaly data unavailable

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


  const anomalyData =
    report.anomaly_detection;


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


        {/* TOP */}

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



        {/* HERO */}

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

              <Radar
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

                Behavioral Monitoring

              </p>

            </div>


            <h1
              className="
                text-6xl
                font-semibold
                uppercase
                leading-[0.84]
                tracking-[-0.065em]
                md:text-8xl
                lg:text-9xl
              "
            >

              Find the
              <br />
              Outliers.

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

              Isolation Forest learns expected transaction
              behavior from reference data and identifies
              production records that deviate significantly
              from those patterns.

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
                tracking-[0.28em]
                text-white/30
              "
            >

              Anomaly Status

            </p>


            <p
              className="
                mt-5
                text-4xl
                font-medium
              "
            >

              {anomalyData.status}

            </p>


            <p
              className="
                mt-4
                text-sm
                leading-6
                text-white/40
              "
            >

              Unusual transactions are identified
              independently from the fraud classifier.

            </p>

          </div>

        </section>



        {/* SUMMARY */}

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
            label="Transactions"
            value={
              formatInteger(
                anomalyData.total_transactions
              )
            }
          />


          <SummaryCard
            label="Anomalies Detected"
            value={
              formatInteger(
                anomalyData.anomaly_count
              )
            }
          />


          <SummaryCard
            label="Anomaly Rate"
            value={
              `${anomalyData
                .anomaly_percentage
                .toFixed(2)}%`
            }
          />


          <SummaryCard
            label="Detector"
            value="Isolation Forest"
            small
          />

        </section>



        {/* FEATURED RATE */}

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

            Production anomaly rate

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

              <p
                className="
                  text-7xl
                  font-semibold
                  tracking-[-0.07em]
                  md:text-8xl
                "
              >

                {
                  anomalyData
                    .anomaly_percentage
                    .toFixed(2)
                }%

              </p>


              <p
                className="
                  mt-5
                  max-w-xl
                  text-sm
                  leading-7
                  text-black/50
                "
              >

                {
                  anomalyData.anomaly_count
                } out of{" "}

                {
                  anomalyData.total_transactions
                } production transactions were flagged
                as unusual by the anomaly detector.

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

                System state

              </p>


              <p
                className="
                  mt-2
                  text-3xl
                  font-medium
                "
              >

                {anomalyData.status}

              </p>

            </div>

          </div>

        </section>



        {/* EXPLANATION */}

        <section
          className="
            mt-6
            grid
            gap-6
            lg:grid-cols-2
          "
        >

          <InfoCard
            number="01"
            title="Anomaly ≠ Fraud"
            description="
              An anomaly means a transaction looks unusual
              compared with normal behavior. It does not
              automatically mean that the transaction is
              fraudulent.
            "
          />


          <InfoCard
            number="02"
            title="Anomaly ≠ Drift"
            description="
              Drift describes a change across an overall
              population. Anomaly detection evaluates
              individual records for unusual behavior.
            "
          />

        </section>



        {/* TABLE */}

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
              flex
              flex-wrap
              items-end
              justify-between
              gap-6
              border-b
              border-white/10
              p-7
              md:p-10
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

                Investigation Queue

              </p>


              <h2
                className="
                  mt-2
                  text-2xl
                  font-medium
                "
              >

                Most unusual transactions

              </h2>

            </div>


            <div
              className="
                flex
                items-center
                gap-3
                rounded-full
                border
                border-white/10
                bg-white/[0.02]
                px-4
                py-2.5
              "
            >

              <Search
                size={14}
                className="
                  text-white/30
                "
              />


              <input
                value={search}
                onChange={
                  (
                    event
                  ) =>
                    setSearch(
                      event.target.value
                    )
                }
                placeholder="Search transactions"
                className="
                  w-44
                  bg-transparent
                  text-sm
                  text-white
                  outline-none
                  placeholder:text-white/25
                "
              />

            </div>

          </div>


          <div
            className="
              overflow-x-auto
            "
          >

            <table
              className="
                w-full
                min-w-[1200px]
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
                    Transaction
                  </th>

                  <th className="px-7 py-5">
                    Amount
                  </th>

                  <th className="px-7 py-5">
                    Hour
                  </th>

                  <th className="px-7 py-5">
                    Account Age
                  </th>

                  <th className="px-7 py-5">
                    Failed / 24h
                  </th>

                  <th className="px-7 py-5">
                    International
                  </th>

                  <th className="px-7 py-5">
                    Anomaly Score
                  </th>

                </tr>

              </thead>


              <tbody>

                {
                  anomalies.map(
                    (
                      anomaly,
                      index
                    ) => (

                      <AnomalyRow
                        key={
                          `${anomaly.transaction_id}-${index}`
                        }
                        anomaly={
                          anomaly
                        }
                      />

                    )
                  )
                }

              </tbody>

            </table>

          </div>


          {
            anomalies.length === 0
            &&
            (
              <div
                className="
                  p-10
                  text-center
                  text-sm
                  text-white/35
                "
              >

                No matching transactions found.

              </div>
            )
          }

        </section>



        {/* MODEL DETAILS */}

        <section
          className="
            mt-6
            rounded-[30px]
            border
            border-white/10
            p-8
            md:p-10
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

            Detection Method

          </p>


          <h2
            className="
              mt-3
              text-3xl
              font-medium
            "
          >

            Isolation Forest

          </h2>


          <p
            className="
              mt-5
              max-w-3xl
              text-sm
              leading-7
              text-white/40
            "
          >

            The detector was trained on reference
            numerical behavior and uses isolation
            paths to identify records that are easier
            to separate from normal observations.
            Lower anomaly scores represent more
            unusual transactions in this implementation.

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
  small = false,
}: {
  label: string;
  value: string;
  small?: boolean;
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
        className={
          small
            ?
            "text-xl font-medium"
            :
            "text-4xl font-medium tracking-[-0.04em]"
        }
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
// INFO
// =========================================================

function InfoCard({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {

  return (
    <div
      className="
        rounded-[28px]
        border
        border-white/10
        bg-white/[0.02]
        p-7
        md:p-9
      "
    >

      <p
        className="
          text-xs
          text-white/25
        "
      >

        {number}

      </p>


      <h3
        className="
          mt-8
          text-2xl
          font-medium
        "
      >

        {title}

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
// TABLE ROW
// =========================================================

function AnomalyRow({
  anomaly,
}: {
  anomaly: AnomalyTransaction;
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
          font-mono
          text-sm
        "
      >

        {anomaly.transaction_id}

      </td>


      <td
        className="
          px-7
          py-6
          font-mono
          text-sm
          text-white/70
        "
      >

        ₹{
          formatAmount(
            anomaly.transaction_amount
          )
        }

      </td>


      <td
        className="
          px-7
          py-6
          text-sm
          text-white/45
        "
      >

        {
          anomaly.transaction_hour
        }:00

      </td>


      <td
        className="
          px-7
          py-6
          text-sm
          text-white/45
        "
      >

        {
          anomaly.account_age_days
        } days

      </td>


      <td
        className="
          px-7
          py-6
          text-sm
          text-white/45
        "
      >

        {
          anomaly
            .failed_transactions_last_24h
        }

      </td>


      <td
        className="
          px-7
          py-6
          text-sm
          text-white/45
        "
      >

        {
          anomaly.is_international
          === 1
            ?
            "Yes"
            :
            "No"
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
          anomaly
            .anomaly_score
            .toFixed(4)
        }

      </td>

    </tr>
  );
}


// =========================================================
// FORMATTERS
// =========================================================

function formatInteger(
  value: number
) {

  return new Intl.NumberFormat(
    "en-US"
  ).format(
    value
  );

}


function formatAmount(
  value: number
) {

  return new Intl.NumberFormat(
    "en-IN",
    {
      maximumFractionDigits: 2,
    }
  ).format(
    value
  );

}