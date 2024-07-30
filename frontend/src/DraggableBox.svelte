<script lang="ts">
  import { onMount } from "svelte";
  import { globalRefs } from "./global_ref";
  import { consolidateCodeRanges } from "@motion-canvas/2d";

    // interface Coords {
    //     x: number;
    //     y: number;
    // }

    interface Props {
        x: number;
        y: number;
        width: number;
        idx: number;
        scalar: number
    }

    // interface Props {
    //     scaled_boxes: sc;
    // }

    let { x, y, width, idx, scalar }: Props = $props();
    
  
    let startX, startY, initialX, initialY;
  
    function handleMouseDown(event) {
      startX = event.clientX;
      startY = event.clientY;
      initialX = x;
      initialY = y;
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
  
    function handleMouseMove(event) {
      // console.log("idx: ", idx)
      // console.log(globalRefs.nodes[idx])

      // console.log("x: ", globalRefs.nodes[idx].constructor.name)

      console.log("I have a: ", globalRefs.nodes[idx].constructor.name)
      x = initialX + (event.clientX - startX);
      y = initialY + (event.clientY - startY);
      globalRefs.nodes[idx].x(x/scalar - 960/2 + globalRefs.nodes[idx].width()/2);
      globalRefs.nodes[idx].y(y/scalar - 960/4 + globalRefs.nodes[idx].width()*0.65/2);
      // console.log(globalRefs.nodes[idx].x())
      

    }
  
    function handleMouseUp() {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    }

    onMount(() => {
        console.log("mounted a box");
    });
  </script>
  
  <style>
    .box {
      position: absolute;
      background-color: rgba(89, 89, 196, 0.0);
      cursor: grab;
    }
  </style>
  
  <div
    class="box"
    style="left: {x}px; top: {y}px; width: {width}px; height: {Math.floor(width*0.65)}px;"
    onmousedown={handleMouseDown}
  ></div>