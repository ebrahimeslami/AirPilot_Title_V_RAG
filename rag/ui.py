import gradio as gr
from .query import answer
from .workflows import applicability_check, StepResult

def ask(q):
    text, cites = answer(q, k=6)
    cite_lines = []
    for c in cites:
        cite_lines.append(f"- [{c['title']}]({c['source']}) @ ~{c['offset']} (score={c['score']:.3f})")
    return text, "\n".join(cite_lines)

def run_app():
    with gr.Blocks(title="Texas Title V RAG") as demo:
        gr.Markdown("# Texas Title V RAG (Human-in-the-Loop)")
        inp = gr.Textbox(label="Ask a question (e.g., CAM applicability for boilers)")
        out = gr.Textbox(label="Retrieved Context", lines=16)
        cites = gr.Markdown(label="Citations")
        btn = gr.Button("Search")
        btn.click(fn=ask, inputs=inp, outputs=[out, cites])
    demo.launch()

if __name__ == "__main__":
    run_app()
