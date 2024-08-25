# Main Launch program within UOFast to initialize connections and start FASTApi server.
# (c) UOFast
#
#


from ast import Str
from socket import socket
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from gsocketpool import Pool
import json
import uopy
from UOFast import UOFastConfig
from UOFast.UOClasses.UOFastDataArray import *
from gsocketpool.connection import m_connection
from fastapi.openapi.utils import get_openapi

    
class UOFastConnectionPool:
    #configparams = UOFastConfig.uofastconfiguration()

    def __init__(self):
        self.configparams = UOFastConfig.uofastconfiguration()
        """
        Initialize a connection pool using the given configuration parameters.
        """
        options = dict(user=self.configparams.UOuser, pw=self.configparams.UOpassword)
        self._pool = Pool(
            m_connection,
            options,
            initial_connections=self.configparams.initial_connections,
            max_connections=self.configparams.max_connections,
            reap_interval=self.configparams.reap_interval,
        )

    def shutdown_event(self):
        """
        Shutdown event to close all connections in the pool.
        This is very important for a clean shutdown and to clear Pool sessions.
        """
        # Iterate over all connections in the pool
        for conn in self._pool: 
            # Close each connection
            conn.close()
                
    def uofast_process(self, multi_svr_object : multi_svr_object):
        print("multi_svr_object",multi_svr_object)

        try:
            print("Params",multi_svr_object.ProcessParams)
            #multi_svr_object.ProcessParams = json.loads(multi_svr_object.ProcessParams)
            UOFast = self._callsubroutine(multi_svr_object.ProcessName, 
                                          multi_svr_object.ProcessParams.getString())
        except Exception as e:
            raise e
            #FastMVApi = None

        return {'UOFast': UOFast}

    def uofast_process(self, multi_svr_object : multi_svr_object):
        print("multi_svr_object",multi_svr_object)

        try:
            print("Params",multi_svr_object.ProcessParams)
            #multi_svr_object.ProcessParams = json.loads(multi_svr_object.ProcessParams)
            UOFast = self._callsubroutine(multi_svr_object.ProcessName, 
                                          multi_svr_object.ProcessParams.getString())
        except Exception as e:
            raise e #HTTPException(status_code=418, detail=str(e.detail))
            #FastMVApi = None

        return {'UOFast': UOFast}

    def uofast_file_process(self, FileName :str):
        print("multi_svr_object",FileName)

        try:
            print("Params",FileName)
            #multi_svr_object.ProcessParams = json.loads(multi_svr_object.ProcessParams)
            UOFast = self.__uogetfile(FileName)
        except Exception as e:
            raise e #HTTPException(status_code=418, detail=str(e.detail))
            #FastMVApi = None

        return UOFast

    def uofast_file_process(self, FileName :file_dict_obj):
        file_name=FileName.file_name
        file_dict=FileName.dict_fields
        print("UODFile ",file_name)
        print("dict = " + str(file_dict))

        try:
            print("Params",str(FileName))
            #multi_svr_object.ProcessParams = json.loads(multi_svr_object.ProcessParams)
            UOFast = self.__uogetfilewithdict(FileName)
        except Exception as e:
            raise e #HTTPException(status_code=418, detail=str(e.detail))
            #FastMVApi = None

        return UOFast

    def uofast_file_process(self, FileName :str):
        print("multi_svr_object",FileName)

        try:
            print("Params",FileName)
            #multi_svr_object.ProcessParams = json.loads(multi_svr_object.ProcessParams)
            UOFast = self.__uogetfile(FileName)
        except Exception as e:
            raise HTTPException(status_code=418, detail=str(e.detail))
            #FastMVApi = None

        return UOFast


    def _callsubroutine(self, Processname, Processparams):
        retVars=""
        mstring = ""
        print("Call subroutine",Processname,Processparams)
        try:
            with self._pool.connection() as conn:
                subcount=0
                errVars=""
                sub = uopy.Subroutine(Processname, 3, session=conn.socket)
                conn.logger_info("params" + Processparams)
                sub.args[0] = Processparams
                sub.args[1] = retVars
                sub.args[2] = errVars
                conn.logger_info("BEGIN Calling Subroutine ..." + Processname)
                conn.logger_info("Params=" + str(Processparams))
                sub.call()
                retVars = str(sub.args[1]) #OUTVALS
                errVars = sub.args[2]  #ERRVALS
                print("errors returned ", str(errVars))            
                if str(errVars) != "":
                    if str(errVars[0]) != "":
                        errVars = str(errVars).replace(dataconstants.VM, "")
                        raise HTTPException(status_code=418, detail=str(errVars))
                        #raise Exception(str(errVars[0]))
                conn.logger_info("END Calling Subroutine ..." + Processname)
                #Now parse the return object            
                mstring = mrecord()
                mstring = mstring.populateArray(retVars)

        except Exception as e:
            retVars = ""
            print("Error calling sub ", str(e))
            raise e #HTTPException(status_code=418, detail=str(e.detail))   
        
        return mstring

    def __uogetfile(self, FileName : str):
        print("Call _uogetfile",str(FileName))
        filerecords = []
        try:
            with self._pool.connection() as conn:
                subcount=0
                errVars=""
                conn.logger_info("BEGIN Reading file ..." + FileName)

                ### Call get file routine
                ###
                uofile = uopy.File(FileName,None,session=conn.socket)
                id_list = uopy.List(0,session=conn.socket).select(uofile).read_list()
                
                #filerecords = uofile.read_records(id_list)[3]
                for x in id_list:
                    rec = str(uofile.read(x))
                    mstring = mdatarecord()
                    mstring.populateArray(rec)
                    print("Reading record if from file " + FileName, str(x))
                    mstring.key_id = str(x)
                    filerecords.append(mstring)
                #print("errors returned ", str(errVars))            
            
                conn.logger_info("END Reading file ..." + FileName)
            
        except Exception as e:
            retVars = ""
            print("Error calling FileRead " + FileName, str(e))
            raise e #HTTPException(status_code=418, detail=str(e.detail))   
        
        
        return filerecords

    def __uogetfilewithdict(self, FileName : file_dict_obj):
        print("Call _uogetfile",str(FileName.file_name))
        
        file_name=FileName.file_name
        file_dict=FileName.dict_fields

        filerecords = []
        try:
            with self._pool.connection() as conn:
                subcount=0
                errVars=""
                conn.logger_info("BEGIN Reading file ..." + file_name)
                conn.logger_info("Processing dict " + str(file_dict))

                ### Call get file routine
                ###
                uofile = uopy.File(file_name,None,session=conn.socket)
                id_list = uopy.List(0,session=conn.socket).select(uofile).read_list()
                
                #filerecords = uofile.read_records(id_list)[3]
                for x in id_list:
                    rec = uofile.read_named_fields(x,file_dict)
                    rec_list = rec[3][0]
                    my_dict = dict(zip(file_dict, rec_list))
                    my_dict['_recID'] = str(x)
                    my_dict['_COLLECTION'] = file_name
                    print("Reading record if from file " + file_name, str(x))
                    
                    filerecords.append(my_dict)
                
                conn.logger_info("END Reading file ..." + file_name)
            
        except Exception as e:
            retVars = ""
            print("Error calling FileRead " + FileName, str(e))
            raise e #HTTPException(status_code=418, detail=str(e.detail))   
        
        
        return filerecords
