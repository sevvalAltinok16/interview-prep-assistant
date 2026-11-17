"""SAHTE llm: arayüzü geliştirmek için. Gerçek llm.py arkadaşında.
Fonksiyon imzaları ve dönüş formatı aynı kalmalı (sözleşme)."""
import random
import time

QUESTIONS = [
    "Kendini ve bu pozisyona neden başvurduğunu kısaca anlatır mısın?",
    "En çok gurur duyduğun projeyi ve orada üstlendiğin rolü anlat.",
    "Bir ekip arkadaşınla anlaşmazlık yaşadığın bir durumu ve nasıl çözdüğini anlat.",
    "Baskı altında çalışmak zorunda kaldığın bir an var mı? Ne yaptın?",
    "Önümüzdeki beş yıl için hedeflerin neler?",
]

STRENGTHS = [
    "Cevabın akıcı ve anlaşılır, konuya doğrudan girmişsin.",
    "Somut bir örnek vermen cevabı güçlendirmiş.",
]
IMPROVEMENTS = [
    "Sonucu rakamla ifade edersen (örneğin %20 hızlanma) daha etkili olur.",
    "Kendi payını daha net ayır: 'biz' yerine 'ben ne yaptım' kısmını vurgula.",
]


def ask_llm(messages, position, level, interview_type):
    """messages: [{"role": "assistant" | "user", "content": str}, ...]

    Döner:
    {
        "feedback": {"strength": str, "improvement": str} veya None (ilk soruda None),
        "next_question": str,
    }
    """
    time.sleep(0.8)  # gerçek API gecikmesini taklit et
    asked = sum(1 for m in messages if m["role"] == "assistant")
    question = QUESTIONS[min(asked, len(QUESTIONS) - 1)]
    feedback = None
    if any(m["role"] == "user" for m in messages):
        feedback = {
            "strength": random.choice(STRENGTHS),
            "improvement": random.choice(IMPROVEMENTS),
        }
    return {"feedback": feedback, "next_question": question}


def generate_report(messages, position, level, interview_type):
    """Döner:
    {
        "score": float (10 üzerinden),
        "strengths": [str, ...],
        "improvements": [str, ...],
        "star_tip": str,
    }
    """
    time.sleep(0.8)
    return {
        "score": 7.5,
        "strengths": STRENGTHS,
        "improvements": IMPROVEMENTS,
        "star_tip": "Cevaplarını Durum, Görev, Eylem, Sonuç sırasıyla kurarsan daha ikna edici olur.",
    }
