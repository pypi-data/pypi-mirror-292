import gradio as gr
from gradio_path_selector import PathSelector

with gr.Blocks() as demo:
    PathSelector()

if __name__ == "__main__":
    demo.launch()

