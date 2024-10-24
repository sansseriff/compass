<script lang="ts">
    import type {
        Player as PlayerType,
        FullSceneDescription,
        ThreadGeneratorFactory,
    } from "@motion-canvas/core";
    import {
        Circle,
        View2D,
        Rect,
        Line,
        Node,
        Spline,
        Knot,
        Txt,
        initial,
    } from "@motion-canvas/2d";
    import PreloadingIndicator from "./PreloadingIndicator.svelte";

    import { setSceneModel, setDecoderModel } from "./api";

    // // originally loaded client side
    import {
        Logger,
        Player,
        ProjectMetadata,
        Stage,
        ValueDispatcher,
        DefaultPlugin,
        createRef,
        all,
        useScene,
        createSignal,
        Vector2,
    } from "@motion-canvas/core";

    import { makeScene2D, Code, LezerHighlighter } from "@motion-canvas/2d";
    import { onMount } from "svelte";
    import { borrowPlayer, updatePlayer } from "./util";
    import { ratio } from "./util";

    import { getScene } from "./api";
    import { scale } from "svelte/transition";

    import { createSceneFromText } from "./instantiate";

    import { Box } from "./nodes/Box";
    import { Laser } from "./nodes/Laser";
    import { Switch } from "./nodes/Switch";
    import { Detector } from "./nodes/Detector";
    import { Compass } from "./nodes/Compass";

    import logo from "./assets/logo.svg";

    import DraggableBox from "./DraggableBox.svelte";

    import { globalRefs } from "./global_ref";

    let player: PlayerType | null = $state(null);
    let inputText = $state("");
    let loading = $state(false);

    let previewRef: HTMLDivElement;

    let boxes: Array<BBox> = [];

    let currentSceneScalable;

    let scaled_boxes: Array<BBox> = $state();

    let variables = { circleFill: "red" }; // remove!~!

    const initial_text =
        "A laser connected to a detector via fiber with a switch connected in between. The laser is on.";

    let decoderModel = $state("llama3-groq-70b-8192-tool-use-preview");
    let sceneModel = $state("gpt-4o-mini");

    function handleText(event) {
        console.log("finised clearing nodes");
        inputText = event.target.value;
        if (event.shiftKey && event.key === "Enter") {
            boxes = [];
            globalRefs.nodes = [];
            event.preventDefault(); // Prevent the default action to avoid a new line in the textarea
            console.log("Sending textarea content to server:", inputText);
            const wordCount = inputText.split(/\s+/).filter(Boolean).length;
            loading = true;

            getScene(inputText).then((response) => {
                console.log("creating scene...");
                currentSceneScalable = createSceneFromText(response);

                // console.log("scene: ", scene);
                updatePlayer(currentSceneScalable(1));
                loading = false;

                setTimeout(() => {
                    globalRefs.nodes.forEach((node, index) => {
                        console.log("starting with box: ", node);
                        if (node.constructor.name !== "Fiber") {
                            console.log("node name: ", node.constructor.name);
                            if (node.width) {
                                // console.log("node height: ", node.height());
                                boxes.push({
                                    x: node.x() + 1920 / 2 - node.width() / 2,
                                    y: node.visible_height ? node.y() + 1920 / 4 + node.visible_height() / 2 : node.y() + 1920 / 4 + node.width() * 0.2 * 0.5,
                                    width: node.width(),
                                    height: node.visible_height ? node.visible_height() : node.width() * 0.2,
                                    idx: index,
                                });

                                console.log("visible height: ", node.visible_height());
                                // boxes.push({x: 0, y: 0, width: 100});
                            }
                            // boxes.push({ x: node.x(), y: node.y(), width:  });
                        }
                    });
                    scaled_boxes = getScaledBoxes(1 / window.devicePixelRatio);
                    
                }, 300);
            });
        }
    }

    export function createInitialScalableScene(): (
        scale_factor: number,
    ) => FullSceneDescription<ThreadGeneratorFactory<View2D>> {
        const scalableScene = (scale_factor: number) => {
            const Description = makeScene2D(function* (view) {
                const compass = new Compass({ x: 0, y: 0, opacity: 0.4 });
                view.add(compass);
                yield* compass
                    .scale(1.1, 1)
                    .to(0.9, 1)
                    .to(1.1, 1)
                    .to(0.9, 1)
                    .to(1.1, 1)
                    .to(0.9, 1)
                    .to(1.1, 1)
                    .to(0.9, 1)
                    .to(1, 0.5);
            });

            return Description as FullSceneDescription<
                ThreadGeneratorFactory<View2D>
            >;
        };

        return scalableScene;
    }

    function getScaledBoxes(scale) {
        return boxes.map((box) => ({
            x: Math.floor(box.x * scale),
            y: Math.floor(box.y * scale),
            width: Math.floor(box.width * scale),
            height: Math.floor(box.height * scale),
            idx: box.idx,
        }));
    }

    const modelOptions = [
        "gpt-4o",
        "gpt-4o-mini",
        "llama3-groq-70b-8192-tool-use-preview",
        "llama3-groq-8b-8192-tool-use-preview",
        "mixtral-8x7b-32768",
        "claude-3-5-sonnet-20240620",
        "llama-3.1-70b-versatile",
    ];

    function handleSceneModelChange(event) {
        sceneModel = event.target.value;
        setSceneModel(sceneModel);
    }

    function handleDecoderModelChange(event) {
        decoderModel = event.target.value;
        console.log("decoderModel: ", decoderModel);
        setDecoderModel(decoderModel);
    }

    function init() {
        player = borrowPlayer(previewRef, player, 1920, variables);
        updatePlayer(currentSceneScalable(1));
    }

    onMount(() => {
        currentSceneScalable = createInitialScalableScene();
        init();

        setTimeout(() => {
            console.log(previewRef.childNodes);

            previewRef.childNodes[0].style.width = `${1920 / window.devicePixelRatio}px`;
            previewRef.childNodes[0].style.height = `${960 / window.devicePixelRatio}px`;
        }, 5);

        setTimeout(() => player?.togglePlayback(), 200);
    });
</script>

<div class="top-bar">
    <div class="left">
        <!-- <div class="logo"> -->
        <img class="logo" src={logo} alt="Logo" />
        <!-- </div> -->
    </div>

    <div class="right">
        <div>
            <label for="decoder-model">Decoder Model:</label>
            <select
                id="decoder-model"
                bind:value={decoderModel}
                onchange={handleDecoderModelChange}
            >
                <option value="" disabled>Select a model</option>
                {#each modelOptions as model}
                    <option value={model}>{model}</option>
                {/each}
            </select>
        </div>

        <div>
            <label for="scene-model">Scene Model:</label>
            <select
                id="scene-model"
                bind:value={sceneModel}
                onchange={handleSceneModelChange}
            >
                <option value="" disabled>Select a model</option>
                {#each modelOptions as model}
                    <option value={model}>{model}</option>
                {/each}
            </select>
        </div>
    </div>
</div>

<div class="preview" bind:this={previewRef}></div>
<br />
<textarea name="paragraph_text" onkeydown={(e) => handleText(e)}
    >{initial_text}</textarea
>

<div class="draggable-container">
    {#each scaled_boxes as scaled_box}
        <DraggableBox {...scaled_box} scalar={1 / window.devicePixelRatio} />
    {/each}
</div>

<style>
    .logo {
        width: 2.5rem;
    }

    .top-bar {
        padding: 0.2rem;
        height: 3rem;
        background-color: #fafafa;
        border-bottom: 1px solid #f2f2f2;
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }

    .left {
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 0.2rem;
    }

    .right {
        display: flex;
        flex-direction: row;
        align-items: center;
        padding-right: 1rem;
    }

    textarea {
        /* flex: 1; */
        height: 100px;
        margin: 5px 0;
        box-sizing: border-box;
    }

    .preview {
        border: 1px solid #bdbdbd;
        display: inline-flex; /* Change to inline-flex to shrink to fit content */
        align-items: flex-start; /* Align items to the start */
    }

    label {
        font-size: 1em;
        font-weight: 500;
        font-family: inherit;
        margin-right: 0.5em;
        margin-left: 1.5rem;
    }

    /* Dropdown styling */
    select {
        padding: 0.6em 1.2em;
        border-radius: 8px;
        border: 1px solid transparent;
        font-size: 1em;
        font-weight: 500;
        font-family: inherit;
        background-color: #1a1a1a;
        color: white;
        cursor: pointer;
        transition:
            border-color 0.25s,
            background-color 0.25s;
    }

    select:hover {
        border-color: #646cff;
    }

    select:focus,
    select:focus-visible {
        outline: 4px auto -webkit-focus-ring-color;
        background-color: #333;
    }

    /* Light mode styles */
    @media (prefers-color-scheme: light) {
        select {
            background-color: #f2f2f2;
            color: #213547;
        }

        select:hover {
            border-color: #747bff;
        }

        select:focus,
        select:focus-visible {
            background-color: #e0e0e0;
        }
    }
</style>
