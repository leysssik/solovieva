from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

# Использовать конфигурацию через объект, а не глобальную переменную
app.config['DB_PATH'] = os.environ.get('DB_PATH', 'products.db')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

@app.route('/search', methods=['GET'])          # ← явно указан метод
def search_products():
    search_term = request.args.get('q', '')

    # Используем параметризованный запрос для защиты от SQL-инъекции
    query = "SELECT * FROM products WHERE name LIKE ?"
    try:
        with sqlite3.connect(app.config['DB_PATH']) as conn:   # менеджер контекста закроет соединение автоматически
            cursor = conn.cursor()
            cursor.execute(query, (f'%{search_term}%',))
            results = cursor.fetchall()
        return str(results)
    except Exception as e:
        # Логируем ошибку, не показывая детали пользователю
        app.logger.error(f"Database error: {e}")
        return "Internal error", 500

def calculate_price(items):
    total = 0
    discount = 0.1

    for item in items:
        price = item.get('price')      # безопасное получение значения
        if price is not None:
            try:
                if price > 100:
                    total += price * (1 - discount)
                else:
                    total += price
            except TypeError:
                # На случай, если price — не число
                app.logger.warning(f"Invalid price: {price}")
                continue
        else:
            # Просто пропускаем товары без цены
            pass

    # Неиспользуемая переменная УДАЛЕНА
    return total

@app.route('/config', methods=['GET'])   # ← явно указан метод
def show_config():
    # Возвращаем только обезличенную информацию, без секретов
    return {"status": "configured", "db_used": bool(app.config['DB_PATH'])}, 200

if __name__ == '__main__':
    # debug берётся из конфигурации, а не хардкодится
    app.run(debug=app.config['DEBUG'])