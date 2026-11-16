def ask_llm(messages, position, level, interview_type):
    fb = None if not messages else {
        "strength": "Cevabınız net ve düzenliydi.",
        "improvement": "Somut bir örnek ekleyebilirsiniz."}
    return {"feedback": fb, "question": "Bu bir deneme sorusudur. Kendinizden bahseder misiniz?"}

def generate_report(messages, position, level):
    return {"score": 7.5, "strengths": ["Örnek güçlü yön"],
            "improvements": ["Örnek gelişim alanı"], "tip": "STAR metodunu kullanın."}