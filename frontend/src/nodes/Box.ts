import type { NodeProps, RectProps } from "@motion-canvas/2d";
import { Rect, Node, Spline, Knot, Circle } from "@motion-canvas/2d";

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

  private rect: Rect;
  private port_1: Circle;
  private port_2: Circle;

  public constructor(props?: BoxProps) {
    super({
      ...props,
    });


    this.port_1 = new Circle({x: 10, y: 10, fill:"#363636", width: 10, height: 10});
    this.port_2 = new Circle({x: -10, y: 10, fill:"#363636", width: 10, height: 10});
    this.rect = new Rect({
      smoothCorners: true,
      radius: 5,
      x: 0,
      y: 0,
      shadowColor: {a: 0.25, r: 0, g: 0, b: 0},
      stroke: "black",
      lineWidth: 2,
      shadowOffset: new Vector2(-2, 2),
      shadowBlur: 5,
      width: this.width,
      height: this.height,
      children: [this.port_1, this.port_2],
      // x: this.x,
      // y: this.y,
      // width: this.width,
      // height: this.height,
      fill: this.fill,
    })


    this.add(
      this.rect
    );

    console.log("color value: ", this.fill().valueOf())

    // console.log("trying to calculate values to put in signal")
    // this.portInput(new Vector2(100, 100));
    // console.log("singal updated")
    // console.log("updated signal: ", this.portInput())

    this.portOutput = createSignal(() => this.port_1.absolutePosition());
    this.portInput = createSignal(() => this.port_2.absolutePosition());
  }
}
