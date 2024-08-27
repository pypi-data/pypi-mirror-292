from enum import Enum
import requests
#from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import base64
import orjson


class THttpType(Enum):
    """THttpType Liste of Authentication type for Http
    """
    BasicUsrPws = 0 #Basic user/password
    Token = 1 #Token
    ApiKey = 2 #API Keypy install get enum
    OAuth2 = 3 #OAuth2

class THttpMethode(Enum):
    """THttpMethode Liste of methode available for request Http
    """
    GET = 0 #Get
    POST = 1 #Post
    PUT = 2 #Put

class Http :
    """ To commincate with web and webmethode
    """
    def __init__(self, aAuthType : THttpType):
        """__init__ 
            Cretae and manage QHttp request
            
        Parameters
        ----------
        DataConnection : pyodbc.Cursor
            The ADS database connection cursor
        """
        self._AuthType     = THttpType.BasicUsrPws
        self._AuthType     = aAuthType
        self._userName     = ''
        self._passWord     = ''
        self._Url          = ''
        self._headers      = {}
        self._methode      = '' 
        self._headers      = ''
        self._body         = ''
        self._tokenRefresh = '' #Url for thoken request/refresh
        self._tokenType    = 'Bearer'
        self._tokenAccess  = ''
        self._tokendelais  = 3600 #ms
        
        match self._AuthType:
            case THttpType.Token:
                #Token
                self._userName = 'Bearer'

            case THttpType.ApiKey:
               #ApiKey
                self._userName = 'ApiKey'

    def request(self, aHttpMethode : THttpMethode, aUrl : str, aBody : dict = {})->dict:
        self._Url = aUrl
        value = ''
        statusCode = 200
        reason = ''
        
        token = {
            'access_token': 'eswfld123kjhn1v5423',
            'refresh_token': 'asdfkljh23490sdf',
            'token_type': {self._tokenType},
            'expires_in': {self._tokendelais},     # initially 3600, need to be updated by you
            }
          
        extra = {
            'client_id': {self._userName},
            'client_secret': r''.join(self._passWord),
            }
        
        self.__testAuthMode()
        
        if self._AuthType == THttpType.OAuth2:
            #OAuth2
            #implémentation not finished
            oauth = OAuth2Session(self._userName, token=token, auto_refresh_url=self._tokenRefresh,
                                  auto_refresh_kwargs=extra, token_updater=self._token_saver)                  
            response = oauth.get(self._Url)
        else:
            match self._AuthType:
                case THttpType.Token:                      
                    #Token
                    self._userName = 'Bearer'
                    self._headers['Authorization'] = f"{self._userName} {self._passWord}"

                case THttpType.ApiKey:
                    #APIKEY
                    self._userName = 'ApiKey'
                    self._headers['Authorization'] = f"{self._userName} {self._passWord}"
              
                case _:
                    #BasicUsrPws:
                    credentials = f"{self._userName}:{self._passWord}"
                    #encode credentials in base 64
                    encoded_cred = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                    #creating Authorisation header value
                    self._headers['Authorization'] = f"Basic {encoded_cred}"
                                            
            if (len(aBody) == 0):
                match aHttpMethode:
                    case  THttpMethode.GET:
                        response = requests.get(self._Url, headers=self._headers)
                    case THttpMethode.POST:
                        response = requests.post(self._Url, headers=self._headers)
                    case THttpMethode.PUT:
                        response = requests.put(self._Url, headers=self._headers)
            else:
                match aHttpMethode:
                    case  THttpMethode.GET:
                        response = requests.get(self._Url, headers=self._headers, json=aBody)
                    case THttpMethode.POST:
                        response = requests.post(self._Url, headers=self._headers, json=aBody)
                    case THttpMethode.PUT:
                        response = requests.put(self._Url, headers=self._headers, json=aBody)

        statusCode = response.status_code
        reason = response.reason
        
        if len(response.content) != 0:
            if 'application/json' in response.headers.get('content-type'):
                value = orjson.loads(response.content)
            else:
                value = response.content
          
        while (type(value) == list):
            value = value[0]
        
        retValue ={
            'statusCode' : statusCode,
            'reason' : reason,
            'content' : value,
            'headers' : response.headers
            }    
              
        return retValue
     
    #private functions
    def _token_saver(self, token):
        self._tokenAccess = token

    def __testAuthMode(self)->bool:
        """__testAuthMode Contole if informations needed 
        by authentication mode are available

        Returns
        -------
        bool
            True if all corract
        """
        authModeallowed = False

        match self._AuthType:
            case THttpType.Token:
                #Token
                if (self._passWord == ''):
                    raise ValueError('Token mode, the Acces user, password must be filled.')

            case THttpType.ApiKey:
                #ApiKey
                if (self._passWord == ''):
                    raise ValueError('API ket mode, the password must be filled.')
                        
            case THttpType.OAuth2:
                #OAuth2
                if ((self._userName == '') or (self._passWord == '') or 
                    (self._tokenRefresh == '')):
                    raise ValueError('OAuth2 mode, the user, password and Token refresh must be filled.')

            case _:
                #BasicUsrPws:
                if ((self._userName == '') or (self._passWord == '')):
                    raise ValueError('Basic mode, the user and password must be filled.')
        
        authModeallowed

        return authModeallowed

    #property function
    def __getUserName(self)->str:
        return self._userName

    def __setUserName(self, aUsrName : str):
        if self._AuthType == THttpType.Token:
                #Token
                raise ValueError('Http Token mode, impossible to set username.')
        elif self._AuthType == THttpType.ApiKey:
                #ApiKey
                raise ValueError('Http API key mode, impossible to set username.')
        else:
            self._userName = aUsrName

    def __getpassWord(self)->str:
        return self._passWord
    
    def __setpassWord(self, aPassWord : str):
        self._passWord = aPassWord

    def __get_AuthType(self)->THttpType:
        return self._AuthType

    def __get_Headers(self)->dict:
        return self._headers
    
    def __set_Headers(self, aHeaders : dict):
        self._headers = aHeaders

    def __getUrl(self)->str:
        return self._Url
    
    def __setUrl(self, aUrl : str):
        self._Url = aUrl

    # Set property() to use get_name, set_name and del_name methods
    userName = property(__getUserName, __setUserName)
    passWord = property(__getpassWord, __setpassWord)
    authType = property(__get_AuthType)
    headers = property(__get_Headers, __set_Headers)
    url = property(__getUrl,__setUrl)