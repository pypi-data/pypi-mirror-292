import sys, socket, json
from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Header, Footer, Static, ProgressBar, Input, Button, Log
from textual import work
from textual.containers import Horizontal, Container, HorizontalScroll, VerticalScroll
from textual.reactive import reactive


class Info(Widget):
    information_data = reactive("")  

    def __init__(self, key_info):
        super().__init__()
        self.key_info = key_info

    def render(self) -> str:
        try:
            information_data_json = json.loads(self.information_data)
        except:
            return ""
        
        match self.key_info:
            case "system":
                return information_data_json["system"]
            case "node":
                return information_data_json["node"]
            case "kernel":
                return information_data_json["kernel"]
            case "cpu":
                return information_data_json["cpu"]
            case "architecture":
                return information_data_json["architecture"]
            case "cores":
                return f"Logical: {information_data_json["num_logical_cores"]} - Physical: {information_data_json["num_physical_cores"]}"
            case "ram":
                return information_data_json["total_memory"]
            case "disk_total":
                return information_data_json["disk_total"]
            case "disk":
                disk_data = "\nDisk:\n"
                for disk in information_data_json["disk_info"]:
                    disk_data += f" {disk["device"]}: {disk["used"]:.2f}/{disk["total"]:.2f} GB ({disk["percent_used"]}%)\n"
                return disk_data
            case "download_speed":
                return f" Receiving: {information_data_json["download_speed"]}"
            case "upload_speed":
                return f" Sending: {information_data_json["upload_speed"]}"
            case "bytes_received":
                return f" Total Received: {information_data_json["bytes_received"]}"
            case "bytes_sent":
                return f" Total Sent: {information_data_json["bytes_sent"]}"
        return ""

class ClientGui(App):
    CSS = """
        Screen {
            scrollbar-size: 1 1;
            overflow-x: scroll;
        }

        .info_area {
            padding-top: 1;
            height: auto;
        }

        .info_item {
            color: white;
            border: solid white;
            padding: 1 2;
            margin-left: 1;
            height: 20;
            width: 60;
        }

        .info_horizontal {
            height: 2;
        }

        .info_item_name {
            width: 15;
        }

        .info_item_value {
            width: 30;
        }

        .network_horizontal {
            height: 1;
        }

        .network_item {
            width: 50%;
        }

        .send_file {
            color: white;
            border: solid white;
            padding: 1 2;
            margin: 1;
            height: auto;
        }

        .send_file_button {
            margin-top: 1;
        }

        .terminal {
            color: white;
            border: solid white;
            padding: 1 2;
            margin: 1;
            height: auto;
        }

        .terminal_note {
            margin-bottom: 1;
            margin-left: 1;
        }

        .terminal_log {
            background: black;
            padding-left: 1;
            padding-top: 1;
            height: 20;
        }
    """

    BINDINGS = [
        Binding(key="q", action="quit_app", description="Quit the app"),
    ]

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.quit = False

    def compose(self) -> ComposeResult:
        info_item_one = Container(
            Horizontal(
                Static("OS:", classes="info_item_name"),
                Container(Info("system"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Node:", classes="info_item_name"),
                Container(Info("node"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Kernel:", classes="info_item_name"),
                Container(Info("kernel"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Architecture:", classes="info_item_name"),
                Container(Info("architecture"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Cpu:", classes="info_item_name"),
                Container(Info("cpu"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Cores:", classes="info_item_name"),
                Container(Info("cores"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Ram:", classes="info_item_name"),
                Container(Info("ram"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Storage:", classes="info_item_name"),
                Container(Info("disk_total"), classes="info_item_vaule"),
                classes="info_horizontal",
            ),
            classes="info_item",
        )
        info_item_one.border_title = "System Information"

        info_item_two = Container(
            Horizontal(
                Static("CPU:", classes="info_item_name"),
                ProgressBar(show_eta=False, classes="info_item_vaule", id="cpu_percent"),
                classes="info_horizontal",
            ),
            Horizontal(
                Static("Ram:", classes="info_item_name"),
                ProgressBar(show_eta=False, classes="info_item_vaule", id="percent_used_menory"),
                classes="info_horizontal",
            ),
           
            Static("Network:"),
            Horizontal(
                Container(Info("download_speed"), classes="network_item"),
                Container(Info("upload_speed"), classes="network_item"),
                classes="network_horizontal",
            ),
            Horizontal(
                Container(Info("bytes_received"), classes="network_item"),
                Container(Info("bytes_sent"), classes="network_item"),
                classes="network_horizontal",
            ),
            Info("disk"),
            classes="info_item",             
        )
        info_item_two.border_title = "Resource Utilization"
        
        # send_file = Container(
        #     Input(placeholder="File path to send", id="file_path_send"),
        #     Input(placeholder="Folder path to receive"),
        #     Static("[bold red]ddd[/]", id="send_file_error"),
        #     Static("[bold green]ddd[/]", id="send_file_success"),
        #     Button("Send", variant="primary", classes="send_file_button", id="send_file"),
        #     classes="send_file"
        # )
        # send_file.border_title = "Send file"

        terminal = Container(
            Input(placeholder="Enter command to execute", id="terminal_input"),
            Static("Enter to send", classes="terminal_note"),
            Log(auto_scroll=True, classes="terminal_log"),
            classes="terminal"
        )
        terminal.border_title = "Terminal"

        yield Header(show_clock=True)
        yield VerticalScroll(
            HorizontalScroll(
                info_item_one,
                info_item_two,
                classes="info_area",
            ),
            terminal,
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Fiver"
        self.update_data()

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     """Event handler called when a button is pressed."""
    #     log = self.query_one(Log)
    #     if event.button.id == "send_file":
    #         file_path_send = self.query_one("#file_path_send").value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called as the user types."""
        log = self.query_one(Log)
        if event.input.id == "terminal_input":
            data = self.query_one("#terminal_input").value

            if data == "clear":
                log.clear()
                self.query_one("#terminal_input").clear()
                return

            data_send = {
                "key": "terminal",
                "data": data,
            }
            self.sock.send(json.dumps(data_send).encode())

            log.write_line(f"You: {data}")
            self.query_one("#terminal_input").clear()
            

    @work(exclusive=True, thread=True)
    def update_data(self):        
        maxBytes = 4096
        log = self.query_one(Log)

        while True:
            if self.quit:
                break

            message_receive = self.sock.recv(maxBytes)

            try:
                message_receive = json.loads(message_receive.decode())
            except:
                continue
            
            if message_receive["key"] == "information":
                for widget in self.query(Info):
                    widget.information_data = json.dumps(message_receive["value"])
                
                self.query_one("#cpu_percent").update(
                    total = 100,
                    progress = message_receive["value"]["cpu_percent"],
                )

                self.query_one("#percent_used_menory").update(
                    total = 100,
                    progress = message_receive["value"]["percent_used_menory"],
                )

                self.query_one("#percent_used_menory").update(
                    total = 100,
                    progress = message_receive["value"]["percent_used_menory"],
                )
            elif message_receive["key"] == "terminal":
                log.write_line(f"{message_receive["data"]}")
            

    def action_quit_app(self):
        self.quit = True
        sys.exit(1)
        
    

def client_app(address):
    try:
        serverIP, serverPort = address.split(':')
    except:
        return print("[error] Ip server is incorrect")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((serverIP, int(serverPort)))
    except socket.error as e:
        return print(f"[error] {e}")

    app = ClientGui(sock)
    app.run()
    
 


    