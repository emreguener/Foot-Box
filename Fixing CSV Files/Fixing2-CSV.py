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

df = pd.read_csv("C:\\Users\\batur\\OneDrive\\Masaüstü\\Personal Development\\Codes\\tümoyuncular.csv")

new_df2 = df.copy()

# Piyasa değerini dönüştürme
new_df2["Piyasa Değeri (Sayısal)"] = new_df2["Piyasa Değeri"].apply(convert_value)


# Yeni CSV dosyasına kaydet
new_df2.to_csv(
    "C:\\Users\\batur\\OneDrive\\Masaüstü\\Personal Development\\Codes\\Footbox\\CSV Files\\TümOyuncular2.csv",
    index=False,
)