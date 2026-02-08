import random

pcsayı = random.randint(1, 100)  
tahmin = 0

while tahmin != pcsayı:
    tahmin = int(input("Sayı giriniz: "))

    if tahmin > pcsayı:
        print("Aşağı in")
    elif tahmin < pcsayı:
        print("Yukarı çık")
    else:
        print("Tebrikler, bildiniz!")
