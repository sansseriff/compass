import {createSignal, Vector2} from '@motion-canvas/core';

// export interface C {
//     obj_id: string;
//     port: string;
// }

// export interface ObjectPointer {
//     obj_id: string;
//     port: string;
// }

// export interface FiberPointer {
//     fiber_id: string;
//     port: string;
// }

export interface Port {
    obj_id: string;
    port: string;
}

export interface InterfaceWireProps {
    from_: Port;
    to: Port;
}


// export class InterfaceWire {

//     public declare readonly input: C;
//     public declare readonly output: C;
//     public declare readonly sig: () => any;

//     public constructor(props: InterfaceWireProps) {
//         this.input = props.input;
//         this.output = props.output;
//         this.sig = Vector2.createSignal(new Vector2(0,0));
//     }

//     signal() {
//         return this.sig;
//     }

// }



export interface InterfaceFiberProps {
    from_: Port;
    to: Port;
}


// export class InterfaceFiber extends InterfaceWire  {

//     public constructor(props: InterfaceFiberProps) {
//         super({...props});
//     }

// }



