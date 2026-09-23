import requests
import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------

API_URL = "http://127.0.0.1:8000/api/reliability"


st.set_page_config(
    page_title="AI Reliability Platform",
    page_icon="🤖",
    layout="wide",
)


# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------

def get_reliability_data():

    try:

        response = requests.get(
            API_URL,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to FastAPI backend. "
            "Make sure the backend is running."
        )

        return None

    except requests.exceptions.RequestException as error:

        st.error(
            f"API Error: {error}"
        )

        return None


def percentage(value):

    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


def status_icon(status):

    if status == "HEALTHY":
        return "✅"

    if status == "WARNING":
        return "⚠️"

    if status == "CRITICAL":
        return "🚨"

    return "❓"


# ---------------------------------------------------------
# 3. TITLE
# ---------------------------------------------------------

st.title(
    "🤖 Enterprise AI Reliability Platform"
)

st.caption(
    "Monitor model performance, data drift, "
    "data quality and root causes."
)


# ---------------------------------------------------------
# 4. REFRESH BUTTON
# ---------------------------------------------------------

if st.button(
    "🔄 Refresh Analysis"
):

    st.rerun()


# ---------------------------------------------------------
# 5. LOAD DATA
# ---------------------------------------------------------

data = get_reliability_data()


if data is None:

    st.stop()


# ---------------------------------------------------------
# 6. OVERALL STATUS
# ---------------------------------------------------------

overall_status = data[
    "overall_status"
]


st.header(
    "System Overview"
)


if overall_status == "HEALTHY":

    st.success(
        "Overall AI System Status: HEALTHY"
    )

elif overall_status == "WARNING":

    st.warning(
        "Overall AI System Status: WARNING"
    )

else:

    st.error(
        "Overall AI System Status: CRITICAL"
    )


# ---------------------------------------------------------
# 7. SYSTEM HEALTH CARDS
# ---------------------------------------------------------

data_quality = data[
    "data_quality"
]

data_drift = data[
    "data_drift"
]

model_performance = data[
    "model_performance"
]


col1, col2, col3 = st.columns(3)


with col1:

    status = data_quality[
        "status"
    ]

    st.metric(
        label=(
            f"{status_icon(status)} "
            "Data Quality"
        ),
        value=status,
    )


with col2:

    status = data_drift[
        "status"
    ]

    st.metric(
        label=(
            f"{status_icon(status)} "
            "Data Drift"
        ),
        value=status,
    )


with col3:

    status = model_performance[
        "status"
    ]

    st.metric(
        label=(
            f"{status_icon(status)} "
            "Model Performance"
        ),
        value=status,
    )


st.divider()


# ---------------------------------------------------------
# 8. MODEL PERFORMANCE
# ---------------------------------------------------------

st.header(
    "📊 Model Performance"
)


baseline = model_performance[
    "reference"
]

production = model_performance[
    "production"
]

performance_drop = model_performance[
    "performance_drop"
]


metric1, metric2, metric3, metric4 = (
    st.columns(4)
)


with metric1:

    st.metric(
        "Accuracy",
        percentage(
            production["accuracy"]
        ),
        delta=(
            f"-{performance_drop['accuracy'] * 100:.2f}%"
        ),
    )


with metric2:

    st.metric(
        "Precision",
        percentage(
            production["precision"]
        ),
        delta=(
            f"-{performance_drop['precision'] * 100:.2f}%"
        ),
    )


with metric3:

    st.metric(
        "Recall",
        percentage(
            production["recall"]
        ),
        delta=(
            f"-{performance_drop['recall'] * 100:.2f}%"
        ),
    )


with metric4:

    st.metric(
        "F1 Score",
        percentage(
            production["f1"]
        ),
        delta=(
            f"-{performance_drop['f1'] * 100:.2f}%"
        ),
    )


# ---------------------------------------------------------
# 9. BASELINE VS PRODUCTION TABLE
# ---------------------------------------------------------

performance_df = pd.DataFrame(
    {
        "Metric": [
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score",
        ],

        "Baseline": [
            baseline[
                "accuracy"
            ],
            baseline[
                "precision"
            ],
            baseline[
                "recall"
            ],
            baseline[
                "f1"
            ],
        ],

        "Production": [
            production[
                "accuracy"
            ],
            production[
                "precision"
            ],
            production[
                "recall"
            ],
            production[
                "f1"
            ],
        ],
    }
)


performance_df[
    "Baseline"
] = (
    performance_df[
        "Baseline"
    ]
    * 100
)


performance_df[
    "Production"
] = (
    performance_df[
        "Production"
    ]
    * 100
)


st.subheader(
    "Baseline vs Production"
)


st.dataframe(
    performance_df,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# 10. PERFORMANCE CHART
# ---------------------------------------------------------

chart_data = (
    performance_df
    .set_index(
        "Metric"
    )[
        [
            "Baseline",
            "Production",
        ]
    ]
)


st.bar_chart(
    chart_data
)


st.divider()


# ---------------------------------------------------------
# 11. DATA DRIFT
# ---------------------------------------------------------

st.header(
    "📈 Data Drift Analysis"
)


drift_features = (
    data_drift[
        "features"
    ]
)


drift_df = pd.DataFrame(
    drift_features
)


if not drift_df.empty:

    display_drift_df = drift_df[
        [
            "feature",
            "feature_type",
            "drift_level",
            "score",
            "p_value",
        ]
    ].copy()


    display_drift_df.columns = [
        "Feature",
        "Type",
        "Drift Level",
        "Drift Score",
        "P-Value",
    ]


    st.dataframe(
        display_drift_df,
        use_container_width=True,
        hide_index=True,
    )


    # ---------------------------------------------
    # DRIFT SUMMARY
    # ---------------------------------------------

    high_count = (
        drift_df[
            "drift_level"
        ]
        == "HIGH"
    ).sum()


    moderate_count = (
        drift_df[
            "drift_level"
        ]
        == "MODERATE"
    ).sum()


    low_count = (
        drift_df[
            "drift_level"
        ]
        == "LOW"
    ).sum()


    drift_col1, drift_col2, drift_col3 = (
        st.columns(3)
    )


    with drift_col1:

        st.metric(
            "High Drift Features",
            int(
                high_count
            ),
        )


    with drift_col2:

        st.metric(
            "Moderate Drift Features",
            int(
                moderate_count
            ),
        )


    with drift_col3:

        st.metric(
            "Low Drift Features",
            int(
                low_count
            ),
        )


st.divider()


# ---------------------------------------------------------
# 12. DATA QUALITY
# ---------------------------------------------------------

st.header(
    "🧹 Data Quality"
)


quality_col1, quality_col2 = (
    st.columns(2)
)


with quality_col1:

    st.metric(
        "Quality Score",
        (
            f"{data_quality['score']}/100"
        ),
    )


with quality_col2:

    st.metric(
        "Duplicate Transactions",
        data_quality[
            "duplicates"
        ],
    )


if (
    not data_quality[
        "missing_values"
    ]
    and not data_quality[
        "numerical_issues"
    ]
    and not data_quality[
        "categorical_issues"
    ]
):

    st.success(
        "No major data quality issues detected."
    )

else:

    if data_quality[
        "missing_values"
    ]:

        st.warning(
            "Missing values detected:"
        )

        st.json(
            data_quality[
                "missing_values"
            ]
        )


    if data_quality[
        "numerical_issues"
    ]:

        st.warning(
            "Invalid numerical values detected:"
        )

        st.json(
            data_quality[
                "numerical_issues"
            ]
        )


    if data_quality[
        "categorical_issues"
    ]:

        st.warning(
            "Invalid categorical values detected:"
        )

        st.json(
            data_quality[
                "categorical_issues"
            ]
        )


st.divider()


# ---------------------------------------------------------
# 13. ROOT CAUSE ANALYSIS
# ---------------------------------------------------------

st.header(
    "🔍 Root Cause Analysis"
)


root_causes = data[
    "root_causes"
]


root_cause_df = pd.DataFrame(
    root_causes
)


if not root_cause_df.empty:

    display_root_df = root_cause_df[
        [
            "feature",
            "drift_level",
            "model_importance",
            "root_cause_score",
            "root_cause_priority",
        ]
    ].copy()


    display_root_df.columns = [
        "Feature",
        "Drift Level",
        "Model Importance",
        "Root Cause Score",
        "Priority",
    ]


    st.dataframe(
        display_root_df,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# 14. TOP ROOT CAUSES
# ---------------------------------------------------------

st.subheader(
    "Top Suspected Causes"
)


top_causes = (
    root_cause_df
    .head(3)
)


for index, row in (
    top_causes.iterrows()
):

    priority = row[
        "root_cause_priority"
    ]

    feature = row[
        "feature"
    ]

    score = row[
        "root_cause_score"
    ]


    st.write(
        f"**{index + 1}. {feature}** "
        f"— Priority: `{priority}` "
        f"— Score: `{score:.3f}`"
    )


st.divider()


# ---------------------------------------------------------
# 15. RECOMMENDATION
# ---------------------------------------------------------

st.header(
    "💡 Recommended Action"
)


st.info(
    data[
        "recommendation"
    ]
)


# ---------------------------------------------------------
# 16. FOOTER
# ---------------------------------------------------------

st.divider()


st.caption(
    "Enterprise AI Reliability Platform | "
    "Data Science Final Year Project"
)