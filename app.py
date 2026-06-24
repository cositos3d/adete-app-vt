import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
import pandas as pd
import os
from datetime import datetime
import pytz

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CadeteApp Pro", page_icon="🛵", layout="centered")

# Configurar Zona Horaria de Argentina
ARG_TZ = pytz.timezone('America/Argentina/Buenos_Aires')
ARCHIVO_HISTORIAL = "historial_viajes.csv"

# --- ESTILOS CSS (Animación de carga y de cálculo) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* Animación 1: El saludo de bienvenida (Splash) */
    @keyframes saludo-inicial {
        0% { transform: translateX(-150px) scaleX(1); }
        45% { transform: translateX(80px) scaleX(1); }
        50% { transform: translateX(80px) scaleX(-1); } /* Gira para saludar */
        75% { transform: translateX(80px) scaleX(-1); }
        80% { transform: translateX(80px) scaleX(1); }  /* Vuelve a mirar al frente */
        100% { transform: translateX(400px) scaleX(1); } /* Se va de la pantalla */
    }
    .welcome-box { text-align: center; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .cadete-saludo { font-size: 70px; animation: saludo-inicial 3.5s forwards linear; width: fit-content; margin: 0 auto; }
    
    /* Animación 2: La motito del cálculo */
    @keyframes move-moto {
        0% { transform: translateX(-100px); }
        100% { transform: translateX(300px); }
    }
    .moto-animation { font-size: 50px; animation: move-moto 2s infinite linear; width: 100%; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE MEMORIA DE SESIÓN ---
if 'tarifas' not in st.session_state:
    st.session_state.tarifas = {"base": 3000.0, "km_min": 1.5, "km_extra": 1000.0}

if 'viaje_actual' not in st.session_state:
    st.session_state.viaje_actual = None

# Control de la pantalla de bienvenida
if 'bienvenida_mostrada' not in st.session_state:
    st.session_state.bienvenida_mostrada = False

# --- PANTALLA DE BIENVENIDA ANIMADA ---
if not st.session_state.bienvenida_mostrada:
    welcome_container = st.container()
    with welcome_container:
        st.markdown("""
            <div class="welcome-box">
                <h1 style='color: #1E88E5; font-size: 32px;'>¡Buenas rutas! 🌍</h1>
                <p style='color: #555; font-size: 18px;'>Abriendo CadeteApp Pro...</p>
                <div class="cadete-saludo">🛵🧑‍✈️👋</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(3.5) # Duración exacta de la animación del saludo
    st.session_state.bienvenida_mostrada = True
    st.rerun()

# --- CARGA DE FUNCIONES PERMANENTES ---
def cargar_historial_permanente():
    if os.path.exists(ARCHIVO_HISTORIAL):
        try: return pd.read_csv(ARCHIVO_HISTORIAL).to_dict(orient="records")
        except: return []
    return []

def guardar_viaje_permanente(nuevo_viaje):
    df_nuevo = pd.DataFrame([nuevo_viaje])
    if not os.path.exists(ARCHIVO_HISTORIAL): df_nuevo.to_csv(ARCHIVO_HISTORIAL, index=False)
    else: df_nuevo.to_csv(ARCHIVO_HISTORIAL, mode='a', header=False, index=False)

def borrar_historial_permanente():
    if os.path.exists(ARCHIVO_HISTORIAL): os.remove(ARCHIVO_HISTORIAL)

# --- CONTENIDO PRINCIPAL DE LA APP ---
st.title("🛵 CadeteApp Pro")
st.caption("Gestión inteligente de envíos urbanos")

tab1, tab2, tab3 = st.tabs(["🏍️ Calculador", "📊 Mi Historial", "⚙️ Tarifas"])

# --- PESTAÑA 1: CALCULADOR ---
with tab1:
    origen = st.text_input("📍 Origen", value="Belgrano 170")
    destino = st.text_input("🏁 Destino", placeholder="Ej: Castelli 1200")
    
    geolocator = Nominatim(user_agent="cadete_vt_pro_v6")
    ciudad = ", Venado Tuerto, Santa Fe, Argentina"

    if st.button("⚡ Calcular Tarifa"):
        if origen and destino:
            moto_placeholder = st.empty()
            moto_placeholder.markdown('<div class="moto-animation">🛵💨</div>', unsafe_allow_html=True)
            
            try:
                time.sleep(1.5)
                loc_o = geolocator.geocode(origen + ciudad, timeout=10)
                loc_d = geolocator.geocode(destino + ciudad, timeout=10)
                moto_placeholder.empty()

                if loc_o and loc_d:
                    dist = round(geodesic((loc_o.latitude, loc_o.longitude), (loc_d.latitude, loc_d.longitude)).kilometers * 1.25, 2)
                    if dist == 0: dist = 0.5
                    
                    t = st.session_state.tarifas
                    if dist <= t["km_min"]: precio = t["base"]
                    else: precio = t["base"] + ((dist - t["km_min"]) * t["km_extra"])
                    
                    st.session_state.viaje_actual = {
                        "origen": origen, "destino": destino, "distancia": dist, "precio": round(precio, 0)
                    }
                    
                    st.success(f"Cálculo listo")
                    c1, c2 = st.columns(2)
                    c1.metric("Distancia", f"{dist} KM")
                    c2.metric("Precio", f"${round(precio, 0):,.0f}")
                else:
                    st.error("No se encontraron las direcciones.")
            except Exception as e:
                st.error("Error en la conexión. Reintente.")

    if st.session_state.viaje_actual:
        st.divider()
        v = st.session_state.viaje_actual
        col_m1, col_m2 = st.columns(2)
        
        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={v['origen'].replace(' ', '+')}+Venado+Tuerto&destination={v['destino'].replace(' ', '+')}+Venado+Tuerto&travelmode=driving"
        col_m1.link_button("🗺️ Ver Mapa", maps_url)
        
        mp_url = "https://www.mercadopago.com.ar/home"
        col_m2.link_button("💳 Cobrar con MP", mp_url)
        
        if st.button("✅ Finalizar y Guardar Viaje", type="primary"):
            ahora_arg = datetime.now(ARG_TZ)
            nuevo_registro = {
                "Fecha": ahora_arg.strftime("%d/%m/%Y"),
                "Hora": ahora_arg.strftime("%H:%M:%S"),
                "Ruta": f"{v['origen']} -> {v['destino']}",
                "KM": v['distancia'],
                "Monto": v['precio']
            }
            guardar_viaje_permanente(nuevo_registro)
            st.session_state.viaje_actual = None
            st.balloons()
            st.info("Viaje guardado permanentemente.")
            time.sleep(1.5)
            st.rerun()

# --- PESTAÑA 2: HISTORIAL PERMANENTE ---
with tab2:
    st.subheader("Historial Acumulado")
    historial_lista = cargar_historial_permanente()
    
    if historial_lista:
        df = pd.DataFrame(historial_lista)
        hoy_arg = datetime.now(ARG_TZ).strftime("%d/%m/%Y")
        df_hoy = df[df["Fecha"] == hoy_arg]
        
        st.markdown(f"### 📅 Resumen de Hoy ({hoy_arg})")
        if not df_hoy.empty:
            total_ganado_hoy = df_hoy["Monto"].sum()
            total_viajes_hoy = len(df_hoy)
            c_h1, c_h2 = st.columns(2)
            c_h1.metric("Ganancia de Hoy", f"${total_ganado_hoy:,.0f}")
            c_h2.metric("Viajes de Hoy", total_viajes_hoy)
        else:
            st.info("Todavía no registraste viajes en el día de hoy.")
        
        st.divider()
        st.markdown("### 🗄️ Todos los viajes registrados")
        st.dataframe(df.iloc[::-1], use_container_width=True)
        
        if st.button("🗑️ Borrar Todo el Historial"):
            borrar_historial_permanente()
            st.success("Historial eliminado.")
            time.sleep(1)
            st.rerun()
    else:
        st.info("No hay ningún viaje registrado en el historial permanente.")

# --- PESTAÑA 3: CONFIGURAR TARIFAS ---
with tab3:
    st.subheader("Configuración de Precios")
    st.write("Modificá los valores y se aplicarán al instante en el calculador.")
    
    base = st.number_input("Valor Base ($)", value=st.session_state.tarifas["base"], step=100.0)
    dist_min = st.number_input("Distancia Mínima incluida (KM)", value=st.session_state.tarifas["km_min"], step=0.1)
    km_ex = st.number_input("Precio por KM extra ($)", value=st.session_state.tarifas["km_extra"], step=50.0)
    
    if st.button("💾 Guardar Nuevas Tarifas"):
        st.session_state.tarifas = {"base": base, "km_min": dist_min, "km_extra": km_ex}
        st.success("Tarifas de sesión actualizadas correctamente.")
