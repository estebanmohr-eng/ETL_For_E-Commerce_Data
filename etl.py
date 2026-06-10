# Copyright (c) 2026 Esteban Mohr (estebanmohr-eng)
# SPDX-License-Identifier: MIT

import pandas as pd
import glob
import os

#################################################################################
#                                       EXTRACT
#################################################################################

###########################################
# Extract: Lectura de data de archivos CSV
###########################################

# Verificar que existen los archivos CSV descargados
archivos = glob.glob('data/ecommerce_*.csv')
if not archivos:
    print("No se encontraron los archivos. Asegurate de descargarlos en la carpeta data/")
    print("Deberías tener: ecommerce_orders.csv, ecommerce_customers.csv, etc.")
else:
    print(f"Archivos encontrados: {len(archivos)}")
    for f in sorted(archivos):
        print(f"  - {os.path.basename(f)}")

# Cargar los CSVs principales
df_orders = pd.read_csv('data/ecommerce_orders.csv')
df_order_items = pd.read_csv('data/ecommerce_order_items.csv')
df_customers = pd.read_csv('data/ecommerce_customers.csv')
df_products = pd.read_csv('data/ecommerce_products.csv')
dataframes = [(df_orders,'orders'),(df_order_items,'order items'),(df_customers,'customers'),(df_products,'products')]

for dataframe in dataframes:
    df,name = dataframe
    if df.empty:
        raise ValueError(f"Error: El dataframe {name} no contiene data, revisar el archivo csv")


###########################################
# Extract: Explorar data extraida
###########################################

# Explorar
print(f"\n  Resumen:")
print(f"Orders: {len(df_orders)} filas, {len(df_orders.columns)} columnas")
print(f"Order Items: {len(df_order_items)} filas, {len(df_order_items.columns)} columnas")
print(f"Customers: {len(df_customers)} filas, {len(df_customers.columns)} columnas")
print(f"Products: {len(df_products)} filas, {len(df_products.columns)} columnas")

print("\n  Primeras filas de orders:")
print(df_orders.head())
print("\n  Info de orders:")
print(df_orders.info())
print("\n Distribución de orders")
print(df_orders.describe().T)

print("\n  Primeras filas de order items:")
print(df_order_items.head())
print("\n  Info de order items:")
print(df_order_items.info())
print("\n Distribución de items")
print(df_order_items.describe().T)

print("\n  Primeras filas de customers:")
print(df_customers.head())
print("\n  Info de customers:")
print(df_customers.info())
print("\n Distribución de customers")
print(df_customers.describe().T)

print("\n  Primeras filas de products:")
print(df_products.head())
print("\n  Info de products:")
print(df_products.info())
print("\n Distribución de products")
print(df_products.describe().T)

#################################################################################
#                                       TRANSFORM
#################################################################################

###########################################
# Transform: Manejo de valores nulos
###########################################

#Conteo de valores nulos por dataframe y por fila
orders_null_count = df_orders.isnull().sum()
order_items_null_count = df_order_items.isnull().sum()
customers_null_count = df_customers.isnull().sum()
products_null_count = df_products.isnull().sum()

orders_null_percent = round( (orders_null_count / df_orders.shape[0]) * 100 ,2)
order_items_null_percent = round( (order_items_null_count / df_order_items.shape[0]) * 100 ,2)
customers_null_percent = round( (customers_null_count / df_customers.shape[0]) *100 ,2)
products_null_percent = round( (products_null_count / df_products.shape[0]) * 100 ,2)

orders_null_stats = pd.DataFrame({'Null_Count': orders_null_count , 'Null_percent': orders_null_percent})
order_items_null_stats = pd.DataFrame({'Null_Count': order_items_null_count , 'Null_percent': order_items_null_percent})
customers_null_stats = pd.DataFrame({'Null_Count': customers_null_count , 'Null_percent': customers_null_percent})
products_null_stats = pd.DataFrame({'Null_Count': products_null_count , 'Null_percent': products_null_percent})

print("------------------------------------------\n")
print("\n Valores nulos de orders:")
print(orders_null_stats)
print("\n Valores nulos de order_items:")
print(order_items_null_stats)
print("\n Valores nulos de customers:")
print(customers_null_stats)
print("\n Valores nulos de products:")
print(products_null_stats)

# A continuación se detalla como se manejarán los valores nulos según la criticidad de las filas.
# Para decidir la criticidad de las filas se consideran los objetivos del análisis a realizar.
# Se desea responder a las siguientes preguntas de negocio:
# 1) ¿Quienes son los 5 clientes que mas gastan?
# 2) ¿Cuál es el producto mas vendido? (por cantidad)
# 3) ¿Cómo evolucionaron las ventas mes a mes?

#Conclusiones de análisis de valores nulos:
# Orders:
# Columnas no críticas (se rellenaran con 0 o ""): order_number, discount_percent, shipping_cost, ,tax_amount, payment_method, shipping_method, promotion_id, notes, status, subtotal
# Columnas críticas (se eliminará fila): order_id, customer_id, order_date, total_amount
#
# Order Items:
# Columnas no críticas: unit_price, quantity, subtotal (estas columnas se puede calcular con los datos de otras columnas, si no es posible hacer el cálculo se considera como crítico, en esta sección se cambiarán por cero y se revisará en limpieza posterior)
# Columnas críticas (se eliminará fila): order_item_id, order_id, product_id,
#
# Customers:
# Columnas no críticas (se rellenaran con 0 o ""): first_name, last_name,email, phone, birth_date, city, country, postal_code, segment, registration_date, last_login
# Columnas críticas (se eliminará fila): customer_id
#
# Products:
# Columnas no críticas (se rellenaran con 0 o ""): sku,product_name, description, category_id, brand_id, supplier_id, cost, weight_kg, is_active, created_at, updated_at
# Columnas críticas (se eliminará fila): product_id, price

# Filas críticas
orders_critical_rows = ['order_id','customer_id','order_date','total_amount']
order_items_critical_rows = ['order_item_id','order_id','product_id']
customers_critical_rows = ['customer_id']
products_critical_rows = ['product_id','price']

# Filas no críticas (una lista para filas string y otra para filas numéricas)
orders_non_critical_str_rows = ['order_number', 'payment_method', 'shipping_method','notes','status']
orders_non_critical_num_rows = ['discount_percent','shipping_cost','tax_amount','promotion_id','subtotal']

order_items_non_critical_num_rows = ['unit_price','quantity','subtotal']

customers_non_critical_str_rows = ['first_name','last_name','email','phone','birth_date','city','country','segment','registration_date','last_login']
customers_non_critical_num_rows = ['postal_code','accepts_marketing']
customers_non_critical_bool_rows = ['is_verified']

products_non_critical_str_rows = ['sku','product_name','description','created_at','updated_at']
products_non_critical_num_rows = ['category_id','brand_id','supplier_id','cost','weight_kg']
products_non_critical_bool_rows = ['is_active']

# Eliminar donde hay nulos en columnas críticas
df_orders_clean_null = df_orders.dropna(subset=orders_critical_rows)
df_order_items_clean_null = df_order_items.dropna(subset=order_items_critical_rows)
df_customers_clean_null = df_customers.dropna(subset=customers_critical_rows)
df_products_clean_null = df_products.dropna(subset=products_critical_rows)


# Rellenar las filas no críticas con 0 en filas numéricas, "" en filas de strings y False en filas booleanas
df_orders_clean_null[orders_non_critical_str_rows] = df_orders_clean_null[orders_non_critical_str_rows].fillna("")
df_orders_clean_null[orders_non_critical_num_rows] = df_orders_clean_null[orders_non_critical_num_rows].fillna(0)

df_order_items_clean_null[order_items_non_critical_num_rows] = df_order_items_clean_null[order_items_non_critical_num_rows].fillna(0)

df_customers_clean_null[customers_non_critical_str_rows] = df_customers_clean_null[customers_non_critical_str_rows].fillna("")
df_customers_clean_null[customers_non_critical_num_rows] = df_customers_clean_null[customers_non_critical_num_rows].fillna(0)
df_customers_clean_null[customers_non_critical_bool_rows] = df_customers_clean_null[customers_non_critical_bool_rows].fillna(False)

df_products_clean_null[products_non_critical_str_rows] = df_products_clean_null[products_non_critical_str_rows].fillna("")
df_products_clean_null[products_non_critical_num_rows] = df_products_clean_null[products_non_critical_num_rows].fillna(0)
df_products_clean_null[products_non_critical_bool_rows] = df_products_clean_null[products_non_critical_bool_rows].fillna(False)

#Imprimir cuantas filas se eliminaron por dataset
orders_rows_erased = df_orders.shape[0] - df_orders_clean_null.shape[0]
order_items_rows_erased = df_order_items.shape[0] - df_order_items_clean_null.shape[0]
customers_rows_erased = df_customers.shape[0] - df_customers_clean_null.shape[0]
products_rows_erased = df_products.shape[0] - df_products_clean_null.shape[0]

print(f"\n  Filas eliminadas para tratamiento de nulos:")
print(f"Orders: {orders_rows_erased} filas")
print(f"Order Items: {order_items_rows_erased} filas")
print(f"Customers: {customers_rows_erased} filas")
print(f"Products: {products_rows_erased} filas")

print(f'\nValores nulos post limpieza, si se tienen aun nulos se debe realizar alguna corrección:')
print("Nulos de Orders:")
print(df_orders_clean_null.isnull().sum())
print("Nulos de Order Items:")
print(df_order_items_clean_null.isnull().sum())
print("Nulos de Customers:")
print(df_customers_clean_null.isnull().sum())
print("Nulos de Products:")
print(df_products_clean_null.isnull().sum())

###########################################
# Transform: Manejo de valores duplicados
###########################################

#Conteo de valores duplicados por dataframe (considerando columnas críticas)
orders_dupl_count = df_orders_clean_null.duplicated(subset = orders_critical_rows).sum()
order_items_dupl_count = df_order_items_clean_null.duplicated(subset = order_items_critical_rows).sum()
customers_dupl_count = df_customers_clean_null.duplicated(subset = customers_critical_rows).sum()
products_dupl_count = df_products_clean_null.duplicated(subset = products_critical_rows).sum()

orders_dupl_percent_orig = round( (orders_dupl_count / df_orders.shape[0]) * 100 ,2)
order_items_dupl_percent_orig = round( (order_items_dupl_count / df_order_items.shape[0]) * 100 ,2)
customers_dupl_percent_orig = round( (customers_dupl_count / df_customers.shape[0]) *100 ,2)
products_dupl_percent_orig = round( (products_dupl_count / df_products.shape[0]) * 100 ,2)

orders_dupl_percent_new = round( (orders_dupl_count / df_orders_clean_null.shape[0]) * 100 ,2)
order_items_dupl_percent_new = round( (order_items_dupl_count / df_order_items_clean_null.shape[0]) * 100 ,2)
customers_dupl_percent_new = round( (customers_dupl_count / df_customers_clean_null.shape[0]) *100 ,2)
products_dupl_percent_new = round( (products_dupl_count / df_products_clean_null.shape[0]) * 100 ,2)

print("------------------------------------------")
print("\nValores duplicados de orders:")
print(f"  Duplicados:                                   {orders_dupl_count}")
print(f"  % sobre dataframe original:                   {orders_dupl_percent_orig}%")
print(f"  % sobre dataframe con nulos eliminados:       {orders_dupl_percent_new}%")

print("\nValores duplicados de order_items:")
print(f"  Duplicados:                                   {order_items_dupl_count}")
print(f"  % sobre dataframe original:                   {order_items_dupl_percent_orig}%")
print(f"  % sobre dataframe con nulos eliminados:       {order_items_dupl_percent_new}%")

print("\nValores duplicados de customers:")
print(f"  Duplicados:                                   {customers_dupl_count}")
print(f"  % sobre dataframe original:                   {customers_dupl_percent_orig}%")
print(f"  % sobre dataframe con nulos eliminados:       {customers_dupl_percent_new}%")

print("\nValores duplicados de products:")
print(f"  Duplicados:                                   {products_dupl_count}")
print(f"  % sobre dataframe original:                   {products_dupl_percent_orig}%")
print(f"  % sobre dataframe con nulos eliminados:       {products_dupl_percent_new}%")
print("------------------------------------------")

#Eliminación de valores duplicados
df_orders_clean_dupl = df_orders_clean_null.drop_duplicates(subset = orders_critical_rows)
df_order_items_clean_dupl = df_order_items_clean_null.drop_duplicates(subset = order_items_critical_rows)
df_customers_clean_dupl = df_customers_clean_null.drop_duplicates(subset = customers_critical_rows)
df_products_clean_dupl = df_products_clean_null.drop_duplicates(subset = products_critical_rows)

#Conteo de valores duplicados por dataframe post limpieza (considerando columnas críticas)
orders_dupl_count = df_orders_clean_dupl.duplicated(subset = orders_critical_rows).sum()
order_items_dupl_count = df_order_items_clean_dupl.duplicated(subset = order_items_critical_rows).sum()
customers_dupl_count = df_customers_clean_dupl.duplicated(subset = customers_critical_rows).sum()
products_dupl_count = df_products_clean_dupl.duplicated(subset = products_critical_rows).sum()

print("------------------------------------------")
print(f'\nValores duplicados post limpieza (columnas criticas), si se tienen aun duplicados se debe realizar alguna correccion:')
print(f"\nDuplicados de Orders:      {orders_dupl_count}")
print(f"Duplicados de Order Items: {order_items_dupl_count}")
print(f"Duplicados de Customers:   {customers_dupl_count}")
print(f"Duplicados de Products:    {products_dupl_count}")
print("------------------------------------------")

###########################################
# Transform: Manejo de tipo de variables
###########################################

###########################################
# Transform: Otros
###########################################

#################################################################################
#                                       LOAD
#################################################################################

###########################################
# Load: Guardar data como CSV
###########################################

###########################################
# Load: Guardar data como Parquet
###########################################