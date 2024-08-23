
import gradio as gr
from app import demo as app
import os

_docs = {'Model3DGSCamera': {'description': 'Creates a component allows users view 3D Model files (.splat or .ply).', 'members': {'__init__': {'value': {'type': 'str | Callable | None', 'default': 'None', 'description': 'path to (.obj, .glb, .stl, .gltf, .splat, or .ply) file to show in Model3DGSCamera viewer. If callable, the function will be called whenever the app loads to set the initial value of the component.'}, 'height': {'type': 'int | str | None', 'default': 'None', 'description': 'The height of the Model3DGSCamera component, specified in pixels if a number is passed, or in CSS units if a string is passed.'}, 'width': {'type': 'int | str | None', 'default': 'None', 'description': 'The width of the Model3DGSCamera component, specified in pixels if a number is passed, or in CSS units if a string is passed.'}, 'camera_width': {'type': 'int | None', 'default': 'None', 'description': 'The width of camera in pixels.'}, 'camera_height': {'type': 'int | None', 'default': 'None', 'description': 'The height of camera in pixels.'}, 'camera_fx': {'type': 'float | None', 'default': 'None', 'description': 'The camera focal length.'}, 'camera_fy': {'type': 'float | None', 'default': 'None', 'description': 'The camera focal length.'}, 'camera_near': {'type': 'float | None', 'default': 'None', 'description': 'The camera near clip distance.'}, 'camera_far': {'type': 'float | None', 'default': 'None', 'description': 'The camera far clip distance.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will allow users to upload a file; if False, can only be used to display files. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | None', 'default': 'None', 'description': 'if assigned, will be used to assume identity across a re-render. Components that have the same key across a re-render will have their value preserved.'}}, 'postprocess': {'value': {'type': 'str\n    | pathlib.Path\n    | None\n    | tuple[\n        str | pathlib.Path,\n        tuple[float, float, float] | None,\n        tuple[float, float, float] | None,\n    ]', 'description': "The output data received by the component from the user's function in the backend."}}, 'preprocess': {'return': {'type': 'tuple[\n    str | pathlib.Path | None,\n    tuple[float, float, float] | None,\n    tuple[float, float, float] | None,\n]', 'description': "The preprocessed input data sent to the user's function in the backend."}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the Model3DGSCamera changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'clear': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clears the Model3DGSCamera using the X button for the component.'}}}, '__meta__': {'additional_interfaces': {}}, 'Model3DGSCameraData': {'description': 'A dataclass for file and camera poses.', 'members': {'__init__': {'data': {'type': 'Any', 'description': None}, 'return': {'type': 'None', 'description': None}}}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_model3dgscamera`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.3%20-%20orange"> <a href="https://github.com/hellnear/gradio-model3dgscamera/issues" target="_blank"><img alt="Static Badge" src="https://img.shields.io/badge/Issues-white?logo=github&logoColor=black"></a> 
</div>

3DGS viewer with camera control
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_model3dgscamera
```

## Usage

```python
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

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `Model3DGSCamera`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["Model3DGSCamera"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["Model3DGSCamera"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, the preprocessed input data sent to the user's function in the backend.
- **As output:** Should return, the output data received by the component from the user's function in the backend.

 ```python
def predict(
    value: tuple[
    str | pathlib.Path | None,
    tuple[float, float, float] | None,
    tuple[float, float, float] | None,
]
) -> str
    | pathlib.Path
    | None
    | tuple[
        str | pathlib.Path,
        tuple[float, float, float] | None,
        tuple[float, float, float] | None,
    ]:
    return value
```
""", elem_classes=["md-custom", "Model3DGSCamera-user-fn"], header_links=True)


    gr.Markdown("""
## `Model3DGSCameraData`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["Model3DGSCameraData"]["members"]["__init__"], linkify=[])







    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {};
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
