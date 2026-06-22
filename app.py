import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Configuración de pantalla modo celular
st.set_page_config(page_title="Cadetería Venado Tuerto", page_icon="🛵", layout="centered")

st.title("🛵 CadeteApp VT")
st.caption("Calculador automático de tarifas para Venado Tuerto")

# --- LÓGICA DE TARIFAS ---
VALOR_BASE = 3000.0
DISTANCIA_BASE_KM = 1.5
PRECIO_POR_KM_EXTRA = 1000.0 # $100 cada 0.1km = $1000 por 1km

# Inicializamos el buscador de direcciones (Geolocalizador)
geolocator = Nominatim(user_agent="cadete_app_vt")

st.markdown("### 📍 Direcciones del Viaje")

# Inputs de texto rápido
origen_input = st.text_input("1. Dirección de SALIDA (Origen)", value="San Martín y Belgrano")
destino_input = st.text_input("2. Dirección de ENTREGA (Destino)", placeholder="Ej: Castelli 1200")

# Forzamos a que busque dentro de Venado Tuerto para evitar errores
ciudad_filtro = ", Venado Tuerto, Santa Fe, Argentina"

if st.button("⚡ Calcular Viaje", use_container_width=True):
    if origen_input and destino_input:
        with st.spinner("Calculando distancia óptima..."):
            try:
                # Buscamos las coordenadas reales en VT
                loc_origen = geolocator.geocode(origen_input + city_filter)
                loc_destino = geolocator.geocode(destino_input + city_filter)
                
                if loc_origen and loc_destino:
                    # Calculamos los KM de distancia
                    coord_origen = (loc_origen.latitude, loc_origen.longitude)
                    coord_destino = (loc_destino.latitude, loc_destino.longitude)
                    
                    # Distancia estimada aproximada por calles (usamos un multiplicador de 1.3 para aproximar el recorrido real y no en línea recta)
                    distancia_linea_recta = geodesic(coord_origen, coord_destino).kilometers
                    distancia_estimada = round(distancia_linea_recta * 1.25, 2) 
                    
                    # --- CÁLCULO DE COSTO ---
                    if distancia_estimada <= DISTANCIA_BASE_KM:
                        costo_final = VALOR_BASE
                    else:
                        km_excedentes = distancia_estimada - DISTANCIA_BASE_KM
                        costo_final = VALOR_BASE + (km_excedentes * PRECIO_POR_KM_EXTRA)
                    
                    # Redondeamos para no tener centavos feos
                    costo_final = round(costo_final, 0)

                    # --- MOSTRAR RESULTADOS ---
                    st.success("¡Cálculo exitoso!")
                    
                    col1, col2 = st.columns(2)
                    col1.metric(label="Distancia Estimada", value=f"{distancia_estimada} KM")
                    col2.metric(label="PRECIO A COBRAR", value=f"${costo_final:,.0f}")
                    
                    st.divider()
                    
                    # Link directo para abrir en el Google Maps del celu del cadete
                    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origen_input.replace(' ', '+')}+Venado+Tuerto&destination={destino_input.replace(' ', '+')}+Venado+Tuerto&travelmode=driving"
                    st.link_button("🚀 Abrir ruta en Google Maps", maps_url, use_container_width=True)
                    
                else:
                    st.error("No se pudo encontrar alguna de las direcciones. Asegurate de escribir bien la calle y altura.")
            except Exception as e:
                st.error("Hubo un problema con el mapa. Intentá de nuevo.")
    else:
        st.warning("Por favor, completa ambos campos.")
