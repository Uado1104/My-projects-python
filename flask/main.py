# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
import json

'''
接口需求：
实现对设备单位时间处理水量的统计，原始数据见附件一（由于开通数据库rds服务需要付费，鉴于数据量不大，可以考虑以json格式写死在代码中）
需要根据起始时间与结束时间，按照日或月的颗粒度统计处理水量（每日处理水量或每月处理水量），其中表格中原有数据为累计流量，
其中：单位时间处理水量 = 当前累计流量 – 上一个时间点累计流量。
入参：
设备id（如数值为0则返回全部设备）、起始时间（月-日的格式，文本，如12-01）、结束时间、时间颗粒度（日或月）
出参：
json格式，内容见下demo
[
    {
    "DeviceID":"LvXin_YT_001",
    "Date":"11-08",
    "value":0,
    "Column":"处理水量",
    "DateFormat":"日"
    }
]
'''

app = Flask(__name__)
@app.route('/main', methods=['POST'])

def main():

    # 数据处理函数
    def process(deviceID, startDate, endDate, dateFormat):
            # 预处理数据
        if dateFormat == '日':
            dateFormat = 'day'
        elif dateFormat == '月':
            dateFormat = 'month'
        else:
            print('None dateFormat')
        # 提取开始的月份和日子
        start_month = int(startDate.split('-')[0])
        start_day = int(startDate.split('-')[1])
        end_month = int(endDate.split('-')[0])
        end_day = int(endDate.split('-')[1])
        # 预处理1月份
        if start_month == 1:
            start_month = 13
        elif start_month == 12 or start_month == 13:
            pass
        else:
            print("None date")
        if end_month == 1:
            end_month = 13
        elif end_month == 12 or end_month == 13:
            pass
        else:
            print("None date")

        # 将数据从json格式转为列表
        try:
            data_json = open("./data.json").read()
            data_list = json.loads(data_json)
        except IOError:
            print("Error: 没有找到文件或读取文件失败")

        # 初始化数据列表
        data = []

        # 判断设备，从数据列表中提取相应的数据映射在排序好的列表中。
        if deviceID == 'A001':
            # 将设备A001的数据存入列表
            for i in range(0, 17):
                data.append(0)
            for i in range(0, 59):
                data.append(int(data_list[i]['累计流量']))
            value_monthly = [data[30] - data[17], data[61] - data[31], data[75] - data[62]]
        elif deviceID == 'A002':
            # 将设备A002的数据存入列表
            for i in range(0, 17):
                data.append(0)
            for i in range(59, 118):
                data.append(int(data_list[i]['累计流量']))
            value_monthly = (data[30] - data[17], data[61] - data[31], data[75] - data[62])
        else:
            print('None Devices')

        # 初始化输出的列表
        output_list = []
        # 传出参数函数
        def output(device_ID, date, value, date_format):
            dir = {}
            dir["DeviceID"] = device_ID
            dir["Date"] = date
            dir["value"] = value
            dir["Column"] = "处理水量"
            if date_format == 'day':
                dir["DateFormat"] = "日"
            else:
                dir["DateFormat"] = "月"
            return dir

        # 根据时间颗粒度选取相应计算函数
        def locate(monthly, dayly):
            if monthly == 11:
                location = (monthly - 11) * 30 + dayly - 1
            elif monthly == 12 or monthly == 13:
                location = (monthly - 11) * 30 + dayly
            else:
                print('None date')
            return location

        # 日颗粒度的计算函数
        if dateFormat == 'day':
            location_start = locate(start_month, start_day)
            location_end = locate(end_month, end_day)
            i = location_start
            while i <= location_end:
                if i < 31:
                    month = 11
                    day = i + 1
                elif i < 61:
                    month = 12
                    day = i - 30
                else:
                    month = 1
                    day = i - 60
                date_current = str(month) + '-' + str(day)
                val = data[i] - data[i - 1]
                output_list.append(output(deviceID, date_current, val, dateFormat))
                i = i + 1

        # 月颗粒度的计算函数
        elif dateFormat == 'month':
            i = start_month
            while i < (end_month+ 1):
                if i < 13:
                    date_current = str(i) + '-01'
                else:
                    date_current = str(i-12) + '-01'
                val = value_monthly[i-11]
                output_list.append(output(deviceID, date_current, val, dateFormat))
                i = i + 1
        else:
            print('None dateFormat')

        return output_list

    # 入参
    deviceID_input = request.form.get('设备id')
    startDate_input = request.form.get('起始时间')
    endDate_input = request.form.get('结束时间')
    dateFormat_input = request.form.get('时间颗粒度')
    
    # 根据设备ID选用合适的处理函数
    if deviceID_input == 'A001' or deviceID_input == 'A002':
        output_list = process(deviceID_input, startDate_input, endDate_input, dateFormat_input)
    elif deviceID_input == '0':
        output_list = process('A001', startDate_input, endDate_input, dateFormat_input) + process('A002', startDate_input, endDate_input, dateFormat_input)
    else:
        print('None Device')

    # 出参
    out = json.dumps(output_list)
    return out

# main程序入口
if __name__ == '__main__':
    app.run()
    

