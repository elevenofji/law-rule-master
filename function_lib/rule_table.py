import re
from function_lib.functions import *

# 去除句子开始的（一）、（十）
def number_zh_filter(s):
    return re.sub('^\（[一二三四五六七八九十]\）', '', s)


# 去除句子首尾的标点符号
def remove_special_character(s):
    return re.sub('^(、|，|；|。|：)+|(、|，|；|。|：)+$', '', s)

# 去除句子最后一个“的”字
def remove_last_de(s):
    return re.sub('的$', '', s)


def item_title_filter(s):
    item = re.sub('第.*?条', '',  s)
    return item


# 去除条件中的描述性文字“四、增加一款，作为第二款：”
# “第三款修改为：”
def remove_useless_desc(s):
    return re.sub('.*：', '', s)


def condition_trim(s):
    return re.sub('(，|：).*', '', s)


def remove_dun(s):
    return re.sub('^（[一二三四五六七八九十]+）', '', s)


# 判断的方法应该是看法条里有没有“（一）（二）”
def has_key_one(s):
    has_key_flag = False
    pattern = re.compile('（[一二三四五六七八九十]+）')
    sub_matcher = pattern.findall(s)
    if len(sub_matcher) >= 1:
        has_key_flag = True
    return has_key_flag


def has_key_one_plus(s):
    key1 = ['下列', '以下', '如下']
    has_key_flag = False
    for k in key1:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def has_key_two(s):
    keys = ['当', '应当', '方可', '不得', '禁止', '严禁', '可以']
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def has_key_three(s):
    reg = '(.*?)(由|按照)(.*)'
    return re.match(reg, s)


def filter_three(sentence):
    """
    :param sentence:
    :return:
    """
    data = []
    reg = '(.*?)(由|按照)(.*)'  # 匹配到第一个停下来

    matcher = re.match(reg, sentence)
    if matcher:
        data.append(matcher.group(1))
        data.append(matcher.group(2))
        data.append(matcher.group(3))
    return data

def filter_four(sentence):
    data = []
    reg = '(.*?)(责令|没收)(.*)'
    matcher = re.match(reg, sentence)
    if matcher:
        data.append(matcher.group(1))
        data.append(matcher.group(2))
        data.append(matcher.group(3))
    return data


def has_four_plus(sentence):
    keys = ['全民']
    has_key_flag = False
    for k in keys:
        if k in sentence:
            has_key_flag = True
            break
    return has_key_flag

def has_result(sen):
    with open('../data_process/result.txt', 'r',encoding='UTF-8') as f:
        lines = [line.strip() for line in f.readlines()]
        lines[0] = re.sub('\ufeff','',lines[0])
        if sen in lines:
            return True
    return False

def has_subject(sen):
    with open('../data_process/subject.txt', 'r',encoding='UTF-8') as f:
        lines = [line.strip() for line in f.readlines()]
        lines[0] = re.sub('\ufeff','',lines[0])
        if sen in lines:
            return True
    return False

def add_to_subject(s):
    with open('../data_process/subject.txt', 'a', encoding='UTF-8') as f:
        f.write(s + '\n')
    return 0

    '''
if __name__ == '__main__':
    s = '123'
    add_to_subject(s)
    print(has_subject(s))
    '''