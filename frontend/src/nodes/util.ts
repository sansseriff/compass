import { Vector2 } from "@motion-canvas/core";
import type { SimpleSignal } from "@motion-canvas/core";

export interface Connection {
  position: SimpleSignal<Vector2, void>;
  light: SimpleSignal<boolean, void>;
}
