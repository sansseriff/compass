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
  import type { View2D } from "@motion-canvas/2d";

  // originally loaded client side
  import {
    Logger,
    Player,
    ProjectMetadata,
    Stage,
    ValueDispatcher,
    DefaultPlugin,
  } from "@motion-canvas/core";

  import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";

  let Description: FullSceneDescription<ThreadGeneratorFactory<View2D>> | null = null;
  let ProjectInstance: Project | null = null;
  let PlayerInstance: PlayerType | null = null;


  Description = makeScene2D(function* () {
    yield;
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
      size: ProjectInstance.meta.shared.size.get(),
    });

</script>
