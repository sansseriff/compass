import { Circle, Rect, Line, Node, Polygon, View2D } from "@motion-canvas/2d";
import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";
import { Description } from "./util";
import type {
  FullSceneDescription,
  ThreadGeneratorFactory,
} from "@motion-canvas/core";

import { all, Vector2, map, tween } from "@motion-canvas/core";

import { Box } from "./nodes/Box";
import { Fiber } from "./nodes/Fiber";
import { FiberAnimated } from "./nodes/FiberAnimated";
import { Laser } from "./nodes/Laser";
import { Switch } from "./nodes/Switch";
import { Detector } from "./nodes/Detector";

import type { Connection } from "./nodes/util";

import type { ReturnType } from "./fetch_types";
import type {
  InterfaceWireProps,
  InterfaceFiberProps,
} from "./node_interface/FiberInterface";

import { loop } from "@motion-canvas/core/lib/flow";

import { globalRefs } from "./global_ref"

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
registerObject("Fiber", FiberAnimated);
registerObject("Laser", Laser);
registerObject("Switch", Switch);
registerObject("Detector", Detector);

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

interface FiberPort {
  donate_position: boolean;
  donate_light: boolean;
}

export function createSceneFromText(
  jsonData: ReturnType
): (
  scale_factor: number
) => FullSceneDescription<ThreadGeneratorFactory<View2D>> {
  const scalableScene = (scale_factor: number) => {
    const Description = makeScene2D(function* (view) {
      try {
        // using try/catch because I think motion-canvas usually pipes errors differently
        // console.log("do you get here?");
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
            const from_store = { index: 0, port: "" };
            const to_store = { index: 0, port: "" };
            const portTypeKey_from = node_interface.from_.port + "Type"; // portInputType or portOutputType
            const portTypeKey_to = node_interface.to.port + "Type"; // portInputType or portOutputType

            // find the "from" object
            for (const [node_idx, object_from] of jsonData.objects.entries()) {
              
              if (
                object_from.id === node_interface.from_.obj_id &&
                portTypeKey_from in object_from
              ) {
                from_store.index = node_idx;
                from_store.port = node_interface.from_.port;
              }
            }

            // find the "to" object
            for (const [
              node_idx,
              object_to,
            ] of jsonData.objects.entries()) {
              if (
                object_to.id === node_interface.to.obj_id &&
                portTypeKey_to in object_to
              ) {
                to_store.index = node_idx;
                to_store.port = node_interface.to.port;
              }
            }
            // console.log(
            //   "this is the donator store: ",
            //   from_store,
            //   nodes[from_store.index]
            // );
            // console.log(
            //   "this is the acceptor store: ",
            //   to_store,
            //   nodes[to_store.index]
            // );


            const port_from_instruction: FiberPort = (jsonData.objects[from_store.index] as any)[portTypeKey_from];
            const port_to_instruction: FiberPort = (jsonData.objects[to_store.index] as any)[portTypeKey_to];
            // console.log("this is the port from instruction: ", port_from_instruction);
            // console.log("this is the port to instruction: ", port_to_instruction);

            // console.log("nodes: ", nodes);


            // console.log("from store: trying to get the ", from_store.port, " port from ", nodes[from_store.index]);
            // console.log("this is the from store: ", from_store)
            const port_from: Connection = (nodes[from_store.index] as any)[from_store.port];

            // if (nodes[from_store.index] == undefined || nodes[to_store.index] == undefined) {
            //   console.log("remember to add to registry!")
            // }

            // console.log("to store: trying to get the ", to_store.port, " port from ", nodes[to_store.index]);
            // console.log("this is the to store: ", to_store)
            // console.log("the node idx is ", to_store.index, "and the length is", nodes.length);
            const port_to: Connection = (nodes[to_store.index] as any)[to_store.port];


            // if the "from" port donates a signal and the "to" port does not, then give the "to" port the signal from the "from" port
            try {
              if (port_from_instruction.donate_position && !port_to_instruction.donate_position) {
                port_to.position = port_from.position;
              }
              else if (!port_from_instruction.donate_position && port_to_instruction.donate_position) {
                port_from.position = port_to.position;
              }
  
              if (port_from_instruction.donate_light && !port_to_instruction.donate_light) {
                port_to.light = port_from.light;
              }
              else if (!port_from_instruction.donate_light && port_to_instruction.donate_light) {
                port_from.light = port_to.light;
              }
            }
            catch (e) {
              console.log("error: ", e);
            }
            

            // give the acceptor the signal from the donator
            // (nodes[from_store.index] as any)[acceptor_store.port] = (
            //   nodes[donator_store.index] as any
            // )[donator_store.port];
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
        // console.log(nodes);

        // globalRefs.laser = nodes[0];

        console.log("adding to global refs. ");

        globalRefs.nodes = nodes;

        // yield* all(
        //   // nodes[0].position(nodes[0]?.position().add(new Vector2(0,50)), 2).to(nodes[0]?.position().add(new Vector2(0,-50)), 2).to(nodes[0]?.position().add(new Vector2(0,0)), 2),

        const yieldable = nodes.filter((node) => node.constructor.name === "FiberAnimated").map((node) => loop(60,() => node.runFiber(2)));

        if (yieldable.length === 0) {
          yield * nodes[0]?.rotation(0,100);
        }

        // console.log("this is the yieldable: ", yieldable);

        // console.log(" this might be fiber progres: ", nodes[2]?.progress);

        // find with of the nodes has a "progress" signal:
        // const progress_node = nodes.find((node) => node.progress !== undefined);


        // yield* all(...yieldable);
        yield* all(
        // yield * node[1].runFiber(2);
        // yield * node[0].rotation(0, 20).to(-7, .5).to(0, .5);
          // yield* nodes[0].rotation(0, 20)
          // .to(-7, .5).to(0, .5),
          // nodes[0].scale(2, 2),
          // progress_node?.progress(0, 2).to(1, 2).to(0, 2),
          ...yieldable,
          // loop(20, () => progress_node.runFiber(2)),
          // nodes[1].rotation(7, .5).to(-7, .5).to(0, .5),
          // loop(Infinity, () => {nodes[0].rotation(7, .5).to(-7, .5)})
        );
        // yield loop(Infinity, () => {notes[0].rotation(7, .5).to(-7, .5)});
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
