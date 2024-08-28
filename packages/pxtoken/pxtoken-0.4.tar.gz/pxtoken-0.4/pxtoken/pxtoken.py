import json
import os,time,hashlib
import requests
import urllib.parse

class PxToken:
    def __init__(self,host,client_id,secret) -> None:
        self.host=host
        self.client_id=client_id
        self.secret=secret

    def _verify_base_parms(self):
        if  len(self.host)==0 or len(self.client_id)==0 or len(self.secret)==0 :
            raise Exception("参数设置错误")

        return True

    def do_login(self,username,password,device=""):
        self._verify_base_parms()
        headers={
             'client-id':self.client_id
        }

        data={
            "username":username,
            "password":password,
            "device":device
        }
        url="%s/oauth2/doLogin" % self.host
        try:
            rest = self._post_form(url,data=data,headers=headers)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))

        return None

    def build_login_authorize(self,redirect_uri,response_type="code"):

        self._verify_base_parms()
        if len(redirect_uri)==0:
            raise Exception("redirect_uri 不能为空")

        params = {
            'client_id' : self.client_id,
            'redirect_uri' :redirect_uri,
            'response_type':response_type
        }
        queryString = urllib.parse.urlencode(params)
        signature=self._sha256("%s%s"%(queryString,self.secret))
        queryString="%s&signature=%s" %(queryString,signature)
        return "%s/oauth2/login_authorize?%s" %(self.host ,queryString)
    
    def get_login_access_token(self,code):
        self._verify_base_parms()
        params = {
            'client_id' :self.client_id,
            'code' :code
        } 
        queryString = urllib.parse.urlencode(params)
        signature=self._sha256("%s%s"%(queryString,self.secret))
        queryString="%s&signature=%s" %(queryString,signature)
        url="%s/oauth2/login_access_token?%s" %(self.host,queryString)

        try:
            rest = self._get(url)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))

        return None

    def get_login_user(self,access_token):
        self._verify_base_parms()
        headers = {
            'access-token':access_token,
            'client-id':self.client_id
        }

        url="%s/oauth2/user_info" % self.host
        try:
            rest = self._get(url,headers=headers)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))

        return None


    def build_data_authorize(self,target_client_id,redirect_uri,response_type="code"):

        self._verify_base_parms()
        if len(redirect_uri)==0:
            raise Exception("redirect_uri 不能为空")

        if len(target_client_id)==0:
            raise Exception("target_client_id 不能为空")
        
        params = {
            'client_id' : self.client_id,
            'target_client_id' : target_client_id,
            'redirect_uri' :redirect_uri,
            'response_type':response_type
        }
        queryString = urllib.parse.urlencode(params)
        signature=self._sha256("%s%s"%(queryString,self.secret))
        queryString="%s&signature=%s" %(queryString,signature)
        return "%s/oauth2/data_authorize?%s" %(self.host ,queryString)
    
    def get_data_access_token(self,code):
        self._verify_base_parms()
        params = {
            'client_id' :self.client_id,
            'code' :code
        } 
        queryString = urllib.parse.urlencode(params)
        signature=self._sha256("%s%s"%(queryString,self.secret))
        queryString="%s&signature=%s" %(queryString,signature)
        url="%s/oauth2/data_access_token?%s" %(self.host,queryString)
        try:
            rest = self._get(url)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))
        return None

    def data_authorize_verify(self,access_token):
        self._verify_base_parms()
        headers = {
            'access-token':access_token,
            'client-id':self.client_id
        }

        url="%s/oauth2/data_authorize_verify" % self.host
        try:
            rest = self._get(url,headers=headers)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))

        return None

    def get_app_access_token(self,target_client_id):
        self._verify_base_parms()
        params = {
            'client_id' : self.client_id,
            'target_client_id': target_client_id
        } 

        queryString = urllib.parse.urlencode(params)
        signature=self._sha256("%s%s"%(queryString,self.secret))
        params["signature"]=signature
        url="%s/oauth2/app_access_token" % self.host
        try:
            rest = self._post_form(url,data=params)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))

        return None

    def app_authorize_verify(self,access_token):
        self._verify_base_parms()
        headers = {
            'access-token':access_token,
            'client-id':self.client_id
        }

        url="%s/oauth2/app_authorize_verify" % self.host
        try:
            rest = self._get(url,headers=headers)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))

        return None


    def user_register(self,username,password,nickname,sex:int=1,phone="",email="",head=""):
        self._verify_base_parms()
        params = {
            'client_id' : self.client_id,
            'username': username,
            'password': password
        } 

        queryString = urllib.parse.urlencode(params)
        signature=self._sha256("%s%s"%(queryString,self.secret))
        params["signature"]=signature

        params["nickname"]=nickname
        params["sex"]=sex
        params["phone"]=phone
        params["email"]=email
        params["head"]=head

        url="%s/oauth2/do_register" % self.host
        try:
            rest = self._post_form(url,data=params)
            return json.loads(rest)
        except Exception as ex:
            print(str(ex))

        return None

    def _sha256(self,data):
        sha256 = hashlib.sha256()
        sha256.update(data.encode('utf-8'))
        return sha256.hexdigest()

    def _get(self,url,headers:dict=None):
        try:
            payload = {}
            if headers is None:
                headers={}
            response = requests.request("GET", url, headers=headers, data=payload)
            return response.text
        except Exception as ex:
            return False
    
    def _post_form(self,url,data:dict=None,headers:dict=None,files:list=None):
        try:
            if data is None:
                data={}
            if headers is None:
                headers={}
            if files is None:
                files=[]
            response = requests.request("POST", url, headers=headers, data=data, files=files)
            return response.text
        except Exception as ex:
            return False
        
    def _post_json(self,url,data:dict=None,headers:dict=None):
        try:
            if data is None:
                data={}
            if headers is None:
                headers={}
            if 'Content-Type' not in headers:
                headers['Content-Type']= 'application/json'
            payload = json.dumps(data)
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.text
        except Exception as ex:
            return False