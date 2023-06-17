import teradata
import pandas as pd

session = None

def get_session():
        global session
        if session is None:
                # print SIMBA_SERVER
                # print simba_uname
                # udaExec = teradata.UdaExec(appName="DQM",version=1)
                # session = udaExec.connect(method="odbc",system=SIMBA_SERVER,username=simba_uname,password=simba_pw)
                udaExec = teradata.UdaExec()
                session = udaExec.connect("Simba")
        return session

session = get_session()

query = """
select top 1 * from pp_oap_rom_t.unified_rule_metadata 
"""
df = pd.read_sql(query, session)
print(df)



