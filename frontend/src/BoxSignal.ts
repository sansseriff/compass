import type { NodeProps, RectProps } from "@motion-canvas/2d";
import { Rect, Node, Spline, Knot } from "@motion-canvas/2d"

import type { SignalValue, PossibleColor, SimpleSignal, SerializedVector2, PossibleVector2 } from "@motion-canvas/core";
import {createSignal} from '@motion-canvas/core';


import { signal, initial } from "@motion-canvas/2d";


// export interface FiberInterface {
//     x: SignalValue<number>
//     y: SignalValue<number>
// }

export interface SignalRectProps extends NodeProps {
    fiber_out_position: SignalValue<PossibleVector2>;
    // values to accent rather than a `Color`
    // accent?: SignalValue<PossibleColor>;
    rect_props: RectProps
  }

export class SignalRect extends Node {

    @signal()
    public declare readonly fiber_out_position: SimpleSignal<PossibleVector2>;

    @signal() //??????????????????????????
    public declare readonly rect_props: RectProps;


    public constructor(props?: SignalRectProps) {
        super({
            ...props,
        });

        this.add(new Rect(this.rect_props))

        this.fiber_out_position(props?.rect_props?.position ? {x: props.rect_props.x + 10, y: props.rect_props.y + 10} : {x: 0, y: 0});

    }
}