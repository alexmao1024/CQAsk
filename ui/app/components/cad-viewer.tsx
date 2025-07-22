"use client"

import { useEffect, useRef } from 'react'
import "../../dist/three-cad-viewer/three-cad-viewer.css"
import { Viewer } from "../../dist/three-cad-viewer/three-cad-viewer.esm.js"

function nc(change: any) {}

export interface CadViewerProps {
    cadShapes: any
}


export default function CadViewer({ cadShapes }: CadViewerProps) {
    const ref = useRef(null)
    const { innerWidth: width, innerHeight: height } = window

    const viewerOptions = {
        theme: "light",
        ortho: true,
        control: "trackball", // "orbit",
        normalLen: 0,
        cadWidth: width,
        height: height * 0.85,
        ticks: 10,
        ambientIntensity: 0.9,
        directIntensity: 0.12,
        transparent: false,
        blackEdges: false,
        axes: true,
        grid: [false, false, false],
        timeit: false,
        rotateSpeed: 1,
        tools: false,
        glass: false
    }

    const renderOptions = {
        ambientIntensity: 1.0,
        directIntensity: 1.1,
        metalness: 0.30,
        roughness: 0.65,
        edgeColor: 0x707070,
        defaultOpacity: 0.5,
        normalLen: 0,
        up: "Z"
    }


    useEffect(() => {
        const container = ref.current

        // 如果没有cadShapes或cadShapes为空数组，清除viewer
        if (!cadShapes || !Array.isArray(cadShapes) || cadShapes.length === 0) {
            // 这里可以清除viewer或显示空状态
            return
        }

        if (cadShapes && Array.isArray(cadShapes) && cadShapes.length >= 2) {
            try {
                const viewer = new Viewer(container, viewerOptions, nc)
                
                // cadShapes 是一个包含 [shapes, meshed_instances] 的数组
                const [shapes, meshed_instances] = cadShapes
                
                // 检查数据是否有效
                if (!shapes || !meshed_instances) {
                    console.error("Invalid shapes or meshed_instances data:", { shapes, meshed_instances })
                    return
                }
                
                console.log("Rendering with shapes:", shapes)
                console.log("Rendering with meshed_instances:", meshed_instances)
                
                // 根据shapes结构生成正确的states
                const states: { [key: string]: any } = {}
                if (shapes && shapes.parts) {
                    shapes.parts.forEach((part: any) => {
                        if (part.id && part.state) {
                            states[part.id] = part.state
                        }
                    })
                }
                
                const renderFunction = (name: string, shapes: any, states: any) => {
                    viewer?.clear()
                    
                    // 确保 shapes 和 states 都存在且有效
                    if (!shapes || !states) {
                        console.error("Missing shapes or states for rendering:", { shapes, states })
                        return
                    }
                    
                    const [unselected, selected] = viewer.renderTessellatedShapes(shapes, states, renderOptions)
                    console.log("Unselected:", unselected)
                    console.log("Selected:", selected)

                    viewer.render(
                        unselected,
                        selected,
                        states,
                        renderOptions,
                    )
                }
                
                renderFunction("input", shapes, states)
            } catch (error) {
                console.error("Error rendering CAD shapes:", error)
            }
        } else {
            console.log("No valid cadShapes data:", cadShapes)
        }
    }, [cadShapes])

    return (
        <div ref={ref}></div>
    )
}