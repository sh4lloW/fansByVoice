import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import speech

COM_PORT = "com3" # USB-串口端口，需要在设备管理器中手动查看并修改

def ConnectRelay(PORT):
    """
    此函数为连接串口继电器模块，为初始函数，必须先调用
    :param PORT: USB-串口端口，需要手动填写，须在计算机中手动查看对应端口
    :return: >0 连接成功，<0 连接超时
    """
    try:
        # c2s03设备默认波特率9600、偶校验、停止位1
        master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,
                                                    baudrate=9600, bytesize=8, parity='E', stopbits=1))
        master.set_timeout(5.0)
        master.set_verbose(True)

        # 读输入寄存器
        # c2s03设备默认slave=2, 起始地址=0, 输入寄存器个数2
        master.execute(2, cst.READ_INPUT_REGISTERS, 0, 2)

        # 读保持寄存器
        # c2s03设备默认slave=2, 起始地址=0, 保持寄存器个数1
        master.execute(2, cst.READ_HOLDING_REGISTERS, 0, 1)  # 这里可以修改需要读取的功能码

        # 没有报错，返回1
        response_code = 1

    except Exception as exc:
        print(str(exc))
        # 报错，返回<0并输出错误
        response_code = -1
        master = None

    return response_code, master

def Switch(master, ACTION):
    """
    此函数为控制继电器开合函数，如果ACTION=ON则闭合，如果如果ACTION=OFF则断开。
    :param master: 485主机对象，由ConnectRelay产生
    :param ACTION: ON继电器闭合，开启风扇；OFF继电器断开，关闭风扇。
    :return: >0 操作成功，<0 操作失败
    """
    try:

        if "on" in ACTION.lower():
            # 写单个线圈，状态常量为0xFF00，请求线圈接通
            # c2s03设备默认slave=2, 线圈地址=0, 请求线圈接通即output_value不等于0
            master.execute(2, cst.WRITE_SINGLE_COIL, 0, output_value=1)

        else:
            # 写单个线圈，状态常量为0x0000，请求线圈断开
            # c2s03设备默认slave=2, 线圈地址=0, 请求线圈断开即output_value等于0
            master.execute(2, cst.WRITE_SINGLE_COIL, 0, output_value=0)

        # 没有报错，返回1
        response_code = 1

    except Exception as exc:
        print(str(exc))
        # 报错，返回<0并输出错误
        response_code = -1

    return response_code

if __name__ == '__main__':
    # 先检查串口继电器是否连接成功
    response_code, master = ConnectRelay(COM_PORT)
    if response_code > 0:
        print("串口继电器模块连接成功！")
    else:
        print("串口继电器模块连接失败，请排查原因！")
        exit()
    while True:
        words = speech.input()
        print("你的命令是：" + words)
        if "电风扇" in words and "开" in words:
            Switch(master, "on")
            if response_code > 0:
                print("电风扇开启成功！")
                speech.say("电风扇开启成功！")
            else:
                print("电风扇开启失败，请检查USB串口连接！")
                speech.say("电风扇开启失败，请检查USB/串口连接！")
                exit()

        if "电风扇" in words and "关" in words:
            Switch(master, "off")
            if response_code > 0:
                print("电风扇关闭成功！")
                speech.say("电风扇关闭成功！")
            else:
                print("电风扇关闭失败，请检查USB串口连接！")
                speech.say("电风扇关闭失败，请检查USB/串口连接！")
                exit()