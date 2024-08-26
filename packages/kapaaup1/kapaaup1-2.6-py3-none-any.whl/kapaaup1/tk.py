import tkinter as tk
from tkinter import font
import socket
import threading
from image_recognition import main_function

# 设置远程服务器地址为 ('127.0.0.1', 2002)
remote_server_address = ('192.168.2.12', 2002)
#remote_server_address = ('127.0.0.1', 2002)
# 初始化 socket_client 变量为 None
socket_client = None


# 定义名为 connect_to_server 的函数，接受 connect_btn 参数
def connect_to_server(connect_btn):
    global socket_client

    # 检查是否需要建立新的连接
    if socket_client is None or socket_client.fileno() == -1:
        try:
            # 创建一个新的 socket 客户端并连接到远程服务器地址
            socket_client = socket.socket()
            socket_client.connect(remote_server_address)
            print("成功连接到服务器")
            # 设置按钮颜色为绿色表示成功连接
            connect_btn.config(bg="green")
        except ConnectionRefusedError as e:
            # 处理连接被拒绝的情况
            print("无法连接到服务器：连接被拒绝，错误信息:", e)
            socket_client = None
            # 设置按钮颜色为红色表示连接失败
            connect_btn.config(bg="red")
        except Exception as e:
            # 处理其他连接错误
            print("连接错误:", e)
            socket_client = None
            print("无法连接到服务器：请检查网络连接或服务器地址.")
            # 设置按钮颜色为红色表示连接失败
            connect_btn.config(bg="red")
    else:
        print("已连接到服务器")
def login():
    open_new_window()
    # 检查输入的用户名和密码是否匹配凭据 "admin" 和 "123456"
    if username_entry.get() == "admin" and password_entry.get() == "123456":
        # 如果凭据正确，隐藏登录屏幕并打开一个新窗口
        login_screen.withdraw()
        open_new_window()
    else:
        # 如果凭据不匹配，显示错误消息并清除输入字段
        error_label.config(text="输入有误，请重新输入")  # 显示错误消息
        username_entry.delete(0, 'end')  # 清除用户名输入字段
        password_entry.delete(0, 'end')  # 清除密码输入字段


def send_command_to_server(command):
    global socket_client

    try:
        # 检查是否存在有效的套接字对象和连接
        if socket_client is not None and socket_client.fileno() != -1:
            # 将指令编码并发送到服务器
            socket_client.send(command.encode())
            print(f"已发送指令到服务器: {command}")
        else:
            # 若未建立有效连接，显示提示信息
            print("未建立有效连接到服务器")
    except Exception as e:
        # 捕获异常并打印错误消息
        print("发送指令时出错:", e)


def open_new_window():
    # 定义一个函数来运行图像识别
    def run_image_recognition():
        threading.Thread(target=main_function).start()
        try:
            # 模拟成功执行图像识别的情况
            print("图像识别代码调用成功")
            recognize_button.config(bg="green")  # 更改“图像识别”按钮颜色为绿色
        except Exception as e:
            print(f"图像识别出错: {e}")

    # 创建一个新窗口
    new_window = tk.Toplevel()
    new_window.title("运行窗口")  # 设置新窗口标题
    new_window.geometry("400x350")  # 设置新窗口大小
    custom_font = font.Font(family='Arial', size=12)
    new_window.configure(bg='#f5f5f5')  # 设置新窗口背景颜色

    # 创建和配置“通讯连接”按钮
    connect_button = tk.Button(new_window, text="通讯连接", font=custom_font)
    connect_button.pack(pady=10)
    connect_button.config(command=lambda: connect_to_server(connect_button))

    # 创建和配置“正转启动”按钮
    forward_button = tk.Button(new_window, text="正转启动", font=custom_font)
    forward_button.pack(pady=10)
    forward_button.config(command=lambda: send_command_to_server("an_plc_zz"))

    # 创建和配置“反转启动”按钮
    reverse_button = tk.Button(new_window, text="反转启动", font=custom_font)
    reverse_button.pack(pady=10)
    reverse_button.config(command=lambda: send_command_to_server("an_plc_fz"))


    # 创建和配置“物资分拣”按钮
    sort_button = tk.Button(new_window, text="物资分拣", font=custom_font)
    sort_button.pack(pady=10)
    sort_button.config(command=lambda: send_command_to_server("an_plc_wz"))

    # 创建和配置“图像识别”按钮
    recognize_button = tk.Button(new_window, text="图像识别", font=custom_font)
    recognize_button.pack(pady=10)
    recognize_button.config(command=run_image_recognition)

    try:
        new_window.mainloop()  # 进入新窗口的主事件循环
    except KeyboardInterrupt:
        new_window.destroy()  # 异常处理：销毁新窗口

login_screen = tk.Tk()
login_screen.title("人工智能机器人系统集成")  # 设置登录窗口标题
login_screen.geometry("400x250")  # 设置登录窗口大小

username_label = tk.Label(login_screen, text="用户名", font=("Arial", 12))
username_label.pack(pady=10)  # 显示“用户名”标签
username_entry = tk.Entry(login_screen)
username_entry.pack(pady=5)  # 创建并显示用户名输入框

password_label = tk.Label(login_screen, text="密码", font=("Arial", 12))
password_label.pack(pady=5)  # 显示“密码”标签
password_entry = tk.Entry(login_screen, show="*")
password_entry.pack(pady=5)  # 创建并显示密码输入框（显示为*）

error_label = tk.Label(login_screen, text="", fg="red")
error_label.pack(pady=5)  # 显示错误消息的标签

login_button = tk.Button(login_screen, text="登录", command=login)
login_button.pack(pady=10)  # 创建并显示登录按钮，点击时执行登录函数

try:
    login_screen.mainloop()  # 进入登录窗口的主事件循环
except KeyboardInterrupt:
    login_screen.destroy()  # 异常处理：销毁登录窗口
