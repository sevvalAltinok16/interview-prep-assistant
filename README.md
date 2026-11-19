# AI Interview Coach: Akıllı Mülakat Hazırlık Asistanı

Büyük dil modeli (Google Gemini) ile çalışan, seçtiğin pozisyona göre mülakat soruları soran, her cevabına anlık geri bildirim veren ve sonunda puanlı bir **karne** çıkaran web uygulaması. Streamlit ile geliştirilmiştir.

**Canlı demo:** https://interview-prep-assistant-01.streamlit.app

> Uygulama bir süre kullanılmazsa uykuya geçebilir. İlk açılışta birkaç saniye bekleyebilir.

## Ne yapar?

1. Kullanıcı bir **pozisyon** (ya da "Diğer" ile kendi pozisyonunu), **deneyim seviyesi** ve **mülakat türü** seçer.
2. Yapay zeka mülakatçı, pozisyona ve seviyeye uygun **5 soru** sorar.
3. Her cevaptan sonra **Mülakat Koçu** paneli, cevabın bir güçlü yönünü ve bir geliştirilebilir yönünü söyler.
4. Mülakat bitince **karne** üretilir: 10 üzerinden puan, güçlü yönler, gelişim alanları ve STAR yöntemiyle ilgili kısa bir ipucu.

## Kullanılan NLP / LLM kavramları

- **System prompting:** Modele "deneyimli mülakatçı" rolü, pozisyon, seviye ve mülakat türü arka planda verilir.
- **Alana özel odak:** Pozisyona göre (yazılım, veri, siber güvenlik, finans, pazarlama, biyoinformatik/CADD vb.) modele odak konular verilir. Listede olmayan pozisyonlarda genel bir yedek odak kullanılır.
- **Yapılandırılmış çıktı:** Model her seferinde JSON döndürür, arayüz bu veriyi doğrudan koç paneline ve karneye yerleştirir.
- **Bağlam yönetimi:** Konuşma geçmişi `st.session_state` içinde tutulur ve her çağrıda modele gönderilir.
- **Hata dayanıklılığı:** API yoğunluğunda (503) ya da zaman aşımında yedek modellere geçilir, boş cevaplar güvenle işlenir, hatalarda uygulama çökmez.

## Proje yapısı

```
app.py            Streamlit arayüzü (ekranlar, oturum durumu)
llm.py            Gemini API çağrıları, system prompt, karne üretimi
fake_llm.py       API'siz geliştirme için sahte yanıtlar
style.css         Arayüz stili
requirements.txt  Gerekli kütüphaneler
.env.example      API anahtarı şablonu
```

`app.py` ve `llm.py` arasındaki sözleşme:

```python
ask_llm(messages, position, level, interview_type)
# -> {"feedback": {"strength": "...", "improvement": "..."} | None, "next_question": "..."}

generate_report(messages, position, level, interview_type)
# -> {"score": 7.5, "strengths": [...], "improvements": [...], "star_tip": "..."}
# Hata durumunda ayrıca "error": True döner.
```

## Kendi bilgisayarında çalıştırma

Gereksinimler: Python 3.10 veya üstü ve ücretsiz bir Gemini API anahtarı ([aistudio.google.com](https://aistudio.google.com) → *Get API key*).

```bash
git clone https://github.com/sevvalAltinok16/interview-prep-assistant.git
cd interview-prep-assistant
pip install -r requirements.txt
```

`.env.example` dosyasını `.env` adıyla kopyala ve içine kendi anahtarını yaz:

```
GEMINI_API_KEY=buraya_kendi_anahtarini_yaz
```

Sonra uygulamayı başlat:

```bash
python -m streamlit run app.py
```

Tarayıcıda `http://localhost:8501` adresi açılır.

**API anahtarı olmadan denemek için:** `app.py` içindeki `USE_FAKE_LLM` değerini `True` yap. Bu durumda sahte yanıtlarla çalışır.

## Sınırlılıklar

- Gemini API yoğun olduğunda yanıtlar gecikebilir ya da hata mesajı gösterilebilir. Tekrar denemek yeterlidir.
- Geri bildirim ve puan bir yapay zeka değerlendirmesidir, gerçek bir mülakatın sonucunu garanti etmez. Hukuk, finans gibi alanlardaki içerikler çalışma amaçlı örneklerdir, uzman tavsiyesi yerine geçmez.
- "Diğer" ile girilen pozisyonlarda kısaltmalar yanlış anlaşılabilir. Pozisyonu açık yazmak daha iyi sonuç verir.

## Ekip

- Şevvalnur ALTINOK: LLM entegrasyonu ve prompt tasarımı (`llm.py`)
- Tuba BİRSİN: Arayüz tasarımı ve geliştirme (`app.py`)

Ders projesi olarak geliştirilmiştir.
