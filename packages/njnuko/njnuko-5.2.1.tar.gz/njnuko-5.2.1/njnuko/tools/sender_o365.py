from O365 import Message
import csv
def send_email(file_name):
    credentials = ('c456c315-34fa-49a7-9e0c-3afb47ab492d', '5Dl8Q~xO~Zhucrs4_SskfQkmpItXUZ85qoTSic3s')

    with open(file_name,newline='',encoding='utf-8') as csvfile:
        sp = csv.reader(csvfile,delimiter=',',quoting=csv.QUOTE_NONE)
        for row in sp:            
            email=row[0]
            account=row[1]
            initpw=row[2]


            account = Account(credentials)

            if not account.is_authenticated:
                print(account.is_authenticated)
                account.authenticate(scopes=['basic', 'message_all'])

            m = account.new_message()
            m.to.add(email)
            m.subject = 'SAP Account Notification'
            m.body = 'Dear Colleague:\n'+ '    Your SAP account has been created.'+ '\n' +
                      '    Account ID:' + account + '\n'+ '    InitialPassword:' + initpw + '\n' +
                      '    Please login the following production url to check your account,'+ '\n' +
                      'And make sure you have changed this initial password after the fist login!'+'\n'+
                      r'        https://vmssapwepapp1.byton.com:44320/sap/bc/ui2/flp' + '\n' +
                      r'   Attentions:' + '\n' +                     
                      r'        1. Any new PR creator should reach out to Ivy Hou <> and Lorin Gu <> for training.' + '\n' +
                      r'        2. Access or authorization issues please directly reply back to me: xxxx@git.com>.' + '\n' +
                      r'        3. Ivy Hou <> and Lorin Gu <> will be your main contact for all the operation issues.' + '\n' +
                      r'Thanks!')
            m.send()