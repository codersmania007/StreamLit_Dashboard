import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

try:
    from streamlit_extras.metric_cards import style_metric_cards
    EXTRAS_AVAILABLE = True
except ImportError:
    EXTRAS_AVAILABLE = False

# ---------------------------- Page configuration ----------------------------
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------- Styling ----------------------------
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #f7f9fc 0%, #eef3fb 100%); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101c3a 0%, #172c53 100%);
    }
    [data-testid="stSidebar"] * { color: #f5f7ff; }
    .hero {
        padding: 1.5rem 1.8rem; border-radius: 22px; color: white;
        background: linear-gradient(110deg, #243b80 0%, #5b6ee1 55%, #8b5cf6 100%);
        box-shadow: 0 12px 32px rgba(39, 58, 130, .18); margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; font-size: 2.1rem; }
    .hero p { margin: .4rem 0 0 0; opacity: .9; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e4e9f3; padding: 16px 18px;
        border-radius: 16px; box-shadow: 0 5px 18px rgba(26, 43, 77, .05);
    }
    .block-container { padding-top: 1.8rem; padding-bottom: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
sns.set_theme(style="whitegrid", palette="muted")


# ---------------------------- Dummy dataset ----------------------------
@st.cache_data
def create_dummy_students(n=100, seed=42):
    """Create a reproducible dummy dataset with 100 student records."""
    rng = np.random.default_rng(seed)
    first_names = np.array([
        "Ali", "Ahmed", "Ayesha", "Fatima", "Hassan", "Usman", "Zainab",
        "Hamza", "Sara", "Bilal", "Hira", "Umar", "Maryam", "Saad",
        "Noor", "Ibrahim", "Laiba", "Daniyal", "Mariam", "Huzaifa"
    ])
    last_names = np.array([
        "Khan", "Malik", "Ahmed", "Shah", "Raza", "Iqbal", "Hussain",
        "Butt", "Sheikh", "Qureshi"
    ])
    names = [
        f"{rng.choice(first_names)} {rng.choice(last_names)}"
        for _ in range(n)
    ]
    ages = rng.integers(18, 31, size=n)
    genders = rng.choice(["Male", "Female"], size=n, p=[0.55, 0.45])

    # Simulate subject marks on a 0-100 scale.
    ability = rng.normal(0, 10, size=n)
    ml = np.clip(rng.normal(70, 13, size=n) + ability, 0, 100).round().astype(int)
    dl = np.clip(rng.normal(68, 14, size=n) + ability, 0, 100).round().astype(int)
    nlp = np.clip(rng.normal(72, 12, size=n) + ability, 0, 100).round().astype(int)
    eda = np.clip(rng.normal(75, 11, size=n) + ability, 0, 100).round().astype(int)

    df = pd.DataFrame({
        "Student ID": [f"STU{i:03d}" for i in range(1, n + 1)],
        "Name": names,
        "Age": ages,
        "Gender": genders,
        "Machine Learning": ml,
        "Deep Learning": dl,
        "NLP": nlp,
        "EDA": eda,
    })
    subject_cols = ["Machine Learning", "Deep Learning", "NLP", "EDA"]
    df["Average Marks"] = df[subject_cols].mean(axis=1).round(1)
    df["Total Marks"] = df[subject_cols].sum(axis=1)
    df["Result"] = np.where(df["Average Marks"] >= 50, "Pass", "Needs Improvement")

    # Add a small amount of missing data for demonstrating data-quality charts.
    for col in ["Age", "NLP"]:
        missing_indices = rng.choice(df.index, size=2, replace=False)
        df.loc[missing_indices, col] = np.nan
    return df


def show_hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


df = create_dummy_students()
subject_cols = ["Machine Learning", "Deep Learning", "NLP", "EDA"]
score_cols = subject_cols + ["Average Marks", "Total Marks"]

# ---------------------------- Sidebar navigation ----------------------------
with st.sidebar:
    st.markdown("## 🎓 Student Analytics")
    st.caption("Dummy dataset · 100 student records")
    page = option_menu(
        "NAVIGATION",
        ["Overview", "Student Records", "Subject Analysis", "Relationships", "Data Quality"],
        icons=["speedometer2", "people", "bar-chart-line", "diagram-3", "clipboard-check"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#aebcff", "font-size": "16px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "4px", "--hover-color": "#293f70"},
            "nav-link-selected": {"background-color": "#5268d8", "font-weight": "600"},
        },
    )
    st.markdown("---")
    st.markdown("### 🔎 Filters")
    gender_options = sorted(df["Gender"].dropna().unique().tolist())
    selected_genders = st.multiselect("Gender", gender_options, default=gender_options)
    age_values = df["Age"].dropna()
    min_age, max_age = int(age_values.min()), int(age_values.max())
    selected_age = st.slider("Age range", min_age, max_age, (min_age, max_age))
    selected_result = st.multiselect(
        "Result",
        ["Pass", "Needs Improvement"],
        default=["Pass", "Needs Improvement"],
    )

filtered = df[
    df["Gender"].isin(selected_genders)
    & df["Age"].between(selected_age[0], selected_age[1])
    & df["Result"].isin(selected_result)
].copy()

# ---------------------------- Pages ----------------------------
if page == "Overview":
    show_hero("Student Performance Dashboard 📚", "Explore marks, compare subjects, and discover patterns across a dummy student dataset.")
    st.caption(f"Showing **{len(filtered)}** of **{len(df)}** students after applying sidebar filters.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", f"{len(filtered):,}")
    c2.metric("Average score", f"{filtered['Average Marks'].mean():.1f}" if not filtered.empty else "—", help="Mean of the four subject scores")
    c3.metric("Highest average", f"{filtered['Average Marks'].max():.1f}" if not filtered.empty else "—")
    pass_rate = (filtered["Result"].eq("Pass").mean() * 100) if not filtered.empty else 0
    c4.metric("Pass rate", f"{pass_rate:.1f}%")
    if EXTRAS_AVAILABLE:
        try:
            style_metric_cards(background_color="#ffffff", border_color="#e4e9f3", border_radius_px=16)
        except Exception:
            pass

    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("📊 Average marks by subject")
        subject_means = filtered[subject_cols].mean().rename_axis("Subject").reset_index(name="Average Marks")
        fig = px.bar(
            subject_means, x="Subject", y="Average Marks", color="Subject",
            text_auto=".1f", template="plotly_white",
            title="Class average across subjects",
        )
        fig.update_yaxes(range=[0, 100], title="Marks (out of 100)")
        fig.update_layout(showlegend=False, height=370, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("👥 Students by gender")
        gender_counts = filtered["Gender"].value_counts().rename_axis("Gender").reset_index(name="Students")
        fig = px.pie(gender_counts, names="Gender", values="Students", hole=.55, template="plotly_white")
        fig.update_layout(height=370, margin=dict(l=10, r=10, t=25, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Average score distribution")
    fig = px.histogram(filtered, x="Average Marks", nbins=15, color="Gender",
                       marginal="box", template="plotly_white")
    fig.update_layout(height=350, title="Distribution of student average marks")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⭐ Top 10 students")
    top_students = filtered.nlargest(10, "Average Marks")[["Student ID", "Name", "Gender", "Average Marks", "Result"]]
    st.dataframe(top_students, use_container_width=True, hide_index=True)

elif page == "Student Records":
    show_hero("Student Records 🧑‍🎓", "View, search, and download the generated dummy student data.")
    search = st.text_input("Search by student name or ID", placeholder="e.g. Ali or STU025")
    records = filtered.copy()
    if search:
        mask = records["Name"].str.contains(search, case=False, na=False) | records["Student ID"].str.contains(search, case=False, na=False)
        records = records[mask]
    st.write(f"**{len(records)} records**")
    st.dataframe(records, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered records (CSV)",
        data=records.to_csv(index=False).encode("utf-8"),
        file_name="dummy_student_records.csv",
        mime="text/csv",
    )
    with st.expander("Show the complete dummy dataset"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download all 100 student records",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="all_dummy_student_records.csv",
            mime="text/csv",
            key="download_all",
        )

elif page == "Subject Analysis":
    show_hero("Subject Analysis 📊", "Compare student marks across subjects using interactive visualizations.")
    chart_choice = st.selectbox(
        "Choose visualization",
        ["Grouped bar chart", "Subject box plot", "Subject score histogram", "Pass vs improvement"],
    )
    if chart_choice == "Grouped bar chart":
        long_df = filtered.melt(
            id_vars=["Student ID", "Name", "Gender"],
            value_vars=subject_cols,
            var_name="Subject",
            value_name="Marks",
        )
        fig = px.box(long_df, x="Subject", y="Marks", color="Subject", points="outliers",
                     template="plotly_white", title="Marks spread by subject")
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("The box shows the middle 50% of marks; the line inside each box is the median.")
    elif chart_choice == "Subject box plot":
        long_df = filtered.melt(id_vars=["Gender"], value_vars=subject_cols, var_name="Subject", value_name="Marks")
        fig = px.box(long_df, x="Subject", y="Marks", color="Gender", points="all", template="plotly_white")
        fig.update_layout(height=450, title="Subject scores by gender")
        st.plotly_chart(fig, use_container_width=True)
    elif chart_choice == "Subject score histogram":
        selected_subject = st.selectbox("Subject", subject_cols)
        fig = px.histogram(filtered, x=selected_subject, color="Gender", nbins=15,
                           marginal="rug", template="plotly_white", title=f"{selected_subject} score distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        result_counts = filtered["Result"].value_counts().rename_axis("Result").reset_index(name="Students")
        fig = px.bar(result_counts, x="Result", y="Students", color="Result", text="Students", template="plotly_white")
        fig.update_layout(title="Student results", height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Subject summary statistics")
    st.dataframe(filtered[subject_cols].describe().T, use_container_width=True)

elif page == "Relationships":
    show_hero("Relationships & Correlations 🔗", "Explore relationships between marks in different subjects.")
    corr = filtered[subject_cols + ["Age", "Average Marks"]].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, linewidths=.5, ax=ax)
    ax.set_title("Correlation heatmap")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.subheader("Compare two subjects")
    x_subject = st.selectbox("X-axis subject", subject_cols, index=0)
    y_options = [s for s in subject_cols if s != x_subject]
    y_subject = st.selectbox("Y-axis subject", y_options, index=0)
    fig = px.scatter(
        filtered, x=x_subject, y=y_subject, color="Gender",
        hover_data=["Name", "Age", "Average Marks"],
        trendline="ols" if len(filtered) > 2 else None,
        template="plotly_white",
        title=f"{y_subject} vs. {x_subject}",
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    x_data, y_data = filtered[x_subject], filtered[y_subject]
    corr_value = x_data.corr(y_data) if x_data.nunique() > 1 and y_data.nunique() > 1 else np.nan
    st.metric("Pearson correlation", f"{corr_value:.3f}" if pd.notna(corr_value) else "Not available")

elif page == "Data Quality":
    show_hero("Data Quality Check 🧹", "Inspect missing values, duplicate records, and score distributions.")
    q1, q2, q3 = st.columns(3)
    q1.metric("Missing cells", f"{int(filtered.isna().sum().sum()):,}")
    q2.metric("Duplicate rows", f"{int(filtered.duplicated().sum()):,}")
    q3.metric("Complete rows", f"{int(filtered.notna().all(axis=1).sum()):,}")

    missing = filtered.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    if missing.empty:
        st.success("No missing values in the currently filtered records.")
    else:
        missing_df = missing.rename_axis("Column").reset_index(name="Missing values")
        fig = px.bar(missing_df, x="Column", y="Missing values", color="Column",
                     template="plotly_white", title="Missing values by column")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Score distributions")
    selected_score = st.selectbox("Choose a score column", subject_cols + ["Average Marks"])
    fig, ax = plt.subplots(figsize=(9, 3.5))
    sns.histplot(filtered[selected_score].dropna(), kde=True, ax=ax)
    ax.set_title(f"Distribution of {selected_score}")
    ax.set_xlabel("Marks")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.markdown("---")
st.caption("Student Performance Dashboard · Dummy data generated with NumPy and Pandas")
