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

export let Description: FullSceneDescription<
  ThreadGeneratorFactory<View2D>
> | null = null;

let ProjectInstance: Project | null = null;
let PlayerInstance: PlayerType | null = null;
let StageInstance: StageType | null = null;


export let ratio = $state(2);

let CurrentRatio = 1;
let CurrentWidth = 500;


export function updatePlayer(description: typeof Description) {
    if (Description) {
      Description.onReplaced.current = description;
    }
  }

export function borrowPlayer(previewRef: HTMLDivElement, player: PlayerType | null, width: number) {
  if (StageInstance && (StageInstance.finalBuffer.parentElement === previewRef)) {
    console.log("nothing to do")



    if (CurrentWidth !== width) {
      ProjectInstance.meta.shared.size.set([Math.floor(width), Math.floor(width / ratio)]);
  
      console.log("setting size to: ", [Math.floor(width), Math.floor(width / ratio)])
      ProjectInstance.meta.preview.resolutionScale.set(1);

      console.log("setting resolution scale to: ", ProjectInstance.meta.preview.resolutionScale.get(), "width: ", width)

      Description.onReplaced.current = {
      ...Description.onReplaced.current,
      size: ProjectInstance.meta.shared.size.get(),
      resolutionScale: ProjectInstance.meta.preview.resolutionScale.get(),
    };
    StageInstance.configure({
      size: ProjectInstance.meta.shared.size.get(),
      resolutionScale: ProjectInstance.meta.preview.resolutionScale.get(),
    });
    CurrentWidth = width;

      
      CurrentWidth = width;
    }


    return player;
  }


  if (
    StageInstance &&
    previewRef &&
    StageInstance.finalBuffer.parentElement === previewRef
  ) {

    console.log("removing")
    previewRef?.removeChild(StageInstance.finalBuffer);
  }

  Description = makeScene2D(function* () {
    yield;
  }) as FullSceneDescription<ThreadGeneratorFactory<View2D>>;
  Description.onReplaced = new ValueDispatcher(Description);

  ProjectInstance = {
    name: "fiddle",
    logger: new Logger(),
    plugins: [DefaultPlugin()],
    scenes: [Description],
    experimentalFeatures: true,
  } as Project;

  ProjectInstance.meta = new ProjectMetadata(ProjectInstance);
  ProjectInstance.meta.shared.size.set(960);
  ProjectInstance.meta.preview.resolutionScale.set(1);
  PlayerInstance = new Player(ProjectInstance, {
    fps: 60,
    size: ProjectInstance.meta.shared.size.get(),
    resolutionScale: ProjectInstance.meta.preview.resolutionScale.get(),
  });

  StageInstance = new Stage();
  StageInstance.configure({
    size: ProjectInstance.meta.shared.size.get(),
    resolutionScale: ProjectInstance.meta.preview.resolutionScale.get(),
  });

  PlayerInstance.onRender.subscribe(async () => {

    // console.log("on render called")
    await StageInstance.render(
      PlayerInstance.playback.currentScene,
      PlayerInstance.playback.previousScene
    );
  });

  PlayerInstance.onRecalculated.subscribe(() => {
    // console.log("on recalculated called")
    // console.log("is StageInstance.finalBuffer.parentElement equal to previewRef: ", StageInstance.finalBuffer.parentElement === previewRef);

    if (StageInstance.finalBuffer.parentElement !== previewRef) {
      previewRef?.append(StageInstance.finalBuffer);
      // CurrentSetter(PlayerInstance);
      player = PlayerInstance;
    }
  });

  // player = PlayerInstance;

  // if (CurrentRatio !== ratio) {
  //   ProjectInstance.meta.shared.size.set([960, Math.floor(960 / ratio)]);
  //   Description.onReplaced.current = {
  //     ...Description.onReplaced.current,
  //     size: ProjectInstance.meta.shared.size.get(),
  //   };
  //   StageInstance.configure({
  //     size: ProjectInstance.meta.shared.size.get(),
  //   });
  //   CurrentRatio = ratio;
  // }

  if (CurrentWidth !== width) {
    ProjectInstance.meta.shared.size.set([Math.floor(width), Math.floor(width / ratio)]);
    ProjectInstance.meta.preview.resolutionScale.set(1);

    console.log("setting size to: ", [Math.floor(width), Math.floor(width / ratio)])
    console.log("setting resolution scale to: ", ProjectInstance.meta.preview.resolutionScale.get())
    Description.onReplaced.current = {
      ...Description.onReplaced.current,
      size: ProjectInstance.meta.shared.size.get(),
      resolutionScale: ProjectInstance.meta.preview.resolutionScale.get(),
    };
    StageInstance.configure({
      size: ProjectInstance.meta.shared.size.get(),
      resolutionScale: ProjectInstance.meta.preview.resolutionScale.get(),
    });
    CurrentWidth = width;
  }

  // console.log("what is player now: ", player);
  // console.log("what is player instance now: ", PlayerInstance);

  PlayerInstance.activate();
  PlayerInstance.requestReset();
  return PlayerInstance;
}


export function disposePlayer(player: PlayerType | null) {

  PlayerInstance.deactivate();
  CurrentSetter = null;
  CurrentParent = null;
  StageInstance.finalBuffer.remove();
}
