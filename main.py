import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, ListProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

kv = '''
ScreenManager:
    MainMenu:
    AddBondScreen:
    BondListScreen:
    SettingsScreen:
    BondMarketScreen:

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        canvas.before:
            Color:
                rgba: app.bg_color
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Настройки"
            font_size: '24sp'
            color: app.text_color

        BoxLayout:
            spacing: 10
            size_hint_y: None
            height: '50dp'
            Label:
                text: "Тёмная тема"
                color: app.text_color
            Switch:
                id: theme_switch
                active: app.dark_theme
                on_active: app.toggle_theme(self.active)

        BoxLayout:
            spacing: 10
            size_hint_y: None
            height: '50dp'
            Label:
                text: "Звук"
                color: app.text_color
            Switch:
                id: sound_switch
                active: app.sound_enabled
                on_active: app.sound_enabled = self.active

        Button:
            text: "Назад"
            size_hint_y: None
            height: '50dp'
            on_release: root.manager.current = 'menu'

<MainMenu>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        canvas.before:
            Color:
                rgba: app.bg_color
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Главное меню'
            font_size: '24sp'
            color: app.text_color
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
        Button:
            text: 'Настройки'
            size_hint_y: None
            height: '50dp'
            background_color: (0.2, 0.6, 0.8, 1)
            color: (1, 1, 1, 1)
            on_release: root.manager.current = 'settings'
        Button:
            text: 'Рынок облигаций'
            size_hint_y: None
            height: '50dp'
            background_color: (0.2, 0.6, 0.8, 1)
            color: (1, 1, 1, 1)
            on_release:
                app.show_market()
                root.manager.current = 'market'

<BondMarketScreen>:
    name: 'market'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        canvas.before:
            Color:
                rgba: app.bg_color
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Доступные облигации для добавления"
            font_size: '20sp'
            color: app.text_color
            size_hint_y: None
            height: '40dp'

        ScrollView:
            BoxLayout:
                id: market_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 10

        Button:
            text: "Назад"
            size_hint_y: None
            height: '50dp'
            on_release: root.manager.current = 'menu'

<AddBondScreen>:
    name: 'add'
    AnchorLayout:
        anchor_y: 'top'
        padding: 20

        canvas.before:
            Color:
                rgba: app.bg_color
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
                rgba: app.bg_color
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: '60dp'
            spacing: 10
            Label:
                id: total_monthly
                text: "Суммарный месячный доход: 0"
                color: app.text_color
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            Label:
                id: total_annual
                text: "Суммарный годовой доход: 0"
                color: app.text_color
                text_size: self.size
                halign: 'right'
                valign: 'middle'

        Label:
            text: "Список облигаций:"
            size_hint_y: None
            height: '40dp'
            font_size: '18sp'
            bold: True
            color: app.text_color

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
            rgba: app.bg_color
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
                color: app.text_color
            BoxLayout:
                spacing: 5
                Label:
                    text: "Тикер: " + root.ticker
                    color: app.text_color
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'

                Label:
                    text: "Цена покупки: " + str(root.purchase_price)
                    color: app.text_color
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
            BoxLayout:
                spacing: 5
                Label:
                    text: "Количество: " + str(root.quantity)
                    color: app.text_color
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                Label:
                    text: "Месячный доход: " + str(round(root.monthly_income, 2))
                    color: app.text_color
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
            BoxLayout:
                spacing: 5
                Label:
                    text: "Годовой доход: " + str(round(root.annual_income, 2))
                    color: app.text_color
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                Label:
                    text: "Доходность к погашению: " + str(round(root.ytm, 2)) + "%"
                    color: app.text_color
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
            BoxLayout:
                Label:
                    text: "Дата погашения: " + root.matdate
                    color: app.text_color
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                Label:
                    text: "Оферта: " + root.offerdate
                    color: app.text_color
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

class MainMenu(Screen):
    pass

class AddBondScreen(Screen):
    pass

class BondListScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class BondMarketScreen(Screen):
    pass

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
    quantity = NumericProperty(0)
    ytm = NumericProperty(0)

def get_board_id(ticker):
    url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/securities/{ticker}/securities.xml?iss.meta=off&iss.only=marketdata&marketdata.columns=BOARDID"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            row = root.find(".//row")
            if row is not None:
                board_id = row.attrib.get("BOARDID", "")
                return board_id
    except requests.exceptions.ConnectionError:
        App.get_running_app().show_error("Нет подключения к интернету. Проверьте соединение.")
    except Exception:
        App.get_running_app().show_error("Ошибка при получении данных с сервера MOEX.")
    return ""

def fetch_filtered_bonds(limit=10):
    url = "https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities.xml?iss.meta=off&iss.only=securities&securities.columns=SECID,SHORTNAME,COUPONPERCENT,COUPONVALUE,MATDATE"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        rows = root.findall(".//row")

        suitable_bonds = []
        today = datetime.now()

        for row in rows:
            try:
                secid = row.attrib.get("SECID")
                shortname = row.attrib.get("SHORTNAME", secid)
                coupon_percent = float(row.attrib.get("COUPONPERCENT", 0))
                coupon_value = float(row.attrib.get("COUPONVALUE", 0))
                matdate_raw = row.attrib.get("MATDATE", "")
                if not secid or coupon_percent <= 0 or not matdate_raw:
                    continue
                matdate = datetime.strptime(matdate_raw, "%Y-%m-%d")
                years_left = (matdate - today).days / 365.25

                if years_left >= 1:
                    suitable_bonds.append({
                        "ticker": secid,
                        "name": shortname,
                        "ytm": coupon_percent
                    })

                    if len(suitable_bonds) >= limit:
                        break
            except Exception as e:
                print("Ошибка в обработке облигации:", e)
                continue

        print(f"Подходящих облигаций: {len(suitable_bonds)}")
        return suitable_bonds
    except Exception as e:
        print("Ошибка при получении списка облигаций:", e)
        return []


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
    except requests.exceptions.ConnectionError:
        App.get_running_app().show_error("Не удалось загрузить данные о бумаге. Нет соединения с интернетом.")
        return data
    except Exception as e:
        App.get_running_app().show_error("Сервер биржи не отвечает. Повторите попытку позже.")
        return data

    return data

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

def calculate_income(purchase_price, coupon_value, coupon_percent, facevalue, quantity):
    try:
        if coupon_value > 0:
            annual_income = coupon_value * quantity
        elif coupon_percent > 0 and facevalue > 0:
            annual_income = facevalue * (coupon_percent / 100) * quantity
        else:
            annual_income = purchase_price * (coupon_percent / 100) * quantity

        monthly_income = annual_income / 12
        return round(monthly_income, 2), round(annual_income, 2)
    except Exception as e:
        print(f"Ошибка при расчёте доходности: {e}")
        return 0, 0


def calculate_ytm(purchase_price, coupon_value, facevalue, purchase_date, maturity_date):
    try:
        purchase_dt = datetime.strptime(purchase_date, "%Y-%m-%d")
        maturity_dt = datetime.strptime(maturity_date, "%Y-%m-%d")
        years_to_maturity = (maturity_dt - purchase_dt).days / 365.25
        if years_to_maturity <= 0:
            return 0
        ytm = (coupon_value + (facevalue - purchase_price) / years_to_maturity) / ((facevalue + purchase_price) / 2)
        return ytm * 100
    except Exception as e:
        print("Ошибка при расчёте YTM:", e)
        return 0

class BondsApp(App):
    dark_theme = BooleanProperty(False)
    sound_enabled = BooleanProperty(True)
    bg_color = ListProperty([0.95, 0.95, 0.95, 1])
    text_color = ListProperty([0, 0, 0, 1])


    def show_market(self):
        market_screen = self.sm.get_screen("market")
        container = market_screen.ids.market_list
        container.clear_widgets()

        self.play_sound("click")

        container.add_widget(Label(text="Загружаем облигации...", color=self.text_color, size_hint_y=None, height='30dp'))

        def load_bonds_from_moex():
            bonds = fetch_filtered_bonds(limit=10)

            def update_ui(*args):
                container.clear_widgets()
                if not bonds:
                    container.add_widget(Label(text="Не удалось загрузить облигации", color=self.text_color, size_hint_y=None, height='40dp'))
                    return

                for bond in bonds:
                    box = BoxLayout(orientation="horizontal", size_hint_y=None, height="50dp", spacing=10)
                    label = Label(text=f"{bond['name']} ({bond['ticker']}) - Купон: {bond['ytm']}%", color=self.text_color)
                    btn = Button(text="Добавить", size_hint_x=0.3)
                    btn.bind(on_release=lambda inst, b=bond: self.quick_add_bond(b))
                    box.add_widget(label)
                    box.add_widget(btn)
                    container.add_widget(box)

            Clock.schedule_once(update_ui, 0)

        threading.Thread(target=load_bonds_from_moex).start()

    def quick_add_bond(self, bond_info):
        from datetime import date
        today = str(date.today())

        board_id = get_board_id(bond_info["ticker"])
        if not board_id:
            self.show_error("Не удалось получить BOARDID.")
            return

        sec_data = get_securities_data(board_id, bond_info["ticker"])
        last_price = get_marketdata_last(board_id, bond_info["ticker"])
        purchase_price = last_price or sec_data.get("FACEVALUE", 1000)
        quantity = 1

        monthly, annual = calculate_income(purchase_price, sec_data["COUPONVALUE"], sec_data["COUPONPERCENT"], sec_data["FACEVALUE"], quantity)
        ytm = calculate_ytm(purchase_price, sec_data["COUPONVALUE"], sec_data["FACEVALUE"], today, sec_data["MATDATE"]) if sec_data["MATDATE"] else 0

        bond = {
            'ticker': bond_info["ticker"],
            'purchase_price': purchase_price,
            'purchase_date': today,
            'quantity': quantity,
            'shortname': sec_data["SHORTNAME"],
            'board_id': board_id,
            'coupon_percent': sec_data["COUPONPERCENT"],
            'coupon_value': sec_data["COUPONVALUE"],
            'accrued_interest': sec_data["ACCRUEDINT"],
            'last_price': last_price,
            'facevalue': sec_data["FACEVALUE"],
            'matdate': sec_data["MATDATE"],
            'offerdate': sec_data["OFFERDATE"],
            'monthly_income': monthly,
            'annual_income': annual,
            'ytm': ytm
        }

        self.bonds.append(bond)
        self.save_bonds()
        self.update_bonds_view()
        self.show_info(f"Облигация {bond_info['ticker']} добавлена.")

    def format_date(self, raw_date):
        try:
            if raw_date and len(raw_date) == 10:
                dt = datetime.strptime(raw_date, "%Y-%m-%d")
                return dt.strftime("%d.%m.%Y")
        except:
            pass
        return raw_date or "Не указана"

    def toggle_theme(self, is_dark):
        self.dark_theme = is_dark
        if is_dark:
            self.bg_color = [0.15, 0.15, 0.17, 1]
            self.text_color = [1, 1, 1, 1]
        else:
            self.bg_color = [0.95, 0.95, 0.95, 1]
            self.text_color = [0, 0, 0, 1]

    def play_sound(self, name):
        if not self.sound_enabled:
            return
        sound_path = os.path.join(os.path.dirname(__file__), "sounds", f"{name}.mp3")
        sound = SoundLoader.load(sound_path)
        if sound:
            sound.play()

    def build(self):
        self.title = "Отслеживание доходности облигаций"
        self.bonds = []
        self.sm = Builder.load_string(kv)
        self.load_bonds()
        self.update_bonds_view()
        return self.sm

    def show_error(self, message):
        self.play_sound("error")
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(
            text=message,
            halign='center',
            valign='middle'
        )
        label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None))
        )
        close_btn = Button(text='Закрыть', size_hint=(1, 0.3))
        box.add_widget(label)
        box.add_widget(close_btn)
        popup = Popup(title='Ошибка', content=box, size_hint=(0.8, 0.3))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_info(self, message):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)

        label = Label(
            text=message,
            halign='center',
            valign='middle'
        )
        label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None))
        )

        close_btn = Button(text='Ок', size_hint=(1, 0.3))
        box.add_widget(label)
        box.add_widget(close_btn)

        popup = Popup(
            title='Успех',
            content=box,
            size_hint=(0.6, 0.3),
            auto_dismiss=False
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

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
        if not self.bonds:
            self.quick_add_bond({"ticker": "RU000A1089J4", "name": "Селектел 001Р-04R", "ytm": 20})

    def add_bond(self):
        screen = self.sm.get_screen('add')
        ticker = screen.ids.ticker_input.text.strip()
        purchase_price_text = screen.ids.purchase_price_input.text.strip()
        purchase_date = screen.ids.purchase_date_input.text.strip()
        quantity_text = screen.ids.quantity_input.text.strip()
        screen.ids.ticker_input.background_color = (1, 1, 1, 1)
        screen.ids.purchase_price_input.background_color = (1, 1, 1, 1)
        screen.ids.purchase_date_input.background_color = (1, 1, 1, 1)
        screen.ids.quantity_input.background_color = (1, 1, 1, 1)

        try:
            datetime.strptime(purchase_date, "%Y-%m-%d")
        except ValueError:
            self.show_error("Неверный формат даты. Используйте YYYY-MM-DD.")
            return

        if not ticker or not purchase_price_text or not purchase_date or not quantity_text:
            if not ticker:
                screen.ids.ticker_input.background_color = (1, 0.7, 0.7, 1)
            if not purchase_price_text:
                screen.ids.purchase_price_input.background_color = (1, 0.7, 0.7, 1)
            if not purchase_date:
                screen.ids.purchase_date_input.background_color = (1, 0.7, 0.7, 1)
            if not quantity_text:
                screen.ids.quantity_input.background_color = (1, 0.7, 0.7, 1)

            self.show_error("Заполните все поля: тикер, цена покупки, дата покупки и количество.")
            return

        try:
            purchase_price = float(purchase_price_text)
            quantity = int(quantity_text)
        except Exception as e:
            self.show_error("Неверный формат цены покупки или количества.")
            return

        board_id = get_board_id(ticker)
        if not board_id:
            self.show_error(f"Не удалось получить BOARDID для тикера: {ticker}")
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

        monthly_income, annual_income = calculate_income(purchase_price, coupon_value, coupon_percent, facevalue, quantity)
        total_monthly_income = monthly_income * quantity
        total_annual_income = annual_income * quantity

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

        self.play_sound("click")
        self.show_info("Облигация успешно добавлена!")

        screen.ids.ticker_input.text = ""
        screen.ids.purchase_price_input.text = ""
        screen.ids.purchase_date_input.text = ""
        screen.ids.quantity_input.text = ""

    def update_bonds_view(self):
        screen = self.sm.get_screen('list')
        bonds_list = screen.ids.bonds_list
        bonds_list.clear_widgets()

        if not self.bonds:
            empty_label = Label(
                text="Нет добавленных облигаций.",
                size_hint_y=None,
                height='40dp',
                color=self.text_color,
                halign='center',
                valign='middle'
            )
            empty_label.bind(width=lambda inst, val: setattr(inst, 'text_size', (val, None)))
            bonds_list.add_widget(empty_label)

        total_monthly = 0
        total_annual = 0

        for bond in self.bonds:
            total_monthly += bond.get('monthly_income', 0)
            total_annual += bond.get('annual_income', 0)

            matdate = self.format_date(bond.get('matdate', ''))
            offer = bond.get('offerdate', '')
            if not offer or offer.lower() in ['нет', 'нет оферты', 'n/a', '-']:
                offer = 'Не предусмотрена'
            else:
                offer = self.format_date(offer)

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
                offerdate=offer,
                monthly_income=bond['monthly_income'],
                annual_income=bond['annual_income'],
                quantity=bond['quantity'],
                ytm=bond['ytm']
            )
            bonds_list.add_widget(item)

        screen.ids.total_monthly.text = f"Суммарный месячный доход: {round(total_monthly, 2)}"
        screen.ids.total_annual.text = f"Суммарный годовой доход: {round(total_annual, 2)}"

    def remove_bond(self, ticker, purchase_date):
        self.play_sound("bond_delete")
        self.bonds = [b for b in self.bonds if not (b['ticker'] == ticker and b['purchase_date'] == purchase_date)]
        self.save_bonds()
        self.update_bonds_view()

if __name__ == '__main__':
    BondsApp().run()