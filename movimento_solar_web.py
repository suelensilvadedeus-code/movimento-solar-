
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import io
import qrcode
from PIL import Image
import tempfile
import os

# ------------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA
# ------------------------------------------------------------
st.set_page_config(page_title="Movimento Solar - Irradiância", layout="wide")

st.title("☀️ Movimento do Sol - Irradiância Solar")
st.markdown("""
Este simulador mostra a variação da **irradiância solar (W/m²)** conforme o movimento aparente do Sol.  
Envie o arquivo de medições (.csv), escolha até 4 regiões e visualize a animação com base nos coeficientes de conversão (ADC → Irradiância).
""")

# ------------------------------------------------------------
# COEFICIENTES DE CONVERSÃO (ADC → W/m²)
# ------------------------------------------------------------
coeficientes = {
    "Brasil": (0.021269, -37.69),
    "Alemanha": (0.009186, 35.71),
    "Egito": (0.021190, 23.21),
    "Bahia": (0.019239, -40.61),
    "Minas Gerais": (0.023884, -139.55),
    "Mato Grosso": (0.021707, -66.17),
    "Paraná": (0.012767, 104.99),
    "Salvador": (0.011556, 58.52),
    "Feira": (0.01042, 0.132),
    "Barreiras": (0.021712, 10.18),
    "Cabula": (0.0139, -46.43)
}

# ------------------------------------------------------------
# UPLOAD DO CSV
# ------------------------------------------------------------
arquivo = st.file_uploader("📂 Envie o arquivo CSV unificado", type="csv")

# ------------------------------------------------------------
# SELEÇÃO DE REGIÕES
# ------------------------------------------------------------
regioes_escolhidas = st.multiselect(
    "🌍 Escolha até 4 regiões:",
    list(coeficientes.keys()),
    ["Brasil", "Alemanha", "Egito"]
)

# ------------------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ------------------------------------------------------------
if arquivo and regioes_escolhidas:
    df = pd.read_csv(arquivo, encoding="utf-8-sig")
    df.columns = [c.strip().replace("ã", "a").replace("á", "a") for c in df.columns]

    if "Regiao" not in df.columns or "ADC" not in df.columns:
        st.error("❌ O CSV deve conter as colunas 'Regiao' e 'ADC'.")
        st.stop()

    tipo_col = None
    for c in df.columns:
        if c.strip().lower() == "tipo":
            tipo_col = c
            break

    dados = {}
    for regiao in regioes_escolhidas:
        subset = df[df["Regiao"].str.strip().str.lower() == regiao.lower()]
        if subset.empty:
            st.warning(f"⚠️ Nenhum dado encontrado para {regiao}")
            continue

        usar_direto = False

        # --- Condição 1: Tipo == País ---
        if tipo_col:
            tipo_val = subset[tipo_col].dropna().astype(str).str.strip().str.lower()
            if not tipo_val.empty:
                tipo_freq = tipo_val.mode().iloc[0]
                if tipo_freq in ("pais", "país"):
                    usar_direto = True

        # --- Condição 2: ADC médio muito alto ---
        if not usar_direto:
            adc_media = subset["ADC"].astype(float).mean()
            if adc_media > 200:
                usar_direto = True

        # --- Aplicação ---
        if usar_direto:
            irradiancia = subset["ADC"].astype(float).values
        else:
            a, b = coeficientes.get(regiao, (None, None))
            if a is None:
                st.warning(f"⚠️ Nenhum coeficiente para {regiao}. Ignorado.")
                continue
            irradiancia = a * subset["ADC"].astype(float) + b

        dados[regiao] = irradiancia

    # ------------------------------------------------------------
    # GRÁFICO E ANIMAÇÃO
    # ------------------------------------------------------------
    if dados:
        frames_total = max(len(v) for v in dados.values())
        angulos = np.linspace(0, 180, frames_total)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.set_xlim(0, 180)
        all_vals = np.concatenate(list(dados.values()))
        y_max = max(1000, np.nanmax(all_vals) * 1.15)
        ax.set_ylim(0, y_max)
        ax.set_xlabel("Ângulo Solar (°)", fontsize=12)
        ax.set_ylabel("Irradiância (W/m²)", fontsize=12)
        ax.set_title("Movimento do Sol - Irradiância Solar", fontsize=16, weight="bold")
        ax.set_facecolor('#cce6ff')
        ax.grid(True, linestyle='--', alpha=0.5)

        cores = ["orange", "green", "red", "blue"]
        linhas, marcadores = {}, {}
        for i, regiao in enumerate(dados.keys()):
            linha, = ax.plot([], [], label=regiao, color=cores[i % len(cores)], linewidth=2)
            marcador, = ax.plot([], [], 'o', color='gold', markersize=10)
            linhas[regiao] = linha
            marcadores[regiao] = marcador
        ax.legend(loc='upper right')

        def init():
            for linha in linhas.values():
                linha.set_data([], [])
            return list(linhas.values())

        def animate(i):
            for regiao in dados.keys():
                valores = dados[regiao]
                n = min(i + 1, len(valores))
                linhas[regiao].set_data(angulos[:n], valores[:n])
                marcadores[regiao].set_data([angulos[n-1]], [valores[n-1]])
            return list(linhas.values()) + list(marcadores.values())

        ani = animation.FuncAnimation(fig, animate, init_func=init, frames=frames_total, interval=100, blit=True)

        # ------------------------------------------------------------
        # SALVAR GIF CORRETAMENTE (arquivo temporário)
        # ------------------------------------------------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmpfile:
            ani.save(tmpfile.name, writer="pillow", fps=10)
            tmpfile_path = tmpfile.name

        with open(tmpfile_path, "rb") as f:
            gif_bytes = f.read()

        st.image(gif_bytes, caption="🎞️ Animação do Movimento Solar (Calibrada)", use_container_width=True)

        st.download_button(
            label="💾 Baixar animação como GIF",
            data=gif_bytes,
            file_name="movimento_solar.gif",
            mime="image/gif"
        )

        os.remove(tmpfile_path)

        # ------------------------------------------------------------
        # QR CODE
        # ------------------------------------------------------------
        st.divider()
        st.subheader("🔗 Compartilhe seu simulador via QR Code")

        link_app = "https://movimento-solar.streamlit.app"
        qr_img = qrcode.make(link_app)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        st.image(qr_buffer, caption=f"Acesse o simulador em:\n{link_app}", width=200)

    else:
        st.error("❌ Nenhum dado válido foi encontrado para as regiões selecionadas.")
