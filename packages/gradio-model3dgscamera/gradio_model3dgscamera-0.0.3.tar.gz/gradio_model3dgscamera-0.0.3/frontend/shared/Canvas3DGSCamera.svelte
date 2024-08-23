<script lang="ts">
	import { onMount } from "svelte";
	import * as SPLAT from "gsplat";
	import type { Model3DGSCameraData } from "./Model3DGSCameraData.ts";
	import { resolve_wasm_src } from "@gradio/wasm/svelte";

	export let value: Model3DGSCameraData | null = null;
	export let camera_width: number | null = null;
	export let camera_height: number | null = null;
	export let camera_fx: number | null = null;
	export let camera_fy: number | null = null;
	export let camera_near: number | null = null;
	export let camera_far: number | null = null;

	let init_camera_pos: SPLAT.Vector3 = new SPLAT.Vector3(0, 0, -5);
	let init_camera_rot: SPLAT.Quaternion = new SPLAT.Quaternion();
	let init_camera_at: SPLAT.Vector3 = new SPLAT.Vector3(0, 0, 0);

	$: url = value.file.url;

	/* URL resolution for the Wasm mode. */
	export let resolved_url: typeof url = undefined;

	let latest_url: typeof url;
	$: {
		resolved_url = url;

		if (url) {
			latest_url = url;
			const resolving_url = url;
			resolve_wasm_src(url).then((resolved) => {
				if (latest_url === resolving_url) {
					resolved_url = resolved ?? undefined;
				} else {
					resolved && URL.revokeObjectURL(resolved);
				}
			});
		}
	}

	let canvas: HTMLCanvasElement;
	let scene: SPLAT.Scene;
	let camera: SPLAT.Camera;
	let renderer: SPLAT.WebGLRenderer | null = null;
	let controls: SPLAT.OrbitControls;
	let mounted = false;
	let frameId: number | null = null;

	function update_camera() {
		value.camera_pos = [
			camera.position.x, camera.position.y, camera.position.z
		];
		let euler = camera.rotation.toEuler()
		value.camera_rot = [
			euler.x, euler.y, euler.z
		];
	}

	function reset_scene(): void {
		if (frameId !== null) {
			cancelAnimationFrame(frameId);
			frameId = null;
		}

		if (renderer !== null) {
			renderer.dispose();
			renderer = null;
		}

		scene = new SPLAT.Scene();
		camera = new SPLAT.Camera();
		renderer = new SPLAT.WebGLRenderer(canvas);
		controls = new SPLAT.OrbitControls(camera, canvas);
		controls.setCameraTarget(init_camera_at)

		if (!value) {
			return;
		}

		reset_camera_param(
			camera_width, camera_height, camera_fx, camera_fy, camera_near,
	 		camera_far
		);
		reset_camera_pose(value.camera_pos, value.camera_rot);
		camera.addEventListener("objectChanged", update_camera);

		let loading = false;
		const load = async (): Promise<void> => {
			if (loading) {
				console.error("Already loading");
				return;
			}
			if (!resolved_url) {
				throw new Error("No resolved URL");
			}
			loading = true;
			if (resolved_url.endsWith(".ply")) {
				await SPLAT.PLYLoader.LoadAsync(resolved_url, scene, undefined);
			} else if (resolved_url.endsWith(".splat")) {
				await SPLAT.Loader.LoadAsync(resolved_url, scene, undefined);
			} else {
				throw new Error("Unsupported file type");
			}
			loading = false;
		};

		const frame = (): void => {
			if (!renderer) {
				return;
			}

			if (loading) {
				frameId = requestAnimationFrame(frame);
				return;
			}

			controls.update();
			renderer.render(scene, camera);

			frameId = requestAnimationFrame(frame);
		};

		load();
		frameId = requestAnimationFrame(frame);
	}

	onMount(() => {
		if (value != null) {
			reset_scene();
		}
		mounted = true;

		return () => {
			if (renderer) {
				renderer.dispose();
			}
		};
	});

	$: ({ path } = value.file || {
		path: undefined
	});

	$: canvas && mounted && path && reset_scene();

	export function reset_camera_pose(
		position: [number, number, number] | null = null,
		rotation: [number, number, number] | null = null
	): void {
		if (camera) {
			if (position) {
				 init_camera_pos = new SPLAT.Vector3(
					position[0], position[1], position[2]
				 );
			}
			camera.position = init_camera_pos;

			if (rotation) {
				init_camera_rot = SPLAT.Quaternion.FromEuler(new SPLAT.Vector3(
					rotation[0], rotation[1], rotation[2]
				));
			}
			camera.rotation = init_camera_rot;
		}
	}

	export function reset_camera_param(
		camera_width: number | null = null,
		camera_height: number | null = null,
	 	camera_fx: number | null = null,
	 	camera_fy: number | null = null,
	 	camera_near: number | null = null,
	 	camera_far: number | null = null
	): void {
		if (camera_width && camera_height) {
			camera.data.setSize(camera_width, camera_height);
		}
		if (camera_fx) {
			camera.data.fx = camera_fx;
		}
		if (camera_fy) {
			camera.data.fy = camera_fy;
		}
		if (camera_near) {
			camera.data.near = camera_near;
		}
		if (camera_far) {
			camera.data.far = camera_far;
		}
	}

</script>

<canvas bind:this={canvas}></canvas>
