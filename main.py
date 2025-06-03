import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os


from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

kv = '''
ScreenManager:
    MainMenu:
    AddBondScreen:
    BondListScreen:

<MainMenu>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Главное меню'
            font_size: '24sp'
            color: (0, 0, 0, 1)
        Button:
            text: 'Добавить облигацию'
            size_hint_y: None
            height: '50dp'
            background_color: (0.2, 0.6, 0.8, 1)
            color: (1, 1, 1, 1)
            on_release: root.manager.current = 'add'
        Button:
            text: 'Список облигаций'
            size_hint_y: None
            height: '50dp'
            background_color: (0.2, 0.6, 0.8, 1)
            color: (1, 1, 1, 1)
            on_release: root.manager.current = 'list'

<AddBondScreen>:
    name: 'add'
    AnchorLayout:
        anchor_y: 'top'
        padding: 20

        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            orientation: 'vertical'
            spacing: 15
            size_hint_y: None
            padding: [0, 40, 0, 0]
            height: self.minimum_height

            BoxLayout:
                size_hint_y: None
                height: '50dp'
                spacing: 15
                TextInput:
                    id: ticker_input
                    hint_text: "Введите тикер облигации"
                    multiline: False
                    size_hint_x: 0.4
                TextInput:
                    id: purchase_price_input
                    hint_text: "Цена покупки"
                    input_filter: 'float'
                    multiline: False
                    size_hint_x: 0.3

            BoxLayout:
                size_hint_y: None
                height: '50dp'
                spacing: 15
                TextInput:
                    id: purchase_date_input
                    hint_text: "Дата покупки (YYYY-MM-DD)"
                    multiline: False
                    size_hint_x: 0.5
                TextInput:
                    id: quantity_input
                    hint_text: "Количество облигаций"
                    input_filter: 'int'
                    multiline: False
                    size_hint_x: 0.5

            Button:
                text: "Добавить облигацию"
                size_hint_y: None
                background_color: (0.2, 0.6, 0.8, 1)
                color: (1, 1, 1, 1)
                height: '50dp'
                on_release:
                    app.add_bond()
                    root.manager.current = 'menu'

            Button:
                text: "Вернуться в меню"
                size_hint_y: None
                height: '50dp'
                on_release: root.manager.current = 'menu'


<BondListScreen>:
    name: 'list'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size

        # 🔽 Новый блок для отображения суммарной доходности
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            Label:
                id: total_monthly
                text: "Суммарный месячный доход: 0"
                color: (0, 0, 0, 1)
            Label:
                id: total_annual
                text: "Суммарный годовой доход: 0"
                color: (0, 0, 0, 1)

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

        Button:
            text: "Вернуться в меню"
            size_hint_y: None
            height: '50dp'
            on_release: root.manager.current = 'menu'

<BondItem>:
    size_hint_y: None
    height: '200dp'
    padding: 10
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
    RelativeLayout:
        BoxLayout:
            orientation: 'vertical'
            spacing: 6
            padding: [0, 10, 0, 0]
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
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'

                Label:
                    text: "Цена покупки: " + str(root.purchase_price)
                    color: (0.2, 0.2, 0.2, 1)
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
            BoxLayout:
                spacing: 5
                Label:
                    text: "Количество: " + str(root.quantity)
                    color: (0.2, 0.2, 0.2, 1)
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                Label:
                    text: "Месячный доход: " + str(round(root.monthly_income, 2))
                    color: (0.2, 0.2, 0.2, 1)
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
            BoxLayout:
                spacing: 5
                Label:
                    text: "Годовой доход: " + str(round(root.annual_income, 2))
                    color: (0.2, 0.2, 0.2, 1)
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                Label:
                    text: "Доходность к погашению: " + str(round(root.ytm, 2)) + "%"
                    color: (0.2, 0.2, 0.2, 1)
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
            Label:
                text: "Дата погашения: " + root.matdate
                color: (0.2, 0.2, 0.2, 1)
                text_size: self.size
                halign: 'left'
                valign: 'middle'

        Button:
            text: "X"
            size_hint: None, None
            size: '28dp', '28dp'
            pos_hint: {'right': 1, 'top': 1}
            background_color: (1, 0.3, 0.3, 1)
            color: (1, 1, 1, 1)
            font_size: '14sp'
            on_release: app.remove_bond(root.ticker, root.purchase_date)

'''

# Определяем экраны
class MainMenu(Screen):
    pass

class AddBondScreen(Screen):
    pass

class BondListScreen(Screen):
    pass

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
    matdate = StringProperty('')    # Дата погашения
    offerdate = StringProperty('')
    monthly_income = NumericProperty(0)
    annual_income = NumericProperty(0)
    quantity = NumericProperty(0)
    ytm = NumericProperty(0)

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

# Функция расчёта доходности (на одну облигацию)
def calculate_income(purchase_price, coupon_value, coupon_percent, facevalue):
    if coupon_value > 0:
        annual_income = coupon_value
    elif coupon_percent > 0 and facevalue > 0:
        annual_income = facevalue * coupon_percent / 100
    else:
        annual_income = purchase_price * coupon_percent / 100
    monthly_income = annual_income / 12
    return monthly_income, annual_income

# Функция расчёта доходности к погашению (YTM) по приблизительной формуле
def calculate_ytm(purchase_price, coupon_value, facevalue, purchase_date, maturity_date):
    try:
        purchase_dt = datetime.strptime(purchase_date, "%Y-%m-%d")
        maturity_dt = datetime.strptime(maturity_date, "%Y-%m-%d")
        years_to_maturity = (maturity_dt - purchase_dt).days / 365.25
        if years_to_maturity <= 0:
            return 0
        # Приблизительная формула YTM:
        ytm = (coupon_value + (facevalue - purchase_price) / years_to_maturity) / ((facevalue + purchase_price) / 2)
        return ytm * 100  # в процентах
    except Exception as e:
        print("Ошибка при расчёте YTM:", e)
        return 0

class BondsApp(App):
    def build(self):
        self.title = "Отслеживание доходности облигаций"
        self.bonds = []
        self.sm = Builder.load_string(kv)
        self.load_bonds()  # загружаем сохранённые облигации
        self.update_bonds_view()  # отображаем их
        return self.sm

    def get_save_file(self):
        return os.path.join(self.user_data_dir, "bonds.json")

    def save_bonds(self):
        try:
            with open(self.get_save_file(), "w", encoding="utf-8") as f:
                json.dump(self.bonds, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Ошибка при сохранении облигаций:", e)

    def load_bonds(self):
        try:
            filepath = self.get_save_file()
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    self.bonds = json.load(f)
        except Exception as e:
            print("Ошибка при загрузке облигаций:", e)


    def add_bond(self):
        screen = self.sm.get_screen('add')
        ticker = screen.ids.ticker_input.text.strip()
        purchase_price_text = screen.ids.purchase_price_input.text.strip()
        purchase_date = screen.ids.purchase_date_input.text.strip()
        quantity_text = screen.ids.quantity_input.text.strip()
        if not ticker or not purchase_price_text or not purchase_date or not quantity_text:
            print("Не заполнены обязательные поля: тикер, цена покупки, дата покупки и количество.")
            return
        try:
            purchase_price = float(purchase_price_text)
            quantity = int(quantity_text)
        except Exception as e:
            print("Неверный формат цены покупки или количества.")
            return

        board_id = get_board_id(ticker)
        if not board_id:
            print("Не удалось получить BOARDID для тикера:", ticker)
            return

        securities_data = get_securities_data(board_id, ticker)
        last_price = get_marketdata_last(board_id, ticker)

        shortname = securities_data.get("SHORTNAME", ticker)
        coupon_percent = securities_data.get("COUPONPERCENT", 0)
        coupon_value = securities_data.get("COUPONVALUE", 0)
        accrued_interest = securities_data.get("ACCRUEDINT", 0)
        facevalue = securities_data.get("FACEVALUE", 0)
        matdate = securities_data.get("MATDATE", "")  # Дата погашения
        offerdate = securities_data.get("OFFERDATE", "нет оферты")

        # Расчёт доходности для одной облигации
        monthly_income, annual_income = calculate_income(purchase_price, coupon_value, coupon_percent, facevalue)
        # Итоговый доход с учётом количества облигаций
        total_monthly_income = monthly_income * quantity
        total_annual_income = annual_income * quantity

        # Расчёт доходности к погашению (если задана дата погашения)
        ytm = calculate_ytm(purchase_price, coupon_value, facevalue, purchase_date, matdate) if matdate else 0

        bond = {
            'ticker': ticker,
            'purchase_price': purchase_price,
            'purchase_date': purchase_date,
            'quantity': quantity,
            'shortname': shortname,
            'board_id': board_id,
            'coupon_percent': coupon_percent,
            'coupon_value': coupon_value,
            'accrued_interest': accrued_interest,
            'last_price': last_price,
            'facevalue': facevalue,
            'matdate': matdate,
            'offerdate': offerdate,
            'monthly_income': total_monthly_income,
            'annual_income': total_annual_income,
            'ytm': ytm
        }
        self.bonds.append(bond)
        self.update_bonds_view()
        self.save_bonds()

        screen.ids.ticker_input.text = ""
        screen.ids.purchase_price_input.text = ""
        screen.ids.purchase_date_input.text = ""
        screen.ids.quantity_input.text = ""

    def update_bonds_view(self):
        bonds_list = self.sm.get_screen('list').ids.bonds_list
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
                annual_income=bond['annual_income'],
                quantity=bond['quantity'],
                ytm=bond['ytm']
            )
            bonds_list.add_widget(item)

    def remove_bond(self, ticker, purchase_date):
        # Удалим облигацию из списка
        self.bonds = [b for b in self.bonds if not (b['ticker'] == ticker and b['purchase_date'] == purchase_date)]
        self.save_bonds()
        self.update_bonds_view()


if __name__ == '__main__':
    BondsApp().run()
