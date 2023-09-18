import pandas as pd
import sys

#Allow dataframes to be sorted by specific columns
def filterdf(code, column, df):
    if code is None:
        return df
    if isinstance(code,list):
        if len(code) == 0:
            return df
        return df[df[column].isin(code)]
    return df[df[column]==code]

if __name__ == "__main__":
    #Initialize dataframes
    DATAFRAME = pd.read_csv('../dash/datasets/Faostat_Data.csv')
    SPECIES = sorted(DATAFRAME['species'].unique())
    COUNTRIES = sorted(DATAFRAME['country'].unique())

    df = filterdf(species,'Chickens',DATAFRAME)

    df = df.sort_values(["country","year"])

    newdf = pd.DataFrame()

    k = 0
    for j in df['population']:
        if(k != 0):
            if(df['country'].iloc[k] == df['country'].iloc[k-1]): # if countries are the same
                if(df['population'].iloc[k-1] != 0): # if not the first year of said country
                    diff = (df['population'].iloc[k] / df['population'].iloc[k-1]) * 100

                    if diff < 0:
                        diff = diff * -1

                    if diff > percent:
                        newdf = newdf.append(df.iloc[0], ignore_index=True)

        k+=1