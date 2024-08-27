#!/usr/bin/python3
import json
import requests
import hashlib
import os
import exiftool
import datetime
import time
from PIL import Image
import imagehash
import shutil


class Checked_File:

    def __init__(self,file_loc):
        self.file_loc = file_loc
        self.b_name = os.path.basename(self.file_loc)
        self.dir_name = os.path.dirname(self.file_loc)
    
    def get_md5(self):
        the_md5=hashlib.md5()
        hash = ''
        with open(self.file_loc,'rb') as f:
            the_md5.update(f.read())
            hash = the_md5.hexdigest()
        return hash

    def get_metadata(self):
        """
        EXIF:Model
        Checked_File:MIMEType
        EXIF:Make
        """
        metadata = ""
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(self.file_loc)
        return metadata

    def get_maker(self):
        exif = self.get_metadata()
        if exif.get("EXIF:Make") is None:
                return "NON"
        else:
            return exif.get("EXIF:Make").strip().replace(" ","")+"-"+exif.get("EXIF:Model").strip().replace(" ","")


    def get_type(self):
        exif = self.get_metadata()
        if exif.get("Checked_File:Checked_FileType") is None:
            if os.path.splitext(self.b_name)[1][1:].upper() != "":
                return os.path.splitext(self.b_name)[1][1:].upper()
            else:
                return "NON"
        else:
            return exif.get("Checked_File:Checked_FileType")
        return "NON"


    def get_create_date(self):
        exif = self.get_metadata()
        if exif.get("EXIF:CreateDate"):
            a = exif.get("EXIF:CreateDate")[0:10]
            b = a.replace(":","-")
            return b
        elif exif.get("QuickTime:CreateDate"):
            a = exif.get("QuickTime:CreateDate")[0:10]
            b = a.replace(":","-")
            return b
        else:
            pass
        create_time =datetime.datetime.strptime(time.ctime(os.path.getctime(self.file_loc)), "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d")
        return create_time

    def get_geo_address(self):
        dict={}
        exif = self.get_metadata()
        if exif.get("Composite:GPSLatitude") is not None:
            geo='{:.4f}'.format(exif.get("Composite:GPSLongitude"))+","+'{:.4f}'.format(exif.get("Composite:GPSLatitude"))
            gaode=json.load(open(os.path.join(os.path.dirname(os.getcwd()),"config","gaode.json")))
            base=gaode.get("base")
            key = gaode.get("key")
            parameters={"location":geo,"key":key}
            try:
                response = requests.get(base, parameters)
                if response.status_code == 200:
                    address = response.json()
                    dict["city"]=address.get("regeocode").get("addressComponent").get("city")
                    dict["province"]=address.get("regeocode").get("addressComponent").get("province")
                    dict["district"]=address.get("regeocode").get("addressComponent").get("district")
                    dict["country"]=address.get("regeocode").get("addressComponent").get("country")
                    dict["address"]=address.get("regeocode").get("formatted_address")
                else:
                    pass
            except:
                pass
            return dict
    def is_same(self,cmp_file):
        """
        返回same如果相同
        返回similar如果相似
        返回空如果不同
        """
        media2= Checked_File(cmp_file)
        hash2=media2.get_md5()
        hash1=self.get_md5()
        status = ""
        if hash1==hash2:
            status = "same"
        else:
            hash11 =  imagehash.average_hash(Image.open(self.file_loc))
            hash12 =  imagehash.average_hash(Image.open(cmp_file))
            if (hash11 == hash12):
                status = "similar"
        return status

    def move_to(self,dest):
        hash1=self.get_md5()
        log=""
        if os.path.exists(os.path.join(dest,self.b_name)):
            media2 = Checked_File(os.path.join(dest,self.b_name))
            hash2=media2.get_md5()
            if hash1 == hash2:
                log=['delete',self.b_name,self.file_loc,os.path.join(dest,self.b_name),os.path.getsize(self.file_loc),hash1]
                os.remove(self.file_loc)
            else:
                new_file_name  = os.path.join(dest,os.path.splitext(self.b_name)[0] + "_1" + os.path.splitext(self.b_name)[1])
                while os.path.exists(new_file_name):
                    new_file_name  = os.path.join(dest,os.path.splitext(os.path.basename(new_file_name))[0] + "_1" + os.path.splitext(new_file_name)[1])
                shutil.move(self.file_loc,os.path.join(new_file_name))
                print("shutil move,"+ "from,"+ self.file_loc + ",to,"+ new_file_name )
                log=['rename',self.b_name,self.file_loc,new_file_name,os.path.getsize(new_file_name),hash1]
        else:
            shutil.move(self.file_loc,os.path.join(dest,self.b_name))
            print("shutil move,"+ "from,"+ self.file_loc + ",to,"+ os.path.join(dest,self.b_name))
            log=['move',self.b_name,self.file_loc,os.path.join(dest,self.b_name),os.path.getsize(os.path.join(dest,self.b_name)),hash1]
        return log

import os
import os.path
import csv
import stat
import time
import sqlite3
import imagehash
#引入folder里面的通用函数，例如file_move,get_db,update_db


class Check_Folder:
    """
    ### log 字段说明，从0到5
    ### ['duplicate',i,os.path.join(folder,i),'',os.path.getsize(os.path.join(folder,i)),hash]
    ### (action varchar(20),name varchar(200),source varchar(1000),dest varchar(1000),size varchar(50),md5 varchar(50))
    1. one_folder，把当前目录中所有子目录文件移动到根目录下，并删除空的文件夹
    2. check,检查当前目录中的所有文件，并删除重复文件（根据MD5值来判断）
    3. compare,比较当前folder和目标folder，如果文件存在于目标folder，则删除

    
    """
    global HASH_COLUMN
    HASH_COLUMN = 5
    global DEFAULT_LOC
    DEFAULT_LOC = os.path.join(os.environ['HOME'],".log")

    def __init__(self,folder_loc):
        self.folder_loc=folder_loc
        self.dir_name = os.path.dirname(folder_loc)

    def one_folder(self):
        folder = self.folder_loc
        one_log = self.init_log(os.path.basename(folder)+'_one.log')
        for i in os.listdir(folder):
            if os.path.isdir(os.path.join(folder,i)):
                if i[0] not in ['@','.']:
                    self.process_one(os.path.join(folder,i),folder,one_log)
        return one_log
    def process_one(self,folder,base_folder,log):
        for i in os.listdir(folder):
            if os.path.isdir(os.path.join(folder,i)):
                if i[0] not in ['@','.']:
                    self.process_one(os.path.join(folder,i),base_folder,log)
                else:
                    shutil.rmtree(os.path.join(folder,i),ignore_errors = True)
            else:
                check_file = Checked_File(os.path.join(folder,i))
                mov_log = check_file.move_to(self.folder_loc)
                with open(log,'a',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(mov_log)
        if self.folder_loc != folder:
            os.rmdir(folder)

    def check(self):
        folder = self.folder_loc
        check_log = self.init_log(os.path.basename(folder)+'_check.log')
        global checking
        checking = []
        self.process_checking(folder,check_log)
        #conn = self.init_db(DEFAULT_DB)
        #init_db_table(conn,os.path.basename(folder))
        #print(folder,check_log,conn)
        #update_db_record(os.path.basename(folder),check_log,conn)
        return check_log

    def process_checking(self,folder,log):
        global checking
        for i in os.listdir(folder):            
            if os.path.isdir(os.path.join(folder,i)):
                if i[0] not in ['@','.']:
                    print(str(os.path.join(folder,i)) + " is not dummy folder")
                    Check_Folder.process_checking(self,os.path.join(folder,i),log)
            else:
                media = Checked_File(os.path.join(folder,i))
                hash = media.get_md5()
                if hash is not None:
                    if hash in checking:
                        with open(log,'a',newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['duplicate',i,os.path.join(folder,i),'',os.path.getsize(os.path.join(folder,i)),hash])
                        os.remove(os.path.join(folder,i)) 
                    else:
                        with open(log,'a',newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['new',i,os.path.join(folder,i),'',os.path.getsize(os.path.join(folder,i)),hash])
                        checking.append(hash)
        return log

    def compare(self,std_folder):
        """
        用来对比文件夹cmp_folder和文件夹cmp_folder
        如果cmp_foler中的文件在ctd_folder中，则删除
        """
        #global compare
        #compare = []
        cmp_folder=self.folder_loc
        cmp_log = self.init_log(os.path.basename(cmp_folder)+'_comp.log')
        check_log = os.path.join(DEFAULT_LOC,os.path.basename(std_folder)+'_check.log')
        if os.path.exists(check_log):
            std_log = check_log 
        else:
            check_folder=Check_Folder(std_folder)
            std_log = check_folder.check()
        self.process_comparing(self.folder_loc,std_log,cmp_log)
        return cmp_log

    def process_comparing(self,folder,std_log,cmp_log):
        global HASH_COLUMN
        for i in os.listdir(folder):
            if os.path.isdir(os.path.join(folder,i)):
                if i[0] not in ['@','.']:
                    print(str(os.path.join(folder,i)) + " is not dummy folder")
                    self.process_comparing(os.path.join(folder,i),std_log,cmp_log)
            else:
                media = Checked_File(os.path.join(folder,i))
                hash = media.get_md5()
                if hash is not None:
                    a = self.find_csv(std_log,hash,HASH_COLUMN)
                    if a is not None:
                        with open(cmp_log,'a',newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['duplicate',i,os.path.join(folder,i),a[2],os.path.getsize(os.path.join(folder,i)),hash])
                        os.remove(os.path.join(folder,i))
                    else:
                        with open(cmp_log,'a',newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['new',i,os.path.join(folder,i),'',os.path.getsize(os.path.join(folder,i)),hash])                   
                            #compare.append(hash)  

    def class_bysize(self,dstfold,large=1):
        folder = self.folder_loc
        class_by_size_log = self.init_log(os.path.basename(folder)+'_class_by_size.log')
        if not os.path.exists(os.path.join(dstfold,"large")):
            os.makedirs(os.path.join(dstfold,"large"))
        if not os.path.exists(os.path.join(dstfold,"small")):
            os.makedirs(os.path.join(dstfold,"small"))
        if os.path.exists(class_by_size_log):
            os.remove(class_by_size_log)
        f = open(class_by_size_log,'w')
        f.close()  
        self.process_bysize(folder,dstfold,class_by_size_log,large)
        return class_by_size_log

    def process_bysize(self,folder,dstfold,log,large):

        for i in os.listdir(folder):
            if i[0] not in ['@','.']:
                if os.path.isdir(os.path.join(folder,i)):
                    self.process_bysize(os.path.join(folder,i),dstfold,log,large)
                else:
                    size = os.path.getsize(os.path.join(folder,i))
                    a = Checked_File(os.path.join(folder,i))
                    if size < large*1024*1024:
                        xx=a.move_to(os.path.join(dstfold,"small"))
                        with open(log,'a',newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(xx)
                            f.close()    
                    else:
                        xx=a.move_to(os.path.join(dstfold,"large"))
                        with open(log,'a',newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(xx)
                            f.close()     

    def class_bytype(self,dstfold):
        folder = self.folder_loc
        class_by_type_log = self.init_log(os.path.basename(folder)+'_class_by_type.log')
        self.process_bytype(folder,dstfold,class_by_type_log)
        return class_by_type_log

    def process_bytype(self,folder,dstfold,log):
        for i in os.listdir(folder):
            if i[0] not in ['@','.']:
                if os.path.isdir(os.path.join(folder,i)):
                    self.process_bytype(os.path.join(folder,i),dstfold,log)
                else:
                    media = Checked_File(os.path.join(folder,i))
                    type = media.get_type()
                    if not (os.path.exists(os.path.join(dstfold,type))):
                        os.makedirs(os.path.join(dstfold,type))
                    a=Checked_File(os.path.join(folder,i))
                    result=a.move_to(os.path.join(dstfold,type))
                    with open(log,'a',newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(result)
        

    def class_bytime(self,desfold):
        folder= self.folder_loc
        log = self.init_log(os.path.basename(folder)+'_class_bytime.log')
        self.process_bytime(folder,desfold,log)
        return log

    def process_bytime(self,folder,desfold,log):
        for i in os.listdir(folder):
            if i[0] not in ['@','.']:
                if os.path.isdir(os.path.join(folder,i)):
                    process_bytime(os.path.join(folder,i),desfold,log)
                else:
                    media = Checked_File(os.path.join(folder,i))
                    a = media.get_create_date()          
                    if not os.path.exists(os.path.join(desfold,a)):
                        os.makedirs(os.path.join(desfold,a))
                    cc = Checked_File(os.path.join(folder,i))
                    temp_log = cc.move_to(os.path.join(desfold,a))
                    with open(log,'a',newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(temp_log)

    def class_bymaker(self,desfold):
        folder = self.folder_loc
        log = self.init_log(os.path.basename(folder)+'_class_bymaker.log')
        self.process_bymaker(folder,desfold,log)
        return log

    def process_bymaker(self,folder,desfold,log):
        for i in os.listdir(folder):
            if i[0] not in ['@','.']:
                if os.path.isdir(os.path.join(folder,i)):
                    process_bymaker(os.path.join(folder,i),desfold,log)
                else:            
                    media = Checked_File(os.path.join(folder,i))
                    maker = media.get_maker()
                    if not os.path.exists(os.path.join(desfold,maker)):
                        os.makedirs(os.path.join(desfold,maker))
                    cc = Checked_File(os.path.join(folder,i))   
                    temp_log = cc.move_to(os.path.join(desfold,maker))   
                    with open(log,'a',newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(temp_log)       



    def init_log(self,logname):
        global DEFAULT_LOC
        if not os.path.exists(DEFAULT_LOC):
            os.mkdir(DEFAULT_LOC)
        if os.path.exists(os.path.join(DEFAULT_LOC,logname)):
            os.remove(os.path.join(DEFAULT_LOC,logname))
        f = open(os.path.join(DEFAULT_LOC,logname),'w')
        f.close() 
        return os.path.join(DEFAULT_LOC,logname)

    def find_csv(self,csv_file,key_words,column):
        with open(csv_file,'r') as f:
            reader = csv.reader(f,delimiter=",")
            for row in reader:
                if row[column] == key_words:
                    return row
        







        
