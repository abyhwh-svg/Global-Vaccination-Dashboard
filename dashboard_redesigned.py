"""Responsive Global Vaccination & Disease Dashboard.
Run: streamlit run dashboard_redesigned.py
Place this file in the same project folder as cleaned_data/ and datasets/.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Global Vaccination & Disease Dashboard", page_icon="🌍", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #030B1B 0%,
        #092444 45%,
        #07172E 75%,
        #03101F 100%
    );
    color: #E6F5FF;
}

h1, h2, h3, p, label {
    color: #E6F5FF !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(9, 39, 73, 0.65);
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""<style>
.block-container {padding-top:1rem;padding-bottom:1rem;max-width:1900px}
h1 {font-size:1.8rem!important;margin-bottom:.2rem!important}
h2,h3 {margin-top:.4rem!important}
[data-testid="stMetric"] {background:rgba(40,110,145,.12);border-radius:10px;padding:9px}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px}
@media(max-width:750px){.block-container{padding:0.6rem 0.6rem 1rem}h1{font-size:1.35rem!important}}
</style>""", unsafe_allow_html=True)
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #030B1B 0%,
        #092444 45%,
        #07172E 75%,
        #03101F 100%
    );
    color: #E6F5FF;
}

h1, h2, h3, p, label {
    color: #E6F5FF !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(9, 39, 73, 0.65);
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.medical-icons {
    display: flex;
    justify-content: space-between;
    margin: 10px 0;
}
.medical-icon {
    font-size: 48px;
    animation: float-icon 3s ease-in-out infinite;
    transition: transform 0.3s;
    cursor: pointer;
}
.medical-icon:hover {
    animation-play-state: paused;
    transform: scale(1.3) rotate(12deg);
}
@keyframes float-icon {
    0%, 100% { translate: 0 0; }
    50% { translate: 0 -10px; }
}
</style>
<div class="medical-icons">
    <span class="medical-icon" title="Vaccination">💉</span>
    <span class="medical-icon" title="Disease Surveillance">🦠</span>
</div>
""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parent
SEARCH_DIRS = [ROOT / "cleaned_data", ROOT / "datasets", ROOT]

@st.cache_data(show_spinner=False)
def load_csv(keyword, preferred=None):
    paths = []
    for folder in SEARCH_DIRS:
        if folder.is_dir():
            paths.extend(folder.glob("*.csv"))
    if preferred:
        exact = [p for p in paths if p.name.lower() == preferred.lower()]
        paths = exact + [p for p in paths if p not in exact]
    for path in paths:
        if keyword in path.name.lower():
            try:
                return pd.read_csv(path, low_memory=False), path.name
            except Exception:
                pass
    return pd.DataFrame(), None

@st.cache_data(show_spinner=False)
def load_excel(keyword):
    for folder in SEARCH_DIRS:
        if folder.is_dir():
            for path in folder.glob("*.xlsx"):
                if keyword in path.name.lower():
                    try:
                        return pd.read_excel(path), path.name
                    except Exception:
                        pass
    return pd.DataFrame(), None

def canonical(df):
    """Normalize source headers without changing original files."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    aliases = {
        "country": "name", "country_name": "name", "entity": "name",
        "iso3": "code", "iso_code": "code", "country_code": "code",
        "disease_name": "disease", "antigen_name": "antigen",
        "reported_cases": "cases", "number_of_cases": "cases",
        "vaccination_coverage": "coverage", "coverage_percent": "coverage",
        "incidence_rate": "incidence", "rate": "incidence",
    }
    for old, new in aliases.items():
        if old in df and new not in df:
            df = df.rename(columns={old:new})
    for col in ("year", "cases", "coverage", "incidence"):
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ("name", "disease", "code", "antigen"):
        if col in df:
            df[col] = df[col].astype("string").str.strip()
    return df

def plot_empty(message):
    st.info(message)

def line_panel(df, x, y, color=None, height=235, title=None):
    if df.empty or x not in df or y not in df:
        plot_empty("No data available for these filters.")
        return
    fig = px.line(df, x=x, y=y, color=color if color in df else None, markers=True, title=title)
    fig.update_layout(height=height, margin=dict(l=4,r=4,t=35 if title else 8,b=8), legend=dict(orientation="h",y=-.25), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

def bar_panel(df, x, y, height=235, horizontal=False):
    if df.empty:
        plot_empty("No matching data.")
        return
    fig = px.bar(df, x=y if horizontal else x, y=x if horizontal else y, orientation="h" if horizontal else "v", color_discrete_sequence=["#56b8d2"])
    fig.update_layout(height=height, margin=dict(l=4,r=4,t=8,b=8), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

cases, cases_source = load_csv("cases_incidence_merged", "cases_incidence_merged.csv")
if cases.empty:
    cases, cases_source = load_csv("reported-cases")
if cases.empty:
    cases, cases_source = load_csv("reported_cases")
coverage, coverage_source = load_csv("coverage")
if coverage.empty:
    coverage, coverage_source = load_excel("coverage")
incidence, incidence_source = load_csv("incidence-rate")
if incidence.empty:
    incidence, incidence_source = load_excel("incidence-rate")
cases, coverage, incidence = canonical(cases), canonical(coverage), canonical(incidence)

st.title("🌍 Global Vaccination & Disease Dashboard")
st.caption("Interactive world view · disease surveillance · vaccination coverage")
if cases.empty:
    st.error("No disease-case CSV found. Put dashboard_redesigned.py beside your cleaned_data folder containing cases_incidence_merged.csv, then refresh.")
    st.stop()
required = {"name", "disease", "year", "cases"}
if not required.issubset(cases.columns):
    st.error(f"Disease file '{cases_source}' needs columns {sorted(required)}. Found: {list(cases.columns)}")
    st.stop()

# Top filters: the only controls above the globe.
f1, f2, f3 = st.columns(3)
all_diseases = sorted(cases["disease"].dropna().unique().tolist())
all_years = sorted(cases["year"].dropna().astype(int).unique().tolist())
all_countries = sorted(cases["name"].dropna().unique().tolist())
with f1:
    chosen_diseases = st.multiselect("Disease", all_diseases, placeholder="All diseases")
with f2:
    chosen_years = st.multiselect("Year", all_years, placeholder="All years")
with f3:
    chosen_countries = st.multiselect("Location", all_countries, placeholder="All locations")
filtered = cases.copy()
if chosen_diseases:
    filtered = filtered[filtered["disease"].isin(chosen_diseases)]
if chosen_years:
    filtered = filtered[filtered["year"].isin(chosen_years)]
if chosen_countries:
    filtered = filtered[filtered["name"].isin(chosen_countries)]
filtered = filtered.copy()
filtered["cases"] = filtered["cases"].fillna(0)

# Responsive layout: Streamlit columns stack on narrow screens.
left, middle, right = st.columns([1.05, 2.25, 1.05], gap="medium")
with middle:
    st.subheader("🌐 Global Disease Cases Map")
    if "code" in filtered:
        country_cases = filtered.dropna(subset=["code"]).groupby("code",as_index=False)["cases"].sum()
        country_cases = country_cases[country_cases["code"].str.len()==3]
    else:
        country_cases = pd.DataFrame(columns=["code","cases"])
    globe = go.Figure()
    if not country_cases.empty:
        globe.add_trace(go.Choropleth(locations=country_cases["code"], z=country_cases["cases"], locationmode="ISO-3", colorscale="Blues", marker_line_color="rgba(130,200,230,.35)", marker_line_width=.4, colorbar=dict(title="Cases", len=.65, thickness=10), hovertemplate="%{location}<br>Cases: %{z:,.0f}<extra></extra>"))
    globe.update_geos(projection_type="orthographic", showocean=True, oceancolor="#071b34", showland=True, landcolor="#183a55", showcountries=True, countrycolor="#6c94a9", bgcolor="rgba(0,0,0,0)", showcoastlines=True, coastlinecolor="#5e90a9")
    globe.update_layout(height=510, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", dragmode="pan")
    st.plotly_chart(globe, use_container_width=True, config={"scrollZoom":True, "displaylogo":False})
    st.caption("Drag to rotate the globe; scroll or pinch to zoom. Blank filters mean all values.")
    a,b,c = st.columns(3)
    a.metric("Filtered records",f"{len(filtered):,}")
    b.metric("Reported cases",f"{filtered['cases'].sum():,.0f}")
    c.metric("Countries",f"{filtered['name'].nunique():,}")

with left:
    st.subheader("💉 Vaccination")
    if coverage.empty or not {"name","year","coverage"}.issubset(coverage.columns):
        st.info("Vaccination coverage data not found or missing required columns.")
    else:
        v = coverage.copy()
        if chosen_countries: v = v[v["name"].isin(chosen_countries)]
        if chosen_years: v = v[v["year"].isin(chosen_years)]
        if "coverage_category" in v:
            official = v[v["coverage_category"].str.upper().eq("OFFICIAL")]
            if not official.empty: v = official
        with st.container(border=True):
            st.markdown("**Vaccination coverage over time**")
            if "antigen" in v:
                antigens = sorted(v["antigen"].dropna().unique().tolist())
                antigen = st.selectbox("Vaccine", antigens, key="time_vaccine") if antigens else None
                if antigen: vtime = v[v["antigen"]==antigen]
                else: vtime = v
            else: vtime = v
            trend = vtime.groupby("year",as_index=False)["coverage"].mean().sort_values("year")
            line_panel(trend,"year","coverage",height=210)
        with st.expander("Compare vaccination coverage between countries"):
            countries_v = sorted(v["name"].dropna().unique().tolist())
            if len(countries_v)>=2:
                one = st.selectbox("First country", countries_v, index=0, key="v_country_1")
                two = st.selectbox("Second country", countries_v, index=1, key="v_country_2")
                subset = v[v["name"].isin([one,two])]
                if "antigen" in subset:
                    opts = sorted(subset["antigen"].dropna().unique().tolist())
                    if opts:
                        vac = st.selectbox("Vaccine to compare",opts,key="v_compare_vaccine")
                        subset = subset[subset["antigen"]==vac]
                trend = subset.groupby(["year","name"],as_index=False)["coverage"].mean()
                line_panel(trend,"year","coverage","name")
                latest = subset.dropna(subset=["year","coverage"]).sort_values("year").groupby("name").tail(1)
                st.dataframe(latest[["name","year","coverage"]],hide_index=True,use_container_width=True)
            else: st.info("Select data containing at least two countries.")
        with st.expander("Compare regions"):
            region_col = next((x for x in ("region","who_region","un_region") if x in v),None)
            if region_col:
                regions = sorted(v[region_col].dropna().unique().tolist())
                chosen_regions = st.multiselect("Regions",regions,default=regions[:2])
                r = v[v[region_col].isin(chosen_regions)].groupby(["year",region_col],as_index=False)["coverage"].mean()
                line_panel(r,"year","coverage",region_col)
            else: st.info("No region column in the vaccination dataset.")
        with st.expander("Latest vaccination coverage comparison"):
            latest = v.dropna(subset=["year","coverage"]).sort_values("year").groupby("name").tail(1).sort_values("coverage",ascending=False).head(15)
            bar_panel(latest,"name","coverage",height=300,horizontal=True)
        with st.expander("Vaccination coverage dataset"):
            st.dataframe(v.head(1000),use_container_width=True,hide_index=True)

with right:
    st.subheader("🦠 Disease")
    with st.container(border=True):
        st.markdown("**Disease breakdown**")
        d = filtered.groupby("disease",as_index=False)["cases"].sum().sort_values("cases",ascending=False).head(12)
        bar_panel(d,"disease","cases",height=280,horizontal=True)
    with st.expander("Reported disease cases over time"):
        t = filtered.groupby("year",as_index=False)["cases"].sum().sort_values("year")
        line_panel(t,"year","cases")
    with st.expander("Selected country diseases over time"):
        c = filtered.groupby(["year","disease"],as_index=False)["cases"].sum()
        if len(c["disease"].unique())>12:
            top = filtered.groupby("disease")["cases"].sum().nlargest(12).index
            c = c[c["disease"].isin(top)]
        line_panel(c,"year","cases","disease",height=290)
    with st.expander("Disease incidence rate over time"):
        if "incidence" in filtered:
            i = filtered.groupby("year",as_index=False)["incidence"].mean()
            line_panel(i,"year","incidence")
        elif not incidence.empty and {"year","incidence"}.issubset(incidence.columns):
            i = incidence.copy()
            if chosen_countries and "name" in i: i=i[i["name"].isin(chosen_countries)]
            if chosen_diseases and "disease" in i: i=i[i["disease"].isin(chosen_diseases)]
            if chosen_years: i=i[i["year"].isin(chosen_years)]
            line_panel(i.groupby("year",as_index=False)["incidence"].mean(),"year","incidence")
        else: st.info("No incidence-rate column available.")

st.divider()
with st.expander("📊 Dataset overview, filtered records and data preview"):
    a,b,c=st.columns(3)
    a.metric("All records",f"{len(cases):,}")
    b.metric("Filtered records",f"{len(filtered):,}")
    c.metric("Diseases",f"{filtered['disease'].nunique():,}")
    st.dataframe(filtered.head(1000),use_container_width=True,hide_index=True)
    st.download_button("Download filtered records (CSV)",data=filtered.to_csv(index=False).encode("utf-8"),file_name="filtered_disease_records.csv",mime="text/csv")
with st.expander("ℹ️ Data sources and interpretation"):
    st.write(f"Disease cases: {cases_source or 'not found'}; coverage: {coverage_source or 'not found'}; incidence: {incidence_source or 'not found'}.")
    st.caption("Case totals reflect reported observations, not population-adjusted rates. Coverage charts show means of available observations and are not necessarily population-weighted. Region comparisons require a region field in the coverage data. Missing data does not mean zero cases or zero vaccination.")
