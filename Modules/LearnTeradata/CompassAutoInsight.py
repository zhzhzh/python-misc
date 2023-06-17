#!/usr/local/bin/python

import sys
import os
# from sendmailmodplus import *
import teradata
import pandas as pd
# from cred import *
import matplotlib.pyplot as plt  

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

def get_check_date(check_date_offset=1):        
        session = get_session()
        query_check_date = """SELECT CURRENT_DATE - {0} AS check_date""".format(check_date_offset)
        check_date_result = pd.read_sql(sql=query_check_date, con=session)
        #print check_date_result['check_date'][0]
        return check_date_result['check_date'][0]

def get_check_date_offset(check_date):        
        session = get_session()
        query_check_date_offset = """SELECT CURRENT_DATE - DATE '{0}' AS check_date_offset """.format(check_date)
        check_date_offset_result = pd.read_sql(sql=query_check_date_offset, con=session)
        #print check_date_offset_result['check_date_offset'][0]
        return check_date_offset_result['check_date_offset'][0]

def get_flag(metric_name,date_offset=1):        
        session = get_session()
        query_flag = """SELECT mavg_7d_change, mavg_7d_change_II, accu_trend
                          FROM pp_oap_xinglv1_t.compass_case_monitoring
                         WHERE "type" = '{0}'
                               AND datetime = CURRENT_DATE - {1}""".format(metric_name,date_offset)
        flag_result = pd.read_sql(sql=query_flag, con=session)
        #print flag_result
        return flag_result    

def get_data(metric_name,date_offset=1):        
        session = get_session()
        query_data = """SELECT *
                          FROM pp_oap_xinglv1_t.compass_case_monitoring
                         WHERE "type" = '{0}'
                               AND datetime BETWEEN -90 - {1} AND CURRENT_DATE - {1}
                         ORDER BY datetime""".format(metric_name,date_offset)
        data_result = pd.read_sql(sql=query_data, con=session)
        #print data_result
        return data_result             

def get_driver(trend_type,trend_direction,date_offset=1):        
        session = get_session()
        if trend_type == "mavg_7d":
                if trend_direction == 1: 
                        query_driver = """SELECT "name", "type", mavg_7d_change_rate, accu_trend, positive_negative_backlog
                                                ,positive_negative_backlog*accu_trend AS accutrend_driver_share
                                                ,positive_negative_backlog*mavg_7d_change_rate AS mavg7d_driver_share
                                            FROM pp_oap_xinglv1_t.compass_case_monitoring
                                           WHERE mavg7d_driver_share > 0
                                                 AND datetime = CURRENT_DATE - {0}
                                         QUALIFY ROW_NUMBER() OVER (PARTITION BY datetime ORDER BY mavg7d_driver_share desc) <= 3""".format(date_offset)
                elif trend_direction == -1:                        
                        query_driver = """SELECT "name", "type", mavg_7d_change_rate, accu_trend, positive_negative_backlog
                                                ,positive_negative_backlog*accu_trend AS accutrend_driver_share
                                                ,positive_negative_backlog*mavg_7d_change_rate AS mavg7d_driver_share
                                            FROM pp_oap_xinglv1_t.compass_case_monitoring
                                           WHERE mavg7d_driver_share < 0
                                                 AND datetime = CURRENT_DATE - {0}
                                         QUALIFY ROW_NUMBER() OVER (PARTITION BY datetime ORDER BY mavg7d_driver_share) <= 3""".format(date_offset)
        elif trend_type == "accu_trend":
                if trend_direction == 1: 
                        query_driver = """SELECT "name", "type", mavg_7d_change_rate, accu_trend, positive_negative_backlog
                                                ,positive_negative_backlog*accu_trend AS accutrend_driver_share
                                                ,positive_negative_backlog*mavg_7d_change_rate AS mavg7d_driver_share
                                            FROM pp_oap_xinglv1_t.compass_case_monitoring
                                           WHERE accutrend_driver_share > 0
                                                 AND datetime = CURRENT_DATE - {0}
                                         QUALIFY ROW_NUMBER() OVER (PARTITION BY datetime ORDER BY accutrend_driver_share desc) <= 3""".format(date_offset)
                elif trend_direction == -1:                        
                        query_driver = """SELECT "name", "type", mavg_7d_change_rate, accu_trend, positive_negative_backlog
                                                ,positive_negative_backlog*accu_trend AS accutrend_driver_share
                                                ,positive_negative_backlog*mavg_7d_change_rate AS mavg7d_driver_share
                                            FROM pp_oap_xinglv1_t.compass_case_monitoring
                                           WHERE accutrend_driver_share < 0
                                                 AND datetime = CURRENT_DATE - {0}
                                         QUALIFY ROW_NUMBER() OVER (PARTITION BY datetime ORDER BY accutrend_driver_share) <= 3""".format(date_offset)            

        driver_result = pd.read_sql(sql=query_driver, con=session)
        print(driver_result)
        return driver_result 


def draw_mavg_chart(metric_name,chart_data):
        plt.figure(figsize=(8,3.5))  
        plt.plot(chart_data.datetime,chart_data.value,label=metric_name,color='steelblue',linewidth=2) 
        plt.plot(chart_data.datetime,chart_data.mavg_7d,label="7 days Moving Average",color='dimgrey',linewidth=1)         
        plt.plot(chart_data.datetime,chart_data.mavg_7d*1.1,label="1.1 * Moving Average",color='dimgray',linestyle='--',linewidth=1)
        plt.plot(chart_data.datetime,chart_data.mavg_7d*0.9,label="0.9 * Moving Average",color='dimgray',linestyle='--',linewidth=1)
        plt.grid(True, linestyle='--', color='darkgrey', linewidth = '0.5')         

        plt.xlabel('Date',fontsize=9)
        plt.ylabel(metric_name,fontsize=9)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6) 

        for a,b,c in zip(chart_data.datetime[-35:],chart_data.value[-35:],chart_data.mdiff_2d_change[-35:]):
                c_color = 'grey'
                if c > 0:
                        c_color = 'green'
                elif c < 0:
                        c_color = 'red'

                plt.text(a, b+0.3, '%d'%c, ha='center', va='bottom', fontsize=6, color=c_color)

        plt.legend(loc='best', fontsize=8)
        plt.xticks(rotation=30) 

        plt.title(metric_name+" of last 90 days")  
        plt.savefig(metric_name.replace(' ','')+".png", dpi=1000)     

def draw_chart(metric_name,chart_data):
        plt.figure(figsize=(8,3.5))  
        plt.plot(chart_data.datetime,chart_data.value,label=metric_name,color='#008000',linewidth=2) 
        plt.plot(chart_data.datetime,chart_data.mavg_7d,label="7 days Moving Average",color='dimgrey',linewidth=1)         
        plt.grid(True, linestyle='--', color='darkgrey', linewidth = '0.5')         

        plt.xlabel('Date',fontsize=9)
        plt.ylabel(metric_name,fontsize=9)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6) 

        plt.legend(loc='best', fontsize=8)
        plt.xticks(rotation=30) 

        plt.title(metric_name+" of last 90 days")  
        plt.savefig(metric_name.replace(' ','')+".png", dpi=500)    

if __name__ == '__main__':

        # For Testing on specific day
        check_date = '2017-08-02'
        check_date_offset = get_check_date_offset(check_date)
        print(check_date_offset)

        '''
        # Normally, monitor -1 day
        check_date_offset = 1
        check_date = get_check_date(check_date_offset)
        '''

        subject = "Compass Case Backlog Volume is Normal! "+ check_date
        receivers = ["jzhang14@paypal.com"]
        sender = "DL-PP-DNA_SHA_DataQuality@paypal.com"

        ##### Backlog #####
        BacklogVol_flag = get_flag('PROJ:Compass Monitoring|CAT:BacklogVol',check_date_offset)    # Backlog monitor result flag
        BacklogVol_data = get_data('PROJ:Compass Monitoring|CAT:BacklogVol',check_date_offset)    # Backlog data
        draw_mavg_chart("Backlog Volume",BacklogVol_data)    # Draw Backlog Chart 
        logfile_path = "BacklogVolume.png"


        ##### Get Backlog Drivers #####
        if BacklogVol_flag['mavg_7d_change'][0] != 0: # (> 1.1*benchmark OR < 0.9*benchmark)

                if BacklogVol_flag['mavg_7d_change'][0] == 1:  # Increase
                        subject = "Alert! Compass Case Backlog Volume increased! "+ check_date
                        html_text = '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">Compass Case Backlog Volume Increasd more than 10% of last 7 days average!</p>'"<br>"
                        driver = get_driver("mavg_7d",1,check_date_offset)


                elif BacklogVol_flag['mavg_7d_change'][0] == -1:   # Decrease
                        subject = "Alert! Compass Case Backlog Volume decreased! "+ check_date
                        html_text = '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">Compass Case Backlog Volume Decreased more than 10% of last 7 days average!</p>'"<br>"
                        driver = get_driver("mavg_7d",-1,check_date_offset)

                receivers = ["xinglv1@paypal.com"]  # Need to expand to real receivers after tesing!

        elif abs(BacklogVol_flag['accu_trend'][0]) == 5 and BacklogVol_flag['mavg_7d_change_II'][0] != 0:  # (continued 5 days up/down trend) AND (> 1.1*benchmark OR < 0.9*benchmark)

                if BacklogVol_flag['accu_trend'][0] == 5:  # Increase
                        subject = "Alert! Compass Case Backlog Volume increased! "+ check_date
                        html_text = '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">Compass Case Backlog Volume kept Increasing for more than 5 days!</p>'"<br>"
                        driver = get_driver("accu_trend",1,check_date_offset)


                elif BacklogVol_flag['accu_trend'][0] == -5:   # Decrease
                        subject = "Alert! Compass Case Backlog Volume decreased! "+ check_date
                        html_text = '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">Compass Case Backlog Volume kept Decreasing for more than 5 days!</p>'"<br>"
                        driver = get_driver("accu_trend",-1,check_date_offset)

                receivers = ["xinglv1@paypal.com"]  # Need to expand to real receivers after tesing!

        html_text += '<img src=BacklogVolume.png width="2400" height="900" />'
        html_text += '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">The top drivers are: </p>'"<br>"
        
        ##### Draw driver charts #####
        for index, row in driver.iterrows():
                print(row['type'])
                print(row['name'])
                driver_data = get_data(row['type'],check_date_offset)
                draw_chart(row['name'],driver_data)
                logfile_path += ","+row['name'].replace(' ','')+".png"
                html_text += '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">Top '+ str(index+1) +': '+ row['name'] +'</p>'"<br>"
                if row['accu_trend'] > 0:
                        html_text += '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">kept Increasing for '+ str(row['accu_trend']) +' days </p>'"<br>"
                elif row['accu_trend'] < 0:                        
                        html_text += '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">kept Dncreasing for '+ str(abs(row['accu_trend'])) +'days </p>'"<br>"
                html_text += '<p style = "font-family:Arial;font-size:14px;font-weight:bold;color:red">Change Rate is '+ str(row['mavg_7d_change_rate']) +'</p>'"<br>"                    
                html_text += '<img src='+row['name'].replace(' ','')+'.png width="2400" height="900" />'

        ##### Send the email #####
        # send_attach_mail(subject, sender, receivers, [html_text], logfile_path)
        print(html_text)

        print("--end--")

