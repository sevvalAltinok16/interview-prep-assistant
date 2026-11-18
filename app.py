import html
import time

import streamlit as st

try:  # .env içindeki GEMINI_API_KEY'i ortam değişkenine yükler
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# True: sahte fake_llm.py (anahtar gerekmez). False: arkadaşın gerçek llm.py'si.
USE_FAKE_LLM = False

if USE_FAKE_LLM:
    import fake_llm as llm
else:
    import llm

TOTAL_QUESTIONS = 5

st.set_page_config(page_title="Mülakat Koçu", layout="wide")


def load_css(path="style.css"):
    with open(path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_state():
    defaults = {
        "page": "welcome",
        "selected_position": None,
        "position": None,
        "level": "Junior",
        "interview_type": "Davranışsal",
        "messages": [],
        "feedback": None,
        "question_no": 1,
        "error": None,
        "report": None,
        "start_time": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def call_llm_for_next_question():
    """Modeli çağırır. Başarılıysa soruyu ve geri bildirimi state'e yazar.

    Hata durumunda (istisna ya da '⚠' ile başlayan soru) mesajlara EKLEMEZ ve
    soru sayacını artırmaz; sadece s.error doldurulur (Tekrar Dene butonu için).
    """
    s = st.session_state
    try:
        with st.spinner("Düşünüyor..."):
            result = llm.ask_llm(s.messages, s.position, s.level, s.interview_type)
        question = str(result["next_question"]).strip()
        if question.startswith("\u26a0"):
            s.error = question
            return
        # Sayaç sadece bir cevaptan sonra gelen yeni soruda artar (ilk soruda artmaz)
        advance = any(m["role"] == "user" for m in s.messages)
        s.feedback = result["feedback"]
        s.messages.append({"role": "assistant", "content": question})
        if advance:
            s.question_no += 1
        s.error = None
    except Exception:
        s.error = "Soru alınamadı. Bağlantını kontrol edip tekrar dene."


def interview_page():
    s = st.session_state
    if s.start_time is None:
        s.start_time = time.time()

    # İlk soru
    if not s.messages and not s.error:
        call_llm_for_next_question()

    # Üst bar
    left, right = st.columns([3, 1])
    with left:
        st.markdown(f"**{s.position}**")
        st.caption(f"{s.level} seviye, {s.interview_type} mülakat")
    with right:
        st.markdown(
            f'<div style="text-align:right;font-weight:600">'
            f"Soru {s.question_no} / {TOTAL_QUESTIONS}</div>",
            unsafe_allow_html=True,
        )
    st.progress(s.question_no / TOTAL_QUESTIONS)
    st.write("")

    chat_col, coach_col = st.columns([2, 1], gap="large")

    # Sol: sohbet
    with chat_col:
        if s.messages:
            last = s.messages[-1]
            if last["role"] == "assistant":
                history, active = s.messages[:-1], last
            else:  # cevap verildi ama yeni soru gelmedi (hata): hepsi geçmiş
                history, active = s.messages, None

            with st.container(key="history"):
                for m in history:
                    with st.chat_message(m["role"]):
                        st.write(m["content"])

            if active:
                with st.chat_message("assistant"):
                    st.markdown(
                        f'<div class="active-question">{html.escape(active["content"])}</div>',
                        unsafe_allow_html=True,
                    )

        if s.error:
            st.error(s.error)
            if st.button("Tekrar Dene"):
                s.error = None
                call_llm_for_next_question()
                st.rerun()

        answer = st.chat_input("Cevabını yaz...", disabled=bool(s.error))
        if answer and answer.strip():
            s.messages.append({"role": "user", "content": answer.strip()})
            if s.question_no >= TOTAL_QUESTIONS:
                s.error = None
                s.page = "report"
            else:
                call_llm_for_next_question()
            st.rerun()

    # Sağ: Mülakat Koçu
    with coach_col:
        st.markdown("**Mülakat Koçu**")
        fb = s.feedback
        if fb:
            st.markdown(
                f'<div class="coach-good"><b>Güçlü yön</b><br>{html.escape(fb["strength"])}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="coach-warn"><b>Geliştirilebilir</b><br>{html.escape(fb["improvement"])}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="card muted">Henüz geri bildirim yok. İlk cevabını yazınca burada görünecek.</div>',
                unsafe_allow_html=True,
            )

    st.write("")
    has_answer = any(m["role"] == "user" for m in s.messages)
    if st.button("Mülakatı Bitir", type="primary", disabled=not has_answer):
        s.error = None
        s.page = "report"
        st.rerun()


POSITIONS = [
    ("Yazılım Mühendisi", "Algoritma ve sistem tasarımı"),
    ("Veri Analisti", "SQL, analiz ve veriyle hikaye anlatma"),
    ("Siber Güvenlik Uzmanı", "Zafiyet analizi ve olay müdahalesi"),
    ("Gömülü Sistemler Mühendisi", "Mikrodenetleyici ve devre"),
    ("Biyoinformatik / CADD Uzmanı", "İlaç tasarımı ve moleküler modelleme"),
    ("Ürün Yöneticisi", "Önceliklendirme ve strateji"),
    ("Pazarlama Uzmanı", "Kampanya, marka ve büyüme"),
    ("Satış / Müşteri Temsilcisi", "İkna ve müşteri ilişkileri"),
    ("İK Uzmanı", "İşe alım, çalışan deneyimi, iletişim"),
    ("Finans / Muhasebe Uzmanı", "Bütçe, analiz ve risk"),
    ("UX / Grafik Tasarımcı", "Tasarım süreci ve portföy"),
    ("Makine / İnşaat / Endüstri Mühendisi", "Proje, süreç ve kalite"),
    ("Diğer", "Kendi pozisyonunu yaz"),
]
LEVELS = ["Stajyer", "Junior", "Orta", "Kıdemli"]
# "İngilizce" değeri aynen kalmalı: llm.py mülakatı İngilizce yapmak için bunu arıyor.
INTERVIEW_TYPES = ["Davranışsal", "Teknik", "Karışık", "İngilizce"]


def welcome_page():
    s = st.session_state

    st.title("Hangi mülakata hazırlanıyorsun?")
    st.caption("Pozisyonunu seç, yapay zeka mülakatçı sana 5 soru sorsun ve sonunda karne versin.")
    st.write("")

    # Pozisyon kartları: 3 sütunluk ızgara (liste üzerinden döngüyle çizilir)
    for row_start in range(0, len(POSITIONS), 3):
        cols = st.columns(3, gap="medium")
        for col, (i, (name, subtitle)) in zip(
            cols, list(enumerate(POSITIONS))[row_start : row_start + 3]
        ):
            selected = s.selected_position == name
            key = f"poscard_{i}_sel" if selected else f"poscard_{i}"
            with col:
                if st.button(f"**{name}**  \n:gray[{subtitle}]", key=key, use_container_width=True):
                    s.selected_position = name
                    st.rerun()

    # "Diğer" seçilince serbest metin
    custom_position = ""
    if s.selected_position == "Diğer":
        custom_position = st.text_input(
            "Pozisyon adı", key="custom_position", placeholder="Pozisyonu açık yaz, örn. Hukuk Danışmanı"
        ).strip()

    st.write("")
    level_col, type_col = st.columns(2, gap="large")
    with level_col:
        level = st.radio("Deneyim seviyesi", LEVELS, index=1, horizontal=True, key="level_choice")
    with type_col:
        interview_type = st.radio("Mülakat türü", INTERVIEW_TYPES, horizontal=True, key="type_choice")

    position = custom_position if s.selected_position == "Diğer" else s.selected_position

    st.write("")
    if st.button("Mülakatı Başlat", type="primary", disabled=not position):
        s.position = position
        s.level = level
        s.interview_type = interview_type
        reset_interview(page="interview")
        st.rerun()
    if not position:
        st.caption("Başlamak için bir pozisyon seç.")


def format_duration(seconds):
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes} dk {secs} sn" if minutes else f"{secs} sn"


def reset_interview(page="welcome"):
    s = st.session_state
    s.messages = []
    s.feedback = None
    s.error = None
    s.report = None
    s.start_time = None
    s.question_no = 1
    s.page = page


def report_page():
    s = st.session_state

    if s.report is None and not s.error:
        try:
            with st.spinner("Karne hazırlanıyor..."):
                result = llm.generate_report(
                    s.messages, s.position, s.level, s.interview_type
                )
            if not isinstance(result, dict) or result.get("error"):
                s.error = "Karne şu an oluşturulamadı, tekrar dene."
            else:
                s.report = result
                s.error = None
        except Exception:
            s.error = "Karne şu an oluşturulamadı, tekrar dene."

    if s.error:
        # Konuşma geçmişi silinmez: "Tekrar Dene" aynı konuşmayla karneyi yeniden ister.
        st.error(s.error)
        if st.button("Tekrar Dene", type="primary"):
            s.error = None
            st.rerun()
        if st.button("Yeni Mülakat"):
            reset_interview()
            st.rerun()
        return

    report = s.report
    duration = format_duration(time.time() - s.start_time) if s.start_time else None

    st.title("Mülakat karnen")
    caption = f"{s.position}, {s.level} seviye, {s.interview_type} mülakat"
    if duration:
        caption += f". Toplam süre: {duration}"
    st.caption(caption)
    st.write("")

    with st.container(key="score"):
        st.metric("Genel puan", f"{report['score']} / 10")
    st.write("")

    good_col, improve_col = st.columns(2, gap="large")
    with good_col:
        st.subheader("Güçlü yönler")
        for item in report["strengths"]:
            st.markdown(f'<div class="coach-good">{html.escape(item)}</div>', unsafe_allow_html=True)
    with improve_col:
        st.subheader("Geliştirilmesi gerekenler")
        for item in report["improvements"]:
            st.markdown(f'<div class="coach-warn">{html.escape(item)}</div>', unsafe_allow_html=True)

    st.write("")
    with st.container(key="startip"):
        st.info(report["star_tip"])

    with st.expander("Konuşmayı Göster"):
        for m in s.messages:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    st.write("")
    if st.button("Yeni Mülakat", type="primary"):
        reset_interview()
        st.rerun()


load_css()
init_state()

page = st.session_state.page
if page == "welcome":
    welcome_page()
elif page == "interview":
    interview_page()
else:
    report_page()