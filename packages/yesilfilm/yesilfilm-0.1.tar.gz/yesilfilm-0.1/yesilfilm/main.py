import webbrowser

# Filmleri kategorilere ayırarak bir sözlükte tanımlıyoruz
filmler = {
    1: {"kategori": "Hababam Sınıfı Serisi", "isim": "Hababam Sınıfı", "url": "https://hababamsinifi.com/film1"},
    2: {"kategori": "Hababam Sınıfı Serisi", "isim": "Hababam Sınıfı Sınıfta Kaldı", "url": "https://hababamsinifi.com/film2"},
    3: {"kategori": "Hababam Sınıfı Serisi", "isim": "Hababam Sınıfı Uyanıyor", "url": "https://hababamsinifi.com/film3"},
    4: {"kategori": "Hababam Sınıfı Serisi", "isim": "Hababam Sınıfı Tatilde", "url": "https://hababamsinifi.com/film4"},
    
    5: {"kategori": "Kemal Sunal Filmleri", "isim": "Süt Kardeşler", "url": "https://kemalsunal.com/sutkardesler"},
    6: {"kategori": "Kemal Sunal Filmleri", "isim": "Tosun Paşa", "url": "https://kemalsunal.com/tosunpasa"},
    7: {"kategori": "Kemal Sunal Filmleri", "isim": "Şaban Oğlu Şaban", "url": "https://kemalsunal.com/sabanoglusaban"},
    8: {"kategori": "Kemal Sunal Filmleri", "isim": "Kibar Feyzo", "url": "https://kemalsunal.com/kibarfeyzo"},
    9: {"kategori": "Kemal Sunal Filmleri", "isim": "Davaro", "url": "https://kemalsunal.com/davaro"},
    10: {"kategori": "Kemal Sunal Filmleri", "isim": "Kapıcılar Kralı", "url": "https://kemalsunal.com/kapicilarkrali"},
    11: {"kategori": "Kemal Sunal Filmleri", "isim": "Zübük", "url": "https://kemalsunal.com/zubuk"},
    12: {"kategori": "Kemal Sunal Filmleri", "isim": "Doktor Civanım", "url": "https://kemalsunal.com/doktorcivanim"},
    
    13: {"kategori": "Türkan Şoray Filmleri", "isim": "Selvi Boylum Al Yazmalım", "url": "https://turkansoray.com/selviboylum"},
    14: {"kategori": "Türkan Şoray Filmleri", "isim": "Dila Hanım", "url": "https://turkansoray.com/dilahanim"},
    15: {"kategori": "Türkan Şoray Filmleri", "isim": "Sultan", "url": "https://turkansoray.com/sultan"},
    16: {"kategori": "Türkan Şoray Filmleri", "isim": "Acı Hayat", "url": "https://turkansoray.com/acihayat"},
    17: {"kategori": "Türkan Şoray Filmleri", "isim": "Vesikalı Yarim", "url": "https://turkansoray.com/vesikalayarim"},
    18: {"kategori": "Türkan Şoray Filmleri", "isim": "Köyden İndim Şehire", "url": "https://turkansoray.com/koydenindimsehire"},
    
    19: {"kategori": "Şener Şen Filmleri", "isim": "Züğürt Ağa", "url": "https://senersen.com/zugurtağa"},
    20: {"kategori": "Şener Şen Filmleri", "isim": "Eşkıya", "url": "https://senersen.com/eskıya"},
    21: {"kategori": "Şener Şen Filmleri", "isim": "Davaro", "url": "https://senersen.com/davaro"},
    22: {"kategori": "Şener Şen Filmleri", "isim": "Kibar Feyzo", "url": "https://senersen.com/kibarfeyzo"},
    23: {"kategori": "Şener Şen Filmleri", "isim": "Çiçek Abbas", "url": "https://senersen.com/cicekabbas"},
    24: {"kategori": "Şener Şen Filmleri", "isim": "Şalvar Davası", "url": "https://senersen.com/salvardavasi"},
    25: {"kategori": "Şener Şen Filmleri", "isim": "Muhsin Bey", "url": "https://senersen.com/muhsinbey"},
    
    26: {"kategori": "Diğer Filmler", "isim": "Neşeli Günler", "url": "https://yesilcam.com/neseligunler"},
    27: {"kategori": "Diğer Filmler", "isim": "Mavi Boncuk", "url": "https://yesilcam.com/maviboncuk"},
    28: {"kategori": "Diğer Filmler", "isim": "Gülen Gözler", "url": "https://yesilcam.com/gulengozler"},
    29: {"kategori": "Diğer Filmler", "isim": "Yedi Bela Hüsnü", "url": "https://yesilcam.com/yedibelahusnu"},
    30: {"kategori": "Diğer Filmler", "isim": "Banker Bilo", "url": "https://yesilcam.com/bankerbilo"},
}

# Filmleri listeleyelim
print("Yeşilçam Filmleri:")
print("------------------")

son_kategori = None
for numara, film in filmler.items():
    if film['kategori'] != son_kategori:
        if son_kategori is not None:
            print()  # Kategoriler arasında boşluk ekler
        son_kategori = film['kategori']
    print(f"{numara}. {film['kategori']} - {film['isim']}")

# Kullanıcıdan bir seçim yapmasını istiyoruz
secim = int(input("\nLütfen bir film numarası girin: "))

# Seçilen filmi açıyoruz
if secim in filmler:
    secilen_film = filmler[secim]
    print(f"\nSeçilen Film: {secilen_film['isim']}")
    webbrowser.open(secilen_film['url'])
else:
    print("Geçersiz seçim!")