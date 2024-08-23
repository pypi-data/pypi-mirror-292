<script lang="ts">
	import type { Model3DGSCameraData } from "./Model3DGSCameraData.ts";
	import { BlockLabel, IconButton } from "@gradio/atoms";
	import { File, Download, Undo } from "@gradio/icons";
	import type { I18nFormatter } from "@gradio/utils";
	import { dequal } from "dequal";
	import type Canvas3DGSCamera from "./Canvas3DGSCamera.svelte";

	export let value: Model3DGSCameraData | null = null;
	export let label = "";
	export let show_label: boolean;
	export let i18n: I18nFormatter;
	export let camera_width: number | null = null;
	export let camera_height: number | null = null;
	export let camera_fx: number | null = null;
	export let camera_fy: number | null = null;
	export let camera_near: number | null = null;
	export let camera_far: number | null = null;

	let Canvas3DGSComponent: typeof Canvas3DGSCamera;
	async function loadCanvas3DGS(): Promise<typeof Canvas3DGSCamera> {
		const module = await import("./Canvas3DGSCamera.svelte");
		return module.default;
	}
	$: if (value) {
		loadCanvas3DGS().then((component) => {
			Canvas3DGSComponent = component;
		});
	}

	let canvas3dgscamera: Canvas3DGSCamera | undefined;
	function handle_undo(): void {
		canvas3dgscamera?.reset_camera_pose();
	}

	let resolved_url: string | undefined;
</script>

<BlockLabel
	{show_label}
	Icon={File}
	label={label || i18n("3D_model.3d_model")}
/>
{#if value}
	<div class="model3DGSCamera">
		<div class="buttons">
			<IconButton Icon={Undo} label="Undo" on:click={() => handle_undo()} />
			<a
				href={resolved_url}
				target={window.__is_colab__ ? "_blank" : null}
				download={window.__is_colab__ ? null : value.file.orig_name || value.file.path}
			>
				<IconButton Icon={Download} label={i18n("common.download")} />
			</a>
		</div>

		<svelte:component
			this={Canvas3DGSComponent}
			bind:this={canvas3dgscamera}
			bind:resolved_url
			{value}
			{camera_width}
	 		{camera_height}
	 		{camera_fx}
	 		{camera_fy}
	 		{camera_near}
	 		{camera_far}
		/>
	</div>
{/if}

<style>
	.model3DGSCamera {
		display: flex;
		position: relative;
		width: var(--size-full);
		height: var(--size-full);
		border-radius: var(--block-radius);
		overflow: hidden;
	}
	.model3DGSCamera :global(canvas) {
		width: var(--size-full);
		height: var(--size-full);
		object-fit: contain;
		overflow: hidden;
	}
	.buttons {
		display: flex;
		position: absolute;
		top: var(--size-2);
		right: var(--size-2);
		justify-content: flex-end;
		gap: var(--spacing-sm);
		z-index: var(--layer-5);
	}
</style>
