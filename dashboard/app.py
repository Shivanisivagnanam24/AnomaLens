import streamlit as st
import pandas as pd
import joblib
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "prediction_dataset.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "random_forest_model.pkl"
)


# --------------------------------------------------
# MODEL FEATURES
# --------------------------------------------------

FEATURES = [
    "normal_count_last_3",
    "warning_count_last_3",
    "error_count_last_3",
    "warning_rate_last_3",
    "error_rate_last_3"
]


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AnomaLens | Kubernetes Monitoring",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --------------------------------------------------
# CUSTOM UI
# --------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #263244;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #9ca3af;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    .anomalens-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .anomalens-subtitle {
        color: #94a3b8;
        font-size: 17px;
        margin-top: 2px;
    }

    .status-online {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background-color: rgba(34, 197, 94, 0.12);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        font-size: 14px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# LOAD DATA AND MODEL
# --------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)


@st.cache_resource
def load_model():
    return joblib.load(MODEL_FILE)


data = load_data()
model = load_model()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

header_left, header_right = st.columns(
    [4, 1]
)

with header_left:

    st.markdown(
        '<div class="anomalens-title">'
        'AnomaLens'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="anomalens-subtitle">'
        'Intelligent Kubernetes Log Analysis '
        'and Failure Prediction'
        '</div>',
        unsafe_allow_html=True
    )


with header_right:

    st.markdown(
        '<div style="text-align:right; padding-top:15px;">'
        '<span class="status-online">'
        '● Monitoring Active'
        '</span>'
        '</div>',
        unsafe_allow_html=True
    )


st.divider()


# --------------------------------------------------
# SYSTEM OVERVIEW
# --------------------------------------------------

total_samples = len(data)

failure_samples = int(
    data["failure_next"].sum()
)

normal_samples = (
    total_samples - failure_samples
)

total_sequences = (
    data["sequence_id"].nunique()
)


st.markdown("### System Overview")


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Experimental Sequences",
    total_sequences,
    help="Controlled Kubernetes workload sequences"
)


col2.metric(
    "Prediction Samples",
    total_samples,
    help="Temporal log windows used for prediction"
)


col3.metric(
    "Normal Windows",
    normal_samples,
    help="Windows not immediately followed by failure"
)


col4.metric(
    "Pre-Failure Windows",
    failure_samples,
    help="Windows immediately preceding simulated failure"
)


st.divider()


# --------------------------------------------------
# MODEL PERFORMANCE
# --------------------------------------------------

st.header("Model Performance")

st.caption(
    "Initial benchmark results from the controlled "
    "Kubernetes failure-prediction experiment."
)


performance_data = pd.DataFrame({
    "Approach": [
        "Rule-Based Threshold",
        "Logistic Regression",
        "Random Forest"
    ],

    "Accuracy": [
        0.8571,
        1.0000,
        1.0000
    ],

    "Precision": [
        0.5000,
        1.0000,
        1.0000
    ],

    "Recall": [
        1.0000,
        1.0000,
        1.0000
    ],

    "F1-Score": [
        0.6667,
        1.0000,
        1.0000
    ]
})


st.dataframe(
    performance_data,
    use_container_width=True,
    hide_index=True
)


st.divider()


# --------------------------------------------------
# FAILURE PREDICTION
# --------------------------------------------------

st.header("Failure Prediction")

st.write(
    "Analyze the latest 3-event Kubernetes log "
    "window using the trained Random Forest model."
)


input_col, result_col = st.columns(
    [1, 1],
    gap="large"
)


with input_col:

    st.subheader("Log Window")

    normal_count = st.number_input(
        "Normal events",
        min_value=0,
        max_value=3,
        value=1,
        step=1
    )

    warning_count = st.number_input(
        "Warning events",
        min_value=0,
        max_value=3,
        value=2,
        step=1
    )

    error_count = st.number_input(
        "Error events",
        min_value=0,
        max_value=3,
        value=0,
        step=1
    )


total_events = (
    normal_count
    + warning_count
    + error_count
)


with result_col:

    st.subheader("Analysis")

    if total_events != 3:

        st.warning(
            "The observation window must contain "
            "exactly 3 log events."
        )

    else:

        warning_rate = (
            warning_count / 3
        )

        error_rate = (
            error_count / 3
        )


        input_data = pd.DataFrame(
            [[
                normal_count,
                warning_count,
                error_count,
                warning_rate,
                error_rate
            ]],
            columns=FEATURES
        )


        if st.button(
            "Analyze Failure Risk",
            type="primary",
            use_container_width=True
        ):

            prediction = model.predict(
                input_data
            )[0]


            probabilities = model.predict_proba(
                input_data
            )[0]


            failure_probability = (
                probabilities[1]
            )


            if prediction == 1:

                st.error(
                    "⚠️ Potential failure "
                    "pattern detected"
                )

            else:

                st.success(
                    "✓ No immediate failure "
                    "pattern detected"
                )


            st.metric(
                "Model Failure Probability",
                f"{failure_probability * 100:.2f}%"
            )


            st.caption(
                "Prediction generated using the "
                "trained Random Forest model."
            )


st.divider()


# --------------------------------------------------
# RECENT DATA
# --------------------------------------------------

st.header("Recent Prediction Windows")

st.caption(
    "Latest temporal windows generated from the "
    "controlled Kubernetes log experiment."
)


display_columns = [
    "sequence_id",
    "window_end_timestamp",
    "normal_count_last_3",
    "warning_count_last_3",
    "failure_next"
]


st.dataframe(
    data[display_columns].tail(10),
    use_container_width=True,
    hide_index=True
)


st.divider()


# --------------------------------------------------
# EXPERIMENT INFORMATION
# --------------------------------------------------

st.header("Experimental Model")


info1, info2, info3, info4 = st.columns(4)


with info1:

    st.markdown("**Primary Model**")

    st.write(
        "Random Forest"
    )


with info2:

    st.markdown("**Observation Window**")

    st.write(
        "3 log events"
    )


with info3:

    st.markdown("**Prediction Target**")

    st.write(
        "Next-event failure"
    )


with info4:

    st.markdown("**Prototype Stage**")

    st.write(
        "Controlled experiment"
    )


st.caption(
    "Current predictions represent patterns learned "
    "from controlled simulated Kubernetes application "
    "failure scenarios."
)   