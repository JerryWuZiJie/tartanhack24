import pandas as pd
from flask import Flask, render_template, request
from sklearn.manifold import TSNE
from scipy.stats import spearmanr
import numpy as np


def scoring(rank, df):

    def tsne_score(df):
        TSNEout = TSNE(n_components=2, method="exact").fit_transform(df)
        score = TSNEout[:, 0] - TSNEout[:, 1]

        return score

    df.fillna(0, inplace=True)

    df = (df - df.min(0)) / (df.max(0) - df.min(0))

    #  spearsman corr
    corr = spearmanr(rank, df, nan_policy="omit")[0][0][1:]
    df *= corr

    score = tsne_score(df)
    score = score / score.sum()

    return corr, score


app = Flask(__name__)

df = pd.read_csv("../Datasets/post_processed.csv")
# Normalize the data sum to 1
for col in df.iloc[:, 3:]:
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col] / df[col].sum()
    if df[col].dtype == object and df[col].str.contains("%").any():
        # Remove the percentage sign and convert to float
        df[col] = df[col].str.replace("%", "").astype(float) / 100
        # Now normalize
        df[col] = df[col] / df[col].sum()
    if df[col].dtype == object and df[col].str.contains("$").any():
        # Remove the percentage sign and convert to float
        df[col] = df[col].str.replace("[\$,]", "", regex=True).astype(float) / 100
        # Now normalize
        df[col] = df[col] / df[col].sum()
# Data Selection
drop_lst = [
    "SNAP_All_csv_Median_Home_Value_",
    "Med__Val____00_in__10_Dollars_",
    "SNAP_All_csv_Part_1_Crime_per_1",
    "SNAP_All_csv__Murder__2010_",
    "SNAP_All_csv__Rape__2010_",
    "SNAP_All_csv__Robbery__2010_",
    "F_Agr__Assault__2010_",
    "SNAP_All_csv__Burglary__2010_",
    "SNAP_All_csv__Auto_Theft__2010_",
    "SNAP_All_csv__Drug_Violations__",
    "SNAP_All_csv___Good___Excellent",
    "SNAP_All_csv___Average_Conditio",
    "SNAP_All_csv___Poor___Derelict_",
    "SNAP_All_csv_Landslide_Prone___",
    "SNAP_All_csv_Woodland____of_lan",
    "SNAP_All_csv_Cemetery____of_lan",
    "Population (2010)",
    "Miles of Major Roads",
    "Total Street Miles",
    "Commute to Work: Drive Alone (2010)",
    "Commute to Work: Carpool/Vanpool (2010)",
    "Commute to Work: Public Transportation (2010)",
    "Commute to Work: Taxi (2010)",
    "Commute to Work: Motorcycle (2010)",
    "Commute to Work: Bicycle (2010)",
    "Commute to Work: Walk (2010)",
    "Commute to Work: Other (2010)",
    "Work at Home (2010)",
    "Neighborhood_2010_SQMILES",
    "SNAP_All_csv_2009_Median_Income",
    "Total Working Pop. (Age 16+) (2010)",
    "SNAP_All_csv_Residential",
]
unused = df[["Neighborhood"] + drop_lst]
trash_lst = df[drop_lst]
df.drop(columns=drop_lst, inplace=True)
df.drop(columns=["Latitude", "Longitude"], inplace=True)

parameters = ["0", "0", "0", "0", "0"]


# Landing Page, show a list of features
@app.route("/", methods=["GET", "POST"])
def index():
    global parameters
    param_names = [
        "Parking Friendliness",
        "Biking Friendliness",
        "Ease of Commute",
        "Affordability",
        "Safety",
    ]
    rank = ["Irrelevant", "Low", "Medium", "High"]
    if request.method == "POST":
        parameters = [request.form.get(param_name) for param_name in param_names]
        mapped_param = {"0": 0, "1": 0.25, "2": 0.6, "3": 1}

        df["sum"] = (
            mapped_param[parameters[0]] * (df.iloc[:, 12] + df.iloc[:, 13]) / 2
            + mapped_param[parameters[1]] * df.iloc[:, 2]
            + mapped_param[parameters[2]] * (df.iloc[:, 15] + df.iloc[:, 16]) / 2
            + mapped_param[parameters[3]]
            * (-df.iloc[:, 5] + -df.iloc[:, 6] + df.iloc[:, 7] + df.iloc[:, 8])
            / 4
            + mapped_param[parameters[4]]
            * (
                -df.iloc[:, 1]
                - df.iloc[:, 3]
                - df.iloc[:, 4]
                - df.iloc[:, 9]
                - df.iloc[:, 10]
                - df.iloc[:, 11]
            )
            / 6
        )

        df.sort_values("sum", ascending=False, inplace=True)
        ranked_list_temp = df.iloc[:, 0].values
        print("ranked_list_temp", ranked_list_temp)

        corr, undefault_score = scoring(np.array(range(len(trash_lst))), trash_lst)
        df["final_score"] = df["sum"] + 0.1 * undefault_score
        df.sort_values("final_score", ascending=False, inplace=True)
        ranked_list = df.iloc[:, 0].values

        return render_template(
            "index.html",
            parameters=parameters,
            ranked_list=ranked_list,
            param_names=param_names,
            rank=rank,
        )
    else:
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
    detail_lst = []

    temp_df = df.loc[df["Neighborhood"] == county]
    park_lst = [
        "Parking Friendliness",
        [temp_df.columns[12], temp_df.iloc[0, 12]],
        [temp_df.columns[13], temp_df.iloc[0, 13]],
    ]
    bike_lst = ["Biking Friendliness", [temp_df.columns[2], temp_df.iloc[0, 2]]]
    commute_lst = [
        "Ease of Commute",
        [temp_df.columns[15], temp_df.iloc[0, 15]],
        [temp_df.columns[16], temp_df.iloc[0, 16]],
    ]
    afford_lst = [
        "Affordability",
        [temp_df.columns[5], temp_df.iloc[0, 5]],
        [temp_df.columns[6], temp_df.iloc[0, 6]],
        [temp_df.columns[7], temp_df.iloc[0, 7]],
        [temp_df.columns[8], temp_df.iloc[0, 8]],
    ]
    safe_lst = [
        "Safety",
        [temp_df.columns[1], temp_df.iloc[0, 1]],
        [temp_df.columns[3], temp_df.iloc[0, 3]],
        [temp_df.columns[4], temp_df.iloc[0, 4]],
        [temp_df.columns[9], temp_df.iloc[0, 9]],
        [temp_df.columns[10], temp_df.iloc[0, 10]],
        [temp_df.columns[11], temp_df.iloc[0, 11]],
    ]

    temp_df = unused.loc[unused["Neighborhood"] == county]
    unused_lst = ["Other parameters"]
    for i, col in enumerate(temp_df.columns[1:]):
        unused_lst.append([col, temp_df.iloc[0, i]])

    detail_lst.append(park_lst)
    detail_lst.append(bike_lst)
    detail_lst.append(commute_lst)
    detail_lst.append(afford_lst)
    detail_lst.append(safe_lst)
    detail_lst.append(unused_lst)

    return render_template("details.html", county=county, table_list=detail_lst)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
