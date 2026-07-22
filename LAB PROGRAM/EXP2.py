import pandas as pd

df = pd.read_csv("job_historyEXP2.csv")

result = df["EMPLOYEE_ID"].value_counts()

print(result[result >= 2])
