import type { NodeProps, RectProps } from "@motion-canvas/2d";
import { Rect, Node, Circle, Img } from "@motion-canvas/2d";

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

import detector_on from "../assets/detector_on.svg";
import detector_off from "../assets/detector_off.svg";

export interface DetectorProps extends NodeProps {
  width?: SignalValue<number>;
  x?: SignalValue<number>;
  y?: SignalValue<number>;
}

export class Detector extends Node {
  public declare readonly portInput: Connection;

  //   public declare readonly portOutput: Connection;

  @signal()
  public declare readonly on: SimpleSignal<boolean>;

  //   @signal()
  //   public declare readonly fill: SimpleSignal<PossibleColor>;

  @initial(100)
  @signal()
  public declare readonly width: SimpleSignal<number, void>;

  private img: Img;
  private port_input: Circle;
  //   private port_output: Circle;

  public constructor(props?: DetectorProps) {
    super({
      ...props,
    });

    // to be overridden
    this.portInput = {
      position: createSignal(new Vector2(0, 0)),
      light: createSignal(false),
    };
    // this.portOutput = {
    //   position: createSignal(new Vector2(0, 0)),
    //   light: createSignal(false),
    // };

    this.port_input = new Circle({
      x: -this.width() / 2  + this.width()/30,
      y: 0,
      width: 1,
      height: 20,
      fill: "black",
      opacity: 0,
    });
    // this.port_output = new Circle({
    //   x: 30,
    //   y: 0,
    //   width: 3,
    //   height: 20,
    //   fill: "black",
    //   opacity: 0,
    // });

    this.on = createSignal(() => this.portInput.light());

    this.img = new Img({
      width: this.width,
      src: () => (this.on() ? detector_on : detector_off),
      children: [this.port_input],
    });

    this.add(this.img);

    this.portInput.position = createSignal(() =>
      this.port_input.absolutePosition()
    );
  }
}
