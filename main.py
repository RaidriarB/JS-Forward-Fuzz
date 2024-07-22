from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests,os


FORWORD_PORT = 28080
ECHO_PORT = 38080
BURP_PORT = 18888
# 定义文件路径
FUZZ_FOLDER = 'fuzz-dict'
PROGRESS_FILE_NAME = 'fuzz.progress'

# ------------------------------- FUZZ -------------------------------------
def load_progress():
	"""加载当前的fuzz进度"""
	progress = {}
	progress_file = os.path.join(FUZZ_FOLDER, PROGRESS_FILE_NAME)
	if os.path.exists(progress_file):
		with open(progress_file, 'r') as file:
			for line in file:
				variable, line_number = line.strip().split()
				progress[variable] = int(line_number)
	return progress


def save_progress(progress):
	"""保存当前的fuzz进度"""
	progress_file = os.path.join(FUZZ_FOLDER, PROGRESS_FILE_NAME)
	with open(progress_file, 'w') as file:
		for variable, line_number in progress.items():
			file.write(f'{variable} {line_number}\n')

def get_next_input(variable):
	"""获取下一个fuzz输入"""
	dictionary_file = os.path.join(FUZZ_FOLDER, f'{variable}.txt')
	progress = load_progress()
	current_line = progress.get(variable, 0)

	try:
		with open(dictionary_file, 'r') as file:
			for i, line in enumerate(file):
				if i == current_line:
					progress[variable] = current_line + 1
					save_progress(progress)
					return line.strip()
		# 如果达到文件末尾，返回None表示没有更多数据
		return None
	except FileNotFoundError:
		print(f'Dictionary file for variable "{variable}" not found.')
		return None

def test():
    # 示例使用
    variable_name = 'vul_data'  # 将此替换为你的变量名
    next_input = get_next_input(variable_name)
    if next_input:
        print(f'Next fuzz input for variable "{variable_name}": {next_input}')
    else:
        print(f'No more fuzz inputs available for variable "{variable_name}".')
# --------------------------------------------------------------------------

class ForwardRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('content-length', 0))

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        data = self.rfile.read(content_length)
        if str(self.path) == "/REQUEST":
            r = requests.request('REQUEST', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                 proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                 data=data)
            new_data = r.text
            self.wfile.write(new_data.encode('utf8'))
        elif str(self.path) == "/RESPONSE":
            try:
                r = requests.request('RESPONSE', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                     proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                     data=data)
                new_data = r.text
                self.wfile.write(new_data.encode('utf8'))
            except:
                self.wfile.write(data)
        elif str(self.path) == "/FUZZ":
            param_name = data.decode()
            param_value = get_next_input(param_name)
            if param_name and param_value:
                self.wfile.write(param_value.encode('utf8'))
                print(f"Fuzzing: param 【{param_name}】->【{param_value}】")
            else:
                self.wfile.write(b'')
                print("fuzzing complete.")

class RequestHandler(BaseHTTPRequestHandler):
    def do_REQUEST(self):
        content_length = int(self.headers.get('content-length', 0))
        self.send_response(200)
        # 不加入这行会导致跨域问题
        #self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(self.rfile.read(content_length))

    do_RESPONSE = do_REQUEST

def echo_server_thread():
    print('>> 开始监听镜像服务器,端口:{}'.format(ECHO_PORT))
    server = HTTPServer(('0.0.0.0', ECHO_PORT), RequestHandler)
    server.serve_forever()

def echo_forward_server_thread():
    print('>> 开始监听转发服务器,端口:{}'.format(FORWORD_PORT))
    server = HTTPServer(('0.0.0.0', FORWORD_PORT), ForwardRequestHandler)
    server.serve_forever()




def get_payload():
    while(1):
        #print("=========================== Payload Generator ========================================")
        param_name = input(">> 请输入要传递出来的参数名(输入回车结束)：\n> ")
        if not param_name:
            return False
        request_type = input(">> 请输入针对该变量的动作：\n 1 将变量继续传递（如传递至burpsuite）\n 2 基于程序字典文件夹执行fuzz操作：\n> ")
        data_type = input(">> 请输入" + param_name +  "的数据类型(json/string)：\n> ")
        if request_type.strip() == "1":
            if data_type == "json":
                base_payload = f'var xhr = new XMLHttpRequest();xhr.open("post", "http://127.0.0.1:{FORWORD_PORT}/REQUEST", false);xhr.send(JSON.stringify({param_name}));{param_name}=JSON.parse(xhr.responseText);'
            elif data_type == "string":
                base_payload = f'var xhr = new XMLHttpRequest();xhr.open("post", "http://127.0.0.1:{FORWORD_PORT}/REQUEST", false);xhr.send({param_name});{param_name}=xhr.responseText;'
            else:
                print(">> 您的数据类型输入有误")
                return True
        elif request_type.strip() == "2":
            #base_payload = f'var xhr = new XMLHttpRequest();xhr.open("post", "http://127.0.0.1:{FORWORD_PORT}/FUZZ", false);xhr.send({param_name});{param_name}=xhr.responseText;'
            if data_type == "json":
                base_payload = f'var xhr = new XMLHttpRequest();xhr.open("post", "http://127.0.0.1:{FORWORD_PORT}/FUZZ", false);xhr.send("{param_name}");{param_name}=JSON.parse(xhr.responseText);'
            elif data_type == "string":
                base_payload = f'var xhr = new XMLHttpRequest();xhr.open("post", "http://127.0.0.1:{FORWORD_PORT}/FUZZ", false);xhr.send("{param_name}");{param_name}=xhr.responseText;'
            else:
                print(">> 您的数据类型输入有误")
                return True
        else:
            print(">> 您的请求标识输入有误")
            return True
        print('>> payload生成完毕:\n' + base_payload)
    print("============================================================================================")


def banner():
    banner=r'''
============================================================
         __    _____  __          __  __    ___   ____ 
       |/__`__|__/  \|__)|  | /\ |__)|  \__|__|  | / / 
    \__/.__/  |  \__/|  \|/\|/~~\|  \|__/  |  \__//_/_ 
                                                   
============================================================


'''
    print(banner)



if __name__ == '__main__':
    banner()
    flag = True
    while flag:
        flag = get_payload()
    t1 = Thread(target=echo_forward_server_thread)
    t = Thread(target=echo_server_thread)
    t.daemon = True
    t.start()
    t1.daemon = True
    t1.start()
    print(f">准备就绪,程序转发出的变量值将会发往端口: {BURP_PORT}")
    for t in [t, t1]:
        t.join()
