import requests


def format_messages_to_html(data,div_list):
    '''
    算法结果封装为mime形式，添加链接和字体颜色，加粗
    '''
    # print(data)
    # div_list = []
    # print(div_list)
    div_list = div_list[0]
    A = data.iat[0, 1]
    B = data.iat[1, 1]
    C = data.iat[2, 1]
    D = data.iat[3, 1]
    A = [f'<a href="https://finance.sina.com.cn/futures/quotes/{i}.shtml"> {i} | </a>' for i in A]
    As=''
    for i in A:
        As += i
    B = [f'<a href="https://finance.sina.com.cn/futures/quotes/{i}.shtml"> {i} | </a>' for i in B]
    Bs=''
    for i in B:
        Bs += i
    C = [f'<a href="https://finance.sina.com.cn/futures/quotes/{i}.shtml"> {i} | </a>' for i in C]
    Cs=''
    for i in C:
        Cs += i
    D = [f'<a href="https://finance.sina.com.cn/futures/quotes/{i}.shtml"> {i} | </a>' for i in D]
    Ds=''
    for i in D:
        Ds += i
    if As == '':
        As = '无'
    if Bs == '':
        Bs = '无'
    if Cs == '':
        Cs = '无'
    if Ds == '':
        Ds = '无'
    messages = """\
    
        <html>
        <head>
        <style>
        table, th, td {{
        border:1px solid black;
        }}
        </head>
        </style>
        <body>
            <table style="width:100%">
            <tr>
                <th>评估指标</th>
                <th>评估结果</th>
            </tr>
            <tr>
                <td>正基差</td>
                <td>{As}</td>
            </tr>
            <tr>
                <td>价格高于20日均线，且日KDJ交金叉</td>
                <td>{Bs}</td>
            </tr>
            <tr>
                <td>价格高于60分钟-20均线，且60分钟-KDJ交金叉</td>
                <td>{Cs}</td>
            </tr>
            <tr>
                <td><b><p style="color:red;">综合结果</p></b></td>
                <td>{Ds}</td>
            </tr>
            </table>
            {div_list}
        </body>
        </html>
    """
    messages = messages.format(As=As,Bs=Bs,Cs=Cs,Ds=Ds,div_list=div_list)
    return messages






def send_email(mail):
    endpoint = 'https://futurequant.azurewebsites.net/api/SendEmail'
        # {
        # "recipient": "lei.lei.fan.meng@gmail.com",
        # "subject": "This is a test email from lei",
        # 
        # "messages": "aa"}
    if mail is None:
        return False
    else:
        mail['mail_auth']="OUBDVKZHNFSBZUXY"
        mail['sender']="13091171683@163.com"
    requests.post(endpoint,json = mail)
    return True