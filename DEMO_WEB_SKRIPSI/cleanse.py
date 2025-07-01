import re
import pandas as pd
import json
import sys

def clean_and_validation(df):
    # Cleanse Nama Ibu Kandung
    df['cleaned_NAMA_IBU_KANDUNG'] = df['NAMA_IBU_KANDUNG'].apply(lambda x: str(x).upper() if pd.notna(x) else '')
    
    # Cleanse Tempat Lahir
    df['cleaned_TEMPAT_LAHIR'] = df['TEMPAT_LAHIR'].apply(lambda x: str(x).upper() if pd.notna(x) else '')
    # Remove 'CONVERTED', 'OTHERS', 'OTHER' and clean up single letter and repeated characters
    df['cleaned_TEMPAT_LAHIR'] = df['cleaned_TEMPAT_LAHIR'].apply(lambda x: '' if x in ['CONVERTED', 'OTHERS', 'OTHER'] else x)
    # Remove spaces in TEMPAT_LAHIR
    df['cleaned_TEMPAT_LAHIR'] = df['cleaned_TEMPAT_LAHIR'].str.replace(" ", "", regex=False)
    # Check for single letter and repeated characters after cleaning spaces
    df['cleaned_TEMPAT_LAHIR'] = df['cleaned_TEMPAT_LAHIR'].apply(lambda x: '' if re.match(r'^[A-Za-z]$', x) or re.match(r'^(.)\1*$', x) else x)

    prefixes = {"IR", "DR", "PROF", "DRS", "DRA", "DRG", "HJ", "ALM", "ALMH", "DRH",
                "PHYSO", "NERS", "AK", "BKP", "APT", "PSI", "PEKSOS", "GR", "KONS",
                "AR", "CPA", "CA", "PDT"}
    
    def cleanse_name(name):
        if not isinstance(name, str):
            return ''

	# Replace dots and underscores in one go
	# REPLACE TANDA BACA & SYMBOL JADI SPASI SEBELUM MASUK KE CLEANSING PREFIX & SUFFIX
        cleaned_name = re.sub(r'[^A-Za-z0-9]', ' ', name)
        tokens = cleaned_name.split()

	# Find split_index where token length > 2 and not a prefix (after normalization)
        split_index = next(
            (i for i, token in enumerate(tokens)
            if len(token.strip()) > 2 and token.strip() not in prefixes),
            0
        )

        front_part = tokens[:split_index]
        rest_part = tokens[split_index:]
	
	# Normalize and filter front_part
        front_part_filtered = [
            token.strip()
            for token in front_part
            if token.strip() not in prefixes
        ]
		
        final_tokens = front_part_filtered + rest_part
        return ' '.join(final_tokens)
        
    # 2. Clean Title
    def create_pattern(title_list):
        patterns = []
        for title in title_list:
            pattern = r'\b' + r'\s*'.join([re.escape(part) for part in title]) + r'\b'
            patterns.append(pattern)
        return re.compile('|'.join(patterns), re.IGNORECASE)

    # Title lists
    title = [('MSIE'), ('MMSI'), ('MSEE'), ('MSA'),('MA'), ("CA"), ("PDT"),
                ('IR'), ('DR'), ('PROF',), ('DRS'), ('DRA'), ('DRG'), ('CPA'),
                ('HJ'), ('ALM'), ('ALMH'), ('DRH'), ('PHYSO'), ('NERS'), ('AK'),
                ('BKP'), ('APT'), ('PSI'), ('PEKSOS'), ('GR'), ('KONS'), ('AR'),



            
                ('S', 'ADM'), ('S', 'AG'), ('S', 'AK'), ('S', 'ANT'), ('S', 'ARS'),
                ('S', 'DES'), ('S', 'DS'), ('S', 'E'), ('S', 'FARM'), ('S', 'FIL'),
                ('S', 'FT'), ('S', 'GZ'), ('S', 'H'), ('S', 'HAN'), ('S', 'HUM'),
                ('S', 'HUT'), ('S', 'IIP'), ('S', 'IK'), ('S', 'IN'), ('S', 'IP'),
                ('S', 'KEB'), ('S', 'KED'), ('S', 'KEL'), ('S', 'KEP'), ('S', 'KG'),
                ('S', 'KOM'), ('S', 'LI'), ('S', 'M'), ('S', 'MB'), ('S', 'P'), ('I', 'R'),
                ('S', 'PAR'), ('S', 'PD'), ('S', 'PI'), ('S', 'PN'), ('S', 'PSI'),
                ('S', 'PT'), ('S', 'PTK'), ('S', 'PWK'), ('S', 'S'), ('S', 'SI'),
                ('S', 'SN'), ('S', 'SOS'), ('S', 'ST'), ('S', 'STAT'), ('S', 'STP'),('S', 'IKOM'),
                ('S', 'SY'), ('S', 'T'), ('S', 'TH'), ('S', 'TI'),('S', 'AKTR'),  ('S', 'TP'),('S', 'A'), ('S', 'MAT'), ('S', 'AGR'),


                ('D', 'M'), ('B', 'SC'), ('B', 'A'),

                ('M', 'T'), ('M', 'E'),('M', 'HUM'), ('M', 'M'), ('M', 'KN'), ('M', 'KOM'),  ('M', 'MPD'), ('M', 'ECON'), ('M', 'AB'),  ('M', 'AK'),
                ('M', 'PSI'), ('M', 'STAT'), ('M', 'ED'), ('M', 'CS'), ('M', 'H'), ('M', 'FARM'), ('M', 'SC'), ('M', 'AG'), ('M', 'A'),('M', 'TI'),('M', 'HUT'),
                ('M', 'AP'),('M', 'SI'),('M', 'PD'),('M', 'SN'), ('M', 'FARM'), ('M', 'DIV'), ('M', 'S'), ('M', 'TH'),

                ('PH', 'D'),
                
                
                
                
                ('S', 'I', 'A'), ('S', 'TR', 'AK'), ('S', 'E', 'AS'), ('S', 'A', 'B'), 
                ('S', 'PD', 'B'), ('S', 'TR', 'BNS'), ('S', 'BIS', 'DIG'), ('S', 'K', 'G'), 
                ('S', 'FIL', 'H'), ('S', 'H', 'H'), ('S', 'K', 'H'), ('S', 'PD', 'H'), 
                ('S', 'SOS', 'H'), ('S', 'TR', 'HAN'), ('S', 'E', 'I'), ('S', 'FIL', 'I'), 
                ('S', 'H', 'I'), ('S', 'KOM', 'I'), ('S', 'PD', 'I'), ('S', 'SOS', 'I'), 
                ('S', 'HUB', 'INT'), ('S', 'TR', 'IP'), ('S', 'I', 'K'), ('S', 'TR', 'K'), 
                ('S', 'TR', 'KEB'), ('S', 'I', 'KOM'), ('S', 'TR', 'KOM'), ('S', 'K', 'L'), 
                ('S', 'K', 'M'), ('S', 'A', 'N'), ('S', 'A', 'P'), ('S', 'I', 'P'), 
                ('S', 'T', 'P'), ('S', 'ST', 'PI'), ('S', 'TR', 'PI'), ('S', 'I', 'PTK'), 
                ('S', 'PD', 'SD'), ('S', 'PD', 'SI'), ('S', 'TR', 'SOS'), ('S', 'E', 'SY'), 
                ('S', 'TR', 'T'), ('S', 'SI', 'TH'), ('S', 'T', 'HAN'), ('S', 'K', 'M'), ('S', 'H', 'H'), 
                ('S', 'TR', 'GZ'), ('S', 'TR', 'SOS'),('S', 'H', 'INT'), ('S', 'TH', 'I'), ('S', 'TR', 'PAR'), 
                ('S', 'TR', 'O'), ('S', 'TR', 'SI'), ('S', 'TR', 'KEP'), ('SP', 'O', 'G'),

                ('D', 'P', 'H'),('S', 'E', 'SY'),('D', 'B', 'A'),('S', 'M', 'B'),
                
                ('M', 'B', 'A'),('M', 'A', 'T'), ('M', 'P', 'H'),
                

                ('A', 'MD', 'TEM'), ('A', 'MD', 'RO'), ('A', 'MD', 'FT'), ('A', 'MD', 'KEB'), ('A', 'MD', 'KEP'), ('A', 'MD', 'RAD'),
                ('A', 'MD', 'AKUN'), ('A', 'MD', 'PEL'), ('A', 'MD', 'PJK'), ('A', 'MD', 'LLASDP'), ('A', 'MD', 'PAR'), ('A', 'MD', 'G'),
                ('A', 'MD', 'KOM'),('A', 'MD', 'PRS'),('A', 'MD', 'FAR'),('A', 'MD', 'RMIK'),
                ('A', 'MD', 'KA'),('A', 'MD', 'POL'), 
                
                



                ('S', 'I', 'K', 'K'), ('S', 'K', 'P', 'M'),  ('S', 'S', 'T', 'P'),

                ('A', 'MD', 'I', 'K'), ('A', 'M', 'K', 'L'), ('A', 'MD', 'A', 'A'),('A', 'MD', 'T', 'K'),('A', 'MD', 'A', 'K'),('A', 'MD', 'K', 'G'),

        

                ('M', 'A', 'R', 'S'),('M', 'S', 'C','E'),





                ('A', 'MD', 'M', 'I', 'D'), ('A', 'MD', 'M', 'B', 'U'), ('A', 'MD', 'A', 'P', 'S'),('A', 'MD', 'M', 'I', 'P'), ('A', 'MD', 'M', 'TR', 'U'),
                ('A', 'MD', 'M', 'TR', 'L'), ('A', 'MD', 'M', 'LOG'),('A', 'MD', 'A', 'K', 'P'),


                ('A', 'MD', 'L', 'L', 'A', 'J')

                ]

    pattern_char = create_pattern(title)
    
    # ADA PERUBAHAN
    def clean_name(name):
        if not isinstance(name, str):
            return ''
        
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\d+', '', name)
        name = name.strip()

        words = name.split()

        while words:
            for i in range(len(words)):
                suffix = ' '.join(words[i:])
                if pattern_char.fullmatch(suffix):
                    words = words[:i]
                    break
            else:
                break  

        return ' '.join(words)
    
    def after_check(name, old_name, prefixes):
        name = name.strip()
        tokens = name.split()
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in prefixes:
                before = tokens[i - 1] if i > 0 else None
                after = tokens[i + 1] if (i + 1) < len(tokens) else None

                # Relaxed condition: okay if before/after are None or not a prefix
                if (before is None or before not in prefixes) and (after is None or after not in prefixes):
                    # Check if symbol is present in the original string (e.g., PROF.)
                    pattern = r'\b' + re.escape(token) + r'(?=[^\s])'
                    if re.search(pattern, old_name, flags=re.IGNORECASE):
                        tokens.pop(i)
                        continue
            i += 1

        return ' '.join(tokens)
    
    def clean_all(name):
        result = cleanse_name(name)
        result = clean_name(result)
        result = after_check(result, name, prefixes)
        return result
    
    df['cleaned_name'] = df['NAME_GOLIVE'].apply(clean_all)
    df['cleaned_name_cob'] = df['NAME_COBORR'].apply(clean_all)
    df['cleaned_NAMA_IBU_KANDUNG'] = df['cleaned_NAMA_IBU_KANDUNG'].apply(clean_all)

    # 3. Clean NO_KTP_KITAS column
    df['cleaned_no_ktp'] = df['NO_KTP_KITAS'].astype(str).str.replace(r'\D', '', regex=True)
    df['cleaned_no_ktp_cob'] = df['NO_KTP_COBORR'].astype(str).str.replace(r'\D', '', regex=True)

    # Function to clean the KTP values
    def clean_no_ktp(ktp):
        # If length is 1 or the value consists of repeating characters (e.g., "1111111111111111", "XXXX", etc.)
        if len(ktp) == 1 or len(set(ktp)) == 1:  
            return None  # Return None for invalid cases
        return ktp

    # Apply the cleaning function to the 'NO_KTP_KITAS' column
    df['cleaned_no_ktp'] = df['cleaned_no_ktp'].apply(clean_no_ktp)
    df['cleaned_no_ktp_cob'] = df['cleaned_no_ktp_cob'].apply(clean_no_ktp)

    # 4. Clean NO_NPWP column
    df['cleaned_no_npwp'] = df['NO_NPWP'].apply(lambda x: ''.join(filter(str.isdigit, str(x))))

    # 5. Clean Address
    substitutions = [
        (r'\b(JLN\s|JLN\.|JALAN\s|JALAN\.|JL\.|JLH\s|JLH\.)\s?', 'JL '),
        (r'\b(GANG\s|GANG\.|GG\.)\s?', 'GG '),
        (r'\b(PONDOK\s|PONDOK\.|PD\.)\s?', 'PD '),
        (r'\b(PERUMAHAN\s|PERUMAHAN\.|PERUM\s|PERUM\.|PRM\.|PERUMNAS\s|PERUMNAS\.)\s?', 'PRM '),
        (r'\b(DESA\s|DESA\.|DUSUN\.|DUSUN\s|DS\.|DSN\.|DSN\s)\s?', 'DS '),
        (r'\b(KP\.|KPG\.|KPG\s|KAMPUNG\s|KAMPUNG\.|KAMP\s|KAMP\.|KMP\s|KMP\.)\s?', 'KP '),
        (r'\b(APARTEMEN\.|APARTEMEN\s|APART\.|APART\s|APARTMENT\.|APARTMENT\s|APARTEMENT\.|APARTEMENT\s|AP\s|AP\.|APT\.)\s?', 'APT '),
        (r'\b(KOMPLEKS\s|KOMPLEKS\.|KOMPLEK\s|KOMPLEK\.|KOMPL\s|KOMPL\.|KOMP\s|KOMP\.|KOM\.)\s?', 'KOM '),
        (r'\b(LINGKUNGAN\s|LINGKUNGAN\.|LINGK\s|LINGK\.|LKG\.)\s?', 'LKG '),
        (r'\b(TAMAN\s|TAMAN\.|TMN\s|TMN\.|TM\.)\s?', 'TM '),
        (r'\b(BLOK\.|BLOK\s|BLK\.|BLK\s|BL\.)\s?', 'BL '),
        (r'\b(VILLA\s|VILLA\.|VILA\s|VILA\.|VIL\.)\s?', 'VIL '),
        (r'\b(GRIYA\s|GRIYA\.|GRY\.)\s?', 'GRY '),
        (r'\b(ASRAMA\s|ASRAMA\.|ASR\.)\s?', 'ASR '),
        (r'\b(TANJUNG\s|TANJUNG\.|TJ\.)\s?', 'TJ ')
    ]

    # Known abbreviations with potential spacing issues
    long_abbreviations = ["APARTEMEN", "APARTEMENT", "APARTMENT", "TANJUNG", "LINGKUNGAN", "ASRAMA", 
                        "KOMPLEKS", "PERUMAHAN", "KAMPUNG", "PERUMNAS", "PONDOK"]

    # Function to add space between compound words
    def add_space_between_compound_words(address):
        for abbr in long_abbreviations:
            address = re.sub(rf'({abbr})([A-Z])', r'\1 \2', address)
        return address

    # Function to apply all substitutions globally
    def update_address(address):
        if not isinstance(address, str):
            return ''  # Handle non-string inputs gracefully
        
        # Correct compound abbreviations
        address = add_space_between_compound_words(address)
        
        # Apply all substitution patterns globally
        for pattern, replacement in substitutions:
            address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)
        
        return address

    df['cleaned_alamat'] = df['ALMT_RUMAH'].apply(update_address)
    df['cleaned_alamat_cob'] = df['ALAMAT_COBORR'].apply(update_address)
    
    # Final fallback if name is empty after cleaning
    df['cleaned_name'] = df.apply(lambda row: row['cleaned_name'] if row['cleaned_name'] != '' else row['NAME_GOLIVE'], axis=1) 
    df['cleaned_name_cob'] = df.apply(lambda row: row['cleaned_name_cob'] if row['cleaned_name_cob'] != '' else row['NAME_COBORR'], axis=1)       
    df['cleaned_NAMA_IBU_KANDUNG'] = df.apply(lambda row: row['cleaned_NAMA_IBU_KANDUNG'] if row['cleaned_NAMA_IBU_KANDUNG'] != '' else row['NAMA_IBU_KANDUNG'], axis=1) 
    
    # Remove 'BUNDA', 'UMI', 'IBU', 'BU', 'NY'
    df['cleaned_NAMA_IBU_KANDUNG'] = df['cleaned_NAMA_IBU_KANDUNG'].apply(lambda x: '' if x in ['BUNDA', 'UMI', 'IBU', 'BU', 'NY', 'NYONYA'] else x)

    # Remove rows with a single letter or repeated characters for cleaned_NAMA_IBU_KANDUNG
    df['cleaned_NAMA_IBU_KANDUNG'] = df['cleaned_NAMA_IBU_KANDUNG'].apply(
    lambda x: '' if isinstance(x, str) and (re.match(r'^[A-Za-z]$', x) or re.match(r'^(.)\1*$', x)) else x)

    def remove_extra_spaces(text):
        # Check if the input is a string or not
        if not isinstance(text, str):
            return ''  # Return an empty string for non-strings (e.g., NaN, float)
        return re.sub(r'\s+', ' ', text).strip()

    df['cleaned_name'] = df['cleaned_name'].apply(remove_extra_spaces)
    df['cleaned_name_cob'] = df['cleaned_name_cob'].apply(remove_extra_spaces)
    df['cleaned_NAMA_IBU_KANDUNG'] = df['cleaned_NAMA_IBU_KANDUNG'].apply(remove_extra_spaces)
    df['cleaned_alamat'] = df['cleaned_alamat'].apply(remove_extra_spaces)
    df['cleaned_alamat_cob'] = df['cleaned_alamat_cob'].apply(remove_extra_spaces)
    return df
    
sample_data = {
    'NAME_GOLIVE': sys.argv[1],
    'NAMA_IBU_KANDUNG': sys.argv[2],
    'TEMPAT_LAHIR': sys.argv[3],
    'NO_NPWP': sys.argv[4],
    'NO_KTP_KITAS': sys.argv[5],
    'ALMT_RUMAH': sys.argv[6],
    'NO_KTP_COBORR': None if sys.argv[7] == 'NAN' else sys.argv[7],
    'NAME_COBORR': None if sys.argv[8] == 'NAN' else sys.argv[8],
    'ALAMAT_COBORR': None if sys.argv[9] == 'NAN' else sys.argv[9]
}

# Creating DataFrame
df_test = pd.DataFrame([sample_data])
df_test = clean_and_validation(df_test)
output = df_test[['cleaned_name','cleaned_NAMA_IBU_KANDUNG','cleaned_TEMPAT_LAHIR','cleaned_no_ktp',
                  'cleaned_no_npwp','cleaned_alamat','cleaned_name_cob','cleaned_no_ktp_cob','cleaned_alamat_cob']]
row = output.iloc[0].to_dict()

def get_bigrams(name):
    if not isinstance(name, str):  # Check if 'name' is a string
        print(f"Non-string value encountered: {name}")
    name = name.replace(" ", "")  # Remove spaces to consider all characters together
    return {name[i: i + 2] for i in range(len(name) - 1)}
row["bigrams"] = list(get_bigrams(df_test['cleaned_name'].iloc[0]))
print(json.dumps([row]))