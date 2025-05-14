import pyodbc 
import matplotlib.pyplot as plt  
import seaborn as sns 
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
import pyodbc

conn_str = (
    r'Driver={ODBC Driver 17 for SQL Server};'
    r'Server=legion5-thanhle;'
    r'Database=ban_nuoc;'
    r'UID=thanh;'
    r'PWD=1;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()



# các hàm để biến đổi
def get_year(date):     # hàm lấy tháng
    return date.year


def get_month(date):    # hàm lấy năm
    return date.month




# các hàm cho doanh thu
def get_doanhthu():   # hàm lấy dữ liệu từ DB
    cursor.execute("SELECT ID_HOADON,NGAY_HOADON, TONGTIEN, HINH_THUC_TT FROM dbo.HOA_DON")
    doanh_thu = cursor.fetchall()
    list_doanh_thu = {}
    for income in doanh_thu:
        list_doanh_thu[income[0]] = {
            "tongtien" : income[2],
            'hinh_thuc_tt' : income[3],
            'thang_hoadon' : get_month(income[1]),
            'nam_hoadon' : get_year(income[1])
            }
    return list_doanh_thu

    # tham số doanh thu 
list_doanhthu = get_doanhthu()

# tính tổng doanh thu
def tong_all_doanhthu():    # hàm tính tổng doanh thu 
    total = 0 
    for  name_value in list_doanhthu.values():
        total += name_value['tongtien']
    return total


def tong_thang_doanhthu(month):     # hàm tổng doanh thu tháng
    
    total = 0 
    for name_value  in list_doanhthu.values():
        if name_value['thang_hoadon'] == month:
            total += name_value['tongtien']
    return total

def tong_nam_doanhthu(year):    # hàm tổng doanh thu nămnăm
    total = 0 
    for name_value  in list_doanhthu.values():
        if name_value['nam_hoadon'] == year:
            total += name_value['tongtien']
    return total

#  tính trung bình doanh thu 
def avg_doanhthu():
    total = tong_all_doanhthu()
    sl = len(list_doanhthu)
    
    if sl > 0 :
        return  total / sl 
    else:
        return 0 

def avg_thang(thang):
    
    ls_thang = []
    for name_value in list_doanhthu.values():
        if name_value['thang_hoadon'] == thang:
            ls_thang.append(name_value['tongtien'])
    tong_thang = sum(ls_thang)
    sl = len(ls_thang)
    return tong_thang / sl

def avg_nam(nam):
    
    ls_nam = []
    for name_value in list_doanhthu.values():
        if name_value['nam_hoadon'] == nam:
            ls_nam.append(name_value['tongtien'])
    tong_nam = sum(ls_nam)
    sl = len(ls_nam)
    return tong_nam / sl
