# PhantomCast: AI-Powered Gesture Control System

PhantomCast is a real-time computer vision application that translates facial expressions and hand gestures into keyboard macros. Built with Python, OpenCV, and MediaPipe, it allows users to control software, trigger hotkeys, or play games completely hands-free.

## 🎥 See it in Action

Watch this demonstration of playing **World of Warcraft** completely hands-free using only camera interactions!

📺 **[Watch the WoW Gameplay Demo on YouTube](https://youtu.be/yTkqjwFcq-0)**

## 🌟 Features

- **Facial Recognition:** Bind keys to mouth opening or eye blinking.
- **Advanced Hand Tracking:** \* Detects hand tilt (left/right) for steering or directional movement.
  - Recognizes specific gestures (e.g., the "Rock 🤘" gesture).
  - Measures finger spread and gap distances for analog-style triggers (Gas/Brake mechanics).
- **Customizable GUI:** A Tkinter-based user interface to adjust sensitivity thresholds and remap keys on the fly.
- **Live HUD:** Real-time visual feedback on the camera feed showing active gestures and triggered keys.
- **Save/Load System:** Automatically saves your custom thresholds and keybinds to a JSON file.

## 🎯 Use Cases

- **Gaming:** Map complex ability rotations in MMORPGs (like World of Warcraft) to hand gestures, or use hand-tilt for driving simulators.
- **3D Software & Art:** Trigger macros or switch tools in software without taking your hands off your drawing tablet.
- **Accessibility:** Navigate software and trigger commands using only facial movements.

## 🚀 Installation

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/YOUR-USERNAME/phantomcast.git](https://github.com/YOUR-USERNAME/phantomcast.git)
   cd phantomcast
   ```

2. **Create a virtual environment (Recommended):**

   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 How to Use

1. Run the main script:
   ```bash
   python main.py
   ```
2. The UI will appear alongside your camera feed.
3. Assign your desired keys in the **KEY ASSIGNMENTS** section (e.g., `ctrl+tab`, `w`, `g, end`).
4. Adjust the **THRESHOLDS** to match your environment and preferences.
5. Click **START SYSTEM** to activate the gesture-to-keyboard listener.
6. Click **SAVE ALL SETTINGS** to keep your configuration for the next session.

## 🛠️ Technologies Used

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [pynput](https://pypi.org/project/pynput/)
- Tkinter

## 👤 Author

**Tarik Husny**

---

---

# PhantomCast: Yapay Zeka Destekli Jest Kontrol Sistemi

PhantomCast, yüz ifadelerini ve el hareketlerini klavye makrolarına çeviren gerçek zamanlı bir bilgisayarlı görü (computer vision) uygulamasıdır. Python, OpenCV ve MediaPipe ile geliştirilen bu sistem; kullanıcıların yazılımları kontrol etmesine, kısayolları tetiklemesine veya tamamen eller serbest bir şekilde oyun oynamasına olanak tanır.

## 🎥 İş Başında Görün

Sadece kamera etkileşimleri kullanılarak, klavyeye dokunmadan **World of Warcraft** oynanan bu demoyu izleyin!

📺 **[WoW Oynanış Demosunu YouTube'da İzle](https://youtu.be/yTkqjwFcq-0)**

## 🌟 Özellikler

- **Yüz Tanıma:** Ağız açma veya göz kırpma hareketlerine tuş atayabilme.
- **Gelişmiş El Takibi:** \* Yönlendirme ve hareket için el eğimini (sağ/sol) algılama.
  - Belirli el hareketlerini tanıma (örn. "Rock 🤘" işareti).
  - Analog tarzı tetikleyiciler için parmak açıklığını ve mesafesini ölçme (Gaz/Fren mekaniği).
- **Özelleştirilebilir Arayüz:** Hassasiyet eşiklerini ayarlamak ve tuş atamalarını anında değiştirmek için Tkinter tabanlı kullanıcı arayüzü.
- **Canlı HUD:** Kamera görüntüsü üzerinde aktif hareketleri ve tetiklenen tuşları gösteren gerçek zamanlı görsel geri bildirim.
- **Kaydet/Yükle Sistemi:** Özel eşik değerlerinizi ve tuş atamalarınızı otomatik olarak bir JSON dosyasına kaydeder.

## 🎯 Kullanım Senaryoları

- **Oyun:** MMORPG'lerde (World of Warcraft gibi) karmaşık yetenek rotasyonlarını el hareketlerine atayabilir veya sürüş simülatörlerinde el eğimini direksiyon olarak kullanabilirsiniz.
- **3D Yazılım ve Sanat:** Ellerinizi çizim tabletinden ayırmadan makroları tetikleyebilir veya araçları (tool) değiştirebilirsiniz.
- **Erişilebilirlik:** Sadece yüz hareketlerini kullanarak yazılımlarda gezinebilir ve komut verebilirsiniz.

## 🚀 Kurulum

1. **Projeyi klonlayın:**

   ```bash
   git clone [https://github.com/YOUR-USERNAME/phantomcast.git](https://github.com/YOUR-USERNAME/phantomcast.git)
   cd phantomcast
   ```

2. **Sanal ortam (Virtual Environment) oluşturun (Önerilir):**

   ```bash
   python -m venv venv

   # Windows için:
   venv\Scripts\activate
   # macOS/Linux için:
   source venv/bin/activate
   ```

3. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Nasıl Kullanılır?

1. Ana dosyayı çalıştırın:
   ```bash
   python main.py
   ```
2. Kullanıcı arayüzü (UI) kamera görüntünüzle birlikte açılacaktır.
3. **KEY ASSIGNMENTS** (Tuş Atamaları) bölümünden istediğiniz tuşları belirleyin (örn: `ctrl+tab`, `w`, `g, end`).
4. **THRESHOLDS** (Eşik Değerleri) bölümünü bulunduğunuz ortama ve kendi hareketlerinize göre ayarlayın.
5. Jest-klavye dinleyicisini aktif etmek için **START SYSTEM** butonuna tıklayın.
6. Ayarlarınızı bir sonraki kullanım için saklamak adına **SAVE ALL SETTINGS** butonuna tıklayın.

## 🛠️ Kullanılan Teknolojiler

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [pynput](https://pypi.org/project/pynput/)
- Tkinter

## 👤 Geliştirici

**Tarik Husny**
