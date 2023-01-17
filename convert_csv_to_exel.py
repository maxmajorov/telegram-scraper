import pandas as pd

def csv_to_exel(file_name):
   pd.read_csv(f"{file_name}.csv", sep=",", encoding="UTF-8").to_excel(f"{file_name}.xlsx", index=None, header=True)

