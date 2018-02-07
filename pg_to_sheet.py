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
    l = df.index[(df ['sottorete'] == sottorete) & (df ['t'] == 1) & (df ['id'] == id)].tolist()
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
    df1 = df[(df ['sottorete'] == sottorete) & (df ['t'] == 1) & (df ['id'] == id)].iloc[:,7:21]  # the : in the first position indicates all rows
    wks.set_dataframe(df1,'A57', nan='')

def edit_wks_route_list (sh, df, id, sottorete):
    wks = sh.worksheet_by_title(id)
    df1 = df[((df ['sottorete'] == sottorete) & df ['t'] == 1) & (df ['id'] == id)].iloc[:,0:7]
    df1 = df1.drop_duplicates()
    wks.set_dataframe(df1,'A52', nan='')
    route_code = df1.iloc[0]['route_code']#['route_short_name']
    wks.update_cell ('C6', route_code)
    route_short_name = df1.iloc[0]['route_short_name']
    wks.update_cell ('C7', route_short_name)


def edit_wks_shp (sh, df, id, sottorete):
    wks = sh.worksheet_by_title(id)
    df1 = df[(df ['sottorete'] == sottorete) & (df ['t'] == 0) & (df ['id'] == id)].iloc[:,7:]
    table = [ [ None for i in range(10) ] for j in range(100) ]
    c = 0
    for i in [1,2,3,4]:
        df2 =  df1[(df1 ['r'] == i)]
        df2 = df2.where((pd.notnull(df2)), None)
        if df2.empty:
            break
        else:
            trip_short_name = df2.iloc[0]['trip_short_name']
            table [0+c][1] = trip_short_name
            start_stop = df2.iloc[0]['_0_da']
            end_stop = df2.iloc[0]['_0_a']
            table [2+c][2] = start_stop
            table [3+c][2] = end_stop
            shape_id_0 = df2.iloc[0]['_0_shape_id']
            shape_id_1 = df2.iloc[0]['_1_shape_id']
            table [2+c][4] = shape_id_0
            table [3+c][4] = shape_id_1
            length_0 = round(df2.iloc[0]['_0_length']/1000,2)
            length_1 = round(df2.iloc[0]['_1_length']/1000,2)
            table [2+c][5] = length_0
            table [3+c][5] = length_1

            PM_0 = df2.iloc[0]['_0_max_t_morn']
            M_0	= df2.iloc[0]['_0_avg_t_morn']
            PP_0 = df2.iloc[0]['_0_max_t_aft']
            ser_0 = df2.iloc[0]['_0_avg_t_night']
            table [2+c][6] = PM_0
            table [2+c][7] = M_0
            table [2+c][8] = PP_0
            table [2+c][9] = ser_0

            PM_1 = df2.iloc[0]['_1_max_t_morn']
            M_1	= df2.iloc[0]['_1_avg_t_morn']
            PP_1 = df2.iloc[0]['_1_max_t_aft']
            ser_1 = df2.iloc[0]['_1_avg_t_night']
            table [3+c][6] = PM_1
            table [3+c][7] = M_1
            table [3+c][8] = PP_1
            table [3+c][9] = ser_1
            c+=8
    wks.update_cells (crange='B19', values=table)
    return (id,'https://docs.google.com/spreadsheets/d/' + str(sh.id) + '/edit#gid=' + str(wks.id))


def main():
    filename = 'data/pg_sheet_1_.csv'
    gc = pygsheets.authorize(outh_file='client_secret.json')
    df = pd.read_csv(filename, delimiter=';')
    list_id =[]
    list_url = []
    for j in get_sheet_name (df):
        sheet_name='SDF_'+ j
        sh = gc.open(sheet_name)
        for i in get_id (df):
            if i in list_id:
                continue
            else:
                if check_change_sheet (df, i, j) != j :
                    add_wks (sh, str(i))
                    edit_wks_shp_list (sh, df, i, j)
                    edit_wks_route_list (sh, df, i, j)
                    edit_wks_shp (sh, df, i, j)
                    print 'created in file SDF_'+j +' worksheet  ' + str(i)
                    list_id.append(i)
                    list_url.append(edit_wks_shp (sh, df, i, j))
                    break
                else:
                    add_wks (sh, str(i))
                    edit_wks_shp_list (sh, df, i, j)
                    edit_wks_route_list (sh, df, i, j)
                    edit_wks_shp (sh, df, i, j)
                    list_id.append(i)
                    list_url.append(edit_wks_shp (sh, df, i, j))
                    print 'created in file SDF_'+j +' worksheet  ' + str(i)
                    time.sleep(10)

    df=pd.DataFrame.from_records (list_url, columns = ['id','url'])
    df.to_csv('data/url.csv')


if __name__ == "__main__":
    main()
