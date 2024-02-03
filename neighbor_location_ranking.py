import pandas as pd

csv_file_path = 'Datasets/neighborhood_match/neighborhood2Location.csv'

df = pd.read_csv(csv_file_path)

# Print the contents of the DataFrame
la = df['intptlat10']
lon = df['intptlon10']
hood = df['hood']

input = (34.21, -78.43)

tester = []
# put hood into result
for i in range(len(la)):
    if(la[i] == ' ' or lon[i] == ' '):
        continue
    temp_lst = []
    temp_lst.append(hood[i])
    temp_lst.append((la[i], lon[i]))
    temp_lst.append((float(la[i]) - input[0])**2 + (float(lon[i]) - input[1])**2)
    tester.append(temp_lst)
    # tester[i][0] = hood[i]
    # tester[i][1] = (la[i], lon[i])
    # tester[i][2] = (float(la[i]) - input[0])**2 + (float(lon[i]) - input[1])**2

tester.sort(key=lambda x: x[2], reverse=True)
print(tester[0])
