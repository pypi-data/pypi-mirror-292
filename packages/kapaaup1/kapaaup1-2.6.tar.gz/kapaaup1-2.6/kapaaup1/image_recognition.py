# 导入必要的库
import cv2
import torch
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os
import time
from torchvision import models
import socket

# 清除存储分类结果图像的目录中的所有文件
def clear_cached_images():
    path = './result/'
    if os.path.exists(path):
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))
    else:
        os.makedirs(path)

# 载入预训练的ResNet-18模型，并加载预训练参数
def load_model():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model_eval = models.resnet18(pretrained=False)
    num_ftrs = model_eval.fc.in_features
    model_eval.fc = nn.Linear(num_ftrs, 8)  # 假设有8个类别
    model_eval.load_state_dict(torch.load('./model/dobot.pkl', map_location=device))
    model_eval.eval()
    return model_eval

# 对输入的图像进行推断，返回预测的类别标签和类别名称
def model_inference(model, src_roi):
    # 将ROI转换为灰度图像
    grey_img = cv2.cvtColor(src_roi, cv2.COLOR_BGR2GRAY)
    image_array = cv2.cvtColor(grey_img, cv2.COLOR_GRAY2RGB)
    image = Image.fromarray(image_array)

    # 定义输入图像的转换管道
    tsfrm = transforms.Compose([
        transforms.Grayscale(3),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])

    # 应用转换到图像
    img = tsfrm(image).unsqueeze(0)

    # 通过模型进行前向传播
    output = model(img)
    prob = str(F.softmax(output, dim=1))
    value, predicted = torch.max(output.data, 1)

    # 将预测的类别索引映射到类别名称
    classes = {0: '方便面', 1: '面包', 2: '香肠', 3: '矿泉水',4: '饼干', 5: '苹果', 6: '可乐', 7: '香蕉'}
    pred_class = classes.get(predicted.item(), '未知物料')

    return predicted.numpy()[0], pred_class

# 将图像显示在屏幕上，并在图像上添加文本标签，然后保存带标签的图像
def display_result(img, text):
    # 调整图像大小以便显示
    new_img = cv2.resize(img, (640, 480))
    fontpath = "font/simsun.ttc"
    font = ImageFont.truetype(fontpath, 48)
    img_pil = Image.fromarray(new_img)
    draw = ImageDraw.Draw(img_pil)
    # 在图像上添加文本
    draw.text((10, 100), text, font=font, fill=(0, 0, 255))
    bk_img = np.array(img_pil)

    # 保存处理后的图像
    str_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    img_name = str_time + '.jpg'
    cv2.imwrite('./result/' + img_name, bk_img)
    # 在屏幕上显示处理后的图像3秒
    cv2.imshow('frame', bk_img)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()

# 主函数，包含了Socket连接的建立、数据接收、模型推断和结果显示等操作
def main_function():
    socket_client = socket.socket()
    #host = "127.0.0.1"
    host = "192.168.2.12"
    port = 2005

    try:
        # 连接服务器
        socket_client.connect((host, port))
        # 清除缓存的图像
        clear_cached_images()
        print('等待中...')

        # 载入预训练模型
        model = load_model()

        while True:
            # 从服务器接收数据
            print('视觉等待从plc接收数据')
            data = socket_client.recv(1024).decode('utf-8')
            print(data)

            # 检查接收到的数据是否为'verify'
            if data == 'plc_tx_wz':
                # 从文件读取图像
                src_roi = cv2.imread('D:/VisionMaster/image.jpg')
                # 对图像进行推断
                label, pred_class = model_inference(model, src_roi)
                print(label, pred_class)
                # 在图像上显示结果
                display_result(src_roi, pred_class)

                # 将预测的类别索引映射为类别名称以发送回服务器
                label_map = {0: 'fangbianmian', 1: 'mianbao', 2: 'xiangchang', 3: 'kuangquanshui',4: 'binggan',
                             5: 'pingguo', 6: 'kele', 7: 'xiangjiao'}
                msg = 'tx_plc_wz,'+ label_map.get(label, 'error')
                # 发送结果回服务器
                socket_client.send(msg.encode())
            #else:
            #    # 如果接收到的数据不是'verify'，则发送'kong'回服务器
            #    msg = 'tx_plc_wz,kong'
            #    socket_client.send(msg.encode())
            #    print('数据错误!')
            time.sleep(0.1)

    except Exception as e:
        # 处理任何异常
        print(f"错误：{e}")

    finally:
        # 关闭Socket连接
        socket_client.close()
        print("Socket连接已关闭")

if __name__ == "__main__":
    # 当脚本被执行时调用主函数
    main_function()
