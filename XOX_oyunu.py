import numpy as np
import pickle

class Durum:
    def __init__(self,p1,p2):
     self.tahta = np.zeros((3,3))
     self.p1 = p1
     self.p2 = p2
     self.bitti = False # oyunun bitip bitmediğini kontrol eder.
     self.oyunTablosu = None # oyun sırasında sıranın kimde olduğunu ve geçmiş hamleleri tutmak için
     # ilk oyuncu p1 
     self.oyuncuNumarası = 1

    # tahtadaki mevcut tablo dizilimini al
    def tabloAl(self):
       self.oyunTablosu = str(self.tahta.reshape(3 * 3))
       return self.oyunTablosu
    
    def kazanan(self):
       # satırda kazanan
       for i in range(3):
          if sum(self.tahta[i,:]) == 3:
             self.bitti = True
             return 1
          if sum(self.tahta[i,:]) == -3:
             self.bitti = True
             return -1
          
       # sütunda kazanan
       for i in range(3):
           if sum(self.tahta[:,i]) == 3:
              self.bitti = True
              return 1
           if sum(self.tahta[:,i]) == -3:
              self.bitti = True
              return -1
           
       # çarprazda kazanan
       diagonal_toplam_1 = sum([self.tahta[i,i] for i in range(3)])
       diagonal_toplam_2 = sum([self.tahta[i,3-i-1] for i in range(3)])

       if diagonal_toplam_1 == 3 or diagonal_toplam_2 == 3:
           self.bitti = True
           return 1
       if diagonal_toplam_1 == -3 or diagonal_toplam_2 == -3:
           self.bitti = True
           return -1
       
       # beraberlik durumu
       if len(self.bosKonumlar()) == 0:
          self.bitti = True
          return 0
       
       self.bitti = False
       return None
    

    def bosKonumlar(self):
       konumlar = []
       for i in range(3):
          for j in range(3):
            if self.tahta[i,j] == 0:
               konumlar.append((i,j))
       return konumlar
    
    def durumGuncelle(self,konum):
       self.tahta[konum] = self.oyuncuNumarası
       # oyuncu değiştir
       self.oyuncuNumarası = -1 if self.oyuncuNumarası == 1 else 1

    # sadece oyun bittiğinde
    def odulVer(self):
       result = self.kazanan()
       # ödül geri yayılması(backpropogate reward)
       # kazanan oyuncu için 1 ödül,kaybedene -1 ödül verilir.
       # backpropagation işleminde oyuncu kendisine verilen ödülü önceki hamlesinde almış gibi davranarak eğitimini güncelliyor.
       if result == 1: # 1.oyuncu için
          self.p1.feedReward(1)
          self.p2.feedReward(0)
       elif result == -1: # 2.oyuncu için
          self.p1.feedReward(0)
          self.p2.feedReward(1)
       else:
          self.p1.feedReward(0.1)
          self.p2.feedReward(0.5)

    # tahta resetleme
    def reset(self):
       self.tahta = np.zeros((3,3))
       self.bitti = False
       self.oyunTablosu = None
       self.oyuncuNumarası = 1

    # eğitim için oynatma
    def play(self,rounds=100):
      for i in range(rounds):
         if i % 1000 == 0:
            print("Rounds ()",format(i))
         while not self.bitti:
           # player 1
           konumlar = self.bosKonumlar()
           p1_aksiyon = self.p1.aksiyonSec(konumlar,self.tahta,self.oyuncuNumarası)
           # aksiyon al ve tahta durumunu güncelle
           self.durumGuncelle(p1_aksiyon)
           oyun_Tablosu = self.tabloAl()
           self.p1.durumEkle(oyun_Tablosu)

           # eğer bittiyse tahta durumunu kontrol et
           win = self.kazanan()
           if win is not None:
              # p1 ile bitti
              print("p1 kazandı")
              self.odulVer()
              self.p1.reset()
              self.p2.reset()
              self.reset
              break
           
           else:
              # player 1
              konumlar = self.bosKonumlar()
              p2_aksiyon = self.p2.aksiyonSec(konumlar,self.tahta,self.oyuncuNumarası)
              # aksiyon al ve durumunu güncelle
              self.durumGuncelle(p2_aksiyon)
              oyun_Tablosu = self.tabloAl()
              self.p2.durumEkle(oyun_Tablosu)

              # eğer bittiyse tahta durumunu kontrol et
              win = self.kazanan()
              if win is not None:
                 # p2 ile bitti
                 print("p2 kazandı")
                 self.odulVer()
                 self.p1.reset()
                 self.p2.reset()
                 self.reset
                 break
              
    # insanla oynama
    def play2(self):
       while not self.bitti:
        # player 1
        konumlar = self.bosKonumlar()
        tahta = self.tahta
        oyuncuNum = self.oyuncuNumarası
        p1_aksiyon = self.p1.aksiyonSec(konumlar,tahta,oyuncuNum)
        # aksiyon al ve tahta durumunu güncelle
        self.durumGuncelle(p1_aksiyon)
        self.tahtaGoster()
        # eğer bittiyse tahta durumunu kontrol et
        win = self.kazanan()
        if win is not None:
          if win == 1:
            print(self.p1.name, "kazandı!")
          else:
            print("berabere!")
            self.reset()
            break
          
        else:
           # Player 2
           konumlar = self.bosKonumlar()
           p2_aksiyon = self.p2.aksiyonSec(konumlar,tahta,oyuncuNum)
           self.durumGuncelle(p2_aksiyon)
           self.tahtaGoster()
           # eğer bittiyse tahta durumunu kontrol et
           win = self.kazanan()
           if win is not None:
              if win == -1:
                 print(self.p2.name, "kazandı!")
              else:
                 print("berabere")
                 self.reset
                 break
              
    def tahtaGoster(self):
       # p1 = x     p2 = o
       for i in range(0,3):
        print("-------------")
        out = '| '
        for j in range(0,3):
          if self.tahta[i,j] == 1:
            isaret = 'x'
          if self.tahta[i,j] == -1:
            isaret = 'o'
          if self.tahta[i,j] == 0:
              isaret = ' '

          out += isaret + ' | '
        print(out)
       print("-------------")


class Player:
   def __init__(self,name,exp_rate=0.3):
      self.name = name
      self.states = [] # tüm konumları kaydet
      self.lr = 0.2
      self.exp_rate = exp_rate
      self.azaltma_katsayisi = 0.9
      self.states_value = {}


   def tabloAl(self,tahta):
      oyunTablosu = str(tahta.reshape(3*3))
      return oyunTablosu
   
   def aksiyonSec(self,konumlar,mevcut_tahta,sembol):
      if np.random.uniform(0,1) <= self.exp_rate:
         # rassal aksiyon al
         idx = np.random.choice(len(konumlar))
         aksiyon = konumlar[idx]
      else:
         max_deger = -999
         for p in konumlar:
            sonraki_tahta = mevcut_tahta.copy()
            sonraki_tahta[p] = sembol
            sonraki_oyunTablosu = self.tabloAl(sonraki_tahta)
            value = 0 if self.states_value.get(sonraki_oyunTablosu) is None else self.states_value.get(sonraki_oyunTablosu)
            if value >= max_deger:
               max_deger =value
               aksiyon = p
      return aksiyon
   
   def durumEkle(self,state):
      self.states.append(state)

   def feedReward(self,reward):

      for st in reversed(self.states):

         if self.states_value.get(st) is None:
            self.states_value[st] = 0

         self.states_value[st] +=  self.lr*(self.azaltma_katsayisi*reward - self.states_value[st])

         reward = self.states_value[st]


   def reset(self):
      self.states = []

   def savePolicy(self):
      print(self.states_value)
      fw = open('policy_' + str(self.name),'wb')
      pickle.dump(self.states_value, fw)
      fw.close()

   def loadPolicy(self, file):
      fr = open(file, 'rb')
      self.states_value = pickle.load(fr)
      fr.close()


class HumanPlayer:
   def __init__(self,name):
      self.name = name

   def aksiyonSec(self,konumlar,tahta,oyuncuNum):
      while True:
         satir = int(input("Satır değerini giriniz...:"))
         sütun = int(input("Sütun değerini giriniz...:"))
         aksiyon = (satir,sütun)
         if aksiyon in konumlar:
            return aksiyon
         
   def durumEkle(self,state):
      pass
   
   def feedReward(self,reward):
      pass
   
   def reset(self):
      pass
   

p1 = Player("p1")
p2 = Player("p2")

st = Durum(p1,p2)
print("Eğitiliyor...")
st.play(100)

p1.savePolicy()
p2.savePolicy()

p1.loadPolicy("policy_p1")


p1 = Player("Bilgisayar",exp_rate=0)
p1.loadPolicy("policy_p1")

p2 = HumanPlayer("Halil")
st = Durum(p1,p2)
st.play2()
              

