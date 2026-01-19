# oczyszczalnia_scada_uproszczone.py - KOMPLETNY KOD
import sys
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QSlider)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QFont

# ==================== KLASY BAZOWE ====================
class Rura:
    def __init__(self, punkty, grubosc=8, kolor=Qt.gray):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie
        
    def draw(self, painter):
        if len(self.punkty) < 2:
            return
        
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)
            
        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)

class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0
        self.temperatura = 20.0
        self.kolor_cieczy = QColor(100, 100, 200, 200)
        
    def dodaj_ciecz(self, ilosc, temperatura_dodawanej=20.0):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        
        if self.aktualna_ilosc > 0 and dodano > 0:
            stara_masa = self.aktualna_ilosc
            nowa_masa = dodano
            self.temperatura = (stara_masa * self.temperatura + nowa_masa * temperatura_dodawanej) / (stara_masa + nowa_masa)
        elif dodano > 0:
            self.temperatura = temperatura_dodawanej
            
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano
    
    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto
    
    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc if self.pojemnosc > 0 else 0
        
    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1
    
    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1
    
    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)
    
    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)
    
    def punkt_lewy_srodek(self):
        return (self.x, self.y + self.height / 2)
    
    def punkt_prawy_srodek(self):
        return (self.x + self.width, self.y + self.height / 2)
        
    def draw(self, painter):
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.kolor_cieczy)
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6), int(h_cieczy - 2))

        pen = QPen(Qt.white, 3)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        
        painter.setPen(Qt.white)
        font = QFont("Arial", 10)
        painter.setFont(font)
        nazwa_text = f"{self.nazwa}\n{self.temperatura:.1f}°C"
        painter.drawText(int(self.x), int(self.y - 25), nazwa_text)
        
        poziom_text = f"{int(self.poziom * 100)}%"
        painter.drawText(int(self.x + self.width/2 - 15), int(self.y + self.height + 20), poziom_text)

class Pompa:
    def __init__(self, x, y, nazwa="Pompa"):
        self.x = x
        self.y = y
        self.nazwa = nazwa
        self.wlaczona = False
        
    def draw(self, painter):
        if self.wlaczona:
            painter.setBrush(QColor(0, 200, 0))
        else:
            painter.setBrush(QColor(100, 100, 100))
        
        painter.setPen(QPen(Qt.white, 2))
        painter.drawEllipse(int(self.x - 15), int(self.y - 15), 30, 30)
        
        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 15), int(self.y + 30), self.nazwa)

class Filtr:
    def __init__(self, x, y, width=80, height=120, nazwa="Filtr"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.stopien_zatkania = 0.0
        self.czy_pracuje = False
        
    def draw(self, painter):
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(150, 150, 100, 100))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        
        zatkanie_wysokosc = self.height * (self.stopien_zatkania / 100)
        painter.setBrush(QColor(150, 100, 50, 200))
        painter.drawRect(int(self.x + 10), 
                        int(self.y + self.height - zatkanie_wysokosc), 
                        int(self.width - 20), 
                        int(zatkanie_wysokosc))
        
        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), f"{self.nazwa} ({int(self.stopien_zatkania)}%)")

class Grzalka:
    def __init__(self, x, y, nazwa="Grzalka"):
        self.x = x
        self.y = y
        self.nazwa = nazwa
        self.temperatura = 20.0
        self.wlaczona = False
        self.moc = 0.0
        
    def draw(self, painter):
        if self.wlaczona:
            painter.setBrush(QColor(255, 50, 50))
        else:
            painter.setBrush(QColor(100, 100, 100))
        
        painter.setPen(QPen(Qt.white, 2))
        painter.drawEllipse(int(self.x - 15), int(self.y - 15), 30, 30)
        
        painter.setPen(Qt.white)
        temp_text = f"{self.nazwa}\n{self.moc:.0f}%"
        painter.drawText(int(self.x - 25), int(self.y + 40), temp_text)

class Sensor:
    def __init__(self, x, y, typ="pH", nazwa="Sensor", zbiornik=None):
        self.x = x
        self.y = y
        self.typ = typ
        self.nazwa = nazwa
        self.zbiornik = zbiornik
        
        if typ == "pH":
            self.wartosc = 11.0
            self.min_wartosc = 6.0
            self.max_wartosc = 12.0
            self.jednostka = "pH"
        elif typ == "Temp":
            self.wartosc = 20.0
            self.min_wartosc = 15.0
            self.max_wartosc = 40.0
            self.jednostka = "°C"
            
    def odswiez_wartosc(self):
        if self.zbiornik and self.typ == "Temp":
            self.wartosc = self.zbiornik.temperatura
        else:
            if self.typ == "pH":
                self.wartosc += random.uniform(-0.05, 0.05) 
            
    def czy_alarm(self):
        if self.typ == "Temp":
            if "bioreaktor" in self.nazwa.lower():
                return self.wartosc < 28 or self.wartosc > 38
        return self.wartosc < self.min_wartosc or self.wartosc > self.max_wartosc
        
    def draw(self, painter):
        if self.czy_alarm():
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QColor(255, 0, 0, 100))
        else:
            painter.setPen(QPen(Qt.green, 2))
            painter.setBrush(QColor(0, 200, 0, 100))
            
        painter.drawEllipse(int(self.x - 10), int(self.y - 10), 20, 20)
        
        painter.setPen(Qt.white)
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        if self.typ == "pH":
            text = f"pH: {self.wartosc:.1f}"
        elif self.typ == "Temp":
            text = f"T: {self.wartosc:.1f}°C"
            
        painter.drawText(int(self.x - 20), int(self.y - 15), text)
        if self.nazwa:
            painter.drawText(int(self.x - 20), int(self.y + 25), self.nazwa)

class VizWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scada = parent
        self.setStyleSheet("background-color: #162447; border: 2px solid #0f3460;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.scada:
            return
            
        painter.setPen(Qt.white)
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(10, 30, "SYSTEM OCZYSZCZALNI ŚCIEKÓW - SCADA")
        
        for rura in self.scada.rury:
            rura.draw(painter)
            
        for zbiornik in self.scada.zbiorniki:
            zbiornik.draw(painter)
            
        self.scada.pompa1.draw(painter)
        self.scada.pompa2.draw(painter)
        self.scada.pompa3.draw(painter)
        self.scada.pompa4.draw(painter)
        self.scada.pompa_napow.draw(painter)
        
        self.scada.filtr.draw(painter)
        self.scada.grzalka.draw(painter)
        
        for sensor in self.scada.sensory:
            sensor.draw(painter)
        
        painter.setPen(Qt.white)
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(50, 500, "Legenda:")
        painter.drawText(50, 520, "● Zbiorniki ● Pompy ● Sensory ● Filtr ● Grzałka")

class OczyszczalniaScada(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCADA Oczyszczalni Ścieków")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background-color: #1a1a2e;")
        
        self.inicjalizuj_elementy()
        self.inicjalizuj_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.symuluj_proces)
        self.timer.start(100)
        
        self.auto_mode = True
        self.czas_symulacji = 0
        
    def inicjalizuj_elementy(self):
        self.zb_surowe = Zbiornik(50, 200, nazwa="Ścieki surowe")
        self.zb_surowe.aktualna_ilosc = 80.0
        self.zb_surowe.temperatura = 18.0
        self.zb_surowe.kolor_cieczy = QColor(150, 100, 50, 200)
        self.zb_surowe.aktualizuj_poziom()
        
        self.zb_wstepny = Zbiornik(250, 100, nazwa="Osadnik wstępny")
        self.zb_wstepny.temperatura = 20.0
        self.zb_wstepny.kolor_cieczy = QColor(130, 110, 70, 200)
        
        self.zb_bioreaktor = Zbiornik(450, 100, nazwa="Bioreaktor")
        self.zb_bioreaktor.temperatura = 25.0
        self.zb_bioreaktor.kolor_cieczy = QColor(80, 120, 80, 200)
        
        self.zb_wtorny = Zbiornik(650, 100, nazwa="Osadnik wtórny")
        self.zb_wtorny.temperatura = 22.0
        self.zb_wtorny.kolor_cieczy = QColor(70, 100, 120, 200)
        
        self.zb_czyste = Zbiornik(850, 100, nazwa="Woda oczyszczona")
        self.zb_czyste.temperatura = 20.0
        self.zb_czyste.kolor_cieczy = QColor(0, 100, 200, 150)
        
        self.zbiorniki = [self.zb_surowe, self.zb_wstepny, self.zb_bioreaktor, 
                         self.zb_wtorny, self.zb_czyste]
        
        self.pompa1 = Pompa(180, 170, "P1")
        self.pompa2 = Pompa(380, 150, "P2")
        self.pompa3 = Pompa(580, 150, "P3")
        self.pompa4 = Pompa(780, 150, "P4")
        self.pompa_napow = Pompa(500, 50, "Napow.")
        
        self.filtr = Filtr(952, 120, nazwa="Filtr")
        self.grzalka = Grzalka(500, 180, "Grzalka")
        
        # Sensory
        self.sensor_ph_bioreaktor = Sensor(450, 290, "pH", "Bio pH", self.zb_bioreaktor)
        self.sensor_temp_bioreaktor = Sensor(500, 290, "Temp", "Bio Temp", self.zb_bioreaktor)
        self.sensor_temp_wstepny = Sensor(270, 290, "Temp", "Osadnik", self.zb_wstepny)
        self.sensor_ph_wstepny = Sensor(330, 290, "pH", "Osad pH", self.zb_wstepny)
        
        self.sensor_ph_wtorny = Sensor(700, 290, "pH", "Wtórny pH", self.zb_wtorny)
        self.sensor_ph_wtorny.wartosc = 11.0 
        self.sensor_ph_wtorny.min_wartosc = 6.0
        self.sensor_ph_wtorny.max_wartosc = 9.0  # Alarm powyżej 9
        
        self.sensory = [
            self.sensor_ph_bioreaktor,
            self.sensor_temp_bioreaktor,
            self.sensor_temp_wstepny,
            self.sensor_ph_wstepny,
            self.sensor_ph_wtorny 
        ]
        
        self.rura1 = Rura([
            self.zb_surowe.punkt_prawy_srodek(),
            (180, self.zb_surowe.y + self.zb_surowe.height/2),
            (180, 170),
            self.zb_wstepny.punkt_lewy_srodek()
        ])
        
        self.rura2 = Rura([
            self.zb_wstepny.punkt_prawy_srodek(),
            (380, self.zb_wstepny.y + self.zb_wstepny.height/2),
            (380, 150),
            self.zb_bioreaktor.punkt_lewy_srodek()
        ])
        
        self.rura3 = Rura([
            self.zb_bioreaktor.punkt_prawy_srodek(),
            (580, self.zb_bioreaktor.y + self.zb_bioreaktor.height/2),
            (580, 150),
            self.zb_wtorny.punkt_lewy_srodek()
        ])
        
        self.rura4 = Rura([
            self.zb_wtorny.punkt_prawy_srodek(),
            (780, self.zb_wtorny.y + self.zb_wtorny.height/2),
            (780, 150),
            self.zb_czyste.punkt_lewy_srodek()
        ])
        
        self.rura_napow = Rura([
            (500, 50),
            (500, 100),
            self.zb_bioreaktor.punkt_gora_srodek()
        ], grubosc=8, kolor=Qt.blue)
        
        self.rury = [self.rura1, self.rura2, self.rura3, self.rura4, self.rura_napow]
        
    def inicjalizuj_ui(self):
        main_layout = QVBoxLayout()
        
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: System aktywny | Tryb: AUTO")
        self.status_label.setStyleSheet("color: white; font-size: 14px;")
        status_layout.addWidget(self.status_label)
        
        self.czas_label = QLabel("Czas: 00:00")
        self.czas_label.setStyleSheet("color: white; font-size: 14px;")
        status_layout.addWidget(self.czas_label)
        
        self.temp_label = QLabel("Temp bioreaktora: 25.0°C")
        self.temp_label.setStyleSheet("color: white; font-size: 14px;")
        status_layout.addWidget(self.temp_label)
        
        status_layout.addStretch()
        main_layout.addLayout(status_layout)
        
        self.viz_widget = VizWidget(self)
        self.viz_widget.setFixedHeight(600)
        main_layout.addWidget(self.viz_widget)
        
        control_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶ START")
        self.btn_start.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px;")
        self.btn_start.clicked.connect(self.start_symulacji)
        
        self.btn_stop = QPushButton("⏹ STOP")
        self.btn_stop.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px;")
        self.btn_stop.clicked.connect(self.stop_symulacji)
        
        self.btn_reset = QPushButton("↻ RESET")
        self.btn_reset.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 10px;")
        self.btn_reset.clicked.connect(self.reset_symulacji)
        
        self.btn_auto = QPushButton("AUTO/MANU")
        self.btn_auto.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 10px;")
        self.btn_auto.clicked.connect(self.przelacz_tryb)
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        control_layout.addWidget(self.btn_reset)
        control_layout.addWidget(self.btn_auto)
        control_layout.addStretch()
        
        self.slider_przeplyw = QSlider(Qt.Horizontal)
        self.slider_przeplyw.setRange(1, 10)
        self.slider_przeplyw.setValue(5)
        self.slider_przeplyw.setEnabled(False)
        self.slider_label = QLabel("Przepływ: 5.0 L/s")
        self.slider_label.setStyleSheet("color: white;")
        
        control_layout.addWidget(QLabel("Przepływ:"))
        control_layout.addWidget(self.slider_przeplyw)
        control_layout.addWidget(self.slider_label)
        
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)
        
    def symuluj_proces(self):
        if not self.auto_mode:
            return
            
        self.czas_symulacji += 1
        
        minuty = self.czas_symulacji // 600
        sekundy = (self.czas_symulacji % 600) // 10
        self.czas_label.setText(f"Czas: {minuty:02d}:{sekundy:02d}")
        
        temp_bioreaktor = self.zb_bioreaktor.temperatura
        
        uchyb = 25.0 - temp_bioreaktor
        
        if uchyb >= -1:
            self.grzalka.wlaczona = True
            self.grzalka.moc = 100
            self.zb_bioreaktor.temperatura += 0.2
            self.grzalka.temperatura = self.zb_bioreaktor.temperatura
        elif uchyb < -1:
            self.grzalka.wlaczona = False
            self.grzalka.moc = 0
            self.zb_bioreaktor.temperatura -= 0.03
            self.grzalka.temperatura = self.zb_bioreaktor.temperatura
        
        for sensor in self.sensory:
            sensor.odswiez_wartosc()
        
        #Ph
        if self.zb_wtorny.aktualna_ilosc > 0:
            # Im więcej wody, tym wolniejszy spadek pH
            spadek_ph = 0.02 / max(1, self.zb_wtorny.poziom * 3)
            self.sensor_ph_wtorny.wartosc -= spadek_ph
            self.sensor_ph_wtorny.wartosc = max(6.0, self.sensor_ph_wtorny.wartosc)
        
        if random.random() < 0.01:
            self.filtr.stopien_zatkania = min(100, self.filtr.stopien_zatkania + 0.5)
            
        przeplyw = self.slider_przeplyw.value() / 2.0
        
        if not self.zb_surowe.czy_pusty() and not self.zb_wstepny.czy_pelny():
            ilosc = self.zb_surowe.usun_ciecz(przeplyw*0.1)
            self.zb_wstepny.dodaj_ciecz(ilosc, self.zb_surowe.temperatura)
            self.pompa1.wlaczona = True
            self.rura1.ustaw_przeplyw(True)
        else:
            self.pompa1.wlaczona = False
            self.rura1.ustaw_przeplyw(False)
            
        if not self.zb_wstepny.czy_pusty() and not self.zb_bioreaktor.czy_pelny():
            ilosc = self.zb_wstepny.usun_ciecz(przeplyw * 0.1)
            efektywnosc = max(0.5, min(1.0, (self.zb_wstepny.temperatura - 15) / 20))
            self.zb_bioreaktor.dodaj_ciecz(ilosc * efektywnosc, self.zb_wstepny.temperatura)
            self.pompa2.wlaczona = True
            self.rura2.ustaw_przeplyw(True)
        else:
            self.pompa2.wlaczona = False
            self.rura2.ustaw_przeplyw(False)
            
        if self.zb_bioreaktor.poziom > 0.3:
            self.pompa_napow.wlaczona = True
            self.rura_napow.ustaw_przeplyw(True)
        else:
            self.pompa_napow.wlaczona = False
            self.rura_napow.ustaw_przeplyw(False)
            
        if self.zb_bioreaktor.aktualna_ilosc > 10 and not self.zb_wtorny.czy_pelny() and self.zb_bioreaktor.temperatura >= 25.0:
            ilosc = self.zb_bioreaktor.usun_ciecz(przeplyw * 0.1)
            # Przenoszenie pH z bioreaktora do osadnika wtórnego
            self.zb_wtorny.dodaj_ciecz(ilosc, self.zb_bioreaktor.temperatura)
            # Aktualizuj pH w osadniku wtórnym (średnia ważona)
            if self.zb_wtorny.aktualna_ilosc > ilosc:
                stara_wartosc = self.sensor_ph_wtorny.wartosc
                nowa_wartosc = self.sensor_ph_bioreaktor.wartosc
                stara_masa = self.zb_wtorny.aktualna_ilosc - ilosc
                nowa_masa = ilosc
                self.sensor_ph_wtorny.wartosc = (stara_masa * stara_wartosc + nowa_masa * nowa_wartosc) / (stara_masa + nowa_masa)
            
            self.pompa3.wlaczona = True
            self.rura3.ustaw_przeplyw(True)
        else:
            self.pompa3.wlaczona = False
            self.rura3.ustaw_przeplyw(False)
            
        #POMPA PH
        if (not self.zb_wtorny.czy_pusty() and not self.zb_czyste.czy_pelny() and 
            self.sensor_ph_wtorny.wartosc <= 8.0):
            wsp_filtra = max(0.1, 1.0 - self.filtr.stopien_zatkania / 200)
            ilosc = self.zb_wtorny.usun_ciecz(przeplyw * wsp_filtra)
            temp_po_filtrze = self.zb_wtorny.temperatura - 5 * (self.filtr.stopien_zatkania / 100)
            self.zb_czyste.dodaj_ciecz(ilosc, temp_po_filtrze)
            self.pompa4.wlaczona = True
            self.filtr.czy_pracuje = True
            self.rura4.ustaw_przeplyw(True)
        else:
            self.pompa4.wlaczona = False
            self.filtr.czy_pracuje = False
            self.rura4.ustaw_przeplyw(False)
            
        if self.zb_surowe.poziom < 0.3 and random.random() < 0.02:
            self.zb_surowe.dodaj_ciecz(30, 18.0)
            
        for zbiornik in self.zbiorniki:
            if zbiornik.aktualna_ilosc > 0:
                utrata = 0.01 if zbiornik.nazwa != "Bioreaktor" else 0.02
                zbiornik.temperatura -= utrata
                zbiornik.temperatura = max(10, zbiornik.temperatura)
        
        self.temp_label.setText(f"Temp bioreaktora: {self.zb_bioreaktor.temperatura:.1f}°C")
        
        status = "Status: System aktywny | "
        status += f"Tryb: {'AUTO' if self.auto_mode else 'MANUAL'} | "
        status += f"Filtr: {int(self.filtr.stopien_zatkania)}% | "
        status += f"Grzałka: {'ON' if self.grzalka.wlaczona else 'OFF'} ({self.grzalka.moc:.0f}%)"
        
        alarmy = []
        if any(sensor.czy_alarm() for sensor in self.sensory):
            alarmy.append("SENSORY")
        if self.filtr.stopien_zatkania > 80:
            alarmy.append("FILTR")
        if self.zb_surowe.czy_pelny():
            alarmy.append("PRZELEW")
        if self.zb_bioreaktor.temperatura < 21:
            alarmy.append("BIO-ZIMNO")
        elif self.zb_bioreaktor.temperatura > 25:
            alarmy.append("BIO-GORĄCO")
        if self.zb_bioreaktor.temperatura < 21  and self.zb_bioreaktor.aktualna_ilosc > 0:
            alarmy.append("ZIMNA WODA")
        #PH ALARM
        if self.zb_wtorny.aktualna_ilosc > 10 and self.sensor_ph_wtorny.wartosc > 8.0:
            alarmy.append(f"pH WTÓRNY: {self.sensor_ph_wtorny.wartosc:.1f}")
            
        if alarmy:
            status += f" | ALARM: {', '.join(alarmy)}"
            self.status_label.setStyleSheet("color: red; font-size: 14px; font-weight: bold;")
        else:
            status += " | Wszystko OK"
            self.status_label.setStyleSheet("color: green; font-size: 14px;")

        self.status_label.setText(status)
        self.slider_label.setText(f"Przepływ: {self.slider_przeplyw.value()/2.0:.1f} L/s")
        
        self.viz_widget.update()
        
    def start_symulacji(self):
        self.timer.start(100)
        self.status_label.setText("Status: Symulacja uruchomiona")
        
    def stop_symulacji(self):
        self.timer.stop()
        self.status_label.setText("Status: Symulacja zatrzymana")
        
    def reset_symulacji(self):
        self.czas_symulacji = 0
        
        self.zb_surowe.aktualna_ilosc = 80.0
        self.zb_surowe.temperatura = 18.0
        
        self.zb_wstepny.aktualna_ilosc = 0.0
        self.zb_wstepny.temperatura = 20.0
        
        self.zb_bioreaktor.aktualna_ilosc = 0.0
        self.zb_bioreaktor.temperatura = 25.0
        
        self.zb_wtorny.aktualna_ilosc = 0.0
        self.zb_wtorny.temperatura = 22.0
        
        self.zb_czyste.aktualna_ilosc = 0.0
        self.zb_czyste.temperatura = 20.0
        
        for zb in self.zbiorniki:
            zb.aktualizuj_poziom()
            
        # Resetuj pH w osadniku wtórnym
        self.sensor_ph_wtorny.wartosc = 11.0
        
        self.filtr.stopien_zatkania = 0
        self.grzalka.temperatura = 20.0
        self.grzalka.wlaczona = False
        self.grzalka.moc = 0
        
        for pompa in [self.pompa1, self.pompa2, self.pompa3, self.pompa4, self.pompa_napow]:
            pompa.wlaczona = False
            
        for rura in self.rury:
            rura.ustaw_przeplyw(False)
            
        self.viz_widget.update()
        
    def przelacz_tryb(self):
        self.auto_mode = not self.auto_mode
        self.slider_przeplyw.setEnabled(not self.auto_mode)
        
        if self.auto_mode:
            self.btn_auto.setText("AUTO/MANU (AUTO)")
        else:
            self.btn_auto.setText("AUTO/MANU (MANUAL)")
            self.status_label.setText("Status: Tryb manualny - użyj suwaków")

# ==================== URUCHOMIENIE ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OczyszczalniaScada()
    window.show()
    sys.exit(app.exec_())