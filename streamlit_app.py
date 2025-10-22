import streamlit as st
import html
from examples import examples
# ---------- Beispielhafte Datenstruktur ----------
examples = examples

# ---------- Hilfsfunktion zum Markieren von Halluzinationen ----------
def render_hallucinations(answer: str, hallucinations):
    """Markiere Halluzinationen im Text mit farbigen <span>-Tags"""
    if not hallucinations:
        return answer

    hallucinations = sorted(hallucinations, key=lambda x: x["start"], reverse=True)
    for h in hallucinations:
        start = h.get("start", -1)
        end = h.get("end", -1)
        conf = h.get("confidence", 0)
        explanation = h.get("explanation", "")
        text = h.get("text", "")

        # Suche Text, falls Startpositionen ungenau sind
        found_index = answer.find(text)
        if found_index != -1:
            start = found_index
            end = found_index + len(text)

        if start < 0 or end > len(answer) or start >= end:
            continue

        # Farbe nach Konfidenz
        if conf > 0.8:
            color = "rgba(255, 77, 77, 0.3)"   # Rot = stark halluziniert
        elif conf > 0.4:
            color = "rgba(255, 166, 77, 0.3)"  # Orange = unsicher
        else:
            color = "rgba(255, 255, 204, 0.3)" # gelb = eher korrekt

        title = f"Confidence: {conf:.2f}\nExplanation: {explanation}"
        title = html.escape(title, quote=True)
        span = f"<span style='background-color:{color}' title=\"{title}\">{answer[start:end]}</span>"

        answer = answer[:start] + span + answer[end:]
    return answer


# ---------- Haupt-App ----------
def main():
    st.set_page_config(page_title="RAG-Halluzinationen", page_icon="🤖")
    st.title("🧠 Simulation: RAG-Chatbot mit markierten Halluzinationen")

    st.markdown("""
Diese Demo zeigt simulierte Antworten eines RAG-Chatbots.  
**Einige Antworten enthalten Halluzinationen**, die farbig markiert sind.  
Fahre mit der Maus über markierte Textstellen, um Details zu sehen.
    """)

    # Zustand verwalten
    if "index" not in st.session_state:
        st.session_state.index = 0

    ex = examples[st.session_state.index]

    # Prompt anzeigen
    st.subheader("🗨️ Prompt")
    st.info(ex["prompt"])

    # Antwort anzeigen
    st.subheader("💬 Antwort des Chatbots")
    rendered = render_hallucinations(ex["answer"], ex["hallucinations"])
    st.markdown(rendered, unsafe_allow_html=True)

    # Kontext ausklappbar unter der Antwort
    with st.expander("📚 Kontext anzeigen"):
        st.write(ex["context"])

    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Zurück", disabled=st.session_state.index == 0):
            st.session_state.index -= 1
            st.rerun()
    with col2:
        if st.button("Weiter ➡️", disabled=st.session_state.index == len(examples) - 1):
            st.session_state.index += 1
            st.rerun()

    st.caption(f"Beispiel {st.session_state.index + 1} von {len(examples)}")


if __name__ == "__main__":
    main()
