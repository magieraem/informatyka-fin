import psychopy
from psychopy import visual, core, event, gui, sound
import pandas as pd
import csv

# Wczytywanie danych bodźców
df_trening = pd.read_csv("treningowestimuli.csv", sep=";")
df_eksperyment = pd.read_csv("eksperymentalnestimuli.csv", sep=";")

# Zbieranie informacji o uczestniku
info = {"ID": "", "Wiek": "", "Płeć": ["Kobieta", "Mężczyzna", "Inna"]}
dialog = gui.DlgFromDict(dictionary=info, title="Dane osoby badanej")
if not dialog.OK:
    core.quit()

# Tworzenie pliku CSV do zapisywania wyników
plik_wynikowy = f"uczestnik_{info['ID']}.csv"
with open(plik_wynikowy, mode='w', newline='') as plik:
    writer = csv.writer(plik)
    writer.writerow(["Próba", "Słowo1", "Słowo2", "Relacja", "CzasOdpowiedzi", "Poprawność", "Część", "Wiek", "Płeć", "InformacjaZwrotna"])

# Funkcja do wyświetlania tekstu
def wyswietl_tekst(okno, glowny_tekst, dolny_tekst=None):
    tekst_instrukcji = visual.TextStim(okno, text=glowny_tekst, color="black", wrapWidth=1.2, pos=(0, 0.2))
    tekst_instrukcji.draw()
    if dolny_tekst:
        dolny_tekst_stim = visual.TextStim(okno, text=dolny_tekst, color="black", pos=(0, -0.8))
        dolny_tekst_stim.draw()
    okno.flip()
    event.waitKeys(keyList=["space"])

# Główna funkcja procedury
def procedura(df, liczba_trial, okno, trening=False, muzyka=None, czesc=None):
    df = df.sample(n=liczba_trial).reset_index(drop=True)
    liczba_poprawnych_odp = 0
    if muzyka:
        muzyka.play()

    for numer_proby, wiersz in df.iterrows():
        if numer_proby == liczba_trial:
            break

        # Wyświetlanie punktu fiksacji
        fiksacja = visual.TextStim(okno, text='+', color=(-1, -1, -1))
        fiksacja.draw()
        okno.flip()
        core.wait(0.8)

        # Wyświetlanie pary słów
        para_slow = f"{wiersz['Slowo1']} \n {wiersz['Slowo2']}"
        bodziec_slow = visual.TextStim(okno, text=para_slow, color=(-1, -1, -1), pos=(0.0, 0.0))

        zegar = core.Clock()
        okno.callOnFlip(zegar.reset)
        okno.callOnFlip(event.clearEvents, eventType='keyboard')
        bodziec_slow.draw()
        okno.flip()

        # Zbieranie odpowiedzi
        odpowiedz = event.waitKeys(maxWait=3, keyList=['m', 'z'], timeStamped=zegar)

        if odpowiedz:
            klawisz, czas_reakcji = odpowiedz[0]
        else:
            klawisz, czas_reakcji = None, None

        # Określenie poprawności odpowiedzi
        tekst_relacji = wiersz['Relacja']
        poprawna = (klawisz == 'm' and wiersz['Relacja'] in ['Powiązane', 'Niepowiązane']) or (klawisz == 'z' and wiersz['Relacja'] == 'Nie-słowo')

        if klawisz is None:
            poprawna = -1
        else:
            poprawna = 1 if poprawna else 0

        if poprawna == 1:
            liczba_poprawnych_odp += 1

        # Informacja zwrotna w sesji treningowej
        informacja_zwrotna = ""
        if trening:
            if klawisz:
                informacja_zwrotna = "poprawnie" if poprawna else "odpowiedź niepoprawna"
            else:
                informacja_zwrotna = "odpowiedź niepoprawna lub udzielona za wolno"

            feedback_stim = visual.TextStim(okno, text=informacja_zwrotna, color=(-1, -1, -1))
            feedback_stim.draw()
            okno.flip()
            core.wait(2)
            okno.flip()
            core.wait(0.8)

        # Zapisywanie odpowiedzi do pliku CSV
        with open(plik_wynikowy, mode='a', newline='') as plik:
            pisarz = csv.writer(plik)
            pisarz.writerow([numer_proby, wiersz['Slowo1'], wiersz['Slowo2'], tekst_relacji, czas_reakcji, poprawna, czesc if not trening else "trening", info['Wiek'], info['Płeć'], informacja_zwrotna if trening else ""])

        okno.flip()
        core.wait(0.8)

    if muzyka:
        muzyka.stop()

    # Jeśli sesja treningowa była nieudana, powtórz instrukcje
    if trening and liczba_poprawnych_odp < liczba_probek // 2:
        dodatkowa_instrukcja = (
            "Wydaje się, że miałeś/aś problem z instrukcją. "
            "Jeśli oba słowa są prawdziwymi polskimi słowami, naciśnij na klawiaturze „m”. "
            "Jeśli jeden lub oba słowa są słowami bezsensownymi, naciśnij na klawiaturze „z”."
            "\n\nNaciśnij spację, aby ponownie przeczytać instrukcje."
        )
        wyswietl_tekst(okno, dodatkowa_instrukcja)
        for instrukcja in instrukcje:
            wyswietl_tekst(okno, instrukcja, dolny_tekst)

# Teksty instrukcji
instrukcje = [
    "W tym zadaniu, które zaraz zobaczysz na ekranie pojawią się jednocześnie dwa słowa. Twoim zadaniem jest ocenić, czy słowa są słowami prawdziwymi czy bezsensownymi. Jeśli oba słowa są prawdziwymi polskimi słowami, naciśnij na klawiaturze „m”. Jeśli jeden lub oba słowa są słowami bezsensownymi, naciśnij na klawiaturze „z”.",
    "Przykłady poprawnych zestawów słów (takich, przy których należy kliknąć „m”): WIOSNA - WIATR. Przykłady niepoprawnych zestawów słów (takich, przy których należy kliknąć „z”): WIOSNA - UZYLE lub AGWITK - HATOPS. W niektórych częściach badania będziesz słuchał/a muzyki. Prosimy o nie zmienianie jej głośności - to część eksperymentu.",
    "Przed rozpoczęciem sesji eksperymentalnej, będziesz poddany krótkiej sesji treningowej, która pomoże Ci zrozumieć zadanie. W trakcie tej sesji treningowej otrzymasz informację po każdej udzielonej odpowiedzi, czy była poprawna. Postaraj się odpowiadać poprawnie i szybko, ponieważ czas Twojej reakcji będzie mierzony."
]
dolny_tekst = "[Naciśnij spację, aby przejść dalej]"

# Otwieranie okna
okno = visual.Window([1280, 720], color="#F5F5F5", monitor="testMonitor", units="norm", fullscr=True)
okno.refreshThreshold = 1 / 60.0  # Ustawienie FPS na 60

# Wczytywanie dźwięków
muz_bez_slow = sound.Sound("bezslow.wav")
muz_slowa = sound.Sound("zeslowamip.wav")

# Wyświetlanie instrukcji
for instrukcja in instrukcje:
    wyswietl_tekst(okno, instrukcja, dolny_tekst)

# Sesja treningowa
procedura(df_trening, 15, okno, trening=True)

# Sesja eksperymentalna
wyswietl_tekst(okno, "Zaraz rozpocznie się sesja eksperymentalna. Pamiętaj, oceniasz czy zestawy słów są prawdziwe i dla takich klikasz klawisz „m” a dla bezsensowych klikasz klawisz „z”. Odpowiadaj poprawnie i staraj się robić to jak najszybciej.", "Naciśnij spację, aby rozpocząć.")

# Części eksperymentalne
wyswietl_tekst(okno, "Sesja eksperymentalna - Część 1", "Naciśnij spację, aby rozpocząć")
procedura(df_eksperyment, 90, okno, muzyka=muz_bez_slow, czesc=1)
wyswietl_tekst(okno, "Ta część dobiegła końca, to chwila na moment odpoczynku.\nGdy będziesz gotowy/a kliknij spację, by kontynuować")

wyswietl_tekst(okno, "Sesja eksperymentalna - Część 2", "Naciśnij spację, aby rozpocząć")
procedura(df_eksperyment, 90, okno, czesc=2)
wyswietl_tekst(okno, "Ta część dobiegła końca, to chwila na moment odpoczynku.\nGdy będziesz gotowy/a kliknij spację, by kontynuować")

wyswietl_tekst(okno, "Sesja eksperymentalna - Część 3", "Naciśnij spację, aby rozpocząć")
procedura(df_eksperyment, 90, okno, muzyka=muz_slowa, czesc=3)
wyswietl_tekst(okno, "To koniec eksperymentu. Bardzo dziękujemy za wzięcie udziału w naszym badaniu!", "[Naciśnij spację, by wyjść z procedury eksperymentalnej]")

# Zamknięcie okna
okno.close()
core.quit()