import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import jieba
from wordcloud import WordCloud
import re

file_path = 'output\\output.json'
with open(file_path,encoding='utf-8') as f:
    data = json.load(f)

with open('config.json',encoding='utf-8') as f:
    config = json.load(f)

df = pd.DataFrame(data['data'])
output_list = []
nicknames = config['nicknames']
exclude_word = set(config['exclude_word'])


output_list.append('# 聊天记录分析\n\n')
output_list.append(f'群号：{config["group_id"]}\n\n')
# activity graph
output_list.append('## 活动图\n\n')
dates = pd.to_datetime(df['time'])

dates = dates.dt.date

activities = dates.groupby(dates).size().reindex(pd.date_range(dates.min(), dates.max(), freq='D')).fillna(0).astype(int).tolist()

activities = [0 for i in range(30-len(activities)%30)] + activities

activities = np.array(activities).reshape(-1,30)
output_list.append('从上到下，从左到右，颜色越深表示消息越多，一格代表一天，一行表示30天\n\n')
plt.figure(figsize=(20,24))
plt.pcolormesh(np.log(activities[::-1,:]+1),cmap='Greens',edgecolors='w',linewidth=1.5)
plt.axis('off')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 24
plt.title(f'从 {dates.min()} 到 {dates.max()}')
plt.savefig('output\\activity.png',bbox_inches='tight')
output_list.append('![活动图](activity.png)\n\n')

max_activity_date = dates.groupby(dates).size().reindex(pd.date_range(dates.min(), dates.max(), freq='D')).fillna(0).astype(int).idxmax()
max_activity = dates.groupby(dates).size().reindex(pd.date_range(dates.min(), dates.max(), freq='D')).fillna(0).astype(int).max()
output_list.append(f'最活跃的一天是{max_activity_date.date()}，共有{max_activity}条消息。\n\n')

output_list.append('## 消息统计\n\n')

data_types = ('总消息','总字符','表情/表情包','图片','平均字符数')
msg_stats = {}
for i in df['sender'].unique():
    msg_count = len(df[df['sender']==i])
    char_count = df[df['sender']==i]['msg'].str.len().sum()
    emj_count  = df[df['sender']==i]['msg'].str.count('--emj').sum()
    img_count = df[df['sender']==i]['msg'].str.count('--某张图片--').sum()
    msg_stats[nicknames[i]] = (msg_count,char_count,emj_count,img_count,char_count/msg_count)
    output_list.append(f'{nicknames[i]}一共发送了 {msg_count} 条消息，共计 {char_count} 个字符，其中有 {emj_count} 个表情/表情包，{img_count} 张图，平均每条消息 {char_count/msg_count:.2f} 个字符。\n')

width = 0.2
index = 0
x = np.arange(len(data_types))
fig, ax = plt.subplots(figsize=(26,10),layout='constrained')
colors = ['#8ECFC9','#FFBE7A',"#FA7F6F","#82B0D2"]

for data_type, data in msg_stats.items():
    offset = width*index
    bar = ax.bar(x+offset,data*np.array([10,1,100,100,8000]),width,label=data_type,color=colors[index])
    ax.bar_label(bar,labels=[f'{i:.0f}' for i in data],padding=3)
    index += 1


ax.set_xticks(x + width, data_types)
ax.set_yticks([])
ax.legend()
plt.savefig('output\\msg_stats.png')
output_list.append('![消息统计](msg_stats.png)\n\n')

# wordcloud
for i in df['sender'].unique():
    text = df[df['sender']==i]['msg'].str.cat(sep=' ').replace('--某张图片--',' ').replace('--某个文件--',' ').replace('>',' ')
    pattern = r'--emj\[\d+\]--'
    text = re.sub(pattern,' ',text) # 尝试去除表情
    text = re.sub(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \d+:\\n',' ',text) # 尝试去除时间戳
    text = re.sub(r'\d+', ' ', text) # 尝试去除数字
    for j in nicknames.values():
        text = text.replace(j,'')
    text = text.replace('\n',' ')
    chinese = re.compile(r'[\u4e00-\u9fa5]')
    eng_text = chinese.sub(' ',text) # 获得纯英文文本
    eng_text = re.sub(r'[^\w\s]', '', eng_text) # 去除各种符号
    eng_list = eng_text.split()

    text_list = jieba.lcut(text,cut_all=False)
    text_list = [i for i in text_list if len(i)>1]
    processed_text = ' '.join(text_list+eng_list)
    wc = WordCloud(font_path='SmileySans-Oblique.ttf',background_color='white',width=800,height=600,
                   max_words=75,max_font_size=100,stopwords=exclude_word).generate(processed_text)
    plt.figure(figsize=(12,9))
    plt.imshow(wc)
    plt.axis('off')
    plt.savefig(f'output\\wordcloud_{nicknames[i]}.png',bbox_inches='tight')
output_list.append('## 词云\n\n')
for i in df['sender'].unique():
    output_list.append(f'**{nicknames[i]}的词云**\n\n')
    output_list.append(f'![{nicknames[i]}的词云](wordcloud_{nicknames[i]}.png)\n\n')


# if output.md exists, delete it

if os.path.exists('output\\output.md'):
    print('output.md exists, deleting...')
    os.remove('output.md')

with open('output\\output.md','w',encoding='utf-8') as f:
    f.write('\n'.join(output_list))
    