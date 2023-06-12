import pandas as pd
import sys
import os
import bisect

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

    spec = 0
    coun = 0
    sortedPerc = []
    
    if(len(sys.argv) < 2):
        print("Please rerun with a selected Country or Species.")
        exit()
    else:
        if sys.argv[1] in SPECIES:
            df = filterdf(sys.argv[1],'species',DATAFRAME)
            spec = 1
        else:
            if sys.argv[1] in COUNTRIES:
                df = filterdf(sys.argv[1],'country',DATAFRAME)
                coun = 1
            else:
                print("Please rerun with a selected Country or Species.")
                exit()

    total = 0
    official = 0
    unoff = 0
    imputed = 0
    forecast = 0
    
    #total counts of each flags representation
    for i in df['flag']:
        if i == ' ':
            official += 1
        elif i == 'F':
            forecast += 1
        elif i == 'Im':
            imputed += 1
        else:
            unoff += 1
        total += 1

    
    print("Summary of " + sys.argv[1] + " Flags")
    print("Offical Flags: " + "{:.2f}".format(official / total * 100))
    print("Unoffical Flags: " + "{:.2f}".format(unoff / total * 100))
    print("Imputed Flags: " + "{:.2f}".format(imputed / total * 100))
    print("Forecasted Flags: " + "{:.2f}".format(forecast / total * 100))

    official = 0
    total = 0

    #Calculate % of official flags in each country
    if coun == 1:
        for i in COUNTRIES:
            df = filterdf(i,'country',DATAFRAME)

            for j in df['flag']:
                if j == ' ':
                    official += 1
                total += 1

            sortedPerc.insert(0,((official / total * 100), i))
        
        sortedPerc.sort(reverse=True)

        index = [x[1] for x in sortedPerc].index(sys.argv[1])
        length = len(COUNTRIES)

        print("\nRanking of Offical Values: " + str(index + 1) + "/" + str(length))

            
            
            