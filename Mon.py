import pyodbc

# Cấu hình kết nối SQL Server
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                    'Server=legion5-thanhle;'
                    'Database=ban_nuoc;'
                    'UID=thanh;'
                    'PWD=1;')

cursor = conn.cursor()

# --- Thêm Món Vào Database ---
def create_mon(ten_mon, don_gia, mo_ta, loai):
    query = '''
        INSERT INTO MON (TEN_MON, DON_GIA, MO_TA, LOAI)
        VALUES (?, ?, ?, ?)
    '''
    cursor.execute(query, (ten_mon, don_gia, mo_ta, loai))
    conn.commit()
    print("Đã thêm món thành công!")

# --- In Danh Sách Món ---
def read_all_mon():
    cursor.execute("SELECT * FROM MON")
    return cursor.fetchall()

# --- Tìm Kiếm Món ---
def tim_kiem_mon(cursor, Ten_Mon):
    cursor.execute("SELECT * FROM Mon WHERE Ten_Mon LIKE ?", ('%' + Ten_Mon + '%',))
    return cursor.fetchall()

# --- Xoá Món ---
def delete_mon(id_mon):
    cursor.execute("DELETE FROM MON WHERE ID_MON = ?", (id_mon,))
    conn.commit()
    print("Đã xóa món.")

