import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Configuración estilo celular
st.set_page_config(page_title="Cadetería Venado Tuerto", page_icon="🛵", layout="centered")

st.title("🛵 CadeteApp VT")
st.caption("Calculador automático de tarifas para Venado Tuerto")

# --- CONFIGURACIÓN DE TARIFAS ---
VALOR_BASE = 3000.0
DISTANCIA_BASE_KM = 1.5
PRECIO_POR_KM_EXTRA = 1000.0  # $100 cada 0.1km = $1000 por 1km

# Forzamos un "User Agent" único para que el mapa no nos bloquee
geolocator = Nominatim(user_agent="cadete_app_venado_tuerto_v2_99")

st.markdown("### 📍 Direcciones del Viaje")

origen_input = st.text_input("1. Dirección de SALIDA (Origen)", value="San Martin y Belgrano")
destino_input = st.text_input("2. Dirección de ENTREGA (Destino)", placeholder="Ej: Castelli 1200")

ciudad_filtro = ", Venado Tuerto, Santa Fe, Argentina"

if st.button("⚡ Calcular Viaje", use_container_width=True):
    if origen_input and destino_input:
        with st.spinner("Buscando direcciones..."):
            try:
                # Buscamos coordenadas en Venado Tuerto
                loc_origen = geolocator.geocode(origen_input + ciudad_filtro, timeout=10)
                loc_destino = geolocator.geocode(destino_input + ciudad_filtro, timeout=10)
                
                if loc_origen and loc_destino:
                    coord_origen = (loc_origen.latitude, loc_origen.longitude)
                    coord_destino = (loc_destino.latitude, loc_destino.longitude)
                    
                    # Calculamos distancia con curva estimada por calles (x1.25)
                    distancia_linea_recta = geodesic(coord_origen, coord_destino).kilometers
                    distancia_estimada = round(distancia_linea_recta * 1.25, 2)
                    
                    # Si por error da 0, le ponemos un mínimo
                    if distancia_estimada == 0:
                        distancia_estimada = 0.5
                    
                    # --- LÓGICA DE TARIFAS ---
                    if distancia_estimada <= DISTANCIA_BASE_KM:
                        costo_final = VALOR_BASE
                    else:
                        km_excedentes = distancia_estimada - DISTANCIA_BASE_KM
                        costo_final = VALOR_BASE + (km_excedentes * PRECIO_POR_KM_EXTRA)
                    
                    costo_final = round(costo_final, 0)

                    # --- MOSTRAR RESULTADOS ---
                    st.success("¡Cálculo exitoso!")
                    
                    col1, col2 = st.columns(2)
                    col1.metric(label="Distancia Estimada", value=f"{distancia_estimada} KM")
                    col2.metric(label="PRECIO A COBRAR", value=f"${costo_final:,.0f}")
                    
                    st.divider()
                    
                    # Botón para abrir Google Maps en el celular
                    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origen_input.replace(' ', '+')}+Venado+Tuerto&destination={destino_input.replace(' ', '+')}+Venado+Tuerto&travelmode=driving"
                    st.link_button("🚀 Abrir ruta en Google Maps", maps_url, use_container_width=True)
                    
                else:
                    st.error("❌ No encontramos las calles en Venado Tuerto. Revisá si están bien escritas (ej: 'Castelli 1200' o 'Mitre y Belgrano').")
            
            except Exception as e:
                # PLAN B: Si el mapa de fondo falla, le damos un botón directo a Google Maps para no trabar el trabajo
                st.warning("⚠️ El buscador automático está saturado, pero podés ver la ruta y cobrar de forma manual:")
                maps_url_fallback = f"https://www.google.com/maps/dir/?api=1&origin={origen_input.replace(' ', '+')}+Venado+Tuerto&destination={destino_input.replace(' ', '+')}+Venado+Tuerto&travelmode=driving"
                st.link_button("🗺️ Abrir en Google Maps para ver Distancia", maps_url_fallback, use_container_width=True)
    else:
        st.warning("Por favor, completa ambos campos.")
