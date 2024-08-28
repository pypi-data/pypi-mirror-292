#!/usr/bin/env python3
# -fire CLI
from fire import Fire

from tdb_io.version import __version__

import pandas as pd

from influxdb import InfluxDBClient
#from pymongo import MongoClient
#import pymongo # to get ASCENDING
import datetime as dt
import time
import os
import json
import sys

import socket
import sys

# DEBUG=1  # will change in MAIN  args
ACTUAL_CREDENTIALS={}


# SSL warning
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


from console import fg,bg,fx
import colorsys
# if DEBUG:print("D...  project/module:  tdb_io/influx :", __version__ )


#OK
#===============================================================
def is_int(n):
    # print(f"/{n}/")
    try:
        float_n = float(n)
        #print(f"/{float_n}/")
        int_n = int(float_n)
        #print(f"/{int_n}/")
    except ValueError:
        return False
    else:
        return float_n == int_n


def cmd_ls(ip, db, series , qlimit = 3, output = None):
    """
Description of the function.

Args:
    param1 (type): Description of param1.
    param2 (type): Description of param2.

    uses check_series AND check_databases
    """
    #print(f"D...             input parameters :   IP=/{ip}/   DB=/{db}/")
    #print("D... listing influx databases")
    #dbcheck = "_"
    #sercheck = ""
    #qlimit = 5
    IP = ip #  "127.0.0.1"
    delete = False
    dbpr = False
    # if len(args)>1:
    #     dbcheck = args[1]
    #     print("D... args  = ",args)
    #     print("D... kwargs=",kwargs)
    # if len(args)>2:
    #     sercheck = args[2]  # which series
    # if len(args)>3:
    #     qlimit = args[3]   # how many
    dbcheck = db
    sercheck = series
    qlimit = qlimit

            # #if len(args)>4:  # i dont want this fixed position
            # #    IP = args[4]

            # if len(kwargs)>0:
            #     if 'delete' in kwargs.keys():
            #         delete = kwargs["delete"]
            #     if 'ip' in kwargs.keys():
            #         IP = kwargs["ip"]
            #         print(f"D... IP == {IP}")

    res = check_databases(IP=IP)
    #print(f"D... in total... {len(res)} databases found " )

    for i in res:
        if i['name'].find("_")==0: continue  # DROP  _databases

        chk = " "
        if (dbcheck is None)or(dbcheck == i["name"]):
            if (dbcheck == i["name"]):chk = "*"
            dbpr = True
            #print()
            print("#>  ", chk, i["name"] )
            if dbpr: # sercheck is determined
                res = check_series(dbcheck, IP=IP) #check 1 database

                if sercheck in res: # There was series requested...
                    # *************    this is a case when I know what I want **************
                    print(f" ... /{sercheck}/ is present among measurements")
                    check_series(dbcheck, sercheck, qlimit, IP, output = output) #check 1 series
                    #if delete:
                    #    influx.check_series(dbcheck, sercheck, delete=True)
                elif sercheck ==  "all":
                    print(f" ...  series==/{sercheck}/  GO THROUGH ALL measurements:")
                    for i in res:
                        #print(i," ----------------------------------------->")
                        check_series(dbcheck, i, qlimit, IP) #check 1 series
    # returning list of databases *******
    return res


def check_port(IP="127.0.0.1"):
    """
Checks if influx runs on IP
    """
    ok = False
    client = InfluxDBClient(host=IP, port=8086)
    try:
        client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (@checkport) NO influx DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            #print("i... database exists, authorization needed")
            ok = True
    return ok



def check_databases(IP="127.0.0.1", user="", password=""):
    """
Checks if influx runs on IP AND shows databases
r=client.query('SELECT "temp" FROM "autogen"."idx232"')

    """
    #if DEBUG:print("D... checkd: ",IP,user)
    ok = False
    autho = False
    dbs = []
    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (chkdb) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            #print("i... database exists, authorization needed")
            ok = False
            autho = True
    if autho and user=="":
        #print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials( DEBUG = 0)

        # NO SSL
        gotit = False
        try:
            #if DEBUG:print("D... chkd:  getting client NO SSL")
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
            client.get_list_database() # this checks error
            gotit = True
        except:
            print("X... exception without SSL, trying with SSL")

        if not gotit:
            try:
                #if DEBUG:print("D... chkd: getting client WITH SSL")
                client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, timeout=3)
                client.get_list_database() # this checks error
            except:
                print("X... ",IP, 8086,creds[0],creds[1],creds[2] )

        dbs = client.get_list_database()
    return dbs



def age_to_color(age):
    hue = None
    brk = 0.8
    if age <= 0:
        hue = brk  # Map age to hue (0.0 to 1.0)
    elif age >= 365:
        hue = 0
    else:
        hue = (365-age) / (365/brk)  # Map age to hue (0.0 to 1.0)
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    hex_color = f'{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
    #print(hue,  "  ",r,g,b , "    ", hex_color)
    return getattr(fg, f't_{hex_color}')







def check_series(database="", series="",
                 qlimit=5,
                 IP="127.0.0.1",
                 user="", password="",
                 output = None,
                 delete=False):
    """
Checks if influx runs on IP, fir each DATABASE it shows ALL SERIES
r=client.query('SELECT "temp" FROM "autogen"."idx232"')

  for a known database it returns the series

 TOO BIG:
 - does all :  output ; delete

    """
    #if DEBUG:print("D... checks: ",IP,user)

    now = dt.datetime.now()
    now = pd.Timestamp.now(tz='UTC')
    if type(qlimit) is int:
        limit_int = True
    else:
        limit_int = False

    ok = False
    autho = False
    dbs = []
    liseries = []
    #
    # check without userpass
    #
    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (chkser) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            #print("i... database exists, authorization needed")
            ok = False
            autho = True
    #
    # userpass needed:  get them
    #
    if autho and user=="":
        #print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials( DEBUG=0)

        # NO SSL
        gotit = False
        limit_int = True
        mytimeout =3 # below 10000 events

        # ------------ make time possible  1h 1d 1w
        #  > SELECT "water_level" FROM "h2o_feet" WHERE time > now() - 1h
        if type(qlimit) is str:
            limit_int = False
            if not qlimit[-1] in ["s","m","h","d","w"]:
                print("X...   limit is string but it is not 1s 1m 1h 1d 1w:", qlimit)
                print("X.... exit")
                sys.exit(1)
            intnum = "".join(qlimit[:-1])
            if  not is_int(intnum):
                print("X...   limit is string but it is not  integer s m h d w:", qlimit, intnum)
                print("X.... exit")
                sys.exit(1)
            mytimeout = 30 # worst case scenario
        #-------------
        if limit_int:
            if qlimit > 10000:
                mytimeout = 10
            if qlimit > 60000:
                mytimeout = 20
            if qlimit > 120000:
                mytimeout = 30


        try:
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=mytimeout)
            dbs = client.get_list_database() # generates exception
            gotit = True
        except:
            print("X... chks: exception without SSL")

        if not gotit:
            #if DEBUG:print("D... chks: trying with SSL")
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, timeout=mytimeout)
            dbs = client.get_list_database() # generates excep

        #if DEBUG:print("D... client obtained - nossl")
        dbs = client.get_list_database()
    #print("D... list of databases obtained", dbs)


    # TERMINAL
    TERMW = 55
    try:
        TERMW, rows = os.get_terminal_size(0)
    except:
        rows = 20
        #TERMW-=1


    #-------------------------------- if series not given, list them
    if series == "":
        #print("D... @stage: check series /empty/....")
        for i in dbs:  #
            #print("D...", type(i), i, i["name"] )
            if i["name"].find("_")==0: # DATABASENAME
                continue
            if (database!="")and(database!=i["name"]):
                continue
            print(f"{fx.bold}DB:~~~~~~~~~~~~~~~~~~~~~~~~~~~{i['name']}~~~~~~~~~~~~~~~~~~~~~~~~~~~{fx.default}")# *(TERMW-len(i['name'])-2) )
            sers = client.get_list_series( i['name'] )
            if len(sers) == 0:
                print("i...  no series in this database...")
            #print(sers)

            maxlen=1
            for j in sers:
                #print(j,len(j))
                if len(j)>maxlen:
                    maxlen=len(j)
            maxlen+=2
            one = int(TERMW/maxlen)

            #print("D... "*50, maxlen, one )
            k = 0
            # ------------- print the measurements in a kind of a table....
            for j in sers:
                k+= 1
                liseries.append(j)
                print( "{ss:{maxlens}}".format(ss=j, maxlens=maxlen), end="" )
                if k % one == 0:
                    print( "     s " )
            if len(sers) > 0: print() # after the table, EOL
        #print("_r_")
        return liseries

    #  =========================================== END AND RETURN =======
    # IF SERIES/MEASUREMENTS were not given


    ######################################## series given...we go to "read" option
    ######################################## series given...we go to "read" option
    ######################################## series given...we go to "read" option
    ######################################## series given...we go to "read" option
    #print("D... stage read....")
    dbs = [i['name'] for i in dbs]
    if not database in dbs:
        print("X ... no such database - exit", database,"in", dbs)
        sys.exit(1)# quit()

    #i = database
    #print(i,"_"*(TERMW-len(i)-2) )
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    sers = client.get_list_series( database )
    if not series in sers:
        print("X ... no such series found - exit", series)
        sys.exit(1)# quit()

    client.switch_database(database)



    # ******************************************
    #               QUERY HERE
    # ******************************************


    aaa = f"{database}/{series}"
    alen = len(aaa)
    #aaa = aaa.ljust(29) #+"_"*(29-alen)
    aaa = aaa+"_"*(29-alen)
    print(f"{fg.white}{fx.bold}________________________________{aaa}_______________ {fg.default}{fx.default} ", end="")
    if limit_int:
        #print("i... quering DESC with limit: ", qlimit)
        r = client.query('SELECT * FROM "autogen"."'+series+'" ORDER BY time DESC LIMIT '+str(qlimit)  )
    else:
        print("i... quering DESC with time: ", qlimit)
        CMD = 'SELECT * FROM "autogen"."'+series+'" WHERE TIME > now() - '+str(qlimit) +" ORDER BY time DESC "
        #print("D... ", CMD )
        r = client.query(CMD)

    # r = client.query('SELECT * FROM "autogen"."'+series+'" ORDER BY time DESC LIMIT '+str(qlimit)  )

    # ******************************************
    #   points extracted from the RESPONSE
    # ******************************************

    #print(r.raw)
    if len( r.raw['series'] ) >0:
        cols = r.raw['series'][0]['columns']
        points = r.get_points()
        # print(cols)  # Print columns not needed
    else:
        print("X... no points in the demanded range;  returning")
        return

    # **********************************************
    #     dict constructed here
    # ***********************************************

    ppoints=0
    dfdict = {}
    divme = 1000
    #h5 = h5py.File("savetest.h5")
    for p in points:
        #print(p, type(p))
        dfdict[ppoints] = p
        ppoints+=1
        #if (ppoints % divme)==0:
        #    print("{:9.0f} * {}  ".format(ppoints/ divme, divme ), end="\r" )

    #print("\nCOLUMNS:",cols)
    #print("TOTAL: {} points printed, the DEMANDED number was {}".format( ppoints, qlimit )," - latest first" )


    # ************************************************************
    #       df constructed here
    # *************************************************************

    df = pd.DataFrame.from_dict(dfdict, "index")
    #print(df.head() )
    #print(df.tail() )
    # ********************************************************************** DF ***************************
    #rx = df.iloc[ -1]['time']
    rx = pd.to_datetime( df.iloc[ -1]['time'] ).tz_convert('UTC')
    rx = now-rx
    age = rx.total_seconds()/24/3600
    #print(round(age),"days")
    #print(rx, type(rx), age )
    #print( age )

    print(age_to_color(age), df ,fg.default)
    #*****************************************************************************DF***********************

    # ******************************************
    #   POSSIBLE   FILE  OUTPUT   HERE
    # ******************************************

    if output is not  None:
        #hdf = HDFStore("influx_{}_{}.h5".format(series,ppoints) )
        now = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

        MYHOSTNAME = socket.gethostname()
        fname = "influx_F{}_H{}_D{}_M{}_{}_{}".format(MYHOSTNAME,IP,database,series,now,ppoints)

        fnameh5 = "{}.h5".format(fname)
        fnamecsv = "{}.csv".format(fname)
        fnameparq = "{}.parquet".format(fname)

        # # tables NEEDE HERE
        # if 'tables' in globals():
        #     print("i... saving h5", fnameh5)
        #     df.to_hdf( fnameh5, series ,format ="table", mode = 'a' ) # this was ment as incremental .... sorry
        # else:
        #     pass
        #     #print("i... NOT saving h5", fnameh5, "format=table nedds tables: doesnt work in windows")
        if output == "csv":
            print("i... saving csv", fnamecsv)
            df.to_csv( fnamecsv )
        else:
            print("X....  UNDEFINED OUTPUT FORMAT :  ",output)

        # if "pyarrow" in globals():
        #     print("i... saving parquet", fnameparq)
        #     df.to_parquet( fnameparq )
        # else:
        #     pass
        #     #print("i... NOT saving parquet", fnameparq, "some problem with pyarow")


    # ******************************************
    #   OH    and DELETE HERE ...
    # ******************************************

    if delete:
        DELETE = 'DELETE  FROM "'+series+'" '
        print( DELETE )
        res = input("REALLY DELETE? y/n  >")
        if res == "y":
            r = client.query( DELETE)
            print(" ... deleted ... ")
        else:
            print(" ... no action taken ....")

    print()

    # ******************************************
    #   well,   I RETURN   DF  --- one can plot with it ...
    # ******************************************

    return df






def _read_series(database="test", series='idx0', IP="127.0.0.1", user="", password="", delete = False):
    """
READS ONE SERIES - MOST COMPELETE FUNCTION HERE
r=client.query('SELECT "temp" FROM "autogen"."idx232"')

    """
    ok = False
    autho = False
    dbs = []
    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (rdser) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            print("i... database exists, authorization needed")
            ok = False
            autho = True
    if autho and user=="":
        #print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials( DEBUG=0)
        # NO SSL
        client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
        #if DEBUG:print("D... client obtained - empty")
        dbs = client.get_list_database()
    dbs = [i['name'] for i in dbs]
    #if DEBUG:print("D... list of databases obtained", dbs)


    TERMW = 55
    try:
        TERMW, rows = os.get_terminal_size(0)
    except:
        rows = 20

    if not database in dbs:
        print("X ... no such database - exit", database,"in", dbs)
        sys.exit(1)#quit()
    i = database
    print(i,"_"*(TERMW-len(i)-2) )

    sers = client.get_list_series( i )
    if not series in sers:
        print("X ... no such series found - exit", series)
        sys.exit(1)# quit()

    client.switch_database(i)
    #
    # i must find columns:
    #

    #r = client.query('SELECT "temp" FROM "autogen"."'+series+'" ')
    r = client.query('SELECT * FROM "autogen"."'+series+'" ')
    #print(r.raw)
    cols = r.raw['series'][0]['columns']
    points = r.get_points()
    print(cols)
    for p in points:
        print(p)
    print("\nCOLUMNS:",cols)

    if delete:
        DELETE = 'DELETE  FROM "'+series+'" '
        print( DELETE )
        res = input("REALLY DELETE? y/n")
        if res == "y":
            r = client.query( DELETE)

    return
    return




def checkout_hostname_database(database="test", series='idx0', IP="127.0.0.1", user="", password="", delete = False):
    """
    Check Hostname in the LOCAL influx DATABASES --- IF DIFFER: DROP;
    """

    MYHOSTNAME = socket.gethostname()
    NEWDB = "i_am_" + MYHOSTNAME
    #if DEBUG:print("D... gethostname:", MYHOSTNAME, NEWDB )

    IP = "127.0.0.1"
    ok = False
    autho = False
    dbs = []

    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (chhodb) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            print("i... database exists, authorization needed")
            ok = False
            autho = True
    if autho and user=="":
        #print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials(DEBUG=0)

        # NO SSL
        gotit = False
        try:
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
            dbs = client.get_list_database()
            gotit = True
            #if DEBUG:print("D... client obtained with NO SSL")
        except:
            print("X... NO SSL - didnt work, I try SSL")

        if not gotit:
            try:
                #if DEBUG:print("D... client trying with  SSL")
                client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, timeout=3)
                dbs = client.get_list_database()
                #if DEBUG:print("D... client obtained with WITH SSL")
            except:
                print("X... WITH SSL - didnt work", IP, 8086,creds[0],creds[1],creds[2])


        dbs = client.get_list_database()
    dbs = [i['name'] for i in dbs]

    #if DEBUG:print("D... list of databases obtained", dbs)

    host_present = False
    ohost_present = False
    ohost_name = "x"
    for i in dbs:
        if i == NEWDB:
            host_present = True
        elif i.find("i_am_")==0:
            ohost_present = True
            ohost_name = i
    if ohost_present:
        print("!... other host present:",ohost_name," - DROP it:", ohost_present)
        client.drop_database(ohost_name)
        #return
    if host_present:
        #if DEBUG:print("D... all ok, my hostname is there with i_am_...")
        return
    print("!... CREATE DATABASE myself:", NEWDB)
    client.create_database(NEWDB)


#def drop_measurement():





def read_infl_credentials(config="~/.influx_userpassdb", DEBUG=True):
    """ READ and RETURN Influxdb  Credentials
    """
    ips=[]
    ips1=[]
    ips2=[]
    filemis = False
    try:
        with open( os.path.expanduser("~/.influx_servers") ) as f:
            ips1=f.readlines()
            ips1 = [x.strip() for x in ips1]
    except:
        filemis = True
        if DEBUG:
            print("X... NO FILE ~/.influx_servers with automatic IPs")

    # try:
    #     with open( os.path.expanduser("~/.seread_discover8086") ) as f:
    #         ips1=f.readlines()
    # except:
    #     filemis = True
    #     if DEBUG:
    #         print("X... NO FILE ~/.seread_discover8086 with automatic IPs")

    # try:
    #     with open( os.path.expanduser("~/.seread_permanent8086") ) as f:
    #         ips2=f.readlines()
    #     filemis = False
    # except:
    #     filemix = True
    #     if DEBUG:
    #         print("X... NO FILE ~/.seread_permanent8086 with permanent IPs")

    # if filemis and DEBUG:
    #     print("x... no ~/.influx_servers  list found")
    #xx seread_permanent8086 NEITHER seread_discover8086 with servers!")

    ips=ips1+ips2 # more files possible

    if len(ips) > 0:
        if DEBUG: print("D... at least on server found:  ", nservers)
        pass
    else:
        if check_port():
            ips = ["127.0.0.1"] # Brutally introduce localhost

    ips=[ i.strip() for i in ips]
    #================ credentials HERE============
    try:
        with open(os.path.expanduser( config ) ) as f:
            creds=f.readlines()
        creds=[ i.strip() for i in creds ]
    except:
        print("X... no credentials in",config )
        sys.exit(1)
        #return (["","","test"],ips)
    if DEBUG:print("D... exiting credentials-read with",creds,ips)
    return (creds,ips)






#=================================================

def influxwrite( DATABASE="test", MEASUREMENT="test",
                 values="" ,
                 IP=None,
                 initialconfig="2DOlater" , DEBUG = False):
    """write data to influx. DATABASE=test,MEASUREMENT=hostname; ./influx.py influxwrite -values b=1
    comma separated values
    """
    if DEBUG:print("D... ************************ writin to influx ******************************")
    creds,remo_ips=read_infl_credentials( DEBUG=DEBUG)


    # ------------------------------------------------ overwrite all
    if DATABASE is None:
        pass #creds[2]
    else:
        creds[2] = DATABASE # overwrite database !!!!

    if IP is not None:
        # overwrite IP
        ips = IP
        if type(ips) == str: ips = [ips]

    if IP is None:
        ips = remo_ips
        if DEBUG: print( "i... REMOTE IP'S TAKEN: ", ips )

    for iIP in ips:
        if DEBUG:print("D... IP=",iIP)
        if len(iIP)<7:
            print("X... IP too short......... skip")
            continue
        if iIP[0].isdigit(): #
            if DEBUG: print("D... IP is number......... no ssl used")
            client = InfluxDBClient(iIP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=2)
        else:
            if DEBUG:print("D... IP is text. ...........I do ssl ")
            client = InfluxDBClient(iIP, 8086,creds[0],creds[1],creds[2],ssl=True, verify_ssl=False,timeout=8)

        #
        # This is for hostname identification across remote IPs
        #
        MYHOSTNAME=socket.gethostname()
        if DEBUG:print("D....................MYHOST=",MYHOSTNAME )
        if DEBUG:print("D....................INFLUX WRITING= DB/MEASUREMENT",DATABASE,MEASUREMENT )

        if len(values)==0:
            if DEBUG:print("D....  no values given ... do you need to look at current values? -exit")
            print("X....  no values given ... do you need to look at current values? -exit")
            #mongo2h5( DATABASE, COLLECTION, nlimit=100000, write_h5=False)
            #quit()
            sys.exit(1)

        insertvals=values.split(",") # comma separated values
        if DEBUG:print("D... insert pairs:", insertvals)
        INSERTDICT={}
        TIMEHERE = None
        for i in insertvals:
            if DEBUG:print("D... insert pair:",i)
            key=i.split("=")[0]
            if key!="time":
                val=float(i.split("=")[1])
                INSERTDICT[key]=val
            else:
                TIMEHERE = i.split("=")[1]
        if DEBUG:print("D... INSERT DICT:", INSERTDICT )

        ###json_body = [ {"measurement":MYHOSTNAME+"_test4"} ]
        if iIP == "127.0.0.1":
            json_body = [ {"measurement":MEASUREMENT} ]
        else:
            json_body = [ {"measurement":MYHOSTNAME+"_"+MEASUREMENT} ]

        if TIMEHERE is not None:
            json_body[0]["time"]= TIMEHERE

        #json_body[0]["fields"]={}
        json_body[0]["fields"]=INSERTDICT
        if DEBUG: print("D... JSON==",json_body)
        res = client.write_points(json_body)
        #print("i... result == ", res)
        client.close()
        #if DEBUG: print("_____-")
        #print("writepoints response=",res)
        if DEBUG:print("D... ************************ influx DONE ******************************")
        return res # client write response






#=================================================


#=============================================================
#=============================================================
#=============================================================
if __name__=="__main__":


    print("F... you can run ")
    print('  ./influx.py influxwrite test testmes "a=1" --DEBUG  ')
    print()
    Fire( {
      'influxwrite':influxwrite ,
      'check_port':check_port ,
      'check_dbs':check_databases ,
      'check_series':check_series ,
#      'read_series':read_series ,
#      'help': help
  } )
