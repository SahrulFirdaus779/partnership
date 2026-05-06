import pandas as pd
import os

def categorize(text):
    text = text.lower()
    if any(k in text for k in ["kunjungan", "silaturahmi", "sdit", "sdn", "mit ", "sekolah"]):
        return "Kunjungan"
    if any(k in text for k in ["rapat", "meeting", "olah data", "fiksasi"]):
        return "Rapat"
    if "canvasing" in text:
        return "Canvasing"
    if any(k in text for k in ["survey", "kandang"]):
        return "Survey"
    if any(k in text for k in ["promo", "early bird", "launching", "flash sale"]):
        return "Promo"
    if "safari dongeng" in text:
        return "Safari"
    if any(k in text for k in ["idul adha", "tasyrik"]):
        return "Raya"
    return "Lainnya"

def load_and_parse_data():
    filepath = "agenda partnership.csv"
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data = []
    current_month = "April"
    has_switched = False
    
    for i in range(len(lines)):
        line = lines[i].strip()
        if not line: continue
        parts = line.split(';')
        if len(parts) < 2: continue
        
        if parts[1] == 'Kegiatan':
            dates = parts[2:9]
            if i + 1 < len(lines):
                agenda_parts = lines[i+1].strip().split(';')
                if len(agenda_parts) >= 2 and agenda_parts[1] == 'Agenda Qurban 1447 H':
                    agendas = agenda_parts[2:9]
                    
                    for idx, d_str in enumerate(dates):
                        if d_str and d_str.strip().isdigit():
                            day = int(d_str.strip())
                            if not has_switched and day == 1 and i > 15:
                                current_month = "Mei"
                                has_switched = True
                            
                            agenda_text = agendas[idx].strip() if idx < len(agendas) else ""
                            if agenda_text:
                                items = agenda_text.split(" - ") if " - " in agenda_text else (agenda_text.split(" | ") if " | " in agenda_text else [agenda_text])
                                for item in items:
                                    if item.strip():
                                        data.append({
                                            "Tanggal": day,
                                            "Bulan": current_month,
                                            "Agenda": item.strip(),
                                            "Kategori": categorize(item.strip())
                                        })
    return pd.DataFrame(data)

df = load_and_parse_data()
print(f"Total Rows: {len(df)}")
print(df.head(20).to_string())
print(df[df['Bulan'] == 'Mei'].head(10).to_string())
