import time
import pymysql
import re
import uuid
from function_lib import rule_table
from model_2 import law_extract_two as lof
from function_lib.functions import *
from regex_select import sentences_to_parts

def write_to_file(res, path, flag=1):

    with open(path, 'w', encoding='UTF-8') as outfile:
        for s in res:
            if flag == 0:
                outfile.write('\t'.join(map(str, s)).replace(r'\u3000', ' ').replace('\n','') + '\n')
            else:
                outfile.write(str(s).replace(r'\u3000', ' ') + '\n')
        print('lines:', len(res))


# 驾驶机动车有下列情形之一的，处200元罚款
def regex_filter(sentences, reg):
    data = []
    for s in sentences:
        matcher = re.match(reg, s)
        if matcher:
            data.append(matcher.group())
    return data


def not_filter(sentences, reg):
    data = []
    for s in sentences:
        matcher = re.match(reg, s)
        if not matcher:
            data.append(s)
    return data

def build_condition(condition_id, sentence_id, condition):
    condition_sql = 'insert into lawcrf_condition values (%s,%s,%s)'
    condition_args = [condition_id, str(sentence_id), condition]
    write_data_to_mysql(condition_sql, [condition_args])


def build_subject(subject_id, sentence_id,  subject):
    subject_sql = 'insert into lawcrf_subject values (%s,%s,%s)'
    subject_args = [subject_id, str(sentence_id), subject]
    write_data_to_mysql(subject_sql, [subject_args])

def build_behavior(behavior_id, sentence_id, behavior, condition_id, subject_id, result_id, key_id=None):
    behavior_sql = 'insert into lawcrf_behavior values (%s,%s,%s,%s,%s,%s,%s)'
    behavior_args = [behavior_id, str(sentence_id), behavior, condition_id, subject_id, result_id,  key_id]
    write_data_to_mysql(behavior_sql, [behavior_args])

def build_result(result_id, sentence_id, result):
    result_sql = 'insert into lawcrf_result values (%s,%s,%s)'
    result_args = [result_id, str(sentence_id), result]
    write_data_to_mysql(result_sql, [result_args])

def build_key(key_id, sentence_id, key):
    key_sql = 'insert into lawcrf_key values (%s,%s,%s)'
    key_args = [key_id, str(sentence_id), key]
    write_data_to_mysql(key_sql, [key_args])


def full_result_1(data):
    # sql_1 = 'select law_item_id, full_result from lawcrflabel where template_num = 1'
    # data = get_data_from_mysql(sql_1)
    print('data size:', len(data))
    for i, t in enumerate(data[:]):
        print(str(i) + '--' + str(t))
        sentence_id = t[0]
        full_result = t[1]
        # full_result = full_result.replace("'", '"')
        # full_result_dict = json.loads(full_result, encoding='UTF-8')
        full_result_dict = full_result
        if not full_result_dict:
            continue
        condition = full_result_dict['condition']
        subject = full_result_dict['subject']
        behavior = full_result_dict['behavior']
        result = full_result_dict['result']
        # key = full_result_dict['key']

        condition_id = None
        if len(condition) > 1:
            condition_id = str(uuid.uuid1())
            build_condition(condition_id, sentence_id, condition)

        result_id = None
        if len(result) > 1:
            result_id = str(uuid.uuid1())
            build_result(result_id, sentence_id, result)

        subject_id = None
        if isinstance(subject, str):
            if len(subject) > 1:
                subject_id = str(uuid.uuid1())
                build_subject(subject_id, sentence_id, subject)
            if behavior:
                for be in behavior:
                    behavior_id = str(uuid.uuid1())
                    build_behavior(behavior_id, sentence_id, be, condition_id, subject_id, result_id,  None)
        elif isinstance(subject, list):
            for i, su in enumerate(subject):
                if su != '':
                    subject_id = str(uuid.uuid1())
                    build_subject(subject_id, sentence_id, su)
                if behavior:
                    behavior_id = str(uuid.uuid1())
                    build_behavior(behavior_id, sentence_id, behavior[i], condition_id, subject_id, result_id, None)


def full_result_2(data):
    # sql_2 = 'select law_item_id, full_result from lawcrflabel where template_num = 2'
    # data = get_data_from_mysql(sql_2)
    print('data size:', len(data))
    for i, t in enumerate(data[:]):
        print(str(i) + '--' + str(t))
        sentence_id = t[0]
        full_result = t[1]
        # full_result = full_result.replace("'", '"')
        for re in full_result:
            # full_result_dict = json.loads(re, encoding='UTF-8')
            full_result_dict = re
            if not full_result_dict:
                continue
            condition = full_result_dict['condition']
            subject = full_result_dict['subject']
            behavior = full_result_dict['behavior']
            key = full_result_dict['key']

            condition_id = str(uuid.uuid1())
            build_condition(condition_id, sentence_id, condition)

            subject_id = str(uuid.uuid1())
            build_subject(subject_id, sentence_id, subject)

            result_id = None

            key_id = str(uuid.uuid1())
            build_key(key_id, sentence_id, key)

            behavior_id = str(uuid.uuid1())
            build_behavior(behavior_id, sentence_id, behavior, condition_id, subject_id, result_id, key_id)


def full_result_3(s):
    pass


def model_result_parse(data_path, n):
    start = time.time()
    lines = read_from_file(data_path)
    sql = 'INSERT INTO lawcrflabel(law_event_id, law_item_id, law_title, full_result, template_num) VALUES(%s,%s,%s,%s,%s)'
    params = []
    for i, line in enumerate(lines[:]):
        if line == '\n':
            continue
        if i % 3 == 0:
            arr = [str(uuid.uuid1())]
            arr.extend(line.split('\t')[:2])
        elif i % 3 == 2:
            arr.append(line.replace('\n', ''))
            arr.append(n)
            params.append(arr)
            print('arr:', arr)
    write_data_to_mysql(sql, params)
    end = time.time()
    print('cost time:%s s' % str(end - start))

# 从数据库中读取杭州，浙江，国家道路交通法律，写入文件
def read_four_law():
    sql_hz = "select k.lawcheckid, k.lawcheckcolumnid, t.lawname, k.content from lawcheckcolumn k left join lawcheck t on k.lawcheckid = t.lawcheckid where k.lawcheckid = " \
             "'81cb96a1-dd38-460f-971c-f4fb00ac259e' union all " \
             "select lawid, c.id, z.TITLE, c.CONTENT from zllawcolumn c left join zllaw z on c.LAWID = z.id where LAWID in ('355250', '332819', '334395')"
    four_law_data = get_data_from_mysql(sql_hz)
    write_to_file(four_law_data, 'four_law.txt', 0)

def four_law_split():
    sql_hz = "select k.lawcheckid, k.lawcheckcolumnid, t.lawname, k.content from lawcheckcolumn k left join lawcheck t on k.lawcheckid = t.lawcheckid where k.lawcheckid = " \
             "'81cb96a1-dd38-460f-971c-f4fb00ac259e' union all " \
             "select lawid, c.id, z.TITLE, c.CONTENT from zllawcolumn c left join zllaw z on c.LAWID = z.id where LAWID in ('355250', '332819', '334395')"
    four_law_data = get_data_from_mysql(sql_hz)
    for line in four_law_data[:]:
        print(line)
        item_id, title, content = line[0], line[1], line[2]


def four_law_parse_from_file():
    four_law_data = read_from_file('four_law.txt')
    data_1 = []
    data_2 = []
    for line in four_law_data[:5]:
        contents = line.split('\t')
        law_id, item_id, title, content = contents[0], contents[1], contents[2], contents[3]
        result, num = rule_table.extract_by_regex(content)
        if not result:
            continue
        if num == 1:
            data_1.append([item_id, result])
        else:
            data_2.append([item_id, result])

    full_result_1(data_1)
    full_result_2(data_2)


# 所有法条，按照三种句模，执行成分标注
def all_law_parse(sql):
    # sql = 'select id, law_id, item_id, sentence from law_item_split'
    four_law_data = get_data_from_mysql(sql)
    data_1 = []
    data_2 = []
    data_3 = []

    for line in four_law_data[:]:
        s_id, law_id, item_id, sentence = line[0], line[1], line[2], line[3]
        result, num = sentences_to_parts(sentence)
        if not result:
            continue
        if num == 1:
            data_1.append([s_id, result])
        elif num == 2:
            data_2.append([s_id, result])
        elif num == 3:
            data_3.append([s_id, result])

    print('data_1', data_1)
    print('data_2', data_2)
    full_result_1(data_1)
    full_result_2(data_2)
    full_result_3(data_3)


def take_out_colon(num, item):
    num1 = ''
    item1 = item
    pattern = re.compile('^(.*?)：')
    sub_matcher = pattern.findall(item)
    if sub_matcher:
        num1 = num + sub_matcher[0]
        item1 = item.replace(num, '')
    return num1, item1

def take_out_num(num, item):
    num1 = ''
    item1 = item
    pattern = re.compile('^(第.*?条)')
    sub_matcher = pattern.findall(item)
    if sub_matcher:
        num1 = num + sub_matcher[0]
        item1 = item.replace(num, '')
    return num1, item1


def law_to_sentences(law_id, item_id, line):
    num = ''
    line = line.strip().replace('；', '</p>').replace('\t', '</p>').replace('。', '</p>').replace(' ', '').replace('“', '').replace('”', '')
    contents_temp = line.split('</p>')
    le = len(contents_temp)
    sen = []
    sen_id = []
    for i in range(0, le):
        item = contents_temp[i].replace('\u3000', '').replace('<p>', '').replace('</p>', '')
        item = lof.remove_dun(item)
        num, item = take_out_num(num, item)
        num, item = take_out_colon(num, item)
        if item:
            item = '<p>' + ' ' + item + '</p>'
            sen_id.append(str(uuid.uuid1()))
            sen.append(item)
        else:
            continue
    return law_id, item_id, sen_id, sen


if __name__ == '__main__':
    print()

    # 97644 交通领域的
    # traffic_sql = "select c.id, z.TITLE, c.CONTENT from zllawcolumn c inner join zllaw z on c.LAWID = z.id where z.TYPENAME like '%交通%'"
    # traffic_res = get_data_from_mysql(traffic_sql)
    # write_to_file(traffic_res, 'traffic_law.txt', 0)

    # 1134 
    # start = time.time()
    # reg = '.*有下列情形之一的.*'
    # traffic_data = read_from_file('traffic_law.txt')
    # traffic_punish_data = regex_filter(traffic_data, reg)
    # write_to_file(traffic_punish_data, 'traffic_punish_law.txt')
    # end = time.time()
    # print('cost time:%s s' % str(end - start))

    # 658 
    # start = time.time()
    # reg = '.*有下列情形之一的.*(处罚|罚款|警告|责令|处分|追究).*'
    # traffic_data = read_from_file('traffic_law.txt')
    # traffic_punish_data = regex_filter(traffic_data, reg)
    # write_to_file(traffic_punish_data, 'traffic_punish_law1.txt')
    # end = time.time()
    # print('cost time:%s s' % str(end-start))

    # 39984
    # start = time.time()
    # reg = '.*(应当|不得|禁止|严禁).*'
    # traffic_data = read_from_file('traffic_law.txt')
    # traffic_not_below_data = not_filter(traffic_data, '.*下列.*')
    # traffic_obli_forbid_data = regex_filter(traffic_not_below_data, reg)
    # write_to_file(traffic_obli_forbid_data, 'traffic_obligation_forbidden.txt')
    # end = time.time()
    # print('cost time:%s s' % str(end - start))

    # 将解析结果从文件写入数据库
    # model_result_parse('../model_2/result.out2', 2)

    # 解析full_result数据
    # full_result_1()

    # read_four_law()
    # four_law_parse()
    # four_law_split()
    # four_law_parse_from_db()

    size = 100000
    step = 10
    for i in range(size):
        sql = 'select id, law_id, item_id, sentence from law_item_split limit ' + i*step + ', ' + step
        # all_law_parse(sql)





