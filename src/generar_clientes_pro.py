import pandas as pd
from faker import Faker
import numpy as np
import os

# Configuración
fake = Faker('es_CL')
PATH_KAGGLE = 'data/raw/PS_20174392719_1491204439457_log.csv' # Tu archivo original
PATH_CLIENTES_OUT = 'data/raw/clientes_maestros_pro.csv' # El nuevo archivo

print("--- 1. GENERANDO MAESTRO DE CLIENTES ENRIQUECIDO ---")

# 1. Obtener IDs únicos de Kaggle para que el cruce sea perfecto
print("Leyendo IDs de transacciones...")
df_trx = pd.read_csv(PATH_KAGGLE, usecols=['nameOrig'])
unique_ids = df_trx['nameOrig'].unique()
total_clientes = len(unique_ids)
print(f"-> Clientes únicos detectados: {total_clientes:,}")

# 2. Configurar Datos Demográficos Realistas
print("Generando atributos (Bancos, Regiones, Edades)...")

# A) BANCOS (Con probabilidades de mercado)
bancos = ['Banco Falabella', 'Banco Santander', 'BancoEstado', 'Banco de Chile', 'BCI', 'Scotiabank', 'Itaú', 'Banco Bice']
prob_bancos = [0.15, 0.20, 0.30, 0.12, 0.10, 0.05, 0.05, 0.03]

# B) REGIONES (Lista oficial completa para el mapa)
regiones = [
    "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama", "Coquimbo", 
    "Valparaíso", "Metropolitana", "O'Higgins", "Maule", "Ñuble", "Biobío", 
    "Araucanía", "Los Ríos", "Los Lagos", "Aysén", "Magallanes"
]
# Pesos: Más gente en Santiago (Metropolitana)
prob_regiones = [0.01, 0.02, 0.03, 0.02, 0.04, 0.10, 0.45, 0.05, 0.06, 0.03, 0.08, 0.04, 0.02, 0.03, 0.01, 0.01]

# C) GENERACIÓN MASIVA (Usando Numpy para velocidad)
df_clientes = pd.DataFrame({'cliente_id': unique_ids})

# Asignamos aleatoriamente
df_clientes['Banco'] = np.random.choice(bancos, size=total_clientes, p=prob_bancos)
df_clientes['Region'] = np.random.choice(regiones, size=total_clientes, p=prob_regiones)
df_clientes['Edad'] = np.random.randint(18, 85, size=total_clientes) # Entre 18 y 85 años

# Segmentos de Edad
condiciones = [
    (df_clientes['Edad'] <= 25),
    (df_clientes['Edad'] <= 40),
    (df_clientes['Edad'] <= 60),
    (df_clientes['Edad'] > 60)
]
opciones = ['Joven (18-25)', 'Adulto Joven (26-40)', 'Adulto (41-60)', 'Senior (+60)']
df_clientes['Segmento_Edad'] = np.select(condiciones, opciones,default='Desconocido')


# Datos Faker (Nombre y Rut - Esto demora más, lo haremos solo para una muestra si quieres velocidad)
# Para este ejercicio, generaremos RUTs falsos rápidos vectorizados para no esperar horas
print("Generando RUTs simulados...")
df_clientes['Rut'] = np.random.randint(5000000, 25000000, size=total_clientes).astype(str) + '-' + np.random.choice(['0','1','2','3','4','5','6','7','8','9','K'], size=total_clientes)

# 3. GUARDAR
print(f"Guardando {PATH_CLIENTES_OUT}...")
df_clientes.to_csv(PATH_CLIENTES_OUT, index=False)
print("✅ MAESTRO DE CLIENTES LISTO.")