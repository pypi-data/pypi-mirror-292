<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { BlockTitle } from "@gradio/atoms";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { tick } from "svelte";

	export let gradio: Gradio<{
		change: never;
		clear_status: LoadingStatus;
	}>;
	export let label = "Path Selector";
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value = "";
	export let show_label: boolean;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus | undefined = undefined;

	let copying: boolean = false;

	let path = "";
	let directories = [];
	let files = [];
	let separator = "/";
	let selected_file_idx = -1;

	let full_path = path;

	function handle_change(): void {
		let obj = JSON.parse(value);
		if (obj.status == "download") {
			path = obj.current_path;
			directories = obj.directories;
			files = obj.files;
			separator = obj.separator;
			update_full_filename();
		}
	}

	function click(inode_idx, type): void {
		if (type === "dict") {
			let obj = {
				"selected_inode": inode_idx === -1 ? -1 : directories[inode_idx],
				"current_path": path,
				"status": "upload",
			}
			value = JSON.stringify(obj)
			selected_file_idx = -1;
			gradio.dispatch("change");
		} else if (type === "file") {
			if (selected_file_idx === inode_idx) {
				// It's already selected so de-select it
				selected_file_idx = -1;
			} else {
				selected_file_idx = inode_idx;
			}
			update_full_filename();
		}
	}

	function copy(): void {
		// Copy the text inside the text field
		navigator.clipboard.writeText(full_path);
		if (!copying) {
			copying = true
			setTimeout(() => {
				if (copying) copying = false;
			}, 1000);
		}
	}

	function update_full_filename(): void {
		let fullname = path;
		if (selected_file_idx != -1) {
			fullname = fullname + separator + files[selected_file_idx]
		}
		full_path = fullname
	}

	$: if (value === null) value = "";

	// When the value changes, dispatch the change event via handle_change()
	// See the docs for an explanation: https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive
	$: value, handle_change();


</script>

<Block
	{visible}
	{elem_id}
	{elem_classes}
	{scale}
	{min_width}
	allow_overflow={false}
	padding={true}
>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
			on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
		/>
	{/if}

	<BlockTitle {show_label} info={undefined}>{label}</BlockTitle>

	<div class="parent">
		<div
			class="scroll-hide path_box"
		>{full_path}</div>
		<button
			class="submit_btn lg secondary svelte-cmf5ev"
			on:click={copy}
		>
		<div>
			<svg class="clippy_icon" width="16" height="16" viewBox="0 0 16 16" class:copying>
				<path class="path1" d="M5.75 4.75H10.25V1.75H5.75V4.75Z" />
				<path class="path2" d="M3.25 2.88379C2.9511 3.05669 2.75 3.37987 2.75 3.75001V13.25C2.75 13.8023 3.19772 14.25 3.75 14.25H12.25C12.8023 14.25 13.25 13.8023 13.25 13.25V3.75001C13.25 3.37987 13.0489 3.05669 12.75 2.88379" />
			</svg>
			<svg class="check_icon" width="16" height="16" viewBox="0 0 16 16" class:copying>
				<circle cx=8 cy=8 r=8 style="fill: green; stroke-width: 0;"/>
				<path d="M13.25 4.75L6 12L2.75 8.75" />
			</svg>
		</div>
		Copy path
		</button>
	</div>

	<div class="inodes">
		<div
			class="inode_option"
			role="button"
			on:click={() => click(-1, "dict")}
			on:keypress={() => click(-1, "dict")}
			tabindex="0"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"
					width="16" height="16" style="display: inline; fill: white;">
					<polygon points="0 45, 45 10, 45 80"/>
					<polygon points="40 45, 85 10, 85 80"/>
				</svg>
				Up
		</div>
		{#each directories as directory, i}
			<div
				class="inode_option"
				role="button"
				on:click={() => click(i, "dict")}
				on:keypress={() => click(i, "dict")}
				tabindex="0"
			>
				<svg
					aria-hidden="true" focusable="false" role="img" class="Octicon-sc-9kayk9-0 fczqEI" viewBox="0 0 16 16"
					width="16" height="16" fill="currentColor" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;"
				>
					<path d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"></path>
				</svg>
				{directory}
			</div>
		{/each}
		{#each files as filename, i}
			<div
				class="inode_option"
				class:selected={selected_file_idx === i}
				role="button"
				on:click={() => click(i, "file")}
				on:keypress={() => click(i, "file")}
				tabindex="0"
			>
				<svg
					aria-hidden="true" focusable="false" role="img" class="color-fg-muted"
					viewBox="0 0 16 16" width="16" height="16" fill="currentColor" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;">
						<path d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16h-9.5A1.75 1.75 0 0 1 2 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V1.5Zm6.75.062V4.25c0 .138.112.25.25.25h2.688l-.011-.013-2.914-2.914-.013-.011Z"></path>
				</svg>
				{filename}
			</div>
		{/each}
	</div>

</Block>

<style>
	*,
	*:after,
	*:before{
		-webkit-box-sizing: border-box;
		-moz-box-sizing: border-box;
		box-sizing: border-box;
	}

	.parent {
		display: grid;
	    grid-template-columns: 4fr minmax(max-content, 1fr);
		grid-column-gap: min(20px, 5vw);
	}

	.path_box {
		position: relative;
		outline: none !important;
		box-shadow: var(--input-shadow);
		background: var(--input-background-fill);
		padding: var(--input-padding);
		width: 100%;
		color: var(--body-text-color);
		font-weight: var(--input-text-weight);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: 10px;
	}

	.parent>* {
		display: inline-block
	}

	.submit_btn {
		display: inline-flex;
		width: 100%;
		align-items: center;
  		justify-content: center;
	}

	.submit_btn>div {
		position: relative;
		width: 16px;
		height: 16px;
		margin-right: 5px;
	}
	.submit_btn>div>svg {
		position: absolute;
		width: inherit;
		height: inherit;
		fill: "none";
		stroke: white;
		width: 16px;
		height: 16px;
		stroke-width: "1.5";
		stroke-linecap: "round";
		stroke-linejoin: "round";

	}

	svg.clippy_icon {
		fill: grey;
		color: white;
		top: 0;
		left: 0;
		opacity: 1;
		stroke-dasharray: 50;
		stroke-dashoffset: 0;
		transition: all 300ms ease-in-out;
		stroke-width: 1.5;
		stroke-opacity: 1;
	}
	.path2 {
		fill-opacity: 0.3;
	}
	svg.check_icon {
		fill: transparent;
		top: 0;
		left: 0;
		opacity: 0;
		stroke-dasharray: 50;
		stroke-dashoffset: -50;
		stroke-width: 1.5;
		transition: all 300ms ease-in-out;
	}
	svg.clippy_icon.copying {
		stroke-dashoffset: -50;
		opacity: 0;
	}
	svg.check_icon.copying {
		stroke-dashoffset: 0;
		opacity: 1;
	}

	.inodes {
		border-radius: 5px;
		border-width: 2px;
		border-color: grey;
		max-height: 300px;
		overflow-y: scroll;
		margin-top: 1em;
	}

	.inode_option {
		padding-left: 5px;
		padding-top: auto;
		padding-bottom: auto;
		border-color: grey;
		border-width: 1px;
		background-color: #555555;
		transition: background-color 0.2s ease-in-out;
	}

	.inode_option:hover, .inode_option.selected {
		background-color: #198754 ;
	}
</style>
