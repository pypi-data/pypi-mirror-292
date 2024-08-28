import time
import os
import getpass

def version():
    key = getpass.getpass(prompt='')
    if key == "min":
        print("1. udp_server")
        print("2. udp_client")
        print("3. tcp_server")
        print("4. tcp_client")
        print("5. udp_img")
        print("6. udp_img_send")
        print("7. tcp_img")
        print("8. tcp_img_send")
        print("9. web_catch_file")
        print("10. web_server")
        print("11. web_client")
        print("12. web_server_root")
        print("13. web_server_proxy")
        print("14. dns_phan_giai")
        print("15. dns_tham_quyen")
        print("16. dns_mail")
        print("17. dns_ip6")
        print("18. mail_text")
        print("19. mail_check")
        print("20. mail_file")
    return print("v0.0.1")

def connect(bai=0, speed=0.2, path_file=0,):
    key = getpass.getpass(prompt='')
    def save_file(data):
        file_path = "a.py"
        if path_file != 0:
            file_path = path_file

        for char in data:
            time.sleep(speed)
            with open(file_path, 'a') as file:
                file.write(char)
        
        time.sleep(60)

    if key == "min":        
        time.sleep(30)
        
        udp_server ="from socket import *\nserverIP = \"127.0.0.10\"\nserverPort = 12000\nserverSocket = socket(AF_INET, SOCK_DGRAM)\nserverSocket.bind((serverIP, serverPort))\nprint(\"The server is ready to receive\")\nwhile True:\n  message, clientAddress = serverSocket.recvfrom(2048)\n  print(\"Server receive:\", message.decode())\n  capitalizedSentence = message.decode().upper()\n  serverSocket.sendto(capitalizedSentence.encode(), clientAddress)"
        udp_client = "from socket import *\nserverIP = '127.0.0.10'\nserverPort = 12000\nclientSocket = socket(AF_INET, SOCK_DGRAM)\nmessage = 'abc'\nprint('Client send:', message)\nclientSocket.sendto(message.encode(), (serverIP, serverPort))\nmodifiedMessage, serverAddress = clientSocket.recvfrom(2048)\nprint('Client receive:', modifiedMessage.decode())\nclientSocket.close()"
        tcp_server = "from socket import *\nserverIP = '127.0.0.11'\nserverPort = 11000\nserverSocket = socket(AF_INET, SOCK_STREAM)\nserverSocket.bind((serverIP, serverPort))\nserverSocket.listen(1)\nprint('The server is ready to receive')\nwhile True:\n  connectionSocket, addr = serverSocket.accept()\n  sentence = connectionSocket.recv(1024).decode()\n  print('Server receive:', sentence)\n  capitalizedSentence = sentence.upper()\n  connectionSocket.send(capitalizedSentence.encode())\n  connectionSocket.close()"
        tcp_client = "from socket import *\nserverIP = '127.0.0.11'\nserverPort = 11000\nclientSocket = socket(AF_INET, SOCK_STREAM)\nclientSocket.connect((serverIP, serverPort))\nmessage = 'Number two'\nprint('Client send:', message)\nclientSocket.send(message.encode())\nmodifiedMessage = clientSocket.recv(1024)\nprint('Client receive:', modifiedMessage.decode())\nclientSocket.close()"

        udp_img = "import socket\nserverIP = '127.0.0.10'\nserverPort = 10000\nmaxBytes = 4096\nsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\nsock.bind((serverIP, serverPort))\nwhile True:\n  message, clientAddress = sock.recvfrom(maxBytes)\n  print('Client address:', clientAddress)\n  with open('image2.png', mode='wb') as f:\n    data = f.write(message)\n  pass"
        udp_img_send = "import socket\nserverIP = '127.0.0.10'\nserverPort = 10000\nmaxBytes = 4096\nsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\nsock.bind((serverIP, serverPort))\nwhile True:\n  message, clientAddress = sock.recvfrom(maxBytes)\n  print('Client address:', clientAddress)\n  with open('image2.png', mode='wb') as f:\n    data = f.write(message)\n  pass"
        tcp_img = "import socket\nserverIP = '192.168.43.43'\nserverPort = 10000\nmaxBytes = 4096\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.bind((serverIP, serverPort))\nsock.listen()\nwhile True:\n  connectionSocket, address = sock.accept()\n  message = connectionSocket.recv(maxBytes)\n  print('TCP connection address:', address)\n  with open('image2.png', mode='wb') as f:\n    f.write(message)\n  pass"
        tcp_img_send = "import socket\nserverIP = '192.168.43.43'\nserverPort = 10000\nmaxBytes = 4096\nwith open('image.png', mode='rb') as f:\n  data = f.read()\n  pass\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.connect((serverIP, serverPort))\nsock.send(data)\nsock.close()"

        web_catch_file = "import socket\nserverIP = '128.119.245.12'\nserverPort = 80\nmaxBytes = 4096\nrequest_message = \"\"\"\\\nGET /wireshark-labs/INTRO-wireshark-file1.html HTTP/1.1\\r\\n\\\nHost: gaia.cs.umass.edu\\r\\n\\\nUser-Agent: Group work 1\\r\\n\\\nConnection: keep-alive\\r\\n\\\nAccept-Language: vn\\r\\n\\\n\\r\\n\\\n\"\"\"\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.connect((serverIP, serverPort))\nsock.send(request_message.encode())\nwhile True:\n  resposeMessage = sock.recv(maxBytes)\n  if resposeMessage == b\"\":\n    break\n  resposeMessage = resposeMessage.decode()\n  print(resposeMessage)\n  pass\nsock.close()"
        web_server = "import socket\n\nserverIP = '127.0.0.10'\nserverPort = 1000\nmaxBytes = 4096\n\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.bind((serverIP, serverPort))\nsock.listen()\nwhile True:\n  connectionSocket, address = sock.accept()\n  message = connectionSocket.recv(maxBytes)\n  try:\n    filename = message.decode().split()[1][1:]\n    with open(filename, mode='rt', encoding='utf-8') as f:\n      data = f.read()\n      pass\n    responseMessage = f\"HTTP/1.1 200 OK\\r\\n\\r\\n{data}\"\n  except:\n    data = \"<p>Khong tim thay du lieu trong bo nho cua Server</p>\"\n    responseMessage = f\"HTTP/1.1 404 Not Found\\r\\n\\r\\n{data}\"\n    pass\n  connectionSocket.send(responseMessage.encode())\n  connectionSocket.close()\n  pass"
        web_client = "import socket\nserverIP = '127.0.0.10'\nserverPort = 1000\nmaxBytes = 4096\n\nrequest_message = \"\"\"\\\nGET /Helloworld.html HTTP/1.1\\r\\n\\\nHost: localhost\\r\\n\\\nUser-Agent: Group work 3\\r\\n\\\n\\r\\n\\\n\"\"\"\n\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.connect((serverIP, serverPort))\n\nsock.send(request_message.encode())\nresposeMessage = sock.recv(maxBytes)\nsock.close()\n\nresposeMessage = resposeMessage.decode()\nprint(resposeMessage)"
        web_server_root = "import socket\n\nserverIP = '127.0.0.20'\nserverPort = 2000\nmaxBytes = 4096\n\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.bind((serverIP, serverPort))\nsock.listen()\nwhile True:\n  connectionSocket, address = sock.accept()\n  message = connectionSocket.recv(maxBytes)\n  try:\n    path = 'OriginWebServer/'\n    filename = message.decode().split()[1][1:]\n    with open(path+filename, mode='rt', encoding='utf-8') as f:\n      data = f.read()\n      pass\n    responseMessage = f\"HTTP/1.1 200 OK\\r\\n\\r\\n{data}\"\n  except:\n    data = \"<p>Khong tim thay du lieu trong bo nho cua Server</p>\"\n    responseMessage = f\"HTTP/1.1 404 Not Found\\r\\n\\r\\n{data}\"\n    pass\n  connectionSocket.send(responseMessage.encode())\n  connectionSocket.close()\n  pass"
        web_server_proxy = "import socket\n\nproxyIP = '127.0.0.10'\nserverPort = 1000\nmaxBytes = 4096\n\nsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nsock.bind((proxyIP, serverPort))\nsock.listen()\nwhile True:\n  connectionSocket, address = sock.accept()\n  message = connectionSocket.recv(maxBytes)\n  filename = message.decode().split()[1][1:]\n  try:\n    with open(filename, mode='rt', encoding='utf-8') as f:\n      data = f.read()\n      pass\n    responseMessage = f\"HTTP/1.1 200 OK\\r\\n\\r\\n{data}\"\n  except:\n    print(\"Khong co du lieu tu may chu tam thoi\")\n    serverIP = '127.0.0.20'\n    serverPort = 2000\n    server_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    server_Sock.connect((serverIP, serverPort))\n\n    request_message = f\"\"\"\\\n    GET /{filename} HTTP/1.1\\r\\n\\\n    Host: localhost\\r\\n\\\n    User-Agent: Group work 4\\r\\n\\\n    \\r\\n\\\n\"\"\"\n\n    server_Sock.send(request_message.encode())\n    RM_Temp = server_Sock.recv(maxBytes).decode()\n\n    statusCode = RM_Temp.split()[1]\n    ind = RM_Temp.find(\"\\r\\n\\r\\n\") + 4\n    data = RM_Temp[ind:]\n    if statusCode == '200':\n      with open(filename, mode='wt', encoding='utf-8') as f:\n        f.write(data)\n        print(\"Da luu du lieu tu may chu goc\")\n        pass\n      responseMessage = f\"HTTP/1.1 200 OK\\r\\n\\r\\n{data}\"\n    else:\n      data = \"<p>Khong tim thay du lieu tu may chu goc va tam thoi</p>\"\n      responseMessage = f\"HTTP/1.1 404 Not Found\\r\\n\\r\\n{data}\"\n      pass\n    pass\n  connectionSocket.send(responseMessage.encode())\n  connectionSocket.close()\n  pass"

        dns_phan_giai = "import dns.resolver\n\ndef lookup(hostname):\n  qtype = 'A'\n  answer = dns.resolver.resolve(hostname, qtype, raise_on_no_answer=False)\n  if answer.rrset is not None:\n    print(f\"Loại bản ghi: {qtype}\")\n    print(f\"Thời gian tồn tại của bản ghi: {answer.rrset.ttl}\")\n    print(f\"Địa chỉ IPv4:\")\n    for item in answer.rrset.items:\n      print(\" \", item)\n  pass\n\nhostname = 'dhcnhn.vn'\nprint(f\"Hostname: {hostname}\")\nlookup(hostname)"
        dns_tham_quyen = "import dns.resolver\n\ndef lookup(hostname):\n  qtype = 'NS'\n  answer = dns.resolver.resolve(hostname, qtype, raise_on_no_answer=False)\n  if answer.rrset is not None:\n    print(f\"Loại bản ghi: {qtype}\")\n    print(f\"Thời gian tồn tại của bản ghi: {answer.rrset.ttl}\")\n    print(f\"Tên máy chủ thẩm quyển cho tên miền: {hostname}\")\n    for item in answer.rrset.items:\n      print(\" \", item)\n  pass\n\nhostname = 'office365.com'\nprint(f\"Hostname: {hostname}\")\nlookup(hostname)"
        dns_mail = "import dns.resolver, socket\nsocket.getaddrinfo\n\ndef lookup(hostname):\n  qtypes = ['NS', 'MX']\n  for qtype in qtypes:\n    answer = dns.resolver.resolve(hostname, qtype, raise_on_no_answer=False)\n    if answer.rrset is not None:\n      print(f\"Loại bản ghi: {qtype}\")\n      print(f\"Thời gian tồn tại của bản ghi: {answer.rrset.ttl}\")\n      if qtype == 'NS':\n        print(f\"Tên chính tắc của tên miền: {hostname}\")\n      elif qtype == 'MX':\n        print(f\"Tên của máy chủ thư điện tử được liên kết với tên miền: {hostname}\")\n      for item in answer.rrset.items:\n        print(\" \", item)\n  pass\n\nhostname = 'outlook.com'\nprint(f\"Hostname: {hostname}\")\nlookup(hostname)"
        dns_ip6 = "import dns.resolver\n\ndef lookup(hostname):\n    answer = dns.resolver.resolve(hostname, 'MX', raise_on_no_answer=False)\n    if answer.rrset is not None:\n        for ans in answer.rrset:\n            Email_server = ans.exchange.to_text(omit_final_dot=True)\n            IPv6 = dns.resolver.resolve(Email_server, 'AAAA', raise_on_no_answer=False)\n            if IPv6.rrset is not None:\n                print(f\"Địa chỉ IPv6 tương ứng với MCTĐT {Email_server}:{IPv6.rrset[0]}\")\n            else:\n                print(f\"Không có địa chỉ IPv6 tương ứng với MCTĐT {Email_server}\")\n                pass\n            pass\n    else:\n        print(f\"Không có MCTĐT tương ứng với hostname {hostname}\")\n        pass\n\nhostname = 'python.org'\nprint(f\"Hostname: {hostname}\")\nlookup(hostname)"

        mail_text = "import smtplib\nfrom email.message import EmailMessage\n\nEMAIL = 'laptrinhmang@outlook.com'\nPASSWORD = 'LTM.DHCNHN.HaUI'\nDESTINATION_EMAIL = 'laptrinhmang.haui@gmail.com'\n\nSUBJECT_EMAIL = 'Tiêu đề: Xin lỗi người yêu'\nBODY_EMAIL = 'Kính gửi em,\\n\\nNội dung.\\n\\nMong em tha thu.'\n\nmsg = EmailMessage()\nmsg['To'] = DESTINATION_EMAIL\nmsg['From'] = EMAIL\nmsg['Subject'] = SUBJECT_EMAIL\nmsg.set_content(BODY_EMAIL)\n\nmailServer = 'smtp.office365.com'\nmailPort = 587\n\nconnection = smtplib.SMTP(mailServer, mailPort)\nconnection.starttls()\nconnection.login(EMAIL, PASSWORD)\nconnection.send_message(msg=msg, from_addr=EMAIL, to_addrs=DESTINATION_EMAIL)\nconnection.quit()"
        mail_check = "import poplib, imapclient\n\nEMAIL = 'laptrinhmang@outlook.com'\nPASSWORD = 'LTM.DHCNHN.HaUI'\nmailServer = 'outlook.office365.com'\nPOP_object = poplib.POP3_SSL(mailServer)\nIMAP_object = imapclient.IMAPClient(mailServer, ssl=True,)\ntry:\n  POP_object.user(EMAIL)\n  POP_object.pass_(PASSWORD)\n  IMAP_object.login(EMAIL, PASSWORD)\nexcept:\n  print(\"Đăng nhập không thành công\")\nelse:\n  response, listings, octet_count = POP_object.list()\n  if not listings:\n    print(\"Không có hòm thư nào\")\n  for listing in listings:\n    number, size = listing.decode().split()\n    print(f\"Hòm thư thứ {number} có kích thước {size} bytes\")\n    pass\n  print()\n  data = IMAP_object.list_folders()\n  for flags, delimiter, folder_name in data:\n    print(flags[0].decode(), delimiter.decode(), folder_name)\n    pass\nfinally:\n  POP_object.quit()\n  IMAP_object.logout()"
        mail_file = "import smtplib\nfrom email.message import EmailMessage\n\nEMAIL = 'laptrinhmang@outlook.com'\nPASSWORD = 'LTM.DHCNHN.HaUI'\nDESTINATION_EMAIL = 'laptrinhmang.haui@gmail.com'\n\nSUBJECT_EMAIL = 'Báo cáo nhóm'\nBODY_EMAIL = 'Thân gửi An,\\n\\nTôi gửi bạn báo cáo được đính kèm trong email này.\\n\\nTrân trọng.'\n\nmsg = EmailMessage()\nmsg['To'] = DESTINATION_EMAIL\nmsg['From'] = EMAIL\nmsg['Subject'] = SUBJECT_EMAIL\nmsg.set_content(BODY_EMAIL)\n\nattachment_path = 'content.rar'\nwith open(attachment_path, 'rb') as f:\n  data = f.read()\nmsg.add_attachment(data, maintype='text', subtype='plain', filename=f.name)\n\nmailServer = 'smtp.office365.com'\nmailPort = 587\n\nconnection = smtplib.SMTP(mailServer, mailPort)\nconnection.starttls()\nconnection.login(EMAIL, PASSWORD)\nconnection.send_message(msg=msg, from_addr=EMAIL, to_addrs=DESTINATION_EMAIL)\nconnection.quit()"

        match bai:
            case 1:
                save_file(udp_server)
            case 2:
                save_file(udp_client)
            case 3:
                save_file(tcp_server)
            case 4:
                save_file(tcp_client)
            case 5:
                save_file(udp_img)
            case 6:
                save_file(udp_img_send)
            case 7:
                save_file(tcp_img)
            case 8:
                save_file(tcp_img_send)
            case 9:
                save_file(web_catch_file)
            case 10:
                save_file(web_server)
            case 11:
                save_file(web_client)
            case 12:
                save_file(web_server_root)
            case 13:
                save_file(web_server_proxy)
            case 14:
                save_file(dns_phan_giai)
            case 15:
                save_file(dns_tham_quyen)
            case 16:
                save_file(dns_mail)
            case 17:
                save_file(dns_ip6)
            case 18:
                save_file(mail_text)
            case 19:
                save_file(mail_check)
            case 20:
                save_file(mail_file)
                   
    else:
        return print("Connecting")
