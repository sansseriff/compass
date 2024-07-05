<script lang="ts">
  // import svelteLogo from './assets/svelte.svg'
  // import viteLogo from '/vite.svg'
  // import Counter from './lib/Counter.svelte'

  //borrowing from https://github.com/motion-canvas/motion-canvas/blob/main/packages/docs/src/components/Fiddle/SharedPlayer.ts

  // import type {
  //   FullSceneDescription,
  //   Player as PlayerType,
  //   Project,
  //   Stage as StageType,
  //   ThreadGeneratorFactory,
  // } from "@motion-canvas/core";

  import type { Player as PlayerType } from "@motion-canvas/core";
  import { Circle, View2D } from "@motion-canvas/2d";

  // // originally loaded client side
  import {
    Logger,
    Player,
    ProjectMetadata,
    Stage,
    ValueDispatcher,
    DefaultPlugin,
    createRef,
    all,
  } from "@motion-canvas/core";

  import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";
  import { onMount } from "svelte";
  import { borrowPlayer, updatePlayer } from "./util.svelte";
  import { ratio } from "./util.svelte"

  // import { Description } from "./app";

  
  let player: PlayerType | null = $state(null);
  let inputText = $state("");
  

  let previewRef: HTMLDivElement;

  

  function createScene() {
    const Description = makeScene2D(function* (view) {
      // view.fill('#242424'); // set the background of this scene
      const circle = new Circle({
        x: -100,
        y: 0,
        width: 100,
        height: 100,
        fill: "#e13238",
      });

      const myCircle = createRef<Circle>();
      view.add(circle);
      yield* all(
        circle.position.x(100, 1).to(-100, 1),
        circle.fill("#e6a700", 1).to("#e13238", 1)
      );
    }) as FullSceneDescription<ThreadGeneratorFactory<View2D>>;

    return Description;
  }

  function otherScene() {
    const Description = makeScene2D(function* (view) {
      // view.fill('#242424'); // set the background of this scene
      const circle = new Circle({
        x: -100,
        y: 0,
        width: 100,
        height: 100,
        fill: "#000000",
      });

      const myCircle = createRef<Circle>();
      view.add(circle);
      yield* all(
        circle.position.x(100, 1).to(-100, 1),
        circle.fill("#fffff2", 1).to("#000000", 1)
      );
    }) as FullSceneDescription<ThreadGeneratorFactory<View2D>>;

    return Description;
  }

  function init() {
    const scene = createScene();

    const containerWidth = document.body.clientWidth;
    const initialWidthPx = document.body.clientWidth * (writingAreaWidth / 100);

    const rightWidthPx = containerWidth - initialWidthPx
    player = borrowPlayer(previewRef, player, rightWidthPx);
    updatePlayer(scene);
  }

  
  function swapScene() {
    const scene = otherScene();
    // player = borrowPlayer(previewRef, player, writingAreaWidth);
    updatePlayer(scene);
  }
  
  // init();

  onMount(() => {
    init();

    console.log("player: ", player);
    // PlayerInstance.togglePlayback();
  });

  let writingAreaWidth = $state(30); // Initial width in percentage

  function startDrag(event) {
    const startX = event.clientX;
    // Convert initialWidth from percentage to pixels for accurate calculation
    const initialWidthPx = document.body.clientWidth * (writingAreaWidth / 100);

    function onMouseMove(event) {
      const dx = event.clientX - startX;
      const containerWidth = document.body.clientWidth;

      // Calculate new width in pixels, then convert back to percentage

      const newWidthPx = initialWidthPx + dx;

      const rightWidthPx = containerWidth - newWidthPx;

      const scene = createScene();
      player = borrowPlayer(previewRef, player, newWidthPx);
      updatePlayer(scene);

      console.log("right width: ", rightWidthPx);

      // console.log("setting new width: ", newWidthPx);

      writingAreaWidth = (newWidthPx * 100) / containerWidth;
    }

    function onMouseUp() {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    }

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  }


  function setWidth(width_string: string) {
    writingAreaWidth = parseInt(width_string);

    const containerWidth = document.body.clientWidth;

    const scene = createScene();
    player = borrowPlayer(previewRef, player, writingAreaWidth);
    updatePlayer(scene);
  }
</script>

<div class="left-right">
  <!-- style="width: {writingAreaWidth}%; -->
  <div class="writing-area">
    <textarea name="paragraph_text" rows="10" style="width: 100%;"></textarea>
  </div>
  <div class="divider" onmousedown={startDrag}></div>
  <!-- style="width: {100 - writingAreaWidth}%;" -->
  <div class="visual-area" >
    <div class="preview" style="aspect-ratio: 2" bind:this={previewRef}>
      {#if !player}
        <div>Press play to preview the animation</div>
      {/if}
    </div>
    <button onclick={() => player.togglePlayback()}
      >toggle playback</button
    >
    <input bind:value={inputText} type="text">
    <button onclick={() => setWidth(inputText)}>Submit</button>

    <button onclick={swapScene}>New Scene</button>
  </div>
</div>

<style>
  .left-right {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    height: 100vh;
  }

  .writing-area textarea {
    width: 100%; /* Ensures the textarea fills its container */
    height: auto; /* Adjusts height based on content, can set to a fixed height if preferred */
    padding: 12px; /* Adds some space inside the textarea for text */
    border: 1px solid #ccc; /* Subtle border color */
    border-radius: 8px; /* Rounded corners for a modern look */
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1); /* Inner shadow for depth */
    outline: none; /* Removes the default focus outline */
    resize: vertical; /* Allows vertical resizing only */
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; /* Modern, readable font */
    font-size: 16px; /* Adequate font size for readability */
    line-height: 1.5; /* Spacing between lines */
    color: #333; /* Darker text for better readability */
    background-color: #f9f9f9; /* Light background color */
    transition:
      border-color 0.3s,
      box-shadow 0.3s; /* Smooth transition for focus effect */
  }

  .writing-area textarea:focus {
    border-color: #007bff; /* Highlight color when focused */
    box-shadow:
      inset 0 1px 3px rgba(0, 0, 0, 0.1),
      0 0 8px rgba(0, 123, 255, 0.5); /* More pronounced shadow on focus */
  }

  .writing-area {
    /* border-right: 1px solid grey; */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    /* border box */
    box-sizing: border-box;
    margin: 2rem;
  }

  .divider {
    background-color: #ccc;
    width: 5px;
    cursor: ew-resize;
  }

  .visual-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-around;
  }

  .preview {
    background-color: var(--ifm-background-surface-color);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid grey;
    margin: 3rem;
  }
</style>
