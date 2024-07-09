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
  import { Circle, View2D, Rect, Line } from "@motion-canvas/2d";

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
  let padding_width = 30;
  let canvas_width = 500;
  

  function createScene() {
    const Description = makeScene2D(function* (view) {
      // view.fill('#242424'); // set the background of this scene
      const circle = new Circle({
        x: -100,
        y: 0,
        width: 100,
        height: 100,
        fill: "#e13238",
        // antialiased: false,
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
      // const circle = new Rect({
      //   x: -100,
      //   y: 0,
      //   width: 100,
      //   height: 100,
      //   rotation: 180,
      //   fill: "#000000",
      //   // antialiased: false,
      // });

      const line = new Line({
                  endArrow:true,
                  arrowSize: 20,
                  // lineCap:"butt",
                  stroke:"424B54",
                  lineWidth:20,
                  points:
                    [[450, 0],
                    [-150, 0]],});

      view.add(line);

      // const myCircle = createRef<Circle>();
      // view.add(circle);
      // yield* all(
      //   circle.position.x(100, 1).to(-100, 1),
      //   circle.rotation(0,1).to(180,1),
      //   circle.fill("#fffff2", 1).to("#000000", 1)
      // );
    }) as FullSceneDescription<ThreadGeneratorFactory<View2D>>;

    return Description;
  }

  function init() {
    const scene = createScene();

    const containerWidth = document.body.clientWidth;
    const initialWidthPx = document.body.clientWidth * (visualAreaWidth / 100);

    const rightWidthPx = containerWidth - initialWidthPx
    player = borrowPlayer(previewRef, player, rightWidthPx);
    updatePlayer(scene);
  }

  
  function swapScene() {
    const scene = otherScene();
    // player = borrowPlayer(previewRef, player, writingAreaWidth);
    updatePlayer(scene);
  }
  
  
  // function setWidth(width_string: string) {
  //   writingAreaWidth = parseInt(width_string);

  //   const containerWidth = document.body.clientWidth;

  //   const scene = createScene();
  //   player = borrowPlayer(previewRef, player, writingAreaWidth);
  //   updatePlayer(scene);
  // }

  onMount(() => {
    init();

    console.log("player: ", player);
    // PlayerInstance.togglePlayback();
  });

  let visualAreaWidth = $state(50); // Initial width in percentage

  function startDrag(event) {
    const startX = event.clientX;

    console.log("initial client x: ", startX);
    // Convert initialWidth from percentage to pixels for accurate calculation

    

    const initialWidthPx = (document.body.clientWidth - event.clientX);

    function onMouseMove(event) {
      const dx = event.clientX - startX;
      console.log("initial mouse move: ", dx);
      const containerWidth = document.body.clientWidth;

      const newWidthPx = initialWidthPx - dx - (2*padding_width);

      canvas_width = Math.floor(newWidthPx);

      const scene = createScene();
      player = borrowPlayer(previewRef, player, canvas_width);
      updatePlayer(scene);

    }

    function onMouseUp() {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    }

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  }


</script>

<div class="left-right">
  <!-- style="width: {writingAreaWidth}%; -->
  <div class="writing-area" style = "padding: {padding_width}px" >
    <textarea name="paragraph_text"></textarea>
  </div>
  <button class="divider" onmousedown={startDrag} role="separator" aria-orientation="vertical"></button>
  <!-- style="width: {100 - writingAreaWidth}%;" -->
  <div class="visual-area" style = "padding: {padding_width}px; width: 100%">
    <div class="preview" bind:this={previewRef}>
      {#if !player}
        <div>Press play to preview the animation</div>
      {/if}
    </div>
    <button class="button" onclick={() => player.togglePlayback()}
      >toggle playback</button
    >
    <input bind:value={inputText} type="text">
    <button class="button" onclick={() => setWidth(inputText)}>Submit</button>

    <button class="button" onclick={swapScene}>New Scene</button>
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
    align-items:end;
    justify-content: center;
  }



  .divider {
    background-color: #f2f2f2;
    cursor: ew-resize;
    padding: 2px;
    /* box-shadow: 0 0 10px 1px rgba(0, 0, 0, 0.1); */
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
    border-radius: 10px;
  }
</style>
