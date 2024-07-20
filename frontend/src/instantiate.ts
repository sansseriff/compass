import { Circle, Rect, Line, Node, Polygon, View2D } from "@motion-canvas/2d";
import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";
import { Description } from "./util";
import type {
  FullSceneDescription,
  ThreadGeneratorFactory,
} from "@motion-canvas/core";

import type { ReturnType } from "./api";

type Constructor<T> = new (data: any) => T;

const classRegistry: { [key: string]: Constructor<Node> } = {};

function registerClass(type: string, ctor: Constructor<Node>) {
  classRegistry[type] = ctor;
}

// Registering classes
registerClass("Rect", Rect);
registerClass("Circle", Circle);
registerClass("Line", Line);
registerClass("Polygon", Polygon);

function createObject(data: any): Node | null {
  const { t, name, ...cleanedData } = data;
  const ctor = classRegistry[t];

  if (cleanedData.hasOwnProperty('y')) {
    cleanedData.y = -cleanedData.y;
  }

  console.log("this is cleaned data", cleanedData);

  if (ctor) {
    return new ctor(cleanedData);
  } else {
    return null;
  }
}

export function createSceneFromText(
  jsonData: ReturnType,
  scale_factor: number
) {

  const Description = makeScene2D(function* (view) {
    const nodes = jsonData.scene.map((data) => {
      const obj = createObject(data);

      return obj;
    });

    const top_node = new Node({
      x: 0,
      y: 0,
      children: nodes,
      scale: [scale_factor, scale_factor],
    });

    view.add(top_node);
  });

  return Description as FullSceneDescription<ThreadGeneratorFactory<View2D>>;
}
