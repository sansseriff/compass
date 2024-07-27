import { Circle, Rect, Line, Node, Polygon, View2D } from "@motion-canvas/2d";
import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";
import { Description } from "./util";
import type {
  FullSceneDescription,
  ThreadGeneratorFactory,
} from "@motion-canvas/core";

import { all, Vector2 } from "@motion-canvas/core";

import { Box } from "./nodes/Box";
import { Fiber } from "./nodes/Fiber";

import type { ReturnType } from "./fetch_types";
import type {
  InterfaceWireProps,
  InterfaceFiberProps,
} from "./node_interface/FiberInterface";

type Constructor<T> = new (data: any) => T;

const objectRegistry: { [key: string]: Constructor<Node> } = {};
// const interfaceRegistry: { [key: string]: Constructor<InterfaceWire> } = {};

function registerObject(type: string, ctor: Constructor<Node>) {
  objectRegistry[type] = ctor;
}

// function registerInterface(type: string, ctor: Constructor<InterfaceWire>) {
//   interfaceRegistry[type] = ctor;
// }

// Registering classes
registerObject("Rect", Rect);
registerObject("Circle", Circle);
registerObject("Line", Line);
registerObject("Polygon", Polygon);
registerObject("Box", Box);
registerObject("Fiber", Fiber);

// registerInterface("InterfaceWire", InterfaceWire);
// registerInterface("InterfaceFiber", InterfaceFiber);

function createObject(data: any): Node | null {
  const { t, name, ...cleanedData } = data;
  const ctor = objectRegistry[t];

  // easier for the LLMs to think of y as up.
  if (cleanedData.hasOwnProperty("y")) {
    cleanedData.y = -cleanedData.y;
  }

  // Remove parameters prefixed by "port"
  for (const key in cleanedData) {
    if (key.startsWith("port")) {
      delete cleanedData[key];
    }
  }

  // console.log("this is cleaned data", cleanedData);

  if (ctor) {
    return new ctor(cleanedData);
  } else {
    return null;
  }
}

// function createInterface(data: any): InterfaceWire | null {
//   const { t, name, ...cleanedData } = data;

//   const intf = interfaceRegistry[t];

//   if (intf) {
//     return new intf(cleanedData);
//   } else {
//     return null;
//   }

// }

export function createSceneFromText(
  jsonData: ReturnType
): (
  scale_factor: number
) => FullSceneDescription<ThreadGeneratorFactory<View2D>> {
  const scalableScene = (scale_factor: number) => {
    const Description = makeScene2D(function* (view) {
      try {
        // using try/catch because I think motion-canvas usually pipes errors differently
        console.log("do you get here?");
        // const node_interfaces = jsonData.interfaces?.map((data) => {
        //   const node_interface = createInterface(data);
        //   return node_interface;
        // });

        const nodes = jsonData.objects.map((data) => {
          const obj = createObject(data);
          return obj;
        });

        if (jsonData.interfaces) {
          for (const node_interface of jsonData.interfaces) {
            const donator_store = { index: 0, port: "" };
            const acceptor_store = { index: 0, port: "" };


            // find the donator
            for (const [
              node_idx,
              possible_donator,
            ] of jsonData.objects.entries()) {
              if (
                possible_donator.id === node_interface.donator_obj.obj_id &&
                node_interface.donator_obj.port in possible_donator
              ) {
                donator_store.index = node_idx;
                donator_store.port = node_interface.donator_obj.port;
              }
            }

            // find the acceptor
            for (const [
              node_idx,
              possible_acceptor,
            ] of jsonData.objects.entries()) {
              if (
                possible_acceptor.id === node_interface.fiber.fiber_id &&
                node_interface.fiber.port in possible_acceptor
              ) {
                acceptor_store.index = node_idx;
                acceptor_store.port = node_interface.fiber.port;
              }
            }
            console.log("this is the donator store: ", donator_store, nodes[donator_store.index]);
            console.log("this is the acceptor store: ", acceptor_store, nodes[acceptor_store.index]);

            // give the acceptor the signal from the donator
            (nodes[acceptor_store.index] as any)[acceptor_store.port] = (nodes[donator_store.index] as any)[donator_store.port];

          }
        }

        // console.log('this is node interfaces: ', node_interfaces);

        // if (node_interfaces) {
        //   node_interfaces.forEach((node_interface) => {

        //     jsonData.objects.forEach((json_node) => {
        //       if (node_interface?.input.obj_id === json_node.id) {
        //         if (node_interface?.input.port === "portInput") {
        //           json_node.portInput = node_interface.signal();
        //         }
        //         if (node_interface?.input.port === "portOutput") {
        //           json_node.portOutput = node_interface.signal();
        //         }
        //       }

        //       if (node_interface?.output.obj_id === json_node.id) {
        //         if (node_interface?.output.port === "portInput") {
        //           json_node.portInput = node_interface.signal();
        //         }
        //         if (node_interface?.output.port === "portOutput") {
        //           json_node.portOutput = node_interface.signal();
        //         }
        //       }

        //     });
        //   });
        // }

        // console.log("but not here...")

        // console.log("json data after ", jsonData.objects);

        // console.log("this is port input on 3rd node: ", nodes[2].portInput());

        const top_node = new Node({
          x: 0,
          y: 0,
          children: nodes,
          scale: [scale_factor, scale_factor],
        });

        view.add(top_node);
        console.log(nodes);

        yield * nodes[0].position(new Vector2(0,100),2).to(new Vector2(0,-100),2);
      } catch (e) {
        console.log("error: ", e);
      }

      

      // yield* nodes[0].portOutput({ x: 100, y: 100 }, 2).to({ x: 200, y: 200 }, 2);
    });

    return Description as FullSceneDescription<ThreadGeneratorFactory<View2D>>;
  };

  return scalableScene;
}

// A box connected to another box via fiber
