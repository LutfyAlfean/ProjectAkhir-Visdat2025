# APBD 2023 — Streamlit Dashboard 

Dashboard interaktif untuk eksplorasi **Pendapatan**, **Belanja**, **Komposisi Belanja**, dan **Rasio kinerja fiskal** dari dataset `APBD_2023.csv`.

## Identitas
**Kelompok 31**
- 0110222078 — Muhammad Lutfi Alfian
- 0110222094 — Ahmad Yasin
- 0110222098 — Farhan Ijayansyah

## Fitur Utama
- Filter interaktif: Pulau, Provinsi, dan pencarian daerah
- KPI cards (Pendapatan/Belanja/Surplus-Defisit) + UI modern dengan micro-animasi
- Ranking Top daerah (pendapatan/belanja/surplus-defisit)
- Stacked bar komposisi belanja (Operasi/Modal/Tidak Terduga/Transfer) + insight otomatis
- Analisis rasio: PAD/pendapatan & belanja modal/belanja + scatter “peta kinerja fiskal”
- Pie breakdown per daerah untuk komposisi belanja

## Run (Local)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run (Docker)
```bash
docker compose up -d --build
```

## Dataset
Letakkan file di:
`data/APBD_2023.csv`

Format minimal kolom:
`daerah/provinsi/pulau/level1/level2/nilai`
