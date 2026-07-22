import pandas as pd

df = pd.read_csv("departmentsEXP1.csv")

print(df["DEPARTMENT_ID"].drop_duplicates())
