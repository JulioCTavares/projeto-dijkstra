import psycopg2
import os
import csv

# Conectar ao banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname="grafo",
    user="postgres",
    password="senha123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Criar tabelas com ID incremental
cursor.execute('''
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY,
    label TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS edges (
    source INTEGER,
    target INTEGER,
    weight REAL,
    FOREIGN KEY (source) REFERENCES nodes (id),
    FOREIGN KEY (target) REFERENCES nodes (id)
)
''')

# Carregar dados dos arquivos
edges_file = './fb-pages-food.edges'


# Carregar os nós e arrestas da base de dados
with open(edges_file, 'r', encoding='utf-8') as f:
    print("Loading edges...")
    for line in f:
        line = line.strip()
        print(f"Read line: {line}")
        parts = line.split()
        if len(parts) == 3:
            try:
                source, target, weight = parts
                # Garantir que os nós de origem e destino existam na tabela nodes
                cursor.execute('INSERT INTO nodes (id) VALUES (%s) ON CONFLICT (id) DO NOTHING', (source,))
                cursor.execute('INSERT INTO nodes (id) VALUES (%s) ON CONFLICT (id) DO NOTHING', (target,))
                print(f"Inserting edge: {source}, {target}, {weight}")
                cursor.execute('INSERT INTO edges (source, target, weight) VALUES (%s, %s, %s)', (int(source), int(target), float(weight)))
            except Exception as e:
                print(f"Error inserting edge: {parts} - {e}")
                conn.rollback()  # Reverter transação para continuar
        else:
            print(f"Malformed line: {parts}")
        conn.commit()  # Finalizar transação bem-sucedida

conn.close()
