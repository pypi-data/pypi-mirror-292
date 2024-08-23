import gradio as gr
from gradio_model3dgscamera import Model3DGSCamera

with gr.Blocks() as demo:
    file = gr.File()
    with gr.Row():
        kwargs = dict(
            width=512,
            height=512,
            camera_width=512,
            camera_height=512,
            camera_fx=491.52,
            camera_fy=491.52,
            camera_near=0.01,
            camera_far=100
        )
        viewer = Model3DGSCamera(**kwargs)
        viewer2 = Model3DGSCamera(**kwargs)
    button = gr.Button(value='Get camera pose')

    def set_viewer(file):
        return file, (0, 0, -4.6804), None

    file.upload(set_viewer, file, viewer)
    button.click(lambda x: x, viewer, viewer2)

if __name__ == "__main__":
    demo.launch()
