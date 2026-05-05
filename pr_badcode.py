from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

# Глобальная переменная - плохая практика
db_path = None

@app.route('/search')
def search_products():
    # УЯЗВИМОСТЬ: SQL-инъекция
    search_term = request.args.get('q', '')
    
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # Критическая уязвимость!
    query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%'"
    cursor.execute(query)
    
    results = cursor.fetchall()
    
    # Не закрыто соединение!
    # conn.close() - забыли
    
    return str(results)

def calculate_price(items):
    total = 0
    discount = 0.1
    
    # Слишком сложная логика
    for item in items:
        if item.get('price'):
            price = item['price']
            if price > 100:
                total += price * (1 - discount)
            else:
                total += price
        else:
            # Потенциальный KeyError
            pass
    
    # Неиспользуемая переменная
    unused_list = [1, 2, 3]
    
    return total

# Потенциальная утечка чувствительной информации
@app.route('/config')
def show_config():
    return f"Database path: {db_path}, Secret key: {os.environ.get('SECRET_KEY')}"

if __name__ == '__main__':
    app.run(debug=True)  # debug=True в продакшене!
