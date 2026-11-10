import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# Configure dashboard
st.set_page_config(
    page_title="Global Vaccination Dashboard",
    page_icon="💉",
    layout="wide"
)

# Dashboard title
st.title("🌍 Global Vaccination & Disease Dashboard")

st.write(
    "Explore vaccination coverage, reported disease cases, "
    "and disease incidence across countries and years."
)

# Load cleaned data
data_path = Path(__file__).parent / "cleaned_data"

@st.cache_data
def load_data():
    return pd.read_csv(
        data_path / "cases_incidence_merged.csv"
    )

df = load_data()

# Load vaccination coverage data
coverage_path = Path(__file__).parent / "datasets" / "coverage-data.xlsx"
@st.cache_data
def load_coverage_data():
    return pd.read_excel(coverage_path)

coverage_df = load_coverage_data()

# Preview vaccination coverage data
st.subheader("💉 Vaccination Coverage Dataset")
st.dataframe(coverage_df.head(5))
# Vaccination coverage visualization
st.subheader("📈 Vaccination Coverage Over Time")

# Select country
coverage_countries = sorted(coverage_df["NAME"].dropna().unique())

coverage_country = st.selectbox(
    "Select Country for Vaccination Coverage",
    coverage_countries
)

# Filter by country
country_coverage = coverage_df[
    coverage_df["NAME"] == coverage_country
].copy()

# Select vaccine
vaccines = sorted(country_coverage["ANTIGEN"].dropna().unique())

coverage_vaccine = st.selectbox(
    "Select Vaccine",
    vaccines
)

# Filter by vaccine
vaccine_data = country_coverage[
    country_coverage["ANTIGEN"] == coverage_vaccine
].copy()

# Use official coverage records
vaccine_data = vaccine_data[
    vaccine_data["COVERAGE_CATEGORY"] == "OFFICIAL"
].copy()

# Prepare numeric data
vaccine_data["YEAR"] = pd.to_numeric(
    vaccine_data["YEAR"], errors="coerce"
)

vaccine_data["COVERAGE"] = pd.to_numeric(
    vaccine_data["COVERAGE"], errors="coerce"
)

vaccine_data = vaccine_data.dropna(
    subset=["YEAR", "COVERAGE"]
)

# Display chart
if not vaccine_data.empty:
    vaccine_data = vaccine_data.sort_values("YEAR")

    st.line_chart(
        vaccine_data,
        x="YEAR",
        y="COVERAGE"
    )
else:
    st.warning(
        "No official vaccination coverage data available for this selection."
    )

# Step 8A: Compare vaccination coverage between countries
st.subheader("🌍 Compare Vaccination Coverage Between Countries")

country_1 = st.selectbox(
    "Select First Country",
    coverage_countries,
    index=0
)

country_2 = st.selectbox(
    "Select Second Country",
    coverage_countries,
    index=1
)

st.write(
    f"Comparing vaccination coverage between {country_1} and {country_2}."
)
# Select a vaccine for country comparison
comparison_vaccines = sorted(
    coverage_df["ANTIGEN"].dropna().unique()
)

comparison_vaccine = st.selectbox(
    "Select Vaccine to Compare",
    comparison_vaccines
)
# Prepare vaccination coverage comparison data
comparison_data = coverage_df[
    (coverage_df["NAME"].isin([country_1, country_2])) &
    (coverage_df["ANTIGEN"] == comparison_vaccine) &
    (coverage_df["COVERAGE_CATEGORY"] == "OFFICIAL")
].copy()

# Convert values to numbers
comparison_data["YEAR"] = pd.to_numeric(
    comparison_data["YEAR"], errors="coerce"
)

comparison_data["COVERAGE"] = pd.to_numeric(
    comparison_data["COVERAGE"], errors="coerce"
)

# Remove missing values
comparison_data = comparison_data.dropna(
    subset=["YEAR", "COVERAGE"]
)
# Display vaccination coverage comparison chart
st.subheader(
    f"📈 {country_1} vs {country_2} — {comparison_vaccine}"
)
st.caption("Vaccination coverage (%) by year")

if (
    country_1 in comparison_data["NAME"].values
    and country_2 in comparison_data["NAME"].values
):
    comparison_chart = comparison_data.pivot_table(
        index="YEAR",
        columns="NAME",
        values="COVERAGE",
        aggfunc="mean"
    )

    st.line_chart(comparison_chart)
else:
    st.warning(
        f"No vaccination coverage comparison available for "
        f"{country_1} and {country_2} "
        f"for vaccine {comparison_vaccine}. "
        f"One or both countries have no available data."
    )
# Compare latest available vaccination coverage
st.subheader("📊 Latest Vaccination Coverage Comparison")

latest_data = comparison_data.dropna(
    subset=["YEAR", "COVERAGE"]
).sort_values("YEAR")
country1_data = latest_data[latest_data["NAME"] == country_1]
country2_data = latest_data[latest_data["NAME"] == country_2]

if country1_data.empty or country2_data.empty:
        st.error(
            f"Vaccination coverage comparison unavailable "
            f"for {comparison_vaccine}."
        )
        if country1_data.empty:
            st.warning(
                f"No vaccination coverage data available for {country_1} "
                f"for vaccine {comparison_vaccine}."
            )

        if country2_data.empty:
            st.warning(
                f"No vaccination coverage data available for {country_2} "
                f"for vaccine {comparison_vaccine}."
            )
else:
        col1, col2 = st.columns(2)

        with col1:
            country1_data = latest_data[
                latest_data["NAME"] == country_1
                ]

            if not country1_data.empty:
                latest1 = country1_data.iloc[-1]
                st.metric(
                    country_1,
                    f"{latest1['COVERAGE']:.1f}%",
                    help=f"Latest available year: {int(latest1['YEAR'])}"
                )
            else:
                st.metric(country_1, "No data")

        with col2:
            country2_data = latest_data[
                latest_data["NAME"] == country_2
                ]

            if not country2_data.empty:
                latest2 = country2_data.iloc[-1]
                st.metric(
                    country_2,
                    f"{latest2['COVERAGE']:.1f}%",
                    help=f"Latest available year: {int(latest2['YEAR'])}"
                )
            else:
                st.metric(country_2, "No data")
    # Calculate vaccination coverage difference
        if not latest_data.empty and not country1_data.empty and not country2_data.empty:
            if latest1["YEAR"] != latest2["YEAR"]:
                 st.warning(
                "These vaccination percentages come from different years. "
                "The difference below is not a same-year comparison."
            )

            if latest1["YEAR"] == latest2["YEAR"]:
                st.info(
                    f"Both countries are being compared using "
                    f"vaccination coverage data from {int(latest1['YEAR'])}."
            )

            difference = latest1["COVERAGE"] - latest2["COVERAGE"]


            st.metric(
                "Vaccination Coverage Difference",
        f"{abs(difference):.1f} percentage points"
        )

            if difference > 0:
                st.success(f"{country_1} has higher coverage than {country_2}.")
            elif difference < 0:
                st.success(f"{country_2} has higher coverage than {country_1}.")
            else:
                st.info("Both countries have equal vaccination coverage.")
# Display basic information
st.subheader("📊 Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", f"{len(df):,}")

with col2:
    st.metric("Countries", df["name"].nunique())

with col3:
    st.metric("Diseases", df["disease"].nunique())

# Preview data

# Interactive filters
st.sidebar.header("🔎 Dashboard Filters")

countries = sorted(df["name"].dropna().unique())
selected_country = st.sidebar.selectbox(
    "Select Country",
    countries
)

country_data = df[df["name"] == selected_country]

diseases = sorted(country_data["disease"].dropna().unique())
selected_disease = st.sidebar.selectbox(
    "Select Disease",
    diseases
)

filtered_data = country_data[
    country_data["disease"] == selected_disease
].copy()

# Convert year to numeric
filtered_data["year"] = pd.to_numeric(
    filtered_data["year"], errors="coerce"
)

filtered_data = filtered_data.sort_values("year")
# Statistics for selected country and disease
st.subheader("📊 Selected Country & Disease Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Selected Country", selected_country)

with col2:
    st.metric("Selected Disease", selected_disease)

with col3:
    st.metric("Available Records", len(filtered_data))

# Disease trends visualization
st.subheader("📈 Reported Disease Cases Over Time")

# Prepare data for visualization
chart_data = filtered_data[["year", "cases"]].copy()

# Convert cases to numeric
chart_data["cases"] = pd.to_numeric(
chart_data["cases"], errors="coerce"
)

# Remove rows with missing values
chart_data = chart_data.dropna(subset=["year", "cases"])

# Group cases by year
chart_data = chart_data.groupby(
"year", as_index=False
)["cases"].sum()

# Display interactive chart
if not chart_data.empty:
    st.line_chart(
        chart_data,
        x="year",
        y="cases",
        use_container_width=True
    )
else:
    st.warning(
        "No reported case data available for this selection."
    )
st.subheader("🔎 Data Preview")
st.dataframe(filtered_data.head(20), use_container_width="strech")
st.subheader("📈 Disease Trends")

st.write(
    f"Showing reported cases for {selected_disease} "
    f"in {selected_country}."
)

chart_data = filtered_data.dropna(
    subset=["year", "cases"]
)

st.line_chart(
    chart_data,
    x="year",
    y="cases"
)

st.subheader("📋 Filtered Records")
st.dataframe(filtered_data, use_container_width="strech")

# Interactive world bubble map
st.divider()
st.subheader("🌍 Global Disease Cases Map")

map_data = df.dropna(
    subset=["code", "cases", "year","disease"]
).copy()

map_data["cases"] = pd.to_numeric(
    map_data["cases"], errors="coerce"
)

map_data["year"] = pd.to_numeric(
    map_data["year"], errors="coerce"
)

map_data = map_data.dropna(
    subset=["cases", "year"]
)
col_disease, col_year, col_location = st.columns(3)
# Disease filter for the map
map_diseases = sorted(map_data["disease"].dropna().unique())

map_disease = (
col_disease.multiselect(
    "Select Disease for World Map",
     map_diseases
))

if map_disease:
    map_data = map_data[
        map_data["disease"].isin(map_disease)
    ]
    # Year filter for the world map

map_years = sorted(map_data["year"].dropna().unique().astype(int))

map_year = col_year.multiselect(
    "Select Year for World Map",
     map_years
)

if map_year:
    map_data = map_data[
        map_data["year"].isin(map_year)
        ]
# Total reported cases by country
# Location filter for the world map
map_locations = sorted(map_data["name"].dropna().unique())

map_location = (
col_location.multiselect(
    "Select Location for World Map",
     map_locations
))

if map_location :
    map_data = map_data[
        map_data["name"] .isin (map_location)
    ]
country_cases = (
    map_data.groupby(["code","disease"], as_index=False)["cases"]
    .sum()
)

country_cases = country_cases[
    country_cases["cases"] > 0
    ]
# Prepare country codes for the geographic map
country_cases["code"] = (
    country_cases["code"].astype(str).str.upper().str.strip()
)
# Interactive world map
disease_colors = {
disease: px.colors.qualitative.Alphabet[i % 26]
for i, disease in enumerate(sorted(country_cases["disease"].dropna().unique()))
}
fig = px.scatter_geo(
country_cases,
locations="code",
locationmode="ISO-3",
size="cases",
color="disease",
color_discrete_map=disease_colors,
hover_name="code",
hover_data={"cases": ":,.0f"},
projection="equirectangular",
title="Reported Disease Cases by Country",
size_max=45
)

fig.update_layout(
height=550,
margin=dict(l=0, r=0, t=50, b=0)
)

st.altair_chart(fig, use_container_width="strech")