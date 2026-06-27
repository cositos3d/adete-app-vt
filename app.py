import streamlit as st
from geopy.geocoders import ArcGIS
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

# --- TRUCO CLAVE: Forzar idioma Español ---
st.markdown("<html lang='es'></html>", unsafe_allow_html=True)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&display=swap');
    
    body, .main, h1, p, .stButton {
        font-family: 'Fredoka', sans-serif !important;
    }
    
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; font-weight: 600; font-size: 16px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    @keyframes avanzar-hacia-izquierda {
        0% { transform: translateX(120%); }
        100% { transform: translateX(-120%); }
    }
    
    .welcome-box { 
        text-align: center; 
        padding: 40px; 
        background: white; 
        border-radius: 24px; 
        box-shadow: 0 6px 20px rgba(0,0,0,0.08); 
        overflow: hidden;
        position: relative;
    }
    
    .animacion-contenedor {
        width: 100%;
        display: inline-block;
        animation: avanzar-hacia-izquierda 3.5s infinite linear;
    }
    
    .titulo-bienvenida {
        color: #1E88E5; 
        font-size: 34px; 
        font-weight: 600;
        white-space: nowrap;
        display: inline-block;
    }
    
    .moto-bici-saludo { 
        font-size: 55px; 
        margin-top: 15px;
        white-space: nowrap;
        display: block;
    }
    
    .moto-animation { 
        font-size: 50px; 
        display: inline-block;
        animation: avanzar-hacia-izquierda 2s infinite linear; 
        width: 100%; 
        text-align: center; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- VALORES POR DEFECTO GENERALES ---
TARIFAS_DEFECTO = {"base": 3000.0, "km_min": 1.5, "km_extra": 1000.0}

if 'viaje_actual' not in st.session_state:
    st.session_state.viaje_actual = None

if 'bienvenida_mostrada' not in st.session_state:
    st.session_state.bienvenida_mostrada = False

# --- PANTALLA DE BIENVENIDA ANIMADA ---
if not st.session_state.bienvenida_mostrada:
    welcome_container = st.container()
    with welcome_container:
        st.markdown("""
            <div class="welcome-box">
                <div class="animacion-contenedor">
                    <div class="titulo-bienvenida">Bienvenido a CadeteApp Pro</div>
                    <div class="moto-bici-saludo">🛵..🚲💨</div>
                </div>
                <p style='color: #666; font-size: 16px; font-weight: 400; margin-top: 25px;'>¡Buenas rutas para hoy! 🌍</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(3.5)
    st.session_state.bienvenida_mostrada = True
    st.rerun()

# --- CONTROL DE ACCESO EXCLUSIVO ---
st.sidebar.markdown("### 👤 Acceso Cadetes")

CADETES_AUTORIZADOS = ["Seleccionar...", "Sergio01", "SaraCarolina02", "LucasAlexis03", "Tomyp04", "Leocalderon05"]

cadete_seleccionado = st.sidebar.selectbox(
    "Seleccioná tu usuario de prueba:",
    options=CADETES_AUTORIZADOS
)

if cadete_seleccionado != "Seleccionar...":
    usuario_clean = cadete_seleccionado.lower()
    ARCHIVO_HISTORIAL = f"historial_{usuario_clean}.csv"
    ARCHIVO_TARIFAS = f"tarifas_{usuario_clean}.csv"
else:
    ARCHIVO_HISTORIAL = None
    ARCHIVO_TARIFAS = None

# --- FUNCIONES DE PERSISTENCIA DE TARIFAS ---
def cargar_tarifas_usuario():
    if ARCHIVO_TARIFAS and os.path.exists(ARCHIVO_TARIFAS):
        try:
            df = pd.read_csv(ARCHIVO_TARIFAS)
            if not df.empty:
                return {
                    "base": float(df.iloc[0]["base"]),
                    "km_min": float(df.iloc[0]["km_min"]),
                    "km_extra": float(df.iloc[0]["km_extra"])
                }
        except:
            return TARIFAS_DEFECTO
    return TARIFAS_DEFECTO

def guardar_tarifas_usuario(nuevas_tarifas):
    if ARCHIVO_TARIFAS:
        df = pd.DataFrame([nuevas_tarifas])
        df.to_csv(ARCHIVO_TARIFAS, index=False)

if cadete_seleccionado != "Seleccionar...":
    if 'tarifas' not in st.session_state or st.session_state.get('usuario_actual') != cadete_seleccionado:
        st.session_state.tarifas = cargar_tarifas_usuario()
        st.session_state.usuario_actual = cadete_seleccionado
else:
    st.session_state.tarifas = TARIFAS_DEFECTO

# --- CARGA DE FUNCIONES DE HISTORIAL ---
def cargar_historial_permanente():
    if ARCHIVO_HISTORIAL and os.path.exists(ARCHIVO_HISTORIAL):
        try: return pd.read_csv(ARCHIVO_HISTORIAL).to_dict(orient="records")
        except: return []
    return []

def guardar_viaje_permanente(nuevo_viaje):
    if ARCHIVO_HISTORIAL:
        df_nuevo = pd.DataFrame([nuevo_viaje])
        if not os.path.exists(ARCHIVO_HISTORIAL): df_nuevo.to_csv(ARCHIVO_HISTORIAL, index=False)
        else: df_nuevo.to_csv(ARCHIVO_HISTORIAL, mode='a', header=False, index=False)

def borrar_historial_permanente():
    if ARCHIVO_HISTORIAL and os.path.exists(ARCHIVO_HISTORIAL): os.remove(ARCHIVO_HISTORIAL)

# --- CONTENIDO PRINCIPAL DE LA APP ---
st.title("🛵 CadeteApp Pro")
st.caption("Gestión inteligente de envíos urbanos")

if cadete_seleccionado == "Seleccionar...":
    st.info("👋 ¡Hola! Para empezar a cotizar y registrar tus viajes de hoy, seleccioná tu código de usuario en el menú de la izquierda.")
else:
    st.sidebar.success(f"Sesión activa: {cadete_seleccionado}")
    
    tab1, tab2, tab3 = st.tabs(["🏍️ Calculador", "📊 Mi Historial", "⚙️ Tarifas"])

    # --- PESTAÑA 1: CALCULADOR ---
    with tab1:
        origen = st.text_input("📍 Origen", placeholder="Ej: Belgrano 170")
        destino = st.text_input("🏁 Destino", placeholder="Ej: Castelli 1200")
        
        # Cambiamos al motor de mapas de ArcGIS (Mucho más rápido y sin bloqueos corporativos)
        geolocator = ArcGIS(timeout=10)
        ciudad = ", Venado Tuerto, Santa Fe, Argentina"

        if st.button("⚡ Calcular Tarifa"):
            if origen and destino:
                moto_placeholder = st.empty()
                moto_placeholder.markdown('<div class="moto-animation">🛵💨</div>', unsafe_allow_html=True)
                
                try:
                    time.sleep(0.5)
                    loc_o = geolocator.geocode(origen + ciudad)
                    loc_d = geolocator.geocode(destino + ciudad)
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
                        st.error("No se encontraron las direcciones en el mapa. Probá agregando la altura exacta.")
                except Exception as e:
                    moto_placeholder.empty()
                    st.error("El servidor de mapas tarda en responder. Esperá 2 segundos y volvé a tocar el botón.")

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
                st.info("Viaje guardado en tu historial.")
                time.sleep(1.5)
                st.rerun()

    # --- PESTAÑA 2: HISTORIAL PERMANENTE ---
    with tab2:
        st.subheader("Historial Acumulado")
        st.caption(f"Historial personal de: **{cadete_seleccionado}**")
        
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
            st.markdown("### 🗄️ Todos tus viajes registrados")
            st.dataframe(df.iloc[::-1], use_container_width=True)
            
            if st.button("🗑️ Borrar mi Historial"):
                borrar_historial_permanente()
                st.success("Tu historial ha sido eliminado.")
                time.sleep(1)
                st.rerun()
        else:
            st.info("No hay ningún viaje registrado en este historial personal.")

    # --- PESTAÑA 3: CONFIGURAR TARIFAS ---
    with tab3:
        st.subheader("Configuración de Precios")
        st.write("Modificá tus valores personales. Se guardarán para tus próximos inicios.")
        
        base = st.number_input("Valor Base ($)", value=st.session_state.tarifas["base"], step=100.0)
        dist_min = st.number_input("Distancia Mínima incluida (KM)", value=st.session_state.tarifas["km_min"], step=0.1)
        km_ex = st.number_input("Precio por KM extra ($)", value=st.session_state.tarifas["km_extra"], step=50.0)
        
        if st.button("💾 Guardar mis Tarifas Permanentes"):
            nuevas_t = {"base": base, "km_min": dist_min, "km_extra": km_ex}
            st.session_state.tarifas = nuevas_t
            guardar_tarifas_usuario(nuevas_t)
            st.success("¡Tus tarifas personales se guardaron de forma permanente!")
            time.sleep(1)
            st.rerun()
