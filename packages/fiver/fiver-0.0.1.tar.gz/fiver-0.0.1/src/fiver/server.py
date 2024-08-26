import os, subprocess, time, platform, signal, threading, json, socket, re
import pickledb
from .utils import path_fiverdb, is_lunix
import psutil

if is_lunix():
    import daemon

def check_status():
    db = pickledb.load(path_fiverdb(), False)
    pid = db.get('pid')
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
        
class StartServer:
    def __init__(self, serverIP, serverPort):
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.connectionSocket = None
        self.save_pid()
        self.create_socket()

    def save_pid(self):
        pid = os.getpid()
        db = pickledb.load(path_fiverdb(), False)
        db.set('pid', pid)
        db.dump()

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.serverIP, self.serverPort))
        sock.listen()
        while True:
            connectionSocket, address = sock.accept()         
            print("[server] TCP connection address:", address)

            self.connectionSocket = connectionSocket

            t_receive_messages = threading.Thread(target=self.receive_messages)
            t_receive_messages.start()   
            t_send_information = threading.Thread(target=self.send_information)
            t_send_information.start()           

    def receive_messages(self):
        maxBytes = 4096
        while True:
            try:
                message = self.connectionSocket.recv(maxBytes)

                if not message: 
                    break

                message_receive = json.loads(message.decode())

                if message_receive["key"] == "terminal":
                    print(f"[terminal] You: {message_receive["data"]}")
                    process = subprocess.Popen(message_receive["data"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    
                    data_terminal = {
                        "key": "terminal",
                        "data": (stdout + stderr).decode('utf-8', errors='ignore')
                    }

                    print((stdout + stderr).decode('utf-8', errors='ignore'))
                    self.connectionSocket.send(json.dumps(data_terminal).encode())
            except Exception as e:
                print(e)
                break

           
        self.connectionSocket.close()
        print('[server] Close socket')

    def get_disk_info(self):
        disk_info = []
        disk_total = 0

        # Iterate over all disk partitions
        for partition in psutil.disk_partitions():
            try:
                # Get disk usage statistics for each partition
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Append the partition information
                disk_info.append({
                    'device': partition.device,
                    'fstype': partition.fstype,
                    'total': usage.total / (1024 ** 3),  # Convert bytes to GB
                    'used': usage.used / (1024 ** 3),    # Convert bytes to GB
                    'free': usage.free / (1024 ** 3),    # Convert bytes to GB
                    'percent_used': usage.percent
                })

                disk_total += usage.total           
            except:
                pass
        
        return disk_info, disk_total
    
    def get_processor_name(self):
        if platform.system() == "Windows":
            return platform.processor()
        elif platform.system() == "Darwin":
            os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
            command ="sysctl -n machdep.cpu.brand_string"
            return subprocess.check_output(command).strip()
        elif platform.system() == "Linux":
            command = "cat /proc/cpuinfo"
            all_info = subprocess.check_output(command, shell=True).decode().strip()
            for line in all_info.split("\n"):
                if "model name" in line:
                    return re.sub( ".*model name.*:", "", line,1).strip()
        return ""

    def get_network_speed(self, interval=1):
        # Lấy số byte đã nhận và gửi tại thời điểm ban đầu
        net_io_start = psutil.net_io_counters()
        bytes_received_start = net_io_start.bytes_recv
        bytes_sent_start = net_io_start.bytes_sent

        # Chờ một khoảng thời gian nhất định (interval)
        time.sleep(interval)

        # Lấy số byte đã nhận và gửi tại thời điểm sau khoảng thời gian đó
        net_io_end = psutil.net_io_counters()
        bytes_received_end = net_io_end.bytes_recv
        bytes_sent_end = net_io_end.bytes_sent

        # Tính toán sự khác biệt về số byte đã nhận và gửi trong khoảng thời gian đó
        download_speed = (bytes_received_end - bytes_received_start) / interval  # Tốc độ tải xuống (bytes per second)
        upload_speed = (bytes_sent_end - bytes_sent_start) / interval  # Tốc độ tải lên (bytes per second)
    
        return download_speed, upload_speed


    def get_information(self):
        kernel = platform.release()
        if not kernel:
            kernel = platform.version()

        virtual_memory = psutil.virtual_memory()
        net_io = psutil.net_io_counters()

        return {
            "system": platform.system(),
            "node": platform.node(),
            "cpu":self.get_processor_name(),
            "kernel": kernel,
            "architecture": platform.machine(),
            "num_logical_cores": psutil.cpu_count(),
            "num_physical_cores": psutil.cpu_count(logical=False),
            "total_memory": f"{virtual_memory.total / (1024 ** 3):.2f} GB",
            "percent_used_menory": virtual_memory.used / virtual_memory.total * 100,
            "download_speed":f"{self.get_network_speed()[0] / (1024 ** 2):.2f} MB/s",
            "upload_speed":  f"{self.get_network_speed()[1] / (1024 ** 2):.2f} MB/s",
            "bytes_sent": f"{net_io.bytes_sent / (1024 ** 2):.2f} MB",
            "bytes_received": f"{net_io.bytes_recv / (1024 ** 2):.2f} MB",
            "disk_info": self.get_disk_info()[0],
            "disk_total": f"{self.get_disk_info()[1] / (1024 ** 3):.2f} GB",
            "cpu_percent": psutil.cpu_percent(interval=1),
        }

    def send_information(self):
        while True:
            try:
                data_send = {
                    "key": "information",
                    "value": self.get_information(),
                }
                # print(data_send)
                self.connectionSocket.send(json.dumps(data_send).encode())
                time.sleep(1)
            except Exception as e:
                # print(e)
                pass
    
    def save_file(self):
        pass
  

def stop_server():
    db = pickledb.load(path_fiverdb(), False)
    pid = db.get('pid')

    if check_status():
        os.kill(pid, signal.SIGTERM)  # ctrl + C
        print("[stop] Server is stopped")

        # os.kill(pid, signal.SIGKILL)  # shutdown
    else:
        print("[stop] Server is not running")
    

def server_app(server_arg):
    # server_arg: ['debug', 'start', 'status', 'stop', ]
    serverIP = socket.gethostbyname(socket.gethostname())
    serverPort = 10000

    match server_arg:
        case 'debug':
            print(f"[server] Server is running at {serverIP}:{serverPort}")
            StartServer(serverIP, serverPort)
        case 'start':
            print(f"[server] Server is running at {serverIP}:{serverPort}")
            if is_lunix():
                with daemon.DaemonContext():
                    StartServer(serverIP, serverPort)
            else:
                StartServer(serverIP, serverPort)
        case 'status':
            if check_status():
                print("[status] Fiver is running")
            else:
                print("[status] Fiver stopped")
        case 'stop':
            stop_server()
        case _:
            check_status()
