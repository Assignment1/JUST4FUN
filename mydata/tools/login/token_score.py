#!/usr/bin/env python
#coding:utf-8

import sys
import os
import json

def file_to_json(file):
    f = open(file)
    text = f.read()
    f.close()
    result = json.loads(text)
    return result

def score(token_schema_file,log_file,token_map_file,token_map_out,log_socre_out):
    token_map = file_to_json(token_map_file)
    logf = open(log_file,'r')
    outf = open(log_socre_out,'w')
    #title
    title = logf.readline().strip().split(',')
    outf.write(','.join(title + ['score']))
    outf.write(os.linesep)
    length = len(title)
    for line in logf:
        tmp_array = line.strip().split(',')
        if len(tmp_array) != length:
            print 'ERROR(1):',line.strip()
            continue
        id = tmp_array[title.index('id')]
        if tmp_array[0] != '':
            score = 0
            if id not in token_map :
                token_map[id] = file_to_json(token_schema_file)
            else:
                #检测是否可以加入history中
                if float(tmp_array[title.index('timestamp')]) - token_map[id]['last_timestamp'] > 3600:
                    for item in token_map[id]['citys']:
                        if item not in token_map[id]['history_citys'] :
                            token_map[id]['history_citys'][item] = 0
                        token_map[id]['history_citys'][item] += 1
                    token_map[id]['citys'] = {}
                    for item in token_map[id]['devices']:
                        if item not in token_map[id]['history_devices'] :
                            token_map[id]['history_devices'][item] = 0
                        token_map[id]['history_devices'][item] += 1
                    token_map[id]['devices'] = {}
                    for item in token_map[id]['activity_types']:
                        if item not in token_map[id]['history_activity_types'] :
                            token_map[id]['history_activity_types'][item] = 0
                        token_map[id]['history_activity_types'][item] += 1
                    token_map[id]['activity_types'] = {}
                    for item in token_map[id]['activity_times']:
                        token_map[id]['history_activity_times'][item] += token_map[id]['activity_times'][item]
                    token_map[id]['activity_times'] = {}
                    for item in token_map[id]['common_citys']:
                        if item not in token_map[id]['history_common_citys'] :
                            token_map[id]['history_common_citys'][item] = 0
                        token_map[id]['history_common_citys'][item] += 1
                    token_map[id]['common_citys'] = {}
                    for item in token_map[id]['common_ips']:
                        if item not in token_map[id]['history_common_ips'] :
                            token_map[id]['history_common_ips'][item] = 0
                        token_map[id]['history_common_ips'][item] += 1
                    token_map[id]['common_ips'] = {}
                    for item in token_map[id]['common_devices']:
                        if item not in token_map[id]['history_common_devices'] :
                            token_map[id]['history_common_devices'][item] = 0
                        token_map[id]['history_common_devices'][item] += 1
                    token_map[id]['common_devices'] = {}
                    token_map[id]['login_count'] += 1
                #常用IP,最多加1000
                if tmp_array[title.index('ip')] in token_map[id]['history_common_ips']:
                    tmp_score = 100 * 2 * token_map[id]['history_common_ips'][tmp_array[title.index('ip')]]
                    if tmp_score <= 1000:
                        score += tmp_score 
                    else:
                        score += 1000
                #print 'IP:',score
                #常用DEVICE,最多加1000
                if tmp_array[title.index('device')] in token_map[id]['history_common_devices']:
                    tmp_score = 100 * 2 * token_map[id]['history_common_devices'][tmp_array[title.index('device')]]
                    if tmp_score <= 1000:
                        score +=  tmp_score 
                    else:
                        score += 1000
                #print 'DEVICE:',score
                #常用城市,最多加400
                if tmp_array[title.index('city')] in token_map[id]['history_common_citys']:
                    tmp_score = 100 * token_map[id]['history_common_citys'][tmp_array[title.index('city')]]
                    if tmp_score <= 400:
                        score +=  tmp_score 
                    else:
                        score += 400
                #短时间切换城市,最多减1000
                if token_map[id]['last_timestamp'] != 0 and token_map[id]['last_city'] != tmp_array[title.index('city')]:
                    tmp_score = (float(tmp_array[title.index('timestamp')]) - token_map[id]['last_timestamp'])/60
                    if tmp_score <= 60:
                        score -= ((60 - tmp_score) * 5)
                        token_map[id]['history_score'] -= score
                #print 'city:',score
                if token_map[id]['login_count'] >= 8:
                    #新城市
                    if tmp_array[title.index('city')] not in token_map[id]['history_citys'] :
                        score -= 200
                        #print 'newcity:',score
                    #新设备
                    if tmp_array[title.index('device')] not in token_map[id]['history_devices'] :
                        score -= 200
                        #print 'newdevice:',score
                #if token_map[id]['login_count'] >= 20:
                    #非活跃时间
                    score -= (0.5 - token_map[id]['history_activity_times'][tmp_array[title.index('time')].split()[1].split(':')[0]]/sum(token_map[id]['history_activity_times'].values())) * 1000
                    #print 'newtime:',score
                    #非常用类型
                    if tmp_array[title.index('type')] not in token_map[id]['history_activity_types']:
                        token_map[id]['history_activity_types'][tmp_array[title.index('type')]] = 0
                    score -= (0.5 - token_map[id]['history_activity_types'][tmp_array[title.index('type')]]/sum(token_map[id]['history_activity_types'].values())) * 500
                    #print 'newtype:',score
            if tmp_array[title.index('city')] not in token_map[id]['citys']:
                token_map[id]['citys'][tmp_array[title.index('city')]] = 1
            if tmp_array[title.index('device')] not in token_map[id]['devices']:
                token_map[id]['devices'][tmp_array[title.index('device')]] = 1
            #if tmp_array[title.index('ip')] not in token_map[id]['ips']:
            #    token_map[id]['ips'][tmp_array[title.index('ip')]] = 1
            if tmp_array[title.index('type')] not in token_map[id]['activity_types']:
                token_map[id]['activity_types'][tmp_array[title.index('type')]] = 1
            if float(tmp_array[title.index('timestamp')]) - token_map[id]['last_timestamp'] > 3600:
                stype = (float(tmp_array[title.index('timestamp')]) - token_map[id]['last_timestamp']) / 3600
                token_map[id]['history_score'] = token_map[id]['history_score'] / stype
            token_map[id]['activity_times'][tmp_array[title.index('time')].split()[1].split(':')[0]] = 1
            token_map[id]['last_city'] = tmp_array[title.index('city')]
            token_map[id]['last_device'] = tmp_array[title.index('device')]
            token_map[id]['last_ip'] = tmp_array[title.index('ip')]
            token_map[id]['last_timestamp'] = float(tmp_array[title.index('timestamp')])
            token_map[id]['new_login'] = True
            #print '11:',score,token_map[id]['current_score'],token_map[id]['history_score']
            token_map[id]['current_score'] = score
            token_map[id]['history_score'] = 0.7 * score + 0.3 * token_map[id]['history_score']
            #print 'new:',score,token_map[id]['current_score'],token_map[id]['history_score']
        else:
            if id not in token_map:
                token_map[id] = file_to_json(token_schema_file)
            else:
                risk = tmp_array[title.index('is_risk')]
                if token_map[id]['new_login']:
                    if risk == '0':
                       if token_map[id]['last_city'] not in token_map[id]['common_citys']:
                           token_map[id]['common_citys'][token_map[id]['last_city']] = 1
                       if token_map[id]['last_device'] not in token_map[id]['common_devices']:
                           token_map[id]['common_devices'][token_map[id]['last_device']] = 1
                       if token_map[id]['last_ip'] not in token_map[id]['common_ips']:
                           token_map[id]['common_ips'][token_map[id]['last_ip']] = 1
            token_map[id]['new_login'] = False
        outf.write(line.strip() + ',' + str(token_map[id]['history_score']))
        outf.write(os.linesep)
    logf.close()
    mapf = open(token_map_out,'w')
    mapf.write(json.dumps(token_map))
    mapf.close()

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print 'Usage:',sys.argv[0],'<token-schema> <log-file> <load-token-map> <new-token-map> <log-result-file>'
        exit()
    score(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    print 'Done!'
