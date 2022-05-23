from sqlite3 import Date, Timestamp
from itsdangerous import base64_encode
import requests
import time
import base64
import urllib.parse
import re
import pandas as pd
from bs4 import BeautifulSoup 

def fPost(url,session_id,auth_id,NET_SessionId):
    Timestamp=int(time.time())
    qurl=url+'action/score.aspx?session_id='+session_id+'&auth_id='+auth_id+'&timestamp='+str(Timestamp)
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                        'Host' : '172.20.2.51',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Cookie': 'AspxAutoDetectCookieSupport=1; ASP.NET_SessionId='+NET_SessionId+''
                    }
    res=requests.get(url=qurl,headers=headers)#提交题目，预期返回值为ok
    #print(res.text)
    qurl=url+'view.aspx?session_id='+session_id+'&auth_id='+auth_id
    res=requests.get(url=qurl,headers=headers)#查看结果
    #print(res.text)
    return res.text

def getScore(res):
    pattern=re.compile('总分</td><td>(.*?)</td>')
    score=re.search(pattern,res)
    fenshu=re.sub('总分</td><td>','',score.group(0))
    fenshu=re.sub('</td>','',fenshu)
    print('本次得分为'+fenshu+'\n')
    fenshu=int(float(fenshu))#提取分数
    return fenshu

def getiinput(res):#获取测试的iinput
    # pattern=re.compile('<pre>(.*?)</pre>')
    # score=re.findall(pattern,res)
    # #print(score)
    # score2={}
    # i=0
    # for key in score:
    #     score2[i]=urllib.parse.quote(key)
    #     i=i+1
    # #print(score2)
    # return score2#这是一个列表

    soup = BeautifulSoup(res, "html.parser")
    s = str(soup.find_all(class_ = "s1 diff")) #class必须加下划线tmd
    s1 = s.split('<pre>')
    s2 = s1[1]
    s3 = s2.split('\n')
    i=0
    score2={}
    for key in s3:
        if(key=='</td>'):
            break
        s3[i]=re.sub('\\r','',s3[i])
        score2[i] = s3[i].rstrip('</pre>') #从右侧去除字符串中的'</pre>'
        score2[i] =re.sub('%','%%',score2[i])
        i=i+1
    print(score2)
    return score2

def getOutput(res):
    #df = pd.read_html(res,)[4]
    #print(df)
    ans={}
    pattern=re.compile('</th>(.*?)</td>')
    score=re.findall(pattern,res)
    #print(score)
    i=2
    for key in score:
        if(i%2==0):
            pattern=re.compile('<b.*>(.*?)</b>')
            score1=re.findall(pattern,key)
            d=int(i/2)
            ans[d]=score1[0]
        i=i+1
    #print(ans)
    for key in ans:
        ans[key]=urllib.parse.quote(ans[key])
    
    return ans


def makeCode(ans,iinput,ptime,code):
    i=0
    if(ptime==1):
        i=0
        code='%23include%3Cstdio.h%3E%0Aint%20main%28%29%0A%7B%0A%20%20%20%20char%20a%5B50%5D%5B80%5D%2Cb%5B50%5D%5B20%5D%5B80%5D%3B'
        #print(iinput)
        if(iinput[0]=='无输入'):
            for key in ans:
                code+='%0A%20%20%20%20printf%28%22'+ans[key]+'%5Cn%22%29%3B'
            return code;
        else:
            for key in iinput:
                code+='%0A%20%20%20%20gets%28a%5B'+str(i)+'%5D%29%3B'
                i=i+1
    i=0
    for key in iinput:
            code+='%0A%20%20%20%20strcpy%28b%5B'+str(ptime-1)+'%5D%5B'+str(i)+'%5D%2C%22'+iinput[key]+'%22%29%3B'
            i=i+1
    code+='%0A%20%20%20%20if%28'
    print('iinputs:'+str(i))
    for key in range(i):
        code+='strcmp%28a%5B'+str(key)+'%5D%2C%20b%5B'+str(ptime-1)+'%5D%5B'+str(key)+'%5D%29%3D%3D0'
        if (key<(i-1)):
            code+='%26%26'
    code+='%29%7B'
    for key in ans:
        code+='%0A%20%20%20%20printf%28%22'+ans[key]+'%5Cn%22%29%3B'
    code+='%0A%7D'
    #print(code)
    return code
        
def getQid(url,session_id,auth_id,NET_SessionId,vis):
    qurl=url+'q.aspx?session_id='+session_id+'&auth_id='+auth_id
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                        'Host' : '172.20.2.51',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Cookie': 'AspxAutoDetectCookieSupport=1; ASP.NET_SessionId='+NET_SessionId+''
                    }
    res=requests.get(url=qurl,headers=headers)#提交题目，预期返回值为ok
    pattern=re.compile("global_qid_data.*=\['(.*?)' \];")
    qid=re.findall(pattern,res.text)
    # print(res.text)
    print('qid:'+qid[0])
    return qid[0]

def getvis(url,session_id,auth_id,NET_SessionId):
    qurl=url+'q.aspx?session_id='+session_id+'&auth_id='+auth_id
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                        'Host' : '172.20.2.51',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Cookie': 'AspxAutoDetectCookieSupport=1; ASP.NET_SessionId='+NET_SessionId+''
                    }
    res=requests.get(url=qurl,headers=headers)
    pattern=re.compile("global_qid_data(.*?)=\[")
    qid=re.findall(pattern,res.text)
    # print(res.text)
    print('vis:'+qid[0])
    return qid[0]

def postCode(url,session_id,ptime,qid,code,NET_SessionId,vis):
    Timestamp=int(time.time())
    qUrl=url+'action/post-answer.aspx?session_id='+session_id+'&timestamp='+str(Timestamp)
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                        'Host' : '172.20.2.51',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Cookie': 'AspxAutoDetectCookieSupport=1; ASP.NET_SessionId='+NET_SessionId
                    }
    data='<?xml version="1.0" encoding="UTF-8"?><data sessionID="'+str(session_id)+'"><t'+vis+'><d><q>'+str(qid)+'</q><v>'+str(code)+'%0A%7D</v></d></t'+vis+'></data>'
    #print(data)
    data=re.sub('%26gt%3B','>',data)
    #data=re.sub('%26lt%3B','&lt',data)
    data=base64_encode(data)
    #print(data)
    data=data.decode()
    data=data.replace('-','+')
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '='* missing_padding
    data=data.replace('====','')
    data=urllib.parse.quote(data)
    data='xml='+data
    #print(data)
    res=requests.post(url=qUrl,data=data,headers=headers)
    print(res.text)

url='http://172.20.2.51/train/'
session_id='be63738447884b3380bc6a1f1aaa12bb'#题目id
auth_id='55ee6d72e84242929ce355b1edc602ef'#账号信息
NET_SessionId='03kil3mhch2cvfazks2jv0ba'
print('请在脚本文件中更改auth_id（在url中）和NET_SessionId（在cookie中）')
while 1:
    session_id=input('输入题目的session_id:\n')
    ptime=1
    code='%23include%3Cstdio.h%3E%0Aint%20main()%0A%7B%0A%20%20%20%20printf(%22test%20msg%22)%3B'
    vis=getvis(url,session_id,auth_id,NET_SessionId)
    qid=getQid(url,session_id,auth_id,NET_SessionId,vis)
    # vis=''(若题目崩溃，请手动输入vis和qid的值，具体值在前面有输出)
    # qid=''
    postCode(url,session_id,ptime,qid,code,NET_SessionId,vis)
    res=fPost(url,session_id,auth_id,NET_SessionId)
    #print(res)
    print('第'+str(ptime)+'次尝试')
    score=getScore(res)
    while score < 10:   
        iinput=getiinput(res)
        ans=getOutput(res)
        code=makeCode(ans,iinput,ptime,code)
        postCode(url,session_id,ptime,qid,code,NET_SessionId,vis)
        res=fPost(url,session_id,auth_id,NET_SessionId)
        ptime=ptime+1
        print('第'+str(ptime)+'次尝试')
        score=getScore(res)
        if (score==0):
            print('请重试或更换题目')
            break
        # print(score)
        # print(iinput)
        # print(ans)
