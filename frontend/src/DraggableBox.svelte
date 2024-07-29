<script lang="ts">
    interface Props {
        x: number;
        y: number;
        width: number;
        height: number;
    }

    // interface Props {
    //     scaled_boxes: sc;
    // }

    let { x, y, width, height }: Props = $props();
    
  
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
      x = initialX + (event.clientX - startX);
      y = initialY + (event.clientY - startY);
    }
  
    function handleMouseUp() {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    }
  </script>
  
  <style>
    .box {
      position: absolute;
      background-color: rgba(89, 89, 196, 0.5);
      cursor: grab;
    }
  </style>
  
  <div
    class="box"
    style="left: {x}px; top: {y}px; width: {width}px; height: {height}px;"
    onmousedown={handleMouseDown}
  ></div>