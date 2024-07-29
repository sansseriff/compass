<script lang="ts">
  import type {
    Player as PlayerTyp,
    FullSceneDescription,
    ThreadGeneratorFactory,
  } from "@motion-canvas/core";
  import {
    Circle,
    View2D,
    Rect,
    Line,
    Node,
    Spline,
    Knot,
  } from "@motion-canvas/2d";
  import PreloadingIndicator from "./PreloadingIndicator.svelte";

  import { setSceneModel, setDecoderModel } from "./api";

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
    createSignal,
    Vector2,
  } from "@motion-canvas/core";

  import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";
  import { onMount } from "svelte";
  import { borrowPlayer, updatePlayer } from "./util";
  import { ratio } from "./util";

  import { getScene } from "./api";
  import { scale } from "svelte/transition";

  import { createSceneFromText } from "./instantiate";

  import { Box } from "./nodes/Box";
  import { Laser } from "./nodes/Laser";
  import { Switch } from "./nodes/Switch";
  import { Detector } from "./nodes/Detector";

  import logo from "./assets/logo.svg";

  import DraggableBox from "./DraggableBox.svelte";

  let loading = $state(false);
  let time_scalar = $state(1);

  let player: PlayerType | null = $state(null);
  let inputText = $state("");

  let previewRef: HTMLDivElement;
  let padding_width = 30;
  let canvas_width = $state(500);

  let currentSceneScalable;

  let variables = { circleFill: "red" };

  import { globalRefs } from "./global_ref"

  // Global object to store references
  

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
        // const box = new Box({
        //   x: 100,
        //   y: 0,
        //   width: 100,
        //   height: 100,
        //   scale: 1,
        //   fill: "#e13238",
        // });

        // const circle = new Circle({
        //   position: () => box.portOutput.position(),
        //   width: 30,
        //   height: 30,
        //   fill: "green",
        //   scale: 1,
        // });

        const laser = new Laser({ x: 0, y: 0 });
        const switch_element = new Switch({ x: 100, y: 0, open: false });
        const detector = new Detector({ x: 200, y: 0 });

        // Store references in the global object
        globalRefs.laser = laser;
        globalRefs.switch_element = switch_element;

        view.add([laser, switch_element, detector]);

        yield* laser
          .position(new Vector2(-100, 0), 1)
          .to(new Vector2(100, 0), 1);
        // );
      });

      return Description as FullSceneDescription<
        ThreadGeneratorFactory<View2D>
      >;
    };

    return scalableScene;
  }

  function init() {
    const size = document.body.clientWidth / 2;
    currentSceneScalable = createInitialScalableScene();

    const containerWidth = document.body.clientWidth;
    const initialWidthPx = document.body.clientWidth * (visualAreaWidth / 100);

    const rightWidthPx = containerWidth - initialWidthPx;
    player = borrowPlayer(previewRef, player, rightWidthPx, variables);
    updatePlayer(currentSceneScalable(canvas_width / 960));
  }

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

  const initial_text =
    "A laser connected to a detector via fiber with a switch connected in between.";

  let decoderModel = $state("llama3-groq-70b-8192-tool-use-preview");
  let sceneModel = $state("gpt-4o-mini");

  const modelOptions = [
    "gpt-4o",
    "gpt-4o-mini",
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-groq-8b-8192-tool-use-preview",
    "mixtral-8x7b-32768",
    "claude-3-5-sonnet-20240620",
  ];

  function handleSceneModelChange(event) {
    sceneModel = event.target.value;
    setSceneModel(sceneModel);
  }

  function handleDecoderModelChange(event) {
    decoderModel = event.target.value;
    console.log("decoderModel: ", decoderModel);
    setDecoderModel(decoderModel);
  }

  onMount(() => {
    init();
    handleDecoderModelChange({ target: { value: decoderModel } });
    handleSceneModelChange({ target: { value: sceneModel } });
  });

  let boxes = [
    { x: 0, y: 0, width: 50, height: 50 },
    { x: 200, y: 150, width: 150, height: 150 },
    // Add more boxes as needed
  ];

  function getScaledBoxes() {
    const scale = canvas_width / 960;
    console.log("scale: ", scale);
    return boxes.map((box) => ({
      x: Math.floor(box.x * scale),
      y: Math.floor(box.y * scale),
      width: Math.floor(box.width * scale),
      height: Math.floor(box.height * scale),
    }));
  }

  let scaled_boxes = $derived.by(() => getScaledBoxes())


</script>

<div class="container">
  <div class="top-bar">
    <div class="left">
      <!-- <div class="logo"> -->
      <img class="logo" src={logo} alt="Logo" />
      <!-- </div> -->
    </div>

    <div class="right">
      <div>
        <label for="decoder-model">Decoder Model:</label>
        <select
          id="decoder-model"
          bind:value={decoderModel}
          onchange={handleDecoderModelChange}
        >
          <option value="" disabled>Select a model</option>
          {#each modelOptions as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="scene-model">Scene Model:</label>
        <select
          id="scene-model"
          bind:value={sceneModel}
          onchange={handleSceneModelChange}
        >
          <option value="" disabled>Select a model</option>
          {#each modelOptions as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>

  <div class="left-right">
    <!-- style="width: {writingAreaWidth}%; -->
    <div class="writing-area" style="padding: {padding_width}px">
      <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}
        >{initial_text}</textarea
      >
      <!-- <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}></textarea>
      <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}></textarea>
      <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}></textarea>
      <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}></textarea>
      <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}></textarea>
      <textarea name="paragraph_text" onkeydown={(e) => handleText(e)}></textarea> -->
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
        <!-- <div class="container"> -->
        <div class="preview" bind:this={previewRef}>
          {#if !player}
            <div>Press play to preview the animation</div>
          {/if}
        </div>
        <div class="draggable-container">
          {#each scaled_boxes as scaled_box}
            <DraggableBox {...scaled_box} />
          {/each}
        </div>
        <!-- </div> -->
      </div>

      <button class="button" onclick={() => { globalRefs.laser.on(true); 
        player.togglePlayback();
        } }
        >toggle playback</button
      >

      <!-- <button class="button" onclick={() => {variables.circleFill = colors[Math.floor(Math.random() * 6)]}}>Change to Green</button> -->

      <!-- <button class="button" onclick={swapScene}>New Scene</button> -->
    </div>
  </div>
</div>

<style>
  .draggable-container {
    position: absolute;
    /* width: 100%;
    height: 100%; */
    top: 4px;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10; /* Ensure it appears on top */
  }

  .together {
    position: relative
  }

  .container {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .logo {
    width: 2.5rem;
  }

  label {
    font-size: 1em;
    font-weight: 500;
    font-family: inherit;
    margin-right: 0.5em;
    margin-left: 1.5rem;
  }

  /* Dropdown styling */
  select {
    padding: 0.6em 1.2em;
    border-radius: 8px;
    border: 1px solid transparent;
    font-size: 1em;
    font-weight: 500;
    font-family: inherit;
    background-color: #1a1a1a;
    color: white;
    cursor: pointer;
    transition:
      border-color 0.25s,
      background-color 0.25s;
  }

  select:hover {
    border-color: #646cff;
  }

  select:focus,
  select:focus-visible {
    outline: 4px auto -webkit-focus-ring-color;
    background-color: #333;
  }

  /* Light mode styles */
  @media (prefers-color-scheme: light) {
    select {
      background-color: #f2f2f2;
      color: #213547;
    }

    select:hover {
      border-color: #747bff;
    }

    select:focus,
    select:focus-visible {
      background-color: #e0e0e0;
    }
  }

  .container {
    display: flex;
    flex-direction: column;
    height: 100vh; /* Full viewport height */
    width: 100vw; /* Full viewport width */
    box-sizing: border-box; /* Include padding and border in the element's total width and height */
  }

  .top-bar {
    padding: 0.2rem;
    height: 3rem;
    background-color: #fafafa;
    border-bottom: 1px solid #f2f2f2;
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .left {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 0.2rem;
  }

  .right {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding-right: 1rem;
  }

  .left-right {
    /* display: flex;
    flex-direction: row;
    justify-content: space-around;
    height: 92vh;
    width: 100vw !important;
    box-sizing: border-box;  */
    flex: 1; /* Take up the remaining space */
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    box-sizing: border-box; /* Include padding and border in the element's total width and height */
    overflow: hidden; /* Prevent overflow */
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
    width: 90%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-around;
  }

  textarea {
    /* flex: 1; */
    height: 100px;
    margin: 5px 0;
    box-sizing: border-box;
  }

  .writing-area {
    width: 10000%; /* this is some weird hack to make the textarea fill the space */
    /* height: 100%; */
    display: flex;

    flex-direction: column;
    align-items: stretch;
    justify-content: center;
    padding: 0rem;
    overflow-y: auto;
    overflow-x: hidden; /* Prevent horizontal scrolling */
    /* height: 100%; */
  }

  .writing-area textarea {
    width: 100%;
    border: 1px solid #f5f5f5;
    border-radius: 2px;
    /* box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1); */
    outline: none;
    resize: vertical;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    color: #333;
    background-color: #ffffff;
    transition:
      border-color 0.3s,
      box-shadow 0.3s;
    overflow-y: auto;
  }

  .writing-area textarea:focus {
    border-color: #9dccff;
    box-shadow:
      inset 0 1px 3px rgba(0, 0, 0, 0.1),
      0 0 8px rgba(0, 123, 255, 0.2);
  }

  .preview {
    width: auto;
    height: auto;
    /* width: 100%; */
    background-color: var(--ifm-background-surface-color);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgb(226, 226, 226);
    /* border-radius: 10px; */
  }
</style>
