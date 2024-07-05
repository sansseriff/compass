<script lang="ts">
  // import svelteLogo from './assets/svelte.svg'
  // import viteLogo from '/vite.svg'
  // import Counter from './lib/Counter.svelte'

  //borrowing from https://github.com/motion-canvas/motion-canvas/blob/main/packages/docs/src/components/Fiddle/SharedPlayer.ts

  import type {
    FullSceneDescription,
    Player as PlayerType,
    Project,
    Stage as StageType,
    ThreadGeneratorFactory,
  } from "@motion-canvas/core";
  import { Circle, View2D } from "@motion-canvas/2d";

  // originally loaded client side
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

  let Description: FullSceneDescription<ThreadGeneratorFactory<View2D>> | null =
    null;
  let ProjectInstance: Project | null = null;
  let PlayerInstance: PlayerType | null = null;
  let StageInstance: StageType | null = null;

  let player = $state();
  let ratio = 2;

  let previewRef: HTMLDivElement;

  Description = makeScene2D(function* (view) {
    // view.fill('#242424'); // set the background of this scene
    const circle = new Circle({
      x: -300,
      y: 0,
      width: 100,
      height: 100,
      fill: "#e13238",
    });

    const myCircle = createRef<Circle>();
    view.add(circle);
    yield* all(
      circle.position.x(100, 1).to(-300, 1),
      circle.fill("#e6a700", 1).to("#e13238", 1)
    );
  }) as FullSceneDescription<ThreadGeneratorFactory<View2D>>;

  ProjectInstance = {
    name: "fiddle",
    logger: new Logger(),
    plugins: [DefaultPlugin()],
    scenes: [Description],
    experimentalFeatures: true,
  } as Project;

  ProjectInstance.meta = new ProjectMetadata(ProjectInstance);
  ProjectInstance.meta.shared.size.set(960);
  PlayerInstance = new Player(ProjectInstance, {
    fps: 60,
    size: ProjectInstance.meta.shared.size.get(),
  });

  StageInstance = new Stage();
  StageInstance.configure({
    size: ProjectInstance.meta.shared.size.get(),
  });

  PlayerInstance.onRender.subscribe(async () => {
    await StageInstance.render(
      PlayerInstance.playback.currentScene,
      PlayerInstance.playback.previousScene
    );
  });

  PlayerInstance.onRecalculated.subscribe(() => {
    if (StageInstance.finalBuffer.parentElement !== previewRef) {
      previewRef?.append(StageInstance.finalBuffer);
      // CurrentSetter(PlayerInstance);
      player = PlayerInstance;
    }
  });

  onMount(() => {
    PlayerInstance.togglePlayback();
  });

  let writingAreaWidth = $state(50); // Initial width in percentage

  function startDrag(event) {
      const startX = event.clientX;
      // Convert initialWidth from percentage to pixels for accurate calculation
      const initialWidthPx = document.body.clientWidth * (writingAreaWidth / 100);

      function onMouseMove(event) {
        const dx = event.clientX - startX;
        const containerWidth = document.body.clientWidth;
        console.log("containerWidth: ", containerWidth);

        // Calculate new width in pixels, then convert back to percentage

        

        const newWidthPx = initialWidthPx + dx;

        const rightWidthPx = containerWidth - newWidthPx;

        ProjectInstance.meta.shared.size.set(rightWidthPx);

        writingAreaWidth = (newWidthPx * 100) / containerWidth;
        console.log("first: ", writingAreaWidth);
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
  <div class="writing-area" style="width: {writingAreaWidth}%;">
    <textarea name="paragraph_text" rows="10" style="width: 100%;"></textarea>
  </div>
  <div class="divider" onmousedown={startDrag}></div>
  <div class="visual-area" style="width: {100 - writingAreaWidth}%;">
    <div class="preview" style="aspect-ratio: {ratio}" bind:this={previewRef}>
      {#if !player}
        <div>Press play to preview the animation</div>
      {/if}
    </div>
    <button onclick={() => PlayerInstance.togglePlayback()}
      >toggle playback</button
    >
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
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Modern, readable font */
    font-size: 16px; /* Adequate font size for readability */
    line-height: 1.5; /* Spacing between lines */
    color: #333; /* Darker text for better readability */
    background-color: #f9f9f9; /* Light background color */
    transition: border-color 0.3s, box-shadow 0.3s; /* Smooth transition for focus effect */
  }

  .writing-area textarea:focus {
    border-color: #007bff; /* Highlight color when focused */
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1), 0 0 8px rgba(0, 123, 255, 0.5); /* More pronounced shadow on focus */
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
