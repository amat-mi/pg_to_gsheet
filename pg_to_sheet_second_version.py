import pygsheets
import csv
import pandas as pd
from numpy import nan
import time


def get_id(df):
    df_id = df ['id'].unique() #.astype(str)
    return df_id

def get_sheet_name (df):
    df_sottorete = df ['sottorete'].unique() #.astype(str)
    return df_sottorete

def check_change_sheet (df, id, sottorete):
    l = df.index[(df ['sottorete'] == sottorete) & (df ['id'] == id)].tolist()
    if not l:
        pass
    else:
        if max(l) + 1 < len(df):
            ind = max(l) + 1
            return df.iloc[ind]['sottorete']
        else:
            return None


def add_wks (sh, id):
    wks = sh.add_worksheet(id, src_worksheet = sh.worksheet_by_title("MODELLO"))

def edit_wks_shp_list (sh, df, id, sottorete):
    wks = sh.worksheet_by_title(id)
    df1 = df[(df ['sottorete'] == sottorete)  & (df ['id'] == id)].iloc[:,7:22]  # the : in the first position indicates all rows
    wks.set_dataframe(df1,'A57', nan='')

def edit_wks_route_list (sh, df, id, sottorete):
    wks = sh.worksheet_by_title(id)
    df1 = df[((df ['sottorete'] == sottorete)) & (df ['id'] == id)].iloc[:,0:7]
    df1 = df1.drop_duplicates()
    wks.set_dataframe(df1,'A52', nan='')
    route_code = df1.iloc[0]['route_code']#['route_short_name']
    wks.update_cell ('C6', route_code)
    route_short_name = df1.iloc[0]['route_short_name']
    wks.update_cell ('C7', route_short_name)
    return (id,'https://docs.google.com/spreadsheets/d/' + str(sh.id) + '/edit#gid=' + str(wks.id))


def main():
    filename = 'data/pg_sheet_second_version_.csv'
    gc = pygsheets.authorize(outh_file='client_secret.json')
    df = pd.read_csv(filename, delimiter=';')
    list_id =[]
    list_url = []
    for j in get_sheet_name (df):
        sheet_name='SDF___'+ j
        sh = gc.open(sheet_name)
        for i in get_id (df):
            if i in list_id:
                continue
            else:
                if check_change_sheet (df, i, j) != j :
                    add_wks (sh, str(i))
                    edit_wks_shp_list (sh, df, i, j)
                    edit_wks_route_list (sh, df, i, j)
                    print 'created in file SDF_'+j +' worksheet  ' + str(i)
                    list_id.append(i)
                    list_url.append(edit_wks_route_list (sh, df, i, j))
                    break
                else:
                    add_wks (sh, str(i))
                    edit_wks_shp_list (sh, df, i, j)
                    edit_wks_route_list (sh, df, i, j)
                    list_id.append(i)
                    list_url.append(edit_wks_route_list  (sh, df, i, j))
                    print 'created in file SDF_'+j +' worksheet  ' + str(i)
                    time.sleep(30)

    df=pd.DataFrame.from_records (list_url, columns = ['id','url'])
    df.to_csv('data/url.csv')


if __name__ == "__main__":
    main()
