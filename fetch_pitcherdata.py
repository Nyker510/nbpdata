from lxml import html
import pandas as pd
import os

def fetch_tabledata_from(url):
    '''指定されたurlのテーブルからデータを読み込みます

    対象とするのはhttp://baseballdata.jp/です。

    @url: string.
        target url string.

    return: pandas.DataFrame.
    '''

    # 最初は requestsとか使っていたけど
    # 何故かこうしないとencode, decodeがうまく行かない。 後で調べる
    parser = html.HTMLParser(encoding='utf8')
    tree = html.parse(url,parser)

    data = []
    for i,tr in enumerate(tree.xpath('//tr')):
        tr_data = []
        for td in tr.iterchildren():
            txt = td.text_content()
            txt = txt.replace('\r\n','').replace('\n','').replace(' ','').replace('　','')
            tr_data.append(txt)
        data.append(tr_data)

    df = pd.DataFrame(data)
    # 重複するのはカラム名の部分なので削除する
    df = df[~df.duplicated()]
    df.columns = df.iloc[0,:]
    df = df.drop(df.index[0])
    return df

def convert2pretty(df):

    df['選手名'] = df['選手名'].str.split(':').str[1]
    df.index = range(len(df))

    # 投球回から獲得アウトカウントに変換
    df['get_out'] = df['投球回'][~df['投球回'].str.contains('/')].astype('int') * 3

    has_hasu = df['投球回'].str.contains('/')
    df.loc[has_hasu, 'get_out'] = df['投球回'][has_hasu].str[:-3].astype('int') * 3 + df['投球回'][has_hasu].str[-3].astype('int')
    del df['一軍']
    return df

def save_to(df, folder_path='data', name='pitcher.csv'):

    if os.path.exists(folder_path) is False:
        os.mkdir(folder_path)

    filepath = os.path.join(folder_path,name)
    print('save to {filepath}'.format(**locals()))
    df.to_csv(filepath)

if __name__ == '__main__':

    df_all = None
    team_ids = [1,2,3,4,5,6,7,8,9,11,12,376] #楽天が376

    for i in team_ids:
        for year in range(2012,2017):
            target_url = 'http://baseballdata.jp/{year}/{i}/cptop.html'.format(**locals())
            df_y = fetch_tabledata_from(target_url)
            print('url: {target_url}'.format(**locals()))
            df_y['year'] = year
            if df_all is None:
                df_all = df_y
            else:
                df_all = pd.concat([df_all,df_y])

    df_all = convert2pretty(df_all)
    save_to(df_all)
