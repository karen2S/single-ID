import mysql.connector
import sys
import pandas as pd
import networkx as nx

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  
    database="skripsi" 
)

cursor = conn.cursor(dictionary=True)

sample_data = {
    'SID_BORR': sys.argv[1],
    'SID_COBORR': None if sys.argv[2] == "" else sys.argv[2],
    'GID': None
}

df_test = pd.DataFrame([sample_data])

cursor.execute("SELECT * FROM mst_sid_borr_coborr")
mst_sid_borr_coborr = cursor.fetchall()
mst_sid_borr_coborr = pd.DataFrame(mst_sid_borr_coborr)

mst_sid_borr_coborr = pd.concat([mst_sid_borr_coborr, df_test], ignore_index=True)

G = nx.Graph()
for _, row in mst_sid_borr_coborr.iterrows():
    if pd.notna(row["SID_COBORR"]):  # Jika ada pasangan
        G.add_edge(row["SID_BORR"], row["SID_COBORR"])
    else:  # Jika tidak ada pasangan
        G.add_node(row["SID_BORR"])

# Perbarui GID tanpa mengubah yang lama
components = list(nx.connected_components(G))
gid_mapping = {node: f"G{str(int(min(comp)))}" for comp in components for node in comp}
mst_sid_borr_coborr["GID"] = mst_sid_borr_coborr["SID_BORR"].map(gid_mapping)

    # Drop and recreate the SQL table
cursor.execute("DROP TABLE IF EXISTS mst_sid_borr_coborr")
cursor.execute("""
    CREATE TABLE mst_sid_borr_coborr (
        SID_BORR VARCHAR(13),
        SID_COBORR VARCHAR(13),
        GID VARCHAR(14)
    )
""")
conn.commit()

# Insert data into SQL
for _, row in mst_sid_borr_coborr.iterrows():
    cursor.execute("""
    INSERT INTO mst_sid_borr_coborr (SID_BORR, SID_COBORR, GID)
    VALUES (%s, %s, %s)
""", (row["SID_BORR"], row["SID_COBORR"], row["GID"]))
conn.commit()