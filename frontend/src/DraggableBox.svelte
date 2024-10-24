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
        height: number;
        idx: number;
        scalar: number
    }

    // interface Props {
    //     scaled_boxes: sc;
    // }

    let { x, y, width, height, idx, scalar }: Props = $props();
    
  
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
      globalRefs.nodes[idx].x(x/scalar - 1920/2 + width/scalar/2);
      globalRefs.nodes[idx].y(y/scalar - 1920/4 - height/scalar/2);
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
    style="left: {x}px; top: {y}px; width: {width}px; height: {height}px;"
    onmousedown={handleMouseDown}
  ></div>