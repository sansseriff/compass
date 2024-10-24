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

import switch_open from "../assets/switch_open.svg";
import switch_closed from "../assets/switch_closed.svg";

export interface SwitchProps extends NodeProps {
  width?: SignalValue<number>;
  x?: SignalValue<number>;
  y?: SignalValue<number>;
  open: SignalValue<boolean>;
}

export class Switch extends Node {

  public declare readonly portInput: Connection;

  public declare readonly portOutput: Connection;

  @signal()
  public declare readonly open: SimpleSignal<boolean>;

  @signal()
  public declare readonly fill: SimpleSignal<PossibleColor>;

  @initial(120)
  @signal()
  public declare readonly width: SimpleSignal<number, void>;

  
  @signal()
  public declare readonly visible_height: SimpleSignal<number, void>;

  private img: Img;
  private port_input: Circle;
  private port_output: Circle;

  public constructor(props?: SwitchProps) {
    super({
      ...props,
    });

    // to be overridden
    this.portInput = {
      position: createSignal(new Vector2(0, 0)),
      light: createSignal(false),
    };
    this.portOutput = {
      position: createSignal(new Vector2(0, 0)),
      light: createSignal(false),
    };

    this.port_input = new Circle({
      x: -this.width()/2 + this.width()*0.07, // here
      y: 0,
      width: 1,
      height: 20,
      fill: "black",
      opacity: 0,
    });
    this.port_output = new Circle({
      x: 30,
      y: 0,
      width: 3,
      height: 20,
      fill: "black",
      opacity: 0,
    });

    


    this.portOutput.light(!this.open() ? () => this.portInput.light() : false)

    // this.open = createSignal(() => this.portInput.light());

    this.img = new Img({
      width: this.width,
      src: () => (this.open() ? switch_open : switch_closed),
      children: [this.port_input, this.port_output],
    });

    this.add(this.img);


    this.visible_height( () => this.img.height());

    this.portInput.position = createSignal(() =>
      this.port_input.absolutePosition()
    );
    this.portOutput.position = createSignal(() =>
      this.port_output.absolutePosition()
    );
  }
}
