import type { NodeProps, RectProps } from "@motion-canvas/2d";
import { Rect, Node, Spline, Knot } from "@motion-canvas/2d";

import type {
  SignalValue,
  PossibleColor,
  SimpleSignal,
  SerializedVector2,
  PossibleVector2,
} from "@motion-canvas/core";
import { createSignal, Vector2 } from "@motion-canvas/core";

import { signal, initial } from "@motion-canvas/2d";

// export interface FiberInterface {
//     x: SignalValue<number>
//     y: SignalValue<number>
// }

export interface BoxProps extends NodeProps {
  // portInput: SignalValue<PossibleVector2>;
  // portOutput: SignalValue<PossibleVector2>;
  // values to accent rather than a `Color`
  // accent?: SignalValue<PossibleColor>;
  width?: SignalValue<number>;
  height?: SignalValue<number>;
  x?: SignalValue<number>;
  y?: SignalValue<number>;
  fill?: SignalValue<PossibleColor>;
}

export class Box extends Node {
  @signal()
  public declare readonly portInput: SimpleSignal<Vector2, void>

  @signal()
  public declare readonly portOutput: SimpleSignal<Vector2, void>

  @signal()
  public declare readonly width: SimpleSignal<number>;

  @signal()
  public declare readonly height: SimpleSignal<number>;

  @signal()
  public declare readonly fill: SimpleSignal<PossibleColor>;

  public constructor(props?: BoxProps) {
    super({
      ...props,
    });

    this.add(
      new Rect({
        x: 0,
        y: 0,
        width: this.width,
        height: this.height,
        // x: this.x,
        // y: this.y,
        // width: this.width,
        // height: this.height,
        fill: this.fill,
      })
    );

    // console.log("trying to calculate values to put in signal")
    // this.portInput(new Vector2(100, 100));
    // console.log("singal updated")
    // console.log("updated signal: ", this.portInput())

    this.portOutput = createSignal(() => this.position().add(new Vector2(20,20)));
    this.portInput = createSignal(() => this.position().add(new Vector2(-20,20)));
  }
}
