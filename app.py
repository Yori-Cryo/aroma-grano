import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="BizIntelligence Aroma & Grano", layout="wide")
st.title("📊 BI Dashboard: Aroma & Grano")

# --- CARGA PROFESIONAL ---
@st.cache_data
def cargar_inventario():
    # Usamos low_memory=False para archivos grandes (en este caso es pequeño pero es buena práctica)
    return pd.read_csv("ventas_pro.csv")

df = cargar_inventario()

# --- SONDEO INICIAL (Teoría en acción) ---
st.header("🔍 1. Sondeo de Categorías")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Productos Únicos", df['producto'].nunique())
    
with col2:
    st.write("Tipos de productos encontrados:")
    st.write(df['tipo'].unique())

with col3:
    st.write("Frecuencia de ventas por producto:")
    st.write(df['producto'].value_counts())
st.text_area("✍️ Tu explicación (Propias palabras, sin IA): Aquí básicamente estamos dando un primer vistazo a los datos. Usé Streamlit para armar 3 columnas y mostrar unas métricas rápidas: veo cuántos productos diferentes tenemos en el archivo, qué categorías hay y cuáles son los que más veces se han registrado. Es como un resumen táctico para entender con qué información estoy lidiando antes de meterle mano." , key="reflexion_paso_2")



st.divider()
st.header("🛠️ 2. Motor de Limpieza")

# PASO A: Eliminar Duplicados (Vimos el ID 2 y 10 repetidos en el CSV)
df = df.drop_duplicates(subset=['id'])

# PASO B: Corregir Tipos de Datos
# El CSV tiene el ID 12 con cantidad "1" entre comillas (texto). Lo forzamos a número.
df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')

# PASO C: Rellenar Nulos (NaN)
# Si no sabemos la cantidad, asumiremos que se vendió 1 unidad.
df['cantidad'] = df['cantidad'].fillna(1)

st.success("✅ Limpieza automátizada: Duplicados removidos, números corregidos y nulos rellenados.")
st.dataframe(df)
st.text_area("✍️ Tu explicación (Propias palabras, sin IA): Esta parte es súper importante porque los datos casi nunca vienen perfectos. Primero eliminé las filas que estaban repetidas basándome en el ID, porque me di cuenta de que había registros duplicados. Luego forcé la columna de cantidad a formato numérico (a veces el CSV lo lee como texto) y, finalmente, si a algún registro le faltaba la cantidad, le puse '1' por defecto para que no me dañe los cálculos más adelante. Con eso la tabla ya queda limpia. ", key="reflexion_paso_3")



st.divider()
st.header("✨ 3. Transformación de Reporte")

# Calculamos el subtotal primero
df['Ingreso_Bruto'] = df['precio'] * df['cantidad']

# CREAMOS UNA VISTA LIMPIA PARA EL REPORTE
# Renombramos y ordenamos de mayor ingreso a menor
reporte_ejecutivo = df.rename(columns={
    'id': 'ID Pedido',
    'producto': 'Producto',
    'Ingreso_Bruto': 'Venta Total ($)'
}).sort_values(by='Venta Total ($)', ascending=False)

st.write("Top de ventas del mes (Ordenado):")
st.dataframe(reporte_ejecutivo[['ID Pedido', 'Producto', 'Venta Total ($)']].head(10))
st.text_area("✍️ Tu explicación (Propias palabras, sin IA): Acá ya empezamos a sacar las cuentas de verdad. Multipliqué el precio por la cantidad para tener la plata real que entró (ingreso bruto). Después, en vez de dejar los nombres feos de las columnas, los renombré a cosas más claras como 'ID Pedido' o 'Venta Total'. Por último, ordené esa tabla de mayor a menor para que los mejores pedidos salgan de primeritos.", key="reflexion_paso_4")



st.sidebar.header("⚙️ Panel de Auditoría")

# Filtro multi-selección
ciudades_filtro = st.sidebar.multiselect(
    "Filtrar por Tipo:",
    options=df['tipo'].unique(),
    default=df['tipo'].unique()
)

# Filtro Slider
monto_min = st.sidebar.slider("Ver ventas superiores a ($):", 0, 100, 0)

# APLICACIÓN DE LÓGICA FILTRADO (AND)
# Que pertenezca al tipo seleccionado Y supere el monto mínimo
df_final = df[(df['tipo'].isin(ciudades_filtro)) & (df['Ingreso_Bruto'] >= monto_min)]

st.subheader("📋 Pedidos Filtrados")
st.table(df_final)
st.text_area("✍️ Tu explicación (Propias palabras, sin IA): Le metí un panel lateral interactivo con dos filtros: uno para poder chulear qué categorías quiero ver y una barrita (slider) para filtrar ventas que superen x cantidad de plata. Lo chévere aquí es que crucé las dos condiciones con un '&', así la tabla final solo me muestra las ventas que cumplan ambas cosas al mismo tiempo. Súper útil para buscar datos específicos rapidito.", key="reflexion_paso_5")



st.divider()
st.header("📈 4. Análisis Agregado")

# Agrupamos por tipo y sumamos ingresos
resumen = df.groupby('tipo')['Ingreso_Bruto'].agg(['sum', 'count', 'mean']).round(2)
st.write(resumen)

st.bar_chart(resumen['sum'])
st.text_area("✍️ Tu explicación (Propias palabras, sin IA): Para esta sección quería algo más visual y resumido. Lo que hice fue agrupar toda la información por 'tipo' de producto y de ahí saqué el total sumado, la cantidad de registros y el promedio de ventas. Ya con esa tabla armada, le pasé el total a un gráfico de barras para que sea evidente a ojo cuál categoría nos está dejando más ingresos.", key="reflexion_paso_6")



# Tabla de ejemplo de proveedores
proveedores = pd.DataFrame({
    'producto': ['Espresso', 'Latte', 'Capuccino', 'Muffin', 'Cold Brew', 'Pastel de Chocolate'],
    'Proveedor': ['Granos del Cauca', 'Lácteos Central', 'Lácteos Central', 'Trigo & Sal', 'Refrescantes S.A.', 'Delicias Doña Ana']
})

# Fusión (Merge)
df_maestro = pd.merge(df, proveedores, on='producto', how='left')

st.header("🏢 Contacto de Proveedores por Pedido")
st.dataframe(df_maestro[['id', 'producto', 'Proveedor']])
st.text_area("✍️ Tu explicación (Propias palabras, sin IA): Al final me armé una tablita chiquita a mano con los nombres cruzados de productos y sus respectivos proveedores. Usé un 'merge' (que es básicamente hacer un BuscarV de Excel pero en código) para unir nuestras ventas principales con esa tablita de proveedores usando el nombre del producto como conexión. Le puse tipo 'left' para que no se me pierdan registros de ventas si de casualidad a algún producto le falta el proveedor.", key="reflexion_paso_7")
