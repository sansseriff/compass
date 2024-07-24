<script lang="ts">
  import type {
    Player as PlayerTyp,
    FullSceneDescription,
    ThreadGeneratorFactory,
  } from "@motion-canvas/core";
  import { Circle, View2D, Rect, Line, Node } from "@motion-canvas/2d";
  import PreloadingIndicator from "./PreloadingIndicator.svelte";

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
    useScene,
  } from "@motion-canvas/core";

  import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";
  import { onMount } from "svelte";
  import { borrowPlayer, updatePlayer } from "./util";
  import { ratio } from "./util";

  import { getScene } from "./api";
  import { scale } from "svelte/transition";

  import { createSceneFromText } from "./instantiate";

  let loading = $state(false);
  let time_scalar = $state(1);

  let player: PlayerType | null = $state(null);
  let inputText = $state("");

  let previewRef: HTMLDivElement;
  let padding_width = 30;
  let canvas_width = 500;

  let currentSceneScalable;

  let variables = {circleFill: 'red'}

  // function createInitialScene(scale_factor = 1) {
  //   const Description = makeScene2D(function* (view) {
  //     // view.fill('#242424'); // set the background of this scene

  //     const circle = new Circle({
  //       x: -100,
  //       y: 0,
  //       width: 100,
  //       height: 100,
  //       fill: "#e13238",
  //     });

  //     const node = new Node({
  //       x: 0,
  //       y: 0,
  //       children: [circle],
  //       scale: [scale_factor, scale_factor],
  //     });

  //     console.log("this is a circle: ", circle);

  //     view.add(node);
  //     yield* all(
  //       circle.position.x(100, 1).to(-100, 1),
  //       circle.fill("#e6a700", 1).to("#e13238", 1)
  //     );
  //   }) as FullSceneDescription<ThreadGeneratorFactory<View2D>>;
  //   return Description;
  // }

  export function createInitialScalableScene(): (
  scale_factor: number
) => FullSceneDescription<ThreadGeneratorFactory<View2D>> {
  
  const scalableScene = (scale_factor: number) => {
    const Description = makeScene2D(function* (view) {
            const circle = new Circle({
        x: -100,
        y: 0,
        width: 100,
        height: 100,
        // fill: useScene().variables.get('circleFill', 'blue')
        fill: "#e13238"
      });

      const node = new Node({
        x: 0,
        y: 0,
        children: [circle],
        scale: [scale_factor, scale_factor],
      });

      // console.log("this is a circle: ", circle);

      view.add(node);
      
      yield* all(
        circle.position.x(100, 1).to(-100, 1),
        circle.fill("#e6a700", 1).to("#e13238", 1)
      );
    });

    return Description as FullSceneDescription<ThreadGeneratorFactory<View2D>>;
  };

  return scalableScene;
}

  // function otherScene() {
  //   const Description = makeScene2D(function* (view) {
  //     // view.fill('#242424'); // set the background of this scene
  //     // const circle = new Rect({
  //     //   x: -100,
  //     //   y: 0,
  //     //   width: 100,
  //     //   height: 100,
  //     //   rotation: 180,
  //     //   fill: "#000000",
  //     //   // antialiased: false,
  //     // });

  //     const line = new Line({
  //       endArrow: true,
  //       arrowSize: 20,
  //       // lineCap:"butt",
  //       stroke: "424B54",
  //       lineWidth: 20,
  //       points: [
  //         [450, 0],
  //         [-150, 0],
  //       ],
  //     });

  //     view.add(line);
  //   }) as FullSceneDescription<ThreadGeneratorFactory<View2D>>;

  //   return Description;
  // }

  function init() {
    const size = document.body.clientWidth / 2;
    currentSceneScalable = createInitialScalableScene();

    const containerWidth = document.body.clientWidth;
    const initialWidthPx = document.body.clientWidth * (visualAreaWidth / 100);

    const rightWidthPx = containerWidth - initialWidthPx;
    player = borrowPlayer(previewRef, player, rightWidthPx, variables);
    updatePlayer(currentSceneScalable(size / 960));
  }

  // function swapScene() {
  //   const scene = otherScene();
  //   // player = borrowPlayer(previewRef, player, writingAreaWidth);
  //   updatePlayer(scene);
  // }

  onMount(() => {
    init();
  });

  let visualAreaWidth = $state(50); // Initial width in percentage

  function startDrag(event) {
    const startX = event.clientX;
    const initialWidthPx = document.body.clientWidth - event.clientX;
    function onMouseMove(event) {
      const dx = event.clientX - startX;
      const containerWidth = document.body.clientWidth;

      const newWidthPx = initialWidthPx - dx - 2 * padding_width * 0.95;

      canvas_width = Math.floor(newWidthPx);

      // const scene = createScene(canvas_width / 960);
      player = borrowPlayer(previewRef, player, canvas_width);
      updatePlayer(currentSceneScalable(canvas_width / 960));
    }

    function onMouseUp() {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    }

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  }

  function handleText(event) {
    inputText = event.target.value;
    if (event.shiftKey && event.key === "Enter") {
      
      event.preventDefault(); // Prevent the default action to avoid a new line in the textarea
      console.log("Sending textarea content to server:", inputText);
      const wordCount = inputText.split(/\s+/).filter(Boolean).length;
      loading = true;
      time_scalar = Math.round((wordCount / 10) * 10) / 10;
      console.log("time_scalar: ", time_scalar);

      getScene(inputText).then((response) => {
        console.log("creating scene...");
        currentSceneScalable = createSceneFromText(response);

        // console.log("scene: ", scene);
        updatePlayer(currentSceneScalable(canvas_width / 960));
        loading = false;
      });
    }
  }


  const colors = ["red", "green", "blue", "yellow", "purple", "orange"];
</script>

<div class="left-right">
  <!-- style="width: {writingAreaWidth}%; -->
  <div class="writing-area" style="padding: {padding_width}px">
    <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}></textarea>
  </div>
  <button
    class="divider"
    onmousedown={startDrag}
    role="separator"
    aria-orientation="vertical"
  ></button>
  <!-- style="width: {100 - writingAreaWidth}%;" -->
  <div class="visual-area" style="padding: {padding_width}px; width: 100%">
    <div class="together">
      <PreloadingIndicator {loading} {time_scalar} />
      <div class="preview" bind:this={previewRef}>
        {#if !player}
          <div>Press play to preview the animation</div>
        {/if}
      </div>
    </div>

    <button class="button" onclick={() => player.togglePlayback()}
      >toggle playback</button
    >

    <!-- <button class="button" onclick={() => {variables.circleFill = colors[Math.floor(Math.random() * 6)]}}>Change to Green</button> -->

    <!-- <button class="button" onclick={swapScene}>New Scene</button> -->
  </div>
</div>

<style>
  .left-right {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    height: 100vh;
  }

  .writing-area {
    width: 10000%; /* this is some weird hack to make the textarea fill the space */
    display: flex;
    flex-direction: column;
    align-items: end;
    justify-content: center;
  }

  .divider {
    background-color: #f2f2f2;
    cursor: ew-resize;
    padding: 1px;
    /* box-shadow: 0 0 10px 1px rgba(0, 0, 0, 0.1); */
    transition: background-color 0.9s;
  }

  .divider:hover {
    background-color: #4998ff;
  }

  .visual-area {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-around;
  }

  .writing-area textarea {
    width: 100%;
    height: 10rem;

    border: 1px solid #ccc;
    border-radius: 8px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
    outline: none;
    resize: vertical;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    color: #333;
    background-color: #fafafa;
    transition:
      border-color 0.3s,
      box-shadow 0.3s;
  }

  .writing-area textarea:focus {
    border-color: #007bff;
    box-shadow:
      inset 0 1px 3px rgba(0, 0, 0, 0.1),
      0 0 8px rgba(0, 123, 255, 0.5);
  }

  .preview {
    width: auto;
    height: auto;
    background-color: var(--ifm-background-surface-color);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgb(226, 226, 226);
    /* border-radius: 10px; */
  }
</style>
