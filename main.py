import requests
import xml.etree.ElementTree as ET

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

# Определяем дизайн приложения через Kivy Language
kv = '''
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 15
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1  # Светлый фон
        Rectangle:
            pos: self.pos
            size: self.size

    # Панель ввода данных
    BoxLayout:
        size_hint_y: None
        height: '50dp'
        spacing: 15
        TextInput:
            id: ticker_input
            hint_text: "Введите тикер облигации"
            multiline: False
            size_hint_x: 0.4
            background_color: (1, 1, 1, 1)
            foreground_color: (0, 0, 0, 1)
            hint_text_color: (0.7, 0.7, 0.7, 1)
        TextInput:
            id: purchase_price_input
            hint_text: "Цена покупки"
            input_filter: 'float'
            multiline: False
            size_hint_x: 0.3
            background_color: (1, 1, 1, 1)
            foreground_color: (0, 0, 0, 1)
            hint_text_color: (0.7, 0.7, 0.7, 1)
        TextInput:
            id: purchase_date_input
            hint_text: "Дата покупки (YYYY-MM-DD)"
            multiline: False
            size_hint_x: 0.3
            background_color: (1, 1, 1, 1)
            foreground_color: (0, 0, 0, 1)
            hint_text_color: (0.7, 0.7, 0.7, 1)

    Button:
        text: "Добавить облигацию"
        size_hint_y: None
        height: '50dp'
        background_color: (0.2, 0.6, 0.8, 1)  # Цвет кнопки
        color: (1, 1, 1, 1)  # Цвет текста
        on_release: app.add_bond()

    Label:
        text: "Список облигаций:"
        size_hint_y: None
        height: '40dp'
        font_size: '18sp'
        bold: True
        color: (0, 0, 0, 1)

    ScrollView:
        BoxLayout:
            id: bonds_list
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: 10

<BondItem>:
    size_hint_y: None
    height: '160dp'
    padding: 10
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1  # Белый фон для элемента
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]  # Закругленные углы
    BoxLayout:
        orientation: 'vertical'
        spacing: 6
        Label:
            text: root.shortname if root.shortname else "Нет данных"
            font_size: '18sp'
            bold: True
            color: (0, 0, 0, 1)
        BoxLayout:
            spacing: 5
            Label:
                text: "Тикер: " + root.ticker
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Цена покупки: " + str(root.purchase_price)
                color: (0.2, 0.2, 0.2, 1)
        BoxLayout:
            spacing: 5
            Label:
                text: "Месячный доход: " + str(round(root.monthly_income, 2))
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Годовой доход: " + str(round(root.annual_income, 2))
                color: (0.2, 0.2, 0.2, 1)
        BoxLayout:
            orientation: 'vertical'
            spacing: 2
            Label:
                text: "Режим торгов (BOARDID): " + root.board_id
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Куп он (%): " + str(root.coupon_percent)
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Купоны (₽): " + str(root.coupon_value)
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "НКД: " + str(root.accrued_interest)
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Цена бумаги (%): " + str(root.last_price)
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Номинал: " + str(root.facevalue)
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Дата погашения: " + root.matdate
                color: (0.2, 0.2, 0.2, 1)
            Label:
                text: "Оферта: " + root.offerdate
                color: (0.2, 0.2, 0.2, 1)
'''

# Виджет для отображения одной облигации с дополнительными данными
class BondItem(BoxLayout):
    ticker = StringProperty('')
    purchase_price = NumericProperty(0)
    purchase_date = StringProperty('')
    shortname = StringProperty('')
    board_id = StringProperty('')
    coupon_percent = NumericProperty(0)
    coupon_value = NumericProperty(0)
    accrued_interest = NumericProperty(0)
    last_price = NumericProperty(0)
    facevalue = NumericProperty(0)
    matdate = StringProperty('')
    offerdate = StringProperty('')
    monthly_income = NumericProperty(0)
    annual_income = NumericProperty(0)

# Функция для получения BOARDID по тикеру (режим торгов)
def get_board_id(ticker):
    url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/securities/{ticker}/securities.xml?iss.meta=off&iss.only=marketdata&marketdata.columns=BOARDID"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            row = root.find(".//row")
            if row is not None:
                board_id = row.attrib.get("BOARDID", "")
                return board_id
    except Exception as e:
        print(f"Ошибка при получении BOARDID: {e}")
    return ""

# Функция для получения данных из блока securities
def get_securities_data(board, ticker):
    url = (f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/{board}/securities/{ticker}/securities.xml"
           "?iss.meta=off&iss.only=securities&securities.columns=SHORTNAME,COUPONPERCENT,COUPONVALUE,ACCRUEDINT,FACEVALUE,MATDATE,OFFERDATE")
    data = {"SHORTNAME": "", "COUPONPERCENT": 0, "COUPONVALUE": 0, "ACCRUEDINT": 0,
            "FACEVALUE": 0, "MATDATE": "", "OFFERDATE": ""}
    try:
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            row = root.find(".//row")
            if row is not None:
                data["SHORTNAME"] = row.attrib.get("SHORTNAME", "")
                try:
                    data["COUPONPERCENT"] = float(row.attrib.get("COUPONPERCENT", 0))
                except:
                    data["COUPONPERCENT"] = 0
                try:
                    data["COUPONVALUE"] = float(row.attrib.get("COUPONVALUE", 0))
                except:
                    data["COUPONVALUE"] = 0
                try:
                    data["ACCRUEDINT"] = float(row.attrib.get("ACCRUEDINT", 0))
                except:
                    data["ACCRUEDINT"] = 0
                try:
                    data["FACEVALUE"] = float(row.attrib.get("FACEVALUE", 0))
                except:
                    data["FACEVALUE"] = 0
                data["MATDATE"] = row.attrib.get("MATDATE", "")
                data["OFFERDATE"] = row.attrib.get("OFFERDATE", "нет оферты")
    except Exception as e:
        print(f"Ошибка при получении securities данных: {e}")
    return data

# Функция для получения рыночной цены (LAST)
def get_marketdata_last(board, ticker):
    url = (f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/{board}/securities/{ticker}/securities.xml"
           "?iss.meta=off&iss.only=marketdata&marketdata.columns=LAST")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            row = root.find(".//row")
            if row is not None:
                try:
                    return float(row.attrib.get("LAST", 0))
                except:
                    return 0
    except Exception as e:
        print(f"Ошибка при получении LAST цены: {e}")
    return 0

# Функция расчёта доходности
def calculate_income(purchase_price, coupon_value, coupon_percent, facevalue):
    # Если задан купон в рублях, используем его;
    # иначе, если есть купон в % и номинал, рассчитываем по ним;
    # в крайнем случае – рассчитываем от цены покупки.
    if coupon_value > 0:
        annual_income = coupon_value
    elif coupon_percent > 0 and facevalue > 0:
        annual_income = facevalue * coupon_percent / 100
    else:
        annual_income = purchase_price * coupon_percent / 100
    monthly_income = annual_income / 12
    return monthly_income, annual_income

class BondsApp(App):
    def build(self):
        self.title = "Отслеживание доходности облигаций"
        self.bonds = []  # Список для хранения облигаций
        self.root = Builder.load_string(kv)
        return self.root

    def add_bond(self):
        # Читаем введённые пользователем данные
        ticker = self.root.ids.ticker_input.text.strip()
        purchase_price_text = self.root.ids.purchase_price_input.text.strip()
        purchase_date = self.root.ids.purchase_date_input.text.strip()
        if not ticker or not purchase_price_text:
            print("Не заполнены обязательные поля: тикер и цена покупки.")
            return
        try:
            purchase_price = float(purchase_price_text)
        except Exception as e:
            print("Неверный формат цены покупки.")
            return

        # Получаем режим торгов (BOARDID) автоматически
        board_id = get_board_id(ticker)
        if not board_id:
            print("Не удалось получить BOARDID для тикера:", ticker)
            return

        # Получаем остальные данные облигации из securities
        securities_data = get_securities_data(board_id, ticker)
        # Получаем рыночную цену бумаги
        last_price = get_marketdata_last(board_id, ticker)

        shortname = securities_data.get("SHORTNAME", ticker)
        coupon_percent = securities_data.get("COUPONPERCENT", 0)
        coupon_value = securities_data.get("COUPONVALUE", 0)
        accrued_interest = securities_data.get("ACCRUEDINT", 0)
        facevalue = securities_data.get("FACEVALUE", 0)
        matdate = securities_data.get("MATDATE", "")
        offerdate = securities_data.get("OFFERDATE", "нет оферты")

        # Рассчитываем доходность
        monthly_income, annual_income = calculate_income(purchase_price, coupon_value, coupon_percent, facevalue)

        # Формируем объект облигации
        bond = {
            'ticker': ticker,
            'purchase_price': purchase_price,
            'purchase_date': purchase_date,
            'shortname': shortname,
            'board_id': board_id,
            'coupon_percent': coupon_percent,
            'coupon_value': coupon_value,
            'accrued_interest': accrued_interest,
            'last_price': last_price,
            'facevalue': facevalue,
            'matdate': matdate,
            'offerdate': offerdate,
            'monthly_income': monthly_income,
            'annual_income': annual_income
        }
        self.bonds.append(bond)
        self.update_bonds_view()

        # Очищаем поля ввода
        self.root.ids.ticker_input.text = ""
        self.root.ids.purchase_price_input.text = ""
        self.root.ids.purchase_date_input.text = ""

    def update_bonds_view(self):
        bonds_list = self.root.ids.bonds_list
        bonds_list.clear_widgets()
        for bond in self.bonds:
            item = BondItem(
                ticker=bond['ticker'],
                purchase_price=bond['purchase_price'],
                purchase_date=bond['purchase_date'],
                shortname=bond['shortname'],
                board_id=bond['board_id'],
                coupon_percent=bond['coupon_percent'],
                coupon_value=bond['coupon_value'],
                accrued_interest=bond['accrued_interest'],
                last_price=bond['last_price'],
                facevalue=bond['facevalue'],
                matdate=bond['matdate'],
                offerdate=bond['offerdate'],
                monthly_income=bond['monthly_income'],
                annual_income=bond['annual_income']
            )
            bonds_list.add_widget(item)

if __name__ == '__main__':
    BondsApp().run()
