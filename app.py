# ---------------- FIXES (IMPORTANT) ----------------
import os
os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

from kivy.core.window import Window
Window.size = (400, 700)

# ---------------- IMPORTS ----------------
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import ScreenManager
import sqlite3

print("✅ App Started Successfully")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("awasthi.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS orders(name TEXT, service TEXT, amount INTEGER)")
conn.commit()

# insert admin once
try:
    cur.execute("INSERT INTO users VALUES('admin','1234')")
    conn.commit()
except:
    pass

# ---------------- LOGIN SCREEN ----------------
class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(orientation="vertical", padding=40, spacing=20)

        self.user = MDTextField(hint_text="Username")
        self.passw = MDTextField(hint_text="Password", password=True)

        btn = MDRaisedButton(text="LOGIN", pos_hint={"center_x": 0.5})
        btn.bind(on_press=self.login)

        self.msg = MDLabel(text="", halign="center")

        layout.add_widget(MDLabel(text="Awasthi Brothers Enterprises", halign="center"))
        layout.add_widget(self.user)
        layout.add_widget(self.passw)
        layout.add_widget(btn)
        layout.add_widget(self.msg)

        self.add_widget(layout)

    def login(self, instance):
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (self.user.text, self.passw.text))
        result = cur.fetchone()

        if result:
            if self.user.text == "admin":
                self.manager.current = "admin"
            else:
                self.manager.current = "home"
        else:
            self.msg.text = "❌ Invalid Login!"

# ---------------- HOME SCREEN ----------------
class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        self.name = MDTextField(hint_text="Your Name")
        self.service = MDTextField(hint_text="Service (Construction / Supply)")
        self.amount = MDTextField(hint_text="Amount (₹)")

        btn = MDRaisedButton(text="BOOK SERVICE")
        btn.bind(on_press=self.book)

        self.msg = MDLabel(text="", halign="center")

        layout.add_widget(MDLabel(text="📋 Book Service", halign="center"))
        layout.add_widget(self.name)
        layout.add_widget(self.service)
        layout.add_widget(self.amount)
        layout.add_widget(btn)
        layout.add_widget(self.msg)

        self.add_widget(layout)

    def book(self, instance):
        try:
            amt = int(self.amount.text)
        except:
            self.msg.text = "⚠ Enter valid amount!"
            return

        if self.name.text == "" or self.service.text == "":
            self.msg.text = "⚠ Fill all fields!"
            return

        cur.execute("INSERT INTO orders VALUES(?,?,?)",
                    (self.name.text, self.service.text, amt))
        conn.commit()

        self.msg.text = "✅ Order Saved!"

        self.name.text = ""
        self.service.text = ""
        self.amount.text = ""

# ---------------- ADMIN PANEL ----------------
class AdminScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout_main = MDBoxLayout(orientation="vertical", padding=20, spacing=10)

        title = MDLabel(text="👨‍💼 Admin Panel", halign="center")

        self.refresh_btn = MDRaisedButton(text="🔄 REFRESH DATA")
        self.refresh_btn.bind(on_press=self.load_data)

        self.data_box = MDBoxLayout(orientation="vertical", spacing=5)

        self.layout_main.add_widget(title)
        self.layout_main.add_widget(self.refresh_btn)
        self.layout_main.add_widget(self.data_box)

        self.add_widget(self.layout_main)

    def load_data(self, instance):
        self.data_box.clear_widgets()

        total = 0
        cur.execute("SELECT * FROM orders")
        data = cur.fetchall()

        if not data:
            self.data_box.add_widget(MDLabel(text="No Orders Yet"))
            return

        for d in data:
            total += d[2]
            self.data_box.add_widget(MDLabel(text=f"{d[0]} | {d[1]} | ₹{d[2]}"))

        self.data_box.add_widget(MDLabel(text=f"💰 Total Earnings: ₹{total}", halign="center"))

# ---------------- APP ----------------
class AwasthiApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AdminScreen(name="admin"))

        return sm

if __name__ == "__main__":
    AwasthiApp().run()
