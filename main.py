import arcpy
from arcpy.sa import *
import pandas as pd

# SŁOWNIK Z WARTOŚCIAMI WSKAŹNIKA C:
c_factor_classes = {
    0: 0,
    1: 0.0015,
    2: 0.05,
    3: 0.5,
    4: 0.1,
    5: 0.6,
    6: 0,
    7: 0,
    8: 0.3
}


# TABELA 'ROOSE 1996 ERODIBILITY' O EROZYJNOŚCI GLEBY I WSKAŹNIKU K:
soil_classes = [
    {
        "name": "Clay",
        "sand_range": (0, 45),
        "silt_range": (0, 40),
        "clay_range": (40, 100),
        "K_values": {"unknown": 0.22, "<2%": 0.24, ">=2%": 0.21}
    },
    {
        "name": "Sandy Clay",
        "sand_range": (45, 65),
        "silt_range": (0, 20),
        "clay_range": (35, 55),
        "K_values": {"unknown": 0.2, "<2%": 0.2, ">=2%": 0.2}
    },
    {
        "name": "Silty Clay",
        "sand_range": (0, 20),
        "silt_range": (40, 60),
        "clay_range": (40, 60),
        "K_values": {"unknown": 0.26, "<2%": 0.27, ">=2%": 0.26}
    },
    {
        "name": "Sand",
        "sand_range": (86, 100),
        "silt_range": (0, 14),
        "clay_range": (0, 10),
        "K_values": {"unknown": 0.02, "<2%": 0.03, ">=2%": 0.01}
    },
    {
        "name": "Sandy Loam",
        "sand_range": (50, 70),
        "silt_range": (0, 50),
        "clay_range": (0, 20),
        "K_values": {"unknown": 0.13, "<2%": 0.14, ">=2%": 0.12}
    },
    {
        "name": "Clay Loam",
        "sand_range": (20, 45),
        "silt_range": (15, 52),
        "clay_range": (27, 40),
        "K_values": {"unknown": 0.3, "<2%": 0.33, ">=2%": 0.28}
    },
    {
        "name": "Loam",
        "sand_range": (23, 52),
        "silt_range": (28, 50),
        "clay_range": (7, 27),
        "K_values": {"unknown": 0.3, "<2%": 0.34, ">=2%": 0.26}
    },
    {
        "name": "Loamy Sand",
        "sand_range": (70, 86),
        "silt_range": (0, 30),
        "clay_range": (0, 15),
        "K_values": {"unknown": 0.04, "<2%": 0.05, ">=2%": 0.04}
    },
    {
        "name": "Sandy Clay Loam",
        "sand_range": (45, 80),
        "silt_range": (0, 28),
        "clay_range": (20, 35),
        "K_values": {"unknown": 0.2, "<2%": 0.2, ">=2%": 0.2}
    },
    {
        "name": "Silty Clay Loam",
        "sand_range": (0, 20),
        "silt_range": (40, 73),
        "clay_range": (27, 40),
        "K_values": {"unknown": 0.32, "<2%": 0.35, ">=2%": 0.3}
    },
    {
        "name": "Silt",
        "sand_range": (0, 20),
        "silt_range": (88, 100),
        "clay_range": (0, 12),
        "K_values": {"unknown": 0.38, "<2%": 0.41, ">=2%": 0.37}
    },
    {
        "name": "Silty Loam",
        "sand_range": (20, 50),
        "silt_range": (74, 88),
        "clay_range": (0, 27),
        "K_values": {"unknown": 0.31, "<2%": 0.41, ">=2%": 0.37}
    }
]


try:
    # Funkcja kopiująca i analizującadane statystyczne/atrybutowe warstwy rastrowej
    # do nowej tabeli atrybutów:

    def k_factor_analysis(raster_path, output_path):
        arcpy.CheckOutExtension("Spatial")

        arcpy.sa.ZonalStatisticsAsTable(
            in_zone_data=raster_path, zone_field="Value",
            in_value_raster=raster_path, out_table=output_path,
        )
        data = []

        with arcpy.da.SearchCursor(output_path, "Value") as cursor:
            for row in cursor:
                data.append(row) # Dodanie wiersza tabeli do listy

        return data

    # Funkcja analizująca dane ze zbioru słowników "soil_classes", na podstawie bazy danych
    # dotyczącej wskaźnika K - "HWSD.mdb", w celu wyznaczenia wskaźnika K:

    def classify_soil(sand, silt, clay, organic_material):

        for soil in soil_classes:
            sand_min, sand_max = soil["sand_range"]
            silt_min, silt_max = soil["silt_range"]
            clay_min, clay_max = soil["clay_range"]
            unknown, lesser, greater = list(soil["K_values"].values())

            if (sand_min <= sand <= sand_max and silt_min <= silt <=
                    silt_max and clay_min <= clay <= clay_max):
                if organic_material < 2:
                    return lesser
                elif organic_material >= 2:
                    return greater
                else:
                    return unknown





    # Ustawienie środowiska - w celu przetestowania kodu na danych ze swojego urządzenia:
    arcpy.env.workspace = r"D:\Studia\semestr_5\podstawy_programowania_GIS\PROJEKT"

    # Ustawienie równoległego przetwarzania na 0 (wyłączenie wielowątkowości) -
    # 'Parallel Processing Factor' w celu przyspieszenia wykonywanych operacji na zlewniach:
    arcpy.env.parallelProcessingFactor = "0"
    arcpy.env.overwriteOutput = True

    # Pobranie ścieżek do danych pierwotnych:
    frame = r"dane\powiat_pulawski\pulawski.shp"
    rainfall_erosivity = r"dane\R\dane_pierwotne\GlobalR_NoPol.tif"
    soil_erodibility = r"dane\K\dane_pierwotne\HWSD2.bil"
    land_cover = r"dane\C_P\dane_pierwotne\woj_lubelskie.tif"
    dem_1 = r"dane\LS\dane_pierwotne\N51E021.hgt"
    dem_2 = r"dane\LS\dane_pierwotne\N51E022.hgt"

    print("Pobieranie danych przebiegło pomyślnie.")





# OBRÓBKA WSKAŹNIKA R:

    # Przycięcie danych do zasięgu:
    R_factor = ExtractByMask(rainfall_erosivity, frame, "INSIDE")
    R_factor.save(r"dane\R\obrobka_danych\R_factor_clip.tif")

    # Nadanie układu współrzędnych (EPSG: 2180):
    arcpy.ProjectRaster_management(
        r"dane\R\obrobka_danych\R_factor_clip.tif",
        r"wyniki\R_factor_out\R_factor_final.tif",
        2180
    )

    print("Pomyślnie zakończono przetwarzanie wskaźnika R.")





    # OBRÓBKA WSKAŹNIKA K:

    # Nadanie układu współrzędnych (EPSG: 2180):

    # Przycięcie danych do zasięgu:
    K_factor_raster = ExtractByMask(soil_erodibility, frame, "INSIDE")
    K_factor_raster.save(r"dane\K\obrobka_danych\K_factor_clip.tif")

    arcpy.ProjectRaster_management(
        r"dane\K\obrobka_danych\K_factor_clip.tif",
        r"wyniki\K_factor_out\K_factor_final.tif",
        2180
    )

# Uzyskanie informacji z komórek rastra, wynik - tabela .dbf

    # Tabela atrybutów z informacjami z komórek rastra wskaźnika K:
    k_raster_path = r"wyniki\K_factor_out\K_factor_final.tif"
    k_table_out_path = r"dane\K\obrobka_danych\K_factor_table.dbf"
    k_table = k_factor_analysis(k_raster_path, k_table_out_path)
    k_table_list = []

    # Zamiana z listy krotek na listę:
    for row in k_table:
        k_table_list.append(row[0])

    # print(k_table_list)

    # Stworzenie data frame do łatwiejszej obsługi danych z excela
    # (przekopiowane z bazy danych)
    results = pd.DataFrame()
    excel_file = r"dane\K\database\HWSD_DATA.xlsx"
    df = pd.read_excel(excel_file)
    K_values = []

    # Jeśli pojawiają się komórki o wartości 7001 (zabudowa), przypisywana jest im wartość
    # domyślna 0.01, gdyż komórki te nie mają informacji w bazie danym HWSD.mdb
    if 7001 in k_table_list:
        K_values.append(0.01)

    # Dodanie odpowiednich pól, stworzenie pola "OM", wyznaczenie wartości
    # wskaźnika K, dla każdego wiersza, na podstawie funkcji classify_soil
    for el in k_table_list:
        if el == 7001:
            continue
        filtered_row = df.loc[(df["MU_GLOBAL"] == el) & (df["SEQ"] == 1)]
        selected = filtered_row[["MU_GLOBAL", "T_SAND", "T_SILT", "T_CLAY", "T_OC"]].copy()
        selected["OM"] = selected["T_OC"] * 1.72
        t_sand = selected["T_SAND"].values[0]
        t_silt = selected["T_SILT"].values[0]
        t_clay = selected["T_CLAY"].values[0]
        om = selected["OM"].values[0]
        K_values.append(classify_soil(t_sand, t_silt, t_clay, om))

    # print(K_values)

    # Dodanie kolumny do warstwy wyjściowej (rastra), z wyznaczonymi wartościami
    # wskaźnika K
    arcpy.AddField_management(k_raster_path, "K_factor", "DOUBLE")
    with arcpy.da.UpdateCursor(k_raster_path, ["K_factor"]) as cursor:
        for idx, row in enumerate(cursor):
            row[0] = K_values[idx]
            cursor.updateRow(row)

    print("Pomyślnie zakończono przetwarzanie wskaźnika K.")





# OBRÓBKA WSKAŹNIKA C oraz P:

    # Przycięcie rastra do zasięgu ramki:

    land_cover_clip = ExtractByMask(land_cover, frame, "INSIDE")
    land_cover_clip.save(r"wyniki\C_P_factors_out\C_factor_final.tif")

    # Dodanie pola factor_C do tabeli atrybutów rastra:
    land_cover_path = r"wyniki\C_P_factors_out\C_factor_final.tif"
    arcpy.BuildRasterAttributeTable_management(land_cover_path, "Overwrite")
    arcpy.AddField_management(land_cover_path, "C_factor", "DOUBLE")

    with arcpy.da.UpdateCursor(land_cover_path, ["OID", "C_factor"]) as cursor:
        for row in cursor:
            rowid = row[0] # Wartość z kolumny 'Rowid'

            if rowid in c_factor_classes:
                row[1] = c_factor_classes[rowid] # Przypisanie wartości C_factor
            else:
                row[1] = None

            cursor.updateRow(row)

    print("Pomyślnie zakończono przetwarzanie wskaźnika C.")





# OBRÓBKA WSKAŹNIKA LS:

    # Złączenie rastrów:
    dem_mosaic = arcpy.management.MosaicToNewRaster(
        [dem_1, dem_2],
        r"dane\LS\obrobka_danych",
        "dem_mosaic.tif", 2180,
        "32_BIT_FLOAT", number_of_bands=1
    )

    # Przycięcie warstwy do zasięgu:
    dem_clip = ExtractByMask(dem_mosaic, frame, "INSIDE")
    dem_clip.save(r"dane\LS\obrobka_danych\dem_clip.tif")

# Wskaźnik L - length (długość zbocza):

    # Wypełnienie zlewni:
    dem_fill = Fill(dem_clip)
    dem_fill.save(r"dane\LS\obrobka_danych\dem_fill.tif")

    # Wyznaczenie kierunku spływu:
    dem_flow_direction = FlowDirection(
        dem_fill, "#", "#", "D8"
    )
    dem_flow_direction.save(r"dane\LS\obrobka_danych\dem_flow_dir.tif")

    # Wyznaczenie akumulacji opadów:
    dem_flow_accumulation = FlowAccumulation(
        dem_flow_direction, "#", "FLOAT",
        "D8"
    )
    dem_flow_accumulation.save(r"dane\LS\obrobka_danych\dem_flow_acc.tif")

    # Wyliczenie wskaźnika L:
    L_factor = Raster(
        Power((dem_flow_accumulation * 30) / 22.13, 0.5)
    )
    L_factor.save(r"dane\LS\obrobka_danych\L_factor.tif")

# Wskaźnik S - steepness (stromość/spadzistość zbocza):

    # Wyznaczenie nachylenia:
    dem_slope = Slope(
        dem_fill, "DEGREE", 1, "PLANAR"
    )
    dem_slope.save(r"dane\LS\obrobka_danych\dem_slope.tif")

    # Wyliczenie wskaźnika S:
    S_factor = Raster(
        Power(Sin(dem_slope * 0.01745) / 0.09, 1.3)
    )
    S_factor.save(r"dane\LS\obrobka_danych\S_factor.tif")

# Wskaźnik LS:

    LS_factor = Raster(
        (L_factor * S_factor) / 100
    )
    LS_factor.save(r"wyniki\LS_factor_out\LS_factor_final.tif")

    print("Pomyślnie zakończono przetwarzanie wskaźnika LS.")





# Obliczenie równania A = R * K * LS * C (* P):

    R_factor_end = r"wyniki/R_factor_out/R_factor_final.tif"
    K_factor_end = r"wyniki/K_factor_out/K_factor_final.tif"
    LS_factor_end = r"wyniki/LS_factor_out/LS_factor_final.tif"
    C_factor_end = r"wyniki/C_P_factors_out/C_factor_final.tif"

    arcpy.Resample_management(
        R_factor_end, r"wyniki/R_factor_out/R_factor_resample.tif",
        700, "NEAREST"
    )
    arcpy.Resample_management(
        K_factor_end, r"wyniki/K_factor_out/K_factor_resample.tif",
        700, "NEAREST"
    )
    arcpy.Resample_management(
        LS_factor_end, r"wyniki/LS_factor_out/LS_factor_resample.tif",
        700, "NEAREST"
    )
    arcpy.Resample_management(
        C_factor_end, r"wyniki/C_P_factors_out/C_factor_resample.tif",
        700, "NEAREST"
    )

    print("Pomyślnie zakończono przetwarzanie narzędzia Resample.")

    # Kalkulacja warstw wynikowych:
    avg_soil_loss = (Raster(R_factor_end) * Raster(K_factor_end) *
                     Raster(LS_factor_end) * Raster(C_factor_end)) / 100000
    avg_soil_loss.save(r"wyniki/soil_loss/soil_loss.tif")

    print("Pomyślnie zakończono kalkulację rastrów.")


except FileNotFoundError as e:
    print(f"BŁĄD: NIE ZNALEZIONO PLIKU. SZCZEGÓŁY: {e}")
except arcpy.ExecuteError as e:
    print(f"NIEZNANY BŁĄD: {e}")
