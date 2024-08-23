<script context="module" lang="ts">
	export { default as BaseModel3DGSCamera } from "./shared/Model3DGSCamera.svelte";
	export { default as BaseExample } from "./Example.svelte";
</script>

<script lang="ts">
	import type { Model3DGSCameraData } from "./shared/Model3DGSCameraData.ts";
	import Model3DGSCamera from "./shared/Model3DGSCamera.svelte";
	import { BlockLabel, Block, Empty } from "@gradio/atoms";
	import { File } from "@gradio/icons";

	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { Gradio } from "@gradio/utils";

	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: Model3DGSCameraData | null = null;
	export let loading_status: LoadingStatus;
	export let label: string;
	export let show_label: boolean;
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let gradio: Gradio;
	export let height: number | undefined = undefined;
	export let width: number | undefined = undefined;
	export let camera_width: number | null = null;
	export let camera_height: number | null = null;
	export let camera_fx: number | null = null;
	export let camera_fy: number | null = null;
	export let camera_near: number | null = null;
	export let camera_far: number | null = null;

	let dragging = false;
</script>

<Block
	{visible}
	variant={value === null ? "dashed" : "solid"}
	border_mode={dragging ? "focus" : "base"}
	padding={false}
	{elem_id}
	{elem_classes}
	{container}
	{scale}
	{min_width}
	{height}
	{width}
>
	<StatusTracker
		autoscroll={gradio.autoscroll}
		i18n={gradio.i18n}
		{...loading_status}
		on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
	/>

	{#if value}
		<Model3DGSCamera
			{value}
			i18n={gradio.i18n}
			{label}
			{show_label}
			{camera_width}
	 		{camera_height}
	 		{camera_fx}
	 		{camera_fy}
	 		{camera_near}
	 		{camera_far}
		/>
	{:else}
		<!-- Not ideal but some bugs to work out before we can
				make this consistent with other components -->

		<BlockLabel {show_label} Icon={File} label={label || "3D Model"} />

		<Empty unpadded_box={true} size="large"><File /></Empty>
	{/if}
</Block>
