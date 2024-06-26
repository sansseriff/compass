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

  let Description: FullSceneDescription<ThreadGeneratorFactory<View2D>> | null = null;
  let ProjectInstance: Project | null = null;
  let PlayerInstance: PlayerType | null = null;
  let StageInstance: StageType | null = null;

  let player = $state();
  let ratio = 2;

  let previewRef: HTMLDivElement;



  Description = makeScene2D(function* (view) {
    // view.fill('#242424'); // set the background of this scene
    const circle = new Circle({ x: -300, y: 0, width: 100, height: 100, fill:"#e13238" });

    const myCircle = createRef<Circle>()
    view.add(circle);
    yield* all(
      circle.position.x(100,1).to(-300,1),
      circle.fill('#e6a700', 1).to('#e13238', 1),
    )
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
        PlayerInstance.playback.previousScene,
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
      PlayerInstance.togglePlayback()
    });


    
</script>

<div
        class="preview"
        style = "aspect-ratio: {ratio}"
        bind:this={previewRef}
      >
        {#if !player}
        <div>Press play to preview the animation</div>
        {/if}
      </div>
      <button onclick={() => PlayerInstance.togglePlayback()}>toggle playback</button>
      <!-- <button onclick={console.log(PlayerInstance.)}>Info</button> -->


<style>

.preview {
  background-color: var(--ifm-background-surface-color);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>