import pandas as pd
import numpy as np
import urllib
import sqlite3
import re
import pickle


### cs-uri-query 문자열 유효성 검정 및 파싱
def get_cs_query_dict(txt, res_dict):
    sp_parse = urllib.parse.unquote(urllib.parse.unquote(txt))
    sp = sp_parse.split('&')
    sent_ids_length = 0
    t, p, m, c = 0, 0, 0, 0

    if not sp[0].startswith('t'):
        return False

    # 항목별 데이터 저장
    for s in sp:
        sp2 = s.split('=')
        key = sp2[0]
        value = re.sub(r'[\[\]"]', '', sp2[1])

        if key == 't':
            t = 1
            t_value = value

        elif key == 'p':
            p = 1
            value_split = value.split(',')
            p_split = []
            p_ids_freqs = []

            for i in range(0, len(value_split), 2):
                for _ in range(int(value_split[i + 1])):
                    p_ids_freqs.append(value_split[i + 1])
                    p_split.append(value_split[i])

            preview_ids = ','.join(p_split)
            preview_ids_length = len(p_split)
            preview_ids_freqs = ','.join(p_ids_freqs)

        elif key == 'm':
            m = 1
            m_value = value

        elif key == 'c':
            c = 1
            value_split = value.split(',')
            c_split = []
            c_ids_freqs = []

            for i in range(0, len(value_split), 2):
                for _ in range(int(value_split[i + 1])):
                    c_ids_freqs.append(value_split[i + 1])
                    c_split.append(value_split[i])

            sent_ids = ','.join(c_split)
            sent_ids_length = len(c_split)
            sent_ids_freqs = ','.join(c_ids_freqs)

    # 유효성 체크
    if (t + p + m) != 3:
        print('invalid', end='/')
        return False

    # 전송 여부에 따른 딕셔너리 업데이트
    res_dict['type'].append(t_value)
    res_dict['sticker_preview_ids'].append(preview_ids)
    res_dict['sticker_preview_ids_len'].append(preview_ids_length)
    res_dict['sticker_preview_ids_freq'].append(preview_ids_freqs)
    res_dict['provider'].append(m_value)

    if c:
        # 스티커 전송
        res_dict['sticker_sent_ids'].append(sent_ids)
        res_dict['sticker_sent_ids_len'].append(sent_ids_length)
        res_dict['sticker_sent_ids_freq'].append(sent_ids_freqs)
        res_dict['is_sticker_sent'].append(1)

    else:
        # 스티커 전송하지 않음
        res_dict['sticker_sent_ids'].append('')
        res_dict['sticker_sent_ids_len'].append(0)
        res_dict['sticker_sent_ids_freq'].append(0)
        res_dict['is_sticker_sent'].append(0)

    return True


####################################
### 데이터 불러오기, 파싱 및 전처리 데이터프레임 생성 ###
####################################

def load_and_parse_data(data_dir):
    df_li = []
    for h in range(24):
        fpath = f'{path}merged_{h}.csv'
        df = pd.read_csv(fpath)[['date', 'time', 'cs-uri-query']]
        res = {info: [] for info in ['date',
                                     'type', 'sticker_preview_ids', 'sticker_preview_ids_len',
                                     'sticker_preview_ids_freq',
                                     'provider', 'sticker_sent_ids', 'sticker_sent_ids_len',
                                     'sticker_sent_ids_freq',
                                     'is_sticker_sent']}

        idx_to_drop = []
        for i, query in enumerate(df['cs-uri-query']):
            rsp = get_cs_query_dict(query, res)
            if not rsp:
                idx_to_drop.append(i)

        df = df.drop(idx_to_drop).reset_index(drop=True)

        assert len(df) == len(pd.DataFrame(res))

        df = pd.concat([df[['time']], pd.DataFrame(res)], axis=1)

        assert df.isnull().sum().sum() == 0

        # RTS (Real Time Service) type = 0
        # TAG type = 1
        # POPULAR type = 2
        df.type = df.type.map({'R': 0, 'T': 1, 'P': 2})

        df = df.astype({'date':'object',
                        'time': 'object',
                        'type': 'int8',
                        'sticker_preview_ids': 'object',
                        'sticker_preview_ids_len': 'int32',
                        'sticker_preview_ids_freq': 'object',
                        'sticker_sent_ids': 'object',
                        'sticker_sent_ids_len': 'int16',
                        'sticker_sent_ids_freq': 'object',
                        'is_sticker_sent': 'int8'})
        df_li.append(df)
        print(h, end='/')


    # 데이터프레임 합치기
    tot_df = df_li[0]
    for df_ in df_li[1:]:
        tot_df = pd.concat([tot_df, df_]).reset_index(drop=True)


    # 전처리 데이터프레임으로부터 필요한 정보만 가져오기

    # type = 0 (RTS only)
    rts = tot_df[tot_df['type']==0]
    #print(prep_total_type0.shape)

    # is_sticker_sent = 1
    rts_commit = rts[rts['is_sticker_sent']==1]
    #print(prep_total_type0_sent1.shape)

    # sticker_preview_ids_len <= 30
    # sticker_sent_ids_len == 1
    cond_pid_len_lte_30 = rts_commit['sticker_preview_ids_len'] <= 30
    cond_sid_len_eq_1 = rts_commit['sticker_sent_ids_len'] == 1
    rts_commit_pid30_sid1 = rts_commit[cond_pid_len_lte_30 & cond_sid_len_eq_1]

    # reset index
    rts_commit_pid30_sid1 = rts_commit_pid30_sid1.reset_index(drop=True)

    return rts_commit_pid30_sid1

#########################
##### DB 데이터 불러오기 #####
#########################
def load_db_info(db_path):
    conn = sqlite3.connect("./data/db/glxDistributionData_2021-02-15_2021-04-05.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    getAll_query = '''
        SELECT 
            dist."distributionType" AS "distributionType",
            stk."objectId" AS "objectId",
            dist."createdAt" AS "createdAt",
            dist_d."order" AS "order",
            dist_d."tag" AS "tag" 
        FROM
            distribution_data AS dist_d 
            LEFT JOIN distribution AS dist
                ON dist_d."distributionId" = dist.id
            LEFT JOIN sticker AS stk
                ON dist_d."stickerId" = stk.id;
    '''

    cur.execute(getAll_query)
    rows = cur.fetchall()
    df_db = pd.DataFrame(rows, columns=['distributionType', 'objectId', 'createdAt', 'order', 'tag'])
    df_db['createdAt_yyyymmdd'] = df_db['createdAt'].apply(lambda x: x[:-10].split(' ')[0].replace('-', '/'))
    # df_db['createdAt_yyyymmddhh'] = df_db['createdAt'].apply(lambda x: x[:-10].split(' ')[0].replace('-', '/')+'/'+x[:-10].split(' ')[1])
    df_db = df_db.drop('createdAt', axis=1)

    df_db_pop = df_db[df_db['distributionType']=='popular']
    df_db_rts = df_db[df_db['distributionType']=='e2s']
    df_db_tag = df_db[df_db['distributionType']=='t2s']

    # print(df_db_rts['createdAt_yyyymmdd'].unique())
    # print(df_db_pop['createdAt_yyyymmdd'].unique())
    # print(df_db_tag['createdAt_yyyymmdd'].unique())

    df_db_rts_dt_tag_groupby = df_db_rts.groupby(['createdAt_yyyymmdd', 'tag'])['objectId'].apply(lambda x: ','.join(x))
    # print(df_db_rts_dt_tag_groupby.index[:3])
    # print(df_db_rts_dt_tag_groupby[:3])

    e2s = {}

    for idx in df_db_rts_dt_tag_groupby.index:

        preview_sticker_ids = df_db_rts_dt_tag_groupby[idx]

        # RTS preview list length (max) = 9
        preview_sticker_ids_split = preview_sticker_ids.split(',')
        preview_length = len(preview_sticker_ids_split)

        # 9개보다 길면 자름
        if preview_length > 9:
            preview_sticker_ids_split = preview_sticker_ids_split[:9]

        preview_sticker_ids = ','.join(preview_sticker_ids_split)
        yyyymmdd = idx[0]
        #     yyyymmdd = yyyymmddhh[:-3]
        #     hh = yyyymmddhh[-2:]
        emoji = idx[1]

        if yyyymmdd not in e2s.keys():
            e2s[yyyymmdd] = {}

        #     e2s[yyyymmdd]['hour'] = hh
        e2s[yyyymmdd][emoji] = preview_sticker_ids

    s2e = {datetime: {v: k for k, v in e2p.items()} for datetime, e2p in e2s.items()}
    return s2e



def tag_inference(df_rts, distributionData):
    # s2e 딕셔너리로부터 전체 배포일자를 int 형변환하여 가져오기
    distribute_datetimes = sorted([int(d.replace('/','')) for d in list(s2e.keys())])

    idx_to_keep, tags_inferenced, commit_sticker_pos_inferenced = [], [], []
    for i, row in rts_commit_pid30_sid1.iterrows():
        # 직전 배포일 찾기
        # current_datetime = int(row['datetime'].replace('/', ''))
        current_datetime = row['datetime']
        datetime_diff = [(dd - current_datetime) for dd in distribute_datetimes \
                         if dd <= current_datetime]
        nearest_date_idx = datetime_diff.index(max(datetime_diff))
        nearest_date = list(s2e.keys())[nearest_date_idx]  # s2e = sticker2emoji dictionary

        # 직직전 배포일 찾기
        if nearest_date_idx > 0:
            second_nearest_date_idx = nearest_date_idx - 1
            second_nearest_date = list(s2e.keys())[second_nearest_date_idx]  # s2e = sticker2emoji dictionary
        else:
            # 존재하지 않으면 0 할당
            second_nearest_date = 0

        # sticker_preview_ids (스티커 배치 순서 X) 및 전송 스티커 id 가져오기
        current_preview = row['sticker_preview_ids'].split(',')
        current_commit = row['sticker_sent_ids']

        # 직전 배포 데이터와 직직전 배포 데이터가 모두 존재할 경우
        if second_nearest_date:

            # 직전 배포 데이터부터 검색
            # 직전 배포 데이터에서 commit sticker를 포함하는 리스트 (=가능성 있는 후보) 검색
            cand_nearest_date = [s.split(',') for s in s2e[nearest_date].keys() if current_commit in s]

            # cand_nearest_date 리스트를 순회하면서 current preview를 부분집합으로 갖는 배포 리스트가 존재하는지 확인
            found_li = []
            for cnd in cand_nearest_date:
                cnd_includes_cp = set(current_preview).issubset(set(cnd))
                cp_includes_cnd = set(cnd).issubset(set(current_preview))
                if cnd_includes_cp or cp_includes_cnd:
                    found_li.append(cnd)

            # 찾지 못함
            if not found_li:
                pass  # 직직전 배포 데이터 확인 코드로 이동

            # 일치하는 리스트가 단 1개만 존재함
            elif len(found_li) == 1:
                # 현재 dataframe row index, inferenced tag, inferenced pos 저장
                idx_to_keep.append(i)
                tags_inferenced.append(s2e[nearest_date][','.join(found_li[0])])
                commit_sticker_pos_inferenced.append(found_li[0].index(current_commit))
                continue  # 다음 iteration으로 이동

            else:
                # 복수의 후보 리스트를 발견했음 ---> advanced inference 필요
                pass  # 직직전 배포 데이터 확인 코드로 이동

            # 존재하지 않는다면 직직전 배포 데이터에서 commit sticker를 포함하는 리스트 찾기
            cand_second_nearest_date = [s.split(',') for s in s2e[second_nearest_date].keys() \
                                        if current_commit in s.split(',')]

            # cand_second_nearest_date 리스트를 순회하면서 current preview를 부분집합으로 갖는 배포 리스트가 존재하는지 확인
            found_li = []
            for csnd in cand_second_nearest_date:
                cnd_includes_cp = set(current_preview).issubset(set(cnd))
                cp_includes_cnd = set(cnd).issubset(set(current_preview))
                if cnd_includes_cp or cp_includes_cnd:
                    found_li.append(csnd)

            # 찾지 못함
            if not found_li:
                pass

            # 일치하는 리스트가 단 1개만 존재함
            elif len(found_li) == 1:

                # 현재 dataframe row index와 inferenced tag 저장
                idx_to_keep.append(i)
                tags_inferenced.append(s2e[second_nearest_date][','.join(found_li[0])])
                commit_sticker_pos_inferenced.append(found_li[0].index(current_commit))
                continue  # 찾았으므로 다음 iteration으로 이동
            else:
                # 복수의 후보 리스트를 발견했음 ---> advanced inference 필요
                pass

        # 직전 배포 데이터만 존재하는 경우
        # 위 예제 코드에서는 존재할 수 없는 경우이므로 생략
        # else:
        #     pass


    rts_commit_pid30_sid1_inferenced = rts_commit_pid30_sid1.iloc[idx_to_keep]
    rts_commit_pid30_sid1_inferenced['tag'] = tags_inferenced
    rts_commit_pid30_sid1_inferenced['sticker_sent_pos'] = commit_sticker_pos_inferenced

    #########################
    ##### emoji to text #####
    #########################

    keytoken2Category = pd.read_csv('./data/dictionary/297 EmojiCategory - keytoken2Category.csv')
    keytoken2Category = keytoken2Category[['icon', 'Category.1']]

    keytoken2Category_dict = {icon:cat for (icon, cat) in zip(keytoken2Category['icon'],
                                     keytoken2Category['Category.1'])}

    rts_commit_pid30_sid1_inferenced['sticker_sent_tag_text'] = rts_commit_pid30_sid1_inferenced['tag'].map(keytoken2Category_dict)

    return rts_commit_pid30_sid1_inferenced


######################################################
###### EM 알고리즘 모델에 적합한 Dictionary 형태로 변환 #######
######################################################



def transform_data(preprocessed):
    result = {}
    for i, row in rts_commit_pid30_sid1_inferenced.iterrows():
        q = row['sticker_sent_tag_text']
        d_list = row['sticker_preview_ids_ordered'].split(',')
        sent_d = row['sticker_sent_ids']

        if q not in result.keys():
            result[q] = {}

        for k, d in enumerate(d_list):
            if d not in result[q].keys():
                result[q][d] = {k: {0: 0,
                                    1: 0}}
            if k not in result[q][d].keys():
                result[q][d][k] = {0: 0,
                                   1: 0}

            # 전송하지 않은 스티커
            if d != sent_d:
                try:
                    result[q][d][k][0] += 1
                except:
                    print(result)
                    print(q, d, k)
            # 전송한 스티커
            else:
                result[q][d][k][1] += 1

    # print('Preprocessing finished.')
    # print(result)
    return result

