# Bangjie Xue
from flask import Flask, render_template, request
import urllib.parse
import os
import pandas as pd
from pprint import pprint
import numpy as np
from sklearn.manifold import TSNE
from scipy.stats import spearmanr

def scoring(rank, df):
    
    def tsne_score(df):
        TSNEout = TSNE(n_components=2, method='exact').fit_transform(df)
        score = TSNEout[:, 0] - TSNEout[:, 1]

        return score
    
    df = (df - df.min(0))/(df.max(0) - df.min(0))
    
    #  spearsman corr
    corr = spearmanr(rank, df)[0][0][1:]
    df *= corr
    
    score = tsne_score(df)
    
    
    return corr, score

app = Flask(__name__)


# Landing Page, show a list of features
@app.route("/", methods=["GET", "POST"])
def index():
    param_names = [
        "Parking Friendliness",
        "Biking Friendliness",
        "Ease of Commute",
        "Affordability",
        "Safety",
    ]
    rank = ["Irrelevant", "Low", "Medium", "High"]
    global parameters
    if request.method == "POST":
        parameters = [request.form.get(param_name) for param_name in param_names]
        mapped_param = {
            '0':0,
            '1':0.25,
            '2':0.6,
            '3':1
            }
        
        df = pd.read_csv("/Users/JimXue/Desktop/tartanhack24/Datasets/post_processed.csv")
        # Normalize the data sum to 1
        for col in df.iloc[:, 3:]:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col] / df[col].sum()
            if df[col].dtype == object and df[col].str.contains('%').any():
                # Remove the percentage sign and convert to float
                df[col] = df[col].str.replace('%', '').astype(float) / 100
                # Now normalize
                df[col] = df[col] / df[col].sum()
            if df[col].dtype == object and df[col].str.contains('$').any():
                # Remove the percentage sign and convert to float
                df[col] = df[col].str.replace('[\$,]', '', regex=True).astype(float) / 100
                # Now normalize
                df[col] = df[col] / df[col].sum()
        # Data Selection
        drop_lst = ['SNAP_All_csv_Median_Home_Value_','Med__Val____00_in__10_Dollars_','SNAP_All_csv_Part_1_Crime_per_1',
                'SNAP_All_csv__Murder__2010_',
               'SNAP_All_csv__Rape__2010_', 'SNAP_All_csv__Robbery__2010_',
               'F_Agr__Assault__2010_', 'SNAP_All_csv__Burglary__2010_',
               'SNAP_All_csv__Auto_Theft__2010_', 'SNAP_All_csv__Drug_Violations__', 'SNAP_All_csv___Good___Excellent', 'SNAP_All_csv___Average_Conditio',
               'SNAP_All_csv___Poor___Derelict_', 'SNAP_All_csv_Landslide_Prone___', 'SNAP_All_csv_Woodland____of_lan', 'SNAP_All_csv_Cemetery____of_lan','Population (2010)', 'Miles of Major Roads',
               'Total Street Miles','Commute to Work: Drive Alone (2010)',
               'Commute to Work: Carpool/Vanpool (2010)',
               'Commute to Work: Public Transportation (2010)',
               'Commute to Work: Taxi (2010)', 'Commute to Work: Motorcycle (2010)',
               'Commute to Work: Bicycle (2010)', 'Commute to Work: Walk (2010)',
               'Commute to Work: Other (2010)', 'Work at Home (2010)','Neighborhood_2010_SQMILES','SNAP_All_csv_2009_Median_Income','Total Working Pop. (Age 16+) (2010)', 'SNAP_All_csv_Residential',]
        trash_lst = df[drop_lst]
        df.drop(columns=drop_lst, inplace=True)
        df.drop(columns=['Latitude', 'Longitude'], inplace=True)
        # Parking friendliness
        # (df.iloc[:, 12] + df.iloc[:, 13] - df.iloc[:, 14])/3
        # Bike friendliness
        # df.iloc[:, 2]
        # Ease of Commute
        # (df.iloc[:, 15] + df.iloc[:, 16])/2
        # Affordability
        # (-df.iloc[:, 5] + -df.iloc[:, 6] + df.iloc[:, 7] - df.iloc[:, 8])/4
        # Safety
        # (-df.iloc[:, 1] -df.iloc[:, 3] -df.iloc[:, 4] - df.iloc[:, 9] - df.iloc[:, 10] - df.iloc[:, 11])/6

        df["sum"] = mapped_param[parameters[0]]*(df.iloc[:, 12] + df.iloc[:, 13])/2 +\
            mapped_param[parameters[1]]*df.iloc[:, 2] +\
                mapped_param[parameters[2]]*(df.iloc[:, 15] + df.iloc[:, 16])/2 +\
                    mapped_param[parameters[3]]*(-df.iloc[:, 5] + -df.iloc[:, 6] + df.iloc[:, 7] - df.iloc[:, 8])/4 +\
                        mapped_param[parameters[4]]*(-df.iloc[:, 1] -df.iloc[:, 3] -df.iloc[:, 4] - df.iloc[:, 9] - df.iloc[:, 10] - df.iloc[:, 11])/6

        print(df.iloc[:,[0,-1]].values)
        df.sort_values('sum', ascending=False, inplace = True)
        # print(df.iloc[:,0].values)
        ranked_list = df.iloc[:,0].values
        
        # ranked_list = ['one', 'two', 'three', 'four', 'five'] 
        
        return render_template('index.html', parameters = parameters, ranked_list = ranked_list, param_names = param_names, rank = rank)
    else:
        parameters = ["0", "0", "0", "0", "0"]
        ranked_list = ["Please adjust the parameters and submit!"]
        return render_template(
            "index.html",
            parameters=parameters,
            ranked_list=ranked_list,
            param_names=param_names,
            rank=rank,
        )


@app.route("/details/<county>")
def details(county):
    # Get all the information of this course from each table
    detail1 = ["detail1"]
    detail2 = ["detail2"]
    detail3 = ["detail3"]
    return render_template(
        "details.html", county=county, detail1=detail1, detail2=detail2, detail3=detail3
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
