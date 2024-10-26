from flask import Flask, render_template, request, redirect, url_for
from config import get_db_connection  # Import hàm kết nối từ config.py
from datetime import date

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Route trang chủ
@app.route('/')
def index():
    return render_template('index.html')

# Route để thêm sách và thành viên
@app.route('/add_data', methods=['GET', 'POST'])  
def add_data():  
    if request.method == 'POST':  
        # Thêm sách  
        book_title = request.form.get('book_title')  
        book_author = request.form.get('book_author')  
        
        # Kết nối đến cơ sở dữ liệu và thực hiện truy vấn  
        connection = get_db_connection()  
        cursor = connection.cursor()  
        
        # Thêm sách  
        cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (book_title, book_author))  
        book_id = cursor.lastrowid  # Lấy ID của sách vừa thêm  
        
        # Thêm thành viên  
        member_name = request.form.get('member_name')  
        member_dob = request.form.get('member_dob')  
        member_address = request.form.get('member_address')  
        cursor.execute("INSERT INTO members (name, dob, address) VALUES (%s, %s, %s)",   
                       (member_name, member_dob, member_address))  
        member_id = cursor.lastrowid  # Lấy ID của thành viên vừa thêm  
        
        # Thêm giao dịch mượn vào borrow_transactions  
        borrow_date = date.today()  
        return_status = False  # Trạng thái mặc định là chưa trả sách  
        cursor.execute("INSERT INTO borrow_transactions (member_id, book_id, borrow_date, return_status) VALUES (%s, %s, %s, %s)",   
                       (member_id, book_id, borrow_date, return_status))  
        
        # Lưu thay đổi và đóng kết nối  
        connection.commit()  
        cursor.close()  
        connection.close()  
        
        return redirect(url_for('index'))  
    
    return render_template('add_data.html')

# Route để tạo báo cáo
@app.route('/report')
def report():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT borrow_transactions.id AS transaction_id, members.name, members.dob, members.address, 
               books.title AS book_title, borrow_transactions.borrow_date, 
               CASE WHEN borrow_transactions.return_status = TRUE THEN 'Đã trả' ELSE 'Đang mượn' END AS status
        FROM borrow_transactions
        JOIN members ON borrow_transactions.member_id = members.id
        JOIN books ON borrow_transactions.book_id = books.id
    """)
    transactions = cursor.fetchall()
    
    # Đóng kết nối
    cursor.close()
    connection.close()
    
    return render_template('report.html', transactions=transactions)

# Route để mượn sách
@app.route('/borrow', methods=['POST'])
def borrow_book():
    member_id = request.form.get('member_id')
    book_id = request.form.get('book_id')
    borrow_date = date.today()
    return_status = False
    
    # Kết nối đến cơ sở dữ liệu và thực hiện truy vấn
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO borrow_transactions (member_id, book_id, borrow_date, return_status) VALUES (%s, %s, %s, %s)", 
                   (member_id, book_id, borrow_date, return_status))
    
    # Lưu thay đổi và đóng kết nối
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('index'))

# Route để trả sách
@app.route('/return_book/<int:transaction_id>', methods=['POST'])
def return_book(transaction_id):
    # Kết nối đến cơ sở dữ liệu và cập nhật trạng thái trả sách
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE borrow_transactions SET return_status = TRUE WHERE id = %s", (transaction_id,))
    
    # Lưu thay đổi và đóng kết nối
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('report'))

if __name__ == '__main__':
    app.run(debug=True)