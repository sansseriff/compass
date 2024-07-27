import type { NodeProps, RectProps, SplineProps } from "@motion-canvas/2d";
import { Node, Spline, Knot } from "@motion-canvas/2d"

import type { SignalValue, PossibleColor, SimpleSignal, PossibleVector2 } from "@motion-canvas/core";

import {createSignal, Vector2} from '@motion-canvas/core';


import { signal, initial } from "@motion-canvas/2d";


export interface FiberProps extends NodeProps {
    fiber_start: SignalValue<number>
    fiber_end: SignalValue<number>
    lineWidth: SignalValue<number>
  }

export class Fiber extends Node {

    // @initial(createSignal(new Vector2(0,0)))
    @signal()
    public declare readonly portInput: SimpleSignal<PossibleVector2>;


    // @initial(new Vector2(50,0))
    @signal()
    public declare readonly portOutput: SimpleSignal<PossibleVector2>;


    @signal()
    public declare readonly lineWidth: SimpleSignal<number>;


    // @signal() //??????????????????????????
    public declare readonly spline_props: SplineProps;

    public constructor(props?: FiberProps) {
        super({
            ...props,
        });

        console.log("adding spline details")
        console.log("and this is the port input signal: ", this.portInput())
        this.add(
            new Spline({lineWidth: this.lineWidth, stroke: "orange", children: [
                new Knot({position: () => this.portInput(), startHandle: [-100, 0]}),
                new Knot({position: () => this.portOutput(), startHandle: [-100, 0]}),
            ]})
        )
    }
}


// so when this object is initialized with the string placeholder for portInput and portOutput, it seems
// like it might be getting messed up by this, and resulting in a messed up object. There could 
// be some hidden magic inside the inherited constructor that is causing this to happen.