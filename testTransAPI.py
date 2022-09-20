# -*- coding: utf-8 -*-
import argparse
import sys
import os

os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.expanduser("~"), 'cacert.pem')

import uuid
import requests
import hashlib
from importlib import reload

import time
import json

reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/api'
error_Codes = (
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 116, 201, 202, 203, 205, 206, 207, 301, 302,
    303,
    304, 401, 402, 411, 412, 1001, 1002, 1003, 1004, 1201, 1301, 1411, 1412, 2003, 2004, 2005, 2006, 2201, 2301, 2411,
    2412,
    3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3201, 3301, 3302, 3303, 3411, 3412, 4001, 4002, 4003,
    4004,
    4005, 4006, 4007, 4201, 4301, 4303, 4411, 4412, 5001, 5002, 5003, 5004, 5005, 5006, 5201, 5301, 5411, 5412, 9001,
    9002,
    9003, 9004, 9005, 9301, 9303, 9411, 9412, 10001, 10002, 10004, 10201, 10301, 10411, 10412, 11001, 11002, 11003,
    11004,
    11005, 11006, 11007, 11201, 11301, 11303, 11411, 11412, 12001, 12002, 12003, 12004, 12005, 12006, 13001, 13002,
    13003,
    13004, 13004, 15001, 15002, 15003, 17001, 17002, 17003, 17004, 17004)

APP_KEY = ''
APP_SECRET = ''

KEY_CHANGED = False
search_path_first = ['.', os.path.expanduser("~")]
ini_file_path = ''
for search_first in search_path_first:
    potential_path = os.path.join(search_first, 'yd_fy_ini.json')
    if os.path.exists(potential_path):
        ini_file_path = potential_path
        break
if ini_file_path == '':
    search_paths = os.getenv('PATH')
    for search_path in search_paths.split(';'):
        potential_path = os.path.join(search_path, 'yd_fy_ini.json')
        if os.path.exists(potential_path):
            ini_file_path = potential_path
            break
if os.path.exists(ini_file_path):
    try:
        with open(ini_file_path, 'r') as ini_file:
            k_s_dict = json.load(ini_file)
            if k_s_dict is None or k_s_dict['Key'] == '' or k_s_dict['Secret'] == '':
                APP_KEY = input('Please input a Key.[Can obtain at:https://ai.youdao.com/#/]\n')
                APP_SECRET = input('Please input a Secret.[Can obtain at:https://ai.youdao.com/#/]\n')
                KEY_CHANGED = True
            else:
                APP_KEY = k_s_dict['Key']
                APP_SECRET = k_s_dict['Secret']
                # print(APP_KEY)
                # print(APP_SECRET)
    except PermissionError:
        print(f'Need higher permission or edit manually.[Path:{ini_file_path}]')
else:
    print('Not found ini_file of json. Input Key and Secret to create one...')
    APP_KEY = input('Please input a Key.[Can obtain at:https://ai.youdao.com/#/]\n')
    APP_SECRET = input('Please input a Secret.[Can obtain at:https://ai.youdao.com/#/]\n')
    KEY_CHANGED = True
if KEY_CHANGED:
    if not ini_file_path.endswith('.json'):
        ini_file_path=os.path.join(os.path.expanduser("~"),'yd_fy_ini.json')
    try:
        with open(ini_file_path, 'w') as ini_file:
            json.dump({'Key': APP_KEY, 'Secret': APP_SECRET}, ini_file)
    except PermissionError:
        print(f'Need higher permission or edit manually.[Path:{ini_file_path}]')


def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(qStr):
    q = qStr
    data = {}
    # data['from'] = 'en'
    # data['to'] = 'zh-CHS'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = "您的用户词表ID"

    # response = do_request(data)
    # contentType = response.headers['Content-Type']
    # if contentType == "audio/mp3":
    #     millis = int(round(time.time() * 1000))
    #     filePath = "合成的音频存储路径" + str(millis) + ".mp3"
    #     fo = open(filePath, 'wb')
    #     fo.write(response.content)
    #     fo.close()
    # else:
    #     print(response.content)

    r = requests.get(YOUDAO_URL, params=data).json()  # 获取返回的json()内容
    # print("err_code: " + r["errorCode"]) #获取翻译的err_code
    # print(r)  # 获取翻译内容
    # print(str(r.keys()))
    # print(r['returnPhrase'][0])
    # print(r['web'])
    MssageOut = ""
    explainMssg = ""
    phoneticMssg = ""
    webExplains = ""
    transForms = ""

    # print(type(int(r['errorCode'])))
    error_code_num = int(r['errorCode'])
    error_flag = error_code_num in error_Codes
    if error_flag:
        if error_code_num == 108:
            print('API key or secret is wrong.[Use arg \'-ks\' to change.]\n')
        else:
            print('Something went wrong.\n')
    elif r['l'] == 'en2zh-CHS':
        MssageOut += (r['query'] + '\t')
        if 'basic' in r:
            if 'phonetic' in r['basic']:
                phoneticMssg += ('[ ' + r['basic']['phonetic'] + ' ]')
                if 'us-phonetic' in r['basic'] and r['basic']['us-phonetic'] != r['basic']['phonetic']:
                    phoneticMssg += (' [ ' + r['basic']['us-phonetic'] + ' ]')
                # phoneticMssg += '\n'
            if not phoneticMssg.isspace():
                MssageOut += (phoneticMssg + '\n')
            MssageOut += '\n'
            if 'explains' in r['basic']:
                for i in range(len(r['basic']['explains'])):
                    explainMssg += ('- ' + ("".join(map(str, r['basic']['explains'][i])) + '\n'))
            if not explainMssg.isspace():
                MssageOut += explainMssg
            if 'wfs' in r['basic']:
                for i in range(len(r['basic']['wfs'])):
                    transForms += (str(r['basic']['wfs'][i]['wf']['name']) + ':' + str(
                        r['basic']['wfs'][i]['wf']['value']) + '\t\t')
            if not transForms.isspace() and "" != transForms:
                MssageOut += (transForms + '\n')
            # MssageOut += '\n'
        if 'web' in r:
            for i in range(len(r['web'])):
                webExplains += (str(i + 1) + '. ')
                webExplains += ("".join(r['web'][i]['key']) + '\n')
                webExplains += ('   ' + (",".join(map(str, r['web'][i]['value'])) + '\n'))
        if webExplains != "" and not webExplains.isspace():
            MssageOut += '\n'
        MssageOut += webExplains
        # print(MssageOut)

    elif r['l'] == 'zh-CHS2en':
        MssageOut += (r['query'] + '\t')
        if 'basic' in r:
            if 'phonetic' in r['basic']:
                phoneticMssg += ('[ ' + r['basic']['phonetic'] + ' ]')
            if not phoneticMssg.isspace():
                MssageOut += (phoneticMssg + '\n')
            MssageOut += '\n'
            if 'explains' in r['basic']:
                for i in range(len(r['basic']['explains'])):
                    explainMssg += ('- ' + ("".join(map(str, r['basic']['explains'][i])) + '\n'))
            if not explainMssg.isspace():
                MssageOut += (explainMssg + '\n')
        if 'web' in r:
            for i in range(len(r['web'])):
                webExplains += (str(i + 1) + '. ')
                webExplains += ("".join(r['web'][i]['key']) + '\n')
                webExplains += ('   ' + (",".join(map(str, r['web'][i]['value'])) + '\n'))
        MssageOut += webExplains
        # print(MssageOut)

    if not error_flag:
        if not MssageOut == (r['query'] + '\t') and not MssageOut.isspace() and "" != MssageOut:
            print(MssageOut)
        else:
            print("Warning:Not found meaningful explains.")


if __name__ == '__main__':
    # print('This is main.\n')
    # parser = argparse.ArgumentParser(description='myFyYouDaoAPI:Input Cn or En words to translate.')
    # parser.add_argument('words', type=str, nargs='+', help='Cn or En words input')
    # args = parser.parse_args()
    # print(args.words)

    if sys.argv[1].startswith('-'):
        if sys.argv[1] == '-ks':
            APP_KEY = input('Please input a Key.[Can obtain at:https://ai.youdao.com/#/]\n')
            APP_SECRET = input('Please input a Secret.[Can obtain at:https://ai.youdao.com/#/]\n')
            if APP_KEY != '' and APP_SECRET != '':
                if not ini_file_path.endswith('.json'):
                    ini_file_path = os.path.join(os.path.expanduser("~"), 'yd_fy_ini.json')
                try:
                    with open(ini_file_path, 'w') as ini_file:
                        json.dump({'Key': APP_KEY, 'Secret': APP_SECRET}, ini_file)
                except PermissionError:
                    print(f'Need higher permission or edit manually.[Path:{ini_file_path}]')
            else:
                print('Invalid Key or Secret.[Can obtain at:https://ai.youdao.com/#/]\n]')
        else:
            print("Warning:Undefined command functions.")
    else:
        args = sys.argv[1:]
        qureyStrChk = ''.join(args).replace('-', '')
        if qureyStrChk.encode('utf-8').isalpha():
            queryStr = ' '.join(args)
            connect(queryStr)
        elif is_chinese(qureyStrChk):
            queryStr = qureyStrChk
            connect(queryStr)
        else:
            print('Warning:Only support En2Cn and Cn2En.')
