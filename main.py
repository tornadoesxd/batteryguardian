from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle, Mesh, Ellipse
from math import sin, cos, radians
import random
import os

try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    BatteryManager = autoclass('android.os.BatteryManager')
    is_android = True
except:
    is_android = False

def get_asset_path(filename):
    if os.path.exists(filename):
        return filename
    dl_path = os.path.join('/storage/emulated/0/Download', filename)
    if os.path.exists(dl_path):
        return dl_path
    sd_path = os.path.join('/sdcard/Download', filename)
    if os.path.exists(sd_path):
        return sd_path
    return None

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.0, 0.9, 1.0, 0.8)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            Color(0.05, 0.1, 0.2, 0.9)
            RoundedRectangle(pos=(self.x + 2, self.y + 2), size=(self.width - 4, self.height - 4), radius=[14])

def draw_realistic_leaf(cx, cy, length=38, width=17, angle_rad=0, stem_color=(0.15, 0.75, 0.35, 0.95)):
    cos_a, sin_a = cos(angle_rad), sin(angle_rad)
    perp_cos, perp_sin = -sin_a, cos_a
    base = (cx, cy)
    tip = (cx + length * cos_a, cy + length * sin_a)
    left_mid = (cx + length * 0.45 * cos_a + width * 0.5 * perp_cos,
                cy + length * 0.45 * sin_a + width * 0.5 * perp_sin)
    right_mid = (cx + length * 0.45 * cos_a - width * 0.5 * perp_cos,
                 cy + length * 0.45 * sin_a - width * 0.5 * perp_sin)

    Color(*stem_color)
    vertices = [
        base[0], base[1], 0, 0,
        left_mid[0], left_mid[1], 0, 0,
        tip[0], tip[1], 0, 0,
        right_mid[0], right_mid[1], 0, 0
    ]
    Mesh(vertices=vertices, indices=[0, 1, 2, 0, 2, 3], mode='triangles')
    Color(stem_color[0]*0.7, stem_color[1]*1.1, stem_color[2]*0.8, 1)
    Line(points=[base[0], base[1], left_mid[0], left_mid[1], tip[0], tip[1], right_mid[0], right_mid[1], base[0], base[1]], width=1.2)
    Line(points=[base[0], base[1], tip[0], tip[1]], width=1.1)

class SafeLeafyBattery(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.battery_label = Label(text="--%", font_size='56sp', bold=True, color=(0.9, 0.95, 1.0, 1), pos_hint={'center_x': 0.5, 'center_y': 0.58})
        self.add_widget(self.battery_label)
        self.status_label = Label(text="SYSTEM SECURE", font_size='13sp', bold=True, color=(0.4, 0.8, 0.9, 0.9), pos_hint={'center_x': 0.5, 'center_y': 0.47})
        self.add_widget(self.status_label)
        self.swipe_hint = Label(text="<< SWIPE FOR THERMAL & LIVE GRAPH >>", font_size='11sp', bold=True, color=(0.0, 0.8, 0.9, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.22})
        self.add_widget(self.swipe_hint)
        self.anim_offset = 0
        self.particles = [{'x_offset': random.uniform(-25, 25), 'y': random.uniform(0, 300), 'speed': random.uniform(2.5, 4.5), 'size': random.uniform(3, 6)} for _ in range(12)]
        Clock.schedule_once(self.first_draw, 0.1)
        Clock.schedule_interval(self.update_app_state, 0.04)

    def first_draw(self, dt):
        self.update_app_state(0)

    def update_app_state(self, dt):
        app = App.get_running_app()
        if not app: return
        pct, is_charging, _, _, _ = app.battery_data
        self.battery_label.text = f"{pct}%"
        speed = app.config_settings.get('anim_speed', 0.06)
        show_sparks = app.config_settings.get('show_sparks', True)
        
        if is_charging:
            self.anim_offset += speed
            self.status_label.text = "BATTERY FULL - UNPLUG" if pct >= 100 else "ENERGY PORTAL ACTIVE"
            self.status_label.color = (0.2, 1.0, 0.3, 1) if pct >= 100 else (0.2, 1.0, 0.6, 1)
            circle_color = (0.0, 0.9, 1.0, 1)
        else:
            self.anim_offset = 0
            self.status_label.text = "SYSTEM DISCHARGING"
            self.status_label.color = (0.7, 0.8, 0.9, 0.8)
            circle_color = (0.2, 1.0, 0.5, 1) if pct > 50 else ((1.0, 0.8, 0.1, 1) if pct > 20 else (1.0, 0.3, 0.3, 1))

        if self.width > 100 and self.height > 100:
            self.canvas.before.clear()
            with self.canvas.before:
                cx, cy = self.width / 2, self.height * 0.58
                radius_in, radius_out = 135, 170
                Color(0.05, 0.08, 0.18, 0.55)
                RoundedRectangle(pos=(cx - 190, cy - 190), size=(380, 380), radius=[30])
                Color(0.15, 0.3, 0.5, 0.4)
                Line(rounded_rectangle=(cx - 190, cy - 190, 380, 380, 30), width=1.5)

                Color(0.1, 0.15, 0.25, 0.6)
                Line(circle=(cx, cy, radius_in), width=12)
                Color(*circle_color)
                Line(circle=(cx, cy, radius_in, 0, (pct / 100) * 360), width=14, cap='round')
                
                if is_charging:
                    target_top_y = int(cy - radius_in)
                    points_data = [(cx + sin(y * 0.03 + self.anim_offset * 1.8) * 16, y) for y in range(0, target_top_y + 12, 12)]
                    for i in range(len(points_data) - 1):
                        x1, y1 = points_data[i]
                        x2, y2 = points_data[i + 1]
                        progress = y1 / float(target_top_y if target_top_y > 0 else 1)
                        t_width = 15.0 * (1.0 - progress * 0.76)
                        Color(0.1, 0.35, 0.18, 0.7)
                        Line(points=[x1, y1, x2, y2], width=t_width, cap='round')
                        Color(0.2, 0.85, 0.4, 0.95)
                        Line(points=[x1, y1, x2, y2], width=max(1.8, t_width * 0.5), cap='round')

                    for idx, y_pos in enumerate([60, 140, 220, 290]):
                        if y_pos < target_top_y - 20:
                            cur_x = cx + sin(y_pos * 0.03 + self.anim_offset * 1.8) * 16
                            is_right = (idx % 2 == 0)
                            base_angle = 0.4 if is_right else 2.74
                            angle_osc = sin(self.anim_offset * 2 + idx) * 0.15
                            stem_end_x = cur_x + (15 if is_right else -15)
                            stem_end_y = y_pos + 8
                            Color(0.18, 0.75, 0.35, 0.9)
                            Line(points=[cur_x, y_pos, stem_end_x, stem_end_y], width=2.5, cap='round')
                            draw_realistic_leaf(stem_end_x, stem_end_y, length=38, width=17, angle_rad=base_angle + angle_osc)

                    if show_sparks:
                        for p in self.particles:
                            p['y'] += p['speed']
                            if p['y'] > target_top_y:
                                p['y'] = random.uniform(0, 30)
                                p['x_offset'] = random.uniform(-20, 20)
                            spark_x = (cx + sin(p['y'] * 0.03 + self.anim_offset * 1.8) * 16) + p['x_offset']
                            Color(0.2, 1.0, 0.8, 0.75)
                            Ellipse(pos=(spark_x, p['y']), size=(p['size'], p['size']))

                    for ring_offset, alpha in [(0, 0.85), (24, 0.5)]:
                        petal_points = []
                        for angle in range(0, 365, 4):
                            wave = sin(angle * 0.08 + self.anim_offset * 2.5) * 14 + cos(angle * 0.04 - self.anim_offset * 1.8) * 7
                            r = radius_out + ring_offset + wave
                            theta = radians(angle + self.anim_offset * 12)
                            petal_points.extend([cx + r * cos(theta), cy + r * sin(theta)])
                        if len(petal_points) >= 4:
                            Color(0.2, 0.9, 0.45, alpha)
                            Line(points=petal_points, width=3, joint='round', cap='round')

                    for angle_deg in range(0, 360, 60):
                        theta = radians(angle_deg + self.anim_offset * 12)
                        wave_offset = sin(angle_deg * 0.1 + self.anim_offset * 2.5) * 10
                        leaf_r = radius_out + 12 + wave_offset
                        draw_realistic_leaf(cx + leaf_r * cos(theta), cy + leaf_r * sin(theta), length=32, width=15, angle_rad=theta + 0.35, stem_color=(0.25, 0.95, 0.5, 0.92))
                else:
                    Color(0.3, 0.6, 0.8, 0.3)
                    Line(circle=(cx, cy, radius_out), width=1.5)

class ThermalScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_ui, size=self.update_ui)
        self.add_widget(Label(text="THERMAL MONITOR", font_size='22sp', bold=True, color=(0.0, 0.9, 1.0, 1), pos_hint={'center_x': 0.5, 'center_y': 0.80}))
        self.temp_val = Label(text="-- C", font_size='54sp', bold=True, color=(0.2, 1.0, 0.6, 1), pos_hint={'center_x': 0.5, 'center_y': 0.63})
        self.add_widget(self.temp_val)
        self.condition_lbl = Label(text="STATUS: COOL & STABLE", font_size='14sp', bold=True, color=(0.7, 0.9, 1.0, 0.9), pos_hint={'center_x': 0.5, 'center_y': 0.52})
        self.add_widget(self.condition_lbl)
        
        box = BoxLayout(orientation='vertical', spacing=8, size_hint=(0.8, 0.22), pos_hint={'center_x': 0.5, 'center_y': 0.36})
        self.volt_lbl = Label(text="VOLTAGE: -- V", font_size='15sp', bold=True, color=(0.9, 0.95, 1.0, 0.9))
        self.health_lbl = Label(text="HEALTH: GOOD", font_size='15sp', bold=True, color=(0.2, 1.0, 0.5, 0.9))
        self.source_lbl = Label(text="SOURCE: AC ADAPTER", font_size='15sp', bold=True, color=(0.6, 0.8, 1.0, 0.9))
        box.add_widget(self.volt_lbl)
        box.add_widget(self.health_lbl)
        box.add_widget(self.source_lbl)
        self.add_widget(box)

        self.hint = Label(text="<< SWIPE RIGHT / LEFT >>", font_size='11sp', bold=True, color=(0.0, 0.8, 0.9, 0.5), pos_hint={'center_x': 0.5, 'center_y': 0.18})
        self.add_widget(self.hint)
        Clock.schedule_interval(self.refresh_stats, 0.5)

    def update_ui(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            cx, cy = self.width / 2, self.height / 2
            Color(0.05, 0.08, 0.18, 0.7)
            RoundedRectangle(pos=(cx - 180, cy - 240), size=(360, 480), radius=[30])
            Color(0.15, 0.35, 0.6, 0.4)
            Line(rounded_rectangle=(cx - 180, cy - 240, 360, 480, 30), width=1.5)

    def refresh_stats(self, dt):
        app = App.get_running_app()
        if not app: return
        _, is_charging, temp, volt, health = app.battery_data
        self.temp_val.text = f"{temp:.1f} C"
        self.volt_lbl.text = f"VOLTAGE: {volt:.2f} V"
        self.health_lbl.text = f"HEALTH: {health}"
        self.source_lbl.text = "SOURCE: AC WALL CHARGER" if is_charging else "SOURCE: DISCONNECTED"
        if temp > 42.0:
            self.temp_val.color = (1.0, 0.3, 0.3, 1)
            self.condition_lbl.text = "WARNING: BATTERY OVERHEATING!"
            self.condition_lbl.color = (1.0, 0.3, 0.3, 1)
        elif temp > 36.0:
            self.temp_val.color = (1.0, 0.8, 0.2, 1)
            self.condition_lbl.text = "STATUS: MODERATE TEMPERATURE"
            self.condition_lbl.color = (1.0, 0.8, 0.2, 1)
        else:
            self.temp_val.color = (0.2, 1.0, 0.6, 1)
            self.condition_lbl.text = "STATUS: OPTIMAL AND COOL"
            self.condition_lbl.color = (0.2, 1.0, 0.6, 1)

class BatteryGraphScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw_graph, size=self.draw_graph)
        self.title = Label(text="LIVE POWER TREND (MARKET STYLE)", font_size='18sp', bold=True, color=(0.0, 0.9, 1.0, 1), pos_hint={'center_x': 0.5, 'center_y': 0.84})
        self.add_widget(self.title)
        self.stats_top = Label(text="BATTERY: --%  |  CURVE: ACTIVE  |  VOLT: -- V", font_size='12sp', bold=True, color=(0.2, 1.0, 0.6, 1), pos_hint={'center_x': 0.5, 'center_y': 0.77})
        self.add_widget(self.stats_top)
        self.legend = Label(text="CYAN: Battery Level Trend (%)   |   ORANGE: Temp Fluctuation (C)", font_size='10sp', bold=True, color=(0.7, 0.8, 0.9, 0.7), pos_hint={'center_x': 0.5, 'center_y': 0.25})
        self.add_widget(self.legend)
        self.hint = Label(text="<< SWIPE RIGHT TO GO BACK", font_size='11sp', bold=True, color=(0.0, 0.8, 0.9, 0.5), pos_hint={'center_x': 0.5, 'center_y': 0.16})
        self.add_widget(self.hint)
        Clock.schedule_interval(self.draw_graph, 0.5)

    def draw_graph(self, *args):
        app = App.get_running_app()
        if not app: return
        pct, is_chg, temp, volt, _ = app.battery_data
        trend_status = "BULLISH (CHARGING)" if is_chg else "BEARISH (DRAIN)"
        self.stats_top.text = f"LEVEL: {pct}%  |  TREND: {trend_status}  |  {volt:.2f} V"
        self.stats_top.color = (0.2, 1.0, 0.5, 1) if is_chg else (1.0, 0.4, 0.4, 1)

        self.canvas.before.clear()
        with self.canvas.before:
            cx, cy = self.width / 2, self.height / 2
            card_w, card_h = 360, 480
            Color(0.04, 0.07, 0.16, 0.75)
            RoundedRectangle(pos=(cx - card_w/2, cy - card_h/2), size=(card_w, card_h), radius=[26])
            Color(0.12, 0.3, 0.55, 0.45)
            Line(rounded_rectangle=(cx - card_w/2, cy - card_h/2, card_w, card_h, 26), width=1.5)

            chart_x, chart_y = cx - 150, cy - 80
            chart_w, chart_h = 300, 180

            Color(0.15, 0.25, 0.4, 0.3)
            for row in range(5):
                gy = chart_y + row * (chart_h / 4)
                Line(points=[chart_x, gy, chart_x + chart_w, gy], width=1)
            for col in range(5):
                gx = chart_x + col * (chart_w / 4)
                Line(points=[gx, chart_y, gx, chart_y + chart_h], width=1)

            b_hist = app.battery_history
            if len(b_hist) >= 2:
                b_pts = []
                for i, val in enumerate(b_hist):
                    px = chart_x + (i / float(len(b_hist) - 1)) * chart_w
                    py = chart_y + (val / 100.0) * chart_h
                    b_pts.extend([px, py])
                Color(0.0, 0.95, 1.0, 0.95)
                Line(points=b_pts, width=2.8, joint='round')
                Color(0.2, 1.0, 0.8, 1)
                Ellipse(pos=(b_pts[-2] - 4, b_pts[-1] - 4), size=(8, 8))

            t_hist = app.temp_history
            if len(t_hist) >= 2:
                t_pts = []
                for i, val in enumerate(t_hist):
                    px = chart_x + (i / float(len(t_hist) - 1)) * chart_w
                    mapped_temp = max(0.0, min(1.0, (val - 20.0) / 30.0))
                    py = chart_y + mapped_temp * chart_h
                    t_pts.extend([px, py])
                Color(1.0, 0.65, 0.1, 0.8)
                Line(points=t_pts, width=2.0, joint='round')

class BatteryGuardianPro(App):
    def build(self):
        self.config_settings = {'anim_speed': 0.06, 'show_sparks': True, 'alarm': True, 'bgm_on': True}
        self.battery_data = (88, True, 32.4, 4.15, "GOOD")
        self.battery_history = [80 + random.uniform(-2, 2) for _ in range(25)]
        self.temp_history = [32 + random.uniform(-1, 1) for _ in range(25)]

        Clock.schedule_interval(self.poll_hardware, 1.0)
        Clock.schedule_interval(self.record_history, 3.0)

        root = FloatLayout()
        
        bg_real_path = get_asset_path('space_bg.jpg')
        if bg_real_path:
            root.add_widget(Image(source=bg_real_path, allow_stretch=True, keep_ratio=False))
        else:
            with root.canvas.before:
                Color(0.03, 0.05, 0.1, 1)
                RoundedRectangle(pos=(0, 0), size=(2000, 2000))

        sound_real_path = get_asset_path('bg_music.mp3')
        if sound_real_path:
            from kivy.core.audio import SoundLoader
            self.sound = SoundLoader.load(sound_real_path)
            if self.sound:
                self.sound.loop = True
                self.sound.volume = 0.4
                self.sound.play()
        else:
            self.sound = None

        self.carousel = Carousel(direction='right', size_hint=(1, 0.88), pos_hint={'x': 0, 'y': 0})
        self.carousel.add_widget(SafeLeafyBattery())
        self.carousel.add_widget(ThermalScreen())
        self.carousel.add_widget(BatteryGraphScreen())
        root.add_widget(self.carousel)

        top_bar = FloatLayout(size_hint=(1, 0.12), pos_hint={'x': 0, 'top': 1})
        top_bar.add_widget(Label(text="BATTERY GUARDIAN", font_size='18sp', bold=True, color=(0.0, 0.9, 1.0, 1), pos_hint={'center_x': 0.38, 'center_y': 0.5}))

        self.settings_btn = RoundedButton(text="SETTINGS", size_hint=(0.28, 0.48), pos_hint={'center_x': 0.83, 'center_y': 0.5}, color=(0.0, 0.9, 1.0, 1), font_size='12sp', bold=True)
        self.settings_btn.bind(on_release=self.open_settings_dialog)
        top_bar.add_widget(self.settings_btn)

        root.add_widget(top_bar)
        return root

    def open_settings_dialog(self, *args):
        content = BoxLayout(orientation='vertical', spacing=14, padding=16)
        grid = GridLayout(cols=2, spacing=10, size_hint_y=0.7)
        grid.add_widget(Label(text="Energy Sparks:", font_size='14sp', bold=True))
        spark_sw = Switch(active=self.config_settings['show_sparks'])
        grid.add_widget(spark_sw)

        grid.add_widget(Label(text="Overcharge Alarm:", font_size='14sp', bold=True))
        alarm_sw = Switch(active=self.config_settings['alarm'])
        grid.add_widget(alarm_sw)

        grid.add_widget(Label(text="Background Music:", font_size='14sp', bold=True))
        bgm_sw = Switch(active=self.config_settings['bgm_on'])
        grid.add_widget(bgm_sw)
        content.add_widget(grid)

        save_btn = RoundedButton(text="SAVE & APPLY", size_hint=(1, 0.28), color=(0.2, 1.0, 0.5, 1), bold=True)
        content.add_widget(save_btn)

        popup = Popup(title='System Preferences', content=content, size_hint=(0.88, 0.46), auto_dismiss=True)
        def save_and_close(inst):
            self.config_settings['show_sparks'] = spark_sw.active
            self.config_settings['alarm'] = alarm_sw.active
            self.config_settings['bgm_on'] = bgm_sw.active
            if self.sound:
                if self.config_settings['bgm_on'] and self.sound.state != 'play':
                    self.sound.play()
                elif not self.config_settings['bgm_on'] and self.sound.state == 'play':
                    self.sound.stop()
            popup.dismiss()
        save_btn.bind(on_release=save_and_close)
        popup.open()

    def record_history(self, dt):
        pct, _, temp, _, _ = self.battery_data
        self.battery_history.append(pct)
        if len(self.battery_history) > 25: self.battery_history.pop(0)
        self.temp_history.append(temp)
        if len(self.temp_history) > 25: self.temp_history.pop(0)

    def poll_hardware(self, dt):
        if is_android:
            try:
                activity = PythonActivity.mActivity
                status = activity.registerReceiver(None, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
                level = status.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                scale = status.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                pct = int((level / float(scale)) * 100) if level != -1 else 75
                chg = status.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
                is_chg = chg in (BatteryManager.BATTERY_STATUS_CHARGING, BatteryManager.BATTERY_STATUS_FULL)
                temp = status.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) / 10.0
                volt = status.getIntExtra(BatteryManager.EXTRA_VOLTAGE, 0) / 1000.0
                self.battery_data = (pct, is_chg, temp, volt, "GOOD")
                return
            except:
                pass
        self.battery_data = (85, True, 32.0, 4.12, "GOOD")

if __name__ == '__main__':
    BatteryGuardianPro().run()
