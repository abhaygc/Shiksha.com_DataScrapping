#import requests
from bs4 import BeautifulSoup

from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import pandas as pd

import sqlite3
urls=["https://www.shiksha.com/b-tech/colleges/b-tech-colleges-mumbai-all","https://www.shiksha.com/b-tech/colleges/b-tech-colleges-mumbai-all-2?ts=36361991&pn=2"]

college_names = []
course_names = []
fee_details=[]
exam_details=[]
affiliation = []
localities=[]
facilities=[]
# FOR COLLEGE ID
college_id=[]
slc = "instituteContainer_"
len_slc=len(slc)
curse='tpl-curse-dtls more_'
# Done for college id
#Placements
placements=[]


for url in urls:


    options = Options()

    # Below line stops from opening browser
    # Comment it if you want to see the browser opening and auto click working
    options.add_argument("--headless")

    # Add path of Geckodriver.exe in executable_path below
    driver = webdriver.Firefox(firefox_options=options,executable_path="C:/Users/Gupta Niwas/Downloads/PBL SEM 4/geckodriver-v0.20.0-win64/geckodriver.exe")
    print("Firefox Headless Browser Invoked")


    driver.get(url)

    #_css_selector(".class_name tag")
    csss=driver.find_elements_by_css_selector(".outerframe a")

    while(len(csss)):
        b=0
        for i in csss:
            #rint(i.text)
            if len(i.text)>=1:
                if i.text[0]=="+":
                    b=1
                    break
        if b==0:
            break
        for i in csss:
            #print(i.text)
            try:
                i.click()
                driver.implicitly_wait(100)
            except:
                pass
        csss=driver.find_elements_by_css_selector(".outerframe a")



    sleep(5)
    # Getting the page surce containing JavaScript Data
    src=driver.page_source

    soup = BeautifulSoup(src,"lxml")
    driver.quit()


    tp = soup.find_all("div",{"class":"clg-tpl-parent"})
    
    def palcements(curl):
        place="-"
        p=requests.get(curl)
        ps=BeautifulSoup(p.content,"lxml")
        try:
            placement=ps.find_all("div",{"id":"placements"})
            placement=placement[0].find_all("span",{"class":"comp-nm"})
            j=0
            for i in placement:
                if j==0:
                    place=i.text
                    j=1
                else:
                    place=place+" , "
                    place=place+i.text
        except:
            pass
        finally:
            print(place)
            placements.append(place)
    
    
    
    def other(x):
        #fees
        word="-"
        try:
            word=x.find_all("div",{"class":"tuple-fee-col"})[0].contents[3].text.replace("\n","")
            word=' '.join(word.split())
        except:
            pass
        finally:
            fee_details.append(word)
    
        #Locality
        localities.append(x.find_all("p")[1].contents[0].replace("| ",""))

        #Exams
        exams="-"
        try:
            exams=x.find_all("div",{"class":"tuple-exam-dtls"})[0].contents[3].text.replace("\n","")
            mores=x.find_all("span",{"class":"more-exam"})
            if len(mores)>0:
                more=mores[0].contents[1].text.replace("\n","")
                exams = exams +" & "+more
        except:
            pass
        finally:
            exam_details.append(exams)
        # College Affiliation
        word="-"
        try:
            word=x.find_all("div",{"class":"tuple-alum-col"})[0].contents[3].text.replace("\n","")
            word=' '.join(word.split())
        except:
            pass
        finally:
            affiliation.append(word)
    
        # Facilities
        facilities_individual="-"
        try:
            for i in range(1,len(x.find_all("ul",{"class":"facility-icons"})[0].contents),2):
                if i==1:
                    facilities_individual=(x.find_all("ul",{"class":"facility-icons"})[0].contents[i].text).replace("\n","")
                else:
                    facilities_individual+=","
                    facilities_individual+=(x.find_all("ul",{"class":"facility-icons"})[0].contents[i].text).replace("\n","")
        except:
            pass
        finally:
            facilities.append(facilities_individual)
    
        #College ID
        college_id.append(x.find_all("div",{"class":"clg-tpl"})[0]['id'][len(slc):])
        return



    for x in tp:
    
        # College Name
    
        word=x.find_all("h2",{"class":"tuple-clg-heading"})[0].contents[0].text
        for i in range(len(word)):
            if (i!=len(word)-1 and word[i]==" "):
                if word[i+1]==" ":
                    word = word[:i]
                    break
        college_name=word
        college_names.append(college_name)
        
        #Course
        word=x.find("a",{"class":"tuple-course-name"}).contents[0]
        for i in range(len(word)):
            if(i!=len(word)-1 and word[i]==" "):
                if word[i+1]==" ":
                    word = word[:i]
                    break
        course_names.append(word)
        curl=x.find("a",{"class":"tuple-course-name"})["href"]
        placements(curl)
        
        other(x)

        try:
            ids=x.find("div",{"class":"clg-tpl"})['id'][len(slc):]
            h=x.find_all("input",{"type":"hidden"})
            no_course=int(h[len(h)-2]["value"])
            for n in range(no_course):
                if(n%4==0):
                    curse_id=curse+ids+"_0"
                if(n%4==1):
                    curse_id=curse+ids+"_1"
                if(n%4==2):
                    curse_id=curse+ids+"_2"
                if(n%4==3):
                    curse_id=curse+ids+"_3"
                aa=soup.find("section",{"class":curse_id})
                ab=aa.find("a",{"class":"tuple-course-name"})
                college_names.append(college_name)
                
                word=aa.contents[1].text
                for i in range(len(word)):
                    if(i!=len(word)-1 and word[i]==" "):
                        if word[i+1]==" ":
                            word = word[:i]
                            break
                course_names.append(word)
                curl=ab["href"]
                placements(curl)
                other(x)
        except:
            pass


data =pd.DataFrame(list(zip(college_names,localities,course_names,fee_details,exam_details,affiliation,facilities)),columns=['Name','Locality','Course', 'Fees','Exam','Affiliation','Facilities'])
conn = sqlite3.connect('Details.sqlite')
c=conn.cursor()
data.to_sql('Details', conn, if_exists='replace') #,index= False
conn.close()
