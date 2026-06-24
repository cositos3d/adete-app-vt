import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CadeteApp Pro VT", page_icon="🛵", layout="centered")

# Estilo personalizado para mejorar la visual en móviles
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .css-10trblm { font-size: 20px; color: #1E88E5; }
    /* Animación de la motito */
    @keyframes move-moto {
        0% { transform: translateX(-100px); }
        100% { transform: translateX(300px); }
    }
    .moto-animation { font-size: 50px; animation: move-moto 2s infinite linear; width: 100%; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE MEMORIA (Session State) ---
if 'tarifas' not in st.session_state:
    st.session_state.tarifas = {"base": 3000.0, "km_min": 1.5, "km_extra": 1000.0}

if 'historial' not in st.session_state:
    st.session_state.historial = []

if 'viaje_actual' not in st.session_state:
    st.session_state.viaje_actual = None

# --- TÍTULO PRINCIPAL ---
st.title("🛵 CadeteApp Pro")
st.caption("Gestión inteligente de envíos para Venado Tuerto")

# --- NAVEGACIÓN POR PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏍️ Calculador", "📊 Mi Historial", "⚙️ Tarifas"])

# --- PESTAÑA 1: CALCULADOR ---
with tab1:
    origen = st.text_input("📍 Origen", value="San Martin y Belgrano")
    destino = st.text_input("🏁 Destino", placeholder="Ej: Castelli 1200")
    
    geolocator = Nominatim(user_agent="cadete_vt_pro_v3")
    ciudad = ", Venado Tuerto, Santa Fe, Argentina"

    if st.button("⚡ Calcular Tarifa"):
        if origen and destino:
            # Espacio para la animación
            moto_placeholder = st.empty()
            moto_placeholder.markdown('<div class="moto-animation">🛵💨</div>', unsafe_allow_html=True)
            
            try:
                # Simulación de tiempo de carga para ver la animación
                time.sleep(1.5)
                
                loc_o = geolocator.geocode(origen + ciudad, timeout=10)
                loc_d = geolocator.geocode(destino + ciudad, timeout=10)
                
                moto_placeholder.empty() # Quitamos la animación

                if loc_o and loc_d:
                    dist = round(geodesic((loc_o.latitude, loc_o.longitude), (loc_d.latitude, loc_d.longitude)).kilometers * 1.25, 2)
                    if dist == 0: dist = 0.5
                    
                    # Cálculo basado en la pestaña de tarifas
                    t = st.session_state.tarifas
                    if dist <= t["km_min"]:
                        precio = t["base"]
                    else:
                        precio = t["base"] + ((dist - t["km_min"]) * t["km_extra"])
                    
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

    # --- FLUJO DE VIAJE ---
    if st.session_state.viaje_actual:
        st.divider()
        v = st.session_state.viaje_actual
        
        col_m1, col_m2 = st.columns(2)
        
        # Botón Google Maps
        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={v['origen'].replace(' ', '+')}+Venado+Tuerto&destination={v['destino'].replace(' ', '+')}+Venado+Tuerto&travelmode=driving"
        col_m1.link_button("🗺️ Ver Mapa", maps_url)
        
        # Botón Mercado Pago (Link genérico de la App)
        mp_url = "https://www.mercadopago.com.ar/home" # Aquí podrías poner tu propio link de cobro
        col_m2.link_button("💳 Cobrar con MP", mp_url)
        
        if st.button("✅ Finalizar y Guardar Viaje", type="primary"):
            nuevo_registro = {
                "Fecha": datetime.now().strftime("%H:%M:%S"),
                "Ruta": f"{v['origen']} -> {v['destino']}",
                "KM": v['distancia'],
                "Monto": v['precio']
            }
            st.session_state.historial.append(nuevo_registro)
            st.session_state.viaje_actual = None
            st.balloons()
            st.info("Viaje guardado en el historial.")
            time.sleep(2)
            st.rerun()

# --- PESTAÑA 2: HISTORIAL ---
with tab2:
    st.subheader("Resumen del Día")
    if st.session_state.historial:
        df = pd.DataFrame(st.session_state.historial)
        
        total_ganado = df["Monto"].sum()
        total_viajes = len(df)
        
        c_h1, c_h2 = st.columns(2)
        c_h1.metric("Total Ganado", f"${total_ganado:,.0f}")
        c_h2.metric("Viajes Hechos", total_viajes)
        
        st.divider()
        st.write("Detalle de viajes:")
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Borrar Historial"):
            st.session_state.historial = []
            st.rerun()
    else:
        st.info("Todavía no hay viajes registrados hoy.")

# --- PESTAÑA 3: CONFIGURAR TARIFAS ---
with tab3:
    st.subheader("Configuración de Precios")
    st.write("Modificá los valores y se aplicarán al instante en el calculador.")
    
    # Inputs vinculados directamente a la memoria de la app
    base = st.number_input("Valor Base ($)", value=st.session_state.tarifas["base"], step=100.0)
    dist_min = st.number_input("Distancia Mínima incluida (KM)", value=st.session_state.tarifas["km_min"], step=0.1)
    km_ex = st.number_input("Precio por KM extra ($)", value=st.session_state.tarifas["km_extra"], step=50.0)
    
    if st.button("💾 Guardar Nuevas Tarifas"):
        st.session_state.tarifas = {
            "base": base,
            "km_min": dist_min,
            "km_extra": km_ex
        }
        st.success("Tarifas actualizadas correctamente.")
