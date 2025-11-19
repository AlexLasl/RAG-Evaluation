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

def render_token(tokens_with_probs: list[dict]) -> str:
        """
        Nimmt eine Liste von Dicts mit Struktur
        [{'token': <str>,  'prob': <float>}, ...]
        und gibt einen HTML-String zurück, in dem Tokens farblich markiert sind.
        """
        highlighted = ""
        print("in token visualisation")

        for item in tokens_with_probs:
            token = item["token"]
            conf = item["prob"]  # Wahrscheinlichkeit, dass Token halluziniert ist

            # Farbcodierung je nach Schwellenwert
            if conf > 0.7:
                color = "rgba(255, 77, 77, 0.3)"   # Rot = stark halluziniert
            elif conf > 0.4:
                color = "rgba(255, 166, 77, 0.3)"  # Orange = unsicher
            elif conf > 0.05:
                color = "rgba(255, 255, 204, 0.5)" # gelb = eher korrekt

            else:
                color = "transparent"  # keine Markierung

            if color == "transparent":
                highlighted += token
            else:
                highlighted += (
                    f"<span style='background-color:{color}' title='p={conf:.2f}'>"
                    f"{token}</span>"
                )
        return highlighted
# ---------- Haupt-App ----------
def main():
    st.set_page_config(page_title="RAG-Halluzinationen", page_icon="🤖")
    st.title("RAG-Chabot Evaluation")
    # Zustand verwalten
    if "index" not in st.session_state:
        st.session_state.index = 0
    ex = examples[st.session_state.index]



    if ex["id"] <= 1:
       
       st.markdown("""
Diese Demo zeigt simulierte Antworten eines RAG-Chatbots.  

    """)
    elif ex["id"]==2:
        st.markdown("""
Die farblichen Markierungen im Text heben Passagen hervor, die von einem automatischen Erkennungssystem als potenziell fehlerhaft eingestuft wurden. Die Farbintensität gibt dabei an, wie sicher sich das System in seiner Einschätzung ist:

- <span style='background-color:rgba(255, 77, 77, 0.3); padding:2px 4px; border-radius:4px;'>Rot: mit hoher Sicherheit fehlerhaft</span>  
- <span style='background-color:rgba(255, 166, 77, 0.3); padding:2px 4px; border-radius:4px;'>Orange: möglicherweise fehlerhaft</span>  
- <span style='background-color:rgba(255, 255, 204, 0.5); padding:2px 4px; border-radius:4px;'>Gelb: mit geringer Sicherheit fehlerhaft</span>
""", unsafe_allow_html=True)
    else:
         st.markdown("""
Die farblichen Markierungen im Text heben Passagen hervor, die von einem automatischen Erkennungssystem als potenziell fehlerhaft eingestuft wurden. Die Farbintensität gibt dabei an, wie sicher sich das System in seiner Einschätzung ist:

- <span style='background-color:rgba(255, 77, 77, 0.3); padding:2px 4px; border-radius:4px;'>Rot: mit hoher Sicherheit fehlerhaft</span>  
- <span style='background-color:rgba(255, 166, 77, 0.3); padding:2px 4px; border-radius:4px;'>Orange: möglicherweise fehlerhaft</span>  
- <span style='background-color:rgba(255, 255, 204, 0.5); padding:2px 4px; border-radius:4px;'>Gelb: mit geringer Sicherheit fehlerhaft</span> \n
Zusätzlich wird eine kurze Erklärung zur Einschätzung angezeigt.
""", unsafe_allow_html=True)


    

    

    # Prompt anzeigen
    st.subheader("🗨️ Prompt")
    st.info(ex["prompt"])

    # Antwort anzeigen
    st.subheader("💬 Antwort des Chatbots")
    if ex["id"] <= 1:
        rendered = ex["answer"]
    elif ex["id"] <= 2:
        rendered = render_token(ex["halucinations_token"])
    else:
        rendered = render_hallucinations(ex["answer"], ex["hallucinations"])
    st.markdown(rendered, unsafe_allow_html=True)

    print(repr(ex["context"][:20]))
    # Kontext ausklappbar unter der Antwort
    with st.expander("📚 Quellen anzeigen"):
        st.markdown(
        f"<div style='white-space: pre-line; margin: 0; font-family: sans-serif;'>{html.escape(ex['context'])}</div>",
        unsafe_allow_html=True
    )

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
