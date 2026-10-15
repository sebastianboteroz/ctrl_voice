import os
import time
import glob
import json
import streamlit as st
import paho.mqtt.client as paho
from PIL import Image
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from gtts import gTTS
from googletrans import Translator

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y UI SMART HOME
# ==========================================
st.set_page_config(
    page_title="AuraHome | Control por Voz IoT",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de Alto Contraste con temática Smart Home / Neon IoT
st.markdown("""
<style>
    /* Estructura Global en Modo Oscuro Elegante */
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
    }

    /* Header Visceral e Impactante */
    .smarthome-header {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
        padding: 2.2rem;
        border-radius: 20px;
        color: #FFFFFF;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(67, 56, 202, 0.25);
        border: 1px solid #4F46E5;
    }

    .smarthome-header h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.4rem;
    }

    .smarthome-header p {
        color: #C7D2FE;
        font-size: 1.1rem;
        margin: 0;
    }

    /* Estado del Sistema (Nielsen #1: Visibilidad del Estado) */
    .status-badge {
        display: inline-flex;
        align-items: center;
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        color: #38BDF8;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    .status-dot {
        height: 10px;
        width: 10px;
        background-color: #22C55E;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 8px #22C55E;
    }

    /* Cards de Control */
    .control-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Ajustes para los componentes Bokeh */
    .bk-btn-default {
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.2s ease !important;
    }

    .bk-btn-default:hover {
        background-color: #4338CA !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES MQTT ORIGINALES (SIN ALTERAR)
# ==========================================
def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("Sebaastiann")
client1.on_message = on_message

# ==========================================
# BARRA LATERAL (MONITOR IoT)
# ==========================================
with st.sidebar:
    st.markdown("## 🏡 AuraHome Hub")
    st.caption("Panel de Control Domótico Central")
    
    st.markdown("---")
    
    st.subheader("🌐 Servidor MQTT")
    st.code(f"Broker: {broker}\nPuerto: {port}\nTópico: controlvozz", language="yaml")
    
    st.markdown("---")
    
    st.subheader("💡 Atajos de Comando Recomendados")
    st.markdown("""
    * *"Encender luces de la sala"*
    * *"Apagar aire acondicionado"*
    * *"Abrir puerta principal"*
    * *"Activar modo noche"*
    """)

# ==========================================
# CUERPO PRINCIPAL
# ==========================================
st.markdown("""
<div class="smarthome-header">
    <h1>AuraHome | Control por Voz IoT 🎙️🏠</h1>
    <p>Dicta comandos en tiempo real para gestionar los dispositivos inteligentes de tu hogar.</p>
</div>
""", unsafe_allow_html=True)

# Indicador de estado
st.markdown("""
<div class="status-badge">
    <span class="status-dot"></span> Broker MQTT Activo & Listo para Conectar
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("🖼️ Dispositivo Inteligente")
    try:
        image = Image.open('voice_ctrl.jpg')
        st.image(image, width=220, caption="Asistente de Voz Inteligente")
    except Exception:
        # Respaldo visual si no se encuentra la imagen local
        st.image(
            "https://images.unsplash.com/photo-1558002038-1055907df827?auto=format&fit=crop&w=500&q=80",
            width=280,
            caption="Smart Home Control Unit"
        )

with col2:
    st.subheader("🎙️ Centro de Comandos por Voz")
    st.write("Presiona el botón e indica la acción requerida para tu hogar:")

    # Botón Bokeh Original
    stt_button = Button(label="🎙️ Iniciar Reconocimiento", width=220)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
     
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
    """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0
    )

    # Lógica Original de MQTT y creación de carpeta temp
    if result:
        if "GET_TEXT" in result:
            texto_capturado = result.get("GET_TEXT")
            
            # Notificación visual clara (Nielsen #3: Control del usuario y realimentación)
            st.success(f"🗣️ Comando detectado: **\"{texto_capturado}\"**")
            
            client1.on_publish = on_publish                           
            client1.connect(broker, port)  
            message = json.dumps({"Act1": texto_capturado.strip()})
            ret = client1.publish("controlvozz", message)
            
            st.info(f"📡 Trama enviada al Broker MQTT: `{message}`")

        try:
            os.mkdir("temp")
        except:
            pass
