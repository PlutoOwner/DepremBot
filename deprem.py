import requests
from bs4 import BeautifulSoup
import asyncio
import time
from pyrogram import Client, filters, idle
from datetime import datetime
from pyrogram.types import Message

# Telegram API bilgileri
api_id = 163786 # api id al gir
api_hash = "544d9e338c852"  # api hash al gir
bot_token = "7215004208:AAG-60htyqPeYjihDRF-3-GXRY" # Bot tokeni yaz
sohbet_id = -1002034665535 # hangi gruba mesaj gidecekse o grubun id
session_name = "DepremBot"  # oynama bura ile gundi

# Bot oluşturuluyor
bot = Client(
    session_name,
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)



son_deprem_zamani = None

    
    
def konumu_temizle(konum_raw):
    parcalar = konum_raw.split()
    # Baştaki -.- veya benzeri anlamsız kısımlar
    if parcalar and not any(c.isalpha() for c in parcalar[0]):
        parcalar = parcalar[1:]
    # Sondaki 'İlksel' gibi etiketleri çıkar
    if parcalar and "ilksel" and "Ýlksel" in parcalar[-1].lower():
        parcalar = parcalar[:-1]
    return " ".join(parcalar)



# Kandilli web sitesinden son deprem verisini çek keke
def son_depremi_getir():
    url = "http://www.koeri.boun.edu.tr/scripts/lst0.asp"
    yanit = requests.get(url)
    sayfa = BeautifulSoup(yanit.text, "html.parser")
    pre = sayfa.find("pre")
    if not pre:
        return None
    satirlar = pre.text.strip().split("\n")[6:]
    if not satirlar:
        return None
    son_satir = satirlar[0]
    parcalar = son_satir.split()
    if len(parcalar) < 7:
        return None
    return {
        "zaman": f"{parcalar[0]} {parcalar[1]}",
        "enlem": parcalar[2],
        "boylam": parcalar[3],
        "derinlik": parcalar[4],
        "buyukluk": parcalar[6],
        "konum": konumu_temizle(" ".join(parcalar[7:]))

    }







# Deprem kontrol döngüsü
async def deprem_kontrol_dongusu():
    global son_deprem_zamani
    while True:
        try:
            deprem = son_depremi_getir()
            if deprem and deprem["zaman"] != son_deprem_zamani:
                son_deprem_zamani = deprem["zaman"]
                buyukluk = float(deprem["buyukluk"])
                tarih_saat = datetime.strptime(deprem["zaman"], "%Y.%m.%d %H:%M:%S")
                tarih = tarih_saat.strftime("%d.%m.%Y")
                saat = tarih_saat.strftime("%H:%M:%S")
                mesaj = (
                    f"⚠️#DEPREM\n\n"
                    f"📍 Yer: {konumu_temizle(deprem['konum'])}\n"
                    f"📅 Tarih: {tarih}\n"
                    f"⏰ Saat: {saat}\n"
                    f"🚧 Derinlik: {deprem['derinlik']} km\n"
                    f"🚨 Büyüklük: {deprem['buyukluk']}"
                )

                min_buyukluk = 3.5  # Depremin min. büyüklüğü zırt pırt göndermesin
                if buyukluk >= min_buyukluk:
                    try:
                        await bot.send_message(sohbet_id, mesaj)
                    except Exception as hata:
                        print(f"{sohbet_id} gönderilemedi: {hata}")
        except Exception as hata:
            print("Kontrol döngüsünde hata:", hata)
        time.sleep(60)  # 1 dakika bekle

# oğlum lokum getir bura @AnonimYazar
async def main():
    print("Bot başlatılıyor...")
    await bot.start()
    print("Bot başlatıldı... ✅")
    asyncio.create_task(deprem_kontrol_dongusu())
    await idle()




if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print("Bot Durdu...") # allahu akbar bum @AnonimYazar