"""gr.Model3DGSCamera() component."""

from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING, Any, Callable, Sequence, Optional, Tuple
)

from gradio_client import handle_file
from gradio_client.documentation import document

from gradio.components.base import Component
from gradio.data_classes import GradioModel, FileData
from gradio.events import Events

if TYPE_CHECKING:
    from gradio.components import Timer

@document()
class Model3DGSCameraData(GradioModel):
    """
    A dataclass for file and camera poses.
    """
    file: FileData
    camera_pos: Optional[Tuple[float, float, float]] = None
    camera_rot: Optional[Tuple[float, float, float]] = None

@document()
class Model3DGSCamera(Component):
    """
    Creates a component allows users view 3D Model files (.splat or .ply).
    """

    EVENTS = [Events.change, Events.clear]

    data_model = Model3DGSCameraData

    def __init__(
        self,
        value: str | Callable | None = None,
        *,
        height: int | str | None = None,
        width: int | str | None = None,
        camera_width: int | None = None,
        camera_height: int | None = None,
        camera_fx: float | None = None,
        camera_fy: float | None = None,
        camera_near: float | None = None,
        camera_far: float | None = None,
        label: str | None = None,
        show_label: bool | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | None = None,
    ):
        """
        Parameters:
            value: path to (.obj, .glb, .stl, .gltf, .splat, or .ply) file to show in Model3DGSCamera viewer. If callable, the function will be called whenever the app loads to set the initial value of the component.
            height: The height of the Model3DGSCamera component, specified in pixels if a number is passed, or in CSS units if a string is passed.
            width: The width of the Model3DGSCamera component, specified in pixels if a number is passed, or in CSS units if a string is passed.
            camera_width: The width of camera in pixels.
            camera_height: The height of camera in pixels.
            camera_fx: The camera focal length.
            camera_fy: The camera focal length.
            camera_near: The camera near clip distance.
            camera_far: The camera far clip distance.
            interactive: if True, will allow users to upload a file; if False, can only be used to display files. If not provided, this is inferred based on whether the component is used as an input or output.
            label: The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            show_label: if True, will display label.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: if assigned, will be used to assume identity across a re-render. Components that have the same key across a re-render will have their value preserved.
        """
        self.height = height
        self.width = width
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera_fx = camera_fx
        self.camera_fy = camera_fy
        self.camera_near = camera_near
        self.camera_far = camera_far
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            value=value,
        )

    def preprocess(
        self, payload: Model3DGSCameraData | None
    ) -> Tuple[
        str | Path | None,
        Tuple[float, float, float] | None,
        Tuple[float, float, float] | None,
    ]:
        if payload is None:
            return None

        return payload.file.path, payload.camera_pos, payload.camera_rot

    def postprocess(
        self,
        value:
            str | Path | None |
            Tuple[
                str | Path,
                Tuple[float, float, float] | None,
                Tuple[float, float, float] | None
            ]
    ) -> Model3DGSCameraData | None:
        if value is None:
            return None

        if isinstance(value, (str, Path)):
            value = (value, None, None, None)
        elif isinstance(value, Tuple):
            if len(value) != 3:
                raise ValueError()
        else:
            raise TypeError()

        def check_tuple(value):
            if value is not None and (
                not isinstance(value, tuple) or len(value) != 3
            ):
                raise ValueError()

        check_tuple(value[1])
        check_tuple(value[2])

        return Model3DGSCameraData(
            file=FileData(path=str(value[0]), orig_name=Path(value[0]).name),
            camera_pos=value[1],
            camera_rot=value[2]
        )

    def api_info(self) -> dict[str, Any]:
        return super().api_info()

    def example_payload(self):
        return Model3DGSCameraData(file=handle_file(
            "https://raw.githubusercontent.com/gradio-app/gradio/main/demo/model3D/files/Fox.gltf"
        ))

    def example_value(self):
        return "https://raw.githubusercontent.com/gradio-app/gradio/main/demo/model3D/files/Fox.gltf"
