import type { FileData } from "@gradio/client";

export class Model3DGSCameraData {
	file: FileData;
    camera_pos?: [number, number, number];
	camera_rot?: [number, number, number];
	readonly meta = { _type: "gradio.Model3DGSCameraData" };

	constructor({
		file,
        camera_pos,
		camera_rot,
	}: {
		file: FileData;
        camera_pos?: [number, number, number];
		camera_rot?: [number, number, number];
	}) {
		this.file = file;
		this.camera_pos = camera_pos;
		this.camera_pos = camera_rot;
	}
}
