# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")

import customtkinter as ctk
import yfinance as yf
import requests
import threading
import time
import sys
import os
import json
import datetime
import concurrent.futures
import webbrowser
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- TEMA VE ARAYÜZ AYARLARI ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- KABUK VE HAFIZA DOSYASI ---
HAFIZA_DOSYASI = "titan_finans_hafiza.json"

# --- 100% TÜRKÇE METİN SÖZLÜĞÜ ---
METINLER = {
    "baslik": "Titan Finans Ağ Geçidi - V18.0 | Vurgu Rengi, Alarm, Hafıza, Grafik & Çevirici",
    "logo": "TİTAN FİNANS\nULTIMATE V18",
    "canli_yayin": "Canlı Yayın (2 Sn)",
    "aninda_cek": "Anında Veri Çek",
    "durum_cevrimici": "Sistem: Çevrimiçi (Hafıza Aktif)",
    "durum_taraniyor": "Piyasalar ve Alarmlar Taranıyor...",
    "arama_placeholder": "🔍 Varlık Ara... (Örn: Dolar, Apple, Bitcoin, Altın, Türk Lirası)",
    "tab_dunya": "Dünya Para Birimleri",
    "tab_kuresel": "Küresel Hisseler",
    "tab_bist": "Borsa İstanbul (BIST)",
    "tab_kripto": "Kripto Varlıklar",
    "tab_emtia": "Mücevher, Maden & Emtia",
    "tab_portfoy": "💼 Portföyüm",
    "tab_alarmlar": "🚨 Fiyat Alarmları",
    "tab_cevirici": "🧮 Çevirici & Hesap",
    "col_varlik": "Varlık Adı",
    "col_fiyat": "Son Fiyat",
    "col_degisim": "Günlük Değişim",
    "col_islem": "İşlemler",
    "col_adet": "Adet",
    "col_maliyet": "Ort. Maliyet",
    "col_kar": "Kâr / Zarar",
    "btn_satin_al": "🛒 Al",
    "btn_alarm": "🔔 Alarm",
    "btn_mynet_ac": "🌐 Mynet",
    "btn_grafik": "📈 Grafik",
    "portfoy_deger": "Toplam Portföy Değeri:",
    "portfoy_kar": "Toplam Kâr/Zarar:",
    "modal_baslik": "Alış Emri",
    "modal_adet_txt": "Alınacak Adet/Miktar:",
    "modal_hata": "Lütfen geçerli bir sayı girin!",
    "modal_onay": "Alış Emrini Onayla",
    "alarm_baslik": "Fiyat Hedef Alarmı Kur",
    "alarm_hedef_txt": "Hedef Fiyat (USD / TL Cinsinden):",
    "alarm_olustur": "Alarmı Kaydet",
    "cevirici_baslik": "Gelişmiş Varlık ve Para Birimi Çevirici",
    "cevirici_miktar": "Çevrilecek Miktar:",
    "cevirici_kaynak": "Kaynak Varlık / Para Birimi:",
    "cevirici_hedef": "Hedef Varlık / Para Birimi:",
    "cevirici_hesapla": "Dönüşümü Gerçekleştir"
}

def t(anahtar):
    return METINLER.get(anahtar, anahtar)

# --- DEVASA DÖVİZ VE PARA BİRİMLERİ VERİTABANI ---
DUNYA_PARA_BIRIMLERI = {
    "Türk Lirası": "TRY",
    "ABD Doları": "USDTRY=X",
    "Euro": "EURTRY=X",
    "İngiliz Sterlini": "GBPTRY=X",
    "Japon Yeni": "JPYTRY=X",
    "İsviçre Frangı": "CHFTRY=X",
    "Kanada Doları": "CADTRY=X",
    "Avustralya Doları": "AUDTRY=X",
    "Çin Yuanı": "CNYTRY=X",
    "Rus Rublesi": "RUBTRY=X",
    "BAE Dirhemi": "AEDTRY=X",
    "Suudi Arabistan Riyali": "SARTRY=X",
    "Kuveyt Dinarı": "KWDTRY=X",
    "Katar Riyali": "QARTRY=X",
    "İsveç Kronu": "SEKTRY=X",
    "Norveç Kronu": "NOKTRY=X",
    "Danimarka Kronu": "DKKTRY=X",
    "Polonya Zlotisi": "PLNTRY=X",
    "Meksika Pesosu": "MXNTRY=X",
    "Güney Afrika Randı": "ZARTRY=X",
    "Brezilya Reali": "BRLTRY=X",
    "Hindistan Rupisi": "INRTRY=X",
    "Singapur Doları": "SGDTRY=X",
    "Hong Kong Doları": "HKDTRY=X",
    "Yeni Zelanda Doları": "NZDTRY=X",
    "Arjantin Pesosu": "ARSTRY=X",
    "Macar Forinti": "HUFTRY=X",
    "Çek Korunası": "CZKTRY=X",
    "Romanya Leyi": "RONTRY=X",
    "Bulgar Levası": "BGNTRY=X",
    "İsrail Şekeli": "ILSTRY=X",
    "Güney Kore Wonu": "KRWTRY=X",
    "Endonezya Rupiahı": "IDRTRY=X",
    "Malezya Ringgiti": "MYRTRY=X",
    "Filipin Pesosu": "PHPTRY=X",
    "Tayland Bahtı": "THBTRY=X",
    "Vietnam Dongu": "VNDTRY=X",
    "Şili Pesosu": "CLPTRY=X",
    "Kolombiya Pesosu": "COPTRY=X",
    "Mısır Lirası": "EGPTRY=X",
    "Pakistan Rupisi": "PKRTRY=X",
    "Ukrayna Grivnası": "UAHTRY=X"
}

# --- KÜRESEL HİSSELER ---
KURESEL_HISSELER = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Nvidia (NVDA)": "NVDA",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "Tesla (TSLA)": "TSLA",
    "Meta Platforms (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "Intel (INTC)": "INTC",
    "AMD (AMD)": "AMD",
    "Qualcomm (QCOM)": "QCOM",
    "Coca-Cola (KO)": "KO",
    "PepsiCo (PEP)": "PEP",
    "Walt Disney (DIS)": "DIS",
    "McDonald's (MCD)": "MCD",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "JPMorgan Chase (JPM)": "JPM",
    "Visa (V)": "V",
    "Mastercard (MA)": "MA"
}

# --- BORSA İSTANBUL (BİST) HİSSELERİ ---
BIST_HISSELERI = {
    "Türk Hava Yolları": "THYAO.IS",
    "Aselsan": "ASELS.IS",
    "Tüpraş": "TUPRS.IS",
    "Garanti BBVA": "GARAN.IS",
    "Koç Holding": "KCHOL.IS",
    "Şişecam": "SISE.IS",
    "Ereğli Demir Çelik": "EREGL.IS",
    "BIM Mağazalar": "BIMAS.IS",
    "Akbank": "AKBNK.IS",
    "Türkiye İş Bankası (C)": "ISCTR.IS",
    "Yapı ve Kredi Bankası": "YKBNK.IS",
    "Sabancı Holding": "SAHOL.IS",
    "Ford Otosan": "FROTO.IS",
    "SASA Polyester": "SASA.IS",
    "Hektaş": "HEKTS.IS",
    "Pegasus Hava Taşımacılığı": "PGSUS.IS",
    "Migros Ticaret": "MGROS.IS",
    "Petkim": "PETKM.IS",
    "Kardemir (D)": "KRDMD.IS",
    "Emlak Konut GYO": "EKGYO.IS"
}

# --- KRİPTO VARLIKLAR ---
KRIPTO_VARLIKLAR = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "Ripple (XRP)": "XRP-USD",
    "Dogecoin (DOGE)": "DOGE-USD",
    "Avalanche (AVAX)": "AVAX-USD",
    "Cardano (ADA)": "ADA-USD",
    "Chainlink (LINK)": "LINK-USD"
}

# --- MÜCEVHER, DEĞERLİ TAŞLAR VE EMTİALAR ---
EMTIALAR_MADENLER = {
    "Elmas (Özel Değerli Taş)": "ELMAS_OZEL",
    "Pırlanta (1 Karat)": "PIRLANTA_OZEL",
    "Zümrüt (Doğal Taş)": "ZUMRUT_OZEL",
    "Obsidiyen (Vulkanik Taş)": "OBSIDIYEN_OZEL",
    "Ons Altın": "GC=F",
    "Gümüş": "SI=F",
    "Platin": "PL=F",
    "Paladyum": "PA=F",
    "Brent Petrol": "BZ=F",
    "Bakır": "HG=F",
    "Doğalgaz": "NG=F"
}

class TitanFinansUltimate(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(t("baslik"))
        self.geometry("1520x880")
        self.minsize(1200, 750)
        
        self.protocol("WM_DELETE_WINDOW", self.guvenli_kapatma)
        self.uygulama_aktif = True  
        self.otomatik_yenile_acik = ctk.BooleanVar(value=True) 
        self.veri_cekiliyor = False 

        # Varsayılan Değerler
        self.nakit_bakiye_usd = 25000.0  
        self.portfoyum = {} 
        self.aktif_alarmlar = [] 
        self.usd_try_kuru = 34.0 
        
        # Hafızadan (JSON) Verileri Yükle
        self.hafizadan_yukle()

        self.ui_haritasi = {}
        self.liste_satirlari = []
        
        self.tum_varliklar = {}
        for kat in [DUNYA_PARA_BIRIMLERI, KURESEL_HISSELER, BIST_HISSELERI, KRIPTO_VARLIKLAR, EMTIALAR_MADENLER]:
            self.tum_varliklar.update(kat)

        self.arayuzu_insaa_et()
        self.saati_baslat()
        self.arka_plan_motorunu_baslat()

    def hafizaya_kaydet(self):
        veri = {
            "nakit": self.nakit_bakiye_usd,
            "portfoy": self.portfoyum,
            "alarmlar": self.aktif_alarmlar
        }
        try:
            with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
                json.dump(veri, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Kayıt hatası:", e)

    def hafizadan_yukle(self):
        if os.path.exists(HAFIZA_DOSYASI):
            try:
                with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                    veri = json.load(f)
                    self.nakit_bakiye_usd = veri.get("nakit", 25000.0)
                    self.portfoyum = veri.get("portfoy", {})
                    self.aktif_alarmlar = veri.get("alarmlar", [])
            except Exception as e:
                print("Okuma hatası:", e)

    def ui_kaydet(self, sembol, tur, bilesen_sozlugu):
        if sembol not in self.ui_haritasi:
            self.ui_haritasi[sembol] = []
        self.ui_haritasi[sembol].append({"tur": tur, "bilesenler": bilesen_sozlugu})

    def arayuzu_insaa_et(self):
        # 1. SOL KONTROL PANELİ
        self.sol_panel = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#14141c")
        self.sol_panel.pack(side="left", fill="y")

        self.logo_etiket = ctk.CTkLabel(self.sol_panel, text=t("logo"), font=ctk.CTkFont(size=18, weight="bold", family="Arial Black"), text_color="#00e676")
        self.logo_etiket.pack(pady=(25, 10), padx=20)
        
        self.saat_etiketi = ctk.CTkLabel(self.sol_panel, text="00:00:00", font=ctk.CTkFont(size=20, weight="bold"))
        self.saat_etiketi.pack(pady=(0, 15))

        # TEMA SEÇİM PANELİ
        tema_frame = ctk.CTkFrame(self.sol_panel, fg_color="#1c1c28")
        tema_frame.pack(pady=6, padx=20, fill="x")
        ctk.CTkLabel(tema_frame, text="Arayüz Teması:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10, pady=8)
        
        self.tema_secim_menu = ctk.CTkOptionMenu(tema_frame, values=["Koyu (Dark)", "Açık (Light)", "Sistem"], width=115, command=self.tema_degistir_fonksiyonu)
        self.tema_secim_menu.set("Koyu (Dark)")
        self.tema_secim_menu.pack(side="right", padx=10, pady=8)

        # ÖZEL VURGU RENGİ SEÇİCİ
        vurgu_frame = ctk.CTkFrame(self.sol_panel, fg_color="#1c1c28")
        vurgu_frame.pack(pady=6, padx=20, fill="x")
        ctk.CTkLabel(vurgu_frame, text="Özel Vurgu Rengi:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10, pady=8)
        
        self.vurgu_secim_menu = ctk.CTkOptionMenu(vurgu_frame, values=["Siber Yeşil", "Kripto Turuncusu", "Klasik Mavi", "Hacker Moru"], width=115, command=self.vurgu_rengini_degistir)
        self.vurgu_secim_menu.set("Siber Yeşil")
        self.vurgu_secim_menu.pack(side="right", padx=10, pady=8)

        # DİL SEÇİMİ
        dil_frame = ctk.CTkFrame(self.sol_panel, fg_color="#1c1c28")
        dil_frame.pack(pady=6, padx=20, fill="x")
        ctk.CTkLabel(dil_frame, text="Dil / Dil:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10, pady=8)
        
        self.dil_secim_menu = ctk.CTkOptionMenu(dil_frame, values=["Türkçe"], width=115)
        self.dil_secim_menu.set("Türkçe")
        self.dil_secim_menu.pack(side="right", padx=10, pady=8)

        self.oto_yenile_switch = ctk.CTkSwitch(
            self.sol_panel, text=t("canli_yayin"), variable=self.otomatik_yenile_acik,
            onvalue=True, offvalue=False, font=ctk.CTkFont(weight="bold"), progress_color="#00e676"
        )
        self.oto_yenile_switch.pack(pady=10, padx=20, fill="x")

        self.btn_yenile = ctk.CTkButton(self.sol_panel, text=t("aninda_cek"), command=self.manuel_yenile, height=40, font=ctk.CTkFont(weight="bold"))
        self.btn_yenile.pack(pady=8, padx=20, fill="x")

        # Cüzdan Paneli (JSON Kalıcı)
        self.cuzdan_bilgi_frame = ctk.CTkFrame(self.sol_panel, fg_color="#1c1c28")
        self.cuzdan_bilgi_frame.pack(pady=10, padx=20, fill="x")
        self.lbl_cuzdan = ctk.CTkLabel(self.cuzdan_bilgi_frame, text=f"Nakit: ${self.nakit_bakiye_usd:,.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00e676")
        self.lbl_cuzdan.pack(pady=10, padx=10)

        self.durum_etiketi = ctk.CTkLabel(self.sol_panel, text=t("durum_cevrimici"), text_color="#00e676", font=ctk.CTkFont(size=13))
        self.durum_etiketi.pack(side="bottom", pady=25)

        # 2. SAĞ ANA GÖVDE
        self.sag_govde = ctk.CTkFrame(self, corner_radius=0, fg_color="#1c1c24")
        self.sag_govde.pack(side="right", fill="both", expand=True)

        # ÜST ÖZET KARTLARI (Elmas çıkarıldı, Altın eklendi)
        self.ust_ozet_paneli = ctk.CTkFrame(self.sag_govde, fg_color="transparent")
        self.ust_ozet_paneli.pack(fill="x", padx=20, pady=(15, 0))

        ozet_verileri = [
            ("ABD Doları", "USDTRY=X", " TL"), ("Euro", "EURTRY=X", " TL"),
            ("Altın", "GC=F", " $"), ("Bitcoin", "BTC-USD", " $")
        ]

        for baslik, sembol, ek_metin in ozet_verileri:
            kart = ctk.CTkFrame(self.ust_ozet_paneli, corner_radius=12, fg_color="#2b2b36", height=90)
            kart.pack(side="left", fill="both", expand=True, padx=6)
            kart.pack_propagate(False)

            lbl_baslik = ctk.CTkLabel(kart, text=baslik, font=ctk.CTkFont(size=13, weight="bold"), text_color="#b0bec5")
            lbl_baslik.pack(anchor="w", padx=12, pady=(10, 0))

            lbl_fiyat = ctk.CTkLabel(kart, text="Yükleniyor...", font=ctk.CTkFont(size=18, weight="bold"))
            lbl_fiyat.pack(anchor="w", padx=12, pady=(2, 0))

            lbl_degisim = ctk.CTkLabel(kart, text="-%-", font=ctk.CTkFont(size=12, weight="bold"))
            lbl_degisim.pack(anchor="w", padx=12, pady=(0, 8))

            self.ui_kaydet(sembol, "kart", {"lbl_fiyat": lbl_fiyat, "lbl_degisim": lbl_degisim, "ek_metin": ek_metin})

        # Arama Çubuğu
        self.arama_cubugu = ctk.CTkEntry(self.sag_govde, placeholder_text=t("arama_placeholder"), height=40, font=ctk.CTkFont(size=14))
        self.arama_cubugu.pack(fill="x", padx=20, pady=(15, 10))
        self.arama_cubugu.bind("<KeyRelease>", self.arama_filtresi_uygula)

        # SEKMELER (Haberler sekmesi kaldırıldı)
        self.sekmeler = ctk.CTkTabview(self.sag_govde, corner_radius=10, segmented_button_selected_color="#1f538d", fg_color="#252530")
        self.sekmeler.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.kategori_sozlugu = {
            t("tab_dunya"): DUNYA_PARA_BIRIMLERI,
            t("tab_kuresel"): KURESEL_HISSELER,
            t("tab_bist"): BIST_HISSELERI,
            t("tab_kripto"): KRIPTO_VARLIKLAR,
            t("tab_emtia"): EMTIALAR_MADENLER
        }

        self.sekmeler.add(t("tab_portfoy"))
        self.portfoy_alani_olustur()

        self.sekmeler.add(t("tab_alarmlar"))
        self.alarmlar_alani_olustur()

        self.sekmeler.add(t("tab_cevirici"))
        self.cevirici_alani_olustur()

        for kat_adi in self.kategori_sozlugu.keys():
            self.sekmeler.add(kat_adi)
            self.tablo_basliklarini_ciz(kat_adi)
            self.satirlari_olustur(kat_adi)
            
        self.alarm_arayuzunu_yenile()
        self.portfoy_arayuzunu_yenile()

    def tema_degistir_fonksiyonu(self, secim):
        if "Koyu" in secim:
            ctk.set_appearance_mode("Dark")
        elif "Açık" in secim:
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("System")

    def vurgu_rengini_degistir(self, secim):
        try:
            renk_paleti = {
                "Siber Yeşil": {"ana": "#00e676", "buton": "#008C45", "hover": "#006432"},
                "Kripto Turuncusu": {"ana": "#ff9100", "buton": "#e65100", "hover": "#bf360c"},
                "Klasik Mavi": {"ana": "#1f538d", "buton": "#1f538d", "hover": "#143c66"},
                "Hacker Moru": {"ana": "#aa00ff", "buton": "#4a148c", "hover": "#311b92"}
            }
            p = renk_paleti.get(secim, renk_paleti["Siber Yeşil"])
            self.logo_etiket.configure(text_color=p["ana"])
            self.oto_yenile_switch.configure(progress_color=p["ana"])
            self.lbl_cuzdan.configure(text_color=p["ana"])
            self.durum_etiketi.configure(text_color=p["ana"])
            self.lbl_cevirici_sonuc.configure(text_color=p["ana"])
            print(f"Bilgi: Vurgu rengi başarıyla '{secim}' olarak güncellendi.")
        except Exception as e:
            print("Vurgu rengi değiştirme hatası:", e)

    def tablo_basliklarini_ciz(self, kategori):
        sekme_alani = self.sekmeler.tab(kategori)
        baslik_frame = ctk.CTkFrame(sekme_alani, fg_color="transparent")
        baslik_frame.pack(fill="x", padx=10, pady=5)
        
        font_b = ctk.CTkFont(size=13, weight="bold")
        ctk.CTkLabel(baslik_frame, text=t("col_varlik"), font=font_b, width=220, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text=t("col_fiyat"), font=font_b, width=120, anchor="e").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text=t("col_degisim"), font=font_b, width=110, anchor="e").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text=t("col_islem"), font=font_b, width=190, anchor="center").pack(side="left", padx=5)

    def satirlari_olustur(self, kategori_adi):
        sekme_alani = self.sekmeler.tab(kategori_adi)
        liste_alani = ctk.CTkScrollableFrame(sekme_alani, fg_color="transparent")
        liste_alani.pack(fill="both", expand=True)

        gercek_veri_sozlugu = self.kategori_sozlugu.get(kategori_adi, {})

        for isim, sembol in gercek_veri_sozlugu.items():
            satir_frame = ctk.CTkFrame(liste_alani, corner_radius=8, fg_color="#2b2b36")
            satir_frame.pack(fill="x", padx=10, pady=4)

            lbl_isim = ctk.CTkLabel(satir_frame, text=isim, width=220, anchor="w", font=ctk.CTkFont(size=13, weight="bold"))
            lbl_isim.pack(side="left", padx=10, pady=10)

            lbl_fiyat = ctk.CTkLabel(satir_frame, text="Yükleniyor...", width=120, anchor="e", font=ctk.CTkFont(size=14))
            lbl_fiyat.pack(side="left", padx=10)

            lbl_degisim = ctk.CTkLabel(satir_frame, text="-%-", width=110, anchor="e", font=ctk.CTkFont(size=14, weight="bold"))
            lbl_degisim.pack(side="left", padx=10)

            btn_grafik = ctk.CTkButton(satir_frame, text=t("btn_grafik"), width=70, fg_color="#4a148c", hover_color="#311b92",
                                      command=lambda i=isim, s=sembol: self.grafik_penceresi_ac(i, s))
            btn_grafik.pack(side="left", padx=3)

            btn_alarm = ctk.CTkButton(satir_frame, text=t("btn_alarm"), width=70, fg_color="#e65100", hover_color="#bf360c",
                                      command=lambda i=isim, s=sembol: self.alarm_kurma_penceresi_ac(i, s))
            btn_alarm.pack(side="left", padx=3)

            btn_mynet = ctk.CTkButton(satir_frame, text=t("btn_mynet_ac"), width=75, fg_color="#1f538d", hover_color="#143c66",
                                      command=lambda s=sembol: webbrowser.open("https://finans.mynet.com/"))
            btn_mynet.pack(side="left", padx=3)

            btn_al = ctk.CTkButton(satir_frame, text=t("btn_satin_al"), width=55, fg_color="#008C45", hover_color="#006432",
                                   command=lambda i=isim, s=sembol: self.gercek_satin_alma_penceresi_ac(i, s))
            btn_al.pack(side="left", padx=3)

            self.ui_kaydet(sembol, "liste", {"lbl_fiyat": lbl_fiyat, "lbl_degisim": lbl_degisim})
            self.liste_satirlari.append({"isim": isim, "frame": satir_frame})

    def portfoy_alani_olustur(self):
        sekme_alani = self.sekmeler.tab(t("tab_portfoy"))
        
        self.portfoy_ozet_frame = ctk.CTkFrame(sekme_alani, fg_color="#1a1a24", corner_radius=10)
        self.portfoy_ozet_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_toplam_deger = ctk.CTkLabel(self.portfoy_ozet_frame, text=f"{t('portfoy_deger')} $0.00", font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_toplam_deger.pack(side="left", padx=20, pady=12)
        
        self.lbl_toplam_kar = ctk.CTkLabel(self.portfoy_ozet_frame, text=f"{t('portfoy_kar')} $0.00", font=ctk.CTkFont(size=15, weight="bold"))
        self.lbl_toplam_kar.pack(side="right", padx=20, pady=12)

        baslik_frame = ctk.CTkFrame(sekme_alani, fg_color="transparent")
        baslik_frame.pack(fill="x", padx=10, pady=5)
        font_b = ctk.CTkFont(size=13, weight="bold")
        
        ctk.CTkLabel(baslik_frame, text=t("col_varlik"), font=font_b, width=220, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text=t("col_adet"), font=font_b, width=100, anchor="e").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text=t("col_maliyet"), font=font_b, width=120, anchor="e").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text=t("col_fiyat"), font=font_b, width=120, anchor="e").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text=t("col_kar"), font=font_b, width=130, anchor="e").pack(side="left", padx=10)

        self.portfoy_liste_alani = ctk.CTkScrollableFrame(sekme_alani, fg_color="transparent")
        self.portfoy_liste_alani.pack(fill="both", expand=True)

    def alarmlar_alani_olustur(self):
        sekme_alani = self.sekmeler.tab(t("tab_alarmlar"))
        
        ctk.CTkLabel(sekme_alani, text="Aktif Fiyat Alarmları Listesi ve Takibi", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00e676").pack(pady=15)
        
        baslik_frame = ctk.CTkFrame(sekme_alani, fg_color="transparent")
        baslik_frame.pack(fill="x", padx=10, pady=5)
        font_b = ctk.CTkFont(size=13, weight="bold")
        
        ctk.CTkLabel(baslik_frame, text="Varlık Adı", font=font_b, width=260, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text="Hedef Fiyat", font=font_b, width=150, anchor="e").pack(side="left", padx=10)
        ctk.CTkLabel(baslik_frame, text="İşlem", font=font_b, width=120, anchor="center").pack(side="left", padx=10)

        self.alarmlar_liste_alani = ctk.CTkScrollableFrame(sekme_alani, fg_color="transparent")
        self.alarmlar_liste_alani.pack(fill="both", expand=True, padx=10, pady=5)

    def alarm_kurma_penceresi_ac(self, isim, sembol):
        pencere = ctk.CTkToplevel(self)
        pencere.title(f"{t('alarm_baslik')}: {isim}")
        pencere.geometry("380x300")
        pencere.attributes("-topmost", True)
        pencere.grab_set()

        ctk.CTkLabel(pencere, text=f"{isim} için Alarm Kur", font=ctk.CTkFont(size=15, weight="bold"), text_color="#00e676").pack(pady=(20, 10))
        ctk.CTkLabel(pencere, text=t("alarm_hedef_txt"), font=ctk.CTkFont(size=12)).pack(pady=5)

        giris_hedef = ctk.CTkEntry(pencere, placeholder_text="0.00", justify="center", height=38, width=220)
        giris_hedef.pack(pady=5)

        hata_etiketi = ctk.CTkLabel(pencere, text="", text_color="red")
        hata_etiketi.pack(pady=5)

        def alarm_kaydet():
            try:
                hedef_str = giris_hedef.get().replace(",", ".")
                hedef_fiyat = float(hedef_str)
                if hedef_fiyat <= 0: raise ValueError

                self.aktif_alarmlar.append({"isim": isim, "sembol": sembol, "hedef": hedef_fiyat})
                self.hafizaya_kaydet()
                self.alarm_arayuzunu_yenile()
                pencere.destroy()
            except ValueError:
                hata_etiketi.configure(text=t("modal_hata"))

        ctk.CTkButton(pencere, text=t("alarm_olustur"), command=alarm_kaydet, fg_color="#e65100", hover_color="#bf360c", height=40, width=180).pack(pady=15)

    def alarm_arayuzunu_yenile(self):
        for widget in self.alarmlar_liste_alani.winfo_children():
            widget.destroy()

        for idx, alarm in enumerate(self.aktif_alarmlar):
            satir = ctk.CTkFrame(self.alarmlar_liste_alani, corner_radius=8, fg_color="#2b2b36")
            satir.pack(fill="x", padx=10, pady=4)

            ctk.CTkLabel(satir, text=alarm["isim"], width=260, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(satir, text=f"{alarm['hedef']:,.2f}", width=150, anchor="e", text_color="#00e676", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

            btn_sil = ctk.CTkButton(satir, text="❌ Kaldır", width=110, fg_color="#b71c1c", hover_color="#7f0000",
                                     command=lambda i=idx: self.alarm_sil(i))
            btn_sil.pack(side="left", padx=10)

    def alarm_sil(self, index):
        if 0 <= index < len(self.aktif_alarmlar):
            del self.aktif_alarmlar[index]
            self.hafizaya_kaydet()
            self.alarm_arayuzunu_yenile()

    def alarm_tetiklendi_bildir(self, alarm, guncel_fiyat):
        pencere = ctk.CTkToplevel(self)
        pencere.title("🚨 FİYAT ALARMI TETİKLENDİ!")
        pencere.geometry("400x220")
        pencere.attributes("-topmost", True)
        pencere.grab_set()

        ctk.CTkLabel(pencere, text="ALARM HEDEFİNE ULAŞILDI!", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ff5252").pack(pady=(20, 10))
        ctk.CTkLabel(pencere, text=f"{alarm['isim']} hedef fiyata ulaştı!\nHedef: {alarm['hedef']:,.2f} | Anlık: {guncel_fiyat:,.2f}", font=ctk.CTkFont(size=13), justify="center").pack(pady=10)
        
        ctk.CTkButton(pencere, text="Tamam", command=pencere.destroy, fg_color="#1f538d", height=38, width=120).pack(pady=15)

    def cevirici_alani_olustur(self):
        sekme_alani = self.sekmeler.tab(t("tab_cevirici"))
        
        frame = ctk.CTkFrame(sekme_alani, fg_color="#2b2b36", corner_radius=12)
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(frame, text=t("cevirici_baslik"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#00e676").pack(pady=25)

        varlik_isimleri = list(self.tum_varliklar.keys())

        ctk.CTkLabel(frame, text=t("cevirici_miktar"), font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        self.cevirici_input = ctk.CTkEntry(frame, width=280, height=40, justify="center", font=ctk.CTkFont(size=15))
        self.cevirici_input.insert(0, "1")
        self.cevirici_input.pack(pady=5)

        ctk.CTkLabel(frame, text=t("cevirici_kaynak"), font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(15, 2))
        self.cevirici_kaynak_menu = ctk.CTkOptionMenu(frame, values=varlik_isimleri, width=320, height=38)
        self.cevirici_kaynak_menu.pack(pady=5)
        if varlik_isimleri:
            self.cevirici_kaynak_menu.set(varlik_isimleri[0])

        ctk.CTkLabel(frame, text=t("cevirici_hedef"), font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(15, 2))
        self.cevirici_hedef_menu = ctk.CTkOptionMenu(frame, values=varlik_isimleri, width=320, height=38)
        self.cevirici_hedef_menu.pack(pady=5)
        if len(varlik_isimleri) > 1:
            self.cevirici_hedef_menu.set(varlik_isimleri[1])

        self.lbl_cevirici_sonuc = ctk.CTkLabel(frame, text="Sonuç: -", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00e676")
        self.lbl_cevirici_sonuc.pack(pady=25)

        ctk.CTkButton(frame, text=t("cevirici_hesapla"), command=self.hesapla_cevirici, fg_color="#1f538d", hover_color="#143c66", height=42, width=220, font=ctk.CTkFont(weight="bold")).pack(pady=10)

    def hesapla_cevirici(self):
        try:
            miktar_str = self.cevirici_input.get().replace(",", ".")
            miktar = float(miktar_str)
            kaynak_isim = self.cevirici_kaynak_menu.get()
            hedef_isim = self.cevirici_hedef_menu.get()

            kaynak_sembol = self.tum_varliklar.get(kaynak_isim)
            hedef_sembol = self.tum_varliklar.get(hedef_isim)

            kaynak_fiyat_usd = self.fiyat_al_usd_cinsinden(kaynak_sembol)
            hedef_fiyat_usd = self.fiyat_al_usd_cinsinden(hedef_sembol)

            if hedef_fiyat_usd == 0:
                self.lbl_cevirici_sonuc.configure(text="Hata: Hedef fiyat sıfır olamaz!")
                return

            toplam_usd = miktar * kaynak_fiyat_usd
            sonuc = toplam_usd / hedef_fiyat_usd

            self.lbl_cevirici_sonuc.configure(text=f"Sonuç: {sonuc:,.4f} {hedef_isim}")
        except ValueError:
            self.lbl_cevirici_sonuc.configure(text="Lütfen geçerli bir miktar girin!")
        except Exception as e:
            self.lbl_cevirici_sonuc.configure(text=f"Hesaplama Hatası: {e}")

    def fiyat_al_usd_cinsinden(self, sembol):
        if sembol == "TRY":
            return 1.0 / self.usd_try_kuru
        guncel, _ = self.tekil_veri_cek(sembol)
        if guncel is None:
            guncel = 100.0
        if "TRY" in sembol or "IS" in sembol:
            return guncel / self.usd_try_kuru
        return guncel

    def grafik_penceresi_ac(self, isim, sembol):
        pencere = ctk.CTkToplevel(self)
        pencere.title(f"{isim} - Fiyat Grafiği (Son 1 Ay)")
        pencere.geometry("750x480")
        pencere.attributes("-topmost", True)
        pencere.grab_set()

        try:
            if sembol == "TRY":
                tarihler = [datetime.date.today() - datetime.timedelta(days=i) for i in range(30, -1, -1)]
                fiyatlar = [1.0 for _ in range(31)]
            elif "_OZEL" in sembol:
                tarihler = [datetime.date.today() - datetime.timedelta(days=i) for i in range(30, -1, -1)]
                fiyatlar = [18500.0 + (i * 12) for i in range(31)]
            else:
                df = yf.Ticker(sembol).history(period="1mo")
                if df.empty:
                    raise Exception("Veri bulunamadı")
                tarihler = df.index
                fiyatlar = df['Close'].values
        except Exception:
            tarihler = [datetime.date.today() - datetime.timedelta(days=1), datetime.date.today()]
            fiyatlar = [100.0, 101.0]

        fig = Figure(figsize=(7, 4.5), dpi=100)
        fig.patch.set_facecolor('#1c1c24')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b36')
        ax.plot(tarihler, fiyatlar, color='#00e676', linewidth=2.2, marker='o', markersize=3)
        ax.set_title(f"{isim} - Son 1 Aylık Fiyat Hareketi", color='white', fontsize=13, fontweight='bold', pad=12)
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('#b0bec5')
        ax.spines['top'].set_color('#2b2b36')
        ax.spines['left'].set_color('#b0bec5')
        ax.spines['right'].set_color('#2b2b36')
        ax.grid(True, linestyle='--', alpha=0.3, color='#b0bec5')
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=pencere)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

    def gercek_satin_alma_penceresi_ac(self, isim, sembol):
        pencere = ctk.CTkToplevel(self)
        pencere.title(f"{t('modal_baslik')}: {isim}")
        pencere.geometry("420x380")
        pencere.attributes("-topmost", True)
        pencere.grab_set()

        ctk.CTkLabel(pencere, text=f"{isim} - Alım Ekranı", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        
        guncel_fiyat_usd = 1.0
        if sembol == "TRY":
            guncel_fiyat_usd = 1.0 / self.usd_try_kuru
        elif sembol in self.ui_haritasi:
            for b in self.ui_haritasi[sembol]:
                if b["tur"] == "liste":
                    val_str = b["bilesenler"]["lbl_fiyat"].cget("text").replace(",", "").replace("$", "").replace("TL", "").strip()
                    try:
                        fiyat_ham = float(val_str)
                        if "TRY" in sembol or "IS" in sembol:
                            guncel_fiyat_usd = fiyat_ham / self.usd_try_kuru
                        else:
                            guncel_fiyat_usd = fiyat_ham
                    except ValueError:
                        pass

        ctk.CTkLabel(pencere, text=f"Güncel Fiyat (USD): ${guncel_fiyat_usd:,.2f}", font=ctk.CTkFont(size=14), text_color="#00e676").pack(pady=5)
        ctk.CTkLabel(pencere, text=f"Kullanılabilir Nakit: ${self.nakit_bakiye_usd:,.2f}", font=ctk.CTkFont(size=13), text_color="#b0bec5").pack(pady=2)

        ctk.CTkLabel(pencere, text=t("modal_adet_txt"), font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
        giris_adet = ctk.CTkEntry(pencere, placeholder_text="0.00", justify="center", height=38)
        giris_adet.pack(pady=5)

        hata_etiketi = ctk.CTkLabel(pencere, text="", text_color="red")
        hata_etiketi.pack(pady=5)

        def islemi_gerceklestir():
            try:
                adet_str = giris_adet.get().replace(",", ".")
                adet = float(adet_str)
                if adet <= 0: raise ValueError
                
                toplam_maliyet_usd = adet * guncel_fiyat_usd

                if toplam_maliyet_usd > self.nakit_bakiye_usd:
                    hata_etiketi.configure(text="Yetersiz Bakiye!")
                    return

                self.nakit_bakiye_usd -= toplam_maliyet_usd
                self.lbl_cuzdan.configure(text=f"Nakit: ${self.nakit_bakiye_usd:,.2f}")

                if sembol in self.portfoyum:
                    eski_adet = self.portfoyum[sembol]["adet"]
                    eski_maliyet = self.portfoyum[sembol]["maliyet"]
                    yeni_toplam_adet = eski_adet + adet
                    yeni_maliyet = ((eski_adet * eski_maliyet) + (adet * guncel_fiyat_usd)) / yeni_toplam_adet
                    self.portfoyum[sembol]["adet"] = yeni_toplam_adet
                    self.portfoyum[sembol]["maliyet"] = yeni_maliyet
                else:
                    self.portfoyum[sembol] = {"isim": isim, "adet": adet, "maliyet": guncel_fiyat_usd}

                self.hafizaya_kaydet()
                self.portfoy_arayuzunu_yenile()
                pencere.destroy()
            except ValueError:
                hata_etiketi.configure(text=t("modal_hata"))

        ctk.CTkButton(pencere, text=t("modal_onay"), command=islemi_gerceklestir, fg_color="#008C45", hover_color="#006432", height=40).pack(pady=15)

    def portfoy_arayuzunu_yenile(self):
        for widget in self.portfoy_liste_alani.winfo_children():
            widget.destroy()
        
        for sembol in self.ui_haritasi.keys():
            self.ui_haritasi[sembol] = [b for b in self.ui_haritasi[sembol] if b["tur"] != "portfoy"]

        for sembol, veri in self.portfoyum.items():
            satir = ctk.CTkFrame(self.portfoy_liste_alani, corner_radius=8, fg_color="#2b2b36")
            satir.pack(fill="x", padx=10, pady=4)

            ctk.CTkLabel(satir, text=veri["isim"], width=220, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(satir, text=f"{veri['adet']}", width=100, anchor="e").pack(side="left", padx=10)
            
            maliyet_f = f"${veri['maliyet']:,.2f}"
            ctk.CTkLabel(satir, text=maliyet_f, width=120, anchor="e", text_color="#b0bec5").pack(side="left", padx=10)

            lbl_canli = ctk.CTkLabel(satir, text="...", width=120, anchor="e")
            lbl_canli.pack(side="left", padx=10)

            lbl_kar = ctk.CTkLabel(satir, text="-", width=130, anchor="e", font=ctk.CTkFont(weight="bold"))
            lbl_kar.pack(side="left", padx=10)

            self.ui_kaydet(sembol, "portfoy", {"lbl_canli": lbl_canli, "lbl_kar": lbl_kar, "adet": veri["adet"], "maliyet": veri["maliyet"]})

    def saati_baslat(self):
        if not self.uygulama_aktif: return
        self.saat_etiketi.configure(text=datetime.datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.saati_baslat)

    def arka_plan_motorunu_baslat(self):
        self.veri_thread = threading.Thread(target=self.veri_guncelleme_dongusu)
        self.veri_thread.daemon = True 
        self.veri_thread.start()

    def veri_guncelleme_dongusu(self):
        while self.uygulama_aktif:
            if self.otomatik_yenile_acik.get() and not self.veri_cekiliyor:
                self.verileri_internetten_cek()
            for _ in range(20):
                if not self.uygulama_aktif: break
                time.sleep(0.1)

    def manuel_yenile(self):
        if not self.veri_cekiliyor:
            threading.Thread(target=self.verileri_internetten_cek, daemon=True).start()

    def tekil_veri_cek(self, sembol):
        if sembol == "TRY":
            return 1.0, 1.0

        guvenli_yedekler = {
            "ELMAS_OZEL": (18500.0, 18400.0),
            "PIRLANTA_OZEL": (12500.0, 12450.0),
            "ZUMRUT_OZEL": (9800.0, 9750.0),
            "OBSIDIYEN_OZEL": (1250.0, 1240.0),
            "USDTRY=X": (34.0, 33.9), "EURTRY=X": (37.0, 36.8), "GBPTRY=X": (44.0, 43.8),
            "JPYTRY=X": (0.22, 0.22), "CHFTRY=X": (39.0, 38.8), "CADTRY=X": (24.0, 23.9),
            "AUDTRY=X": (22.5, 22.4), "CNYTRY=X": (4.7, 4.65), "RUBTRY=X": (0.37, 0.36),
            "AEDTRY=X": (9.25, 9.2), "SARTRY=X": (9.05, 9.0), "KWDTRY=X": (110.5, 110.0),
            "QARTRY=X": (9.3, 9.25), "SEKTRY=X": (3.25, 3.2), "NOKTRY=X": (3.15, 3.1),
            "DKKTRY=X": (4.95, 4.9), "PLNTRY=X": (8.5, 8.45), "MXNTRY=X": (1.85, 1.83),
            "ZARTRY=X": (1.9, 1.88), "BRLTRY=X": (6.0, 5.95), "INRTRY=X": (0.40, 0.39),
            "SGDTRY=X": (26.0, 25.8), "HKDTRY=X": (4.35, 4.33), "NZDTRY=X": (20.5, 20.4),
            "ARSTRY=X": (0.035, 0.034), "HUFTRY=X": (0.092, 0.091), "CZKTRY=X": (1.5, 1.48),
            "RONTRY=X": (7.4, 7.35), "BGNTRY=X": (18.9, 18.8), "HRKTRY=X": (5.2, 5.15),
            "ILSTRY=X": (9.1, 9.05), "KRWTRY=X": (0.025, 0.024), "IDRTRY=X": (0.0021, 0.0020),
            "MYRTRY=X": (7.8, 7.75), "PHPTRY=X": (0.58, 0.57), "THBTRY=X": (0.98, 0.97),
            "VNDTRY=X": (0.0013, 0.0012), "CLPTRY=X": (0.036, 0.035), "COPTRY=X": (0.0085, 0.0084),
            "EGPTRY=X": (0.70, 0.69), "PKRTRY=X": (0.12, 0.119), "UAHTRY=X": (0.82, 0.81),
            "AAPL": (220.0, 218.0), "MSFT": (430.0, 425.0), "NVDA": (120.0, 118.0),
            "AMZN": (185.0, 183.0), "GOOGL": (175.0, 173.0), "TSLA": (240.0, 235.0),
            "META": (490.0, 485.0), "NFLX": (670.0, 665.0), "INTC": (22.0, 21.5),
            "AMD": (155.0, 152.0), "QCOM": (180.0, 178.0), "KO": (68.0, 67.5),
            "PEP": (172.0, 170.0), "DIS": (95.0, 94.0), "MCD": (290.0, 288.0),
            "BRK-B": (430.0, 428.0), "JPM": (210.0, 208.0), "V": (275.0, 272.0), "MA": (460.0, 455.0),
            "THYAO.IS": (310.0, 305.0), "ASELS.IS": (65.0, 64.0), "TUPRS.IS": (160.0, 158.0),
            "GARAN.IS": (105.0, 104.0), "KCHOL.IS": (205.0, 202.0), "SISE.IS": (52.0, 51.5),
            "EREGL.IS": (50.0, 49.5), "BIMAS.IS": (480.0, 475.0), "AKBNK.IS": (58.0, 57.0),
            "ISCTR.IS": (13.5, 13.2), "YKBNK.IS": (28.0, 27.5), "SAHOL.IS": (88.0, 87.0),
            "FROTO.IS": (1150.0, 1140.0), "SASA.IS": (4.2, 4.1), "HEKTS.IS": (1.45, 1.42),
            "PGSUS.IS": (210.0, 205.0), "MGROS.IS": (510.0, 500.0), "PETKM.IS": (21.5, 21.0),
            "KRDMD.IS": (25.0, 24.5), "EKGYO.IS": (11.0, 10.8),
            "BTC-USD": (65000.0, 64000.0), "ETH-USD": (3500.0, 3450.0), "SOL-USD": (150.0, 145.0),
            "XRP-USD": (0.55, 0.54), "DOGE-USD": (0.12, 0.115), "AVAX-USD": (25.0, 24.5),
            "ADA-USD": (0.40, 0.39), "LINK-USD": (14.0, 13.5),
            "GC=F": (2450.0, 2430.0), "SI=F": (28.5, 28.0), "PL=F": (1000.0, 990.0),
            "PA=F": (950.0, 940.0), "BZ=F": (80.0, 79.0), "HG=F": (4.1, 4.0), "NG=F": (2.2, 2.1)
        }

        if sembol in guvenli_yedekler and "_OZEL" in sembol:
            return guvenli_yedekler[sembol]

        try:
            h = yf.Ticker(sembol).history(period="5d")
            if not h.empty and len(h) >= 1:
                c = h['Close'].dropna()
                if len(c) >= 2: return float(c.iloc[-1]), float(c.iloc[-2])
                elif len(c) == 1: return float(c.iloc[-1]), float(c.iloc[-1])
        except Exception:
            pass

        if sembol.endswith("TRY=X"):
            baz = sembol.replace("TRY=X", "")
            for alt in [f"{baz}USD=X", f"{baz}=X"]:
                try:
                    h = yf.Ticker(alt).history(period="5d")
                    if not h.empty and len(h) >= 1:
                        c = h['Close'].dropna()
                        val = float(c.iloc[-1])
                        prev = float(c.iloc[-2]) if len(c) >= 2 else val
                        return val * self.usd_try_kuru, prev * self.usd_try_kuru
                except:
                    pass

        if sembol in guvenli_yedekler:
            return guvenli_yedekler[sembol]

        return 100.0, 99.0

    def verileri_internetten_cek(self):
        if not self.uygulama_aktif: return
        self.veri_cekiliyor = True
        self.durum_yazdir(t("durum_taraniyor"), "yellow")

        sembol_listesi = list(self.ui_haritasi.keys())
        toplam_portfoy_degeri_usd = 0.0
        toplam_portfoy_kar_usd = 0.0

        try:
            kur_h = yf.Ticker("USDTRY=X").history(period="2d")
            if not kur_h.empty:
                self.usd_try_kuru = float(kur_h['Close'].iloc[-1])
        except:
            pass

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            gelecek_veriler = {executor.submit(self.tekil_veri_cek, sembol): sembol for sembol in sembol_listesi}
            
            for gelecek in concurrent.futures.as_completed(gelecek_veriler):
                if not self.uygulama_aktif: break
                sembol = gelecek_veriler[gelecek]
                guncel, onceki = gelecek.result()
                
                if guncel is not None:
                    degisim = ((guncel - onceki) / onceki) * 100 if onceki else 0.0
                    self.after(0, self.arayuz_basarili_guncelle, sembol, guncel, degisim)
                    
                    for alarm in list(self.aktif_alarmlar):
                        if alarm["sembol"] == sembol:
                            if guncel >= alarm["hedef"]:
                                self.after(0, lambda a=alarm, f=guncel: self.alarm_tetiklendi_bildir(a, f))
                                self.aktif_alarmlar.remove(alarm)
                                self.after(0, self.alarm_arayuzunu_yenile)
                                self.hafizaya_kaydet()

                    if sembol in self.portfoyum:
                        adet = self.portfoyum[sembol]["adet"]
                        maliyet = self.portfoyum[sembol]["maliyet"]
                        fiyat_usd = (guncel / self.usd_try_kuru) if (sembol == "TRY" or "TRY" in sembol or "IS" in sembol) else guncel
                        
                        anlik_tutar_usd = adet * fiyat_usd
                        kar_zarar_usd = anlik_tutar_usd - (adet * maliyet)
                        toplam_portfoy_degeri_usd += anlik_tutar_usd
                        toplam_portfoy_kar_usd += kar_zarar_usd
        
        if self.uygulama_aktif:
            self.durum_yazdir(t("durum_cevrimici"), "#00e676")
            self.after(0, self.portfoy_ozet_guncelle, toplam_portfoy_degeri_usd, toplam_portfoy_kar_usd)
            self.veri_cekiliyor = False

    def arayuz_basarili_guncelle(self, sembol, fiyat, degisim):
        if sembol not in self.ui_haritasi: return
        
        fiyat_format = f"{fiyat:,.2f}" if fiyat >= 10 else f"{fiyat:,.4f}"
        degisim_format = f"{degisim:+.2f}%"
        renk = "#00FF7F" if degisim > 0 else "#FF4040" if degisim < 0 else "#b0bec5"

        for b in self.ui_haritasi[sembol]:
            if b["tur"] == "liste":
                b["bilesenler"]["lbl_fiyat"].configure(text=fiyat_format, text_color=renk)
                b["bilesenler"]["lbl_degisim"].configure(text=degisim_format, text_color=renk)
            
            elif b["tur"] == "kart":
                ek = b["bilesenler"].get("ek_metin", "")
                b["bilesenler"]["lbl_fiyat"].configure(text=fiyat_format + ek, text_color="#ffffff")
                b["bilesenler"]["lbl_degisim"].configure(text=degisim_format, text_color=renk)

            elif b["tur"] == "portfoy":
                adet = b["bilesenler"]["adet"]
                maliyet = b["bilesenler"]["maliyet"]
                fiyat_usd = (fiyat / self.usd_try_kuru) if (sembol == "TRY" or "TRY" in sembol or "IS" in sembol) else fiyat
                
                anlik_tutar = adet * fiyat_usd
                toplam_maliyet = adet * maliyet
                kar_zarar = anlik_tutar - toplam_maliyet
                
                b["bilesenler"]["lbl_canli"].configure(text=f"${fiyat_usd:,.2f}", text_color="#ffffff")
                kar_renk = "#00FF7F" if kar_zarar > 0 else "#FF4040" if kar_zarar < 0 else "#b0bec5"
                b["bilesenler"]["lbl_kar"].configure(text=f"${kar_zarar:+,.2f}", text_color=kar_renk)

    def portfoy_ozet_guncelle(self, toplam_deger, toplam_kar):
        self.lbl_toplam_deger.configure(text=f"{t('portfoy_deger')} ${toplam_deger:,.2f}")
        kar_renk = "#00FF7F" if toplam_kar > 0 else "#FF4040" if toplam_kar < 0 else "#ffffff"
        self.lbl_toplam_kar.configure(text=f"{t('portfoy_kar')} ${toplam_kar:+,.2f}", text_color=kar_renk)

    def arama_filtresi_uygula(self, event):
        arama = self.arama_cubugu.get().lower()
        for satir in self.liste_satirlari:
            if arama in satir["isim"].lower():
                satir["frame"].pack(fill="x", padx=10, pady=4)
            else:
                satir["frame"].pack_forget()

    def durum_yazdir(self, mesaj, renk):
        self.durum_etiketi.configure(text=mesaj, text_color=renk)

    def guvenli_kapatma(self):
        self.uygulama_aktif = False 
        self.hafizaya_kaydet()
        self.destroy() 
        os._exit(0)

if __name__ == "__main__":
    app = TitanFinansUltimate()
    app.mainloop()
