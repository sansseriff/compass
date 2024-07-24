<script>
	import { onMount, onDestroy } from 'svelte';

	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

    function customEasing(t) {
        // This is a simple example of a custom easing function
        // that slows down more than cubicOut. You can adjust the
        // math to achieve the desired effect.
        return 1 - Math.pow(1 - t, 2);
    }

	export let loading = false;
    export let time_scalar = 1;
	const progress = tweened(0, {
		easing: customEasing
	});



	const opacity = tweened(0, { easing: cubicOut });
	function handleLoading() {
		opacity.set(0.5, { duration: 0 });
		progress.set(0.9, { duration: time_scalar*1000 + 1700 });
	}
	function handleLoaded() {
		const duration = 500;

		progress.set(1, { duration });
		opacity.set(0, { duration: duration / 2, delay: duration / 2 });

		setTimeout(() => {
			progress.set(0, { duration: 0 });
		}, duration);
	}
	$: loading ? handleLoading() : loading === false ? handleLoaded() : undefined;
</script>

<div class="progress-container" style={`opacity: ${$opacity}`}>
	<div class="progress" style={`--width: ${$progress}`} />
</div>

<style>
	.progress-container {
		position: sticky;
		top: 0;
		left: 0;
		width: 100%;
		pointer-events: none;
		contain: paint;
		height: 0.3em;
		z-index: 999;
		will-change: opacity;

		background-color: hsla(345deg, 10%, 18%, 0.3);
	}
	.progress {
		left: 0;
		top: 0;
		height: 100%;
		background-color: #ff0040;
		pointer-events: none;
		transform-origin: left;
		transform: scaleX(var(--width));
	}
</style>