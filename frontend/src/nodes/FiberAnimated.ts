import type { NodeProps, RectProps, SplineProps } from "@motion-canvas/2d";
import { Node, Spline, Knot, Layout, Polygon } from "@motion-canvas/2d";

import type {
  SignalValue,
  PossibleColor,
  SimpleSignal,
  PossibleVector2,
} from "@motion-canvas/core";

import { createSignal, Vector2, map, tween, all } from "@motion-canvas/core";

import { signal, initial } from "@motion-canvas/2d";

import type { Connection } from "./util";

export interface FiberProps extends NodeProps {
  // fiber_start: SignalValue<number>
  // fiber_end: SignalValue<number>
  lineWidth: SignalValue<number>;
}

export class FiberAnimated extends Node {
  // @initial(createSignal(new Vector2(0,0)))
  @signal()
  public declare readonly portInput: Connection;

  // @initial(new Vector2(50,0))
  @signal()
  public declare readonly portOutput: Connection;

  @signal()
  public declare readonly lineWidth: SimpleSignal<number>;

  // @signal() //??????????????????????????
  public declare readonly spline_props: SplineProps;

  private knot_1: Knot;
  private knot_2: Knot;

  private knot_1a: Knot;
  private knot_2a: Knot;

  public declare readonly progress: SimpleSignal<number>;
//   private sp: Spline;

  public constructor(props?: FiberProps) {
    super({
      ...props,
    });

    // to be overridden

    this.portInput = {
      position: createSignal(new Vector2(0, 0)),
      light: createSignal(false),
    };
    this.portOutput = {
      position: createSignal(new Vector2(50, 0)),
      light: () => this.portInput.light(),
    };

    // console.log("adding spline details")
    // console.log("and this is the port input signal: ", this.portInput.position())

    this.knot_1 = new Knot({ startHandle: [-120, 0] });
    this.knot_2 = new Knot({ startHandle: [-120, 0] });

    this.knot_1a = new Knot({ startHandle: [-120, 0] });
    this.knot_2a = new Knot({ startHandle: [-120, 0] });
    
    

    this.progress = createSignal(0);

    this.knot_1.absolutePosition(() => this.portInput.position());
    this.knot_2.absolutePosition(() => this.portOutput.position());

    this.knot_1a.absolutePosition(() => this.portInput.position().add(new Vector2(0, 1)));
    this.knot_2a.absolutePosition(() => this.portOutput.position().add(new Vector2(0, 1)));

    const polygonCount = 16; // Example: 5 polygons
    const polygons = Array.from(
        { length: polygonCount },
        (_, index) => index * 2*(1/(polygonCount+1)) - 1
      ); // Adjust for your use case
    const alternating = Array.from( 
        { length: polygonCount },
        (_, index) => index % 2 === 0  
      ); // Adjust for your use case


    const light_color_1 = () => this.portInput.light() ? "#eb0e0e" : "#e38d0b";
    const light_color_2 = () => this.portOutput.light() ? "#b50d0d" : "#cf820e";


    const spline = new Spline({
        lineWidth: 10,
        stroke: "orange",
        shadowColor: {a: 0.30, r: 0, g: 0, b: 0},
        shadowOffset: new Vector2(-2, 2),
        shadowBlur: 4,
        children: [
          this.knot_1a,
          this.knot_2a,
        ],
      })

    const highlight_spline = new Spline({
      lineWidth: 7,
      stroke: "white",
      opacity: 0.42,
      compositeOperation: "lighten",
      children: [
        this.knot_1,
        this.knot_2,
      ],
    })


    highlight_spline.filters.blur(3);

    const list_of_moving_objects = polygons.map((offset, index) => {
        return new Node({children: [
            new Layout({
                layout: true,
                position: () =>
                  spline.getPointAtPercentage(this.progress() - offset).position,
                rotation: () =>
                  spline.getPointAtPercentage(this.progress() - offset).normal.flipped
                    .perpendicular.degrees + 90,
                compositeOperation: "source-atop",
                children: [
                  new Polygon({
                    offset: [0, -1],
                    sides: 3,
                    size: [20, 20],
                    fill: alternating[index] ? light_color_1 : light_color_2,
                    scale: [13, 8],
                  }),
                ],
              }),
        ]})
    })


    const top_node = new Node({
      cache: true,
      children: [
        spline,
        ...list_of_moving_objects, highlight_spline],
    });
    this.add(top_node);
  }


  public *runFiber(duration: number) {

    yield* all(tween(duration, (value) => {
      this.portInput.light() ? this.progress(map(0, 0.9, value)) : this.progress(map(0, 0, value));
    }))
  }
}

// so when this object is initialized with the string placeholder for portInput and portOutput, it seems
// like it might be getting messed up by this, and resulting in a messed up object. There could
// be some hidden magic inside the inherited constructor that is causing this to happen.
