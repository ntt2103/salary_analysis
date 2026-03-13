"""
Stack Overflow Developer Survey 2025 — Interactive Dashboard
Run with: streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SO Dev Survey 2025 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS — dark premium look
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Gradient hero header */
    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid #e94560;
    }
    .hero h1 { color: #e94560; font-size: 2rem; font-weight: 700; margin: 0 0 0.3rem 0; }
    .hero p  { color: #a0aec0; font-size: 0.95rem; margin: 0; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="metric-container"] label { color: #a0aec0 !important; }
    [data-testid="metric-container"] [data-testid="metric-value"] { color: #e94560 !important; font-weight: 700; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        background: #16213e;
        border-radius: 8px 8px 0 0;
        color: #a0aec0;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e94560, #c73652) !important;
        color: white !important;
    }

    /* Section headers */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 1.5rem 0 0.8rem 0;
        padding-left: 0.8rem;
        border-left: 4px solid #e94560;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #0f3460; border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Hero header
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>📊 Báo cáo kĩ năng phân tích dữ liệu</h1>
        <p>Interactive salary explorer &amp; career progression dashboard — powered by real survey data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Data loading (cached for performance)
# ─────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Thống nhất tên cột kinh nghiệm làm việc (2024 có thể là WorkExp, 2025 là YearsCodePro)
    if 'WorkExp' in df.columns:
        df = df.rename(columns={'WorkExp': 'YearsCodePro'})

    # Normalise YearsCode and YearsCodePro — coerce any stray strings to float
    if 'YearsCode' in df.columns:
        df["YearsCode"] = pd.to_numeric(df["YearsCode"], errors="coerce")
    if 'YearsCodePro' in df.columns:
        df["YearsCodePro"] = pd.to_numeric(df["YearsCodePro"], errors="coerce")

    # Extract the *first* role when multiple roles are semicolon-separated
    df["DevType_Primary"] = (
        df["DevType"]
        .dropna()
        .str.split(";")
        .str[0]
        .str.strip()
    )
    df["DevType_Primary"] = df["DevType_Primary"].where(df["DevType"].notna(), other=pd.NA)

    # Create seniority Level based on YearsCodePro
    bins   = [-0.01, 2, 5, 9, float("inf")]
    labels = ["Fresher", "Junior", "Senior", "Expert"]
    
    if 'YearsCodePro' in df.columns:
        df["Level"] = pd.cut(df["YearsCodePro"], bins=bins, labels=labels)
    elif 'YearsCode' in df.columns:
        df["Level"] = pd.cut(df["YearsCode"], bins=bins, labels=labels)
    else:
        df["Level"] = pd.NA

    return df

DATA_PATH_2025 = "/home/ntt/cleandata/cleaned_stackoverflow_2025.csv"
DATA_PATH_2024 = "/home/ntt/cleandata/cleaned_stackoverflow_2024.csv"

# Load both datasets
df_2025 = load_data(DATA_PATH_2025)
df_2024 = load_data(DATA_PATH_2024)

# Gộp dữ liệu 2 năm
df = pd.concat([df_2024, df_2025], ignore_index=True)


# ─────────────────────────────────────────────
# Sidebar Filters - Region & Country
# ─────────────────────────────────────────────
st.sidebar.header("Global Filters")

# Map countries to regions
REGION_MAPPING = {
    # North America
    "United States of America": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    
    # Europe
    "United Kingdom of Great Britain and Northern Ireland": "Europe",
    "Germany": "Europe",
    "France": "Europe",
    "Spain": "Europe",
    "Italy": "Europe",
    "Netherlands": "Europe",
    "Poland": "Europe",
    "Sweden": "Europe",
    "Switzerland": "Europe",
    "Ukraine": "Europe",
    "Romania": "Europe",
    "Austria": "Europe",
    "Portugal": "Europe",
    "Czech Republic": "Europe",
    "Belgium": "Europe",
    "Denmark": "Europe",
    "Finland": "Europe",
    "Norway": "Europe",
    "Ireland": "Europe",
    "Greece": "Europe",
    "Hungary": "Europe",
    "Serbia": "Europe",
    "Bulgaria": "Europe",
    "Croatia": "Europe",
    "Lithuania": "Europe",
    "Slovakia": "Europe",
    "Estonia": "Europe",
    "Slovenia": "Europe",
    "Latvia": "Europe",
    "Russian Federation": "Europe", # Often grouped with Europe in these surveys
    
    # Asia
    "India": "Asia",
    "China": "Asia",
    "Japan": "Asia",
    "Indonesia": "Asia",
    "Vietnam": "Asia",
    "Philippines": "Asia",
    "Pakistan": "Asia",
    "Bangladesh": "Asia",
    "Iran, Islamic Republic of...": "Asia",
    "Turkey": "Asia", # Sometimes Europe, often Asia/Middle East
    "Israel": "Asia",
    "Malaysia": "Asia",
    "Singapore": "Asia",
    "Sri Lanka": "Asia",
    "Taiwan": "Asia",
    "Thailand": "Asia",
    "South Korea": "Asia",
    "Nepal": "Asia",
    "United Arab Emirates": "Asia",
    "Saudi Arabia": "Asia",
    "Hong Kong (S.A.R.)": "Asia",
    
    # South America
    "Brazil": "South America",
    "Argentina": "South America",
    "Colombia": "South America",
    "Chile": "South America",
    "Peru": "South America",
    
    # Oceania
    "Australia": "Oceania",
    "New Zealand": "Oceania",
    
    # Africa
    "South Africa": "Africa",
    "Nigeria": "Africa",
    "Egypt": "Africa",
    "Kenya": "Africa",
    "Morocco": "Africa"
}

# Add region column to dataframe
df['Region'] = df['Country'].map(lambda x: REGION_MAPPING.get(x, "Other"))

# 1. Region Selection
region_list = ["All Regions"] + sorted(df["Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", region_list)

# 2. Country Selection (filtered by region)
if selected_region != "All Regions":
    available_countries = sorted(df[df["Region"] == selected_region]["Country"].dropna().unique().tolist())
else:
    available_countries = sorted(df["Country"].dropna().unique().tolist())

country_list = ["All Countries"] + available_countries
selected_country = st.sidebar.selectbox("Select Country", country_list)

# Filter dataframe based on selections
df_filtered = df.copy()

if selected_region != "All Regions":
    df_filtered = df_filtered[df_filtered["Region"] == selected_region]

if selected_country != "All Countries":
    df_filtered = df_filtered[df_filtered["Country"] == selected_country]

# ─────────────────────────────────────────────
# Top-level KPI metrics
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Respondents",  f"{len(df_filtered):,}")
col2.metric("With Salary Data",   f"{df_filtered['SalaryUSD'].notna().sum():,}")
col3.metric("Unique Dev Roles",   f"{df_filtered['DevType_Primary'].nunique():,}")

# Dynamic label for the 4th metric
if selected_country != "All Countries":
    loc_label = "Country"
    loc_val = selected_country
elif selected_region != "All Regions":
    loc_label = "Region"
    loc_val = selected_region
else:
    loc_label = "Countries Covered"
    loc_val = f"{df_filtered['Country'].nunique():,}"
    
col4.metric(loc_label, loc_val)

st.divider()

if len(df_filtered) == 0:
    st.warning("No data available for the selected filters.")
    st.stop()

# ─────────────────────────────────────────────
# Main tabs
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["💰 Salary Explorer", "🚀 Career Progression"])

# ══════════════════════════════════════════════
# TAB 1 — IT Salary Analysis by Role
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-title">Salary Distribution by Developer Role</p>', unsafe_allow_html=True)
    
    if selected_country != "All Countries":
        st.caption(f"Showing salary data for **{selected_country}**.")
    elif selected_region != "All Regions":
        st.caption(f"Showing aggregated salary data for the **{selected_region}** region.")

    # Drop rows with no salary for this tab's calculations only
    df_salary = df_filtered.dropna(subset=["SalaryUSD", "DevType_Primary"]).copy()

    if len(df_salary) == 0:
        st.info("No salary data available for the selected country.")
    else:
        # Aggregate salary statistics per primary DevType
        salary_stats = (
            df_salary
            .groupby("DevType_Primary")["SalaryUSD"]
            .agg(
                Count="count",
                Mean="mean",
                Std="std",
                Median=lambda x: x.median(),
                P25=lambda x: x.quantile(0.25),
                P75=lambda x: x.quantile(0.75),
            )
            .reset_index()
        )

        # Select the Top 15 DevTypes by respondent count
        top15 = salary_stats.nlargest(15, "Count").sort_values("Median")

        # Dynamic title for chart
        if selected_country != "All Countries":
            loc_title = f" in {selected_country}"
        elif selected_region != "All Regions":
            loc_title = f" in {selected_region}"
        else:
            loc_title = " (Global)"
            
        # ── Horizontal Bar Chart ──────────────────────────────────────
        fig_bar = px.bar(
            top15,
            x="Median",
            y="DevType_Primary",
            orientation="h",
            text=top15["Median"].apply(lambda v: f"${v:,.0f}" if pd.notna(v) else ""),
            color="Median",
            color_continuous_scale=["#0f3460", "#e94560"],
            labels={"DevType_Primary": "Developer Role", "Median": "Median Salary (USD)"},
            title=f"Median Annual Salary — Top 15 Developer Roles{loc_title}",
        )
        fig_bar.update_traces(textposition="outside", textfont_size=12)
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0d0d1a",
            font=dict(family="Inter", color="#e2e8f0"),
            title_font_size=18,
            coloraxis_showscale=False,
            xaxis=dict(
                title="Median Salary (USD)",
                gridcolor="#1a1a2e",
                tickprefix="$",
                tickformat=",",
            ),
            yaxis=dict(title="", gridcolor="#1a1a2e"),
            margin=dict(l=20, r=60, t=60, b=40),
            height=520,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ── Detailed statistics table ─────────────────────────────────
        st.markdown('<p class="section-title">Detailed Percentile Breakdown</p>', unsafe_allow_html=True)

        # Calculate 95% Confidence Interval for the Mean
        # Margin of Error = Z * (Std / sqrt(N)). For 95% CI, Z ≈ 1.96
        top15["Margin"] = 1.96 * (top15["Std"] / (top15["Count"] ** 0.5))
        top15["CI 95%"] = top15.apply(
            lambda r: f"${r['Mean'] - r['Margin']:,.0f} - ${r['Mean'] + r['Margin']:,.0f}" if pd.notna(r['Margin']) else "N/A",
            axis=1
        )

        display_df = (
            top15[["DevType_Primary", "Count", "Mean", "Std", "P25", "Median", "P75", "CI 95%"]]
            .sort_values("Median", ascending=False)
            .rename(columns={
                "DevType_Primary": "Developer Role",
                "Count": "# Respondents",
                "Mean": "Mean (USD)",
                "Std": "Std Dev (USD)",
                "P25": "25th Pct (USD)",
                "Median": "Median (USD)",
                "P75": "75th Pct (USD)",
                "CI 95%": "95% CI (Mean)",
            })
            .reset_index(drop=True)
        )

        # Format USD columns
        for col in ["Mean (USD)", "Std Dev (USD)", "25th Pct (USD)", "Median (USD)", "75th Pct (USD)"]:
            display_df[col] = display_df[col].apply(lambda v: f"${v:,.0f}" if pd.notna(v) else "N/A")

        st.dataframe(display_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# TAB 2 — Career Progression & Promotion Probability
# ══════════════════════════════════════════════
with tab2:
    # ── Section 1: Median Salary vs YearsCode Line Chart ─────────
    st.markdown('<p class="section-title">Median Salary vs. Years of Experience</p>', unsafe_allow_html=True)
    
    if selected_country != "All Countries":
        st.caption(f"Showing progression data for **{selected_country}**.")
    elif selected_region != "All Regions":
        st.caption(f"Showing aggregated progression data for the **{selected_region}** region.")

    # Sidebar-style controls inside the tab
    ctrl_col, _ = st.columns([1, 3])
    with ctrl_col:
        # Build DevType list for the selectbox (from roles with salary data)
        all_roles = sorted(
            df_filtered.dropna(subset=["DevType_Primary", "SalaryUSD"])["DevType_Primary"].unique()
        )
        role_options = ["All Roles"] + all_roles
        selected_role = st.selectbox(
            "Filter by Developer Role",
            options=role_options,
            index=0,
        )

    # Apply filter and restrict YearsCode to 0–25 to reduce noise
    df_prog = df_filtered.dropna(subset=["YearsCode", "SalaryUSD"]).copy()
    df_prog = df_prog[(df_prog["YearsCode"] >= 0) & (df_prog["YearsCode"] <= 25)]

    if selected_role != "All Roles":
        df_prog = df_prog[df_prog["DevType_Primary"] == selected_role]

    if len(df_prog) == 0:
        st.info("No progression data available for this selection.")
    else:
        # Calculate median salary at each integer YearsCode value
        salary_by_year = (
            df_prog
            .assign(YearsCode=df_prog["YearsCode"].round().astype(int))
            .groupby("YearsCode")["SalaryUSD"]
            .median()
            .reset_index()
            .sort_values("YearsCode")
        )

        # Plot line chart
        fig_line = px.line(
            salary_by_year,
            x="YearsCode",
            y="SalaryUSD",
            markers=True,
            labels={"YearsCode": "Years of Coding Experience", "SalaryUSD": "Median Salary (USD)"},
            title=f"Median Salary vs Years of Experience — {selected_role}",
        )
        fig_line.update_traces(
            line=dict(color="#e94560", width=3),
            marker=dict(size=8, color="#e94560", line=dict(color="white", width=1.5)),
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0d0d1a",
            font=dict(family="Inter", color="#e2e8f0"),
            title_font_size=18,
            xaxis=dict(
                title="Years of Coding Experience",
                gridcolor="#1a1a2e",
                dtick=1,
            ),
            yaxis=dict(
                title="Median Salary (USD)",
                gridcolor="#1a1a2e",
                tickprefix="$",
                tickformat=",",
            ),
            margin=dict(l=20, r=20, t=60, b=40),
            height=420,
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # ── Section 2: Seniority Level Distribution (100% Stacked Bar) ─
    st.markdown('<p class="section-title">Career Seniority Probability by Years of Experience</p>', unsafe_allow_html=True)
    st.caption(
        "Shows the percentage of respondents at each seniority level for a given number of years of experience (0–25). "
        "This approximates the *probability* of reaching a particular seniority milestone."
    )

    # Use filtered dataset (no salary filter needed for level distribution)
    df_level = df_filtered.dropna(subset=["YearsCode", "Level"]).copy()
    if selected_role != "All Roles":
        # It's better to also filter the level distribution if a specific role is selected
        df_level = df_level[df_level["DevType_Primary"] == selected_role]
        
    df_level = df_level[(df_level["YearsCode"] >= 0) & (df_level["YearsCode"] <= 25)]
    
    if len(df_level) == 0:
         st.info("No seniority distribution data available for this selection.")
    else:
        df_level["YearsCode_Int"] = df_level["YearsCode"].round().astype(int)
    
        # Calculate count of each Level at each YearsCode milestone
        level_counts = (
            df_level
            .groupby(["YearsCode_Int", "Level"], observed=True)
            .size()
            .reset_index(name="Count")
        )
    
        # Pivot to wide format so we can compute row-wise percentages
        level_pivot = level_counts.pivot_table(
            index="YearsCode_Int", columns="Level", values="Count", fill_value=0
        )
    
        # Enforce column order (youngest → most experienced levels)
        ordered_levels = ["Fresher", "Junior", "Senior", "Expert"]
        level_pivot = level_pivot.reindex(columns=ordered_levels, fill_value=0)
    
        # Convert raw counts to row-wise percentages (the "probability" approximation)
        level_row_sums = level_pivot.sum(axis=1)
        # Avoid division by zero
        level_pct = level_pivot.div(level_row_sums.replace(0, 1), axis=0) * 100
        level_pct = level_pct.reset_index().melt(
            id_vars="YearsCode_Int", var_name="Level", value_name="Percentage"
        )
    
        # Colour palette aligned with the dashboard theme
        level_colors = {
            "Fresher":   "#4cc9f0",
            "Junior":    "#4361ee",
            "Senior": "#e94560",
            "Expert":    "#f77f00",
        }
    
        fig_stack = px.bar(
            level_pct,
            x="YearsCode_Int",
            y="Percentage",
            color="Level",
            color_discrete_map=level_colors,
            barmode="stack",
            labels={
                "YearsCode_Int": "Years of Coding Experience",
                "Percentage": "Share (%)",
                "Level": "Seniority Level",
            },
            title=f"Seniority Level Distribution by Years of Experience (100% Stacked) - {selected_role}",
            category_orders={"Level": ordered_levels},
        )
        fig_stack.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Year %{x}: %{y:.1f}%<extra></extra>",
        )
        fig_stack.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#0d0d1a",
            font=dict(family="Inter", color="#e2e8f0"),
            title_font_size=18,
            xaxis=dict(
                title="Years of Coding Experience",
                gridcolor="#1a1a2e",
                dtick=1,
            ),
            yaxis=dict(
                title="Share (%)",
                gridcolor="#1a1a2e",
                ticksuffix="%",
                range=[0, 100],
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=80, b=40),
            height=440,
        )
        st.plotly_chart(fig_stack, use_container_width=True)
    
        # ── Insight callout ──────────────────────────────────────────
        st.info(
            "**How to read this chart:** Each bar for a given year adds up to 100%. "
            "The coloured segments show the *proportion* of survey respondents at that experience milestone "
            "who fall into each seniority category — giving an empirical estimate of career progression likelihood.",
            icon="💡",
        )
