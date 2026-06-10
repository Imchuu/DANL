import mysql.connector
import config.config_data_b as db_config

config = db_config.config

conn = None
cursor = None

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)

    # Lấy dữ liệu từ bảng customer
    query = 'SELECT * FROM customers LIMIT 100'
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        for key, value in row.items():
            print(f"{key}: {value}")
        print('-' * 40)

except mysql.connector.Error as err:
    if err.errno == 1146:
        print('Lỗi: bảng customer không tồn tại trong database mkt.')
        if conn is not None and conn.is_connected():
            with conn.cursor() as helper_cursor:
                helper_cursor.execute('SHOW TABLES')
                tables = helper_cursor.fetchall()
                print('Danh sách bảng hiện có:')
                for table in tables:
                    print('-', table[0])
    else:
        print(f'Lỗi khi kết nối MySQL: {err}')

finally:
    if cursor is not None:
        cursor.close()
    if conn is not None and conn.is_connected():
        conn.close()
