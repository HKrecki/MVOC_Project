import cv2
import numpy as np
import matplotlib.pyplot as plt
import skimage.measure as sime


# Otwarcie pliku
wideo = cv2.VideoCapture("OKNO_10.avi")
if not wideo.isOpened():
    print("Błąd otwarcia pliku")

# Zakresy kolorow tla i obiektow:
tlo_dol = [0,0,0]
tlo_gora = [20,20,20]
zielony_dol = np.array([19, 204, 14], dtype = "uint8") 
zielony_gora = np.array([21, 206, 16], dtype = "uint8") 
niebieski_dol =  np.array([204, 29, 19], dtype = "uint8") 
niebieski_gora =  np.array([206, 31, 21], dtype = "uint8") 
czerwony_dol =  np.array([29, 19, 199], dtype = "uint8") 
czerwony_gora =  np.array([31, 21, 201], dtype = "uint8") 
seledynowy_dol =  np.array([179, 189, 29], dtype = "uint8") 
seledynowy_gora =  np.array([181, 191, 31], dtype = "uint8") 

# Zmienne potrzebne do zliczania elementow
suma_elementow = 0
lista = list()
lista.insert(0,0)
list_index = 0
kurtyna_wiersz = 2 # wiersz od gory obrazu w ktorym umieszczona jest kurtyna

class obiekt:
    def __init__(self, _numer, _kolor, _typ, _stan):
        self.numer = _numer
        self.kolor = _kolor
        self.typ = _typ
        self.stan = _stan
    
    numer = 0
    kolor = ""
    typ = ""
    stan = ""

lista_obiektow = []

aktualny_numer_obiektu = -1
aktualny_typ = "brak"
aktualny_stan = "brak"
aktualny_kolor = "brak"

##########

# Rozpozanie koloru:
def rozpoznanie_koloru(zdjecie):
    maska_z = cv2.inRange(zdjecie, zielony_dol, zielony_gora)
    maska_n = cv2.inRange(zdjecie, niebieski_dol, niebieski_gora)
    maska_c = cv2.inRange(zdjecie, czerwony_dol, czerwony_gora)
    maska_s = cv2.inRange(zdjecie, seledynowy_dol, seledynowy_gora)

    #cv2.imshow("a", maska_z)
    if cv2.countNonZero(maska_z) != 0:
        kolor = "zielony"
    elif cv2.countNonZero(maska_n) != 0:
        kolor = "niebieski"
    elif cv2.countNonZero(maska_c) != 0:
        kolor = "czerwony"
    elif cv2.countNonZero(maska_s) != 0:
        kolor = "seledynowy"
        
    return kolor


def rozpoznanie_kształtu(zdjecie):
    zdjecie = cv2.cvtColor(zdjecie, cv2.COLOR_BGR2GRAY)
    _, binarny = cv2.threshold(zdjecie, 30, 255, cv2.THRESH_BINARY)
    
    etykiety = sime.label(binarny)
    cechy = sime.regionprops(etykiety)
    
    # Rozpoznanie na podstawie cech
    if cechy[0].euler_number == -1: 
        typ = "B"
        stan = "prawidłowy"
    elif cechy[0].euler_number == 1:
        if cechy[0].area > 650 and cechy[0].area < 750: 
            typ = "O"
            stan = "wadliwy"
        elif cechy[0].area > 465 and cechy[0].area < 565: 
            if cechy[0].eccentricity > 0.87 and cechy[0].eccentricity < 0.90: 
                typ = "2"
                stan = "prawidłowy"
            elif cechy[0].eccentricity > 0.77 and cechy[0].eccentricity < 0.79: 
                typ = "C"
                stan = "prawidłowy"
            else:
                typ = "brak"
                stan = "brak"
        else:
            typ = "brak"
            stan = "brak"
            
    elif cechy[0].euler_number == 0:
        if cechy[0].eccentricity > 0.3 and cechy[0].eccentricity < 0.35: 
            typ = "O"
            stan = "prawidłowy"
        elif cechy[0].eccentricity > 0.43 and cechy[0].eccentricity < 0.46: 
            typ = "O"
            stan = "wadliwy"
        elif cechy[0].eccentricity > 0.57 and cechy[0].eccentricity < 0.61: 
            typ = "C"
            stan = "wadliwy"
        elif cechy[0].eccentricity > 0.86 and cechy[0].eccentricity < 0.88: 
            typ = "2"
            stan = "wadliwy"
        else: # 
            if cechy[0].area > 675 and cechy[0].area < 677:
                typ = "2"
                stan = "wadliwy"
            elif cechy[0].area > 759 and cechy[0].area < 813:
                typ = "B"
                stan = "wadliwy"
            else:
                if cechy[0].solidity > 0.70 and cechy[0].solidity < 0.77:
                    typ = "B"
                    stan = "wadliwy"
                elif cechy[0].solidity > 0.60 and cechy[0].solidity < 0.66:
                    typ = "C"
                    stan = "wadliwy"
                else:
                    typ = "brak"
                    stan = "brak"
    else:
        typ = "brak"
        stan = "brak"
      
    return typ, stan    
    

# Główna pętla programu
while(True):
    list_index += 1
    
    # Odczyt danych
    status, ramka_org = wideo.read()
    
    # Zakoncz petle jesli koniec pliku
    if ramka_org is None:
        break
    
    # Preprocessing
    
    # Wyświetlenie
    if status:
        cv2.imshow("obraz_oryginalny", ramka_org) 
     
    # Stop awaryjny - wyzwalany za pomocą spacji
    key = cv2.waitKey(1) 
    if key == 32:
        while(cv2.waitKey() != 32):
            pass
    
    # TODO: Do usunięcia (wyjscie z programu):
    if key == ord('q'):
        break        
    
    # Zliczenie elementow przechodzacych przez kurtyne
    kurtyna = ramka_org[kurtyna_wiersz,:] # Miejsce gdzie jest umieszczona kurtyna -> dany wiersz i wszytskie kolumny (280)
    sum = 0
    
    for i in range(280):
        # Jesli w pikselu kurtyny jest tylko tlo:
        if kurtyna[i,0] < 20 and kurtyna[i,1]<20 and kurtyna[i,2]<20:
            pass
        else: # jesli jest cos innego (suma innych pikseli):
            sum += 1
         
    # Zapisanie do listy ilosci pikseli innych od tla, ktore obecnie sa w zasiegu kurtyny
    if sum > 0:
        lista.append(sum)
    else:
        lista.append(0)
    
    # Jesli w obiekt przeszedl przez kurtyne i jest caly widoczny na obrazie
    if lista[len(lista)-1] == 0 and lista[len(lista)-2] > 0:
        suma_elementow += 1        
        aktualny_numer_obiektu = suma_elementow
        
        # Wyswietlenie strefy detekcji razem z calym widocznym obiektem w osobnym oknie:
        strefa_detekcji = ramka_org[0:60, :]
        if status:
            # Wyswietlenie strefy detekcji z calym widocznym obiektem
            cv2.imshow("Zdjecie ostatniego wykrytego obiektu", strefa_detekcji) 
        
        # Rozpoznanie koloru obiektu:
        aktualny_kolor = rozpoznanie_koloru(strefa_detekcji)
        
        # Rozpoznianie kształtu
        aktualny_typ, aktualny_stan = rozpoznanie_kształtu(strefa_detekcji)
        
        
        if aktualny_typ != "brak" and aktualny_stan != "brak":
            print("Rozpoznany znak nr. ", aktualny_numer_obiektu, ": <", aktualny_typ, "> ", aktualny_stan, ", kolor: ", aktualny_kolor)
            lista_obiektow.append(obiekt(aktualny_numer_obiektu, aktualny_kolor, aktualny_typ, aktualny_stan))
        
        # TODO: Do usuniecia (Zatrzymanie lini w momencie wykrycia elementu)
        #while(cv2.waitKey() != 32):
        #    pass
        
wideo.release()
cv2.destroyAllWindows()    

print("\n---------- Raport koncowy ----------")                
print("Suma wszytskich wykrytych elementow: ", len(lista_obiektow))
#for i in range(len(lista_obiektow)):
    #print(lista_obiektow[i].numer, lista_obiektow[i].kolor, lista_obiektow[i].typ, lista_obiektow[i].stan)


#print("\n---------- Raport koncowy ----------")        
czerwone_2_prawidlowe = 0
czerwone_2_wadliwe = 0
niebieskie_2_prawidlowe = 0
niebieskie_2_wadliwe = 0
zielone_2_prawidlowe = 0
zielone_2_wadliwe = 0

czerwone_O_prawidlowe = 0
czerwone_O_wadliwe = 0
niebieskie_O_prawidlowe = 0
niebieskie_O_wadliwe = 0
zielone_O_prawidlowe = 0
zielone_O_wadliwe = 0

czerwone_B_prawidlowe = 0
czerwone_B_wadliwe = 0
niebieskie_B_prawidlowe = 0
niebieskie_B_wadliwe = 0
seledynowe_B_prawidlowe = 0
seledynowe_B_wadliwe = 0

czerwone_C_prawidlowe = 0
czerwone_C_wadliwe = 0
niebieskie_C_prawidlowe = 0
niebieskie_C_wadliwe = 0
seledynowe_C_prawidlowe = 0
seledynowe_C_wadliwe = 0

for i in lista_obiektow:
    # 2:
    if i.kolor == "czerwony" and i.typ == "2" and i.stan == "prawidłowy":
        czerwone_2_prawidlowe += 1
    if i.kolor == "czerwony" and i.typ == "2" and i.stan == "wadliwy":
        czerwone_2_wadliwe += 1
    if i.kolor == "niebieski" and i.typ == "2" and i.stan == "prawidłowy":
        niebieskie_2_prawidlowe += 1
    if i.kolor == "niebieski" and i.typ == "2" and i.stan == "wadliwy":
        niebieskie_2_wadliwe += 1
    if i.kolor == "zielony" and i.typ == "2" and i.stan == "prawidłowy":
        zielone_2_prawidlowe += 1
    if i.kolor == "zielony" and i.typ == "2" and i.stan == "wadliwy":
        zielone_2_wadliwe += 1        
    # O:
    if i.kolor == "czerwony" and i.typ == "O" and i.stan == "prawidłowy":
        czerwone_O_prawidlowe += 1
    if i.kolor == "czerwony" and i.typ == "O" and i.stan == "wadliwy":
        czerwone_O_wadliwe += 1
    if i.kolor == "niebieski" and i.typ == "O" and i.stan == "prawidłowy":
        niebieskie_O_prawidlowe += 1
    if i.kolor == "niebieski" and i.typ == "O" and i.stan == "wadliwy":
        niebieskie_O_wadliwe += 1
    if i.kolor == "zielony" and i.typ == "O" and i.stan == "prawidłowy":
        zielone_O_prawidlowe += 1
    if i.kolor == "zielony" and i.typ == "O" and i.stan == "wadliwy":
        zielone_O_wadliwe += 1            
    # B:    
    if i.kolor == "czerwony" and i.typ == "B" and i.stan == "prawidłowy":
        czerwone_B_prawidlowe += 1
    if i.kolor == "czerwony" and i.typ == "B" and i.stan == "wadliwy":
        czerwone_B_wadliwe += 1
    if i.kolor == "niebieski" and i.typ == "B" and i.stan == "prawidłowy":
        niebieskie_B_prawidlowe += 1
    if i.kolor == "niebieski" and i.typ == "B" and i.stan == "wadliwy":
        niebieskie_B_wadliwe += 1
    if i.kolor == "seledynowy" and i.typ == "B" and i.stan == "prawidłowy":
        seledynowe_B_prawidlowe += 1
    if i.kolor == "seledynowy" and i.typ == "B" and i.stan == "wadliwy":
        seledynowe_B_wadliwe += 1            
    # C
    if i.kolor == "czerwony" and i.typ == "C" and i.stan == "prawidłowy":
        czerwone_C_prawidlowe += 1
    if i.kolor == "czerwony" and i.typ == "C" and i.stan == "wadliwy":
        czerwone_C_wadliwe += 1
    if i.kolor == "niebieski" and i.typ == "C" and i.stan == "prawidłowy":
        niebieskie_C_prawidlowe += 1
    if i.kolor == "niebieski" and i.typ == "C" and i.stan == "wadliwy":
        niebieskie_C_wadliwe += 1
    if i.kolor == "seledynowy" and i.typ == "C" and i.stan == "prawidłowy":
        seledynowe_C_prawidlowe += 1
    if i.kolor == "seledynowy" and i.typ == "C" and i.stan == "wadliwy":
        seledynowe_C_wadliwe += 1            
    
print("--------------- Dla typu 2: ---------------")
print("Czerwony 2, prawidłowy: ", czerwone_2_prawidlowe)
print("Czerwony 2, wadliwy: ", czerwone_2_wadliwe)
print("Niebieski 2, prawidłowy: ", niebieskie_2_prawidlowe)
print("Niebieski 2, wadliwy: ", niebieskie_2_wadliwe)
print("Zielony 2, prawidłowy: ", zielone_2_prawidlowe)
print("Zielony 2, wadliwy: ", zielone_2_wadliwe)

print("--------------- Dla typu O: ---------------")
print("Czerwony O, prawidłowy: ", czerwone_O_prawidlowe)
print("Czerwony O, wadliwy: ", czerwone_O_wadliwe)
print("Niebieski O, prawidłowy: ", niebieskie_O_prawidlowe)
print("Niebieski O, wadliwy: ", niebieskie_O_wadliwe)
print("Zielony O, prawidłowy: ", zielone_O_prawidlowe)
print("Zielony O, wadliwy: ", zielone_O_wadliwe)
    
print("--------------- Dla typu B: ---------------")
print("Czerwony B, prawidłowy: ", czerwone_B_prawidlowe)
print("Czerwony B, wadliwy: ", czerwone_B_wadliwe)
print("Niebieski B, prawidłowy: ", niebieskie_B_prawidlowe)
print("Niebieski B, wadliwy: ", niebieskie_B_wadliwe)
print("Seledynowy B, prawidłowy: ", seledynowe_B_prawidlowe)
print("Seledynowy B, wadliwy: ", seledynowe_B_wadliwe)
    
print("--------------- Dla typu C: ---------------")
print("Czerwony C, prawidłowy: ", czerwone_C_prawidlowe)
print("Czerwony C, wadliwy: ", czerwone_C_wadliwe)
print("Niebieski C, prawidłowy: ", niebieskie_C_prawidlowe)
print("Niebieski C, wadliwy: ", niebieskie_C_wadliwe)
print("Seledynowy C, prawidłowy: ", seledynowe_C_prawidlowe)
print("Seledynowy C, wadliwy: ", seledynowe_C_wadliwe)
    