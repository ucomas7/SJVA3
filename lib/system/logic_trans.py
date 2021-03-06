# -*- coding: utf-8 -*-
#########################################################
# python
import os, sys
import traceback
import json

# third-party
from flask import Blueprint, request, Response, send_file, render_template, redirect, jsonify


# sjva 공용
from framework.logger import get_logger
from framework import path_app_root, py_urllib2, py_urllib
from framework.util import Util

# 패키지
from .plugin import package_name, logger
from .model import ModelSetting

class SystemLogicTrans(object):
    @staticmethod
    def process_ajax(sub, req):
        try:
            if sub == 'trans_test':
                ret = SystemLogicTrans.trans_test(req)
                return jsonify(ret)
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
    
    @staticmethod
    def process_api(sub, req):
        ret = {}
        try:
            if sub == 'do':
                text = req.args.get('text')
                source = req.args.get('source')
                target = req.args.get('target')
                if source is None:
                    source = 'ja'
                if target is None:
                    target = 'ko'
                tmp = SystemLogicTrans.trans(text, source=source, target=target)
                if tmp is not None:
                    ret['ret'] = 'success'
                    ret['data'] = tmp
                else:
                    ret['ret'] = 'fail'
                    ret['data'] = ''
                
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc()) 
            ret['ret'] = 'exception'
            ret['data'] = str(exception)
        return jsonify(ret)
    ##########################################################################

    @staticmethod
    def trans_test(req):
        try:
            source = req.form['source']
            trans_type = req.form['trans_type']
            #logger.debug('trans_type:%s source:%s', trans_type, source)
            if trans_type == '0':
                return source
            elif trans_type == '1':
                return SystemLogicTrans.trans_google(source) 
            elif trans_type == '2':
                return SystemLogicTrans.trans_papago(source)
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            return False

    @staticmethod
    def trans(text, source='ja', target='ko'):
        try:
            trans_type = ModelSetting.get('trans_type')
            if trans_type == '0':
                return text
            elif trans_type == '1':
                return SystemLogicTrans.trans_google(text, source, target) 
            elif trans_type == '2':
                return SystemLogicTrans.trans_papago(text, source, target) 
        except Exception as exception: 
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            


    @staticmethod
    def trans_papago(text, source='ja', target='ko'):
        trans_papago_key = ModelSetting.get_list('trans_papago_key')
        
        for tmp in trans_papago_key:
            client_id, client_secret = tmp.split(',')
            try:
                if client_id == '' or client_id is None or client_secret == '' or client_secret is None: 
                    return text
                data = "source=%s&target=%s&text=%s" % (source, target, text)
                url = "https://openapi.naver.com/v1/papago/n2mt"
                requesturl = py_urllib2.Request(url)
                requesturl.add_header("X-Naver-Client-Id", client_id)
                requesturl.add_header("X-Naver-Client-Secret", client_secret)
                response = py_urllib2.urlopen(requesturl, data = data.encode("utf-8"))
                if sys.version_info[0] == 2:
                    data = json.load(response, encoding='utf8')
                else:
                    data = json.load(response)
                rescode = response.getcode()
                if rescode == 200:
                    return data['message']['result']['translatedText']
                else:
                    continue
            except Exception as exception:
                logger.error('Exception:%s', exception)
                logger.error(traceback.format_exc())                
        return text

    
    @staticmethod
    def trans_name(name):
        trans_papago_key = ModelSetting.get_list('trans_papago_key')
        
        for tmp in trans_papago_key:
            client_id, client_secret = tmp.split(',')
            try:
                if client_id == '' or client_id is None or client_secret == '' or client_secret is None: 
                    return
                logger.debug(name)
                encText = py_urllib.quote(str(name))
                logger.debug(encText)
                url = "https://openapi.naver.com/v1/krdict/romanization?query=" + encText
                requesturl = py_urllib2.Request(url)
                requesturl.add_header("X-Naver-Client-Id", client_id)
                requesturl.add_header("X-Naver-Client-Secret", client_secret)
                response = py_urllib2.urlopen(requesturl)
                if sys.version_info[0] == 2:
                    data = json.load(response, encoding='utf8')
                else:
                    data = json.load(response)
                rescode = response.getcode()
                logger.debug(data)
                if rescode == 200:
                    return data
                else:
                    continue
            except Exception as exception:
                logger.error('Exception:%s', exception)
                logger.error(traceback.format_exc())                
        return        




    @staticmethod
    def trans_google(text, source='ja', target='ko'):
        try:
            google_api_key = ModelSetting.get('trans_google_api_key')
            if google_api_key == '' or google_api_key is None:
                return text
            data = "key=%s&source=%s&target=%s&q=%s" % (google_api_key, source, target, text)
            url = "https://www.googleapis.com/language/translate/v2"
            requesturl = py_urllib2.Request(url)
            requesturl.add_header("X-HTTP-Method-Override", "GET")

            response = py_urllib2.urlopen(requesturl, data = data.encode("utf-8"))
            if sys.version_info[0] == 2:
                data = json.load(response, encoding='utf8')
            else:
                data = json.load(response)
            rescode = response.getcode()
            if rescode == 200:
                return data['data']['translations'][0]['translatedText']
            else:
                return text
        except Exception as exception:
            logger.error('Exception:%s', exception)
            logger.error(traceback.format_exc())
            return text
