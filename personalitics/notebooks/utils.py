import json
import re
import pandas as pd
from bs4 import BeautifulSoup

TYPES = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ',
         'ENFP', 'ISTJ', 'ISTP', 'ESTJ', 'ESTP', 'ISFJ', 'ISFP',
         'ESFJ', 'ESFP']

def unpack_topic_user(topic_user):
    x = json.loads(topic_user['topic_user'])
    x = pd.DataFrame([x])
    x['url'] = topic_user['url']
    return x

def unpack_subcomments(comment_list):
    comments = json.loads(comment_list['comment_list'])['comments']
    comments = pd.DataFrame.from_dict(comments)
    comments['url'] = comment_list['url']
    return comments

def unpack_subcomment_user(sub_user):
    user = sub_user['user']
    user = pd.DataFrame.from_dict([user])
    user['id'] = sub_user['id']
    return user.iloc[0]

def parse_type_personality_cafe(string):
    if isinstance(string, str):
        user_type = string.split(' ')
        for u in user_type:
            for t in TYPES:
                if u == t:
                    return t
    return string

def parse_type_16personality(string):
    type_ = re.findall(r'.+ \((\w+)-\w\)$', string)
    return type_[0] if type_ else string
    
def html_to_text(html):
    soup = BeautifulSoup(html.strip())
    return soup.get_text().strip()


