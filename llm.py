import os, json, time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=120000)) # milisaniye
MODEL = "gemini-flash-lite-latest" # çalışmazsa AI Studio'dan güncel adı kontrol et
MODELS = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-flash-latest"]
import re

FIELD_GUIDES = [
    (["cadd", "biyoinformatik", "bioinformatics", "kemoinformatik", "ilaç", "drug"],
     "CADD burada Computer-Aided Drug Design (bilgisayar destekli ilaç tasarımı) demektir, "
     "AutoCAD DEĞİLDİR. Odak: moleküler docking, protein-ligand etkileşimi, QSAR, sanal tarama, "
     "moleküler dinamik, ADMET, dizi analizi (BLAST), PDB/ChEMBL, Python/RDKit/Biopython"),
    (["siber", "güvenlik", "security", "cybersecurity", "pentest"],
     "ağ güvenliği, zafiyet analizi, şifreleme, olay müdahalesi, OWASP, saldırı türleri ve savunma"),
    (["elektrik", "elektronik", "gömülü", "embedded", "mikroişlemci", "mikrodenetleyici"],
     "devre analizi, mikrodenetleyiciler, C ile gömülü programlama, sensörler, haberleşme protokolleri (I2C, SPI, UART)"),
    (["finans", "finansal", "muhasebe", "bankacılık", "yatırım", "financial", "accountant"],
     "finansal tablolar, bütçeleme, maliyet analizi, risk, Excel modelleme ve muhasebe temelleri"),
    (["tasarım", "tasarımcı", "design", "designer", "ux", "ui", "grafik"],
     "kullanıcı araştırması, tasarım süreci, prototipleme, tipografi ve renk, portfolyo sunumu, geri bildirimi yönetme"),
    (["makine", "inşaat", "endüstri", "üretim", "mekanik"],
     "mühendislik temelleri, proje ve süreç yönetimi, kalite, iş güvenliği, çizim/CAD araçları ve saha problemleri"),
    (["pazarlama", "marketing", "dijital"],
     "kampanya planlama, hedef kitle, dijital kanallar, içerik, performans metrikleri ve bütçe"),
    (["ürün", "product"],
     "ürün stratejisi, önceliklendirme, kullanıcı ihtiyacı, metrikler ve paydaş yönetimi"),
    (["satış", "sales", "müşteri", "customer"],
     "müşteri ihtiyaç analizi, itiraz yönetimi, ikna, hedef takibi, zor müşteri senaryoları"),
    (["ik", "ık", "hr", "insan"],
     "işe alım süreci, çalışan ilişkileri, çatışma yönetimi ve davranışsal değerlendirme"),
    (["veri", "data", "analist", "analisti", "yapay", "ml"],
     "SQL, istatistik, veri temizleme, görselleştirme, makine öğrenmesi temelleri ve analiz projeleri"),
    (["yazılım", "yazilim", "software", "developer", "geliştirici", "backend", "frontend", "stack"],
     "algoritma, veri yapıları, OOP, SOLID, Git, veritabanı, hata ayıklama ve proje deneyimi"),
]


def _guide(position):
    # Türkçe İ/I harfleri Python'da lower() ile bozulur, önce düzeltiyoruz
    p = position.replace("İ", "i").replace("I", "ı").lower()
    words = set(re.findall(r"\w+", p))
    for keys, text in FIELD_GUIDES:
        if any(k in words for k in keys):
            return text
    return f"{position} pozisyonunun gerçek mülakatlarında sorulan temel konular"


def _to_contents(messages, extra=None):
    # Gemini sohbetin "user" ile başlamasını ister, o yüzden başa bir tetikleyici ekliyoruz
    items = [{"role": "user", "content": "Mülakatı başlat."}] + list(messages)
    if extra:
        items.append({"role": "user", "content": extra})
    contents = []
    for m in items:
        text = (m["content"] or "").strip()
        if not text:  # boş mesajı Gemini yok sayar, yerine açık bir not koyuyoruz
            text = "(Aday cevap vermedi.)"
        contents.append(types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=text)]))
    return contents


def _call_json(system, contents):
    last = None
    for model in MODELS:          # sırayla modelleri dene
        for attempt in range(3):  # her model için 3 deneme
            try:
                r = client.models.generate_content(
                    model=model, contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        response_mime_type="application/json"))
                return json.loads(r.text)
            except Exception as e:
                last = e
                time.sleep(3 * (attempt + 1))  # 3, 6, 9 saniye bekle
    raise last


def ask_llm(messages, position, level, interview_type):
    lang = "İngilizce" if "ngiliz" in interview_type else "Türkçe"
    system = (
        f"Sen deneyimli bir mülakatçısın. Aday {position} pozisyonu için "
        f"{level} seviyesinde başvurdu. Mülakat türü: {interview_type}. "
        f"Mülakatı {lang} yürüt. Resmi ve profesyonel ol. "
        f"Bu alanın odak konuları: {_guide(position)}. Soruları bu konulardan "
        f"seç, pozisyonla alakasız soru sorma ve zorluğu {level} seviyesine uydur. "
        "Her seferinde SADECE şu JSON'u döndür: "
        '{"feedback": {"strength": "...", "improvement": "..."} veya null, '
        '"next_question": "..."}. '
        "Kurallar: Henüz adayın cevabı yoksa feedback null olsun ve ilk soruyu sor. "
        "Aday cevap verdiyse feedback'te strength ve improvement İKİSİNDE de adaya "
        "doğrudan 'sen' diye hitap et, 'aday' kelimesini kullanma. Feedback "
        "alanlarını mülakat dili ne olursa olsun HER ZAMAN Türkçe yaz. "
        "Sadece adayın SON cevabını değerlendir, önceki cevapları övme. "
        "Her biri kısa (1-2 cümle) olsun. Son cevap '(Aday cevap vermedi.)' ise "
        "ya da anlamsızsa, strength alanına 'Bu cevapta belirgin bir güçlü yön "
        "yok.' yaz ve improvement'ta cevap vermenin önemini söyle. "
        "next_question'a bir sonraki gerçekçi mülakat sorusunu koy ve onu "
        "mülakat dilinde yaz. Aynı soruyu tekrar sorma.")
    try:
        data = _call_json(system, _to_contents(messages))
        fb = data.get("feedback")
        if not isinstance(fb, dict):
            fb = None
        return {"feedback": fb, "next_question": str(data["next_question"])}
    except Exception as e:
        return {"feedback": None,
                "next_question": f"⚠️ Bir hata oluştu, tekrar deneyin. ({e})"}

def generate_report(messages, position, level, interview_type):
    system = (
        f"{position} pozisyonu, {level} seviyesi, {interview_type} mülakatının "
        "tamamını adil ve yapıcı biçimde değerlendir. "
        f"Alanın beklentileri: {_guide(position)}. Değerlendirmeyi buna göre yap. "
        "Sadece şu JSON'u döndür: "
        '{"score": 0-10 arası ondalıklı sayı, "strengths": ["..."], '
        '"improvements": ["..."], "star_tip": "..."}. '
        "Kurallar: Adaya doğrudan 'sen' diye hitap et ve strengths, "
        "improvements, star_tip hepsini bu dille yaz (örn. 'Projeni net "
        "anlattın.'). SADECE mülakatta gerçekten konuşulanlara dayan, "
        "konuşulmamış konuları ekleme. Boş, çok kısa ya da bilmiyorum "
        "türü cevapları puana yansıt. strengths ve improvements 2-4 "
        "maddelik liste olsun. star_tip, adayın eksiğine göre STAR "
        "metodunu (Situation, Task, Action, Result) nasıl kullanacağına dair "
        "en fazla 2 kısa cümlelik, 250 karakteri geçmeyen bir öneri olsun; "
        "parantez ve uzun sıralama kullanma. Türkçe yaz.")
    try:
        data = _call_json(system, _to_contents(
            messages, "Mülakat bitti, karneyi hazırla."))
        data["score"] = max(0.0, min(10.0, float(data["score"])))
        data["strengths"] = list(data.get("strengths", []))
        data["improvements"] = list(data.get("improvements", []))
        data["star_tip"] = str(data.get("star_tip", ""))
        return data
    except Exception as e:
        return {"score": 0.0, "strengths": [],
                "improvements": [f"Karne oluşturulamadı: {e}"],
                "star_tip": "", "error": True}


if __name__ == "__main__":  # arayüzsüz terminal testi
    pos = input("Pozisyon: ")
    lvl = input("Seviye (Stajyer/Yeni Mezun/Junior/Senior): ")
    typ = input("Tür (Teknik/İK-Davranışsal/İngilizce): ")
    msgs = []
    for _ in range(3):
        res = ask_llm(msgs, pos, lvl, typ)
        if res["feedback"]:
            print("\nKOÇ:", res["feedback"])
        print("\nAI:", res["next_question"])
        msgs.append({"role": "assistant", "content": res["next_question"]})
        msgs.append({"role": "user", "content": input("Sen: ")})
    print(json.dumps(generate_report(msgs, pos, lvl, typ),
                     ensure_ascii=False, indent=2))