import mysql.connector
import json
import sys
from pyjarowinkler import distance
import pandas as pd
import networkx as nx

sample_data = {
    'cleaned_name': sys.argv[1],
    'cleaned_TEMPAT_LAHIR': sys.argv[2],
    'TGL_LAHIR': pd.to_datetime(sys.argv[3]).date(),
    'cleaned_no_ktp': sys.argv[4],
    'cleaned_no_npwp': sys.argv[5],
    'cleaned_alamat': sys.argv[6],
    'cleaned_NAMA_IBU_KANDUNG': sys.argv[7],
    'CD_SP': sys.argv[8],
    'cleaned_name_cob': sys.argv[9],
    'cleaned_no_ktp_cob': sys.argv[10],
    'TGL_LAHIR_COBORR': None if sys.argv[11] == "NAN" else pd.to_datetime(sys.argv[11]).date(),
    'cleaned_alamat_cob': sys.argv[12]
    }

df_test = pd.DataFrame([sample_data])

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # update this
    database="skripsi"  # update this
)

cursor = conn.cursor(dictionary=True)

# Fetch data from bigram_index
cursor.execute("SELECT * FROM bigram_index")

bigram_groups = cursor.fetchall()

bigram_dict = {
    row['bigram']: json.loads(row['group_values'])
    for row in bigram_groups
}

# Fetch data from bigram_index
cursor.execute("SELECT * FROM monre_dict")
monre_groups = cursor.fetchall()
monre_dict = {
    row['cleaned_name']: json.loads(row['place_index'])
    for row in monre_groups
}

def get_bigrams(name):
    # if not isinstance(name, str):  # Check if 'name' is a string
    #     print(f"Non-string value encountered: {name}")
    name = name.replace(" ", "")  # Remove spaces to consider all characters together
    return {name[i: i + 2] for i in range(len(name) - 1)}

# Function to compare two names based on bigrams and Jaro-Winkler similarity
def compare_bigrams_and_jaro_winkler(name1, name2, threshold=0.5):
    bigrams1 = get_bigrams(name1) # Use precomputed bigrams
    bigrams2 = get_bigrams(name2)  # Use precomputed bigrams
    
    # Find the common bigrams between the two names using set intersection
    common_bigrams = bigrams1.intersection(bigrams2)
    
    # Count how many common bigrams there are
    common_count = len(common_bigrams)
    
    # Find the smallest bigram length between the two names
    min_bigrams_len = min(len(bigrams1), len(bigrams2))
    
    # If common bigrams are greater than 50% of the smallest bigram set, calculate Jaro-Winkler
    if common_count > threshold * min_bigrams_len:
        jaro_winkler_similarity = distance.get_jaro_distance(name1, name2)
        return jaro_winkler_similarity
    else:
        return None

# Function to calculate Jaro-Winkler distances for names based on selected bigrams
def calculate_jaro_winkler_distances(name):
    bigrams = get_bigrams(name) # Use precomputed bigrams
    bigram_weights = [
        (bigram, len(bigram_dict[bigram]))
        for bigram in bigrams
        if bigram in bigram_dict
    ]
    
    # Sort bigrams by their frequency (lower frequency = higher weight)
    bigram_weights_sorted = sorted(bigram_weights, key=lambda x: x[1])

    # Select the top 3 least frequent bigrams
    selected_bigrams = [bg[0] for bg in bigram_weights_sorted[:len(bigram_weights_sorted)]]
    
    # Find all unique names in the groups of these 3 bigrams
    matching_names = set()
    for bigram in selected_bigrams:
        matching_names.update(bigram_dict[bigram])

    matching_names.discard(name)  # Remove the original name from comparison
    
    # Compute Jaro-Winkler similarity for each name in the matching group using bigram comparison
    distances = {}
    
    for other_name in matching_names:
        # Use the new comparison function to check bigram overlap and compute Jaro-Winkler
        similarity = compare_bigrams_and_jaro_winkler(name, other_name)
        if similarity and similarity > 0.75:
            distances[other_name] = similarity

    return name, distances  # Return the name and its distances

def add_new_name_to_results_dict(new_name):
    # Calculate Jaro-Winkler distances for the new name
    name, distances = calculate_jaro_winkler_distances(new_name)
    
    # If the new name has similar names, add it to results_list
    if distances:
        similar_names_df = pd.DataFrame(
            list(distances.items()), columns=["similar_name", "similarity"]
        )
        results_list = similar_names_df["similar_name"].tolist()  # Convert similar names to a list
    else:
        results_list = []
    results_list.append(new_name)
    return results_list

def jaro_winkler_match(value1, value2, threshold=0.92): # Default Threshold
    if pd.notna(value1) and pd.notna(value2):
        value1_str = str(value1).strip() 
        value2_str = str(value2).strip() 
        
        # Ensure neither value is an empty string
        if value1_str and value2_str:
            similarity = distance.get_jaro_distance(value1_str, value2_str)
            return similarity >= threshold
    return False 

rule = 0
check = 0
panjang = 0
panjang_1 = 0
match_found = True

for index, row in df_test.iterrows():
    # Kalau masih kosong
    if not monre_dict:
        kode_cabang = row['CD_SP']
        
        cursor.execute(f"SELECT COUNT FROM sp_count WHERE CD_SP = ({kode_cabang})")
        last_sequence = cursor.fetchone()
        
        sid_value = f"{kode_cabang}{(int(last_sequence['COUNT']) + 1):07d}"
        
        cursor.execute(
            "UPDATE sp_count SET COUNT = %s WHERE CD_SP = %s",
            (int(last_sequence['COUNT']) + 1, kode_cabang)
        )
        conn.commit()
        check = "atas"
        break
    
    row_compared = row
    matched_dfs = []
    results_list = add_new_name_to_results_dict(row['cleaned_name'])
    all_indices = set()
    for name in results_list:
        if name in monre_dict:
            indices = monre_dict[name]
            all_indices.update(map(int, monre_dict[name]))
            id_list = ','.join(map(str, all_indices))
            cursor.execute(f"SELECT * FROM credit_cust WHERE id IN ({id_list})")
            matched_dfs = cursor.fetchall()
            matched_dfs = pd.DataFrame(matched_dfs)
            
    if len(matched_dfs) == 0:
        kode_cabang = row['CD_SP']
        
        cursor.execute(f"SELECT COUNT FROM sp_count WHERE CD_SP = ({kode_cabang})")
        last_sequence = cursor.fetchone()
        
        sid_value = f"{kode_cabang}{(int(last_sequence['COUNT']) + 1):07d}"
        
        cursor.execute(
            "UPDATE sp_count SET COUNT = %s WHERE CD_SP = %s",
            (int(last_sequence['COUNT']) + 1, kode_cabang)
        )
        conn.commit()
        check = "tengah"
        break
    else:
        result_df_nodup = matched_dfs.drop_duplicates(subset='NO_AGGR').reset_index(drop=True)
    
    result_df_nodup = result_df_nodup.replace("", None)
    name_compared = row['cleaned_name']
    dob_compared = row['TGL_LAHIR']
    tempat_compared = row['cleaned_TEMPAT_LAHIR']
    ktp_kitas_compared = row['cleaned_no_ktp']
    mother_name_compared = row['cleaned_NAMA_IBU_KANDUNG'] 
    npwp_compared = row['cleaned_no_npwp']
    address_compared = row['cleaned_alamat']
    
    # panjang = str(result_df_nodup.loc[0]['TGL_LAHIR']) == dob_compared
    # panjang_1 = (
    #     pd.notna(result_df_nodup.loc[0]['TGL_LAHIR']) &
    #     pd.notna(dob_compared) &
    #     (str(result_df_nodup.loc[0]['TGL_LAHIR']) == dob_compared)
    # )
    
    # Filter result_df based on matching criteria
    filtered_result_df = result_df_nodup[
        (
            (pd.notna(result_df_nodup['TGL_LAHIR']) & pd.notna(dob_compared) &
            (result_df_nodup['TGL_LAHIR'].astype(str) == dob_compared)) |

            (pd.notna(result_df_nodup['cleaned_no_ktp']) & pd.notna(ktp_kitas_compared) &
            (result_df_nodup['cleaned_no_ktp'].astype(str) == ktp_kitas_compared)) |

            (pd.notna(result_df_nodup['cleaned_NAMA_IBU_KANDUNG']) & pd.notna(mother_name_compared) &
            (result_df_nodup['cleaned_NAMA_IBU_KANDUNG'] == mother_name_compared)) |

            (pd.notna(result_df_nodup['cleaned_no_npwp']) & pd.notna(npwp_compared) &
            (result_df_nodup['cleaned_no_npwp'].astype(str) == npwp_compared))
        )
    ]
    
    # panjang = len(filtered_result_df) 
    filtered_result_df = filtered_result_df.copy()
    filtered_result_df['flag_SID'] = 'N'  
    filtered_result_df['rule_num'] = None
    
    for index, row in filtered_result_df.iterrows():
        name_sim = jaro_winkler_match(row['cleaned_name'], name_compared)
        
        if (
            name_sim and 
            pd.notna(row['TGL_LAHIR']) and str(row['TGL_LAHIR']) == dob_compared and 
            pd.notna(row['cleaned_TEMPAT_LAHIR']) and row['cleaned_TEMPAT_LAHIR'] == tempat_compared and 
            pd.notna(row['cleaned_NAMA_IBU_KANDUNG']) and jaro_winkler_match(row['cleaned_NAMA_IBU_KANDUNG'], mother_name_compared)  # Rule 1
        ):
            filtered_result_df.loc[index, 'flag_SID'] = 'Y'
            filtered_result_df.loc[index, 'rule_num'] = 'RULE 1'
            rule = "RULE 1"

        elif (
            name_sim and 
            pd.notna(row['cleaned_no_ktp']) and str(row['cleaned_no_ktp']) == ktp_kitas_compared  # Rule 2
        ):
            filtered_result_df.loc[index, 'flag_SID'] = 'Y'
            filtered_result_df.loc[index, 'rule_num'] = 'RULE 2'
            rule = "RULE 2"

        elif (
            name_sim and 
            pd.notna(row['cleaned_no_npwp']) and str(row['cleaned_no_npwp']) == npwp_compared  # Rule 3
        ):
            filtered_result_df.loc[index, 'flag_SID'] = 'Y'
            filtered_result_df.loc[index, 'rule_num'] = 'RULE 3'
            rule = "RULE 3"

        elif (
            jaro_winkler_match(row['cleaned_name'], name_compared, threshold=0.95) and 
            pd.notna(row['cleaned_alamat']) and jaro_winkler_match(row['cleaned_alamat'], address_compared) and  # Rule 4
            pd.notna(row['cleaned_NAMA_IBU_KANDUNG']) and jaro_winkler_match(row['cleaned_NAMA_IBU_KANDUNG'], mother_name_compared)  
        ):
            filtered_result_df.loc[index, 'flag_SID'] = 'Y'
            filtered_result_df.loc[index, 'rule_num'] = 'RULE 4' 
            rule = "RULE 4"
 
        elif (
            pd.notna(row['TGL_LAHIR']) and str(row['TGL_LAHIR']) == dob_compared and 
            pd.notna(row['cleaned_no_ktp']) and row['cleaned_no_ktp'] == ktp_kitas_compared  # Rule 5
        ):
            filtered_result_df.loc[index, 'flag_SID'] = 'Y'
            filtered_result_df.loc[index, 'rule_num'] = 'RULE 5'  
            rule = "RULE 5"
        
        elif (
            jaro_winkler_match(row['cleaned_name'], name_compared, threshold=0.95) and 
            pd.notna(row['cleaned_alamat']) and jaro_winkler_match(row['cleaned_alamat'], address_compared) and
            pd.notna(row['TGL_LAHIR']) and str(row['TGL_LAHIR'] == dob_compared) and 
            pd.notna(row['cleaned_TEMPAT_LAHIR']) and row['cleaned_TEMPAT_LAHIR'] == tempat_compared # Rule 6
        ):
            filtered_result_df.loc[index, 'flag_SID'] = 'Y'
            filtered_result_df.loc[index, 'rule_num'] = 'RULE 6'  
            rule = "RULE 6"

        else:
            filtered_result_df.loc[index, 'flag_SID'] = 'N'
            filtered_result_df.loc[index, 'rule_num'] = None # No match, no rule number
            rule = "None"
    
    # if (pd.notna(filtered_result_df.loc[0]['cleaned_alamat']) and jaro_winkler_match(filtered_result_df.loc[0]['cleaned_alamat'], address_compared)):
    #     # str(filtered_result_df.loc[0]['TGL_LAHIR']) == dob_compared)
    #     # filtered_result_df.loc[0]['cleaned_TEMPAT_LAHIR'] == tempat_compared):
    #     panjang = 1
    # else:
    #     panjang = 2
    # # panjang = filtered_result_df.loc[0]['cleaned_no_ktp']
    # if (pd.notna(filtered_result_df.loc[0]['TGL_LAHIR']) and str(filtered_result_df.loc[0]['TGL_LAHIR'] == dob_compared)):
    #     # str(filtered_result_df.loc[0]['TGL_LAHIR']) == dob_compared)
    #     # filtered_result_df.loc[0]['cleaned_TEMPAT_LAHIR'] == tempat_compared):
    #     panjang_1 = 1
    # else:
    #     panjang_1 = 2
        
    # panjang_1 = ktp_kitas_compared
    # panjang = str(filtered_result_df.loc[0]['TGL_LAHIR'])
    # panjang_1 = filtered_result_df.loc[0]['TGL_LAHIR']
    filtered_result_df = filtered_result_df[filtered_result_df['flag_SID'] == 'Y'].reset_index(drop=True)

    if filtered_result_df.empty:
        row_compared_df = pd.DataFrame([row_compared])  
        row_compared_df['flag_SID'] = 'Y'                
        filtered_result_df = pd.concat([filtered_result_df, row_compared_df], ignore_index=True)

    check_sid_exist = False
    if not filtered_result_df['SID'].isnull().all():
        check_sid_exist = True
        check = "got an existing SID"
        sid_value = filtered_result_df['SID'].dropna().iloc[0]
        
    # If no existing SID is found, generate a new one
    if not check_sid_exist:
        filtered_result_df = filtered_result_df.sort_values(by='DT_GOLIVE_VALID').reset_index(drop=True)
        
        kode_cabang = str(filtered_result_df.loc[0, 'CD_SP']) 
        cursor.execute("SELECT COUNT FROM sp_count WHERE CD_SP = %s", (kode_cabang,))
        last_sequence = cursor.fetchone()
        
        sid_value = f"{kode_cabang}{(int(last_sequence['COUNT']) + 1):07d}"
        
        cursor.execute(
            "UPDATE sp_count SET COUNT = %s WHERE CD_SP = %s",
            (int(last_sequence['COUNT']) + 1, kode_cabang)
        )
        conn.commit()
        filtered_result_df['SID'] = sid_value
        check = "bawah"
    else:
        cursor.execute(f"SELECT * FROM credit_cust WHERE SID = '{sid_value}'")
        data_to_match = cursor.fetchall()

        db_columns = ['cleaned_name','cleaned_TEMPAT_LAHIR','TGL_LAHIR','cleaned_no_ktp',
                      'cleaned_no_npwp','cleaned_alamat','cleaned_NAMA_IBU_KANDUNG']

        df_db = pd.DataFrame(data_to_match, columns=db_columns)

        common_columns = df_test.columns.intersection(df_db.columns)
        match_found = False
        for idx, row in df_db.iterrows():
            mismatches = {}
            for col in common_columns:
                val_test = df_test.at[0, col]
                val_db = row[col]

                if pd.isna(val_test) and pd.isna(val_db):
                    continue
                elif val_test != val_db:
                    mismatches[col] = {'test': val_test, 'db': val_db}

            if not mismatches:
                match_found = True
                break
        
output = dict()
output['sid_value'] = sid_value
output['check'] = check
output['rule'] = rule
output['match_found'] = match_found
# output['differences'] = mismatches
# output['differences'] = {
#     'test': type(mismatches['TGL_LAHIR']['test']).__name__,
#     'db': type(mismatches['TGL_LAHIR']['db']).__name__
# }
# output['panjang'] = panjang
# output['panjang_1'] = panjang_1

# GID
for index, row in df_test.iterrows():
    name_compared = row['cleaned_name_cob']
    name_borr_compared = row['cleaned_name']
    dob_compared = row['TGL_LAHIR_COBORR']
    ktp_kitas_compared = row['cleaned_no_ktp_cob']
    address_compared = row['cleaned_alamat_cob']
    sid_compared = sid_value

    if pd.notna(row['cleaned_name_cob']) and row['cleaned_name_cob'] != '' and row['cleaned_name_cob'] != 'nan':
        row_compared = row
        matched_dfs = []
        all_indices_coborr = set()
        id_list = None
        results_list = add_new_name_to_results_dict(row['cleaned_name_cob'])
        
        for name in results_list:
            if name in monre_dict:
                indices = monre_dict[name]
                all_indices_coborr.update(map(int, monre_dict[name]))
                id_list = ','.join(map(str, all_indices_coborr))
                cursor.execute(f"SELECT * FROM credit_cust WHERE id IN ({id_list})")
                rows_sql = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                matched_df = pd.DataFrame(rows_sql, columns=columns)
                matched_dfs.append(matched_df)

        if len(matched_dfs) > 0:
            combined_df = pd.concat(matched_dfs, ignore_index=True)
            mask = (
                        (
                            pd.notna(combined_df['TGL_LAHIR']) & pd.notna(dob_compared) &
                            (combined_df['TGL_LAHIR'].astype(str) == dob_compared)
                        ) |
                        (
                            pd.notna(combined_df['cleaned_no_ktp']) & pd.notna(ktp_kitas_compared) &
                            (combined_df['cleaned_no_ktp'].astype(str) == ktp_kitas_compared)
                        )
                    )
            
            filtered_result_df = combined_df[mask].copy()
            filtered_result_df['flag'] = None 
            
            for index, row in filtered_result_df.iterrows():
                name_sim = jaro_winkler_match(row['cleaned_name'], name_compared)
                if (
                    name_sim and 
                    pd.notna(row['cleaned_no_ktp']) and pd.notna(ktp_kitas_compared) 
                    and str(row['cleaned_no_ktp']) == ktp_kitas_compared  
                ):
                    filtered_result_df.loc[index, 'flag'] = 'Y'
                    filtered_result_df.loc[index, 'rule_num'] = 'RULE 1'
                elif (
                    pd.notna(row['TGL_LAHIR']) and pd.notna(dob_compared) and  str(row['TGL_LAHIR']) == dob_compared and 
                    pd.notna(row['cleaned_no_ktp']) and pd.notna(ktp_kitas_compared) and row['cleaned_no_ktp'] == ktp_kitas_compared  # Rule 5
                ):
                    filtered_result_df.loc[index, 'flag'] = 'Y'
                    filtered_result_df.loc[index, 'rule_num'] = 'RULE 2'  
                else:
                    filtered_result_df.loc[index, 'flag'] = 'N'
                    filtered_result_df.loc[index, 'rule_num'] = None 

            filtered_result_df = filtered_result_df[filtered_result_df['flag'] == 'Y']
            if len(filtered_result_df) == 0 :
                sid_cobor_value = None
            else:
                if filtered_result_df['SID'].nunique() > 1:
                    print('Coborr dimiripkan dengan 2 SID berbeda yaitu:')
                    print(filtered_result_df['SID'].unique())
                else:
                    sid_cobor_value = filtered_result_df['SID'].iloc[0]
        else:
            sid_cobor_value = None
    else:
        sid_cobor_value = None
output['sid_cobor_value'] = sid_cobor_value

cursor.execute("SELECT * FROM mst_sid_borr_coborr")
mst_sid_borr_coborr = cursor.fetchall()
mst_sid_borr_coborr = pd.DataFrame(mst_sid_borr_coborr)

if len(mst_sid_borr_coborr)==0:
    mst_sid_borr_coborr = pd.DataFrame(columns=['SID_BORR','SID_COBORR','GID'])
    
exists = False

if pd.notna(sid_value) and pd.notna(sid_cobor_value):
    if not mst_sid_borr_coborr[
        (mst_sid_borr_coborr['SID_BORR'] == sid_value) &
        (mst_sid_borr_coborr['SID_COBORR'] == sid_cobor_value)
    ].empty:
        exists = True

elif pd.isna(sid_cobor_value):
    if not mst_sid_borr_coborr[
        mst_sid_borr_coborr['SID_BORR'] == sid_value
    ].empty:
        exists = True
        
added_to_mst_gid = False

# Append only if the pair does not exist
if not exists and match_found:
    new_row = pd.DataFrame([{
        'SID_BORR': sid_value,
        'SID_COBORR': sid_cobor_value,
        'GID': None
    }])
    mst_sid_borr_coborr = pd.concat([mst_sid_borr_coborr, new_row], ignore_index=True)
    added_to_mst_gid = True
    
if added_to_mst_gid:
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
if match_found:
    if sid_cobor_value is None:
        gid_value = mst_sid_borr_coborr[mst_sid_borr_coborr['SID_BORR']==sid_value]['GID'].iloc[0]
    else:
        gid_value = mst_sid_borr_coborr[(mst_sid_borr_coborr['SID_BORR']==sid_value)&(mst_sid_borr_coborr['SID_COBORR']==sid_cobor_value)]['GID'].iloc[0]
else:
    gid_value = f"G{sid_value}"
output['gid_value'] = gid_value  

conn.commit()
print(json.dumps([output]))