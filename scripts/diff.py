import os
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# ================
BASE_USER = "/home/own/"
LAST_RESULT_FILE = BASE_USER + "zCore/scripts/test-result-last.txt"
CURR_RESULT_FILE = BASE_USER + "zCore/scripts/test-result.txt"
DIFF_FILE = BASE_USER + "zCore/scripts/diff.txt"
TEMP_DIFF = "" #BASE_USER + ""
# ================

last_set = set()
curr_set = set()

def compare_diff():
    with open(LAST_RESULT_FILE, 'r') as last, open(CURR_RESULT_FILE, 'r') as curr:
                    # last_lines = last.readlines()
                    # curr_lines = curr.readlines()
                    
                    for line in last.readlines() :
                        last_set.add(line)
                    for line in curr.readlines() :
                        curr_set.add(line)

                    with open(DIFF_FILE, 'w') as f:

                        # if len(last_lines) == len(curr_lines):
                        #     for l,c in zip(last_lines,curr_lines):
                        #         print(l)
                        #         print(c)
                        #         if l==c:
                        #             f.write(l.strip('\n')+" 无变化\n")
                        #         else:
                        #             f.write("last : "+l.strip('\n')+"    "+"curr : "+c)
                        # elif len(last_lines) < len(curr_lines):
                        #     f.write("新增 "+str(len(curr_lines)-len(last_lines)))
                        # elif len(last_lines) > len(curr_lines):
                        #     f.write("减少 "+str(len(last_lines) - len(curr_lines)))

                        common_set = curr_set & last_set
                        diff_set = curr_set - last_set
                        if len(diff_set) == 0:
                            for case in curr_set:
                                f.write(case.strip() + "    测试前后无变化\n")
                            f.write('当前总共 '+str(len(curr_set))+'个测例 \n新增 测试 : '+str(len(curr_set)-len(last_set))+'\n所有测试与上次均无变化')
                        else:
                            for case in common_set:
                                f.write(case.strip() + "    测试前后无变化\n")
                            f.write("------------------------------------------------\n")
                            for case in diff_set:
                                f.write(case.strip() + "    测试后更新为此\n")
                            f.write('当前总共 '+str(len(curr_set))+'个测例 \n新增 测试 : '+str(len(curr_set)-len(last_set))+'\n变化测例 : '+str(len(diff_set)))

                    os.chdir(BASE_USER + 'zCore/scripts/')
                    TEMP_DIFF = '/home/zcore/diff/diff'+str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))+'.txt'
                    os.system('mv diff.txt '+TEMP_DIFF)
                    return TEMP_DIFF
                    
def send_mail(file_name):
    resp = os.popen('git log --pretty=tformat:%h-%cn-%ce -1').readline()
    porp = resp.strip().split('-')
    print(porp)
    sender = '734536637@qq.com'
    receivers = [porp[2]]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    #创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header("zcore kernel performance", 'utf-8')
    message['To'] =  Header(porp[1], 'utf-8')
    subject = '测试结果分析'
    message['Subject'] = Header(subject, 'utf-8')
    
    #邮件正文内容
    message.attach(MIMEText('commit : '+porp[0]+' 的测试与上一次测试比较结果 \n内容见附件 \n测试时间 '+str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")), 'plain', 'utf-8'))
    
    # 构造附件1，传送当前目录下的 test.txt 文件
    att1 = MIMEText(open(diff_name, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
    att1["Content-Disposition"] = 'attachment; filename="result.txt"'
    message.attach(att1)
    
    # 第三方 SMTP 服务
    mail_host="smtp.qq.com"  #设置服务器
    mail_user="734536637@qq.com"    #用户名
    mail_pass="srjduzcigxgqbeha"   #口令 

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        smtpObj.login(mail_user,mail_pass)  
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")



os.chdir(BASE_USER + 'zCore/scripts/')
if os.path.exists(LAST_RESULT_FILE):
    diff_name = compare_diff()
    os.system("mv test-result.txt test-result-last.txt")
    print(diff_name)
    send_mail(diff_name)

else:
    res = os.system("mv test-result.txt test-result-last.txt")





 
