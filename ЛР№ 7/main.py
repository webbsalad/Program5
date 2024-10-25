from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
from abc import ABC, abstractmethod
import requests
import time
import uuid
from threading import Thread
from xml.etree import ElementTree as ET

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# URL для API Центробанка России
API_URL = "https://www.cbr.ru/scripts/XML_daily.asp"

class Subject(ABC):
    """Интерфейс Издателя для управления наблюдателями."""
    
    @abstractmethod
    def attach(self, observer):
        """Присоединяет наблюдателя."""
        pass

    @abstractmethod
    def detach(self, observer):
        """Отсоединяет наблюдателя."""
        pass

    @abstractmethod
    def notify(self):
        """Уведомляет всех наблюдателей."""
        pass

class ConcreteSubject(Subject):
    """Реализация Издателя, которая получает курсы валют."""
    
    def __init__(self):
        self._observers = []
        self._rate_data = {}
    
    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        """Уведомляет всех наблюдателей о новых данных."""
        for observer in self._observers:
            observer.update(self._rate_data)

    def fetch_rates(self):
        """Запрашивает курсы валют из API и уведомляет наблюдателей."""
        while True:
            response = requests.get(API_URL)
            if response.status_code == 200:
                # Обработка XML
                root = ET.fromstring(response.content)
                rates = {}
                for child in root.findall('Valute'):
                    code = child.find('CharCode').text
                    name = child.find('Name').text
                    value = child.find('Value').text
                    rates[code] = {'name': name, 'value': value}
                self._rate_data = rates  # Сохраняем курсы валют
                self.notify()  # Уведомляем наблюдателей о новых данных
            time.sleep(10)  # Запрашиваем курсы каждые 10 секунд

class Observer(ABC):
    """Интерфейс для наблюдателей, которые получают обновления."""
    
    @abstractmethod
    def update(self, data):
        """Получить обновление от субъекта."""
        pass

class CurrencyObserver(Observer):
    """Конкретный наблюдатель, который получает обновления о курсах валют."""
    
    def __init__(self, socket):
        self.socket = socket

    def update(self, data):
        """Отправляет обновленные данные клиенту."""
        self.socket.emit('currency_update', data)


# HTML страничка, для вывода данных клиенту
@app.route('/')
def index():
    client_id = str(uuid.uuid4())  # Генерирует ID клиента
    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Курсы валют</title>
            <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
            <script type="text/javascript">
                var socket = io();
                var clientId = "{{ client_id }}";  // Получаем идентификатор клиента
                document.addEventListener("DOMContentLoaded", function() {
                    document.getElementById('client-id').innerHTML = 'Client ID: ' + clientId;
                });
                socket.on('currency_update', function(data) {
                    let output = '';
                    for (const [code, info] of Object.entries(data)) {
                        output += `<p>${code}: ${info.name} - ${info.value}</p>`;
                    }
                    document.getElementById('data').innerHTML = output;
                });
            </script>
        </head>
        <body>
            <h1>Курсы обмена валют</h1>
            <div id="client-id"></div>  <!-- Здесь ОБЯЗАН отобразится идентификатор клиента -->
            <div id="data">Ожидание обновлений...</div>
        </body>
    </html>
    ''', client_id=client_id)

def start_fetching_rates(subject):
    """Запускает процесс получения курсов валют в отдельном потоке."""
    subject.fetch_rates()

if __name__ == "__main__":
    subject = ConcreteSubject()
    currency_observer = CurrencyObserver(socketio)
    subject.attach(currency_observer)

    # Запускаем поток для получения курсов валют
    Thread(target=start_fetching_rates, args=(subject,), daemon=True).start()
    socketio.run(app, debug=True)
