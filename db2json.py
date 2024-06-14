import sqlite3
import datetime
import pandas as pd
import blackboxprotobuf
import json

with open('config.json',encoding='utf-8') as f:
    config = json.load(f)


database = config['db_path']
group_id = config['group_id']

conn = sqlite3.connect(database)

c = conn.cursor()

# read group_msg_table

c.execute("SELECT * FROM group_msg_table")
rows = c.fetchall()
df = pd.DataFrame(rows, columns=[i[0] for i in c.description])
del rows


df = df[df['40030'] == group_id]


df['40033'] = df['40033'].astype('int64').astype(str) # qq number


def parsed_to_text(parsed):
    parsed_text  = ''
    if type(parsed) == dict:
        parsed = [parsed]
    try:
        for i in parsed:
            message_type = i['45002']
            if message_type == 1:
                if '45101' in i.keys():
                    if type(i['45101']) == dict:
                        continue
                    parsed_text += i['45101']
                elif '45101-2' in i.keys():
                    if type(i['45101-2']) == dict:
                        continue
                    parsed_text += i['45101-2']
            elif message_type == 2:
                parsed_text += "--某张图片--"
            elif message_type == 3:
                parsed_text += "--某个文件--"
            elif message_type == 6:
                parsed_text += f"--emj[{i['47601']}]--"
            elif message_type == 7:
                # decomment this block if you want to include quoted messages
                # parsed_text += "> "
                # if '47423' in i.keys():
                #     quoted_message_time = i['47404']
                #     quoted_message_time = datetime.datetime.fromtimestamp(quoted_message_time)
                #     quoted_message_sender = i['47403']
                #     quoted_message = parsed_to_text(i['47423'])
                # elif '47410' in i.keys():
                #     quoted_message_time = i['47410']['1']['6']
                #     quoted_message_time = datetime.datetime.fromtimestamp(quoted_message_time)
                #     quoted_message_sender = i['47410']['1']['1']
                #     quoted_message = i['47410']['3']['1']['2'][0]['1']['1']
                # parsed_text += f'[{quoted_message_time}] {quoted_message_sender}:\n> {quoted_message}\n'
                pass
            elif message_type == 11:
                parsed_text += i['80900']
            else:
                pass
    except Exception as e:
        raise e
    return parsed_text

errs = []
f = open('output\\output.json','w')
outdata = []
for index,i in df.iterrows():
    data = i['40800']
    if data == None:
        continue
    try:
        parsed,_ = blackboxprotobuf.decode_message(data)
    except Exception as e:
        print(f"BLACKBOX ERROR AT INDEX: {index}")
        errs.append(f'blackbox err {index}')
        continue
    
    out = {
        'sender': i['40033'],
        'time': datetime.datetime.fromtimestamp(i['40050']).strftime("%Y-%m-%d %H:%M:%S"),
        'msg': parsed_to_text(parsed['40800'])
    }
    outdata.append(out)

out_json = {
    'group_id': group_id,
    'updated_time': datetime.datetime.fromtimestamp(df['40050'].max()).strftime("%Y-%m-%d %H:%M:%S"),
    'data': outdata
}
f.write(json.dumps(out_json,indent=4))
f.close()

print(errs)
for i in errs:
    if len(errs) == 0:
        break
    row_index = int(i.split()[-1])
    print(df.loc[row_index])
print('done')