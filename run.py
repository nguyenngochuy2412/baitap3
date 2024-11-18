from flask import Flask, render_template, request, jsonify, render_template_string, session, redirect, url_for
from sqlalchemy import create_engine, inspect, MetaData, Table, text, insert, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#  hiển thị nếu đã đăng nhập
@app.route('/')
def index():
    if not session.get("logged_in"):  
        return redirect(url_for('login'))  # Chuyển hướng tới trang đăng nhập 
    
    # Lấy thông tin đăng nhập từ session
    username = session.get('username')
    password = session.get('password')
    host = session.get('host', 'localhost')
    port = session.get('port', 5432)

    # Tạo engine và kết nối với cơ sở dữ liệu
    engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}')
    try:
        with engine.connect() as connection:
            # Lấy danh sách các cơ sở dữ liệu (trừ các database template)
            databases = connection.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
            database_list = [db[0] for db in databases]
    except SQLAlchemyError as e:
        return jsonify({"message": "Lỗi khi truy xuất cơ sở dữ liệu: " + str(e)}), 500
    
    return render_template('index.html', databases=database_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data['username']
        password = data['password']
        host = data.get('host', 'localhost')
        port = data.get('port', 5432)

        try:
            # Tạo kết nối với cơ sở dữ liệu
            db_url = f"postgresql://{username}:{password}@{host}:{port}"
            engine = create_engine(db_url)
            # Test kết nối
            connection = engine.connect()
            connection.close()

            # Lưu thông tin đăng nhập vào session
            session['username'] = username
            session['password'] = password
            session['host'] = host
            session['port'] = port
            session['logged_in'] = True
            return jsonify({"message": "Kết nối thành công!"})
        
        except SQLAlchemyError as e:
            return jsonify({"message": "Kết nối thất bại: " + str(e)}), 500
    else:
        # Trả về trang đăng nhập nếu phương thức là GET
        return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Xóa toàn bộ dữ liệu trong session
    return jsonify({"message": "Đã đăng xuất thành công", "redirect_url": url_for('login')})

# Cấu hình kết nối cơ sở dữ liệu
def get_engine(database_name):
    # Lấy thông tin đăng nhập từ session
    username = session.get('username')
    password = session.get('password')
    host = session.get('host', 'localhost')  # Giá trị mặc định nếu không có trong session
    port = session.get('port', 5432)  # Giá trị mặc định nếu không có trong session

    # Kiểm tra xem các giá trị có tồn tại trong session không
    if not all([username, password, host, port]):
        raise ValueError("Thông tin đăng nhập không hợp lệ hoặc không đầy đủ trong session.")

    # Tạo kết nối đến cơ sở dữ liệu
    engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}')
    return engine

# Route lấy danh sách bảng của một database
@app.route('/get_tables/<database_name>')
def get_tables(database_name):
    engine = get_engine(database_name)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return jsonify(tables)

# Route lấy nội dung bảng
@app.route('/database/<database_name>/table/<table_name>')
def show_table_data(database_name, table_name):
    engine = get_engine(database_name)
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    
    with engine.connect() as connection:
        query = table.select()
        result = connection.execute(query)
        data = result.fetchall()
        column_names = result.keys()
    
    # Render một phần HTML với dữ liệu bảng
    return render_template('table_data_partial.html', columns=column_names, data=data, table_name=table_name, database_name=database_name)

# Định nghĩa route để thực hiện truy vấn SQL
@app.route('/database/<database_name>/execute_query', methods=['POST'])
def execute_query(database_name):
    data = request.get_json()
    query = data.get('query')

    try:
        engine = get_engine(database_name)
        with engine.connect() as connection:
            result = connection.execute(text(query))
            
            # Đảm bảo commit nếu lệnh INSERT, UPDATE hoặc DELETE
            if query.strip().lower().startswith(("insert", "update", "delete")):
                connection.commit()  # Commit thay đổi
                rowcount = result.rowcount
                if rowcount > 0:
                    message = f"Query executed successfully. Rows affected: {rowcount}"
                else:
                    message = "Query executed successfully, but no rows were affected."
                return jsonify({"success": True, "message": message})

            rows = result.fetchall()
            columns = result.keys()
            result_html = render_template('query_result.html', columns=columns, data=rows)
            
            return jsonify({"success": True, "result": result_html})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/database/<database_name>/table/<table_name>/submit', methods=['POST'])
def add_row(database_name, table_name):
    data = request.json
    
    engine = get_engine(database_name)
    metadata = MetaData()
    print(data, database_name, table_name)
    
    try:
        table = Table(table_name, metadata, autoload_with=engine)

        columns = table.columns
        for column in columns:
            if column.autoincrement:  # Kiểm tra xem cột có phải là auto-increment không
                if column.name in data:
                    del data[column.name]  # Xóa cột auto-increment khỏi dữ liệu
        
        # Thêm dữ liệu vào bảng
        with engine.connect() as connection:
            stmt = insert(table).values(data)
            result = connection.execute(stmt)  # Thực thi câu lệnh và lưu kết quả
            print(f"Rows inserted: {result.rowcount}")  # In số dòng đã được thêm vào
            connection.commit()

        return jsonify({"status": "success", "message": "Row added successfully"})
    except SQLAlchemyError as e:
        print('failed')
        print(e)
        return jsonify({"success": False, "error": str(e)})
    
@app.route('/database/<database_name>/table/<table_name>/update', methods=['POST'])
def update_row(database_name, table_name):
    data = request.json
    form_data = data.get('formData')  # Lấy form data
    column_data = data.get('columnData')  # Lấy column data

    engine = get_engine(database_name)
    metadata = MetaData()

    try:
        table = Table(table_name, metadata, autoload_with=engine)

        columns = table.columns
        # Duyệt qua các cột và loại bỏ cột auto-increment
        for column in columns:
            if column.autoincrement:  # Kiểm tra xem cột có phải là auto-increment không
                if column.name in form_data:  # Kiểm tra nếu cột có trong formData
                    del form_data[column.name]  # Xóa cột auto-increment khỏi form_data
        
        # Trích xuất tên cột và giá trị để làm điều kiện WHERE
        column_name = column_data[0]['columnName'] #tên cột
        column_value = column_data[0]['value']  #giá trị (id hoặc cột có thuộc khóa chính)

        # Tạo câu lệnh UPDATE
        with engine.connect() as connection:
            with connection.begin():  # Bắt đầu giao dịch
                update_stmt = update(table).where(table.c[column_name] == column_value).values(form_data)
                result = connection.execute(update_stmt)
                print(f"Rows updated: {result.rowcount}")  # In số dòng đã được cập nhật

        return jsonify({"status": "success", "message": "Row updated successfully"})
    except SQLAlchemyError as e:
        print('Failed to update row')
        print(e)
        return jsonify({"success": False, "error": str(e)})
        
@app.route('/database/<database_name>/table/<table_name>/delete', methods=['POST'])
def delete_row(database_name, table_name):
    data = request.json  # Ví dụ data = [{'columnName': 'user_id', 'value': '1'}]

    # Lấy phần tử đầu tiên trong danh sách để truy cập cột và giá trị
    row_data = data[0] if data else {}  # Kiểm tra nếu data không rỗng
    column_name = row_data.get("columnName")
    row_value = row_data.get("value")

    engine = get_engine(database_name)
    metadata = MetaData()

    try:
        table = Table(table_name, metadata, autoload_with=engine)

        # Thực thi câu lệnh xóa
        with engine.connect() as connection:
            with connection.begin():  # Bắt đầu giao dịch
                # Tạo câu lệnh delete với tên cột và giá trị động
                delete_stmt = delete(table).where(table.c[column_name] == row_value)
                result = connection.execute(delete_stmt)
                print(f"Rows deleted: {result.rowcount}")  # In số dòng đã được xóa

        return jsonify({"status": "success", "message": "Row deleted successfully"})
    except SQLAlchemyError as e:
        print('Failed to delete row')
        print(e)
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
