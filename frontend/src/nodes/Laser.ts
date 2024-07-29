import type { NodeProps, RectProps } from "@motion-canvas/2d";
import { Rect, Node, Spline, Knot, Circle, Img } from "@motion-canvas/2d";

import type { Connection } from "./util";

import type {
  SignalValue,
  PossibleColor,
  SimpleSignal,
  SerializedVector2,
  PossibleVector2,
} from "@motion-canvas/core";
import { createSignal, Vector2 } from "@motion-canvas/core";

import { signal, initial } from "@motion-canvas/2d";

import laser_on from "../assets/laser_on.svg";
import laser_off from "../assets/laser_off.svg";

export interface LaserProps extends NodeProps {
  x?: SignalValue<number>;
  y?: SignalValue<number>;
  width?: SignalValue<number>;
  on?: SignalValue<boolean>;
}

export class Laser extends Node {
  public declare readonly portOutput: Connection;

  @signal()
  public declare readonly on: SimpleSignal<boolean>;

  @initial(145)
  @signal()
  public declare readonly width: SimpleSignal<number, void>;

  @signal()
  public declare readonly fill: SimpleSignal<PossibleColor>;

  private img: Img;
  private port_1: Circle;

  public constructor(props?: LaserProps) {
    super({
      ...props,
    });

    // to be overridden
    this.portOutput = {
      position: createSignal(new Vector2(0, 0)),
      light: createSignal(false),
    };

    this.portOutput.light(() => this.on());

    this.port_1 = new Circle({
      x: this.width()/3.4,
      y: 0,
      width: 3,
      height: 20,
      fill: "black",
      opacity: 0.01,
    });

    this.img = new Img({
      width: this.width,
      src: () => (this.on() ? laser_on : laser_off),
      children: [this.port_1],
    });

    // this.img.src(() => this.on() ? laser_on : laser_off)

    this.add(this.img);

    // console.log("color value: ", this.fill().valueOf())

    // console.log("trying to calculate values to put in signal")
    // this.portInput(new Vector2(100, 100));
    // console.log("singal updated")
    // console.log("updated signal: ", this.portInput())

    this.portOutput.position = createSignal(() =>
      this.port_1.absolutePosition()
    );
    // this.portInput.position = createSignal(() => this.port_2.absolutePosition());
  }
}
