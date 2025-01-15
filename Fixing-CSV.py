import pandas as pd

def convert_value(value):
    value = value.replace("€", "").strip()  # Euro işaretini kaldır
    if value == "-" or value == "":
        return None  # Eksik veya geçersiz değerler için
    if "mil." in value:
        return float(value.replace("mil.", "").strip()) * 1_000_000  # Milyon çevirimi
    elif "bin" in value:
        return float(value.replace("bin", "").strip()) * 1_000  # Bin çevirimi
    return float(value)  # Eğer birim yoksa direkt çevir

df = pd.read_csv("C:\\Users\\batur\\OneDrive\\Masaüstü\\Personal Development\\Codes\\Footbox\\CSV Files\\TümOyuncular.csv")

new_df2 = df.copy()
new_df2.head()


new_df2["Piyasa Değeri (Sayısal)"] = new_df2["Piyasa Değeri"].apply(convert_value)

# Doğum tarihi ve yaş sütunlarını ayırma
new_df2["Doğum Tarihi"] = new_df2["Doğum Tarihi/Yaş"].str.extract(r"(\d{1,2} \w+ \d{4})")
new_df2["Yaş"] = new_df2["Doğum Tarihi/Yaş"].str.extract(r"\((\d+)\)").astype(int)

# Orijinal sütunu kaldırmak isterseniz:
new_df2 = new_df2.drop(columns=["Doğum Tarihi/Yaş"])

new_df2.to_csv("C:\\Users\\batur\\OneDrive\\Masaüstü\\Personal Development\\Codes\\Footbox\\CSV Files\\TümOyuncular1.csv", index=False)