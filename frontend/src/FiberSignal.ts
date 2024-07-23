import type { NodeProps, RectProps, SplineProps } from "@motion-canvas/2d";
import { Node, Spline, Knot } from "@motion-canvas/2d"

import type { SignalValue, PossibleColor, SimpleSignal, PossibleVector2 } from "@motion-canvas/core";
import {createSignal} from '@motion-canvas/core';


import { signal, initial } from "@motion-canvas/2d";


export interface FiberProps extends NodeProps {
    fiber_start: SignalValue<number>
    fiber_end: SignalValue<number>
    rect_props: SplineProps
  }

export class SignalRect extends Node {

    @signal()
    public declare readonly fiber_start: SimpleSignal<PossibleVector2>;

    @signal()
    public declare readonly fiber_end: SimpleSignal<PossibleVector2>;


    // @signal() //??????????????????????????
    public declare readonly spline_props: SplineProps;

    public constructor(props?: FiberProps) {
        super({
            ...props,
        });

        this.add(
            new Spline({lineWidth: 15, stroke: "orange", children: [
                new Knot({position: this.fiber_start(), startHandle: [-100, 0]}),
                new Knot({position: this.fiber_end(), startHandle: [-100, 0]}),
            ]})
        )
    }
}