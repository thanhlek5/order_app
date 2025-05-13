import pyodbc
from datetime import date
# Cấu hình kết nối SQL Server
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                    'Server=legion5-thanhle;'
                    'Database=ban_nuoc;'
                    'UID=thanh;'
                    'PWD=1;'
                    )

cursor = conn.cursor()

# --- In Danh Sách Món ---
def InNguyenLieu():
    cursor.execute("SELECT * FROM NGUYENLIEU_TONKHO")
    return cursor.fetchall()

# # --- Tìm Kiếm Nguyên Liệu ---
# def tim_kiem_nguyen_lieu(cursor, TEN_NGUYENLIEU):
#     cursor.execute("SELECT * FROM NGUYENLIEU_TONKHO WHERE TEN_NGUYENLIEU LIKE ?", ('%' + TEN_NGUYENLIEU + '%',))
#     return cursor.fetchall()


# --- Xoá Nguyên Liệu ---
def xoa_nguyenlieu( ID_NGUYENLIEU):
    cursor.execute("DELETE FROM NGUYENLIEU_TONKHO WHERE ID_NGUYENLIEU = ?", (ID_NGUYENLIEU))
    conn.commit()
    print("Đã xóa nguyên liệu.")


# --- Thêm Nguyên Liệu Database ---
def add_NguyenLieu(TEN_NGUYENLIEU, DON_VI_TINH, NGAY_CAPNHAT, GHI_CHU):
    if conn and cursor:
        query = '''
            INSERT INTO NGUYENLIEU_TONKHO (TEN_NGUYENLIEU, DON_VI_TINH, NGAY_CAPNHAT, GHI_CHU)
            VALUES (?, ?, ?, ?)
        '''
        try:
            cursor.execute(query, (TEN_NGUYENLIEU, DON_VI_TINH, NGAY_CAPNHAT, GHI_CHU))
            conn.commit()
            print("Đã thêm '{TEN_NGUYENLIEU}' thành công!")
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print("Lỗi khi thêm '{TEN_NGUYENLIEU}' : {sqlstate}")
    else:
        print("Không có kết nối cơ sở dữ liệu để thêm nguyên liệu.")


# --- Cập Nhật Số Lượng Tồn Kho ---
def cap_nhat_ton_kho( ID_NGUYENLIEU, so_luong_thay_doi):
    if cursor and conn:
        try:
            # Lấy số lượng tồn kho hiện tại
            cursor.execute("SELECT SO_LUONG_TON FROM NGUYENLIEU_TONKHO WHERE ID_NGUYENLIEU = ?", (ID_NGUYENLIEU,))
            result = cursor.fetchone()

            if result:
                so_luong_hien_tai = result[0]
                so_luong_moi = so_luong_hien_tai + so_luong_thay_doi # so_luong_thay_doi có thể âm (giảm) hoặc dương (tăng)

                if so_luong_moi >= 0:
                    # Cập nhật số lượng tồn kho mới
                    cursor.execute("UPDATE NGUYENLIEU_TONKHO SET SO_LUONG_TON = ?, NGAY_CAPNHAT = ? WHERE ID_NGUYENLIEU = ?",
                                   (so_luong_moi, date.today(), ID_NGUYENLIEU))
                    conn.commit()
                    print(f"Đã cập nhật tồn kho cho ID = {ID_NGUYENLIEU}. Thay đổi: {so_luong_thay_doi}, Tồn kho mới: {so_luong_moi}")
                else:
                    print(f"Không đủ tồn kho cho ID = {ID_NGUYENLIEU} để giảm {abs(so_luong_thay_doi)}. Hiện có: {so_luong_hien_tai}")
            else:
                print(f"Không tìm thấy nguyên liệu có ID = {ID_NGUYENLIEU}.")

        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Lỗi khi cập nhật tồn kho cho ID = {ID_NGUYENLIEU}: {sqlstate}")
    else:
        print("Không có kết nối cơ sở dữ liệu để cập nhật tồn kho.")



