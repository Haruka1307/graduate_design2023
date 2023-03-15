import numpy as np
import pandas as pd 
import json
import copy
import jieba
import xlsxwriter as xw
import os
import subprocess

class oneweibo:
    def __init__(self,
                wb_id,
                time_stamp,
                user_id,
                user_name,
                user_type,
                is_retweet, #是否转发
                wb_content,
                device,
                edit, #编辑次数
                video,
                region_name, #wb 4.28后公开属地
                r_wb_id,
                zhuan=0,
                ping=0,
                zhan=0):
        self.wb_id=wb_id
        self.time_stamp=time_stamp
        self.user_id=user_id
        self.user_name=user_name
        self.user_type=user_type
        self.is_retweet=is_retweet
        self.wb_content=wb_content
        self.device=device 
        self.edit=edit
        self.video=video
        if is_retweet==1:
            self.video=0   
        self.region_name=region_name
        self.r_wb_id=r_wb_id 
        self.zhuan=zhuan 
        self.ping=ping 
        self.zhan=zhan 
        
    def show(self):
        print(
            "wb_id:",self.wb_id,
            "user_id:",self.user_id,
            "is_retweet:",self.is_retweet,
            "wb_content:",self.wb_content,
            "time_stamp:",self.time_stamp,
            "zhuan",self.zhuan,
            "ping:",self.ping,
            "zhan:",self.zhan
        )
    def __eq__(self,other): 
        return self.wb_content==other.wb_content

class Vertex:
    def __init__(self,
                user_id,
                user_name,
                user_type):
        self.user_id=user_id
        self.user_name=user_name 
        self.user_type=user_type
        self.weibos={} #wb_id list
        self.connectedTo={} #key:usr_id value:strength

    def tweeting(self,wb): #发微博
        self.weibos.append(wb.wb_id)

    def getWeibo(self,wb_id):  #根据微博id返回微博
        if id in self.weibos:
            return self.weibos[id]
        else:
            return None
    
    def showeibo(self):
        for key in self.weibos.keys():
            self.weibos[key].show()

    def addNeighbor(self,nbr_id):
        if nbr_id not in self.connectedTo.keys():
            self.connectedTo[nbr_id]=1
        else:
            self.connectedTo[nbr_id]=self.connectedTo[nbr_id]+1 #多次转发，关系更强

class Graph:
    def __init__(self):
        self.verList={} #user_id:节点
        self.numVertices=0
    
    def addVertex(self,
                user_id,
                user_name,
                user_type):
        self.numVertices=self.numVertices+1
        newVertex=Vertex(user_id,
                        user_name,
                        user_type)
        self.verList[user_id]=newVertex
        return newVertex

    def getVertex(self,user_id):
        if user_id in self.verList:
            return self.verList[user_id]
        else:
            return None
            
    def updateVertex(self,
                    wb_id,
                    time_stamp,
                    user_id,
                    user_name,
                    user_type,
                    is_retweet,
                    wb_content,
                    device,
                    edit,
                    video,
                    region_name,
                    r_wb_id,
                    zhuan,
                    ping,
                    zhan):
        node=Graph.getVertex(self,user_id)
        wb=oneweibo(wb_id,time_stamp,user_id,user_name,user_type,is_retweet,wb_content,device,
        edit,video,region_name,r_wb_id,zhuan,ping,zhan)
        node.tweeting(wb)
        
    def __contains__(self,id):
        return id in self.verList

    def addEdge(self,f_id,t_id): 
        #这里写错了，
        #self.verList[f_id].addNeighbor(t_id)
        self.verList[f_id].addNeighbor(t_id)
    
    def getVertices(self):
        return self.verList.keys()
    def __iter__(self):
        return iter(self.verList.values())
    
def exist(texts,keyword):
    for words in keyword:
        for text in texts:
            if check(text,words):
                return True
    return False
    
def check(text,keyword):
    for word in keyword:
        if word not in text:
            return False
    return True
def Search(keyword,file):
    wbs={}
    with open(file,'r',encoding='utf-8') as f:
        for line in f:
            #print(line[11:])
            piece=eval(line[11:])
            content=piece['weibo_content']
            rcontent=piece['r_weibo_content']
            if exist([content,rcontent],keyword):
                region_name=''
                if 'ext' in piece.keys():
                    region_name=json.loads(piece['ext'])['region_name'].split()[-1] if 'region_name' in json.loads(piece['ext']).keys() else ' '
                new_wb=oneweibo(piece['weibo_id'],piece['time_stamp'],piece['user_id'],piece['nick_name'],piece['user_type'],piece['is_retweet'],piece['weibo_content'],piece['device'],piece['edited'],piece['vedio'],region_name,piece['r_weibo_id'],piece['zhuan'],piece['ping'],piece['zhan'])
                wbs[piece['weibo_id']]=new_wb
    
    return wbs 
    #将结果写入表格


def main():
    keyword=['北京疫情发布会',['北京','发布会','疫情'],'上海疫情发布会','上海市新冠肺炎疫情防控发布会',['上海','发布会','疫情'],'广州疫情防控新闻发布会','广州市疫情防控发布会',['广州','发布会','疫情'],['重庆市政府新闻发布会','疫情'],['重庆','发布会','疫情']]
    totalwbs={}
    t=0
    for file in os.listdir():
        if file[-2:]=='7z':
            p=subprocess.Popen("7z e "+file,shell=True)
            return_code=p.wait()
            if return_code!=0:
                continue
            print("sucessfully unzip"+file)

            wbs=Search(keyword,file[:-3])
            totalwbs.update(wbs)

            p=subprocess.Popen("rm "+file[:-3],shell=True)
            return_code=p.wait()
            print("sucessfully delete"+file)
            
    
    #汇总结果写入excel
    workbook=xw.Workbook("ans.xlsx")
    worksheet1=workbook.add_worksheet("sheet1")
    worksheet1.activate()
    title=['wb_id','time_stamp','user_id','user_name','user_type','is_retweet','wb_content','device','edit','video','region_name','r_wb_id','zhuan','ping','zhan']
    worksheet1.write_row("A1",title)
    i=2
    for j in range(len(totalwbs)):
        wb=list(totalwbs.values())[j]
        insertData=[wb.wb_id,wb.time_stamp,wb.user_id,wb.user_name,wb.user_type,wb.is_retweet,wb.wb_content,wb.device,wb.edit,wb.video,wb.region_name,wb.r_wb_id,wb.zhuan,wb.ping,wb.zhan]
        row='A'+str(i)
        worksheet1.write_row(row,insertData)
        i+=1
    workbook.close()
    return  os.path.abspath("ans.xlsx")

if __name__=='__main__':
    main()
