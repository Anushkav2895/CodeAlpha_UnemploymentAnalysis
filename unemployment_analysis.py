"""
CodeAlpha Task: Unemployment Analysis with Python
-------------------------------------------------
Cleans, explores and visualises India's unemployment data, measures the
impact of Covid-19, looks for seasonal patterns and prints policy insights.

Run:  python unemployment_analysis.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE = Path(__file__).parent
DATA = BASE / "data"
FIG = BASE / "outputs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")
UR = "Unemployment Rate (%)"
LPR = "Labour Participation Rate (%)"
LOCKDOWN = pd.Timestamp("2020-03-25")  # India's nationwide lockdown began


# ----------------------------------------------------------------- 1. LOAD/CLEAN
def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")                      # blank rows in file 1
    for c in df.columns:
        if df[c].dtype == "object" or str(df[c].dtype).startswith("str"):
            df[c] = df[c].str.strip()
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    df = df.rename(columns={
        "Estimated Unemployment Rate (%)": UR,
        "Estimated Employed": "Employed",
        "Estimated Labour Participation Rate (%)": LPR,
    })
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    df["Period"] = df["Date"].apply(
        lambda d: "Pre-Covid" if d < pd.Timestamp("2020-03-01") else "Covid"
    )
    return df.drop_duplicates()


def load():
    a = clean(pd.read_csv(DATA / "Unemployment_in_India.csv"))
    b = clean(pd.read_csv(DATA / "Unemployment_Rate_upto_11_2020.csv"))
    b = b.rename(columns={"Region.1": "Zone"})   # North/South/East/West/Northeast
    return a, b


def save(name):
    plt.tight_layout()
    plt.savefig(FIG / f"{name}.png", dpi=150)
    plt.close()


# ----------------------------------------------------------------- 2. EXPLORE
def explore(a, b):
    print("=" * 70, "\nDATA OVERVIEW\n", "=" * 70, sep="")
    for n, d in (("Unemployment_in_India", a), ("Unemployment_Rate_upto_11_2020", b)):
        print(f"\n{n}: {d.shape[0]} rows | {d['Date'].min():%b %Y} to {d['Date'].max():%b %Y}"
              f" | {d['Region'].nunique()} regions")
        print(d[[UR, "Employed", LPR]].describe().round(2).T)

    sns.histplot(a[UR], bins=30, kde=True, color="steelblue")
    plt.title("Distribution of state-level unemployment rate (May 2019 - Jun 2020)")
    save("01_distribution")

    sns.heatmap(a[[UR, "Employed", LPR]].corr(), annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Correlation of key indicators")
    save("02_correlation")


# ----------------------------------------------------------------- 3. TRENDS
def trends(a, b):
    nat = a.groupby("Date")[UR].mean()
    nat_b = b.groupby("Date")[UR].mean()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(nat.index, nat, marker="o", label="Dataset 1 (May 2019 - Jun 2020)")
    ax.plot(nat_b.index, nat_b, marker="s", label="Dataset 2 (Jan - Oct 2020)")
    ax.axvline(LOCKDOWN, color="red", ls="--", label="National lockdown (25 Mar 2020)")
    ax.set(title="Average unemployment rate across states", ylabel=UR)
    ax.legend()
    save("03_national_trend")

    # Rural vs urban
    ru = a.groupby(["Date", "Area"])[UR].mean().unstack()
    ax = ru.plot(marker="o", figsize=(11, 5))
    ax.axvline(LOCKDOWN, color="red", ls="--")
    ax.set(title="Rural vs Urban unemployment", ylabel=UR)
    save("04_rural_urban")

    # Zones
    zn = b.groupby(["Date", "Zone"])[UR].mean().unstack()
    ax = zn.plot(marker="o", figsize=(11, 5))
    ax.axvline(LOCKDOWN, color="red", ls="--")
    ax.set(title="Unemployment by zone, 2020", ylabel=UR)
    save("05_zones")

    # Labour participation vs unemployment
    lp = b.groupby("Date")[[UR, LPR]].mean()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(lp.index, lp[UR], color="crimson", marker="o", label=UR)
    ax.set_ylabel(UR, color="crimson")
    ax2 = ax.twinx()
    ax2.plot(lp.index, lp[LPR], color="navy", marker="s", label=LPR)
    ax2.set_ylabel(LPR, color="navy")
    ax2.grid(False)
    ax.set_title("Unemployment spike vs labour participation, 2020")
    save("06_unemployment_vs_participation")
    return nat, nat_b


# ----------------------------------------------------------------- 4. COVID IMPACT
def covid_impact(a, b):
    print("\n" + "=" * 70, "\nCOVID-19 IMPACT\n", "=" * 70, sep="")
    # Baseline = Jan-Feb 2020; lockdown window = mean of Apr-May 2020.
    # Dataset 2 is used because it covers the full 2020 recovery.
    pre = b[b["Date"] < "2020-03-01"].groupby("Region")[UR].mean()
    peak_month = b.groupby("Date")[UR].mean().idxmax()
    peak = b[b["Date"].isin(pd.to_datetime(["2020-04-30", "2020-05-31"]))].groupby("Region")[UR].mean()
    chg = pd.DataFrame({"Pre-Covid (Jan-Feb)": pre, "Peak": peak}).dropna()  # Sikkim has no Jan-Feb data
    chg["Increase (pp)"] = chg["Peak"] - chg["Pre-Covid (Jan-Feb)"]
    chg = chg.sort_values("Increase (pp)", ascending=False)

    print(f"\nNational average: {chg.iloc[:, 0].mean():.2f}% (Jan-Feb 2020) -> "
          f"{chg['Peak'].mean():.2f}% (Apr-May 2020 avg; single-month high: {peak_month:%b %Y})")
    rec = b.groupby("Date")[UR].mean()
    print(f"Recovery: national average back to {rec['2020-06-30']:.1f}% by Jun 2020 and {rec.iloc[-1]:.1f}% by Oct 2020.")
    lp = b.groupby("Date")[LPR].mean()
    print(f"Labour participation: {lp.iloc[:2].mean():.1f}% (Jan-Feb) -> {lp.min():.1f}% ({lp.idxmin():%b %Y}).")
    print("\nTop 10 states by increase (percentage points):")
    print(chg.head(10).round(2))
    print("\nLeast affected 5 states:")
    print(chg.tail(5).round(2))

    plt.figure(figsize=(9, 8))
    sns.barplot(x=chg["Increase (pp)"], y=chg.index, color="indianred")
    plt.title(f"Rise in unemployment: Jan-Feb 2020 vs lockdown peak (Apr-May avg)")
    plt.xlabel("Increase (percentage points)")
    save("07_state_covid_increase")

    # Before/after boxplot
    sns.boxplot(data=b, x="Period", y=UR, order=["Pre-Covid", "Covid"], palette="Set2", hue="Period", legend=False)
    plt.title("Unemployment rate across states: Pre-Covid vs Covid")
    save("08_period_boxplot")

    # Employment loss
    emp = b.groupby("Date")["Employed"].sum() / 1e6
    print(f"\nTotal employed (27 states): {emp.iloc[:2].mean():.1f}M (Jan-Feb) -> "
          f"{emp.min():.1f}M (lowest, {emp.idxmin():%b %Y}) = "
          f"{(1 - emp.min() / emp.iloc[:2].mean()) * 100:.1f}% drop")
    ax = emp.plot(marker="o", figsize=(10, 5), color="darkgreen")
    ax.axvline(LOCKDOWN, color="red", ls="--")
    ax.set(title="Total estimated employed (27 states)", ylabel="Millions")
    save("09_employed_total")

    # Rural/urban shock (dataset 1)
    ru = a.assign(P=a["Date"].apply(lambda d: "pre" if d < pd.Timestamp("2020-03-01") else "post"))
    base = a[(a["Date"] >= "2019-05-01") & (a["Date"] < "2020-03-01")].groupby("Area")[UR].mean()
    apr = a[a["Date"] == "2020-04-30"].groupby("Area")[UR].mean()
    print("\nRural/urban (Dataset 1): avg May2019-Feb2020 vs Apr 2020")
    print(pd.DataFrame({"Baseline": base, "Apr 2020": apr}).round(2))
    return chg


# ----------------------------------------------------------------- 5. SEASONALITY
def seasonality(a):
    print("\n" + "=" * 70, "\nSEASONAL PATTERNS (pre-Covid only, May 2019 - Feb 2020)\n", "=" * 70, sep="")
    pre = a[a["Date"] < "2020-03-01"]
    m = pre.groupby("Month")[UR].mean()
    print(m.round(2).to_string())
    order = [5, 6, 7, 8, 9, 10, 11, 12, 1, 2]
    pv = pre.pivot_table(index="Area", columns="Month", values=UR, aggfunc="mean")[order]
    sns.heatmap(pv, annot=True, fmt=".1f", cmap="YlOrRd")
    plt.title("Avg unemployment by month and area (pre-Covid)")
    save("10_seasonality_heatmap")

    ax = m.reindex(order).plot(kind="bar", color="teal", figsize=(9, 4))
    ax.set(title="Pre-Covid monthly average unemployment (note: only ~1 year of data)", ylabel=UR,
           xlabel="Month")
    save("11_monthly_pattern")

    states = pre.pivot_table(index="Region", columns="Month", values=UR)[order]
    vol = states.std(axis=1).sort_values(ascending=False)
    print("\nMost volatile states pre-Covid (std dev of monthly rate):")
    print(vol.head(5).round(2).to_string())


# ----------------------------------------------------------------- 6. REGIONS
def regional(a, b):
    print("\n" + "=" * 70, "\nREGIONAL PATTERNS\n", "=" * 70, sep="")
    top = a.groupby("Region")[UR].mean().sort_values(ascending=False)
    print("\nHighest avg unemployment (Dataset 1):\n", top.head(5).round(2).to_string())
    print("\nLowest avg unemployment (Dataset 1):\n", top.tail(5).round(2).to_string())
    plt.figure(figsize=(9, 8))
    sns.barplot(x=top.values, y=top.index, color="slateblue")
    plt.title("Average unemployment rate by state (May 2019 - Jun 2020)")
    plt.xlabel(UR)
    save("12_state_ranking")

    pivot = b.pivot_table(index="Region", columns="Date", values=UR)
    pivot.columns = pivot.columns.strftime("%b")
    plt.figure(figsize=(11, 9))
    sns.heatmap(pivot, cmap="Reds", annot=True, fmt=".0f")
    plt.title("State-wise unemployment rate by month, 2020")
    save("13_state_month_heatmap")

    z = b.groupby("Zone")[UR].mean().sort_values(ascending=False)
    print("\nZone averages 2020:\n", z.round(2).to_string())


# ----------------------------------------------------------------- 7. INSIGHTS
def insights(chg, a):
    worst = chg.index[:3].tolist()
    ru = a[a["Date"] == "2020-04-30"].groupby("Area")[UR].mean()
    print("\n" + "=" * 70, "\nKEY INSIGHTS & POLICY RECOMMENDATIONS\n", "=" * 70, sep="")
    print(f"""
1. Covid-19 caused an abrupt, short-lived shock: unemployment jumped within a
   month of the lockdown and then recovered through mid-2020.
2. Hardest hit states: {', '.join(worst)} -> prioritise relief, direct
   transfers and targeted job schemes there.
3. Urban India took the sharper hit in April 2020 (Urban {ru.get('Urban', float('nan')):.1f}% vs
   Rural {ru.get('Rural', float('nan')):.1f}%) -> expand urban employment guarantees / gig-worker
   social security alongside MGNREGA-type rural support.
4. Labour participation fell with the spike: many people left the workforce
   rather than being counted as unemployed -> track participation, not just
   the headline rate.
5. The shock was very uneven across states -> region-specific stimulus, skilling
   and MSME credit support.
6. Seasonal patterns can't be confirmed from ~1 pre-Covid year; collect
   multi-year monthly data before planning around seasonality.
""")


def main():
    a, b = load()
    explore(a, b)
    trends(a, b)
    chg = covid_impact(a, b)
    seasonality(a)
    regional(a, b)
    insights(chg, a)
    print(f"Figures saved to {FIG}")


if __name__ == "__main__":
    main()
