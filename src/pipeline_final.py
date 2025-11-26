import pandas as pd
import numpy as np
import os

# Rutas
PATH_KAGGLE = 'data/raw/PS_20174392719_1491204439457_log.csv'
PATH_CLIENTES = 'data/raw/clientes_maestros_pro.csv'
DIR_PROCESSED = 'data/processed/'

print("--- 🏭 INICIANDO GENERACIÓN DE MODELO ESTRELLA ---")

# 1. CARGAR DATOS
print("1. Cargando datos crudos...")
df_trx = pd.read_csv(PATH_KAGGLE)
df_cli = pd.read_csv(PATH_CLIENTES)

# ---------------------------------------------------------
# PREPARACIÓN DE LA TABLA DE HECHOS (FACT_TRANSACCIONES)
# ---------------------------------------------------------
print("2. Procesando Tabla de Hechos (Transacciones)...")

# Generamos Fechas (4 Años: 2020-2023)
fecha_inicio = pd.to_datetime("2020-01-01")
dias_random = np.random.randint(0, 1460, size=len(df_trx))
horas_step = pd.to_timedelta(df_trx['step'] % 24, unit='h')

# Creamos la fecha real
df_trx['Fecha'] = fecha_inicio + pd.to_timedelta(dias_random, unit='D') + horas_step

# Columnas derivadas de tiempo (útiles para PBI)
df_trx['Hora'] = df_trx['Fecha'].dt.hour
condiciones_hora = [
    (df_trx['Hora'].between(0, 6)),
    (df_trx['Hora'].between(7, 12)),
    (df_trx['Hora'].between(13, 18)),
    (df_trx['Hora'].between(19, 24))
]
opciones_hora = ['Madrugada', 'Mañana', 'Tarde', 'Noche']
df_trx['Momento_Dia'] = np.select(condiciones_hora, opciones_hora, default='Noche')

# Traducción y Limpieza
traduccion = {'PAYMENT': 'Pago', 'TRANSFER': 'Transferencia', 'CASH_OUT': 'Retiro', 'DEBIT': 'Débito', 'CASH_IN': 'Depósito'}
df_trx['Tipo_Operacion'] = df_trx['type'].replace(traduccion)
df_trx['Estado_Fraude'] = df_trx['isFraud'].map({0: 'Normal', 1: 'Fraude'})

# SELECCIÓN DE COLUMNAS FACT
# Importante: Mantenemos 'nameOrig' porque es la LLAVE para cruzar con clientes
cols_fact = ['Fecha', 'Hora', 'Momento_Dia', 'Tipo_Operacion', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'Estado_Fraude', 'isFraud', 'nameOrig']

# ---------------------------------------------------------
# PREPARACIÓN DE LA TABLA DIMENSIÓN (DIM_CLIENTES)
# ---------------------------------------------------------
print("3. Procesando Tabla de Dimensión (Clientes)...")
# La tabla de clientes ya viene casi lista del script anterior, 
# solo nos aseguramos de que los nombres de columnas sean bonitos.
# nameOrig en transacciones = cliente_id en clientes.

cols_dim = ['cliente_id', 'Rut', 'Banco', 'Region', 'Edad', 'Segmento_Edad']
df_cli_final = df_cli[cols_dim].copy()

# ---------------------------------------------------------
# EXPORTACIÓN
# ---------------------------------------------------------
os.makedirs(DIR_PROCESSED, exist_ok=True)

print("4. Exportando Modelo Estrella...")

# Exportamos FACT (Muestra grande)
path_fact = os.path.join(DIR_PROCESSED, 'Fact_Transacciones.csv')
df_trx[cols_fact].sample(min(1000000, len(df_trx)), random_state=42).to_csv(path_fact, index=False)
print(f"   -> Hechos: {path_fact}")

# Exportamos DIM (Todos los clientes que coincidan con la muestra o todos)
# Para este ejercicio exportamos todos los clientes generados para asegurar integridad referencial
path_dim = os.path.join(DIR_PROCESSED, 'Dim_Clientes.csv')
df_cli_final.to_csv(path_dim, index=False)
print(f"   -> Dimensión: {path_dim}")

print("✅ MODELO ESTRELLA GENERADO EXITOSAMENTE")