import type { NodeProps, RectProps, SplineProps } from "@motion-canvas/2d";
import { Node, Spline, Knot } from "@motion-canvas/2d"

import type { SignalValue, PossibleColor, SimpleSignal, PossibleVector2 } from "@motion-canvas/core";

import {createSignal, Vector2} from '@motion-canvas/core';


import { signal, initial } from "@motion-canvas/2d";

import type { Connection } from "./util";


export interface FiberProps extends NodeProps {
    // fiber_start: SignalValue<number>
    // fiber_end: SignalValue<number>
    lineWidth: SignalValue<number>
  }

export class Fiber extends Node {

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
    private sp: Spline;

    public constructor(props?: FiberProps) {
        super({
            ...props,
        });

        // to be overridden

        

        this.portInput = {position: createSignal(new Vector2(0, 0)), light: createSignal(false)};
        this.portOutput = {position: createSignal(new Vector2(50, 0)), light: () => this.portInput.light()};

        console.log("adding spline details")
        console.log("and this is the port input signal: ", this.portInput.position())

        this.knot_2 = new Knot({startHandle: [-100, 0]})
        this.knot_1 = new Knot({startHandle: [-100, 0]})
        this.sp = new Spline({lineWidth: this.lineWidth, stroke: "orange", shadowColor: {a: 0.25, r: 0, g: 0, b: 0}, shadowBlur: 2,
            
            children: [this.knot_1, this.knot_2]})

        this.knot_1.absolutePosition(() => this.portInput.position());
        this.knot_2.absolutePosition(() => this.portOutput.position());

        this.add(
            this.sp
        )

        // this.absolutePosition(() => this.portInput());
        // this.absolutePosition(() => this.portOutput());
    }
}


// so when this object is initialized with the string placeholder for portInput and portOutput, it seems
// like it might be getting messed up by this, and resulting in a messed up object. There could 
// be some hidden magic inside the inherited constructor that is causing this to happen.