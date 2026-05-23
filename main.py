import os
import uuid
import tempfile
import shutil
import gradio as gr
import numpy as np
import soundfile as sf
from pedalboard import (
    Pedalboard, Compressor, Gain, HighShelfFilter,
    LowShelfFilter, HighpassFilter, Limiter, Distortion, 
    NoiseGate, Chorus, Reverb
)

# --- CONFIG ---
CLABE_SPEI = "646180157053513364"
# PARCHE: PRECIOS QUE PEDISTE
PAQUETES = {
    "1_ROLA": {"precio": 250, "nombre": "1 Rola"},
    "5_ROLAS": {"precio": 700, "nombre": "5 Rolas"},
    "DISCO_8": {"precio": 1300, "nombre": "Disco 8 Rolas"},
    "STEMS_PRO": {"precio": 2500, "nombre": "Stems Pro"}
}

# PRESETS BÉLICOS - TUNEO PA TROCA Y COPPEL
GENRE_PRESETS = {
    "corrido_tumbado": {
        "low": 10, "sub": 8, "high": 7, "drive": 1.8, 
        "comp_ratio": 3, "threshold": -20, "attack_ms": 15, "release_ms": 120, 
        "makeup": 3, "stereo": 7, "lufs": -7
    },
    "reggaeton": {
        "low": 12, "sub": 10, "high": 8, "drive": 1.2, 
        "comp_ratio": 4, "threshold": -18, "attack_ms": 10, "release_ms": 80, 
        "makeup": 4, "stereo": 9, "lufs": -6
    },
    "banda_sinaloense": {
        "low": 8, "sub": 5, "high": 9, "drive": 0.8, 
        "comp_ratio": 2.5, "threshold": -22, "attack_ms": 20, "release_ms": 150, 
        "makeup": 2, "stereo": 6, "lufs": -8
    },
    "regional_mexicano": {
        "low": 9, "sub": 6, "high": 8, "drive": 1.0, 
        "comp_ratio": 3, "threshold": -21, "attack_ms": 18, "release_ms": 130, 
        "makeup": 2, "stereo": 6, "lufs": -8
    },
    "trap": {
        "low": 14, "sub": 12, "high": 6, "drive": 2.0, 
        "comp_ratio": 5, "threshold": -16, "attack_ms": 5, "release_ms": 60, 
        "makeup": 5, "stereo": 10, "lufs": -6
    },
    "hip_hop": {
        "low": 11, "sub": 9, "high": 7, "drive": 1.5, 
        "comp_ratio": 4, "threshold": -19, "attack_ms": 8, "release_ms": 90, 
        "makeup": 4, "stereo": 8, "lufs": -7
    },
    "dembow": {
        "low": 13, "sub": 11, "high": 7, "drive": 1.3, 
        "comp_ratio": 4.5, "threshold": -17, "attack_ms": 8, "release_ms": 70, 
        "makeup": 4, "stereo": 9, "lufs": -6
    },
    "malianteo": {
        "low": 15, "sub": 13, "high": 5, "drive": 2.5, 
        "comp_ratio": 6, "threshold": -15, "attack_ms": 3, "release_ms": 50, 
        "makeup": 6, "stereo": 10, "lufs": -5
    }
}

def limpiar_tmp():
    temp_dir = tempfile.gettempdir()
    for f in os.listdir(temp_dir):
        path = os.path.join(temp_dir, f)
        try:
            if os.path.isfile(path) and (f.endswith('.wav') or f.endswith('.mp3')):
                os.remove(path)
        except: pass

# --- DSP BÉLICO ---
def forjar_belico(audio_path, genero, paquete, bajo, brillo, ponch, espacio):
    if not audio_path: raise gr.Error("Sube la rola, compa.")
    
    limpiar_tmp()
    preset = GENRE_PRESETS.get(genero, GENRE_PRESETS["reggaeton"])
    data, sr = sf.read(audio_path)
    
    # 90 SEG DEMO
    demo_samples = 90 * sr
    if len(data) > demo_samples: data = data[:demo_samples]
    if data.ndim == 1: data = np.column_stack((data, data))
    
    # CHAIN BÉLICO - PA QUE RETUMBE EN LA TROCA
    chain = Pedalboard([
        NoiseGate(threshold_db=-50, ratio=2),
        HighpassFilter(cutoff_frequency_hz=25),
        LowShelfFilter(cutoff_frequency_hz=60, gain_db=(preset["sub"] + (bajo - 5))),
        LowShelfFilter(cutoff_frequency_hz=120, gain_db=(preset["low"] + (bajo - 5))),
        HighShelfFilter(cutoff_frequency_hz=10000, gain_db=(preset["high"] + brillo - 5)),
        Distortion(drive_db=(preset["drive"] + (ponch - 5) * 0.3)),
        Compressor(
            threshold_db=(preset["threshold"] - ponch + 5), 
            ratio=preset["comp_ratio"], 
            attack_ms=preset["attack_ms"], 
            release_ms=preset["release_ms"]
        ),
        Gain(gain_db=preset["makeup"]),
        Limiter(threshold_db=-0.3, release_ms=80)
    ])
    
    processed = chain(data, sr)
    
    # ESPACIO STEREO
    if espacio!= 5 and processed.shape[1] == 2:
        mid = (processed[:, 0] + processed[:, 1]) / 2
        side = (processed[:, 0] - processed[:, 1]) / 2
        width_factor = 1 + ((espacio - 5) / 3)
        side *= width_factor
        processed[:, 0] = np.clip(mid + side, -0.98, 0.98)
        processed[:, 1] = np.clip(mid - side, -0.98, 0.98)
    
    # EXPORT MP3
    output_path = os.path.join(tempfile.gettempdir(), f"belico_{uuid.uuid4().hex[:8]}.mp3")
    sf.write(output_path, processed, sr, format='MP3')
    
    precio = PAQUETES.get(paquete, {}).get("precio", 250)
    return os.path.abspath(output_path), f"✅ ROLA BÉLICA FORJADA (90S)\n💰 Costo: ${precio} MXN\n🏛️ SPEI: {CLABE_SPEI}\n\n*Pa que retumbe en la troca y en el antro*"

# --- UI BÉLICA ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="orange")) as app:
    gr.Markdown("# 🏴‍☠️ ARSENAL BÉLICO COMERCIAL v1.1")
    gr.Markdown("### *Pa Corridos Tumbados, Reggaetón, Banda, Trap, Hip-Hop*\n**TUNEO ESPECIAL: BOCINAS COPPEL + TROCAS CON BAJOS**")
    
    with gr.Tabs():
        with gr.TabItem("🎵 MASTER BÉLICO"):
            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(type="filepath", label="⬆️ SUBE TU BEAT / MEZCLA")
                    genero = gr.Dropdown(choices=list(GENRE_PRESETS.keys()), value="reggaeton", label="🎯 Género Bélico")
                    paquete = gr.Radio(choices=list(PAQUETES.keys()), value="1_ROLA", label="💳 Paquete")
                with gr.Column():
                    bajo = gr.Slider(0, 10, 7, label="🔊 BAJO - Pa que retumbe")
                    brillo = gr.Slider(0, 10, 6, label="✨ BRILLO - Pa que corte")
                    ponch = gr.Slider(0, 10, 7, label="🥊 PONCH - Pa que pegue")
                    espacio = gr.Slider(0, 10, 8, label="↔️ ESPACIO - Pa que abra")
            
            btn_forjar = gr.Button("🔥 FORJAR ROLA BÉLICA", variant="primary", size="lg")
            resultado = gr.Audio(label="💀 DEMO 90S BÉLICO", type="filepath")
            status = gr.Textbox(label="ESTADO Y PAGO", lines=4)

    btn_forjar.click(forjar_belico, inputs=[audio_input, genero, paquete, bajo, brillo, ponch, espacio], outputs=[resultado, status])

if __name__ == "__main__":
    app.queue().launch(server_name="0.0.0.0", server_port=7860)
