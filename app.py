import streamlit as st
import pandas as pd
import numpy as np
import textwrap
import plotly.express as px

# =========================================================
# Config
# =========================================================
st.set_page_config(
    page_title="APBD 2023 • Dashboard Fiskal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CSS (UI polish + micro-animations)
# =========================================================
st.markdown(
    """
<style>
/* Layout tweaks */
.block-container {padding-top: 1.1rem; padding-bottom: 2.2rem;}
section[data-testid="stSidebar"] {border-right: 1px solid rgba(255,255,255,.08);}
hr {margin: 0.8rem 0 1.0rem 0; opacity: .25}

/* Hero header */
.hero {
  border-radius: 22px;
  padding: 22px 24px;
  background: linear-gradient(120deg, rgba(99,102,241,.22), rgba(14,165,233,.18), rgba(16,185,129,.16));
  background-size: 220% 220%;
  border: 1px solid rgba(255,255,255,.10);
  box-shadow: 0 10px 30px rgba(0,0,0,.18);
  position: relative;
  overflow: hidden;
  animation: fadeInUp .7s ease both, heroShift 16s ease-in-out infinite;
}
.hero:before {
  content: "";
  position: absolute;
  inset: -80px;
  background: radial-gradient(circle at 20% 20%, rgba(99,102,241,.30), transparent 40%),
              radial-gradient(circle at 80% 30%, rgba(14,165,233,.26), transparent 40%),
              radial-gradient(circle at 40% 85%, rgba(16,185,129,.20), transparent 45%);
  filter: blur(18px);
  animation: floaty 10s ease-in-out infinite alternate;
  opacity: .95;
}
.hero * {position: relative; z-index: 1;}
.hero h1 {margin: 0; font-size: 1.55rem; letter-spacing: .2px;}
.hero p {margin: .25rem 0 0 0; opacity: .88}

/* Metric cards */
.kpi-grid {display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 14px;}
@media (max-width: 1100px){ .kpi-grid {grid-template-columns: repeat(2, minmax(0, 1fr));} }
@media (max-width: 560px){ .kpi-grid {grid-template-columns: repeat(1, minmax(0, 1fr));} }

.kpi{
  position: relative;
  border-radius: 18px;
  padding: 14px 14px 12px 14px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.045);
  box-shadow: 0 12px 28px rgba(0,0,0,.18);
  overflow: hidden;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease, background .18s ease;
  animation: fadeInUp .75s ease both;
}
.kpi:before{
  content:"";
  position:absolute; inset:-1px;
  background: radial-gradient(1000px 220px at 10% 0%, rgba(99,102,241,.35), transparent 55%),
              radial-gradient(1000px 220px at 90% 0%, rgba(16,185,129,.25), transparent 55%);
  opacity:.55; pointer-events:none;
}
.kpi:after{
  content:"";
  position:absolute; inset:0;
  background: linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,0));
  opacity:.18; pointer-events:none;
}
.kpi:hover{
  transform: translateY(-3px);
  box-shadow: 0 18px 44px rgba(0,0,0,.28);
  border-color: rgba(255,255,255,.16);
  background: rgba(255,255,255,.06);
}
.kpi-top{display:flex; align-items:center; gap:.55rem; margin-bottom:.25rem; position:relative; z-index:2;}
.kpi-icon{
  width: 34px; height: 34px;
  display:flex; align-items:center; justify-content:center;
  border-radius: 12px;
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.10);
  box-shadow: inset 0 0 0 1px rgba(0,0,0,.08);
  animation: pop .9s ease both;
}
.kpi:nth-child(1) .kpi-icon{background: rgba(99,102,241,.18);}
.kpi:nth-child(2) .kpi-icon{background: rgba(16,185,129,.16);}
.kpi:nth-child(3) .kpi-icon{background: rgba(245,158,11,.16);}
.kpi:nth-child(4) .kpi-icon{background: rgba(236,72,153,.16);}

.kpi .label{font-size:.84rem; opacity:.86; margin:0; font-weight:600; letter-spacing:.2px; position:relative; z-index:2;}
.kpi .value{font-size:1.22rem; font-weight:800; margin:.10rem 0 .15rem 0; position:relative; z-index:2;}
.kpi .hint{font-size:.78rem; opacity:.72; margin:0; position:relative; z-index:2;}

@keyframes pop{0%{transform:scale(.92); opacity:.0} 100%{transform:scale(1); opacity:1}}
.pill {
  display:inline-block; font-size:.72rem; padding:.2rem .55rem; border-radius: 999px;
  background: rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10); opacity:.9;
}

/* Nice section cards */
.card {
  border-radius: 22px;
  padding: 16px 16px 8px 16px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.03);
  box-shadow: 0 10px 28px rgba(0,0,0,.14);
  animation: fadeInUp .7s ease both;
}

/* Small animations */
@keyframes fadeInUp {
  from {opacity: 0; transform: translateY(8px);}
  to {opacity: 1; transform: translateY(0);}
@keyframes heroShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

}
@keyframes floaty {
  from {transform: translate3d(0,0,0) scale(1);}
  to   {transform: translate3d(18px,-10px,0) scale(1.02);}
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# Helpers
# =========================================================
def fmt_idr(x: float) -> str:
    if pd.isna(x):
        return "Rp 0"
    x = float(x)
    absx = abs(x)
    if absx >= 1e12:
        return f"Rp {x/1e12:,.2f} T"
    if absx >= 1e9:
        return f"Rp {x/1e9:,.2f} M"
    if absx >= 1e6:
        return f"Rp {x/1e6:,.2f} Jt"
    return f"Rp {x:,.0f}"

def fmt_pct(x: float) -> str:
    if pd.isna(x) or np.isinf(x):
        return "-"
    return f"{x*100:.1f}%"

def pick_col(df: pd.DataFrame, candidates: list[str]) -> str:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    raise KeyError(f"Kolom tidak ditemukan. Cari salah satu dari: {candidates}. Kolom yang ada: {list(df.columns)}")

@st.cache_data(show_spinner=False)
def load_long(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # normalize colnames
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    # minimal compatibility for similar datasets
    ren = {}
    if "namapemda" in df.columns: ren["namapemda"] = "daerah"
    if "nama_pemda" in df.columns: ren["nama_pemda"] = "daerah"
    if "pemda" in df.columns: ren["pemda"] = "daerah"
    df = df.rename(columns=ren)

    required = {"daerah", "provinsi", "pulau", "level1", "level2", "nilai"}
    missing = sorted(list(required - set(df.columns)))
    if missing:
        raise KeyError(
            "Kolom wajib tidak ditemukan: "
            + ", ".join(missing)
            + f". Kolom yang ada: {list(df.columns)}"
        )

    df["daerah"] = df["daerah"].astype(str).str.strip()
    df["provinsi"] = df["provinsi"].astype(str).str.strip()
    df["pulau"] = df["pulau"].astype(str).str.strip()
    df["level1"] = df["level1"].astype(str).str.strip()
    df["level2"] = df["level2"].astype(str).str.strip()
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce").fillna(0.0)

    return df

@st.cache_data(show_spinner=False)
def build_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    pendapatan = (
        df_long[df_long["level1"].str.contains("Pendapatan", case=False, na=False)]
        .groupby(["daerah", "provinsi", "pulau"], as_index=False)["nilai"].sum()
        .rename(columns={"nilai": "total_pendapatan"})
    )
    belanja = (
        df_long[df_long["level1"].str.contains("Belanja", case=False, na=False)]
        .groupby(["daerah", "provinsi", "pulau"], as_index=False)["nilai"].sum()
        .rename(columns={"nilai": "total_belanja"})
    )

    pad = (
        df_long[
            (df_long["level1"].str.contains("Pendapatan", case=False, na=False))
            & (df_long["level2"].str.contains("PAD", case=False, na=False))
        ]
        .groupby(["daerah", "provinsi", "pulau"], as_index=False)["nilai"].sum()
        .rename(columns={"nilai": "pad"})
    )

    def belanja_comp(keyword: str, out_col: str) -> pd.DataFrame:
        return (
            df_long[
                (df_long["level1"].str.contains("Belanja", case=False, na=False))
                & (df_long["level2"].str.contains(keyword, case=False, na=False))
            ]
            .groupby(["daerah", "provinsi", "pulau"], as_index=False)["nilai"].sum()
            .rename(columns={"nilai": out_col})
        )

    b_operasi = belanja_comp("Belanja Operasi", "belanja_operasi")
    b_modal = belanja_comp("Belanja Modal", "belanja_modal")
    b_tidak = belanja_comp("Belanja Tidak Terduga", "belanja_tidak_terduga")
    b_transfer = belanja_comp("Belanja Transfer", "belanja_transfer")

    wide = pendapatan.merge(belanja, on=["daerah", "provinsi", "pulau"], how="outer")
    for part in [pad, b_operasi, b_modal, b_tidak, b_transfer]:
        wide = wide.merge(part, on=["daerah", "provinsi", "pulau"], how="left")

    for c in ["total_pendapatan", "total_belanja", "pad",
              "belanja_operasi", "belanja_modal", "belanja_tidak_terduga", "belanja_transfer"]:
        if c not in wide.columns:
            wide[c] = 0.0
        wide[c] = pd.to_numeric(wide[c], errors="coerce").fillna(0.0)

    wide["surplus_defisit"] = wide["total_pendapatan"] - wide["total_belanja"]

    # ratios
    wide["rasio_pad"] = np.where(wide["total_pendapatan"] > 0, wide["pad"] / wide["total_pendapatan"], np.nan)
    wide["rasio_modal"] = np.where(wide["total_belanja"] > 0, wide["belanja_modal"] / wide["total_belanja"], np.nan)
    wide["rasio_operasi"] = np.where(wide["total_belanja"] > 0, wide["belanja_operasi"] / wide["total_belanja"], np.nan)

    return wide

def kpi_cards(items: list[tuple[str, str, str]]):
    """Pretty KPI cards (HTML/CSS). Use textwrap.dedent so Markdown doesn't treat it as a code block."""
    def pick_icon(label: str) -> str:
        l = label.lower()
        if "jumlah" in l or "daerah" in l:
            return "🏙️"
        if "pendapatan" in l:
            return "💰"
        if "belanja" in l:
            return "🧾"
        if "surplus" in l or "defisit" in l:
            return "⚖️"
        return "📌"

    cards: list[str] = []
    for i, (label, value, hint) in enumerate(items):
        delay = 80 + i * 80
        icon = pick_icon(label)
        card_html = textwrap.dedent(f"""
        <div class="kpi" style="animation-delay:{delay}ms">
          <div class="kpi-top">
            <div class="kpi-icon">{icon}</div>
            <p class="label">{label}</p>
          </div>
          <p class="value">{value}</p>
          <p class="hint">{hint}</p>
        </div>
        """).strip()
        cards.append(card_html)

    html = '<div class="kpi-grid">' + "".join(cards) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def insight_box(title: str, bullets: list[str], emoji: str = "💡"):
    lis = "".join([f"<li>{b}</li>" for b in bullets])
    html = f"""
<div class="card insight">
  <div class="insight-head">
    <div class="insight-emoji">{emoji}</div>
    <div class="insight-title">{title}</div>
  </div>
  <ul class="insight-list">{lis}</ul>
</div>
"""
    st.markdown(html.strip(), unsafe_allow_html=True)

# =========================================================
# Data
# =========================================================
DATA_PATH = "data/APBD_2023.csv"

df_long = load_long(DATA_PATH)
wide = build_wide(df_long)

# =========================================================
# Sidebar filters
# =========================================================
st.sidebar.markdown("### 🎛️ Filter")
all_pulau = ["(Semua)"] + sorted([p for p in wide["pulau"].dropna().unique().tolist() if p.strip() != ""])
pulau = st.sidebar.selectbox("Pulau", all_pulau, index=0)

prov_choices = sorted(wide["provinsi"].dropna().unique().tolist())
provinsi = st.sidebar.multiselect("Provinsi", prov_choices, default=[])

q = st.sidebar.text_input("Cari daerah / provinsi", value="", placeholder="contoh: Bogor, Jawa Barat...")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👥 Identitas")
st.sidebar.markdown("**Kelompok 31**")
st.sidebar.markdown(
    """
- **0110222078** — Muhammad Lutfi Alfian  
- **0110222094** — Ahmad Yasin  
- **0110222098** — Farhan Ijayansyah  
"""
)
with st.sidebar.expander("Tentang dashboard"):
    st.write(
        "Dashboard ini merangkum APBD 2023 berdasarkan dataset (format long) menjadi metrik pendapatan, belanja, "
        "komposisi belanja, dan rasio-rasio sederhana untuk analisis fiskal."
    )

# apply filters
f = wide.copy()
if pulau != "(Semua)":
    f = f[f["pulau"] == pulau]
if provinsi:
    f = f[f["provinsi"].isin(provinsi)]
if q.strip():
    qq = q.strip().lower()
    f = f[
        f["daerah"].str.lower().str.contains(qq, na=False)
        | f["provinsi"].str.lower().str.contains(qq, na=False)
        | f["pulau"].str.lower().str.contains(qq, na=False)
    ]

# =========================================================
# Header
# =========================================================
st.markdown(
    """
<div class="hero">
  <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px;">
    <div>
      <h1>📊 Dashboard APBD 2023 • Analisis Fiskal Daerah</h1>
      <p>
        Eksplorasi pendapatan, belanja, komposisi belanja, dan rasio kinerja fiskal.
        <span class="pill">Kelompok 31</span>
      </p>
    </div>
    <div style="text-align:right; opacity:.85; font-size:.85rem;">
      <div><b>Dataset:</b> APBD_2023.csv</div>
      <div><b>Mode:</b> Interaktif (filter sidebar)</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# KPIs
# =========================================================
if len(f) == 0:
    st.warning("Tidak ada data yang cocok dengan filter. Coba reset filter di sidebar.")
    st.stop()

sd = f["surplus_defisit"].sum()
label_sd = "Surplus (net)" if sd >= 0 else "Defisit (net)"

kpi_cards([
    ("Jumlah daerah (terfilter)", f"{len(f):,}", "unit pemda"),
    ("Total pendapatan", fmt_idr(f["total_pendapatan"].sum()), "akumulasi"),
    ("Total belanja", fmt_idr(f["total_belanja"].sum()), "akumulasi"),
    (label_sd, fmt_idr(sd), "pendapatan - belanja"),
])

st.divider()

# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs(["🏁 Ringkasan", "🏗️ Komposisi Belanja", "🧭 Rasio & Kinerja", "🥧 Breakdown Daerah"])

# ---------------------------------------------------------
# TAB 1: Overview
# ---------------------------------------------------------
with tab1:
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Top Daerah (Ranking)")
        metric = st.selectbox("Urutkan berdasarkan", ["Total Pendapatan", "Total Belanja", "Surplus/Defisit"], index=0)
        if metric == "Total Pendapatan":
            rank_df = f.sort_values("total_pendapatan", ascending=False).head(20)
            show_cols = ["daerah", "provinsi", "pulau", "total_pendapatan", "pad", "rasio_pad"]
            rank_df["rasio_pad"] = rank_df["rasio_pad"].astype(float)
        elif metric == "Total Belanja":
            rank_df = f.sort_values("total_belanja", ascending=False).head(20)
            show_cols = ["daerah", "provinsi", "pulau", "total_belanja", "belanja_operasi", "belanja_modal", "rasio_modal"]
            rank_df["rasio_modal"] = rank_df["rasio_modal"].astype(float)
        else:
            rank_df = f.sort_values("surplus_defisit", ascending=False).head(20)
            show_cols = ["daerah", "provinsi", "pulau", "surplus_defisit", "total_pendapatan", "total_belanja", "rasio_pad"]

        view = rank_df[show_cols].copy()
        money_cols = [c for c in view.columns if c.startswith("total_") or c.startswith("belanja_") or c in ("pad", "surplus_defisit")]
        for c in money_cols:
            view[c] = view[c].map(fmt_idr)
        pct_cols = [c for c in view.columns if c.startswith("rasio_")]
        for c in pct_cols:
            view[c] = view[c].map(fmt_pct)

        st.dataframe(view, use_container_width=True, hide_index=True)
        st.caption("Tip: gunakan filter di sidebar untuk mempersempit data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Pendapatan vs Belanja (Top 15)")
        topn = (
            f.sort_values("total_pendapatan", ascending=False)
            .head(15)
            .copy()
        )
        melt = topn.melt(
            id_vars=["daerah", "provinsi", "pulau"],
            value_vars=["total_pendapatan", "total_belanja"],
            var_name="kategori",
            value_name="nilai",
        )
        melt["kategori"] = melt["kategori"].map({"total_pendapatan": "Pendapatan", "total_belanja": "Belanja"})
        fig = px.bar(
            melt,
            x="daerah",
            y="nilai",
            color="kategori",
            barmode="group",
            hover_data=["provinsi", "pulau"],
            height=420,
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None, yaxis_title="Nilai (Rp)")
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Quick insights
    top_invest = f.sort_values("rasio_modal", ascending=False).head(1).iloc[0]
    top_ops = f.sort_values("rasio_operasi", ascending=False).head(1).iloc[0]
    insight_box(
        "Insight cepat",
        [
            f"Belanja modal paling tinggi (rasio): **{top_invest['daerah']}** — {fmt_pct(top_invest['rasio_modal'])} dari total belanja.",
            f"Belanja operasi paling 'gendut' (rasio): **{top_ops['daerah']}** — {fmt_pct(top_ops['rasio_operasi'])} dari total belanja.",
            "Rasio ini membantu melihat kecenderungan **investasi jangka panjang** (modal) vs **biaya rutin** (operasi).",
        ],
        emoji="⚡",
    )

# ---------------------------------------------------------
# TAB 2: Belanja composition stacked bar + insights
# ---------------------------------------------------------
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Komposisi Belanja per Daerah (Stacked Bar)")
    st.caption("Sumbu X: daerah • Sumbu Y: total belanja • Warna: komponen belanja")

    n = st.slider("Jumlah daerah yang ditampilkan", min_value=5, max_value=35, value=15, step=5)
    basis = st.selectbox("Pilih basis urutan", ["Total Belanja", "Rasio Belanja Modal", "Rasio Belanja Operasi"], index=0)
    if basis == "Total Belanja":
        bdf = f.sort_values("total_belanja", ascending=False).head(n).copy()
    elif basis == "Rasio Belanja Modal":
        bdf = f.sort_values("rasio_modal", ascending=False).head(n).copy()
    else:
        bdf = f.sort_values("rasio_operasi", ascending=False).head(n).copy()

    comp = bdf[[
        "daerah", "provinsi", "pulau",
        "belanja_operasi", "belanja_modal", "belanja_tidak_terduga", "belanja_transfer"
    ]].copy()

    comp_long = comp.melt(
        id_vars=["daerah", "provinsi", "pulau"],
        var_name="komponen",
        value_name="nilai",
    )
    label_map = {
        "belanja_operasi": "Belanja Operasi",
        "belanja_modal": "Belanja Modal",
        "belanja_tidak_terduga": "Belanja Tidak Terduga",
        "belanja_transfer": "Belanja Transfer",
    }
    comp_long["komponen"] = comp_long["komponen"].map(label_map).fillna(comp_long["komponen"])

    fig2 = px.bar(
        comp_long,
        x="daerah",
        y="nilai",
        color="komponen",
        barmode="stack",
        hover_data=["provinsi", "pulau"],
        height=460,
    )
    fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None, yaxis_title="Total Belanja (Rp)")
    fig2.update_xaxes(tickangle=-35)
    st.plotly_chart(fig2, use_container_width=True)

    # insights for modal vs operasi
    modal_big = f.dropna(subset=["rasio_modal"]).sort_values("rasio_modal", ascending=False).head(5)
    ops_big = f.dropna(subset=["rasio_operasi"]).sort_values("rasio_operasi", ascending=False).head(5)

    st.markdown("#### 🔍 Insight")
    colA, colB = st.columns(2)
    with colA:
        insight_box(
            "Proporsi belanja modal besar (indikasi investasi jangka panjang)",
            [f"**{r.daerah}** ({r.provinsi}) — {fmt_pct(r.rasio_modal)}" for r in modal_big.itertuples()],
            emoji="🏗️",
        )
    with colB:
        insight_box(
            "Belanja operasi “gendut” (indikasi dominasi biaya rutin)",
            [f"**{r.daerah}** ({r.provinsi}) — {fmt_pct(r.rasio_operasi)}" for r in ops_big.itertuples()],
            emoji="🧾",
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: Ratios + scatter map
# ---------------------------------------------------------
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Perbandingan Rasio (Analitis Ringan)")
    st.caption("Rasio PAD/Total Pendapatan vs Rasio Belanja Modal/Total Belanja (peta kinerja fiskal sederhana)")

    # Example selection
    default_examples = (
        f.sort_values("total_pendapatan", ascending=False)["daerah"].head(8).tolist()
    )
    pick_daerah = st.multiselect("Pilih beberapa daerah", sorted(f["daerah"].unique().tolist()), default=default_examples)

    ex = f[f["daerah"].isin(pick_daerah)].copy()
    ex = ex.replace([np.inf, -np.inf], np.nan)

    c1, c2 = st.columns([1, 1.3])

    with c1:
        # bar for ratios
        bar_df = ex[["daerah", "rasio_pad", "rasio_modal"]].copy()
        bar_long = bar_df.melt(id_vars=["daerah"], var_name="rasio", value_name="nilai")
        bar_long["rasio"] = bar_long["rasio"].map({"rasio_pad": "Rasio PAD / Pendapatan", "rasio_modal": "Rasio Modal / Belanja"})
        fig3 = px.bar(
            bar_long,
            x="daerah",
            y="nilai",
            color="rasio",
            barmode="group",
            height=430,
        )
        fig3.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None, yaxis_title="Rasio")
        fig3.update_yaxes(tickformat=".0%")
        fig3.update_xaxes(tickangle=-35)
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        # scatter map of performance
        scatter_df = f.copy()
        scatter_df = scatter_df.replace([np.inf, -np.inf], np.nan).dropna(subset=["rasio_pad", "rasio_modal"])
        xmed = float(scatter_df["rasio_pad"].median()) if len(scatter_df) else 0.0
        ymed = float(scatter_df["rasio_modal"].median()) if len(scatter_df) else 0.0

        fig4 = px.scatter(
            scatter_df,
            x="rasio_pad",
            y="rasio_modal",
            size="total_pendapatan",
            hover_name="daerah",
            hover_data={"provinsi": True, "pulau": True, "total_pendapatan": ":,.0f", "total_belanja": ":,.0f"},
            color="pulau",
            height=430,
        )
        # median lines (quadrants)
        fig4.add_vline(x=xmed, line_dash="dot")
        fig4.add_hline(y=ymed, line_dash="dot")
        fig4.update_layout(margin=dict(l=10, r=10, t=10, b=10), xaxis_title="Rasio PAD / Total Pendapatan", yaxis_title="Rasio Belanja Modal / Total Belanja")
        fig4.update_xaxes(tickformat=".0%")
        fig4.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig4, use_container_width=True)

        insight_box(
            "Cara baca scatter",
            [
                "Kanan-atas: **PAD kuat** + **investasi tinggi** (modal besar).",
                "Kanan-bawah: **PAD kuat**, tapi **investasi rendah** (modal kecil).",
                "Kiri-atas: **PAD lemah**, tapi **investasi tinggi** (butuh kehati-hatian pembiayaan).",
                "Kiri-bawah: **PAD lemah** + **investasi rendah**.",
            ],
            emoji="🧭",
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 4: Breakdown pies
# ---------------------------------------------------------
with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Breakdown (Pie) per Daerah")
    st.caption("Pilih daerah → lihat komposisi belanja (Operasi/Modal/Tidak Terduga/Transfer)")

    # default picks from ranking
    rank_df = f.sort_values("total_belanja", ascending=False).head(10)
    default_picks = rank_df["daerah"].head(3).tolist()

    picks = st.multiselect(
        "Pilih daerah untuk pie chart",
        options=sorted(f["daerah"].unique().tolist()),
        default=default_picks,
    )

    if not picks:
        st.info("Pilih minimal 1 daerah untuk menampilkan pie chart.")
        st.stop()

    show = f[f["daerah"].isin(picks)].copy()

    # show pies in grid
    cols = st.columns(min(3, len(picks)))
    for i, d in enumerate(picks):
        row = show[show["daerah"] == d].iloc[0]
        pie_df = pd.DataFrame({
            "komponen": ["Belanja Operasi", "Belanja Modal", "Belanja Tidak Terduga", "Belanja Transfer"],
            "nilai": [row["belanja_operasi"], row["belanja_modal"], row["belanja_tidak_terduga"], row["belanja_transfer"]],
        })
        figp = px.pie(pie_df, names="komponen", values="nilai", hole=.45)
        figp.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=360, title=f"{d}")
        with cols[i % len(cols)]:
            st.plotly_chart(figp, use_container_width=True)
            st.caption(f"Total belanja: **{fmt_idr(row['total_belanja'])}** • Rasio modal: **{fmt_pct(row['rasio_modal'])}**")

    st.markdown("#### ✨ Mini Insight")
    # best/worst among picks
    show2 = show.dropna(subset=["rasio_modal", "rasio_operasi"])
    if len(show2) >= 1:
        best_modal = show2.sort_values("rasio_modal", ascending=False).iloc[0]
        best_ops = show2.sort_values("rasio_operasi", ascending=False).iloc[0]
        insight_box(
            "Dari pilihan kamu",
            [
                f"Modal tertinggi: **{best_modal['daerah']}** — {fmt_pct(best_modal['rasio_modal'])}",
                f"Operasi tertinggi: **{best_ops['daerah']}** — {fmt_pct(best_ops['rasio_operasi'])}",
            ],
            emoji="🥇",
        )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# Footer
# =========================================================
st.markdown(
    """
<div style="margin-top: 16px; opacity: .78; font-size: .85rem;">
  <hr/>
  <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>© 2026 • Dashboard APBD 2023 • <b>Kelompok 31</b></div>
    <div style="text-align:right;">
      Dibuat oleh: 0110222078-Muhammad Lutfi Alfian • 0110222094-Ahmad Yasin • 0110222098-Farhan Ijayansyah
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
