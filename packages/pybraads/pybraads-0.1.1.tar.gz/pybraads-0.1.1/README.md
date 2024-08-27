# pybraads Readme 📜
Brainstorming package, manage ODBC connexion to database Advantage Database.

# Installation ⚡
Opérating system :  Windows, MacOS & Linux :

# Available function/class 📑
## AdsConnection(DataDirectory, Uid, Pwd)
    To create ans open data base
    DataDirectory : a full path to the data dictionary with ".add" file.
    Uid  : the data base user.
    Pwd : The data base password
### Close()
    To close data base
### commit()
    To save all modification in data base
### rollback()
    To cancel all modification in data base after the last commit
### isconnected
    To test if the data base is connected
### error
    To get the last error
## AdsQuery(adsconn)
    To create à new query.
    adsconn : is the AdsConnection of the data base tu use.
### sql
    To get or set the query before open.
    the parameters in query must be prefixed by ":" like :prefref.
### addparam(aParamName, aParamValue)
    aParamName : the name of the parameter in the query (without the :) attention case sesitive.
    aParamValue : any value for the parameter.
### execute()
    Execute the query.
### open()
    Open the query.
### error
    The get the last execution error
### fieldnames
    To get a list of all field in the select
### FieldIndex(afieldname)
    To get the field position in the query, to use with the dataset.
### eof
    To navigate in all the database unti last record
### allrecords
    To get a list with all record in database
### dataset
    To get one record to read the specific field like :
    Query.dataset[aQuery.FieldIndex('FirstName')]

# Howto use 📰
    import os
    import pybraads
    import pybrafile

    flog = pybraflog.FileLog('testlog.txt', '')
    if flog.iserror:
        print(flog.error)

    flog = pybraflog.FileLog('testlog.txt', os.getcwd())    
    flog.openlog()

    flog.writeLog('first line')
    flog.writeLog('first line indent', 10)
    flog.writeLog('two line')
    
    flog.closelog()
    
    file = pybrafile.FileUtils('testlog.txt')
    file.openfile('r')
    txt = file.readfile()
    file.close()

    print(txt)
    print(pybraflog.version())

## Meta 💬
Brainstorming – Support.erp@brainstorming.eu

Distributed under the MIT license. See ``LICENSE`` for more information.