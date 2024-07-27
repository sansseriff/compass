import type { InterfaceWireProps } from "./node_interface/FiberInterface";

interface BasicObject {
    id: string;
}


export interface ReturnType {
    objects: Array<BasicObject>;
    interfaces?: Array<InterfaceWireProps>;
}