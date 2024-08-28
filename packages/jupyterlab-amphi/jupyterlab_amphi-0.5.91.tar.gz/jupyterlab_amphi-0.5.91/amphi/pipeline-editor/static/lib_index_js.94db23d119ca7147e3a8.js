"use strict";
(self["webpackChunk_amphi_pipeline_editor"] = self["webpackChunk_amphi_pipeline_editor"] || []).push([["lib_index_js"],{

/***/ "./lib/AboutDialog.js":
/*!****************************!*\
  !*** ./lib/AboutDialog.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   createAboutDialog: () => (/* binding */ createAboutDialog)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);

function createAboutDialog(versionNumber) {
    const versionInfo = (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "jp-About-version-info" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "jp-About-version" },
            "v",
            versionNumber)));
    const title = (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "jp-About-header" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("img", { src: "https://amphi.ai/icons/amphi_logo_paths.svg", alt: "Amphi Logo", className: "amphi-logo", style: { height: '24px', marginRight: '10px', verticalAlign: 'middle' } }),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-About-header-info", style: { display: 'inline-block', textAlign: 'center' } }, versionInfo)));
    const websiteURL = 'https://amphi.ai';
    const githubURL = 'https://github.com/amphi-ai/amphi-etl';
    const externalLinks = (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "jp-About-externalLinks" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("a", { href: websiteURL, target: "_blank", rel: "noopener noreferrer", className: "jp-Button-flat" }, "WEBSITE"),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("a", { href: githubURL, target: "_blank", rel: "noopener noreferrer", className: "jp-Button-flat" }, "GITHUB")));
    const copyright = (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "jp-About-copyright" }, "\u00A9 2024 Amphi"));
    const body = (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-About-body" },
        externalLinks,
        copyright));
    return { title, body };
}


/***/ }),

/***/ "./lib/AutoLayout.js":
/*!***************************!*\
  !*** ./lib/AutoLayout.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   getId: () => (/* binding */ getId),
/* harmony export */   getSourceHandlePosition: () => (/* binding */ getSourceHandlePosition),
/* harmony export */   getTargetHandlePosition: () => (/* binding */ getTargetHandlePosition),
/* harmony export */   layoutAlgorithms: () => (/* binding */ layoutAlgorithms)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! reactflow */ "webpack/sharing/consume/default/reactflow/reactflow");
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(reactflow__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _dagrejs_dagre__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @dagrejs/dagre */ "webpack/sharing/consume/default/@dagrejs/dagre/@dagrejs/dagre");
/* harmony import */ var _dagrejs_dagre__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_dagrejs_dagre__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _icons__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./icons */ "./lib/icons.js");




const dagreGraph = new (_dagrejs_dagre__WEBPACK_IMPORTED_MODULE_2___default().graphlib).Graph().setDefaultEdgeLabel(() => ({}));
const dagreLayout = async (nodes, edges, options) => {
    var _a, _b;
    dagreGraph.setGraph({
        rankdir: options.direction,
        nodesep: options.spacing[0],
        ranksep: options.spacing[1],
    });
    for (const node of nodes) {
        dagreGraph.setNode(node.id, {
            width: (_a = node.width) !== null && _a !== void 0 ? _a : 0,
            height: (_b = node.height) !== null && _b !== void 0 ? _b : 0,
        });
    }
    for (const edge of edges) {
        dagreGraph.setEdge(edge.source, edge.target);
    }
    _dagrejs_dagre__WEBPACK_IMPORTED_MODULE_2___default().layout(dagreGraph);
    const nextNodes = nodes.map((node) => {
        var _a;
        const { x, y } = dagreGraph.node(node.id);
        const position = {
            x: x - ((_a = node.width) !== null && _a !== void 0 ? _a : 0) / 2,
            // y: y - (node.height ?? 0) / 2, // align vertically (middle)
            y: y
        };
        return { ...node, position };
    });
    return { nodes: nextNodes, edges };
};
const layoutAlgorithms = {
    dagre: dagreLayout
};

function useAutoLayout(options) {
    const { fitView, setViewport, setNodes, setEdges } = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useReactFlow)();
    const nodesInitialized = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useNodesInitialized)();
    const elements = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useStore)((state) => ({
        nodeMap: state.nodeInternals,
        edgeMap: state.edges.reduce((acc, edge) => acc.set(edge.id, edge), new Map()),
    }), compareElements);
    const runLayout = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(async () => {
        if (!nodesInitialized || elements.nodeMap.size === 0) {
            return;
        }
        const layoutAlgorithm = layoutAlgorithms[options.algorithm];
        const nodes = [...elements.nodeMap.values()];
        const edges = [...elements.edgeMap.values()];
        const { nodes: nextNodes, edges: nextEdges } = await layoutAlgorithm(nodes, edges, options);
        for (const node of nextNodes) {
            node.style = { ...node.style, opacity: 1 };
            node.sourcePosition = getSourceHandlePosition(options.direction);
            node.targetPosition = getTargetHandlePosition(options.direction);
        }
        for (const edge of edges) {
            edge.style = { ...edge.style, opacity: 1 };
        }
        setNodes(nextNodes);
        setEdges(nextEdges);
        setViewport({ x: 0, y: 0, zoom: 1 });
        setTimeout(() => {
            fitView({ padding: 0.4 });
        }, 1);
    }, [nodesInitialized, elements, options, setNodes, setEdges]);
    return runLayout;
}
function compareElements(xs, ys) {
    return (compareNodes(xs.nodeMap, ys.nodeMap) && compareEdges(xs.edgeMap, ys.edgeMap));
}
function compareNodes(xs, ys) {
    if (xs.size !== ys.size)
        return false;
    for (const [id, x] of xs.entries()) {
        const y = ys.get(id);
        if (!y)
            return false;
        if (x.resizing || x.dragging)
            return true;
        if (x.width !== y.width || x.height !== y.height)
            return false;
    }
    return true;
}
function compareEdges(xs, ys) {
    if (xs.size !== ys.size)
        return false;
    for (const [id, x] of xs.entries()) {
        const y = ys.get(id);
        if (!y)
            return false;
        if (x.source !== y.source || x.target !== y.target)
            return false;
        if ((x === null || x === void 0 ? void 0 : x.sourceHandle) !== (y === null || y === void 0 ? void 0 : y.sourceHandle))
            return false;
        if ((x === null || x === void 0 ? void 0 : x.targetHandle) !== (y === null || y === void 0 ? void 0 : y.targetHandle))
            return false;
    }
    return true;
}
function getSourceHandlePosition(direction) {
    switch (direction) {
        case 'TB':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Bottom;
        case 'BT':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Top;
        case 'LR':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Right;
        case 'RL':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Left;
    }
}
function getTargetHandlePosition(direction) {
    switch (direction) {
        case 'TB':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Top;
        case 'BT':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Bottom;
        case 'LR':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Left;
        case 'RL':
            return reactflow__WEBPACK_IMPORTED_MODULE_1__.Position.Right;
    }
}
function getId() {
    return `${Date.now()}`;
}
function AutoLayoutButton() {
    const options = {
        algorithm: 'dagre',
        direction: 'LR',
        spacing: [100, 100],
    };
    const runLayout = useAutoLayout(options);
    const onClick = () => {
        runLayout();
    };
    return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_1__.ControlButton, { onClick: onClick },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_icons__WEBPACK_IMPORTED_MODULE_3__.alignIcon.react, null));
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (AutoLayoutButton);


/***/ }),

/***/ "./lib/CodeEditor.js":
/*!***************************!*\
  !*** ./lib/CodeEditor.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_ace__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-ace */ "../../node_modules/react-ace/lib/index.js");
/* harmony import */ var ace_builds_src_noconflict_mode_python__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ace-builds/src-noconflict/mode-python */ "../../node_modules/ace-builds/src-noconflict/mode-python.js");
/* harmony import */ var ace_builds_src_noconflict_mode_python__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(ace_builds_src_noconflict_mode_python__WEBPACK_IMPORTED_MODULE_2__);



const CodeEditor = ({ code }) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_ace__WEBPACK_IMPORTED_MODULE_1__["default"], { width: '950px', height: '500px', mode: "python", theme: "xcode", name: "Code Export", fontSize: 14, lineHeight: 19, showPrintMargin: true, showGutter: true, highlightActiveLine: true, value: code, setOptions: {
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        enableSnippets: true,
        showLineNumbers: true,
        tabSize: 2,
    } }));
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CodeEditor);


/***/ }),

/***/ "./lib/Commands.js":
/*!*************************!*\
  !*** ./lib/Commands.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   useCopyPaste: () => (/* binding */ useCopyPaste),
/* harmony export */   useUndoRedo: () => (/* binding */ useUndoRedo)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! reactflow */ "webpack/sharing/consume/default/reactflow/reactflow");
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(reactflow__WEBPACK_IMPORTED_MODULE_1__);


const Format = "application/react-flow-format";
function useCopyPaste() {
    const mousePosRef = (0,react__WEBPACK_IMPORTED_MODULE_0__.useRef)({ x: 0, y: 0 });
    const rfDomNode = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useStore)((state) => state.domNode);
    const { getNodes, setNodes, getEdges, setEdges, screenToFlowPosition } = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useReactFlow)();
    const [bufferedNodes, setBufferedNodes] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const [bufferedEdges, setBufferedEdges] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        const events = ['cut', 'copy', 'paste'];
        if (rfDomNode) {
            const onMouseMove = (event) => {
                mousePosRef.current = {
                    x: event.clientX,
                    y: event.clientY,
                };
            };
            rfDomNode.addEventListener('mousemove', onMouseMove);
            return () => {
                rfDomNode.removeEventListener('mousemove', onMouseMove);
            };
        }
    }, [rfDomNode]);
    const copy = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(() => {
        const selectedNodes = getNodes().filter((node) => node.selected);
        const selectedEdges = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.getConnectedEdges)(selectedNodes, getEdges()).filter((edge) => {
            const isExternalSource = selectedNodes.every((n) => n.id !== edge.source);
            const isExternalTarget = selectedNodes.every((n) => n.id !== edge.target);
            return !(isExternalSource || isExternalTarget);
        });
        const data = JSON.stringify({
            type: 'nodes-and-edges',
            nodes: selectedNodes,
            edges: selectedEdges,
        });
        navigator.clipboard.writeText(data);
    }, [getNodes, getEdges]);
    const cut = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(() => {
        const selectedNodes = getNodes().filter((node) => node.selected);
        const selectedEdges = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.getConnectedEdges)(selectedNodes, getEdges()).filter((edge) => {
            const isExternalSource = selectedNodes.every((n) => n.id !== edge.source);
            const isExternalTarget = selectedNodes.every((n) => n.id !== edge.target);
            return !(isExternalSource || isExternalTarget);
        });
        const data = JSON.stringify({
            type: 'nodes-and-edges',
            nodes: selectedNodes,
            edges: selectedEdges,
        });
        navigator.clipboard.writeText(data);
        setNodes((nodes) => nodes.filter((node) => !node.selected));
        setEdges((edges) => edges.filter((edge) => !selectedEdges.includes(edge)));
    }, [getNodes, setNodes, getEdges, setEdges]);
    const paste = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(async () => {
        const pastePos = screenToFlowPosition({
            x: mousePosRef.current.x,
            y: mousePosRef.current.y,
        });
        try {
            const text = await navigator.clipboard.readText();
            let parsedData;
            try {
                parsedData = JSON.parse(text);
            }
            catch (jsonError) {
                // If JSON parsing fails, it means it's plain text
                parsedData = null;
            }
            if (parsedData && parsedData.type === 'nodes-and-edges') {
                const { nodes: bufferedNodes, edges: bufferedEdges } = parsedData;
                const minX = Math.min(...bufferedNodes.map((s) => s.position.x));
                const minY = Math.min(...bufferedNodes.map((s) => s.position.y));
                const now = Date.now();
                const newNodes = bufferedNodes.map((node) => {
                    const id = `${node.id}-${now}`;
                    const x = pastePos.x + (node.position.x - minX);
                    const y = pastePos.y + (node.position.y - minY);
                    return { ...node, id, position: { x, y } };
                });
                const newEdges = bufferedEdges.map((edge) => {
                    const id = `${edge.id}-${now}`;
                    const source = `${edge.source}-${now}`;
                    const target = `${edge.target}-${now}`;
                    return { ...edge, id, source, target };
                });
                setNodes((nodes) => [
                    ...nodes.map((node) => ({ ...node, selected: false })),
                    ...newNodes,
                ]);
                setEdges((edges) => [
                    ...edges.map((edge) => ({ ...edge, selected: false })),
                    ...newEdges,
                ]);
            }
            else if (!parsedData) {
                // Handle plain text paste
                console.log("plain text");
                const activeElement = document.activeElement;
                console.log("active element %o", activeElement);
                console.log("active element tagname %o", activeElement.tagName);
                console.log("text %o", text);
                if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
                    activeElement.value += text;
                    // Manually trigger input event to ensure React picks up the change
                    const event = new Event('input', { bubbles: true });
                    activeElement.dispatchEvent(event);
                }
                else {
                    console.log("Pasted text: ", text);
                }
            }
            else {
                // Fallback to normal text paste if it's not nodes and edges
                console.log("fallback to normal");
            }
        }
        catch (error) {
            console.error("Failed to read clipboard contents: ", error);
        }
    }, [screenToFlowPosition, setNodes, setEdges]);
    useShortcut(['Meta+x', 'Control+x'], cut);
    useShortcut(['Meta+c', 'Control+c'], copy);
    useShortcut(['Meta+v', 'Control+v'], paste);
    return { cut, copy, paste, bufferedNodes, bufferedEdges };
}
function useShortcut(keyCode, callback) {
    const [didRun, setDidRun] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const shouldRun = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useKeyPress)(keyCode);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        if (shouldRun && !didRun) {
            callback();
            setDidRun(true);
        }
        else {
            setDidRun(shouldRun);
        }
    }, [shouldRun, didRun, callback]);
}
const defaultOptions = {
    maxHistorySize: 100,
    enableShortcuts: true,
};
// https://redux.js.org/usage/implementing-undo-history
const useUndoRedo = ({ maxHistorySize = defaultOptions.maxHistorySize, enableShortcuts = defaultOptions.enableShortcuts, } = defaultOptions) => {
    // the past and future arrays store the states that we can jump to
    const [past, setPast] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const [future, setFuture] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const { setNodes, setEdges, getNodes, getEdges } = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useReactFlow)();
    const takeSnapshot = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(() => {
        // push the current graph to the past state
        setPast((past) => [
            ...past.slice(past.length - maxHistorySize + 1, past.length),
            { nodes: getNodes(), edges: getEdges() },
        ]);
        // whenever we take a new snapshot, the redo operations need to be cleared to avoid state mismatches
        setFuture([]);
    }, [getNodes, getEdges, maxHistorySize]);
    const undo = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(() => {
        // get the last state that we want to go back to
        const pastState = past[past.length - 1];
        if (pastState) {
            // first we remove the state from the history
            setPast((past) => past.slice(0, past.length - 1));
            // we store the current graph for the redo operation
            setFuture((future) => [
                ...future,
                { nodes: getNodes(), edges: getEdges() },
            ]);
            // now we can set the graph to the past state
            setNodes(pastState.nodes);
            setEdges(pastState.edges);
        }
    }, [setNodes, setEdges, getNodes, getEdges, past]);
    const redo = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(() => {
        const futureState = future[future.length - 1];
        if (futureState) {
            setFuture((future) => future.slice(0, future.length - 1));
            setPast((past) => [...past, { nodes: getNodes(), edges: getEdges() }]);
            setNodes(futureState.nodes);
            setEdges(futureState.edges);
        }
    }, [setNodes, setEdges, getNodes, getEdges, future]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        // this effect is used to attach the global event handlers
        if (!enableShortcuts) {
            return;
        }
        const keyDownHandler = (event) => {
            if (event.key === 'z' &&
                (event.ctrlKey || event.metaKey) &&
                event.shiftKey) {
                redo();
            }
            else if (event.key === 'z' && (event.ctrlKey || event.metaKey)) {
                undo();
            }
        };
        document.addEventListener('keydown', keyDownHandler);
        return () => {
            document.removeEventListener('keydown', keyDownHandler);
        };
    }, [undo, redo, enableShortcuts]);
    return {
        undo,
        redo,
        takeSnapshot,
        canUndo: !past.length,
        canRedo: !future.length,
    };
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({ useUndoRedo, useCopyPaste });


/***/ }),

/***/ "./lib/Dropzone.js":
/*!*************************!*\
  !*** ./lib/Dropzone.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Dropzone: () => (/* binding */ Dropzone),
/* harmony export */   useDropzone: () => (/* binding */ useDropzone)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);

const useDropzone = (props) => {
    const rootRef = (0,react__WEBPACK_IMPORTED_MODULE_0__.useRef)(null);
    const handleEvent = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)((e) => {
        var _a, _b, _c, _d;
        e.preventDefault();
        e.stopPropagation();
        switch (e.type) {
            case 'lm-dragenter':
                (_a = props.onDragEnter) === null || _a === void 0 ? void 0 : _a.call(props, e);
                break;
            case 'lm-dragleave':
                (_b = props.onDragLeave) === null || _b === void 0 ? void 0 : _b.call(props, e);
                break;
            case 'lm-dragover':
                e.dropAction = e.proposedAction;
                (_c = props.onDragOver) === null || _c === void 0 ? void 0 : _c.call(props, e);
                break;
            case 'lm-drop':
                (_d = props.onDrop) === null || _d === void 0 ? void 0 : _d.call(props, e);
                break;
        }
    }, [props]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        const node = rootRef.current;
        node === null || node === void 0 ? void 0 : node.addEventListener('lm-dragenter', handleEvent);
        node === null || node === void 0 ? void 0 : node.addEventListener('lm-dragleave', handleEvent);
        node === null || node === void 0 ? void 0 : node.addEventListener('lm-dragover', handleEvent);
        node === null || node === void 0 ? void 0 : node.addEventListener('lm-drop', handleEvent);
        return () => {
            node === null || node === void 0 ? void 0 : node.removeEventListener('lm-dragenter', handleEvent);
            node === null || node === void 0 ? void 0 : node.removeEventListener('lm-dragleave', handleEvent);
            node === null || node === void 0 ? void 0 : node.removeEventListener('lm-dragover', handleEvent);
            node === null || node === void 0 ? void 0 : node.removeEventListener('lm-drop', handleEvent);
        };
    }, [handleEvent]);
    return {
        getRootProps: () => ({
            ref: rootRef,
        }),
    };
};
const Dropzone = ({ children, ...rest }) => {
    const { getRootProps } = useDropzone(rest);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: { height: '100%' }, ...getRootProps() }, children));
};


/***/ }),

/***/ "./lib/ExportToImage.js":
/*!******************************!*\
  !*** ./lib/ExportToImage.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! reactflow */ "webpack/sharing/consume/default/reactflow/reactflow");
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(reactflow__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var html_to_image__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! html-to-image */ "webpack/sharing/consume/default/html-to-image/html-to-image");
/* harmony import */ var html_to_image__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(html_to_image__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _icons__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./icons */ "./lib/icons.js");




function sanitizeFilename(filename) {
    return filename.replace(/[^a-z0-9]/gi, '_').toLowerCase();
}
function downloadImage(dataUrl, pipelineName) {
    const sanitizedFilename = sanitizeFilename(pipelineName);
    const a = document.createElement('a');
    a.setAttribute('download', `${sanitizedFilename}.svg`);
    a.setAttribute('href', dataUrl);
    a.click();
}
function DownloadImageButton({ pipelineName, pipelineId }) {
    const { getNodes } = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useReactFlow)();
    const onClick = () => {
        const nodesBounds = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.getNodesBounds)(getNodes());
        const viewportElement = document.querySelector(`.reactflow-wrapper[data-id="${pipelineId}"]`);
        if (viewportElement instanceof HTMLElement) {
            const { width, height } = viewportElement.getBoundingClientRect();
            // const transform = getTransformForBounds(nodesBounds, width, height, 0.5, 2);
            (0,html_to_image__WEBPACK_IMPORTED_MODULE_2__.toSvg)(viewportElement, {
                backgroundColor: '#ffffff',
                width: width,
                height: height
            }).then((dataUrl) => downloadImage(dataUrl, pipelineName));
        }
    };
    return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_1__.ControlButton, { onClick: onClick },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_icons__WEBPACK_IMPORTED_MODULE_3__.exportIcon.react, null));
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DownloadImageButton);


/***/ }),

/***/ "./lib/PipelineEditorWidget.js":
/*!*************************************!*\
  !*** ./lib/PipelineEditorWidget.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   FitViewOptions: () => (/* binding */ FitViewOptions),
/* harmony export */   PipelineEditorFactory: () => (/* binding */ PipelineEditorFactory),
/* harmony export */   PipelineEditorWidget: () => (/* binding */ PipelineEditorWidget),
/* harmony export */   commandIDs: () => (/* binding */ commandIDs)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/docregistry */ "webpack/sharing/consume/default/@jupyterlab/docregistry");
/* harmony import */ var _jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _ExportToImage__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! ./ExportToImage */ "./lib/ExportToImage.js");
/* harmony import */ var _AutoLayout__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! ./AutoLayout */ "./lib/AutoLayout.js");
/* harmony import */ var _Commands__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./Commands */ "./lib/Commands.js");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _Sidebar__WEBPACK_IMPORTED_MODULE_17__ = __webpack_require__(/*! ./Sidebar */ "./lib/Sidebar.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! reactflow */ "webpack/sharing/consume/default/reactflow/reactflow");
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(reactflow__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! antd */ "webpack/sharing/consume/default/antd/antd");
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(antd__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @amphi/pipeline-components-manager */ "webpack/sharing/consume/default/@amphi/pipeline-components-manager");
/* harmony import */ var _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(_amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var _customEdge__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./customEdge */ "./lib/customEdge.js");
/* harmony import */ var reactflow_dist_style_css__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! reactflow/dist/style.css */ "./node_modules/reactflow/dist/style.css");
/* harmony import */ var _style_output_css__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../style/output.css */ "./style/output.css");
/* harmony import */ var _icons__WEBPACK_IMPORTED_MODULE_19__ = __webpack_require__(/*! ./icons */ "./lib/icons.js");
/* harmony import */ var _Dropzone__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./Dropzone */ "./lib/Dropzone.js");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! react-dom */ "webpack/sharing/consume/default/react-dom");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_11___default = /*#__PURE__*/__webpack_require__.n(react_dom__WEBPACK_IMPORTED_MODULE_11__);
/* harmony import */ var _CodeEditor__WEBPACK_IMPORTED_MODULE_18__ = __webpack_require__(/*! ./CodeEditor */ "./lib/CodeEditor.js");




















const PIPELINE_CLASS = 'amphi-PipelineEditor';
const commandIDs = {
    openDocManager: 'docmanager:open',
    newDocManager: 'docmanager:new-untitled',
    saveDocManager: 'docmanager:save',
};
const FitViewOptions = {
    padding: 10,
    maxZoom: 1.0
};
/**
 * Initialization: The class extends ReactWidget and initializes the pipeline editor widget. It sets up the initial properties and state for the widget.
 */
class PipelineEditorWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    // Constructor
    constructor(options) {
        super();
        this.browserFactory = options.browserFactory;
        this.defaultFileBrowser = options.defaultFileBrowser;
        this.shell = options.shell;
        this.toolbarRegistry = options.toolbarRegistry;
        this.commands = options.commands;
        this.context = options.context;
        this.settings = options.settings;
        this.componentService = options.componentService;
        let nullPipeline = this.context.model.toJSON() === null;
        this.context.model.contentChanged.connect(() => {
            if (nullPipeline) {
                nullPipeline = false;
                this.update();
            }
        });
    }
    /*
    * Rendering: The render() method is responsible for rendering the widget's UI.
    * It uses various components and elements to display the pipeline editor's interface.
    */
    render() {
        var _a;
        if (this.context.model.toJSON() === null) {
            return react__WEBPACK_IMPORTED_MODULE_5___default().createElement("div", { className: "amphi-loader" });
        }
        return (react__WEBPACK_IMPORTED_MODULE_5___default().createElement(PipelineWrapper, { context: this.context, browserFactory: this.browserFactory, defaultFileBrowser: this.defaultFileBrowser, shell: this.shell, toolbarRegistry: this.toolbarRegistry, commands: this.commands, widgetId: (_a = this.parent) === null || _a === void 0 ? void 0 : _a.id, settings: this.settings, componentService: this.componentService }));
    }
}
const PipelineWrapper = ({ context, browserFactory, defaultFileBrowser, shell, toolbarRegistry, commands, settings, widgetId, componentService, }) => {
    const manager = defaultFileBrowser.model.manager;
    const edgeTypes = {
        'custom-edge': _customEdge__WEBPACK_IMPORTED_MODULE_12__["default"]
    };
    const nodeTypes = componentService.getComponents().reduce((acc, component) => {
        const id = component._id;
        const ComponentUI = (props) => react__WEBPACK_IMPORTED_MODULE_5___default().createElement(component.UIComponent, { context: context, componentService: componentService, manager: manager, commands: commands, settings: settings, ...props });
        acc[id] = (props) => react__WEBPACK_IMPORTED_MODULE_5___default().createElement(ComponentUI, { context: context, componentService: componentService, manager: manager, commands: commands, ...props });
        return acc;
    }, {});
    const getNodeId = () => `node_${+new Date()}`;
    function PipelineFlow(context) {
        const reactFlowWrapper = (0,react__WEBPACK_IMPORTED_MODULE_5__.useRef)(null);
        const [pipeline, setPipeline] = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(context.context.model.toJSON());
        const pipelineId = pipeline['id'];
        const initialNodes = pipeline['pipelines'][0]['flow']['nodes'];
        const initialEdges = pipeline['pipelines'][0]['flow']['edges'];
        const initialViewport = pipeline['pipelines'][0]['flow']['viewport'];
        const defaultViewport = { x: 0, y: 0, zoom: 1 };
        const [nodes, setNodes, onNodesChange] = (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.useNodesState)(initialNodes);
        const [edges, setEdges, onEdgesChange] = (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.useEdgesState)(initialEdges);
        const [reactFlowInstance, setRfInstance] = (0,react__WEBPACK_IMPORTED_MODULE_5__.useState)(null);
        const { getViewport, setViewport } = (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.useReactFlow)();
        const store = (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.useStoreApi)();
        // Proximity connect
        /*
        const MIN_DISTANCE = 150;
    
        const getClosestEdge = useCallback((node) => {
          const { nodeInternals } = store.getState();
          const storeNodes = Array.from(nodeInternals.values());
    
          const closestNode = storeNodes.reduce(
            (res, n) => {
              if (n.id !== node.id) {
                const dx = n.positionAbsolute.x - node.positionAbsolute.x;
                const dy = n.positionAbsolute.y - node.positionAbsolute.y;
                const d = Math.sqrt(dx * dx + dy * dy);
    
                if (d < res.distance && d < MIN_DISTANCE) {
                  res.distance = d;
                  res.node = n;
                }
              }
    
              return res;
            },
            {
              distance: Number.MAX_VALUE,
              node: null,
            },
          );
    
          if (!closestNode.node) {
            return null;
          }
    
          const closeNodeIsSource =
            closestNode.node.positionAbsolute.x < node.positionAbsolute.x;
    
          return {
            id: closeNodeIsSource
              ? `${closestNode.node.id}-${node.id}`
              : `${node.id}-${closestNode.node.id}`,
            source: closeNodeIsSource ? closestNode.node.id : node.id,
            target: closeNodeIsSource ? node.id : closestNode.node.id,
          };
        }, []);
    
        const onNodeDrag = useCallback(
          (_, node) => {
            const closeEdge = getClosestEdge(node);
      
            setEdges((es) => {
              const nextEdges = es.filter((e) => e.className !== 'temp');
      
              if (
                closeEdge &&
                !nextEdges.find(
                  (ne) =>
                    ne.source === closeEdge.source && ne.target === closeEdge.target,
                )
              ) {
                // closeEdge.className = 'temp';
                nextEdges.push(closeEdge);
              }
      
              return nextEdges;
            });
          },
          [getClosestEdge, setEdges],
        );
      
        const onNodeDragStop = useCallback(
          (_, node) => {
            const closeEdge = getClosestEdge(node);
      
            setEdges((es) => {
              const nextEdges = es.filter((e) => e.className !== 'temp');
      
              if (
                closeEdge &&
                !nextEdges.find(
                  (ne) =>
                    ne.source === closeEdge.source && ne.target === closeEdge.target,
                )
              ) {
                nextEdges.push(closeEdge);
              }
      
              return nextEdges;
            });
          },
          [getClosestEdge],
        );
        */
        // Copy paste
        // const { cut, copy, paste, bufferedNodes } = useCopyPaste();
        // Undo and Redo
        const { undo, redo, canUndo, canRedo, takeSnapshot } = (0,_Commands__WEBPACK_IMPORTED_MODULE_13__.useUndoRedo)();
        const onNodeDragStart = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)(() => {
            // 👇 make dragging a node undoable
            takeSnapshot();
            // 👉 you can place your event handlers here
        }, [takeSnapshot]);
        const onSelectionDragStart = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)(() => {
            // 👇 make dragging a selection undoable
            takeSnapshot();
        }, [takeSnapshot]);
        const onEdgesDelete = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)(() => {
            // 👇 make deleting edges undoable
            takeSnapshot();
        }, [takeSnapshot]);
        const updatedPipeline = pipeline;
        updatedPipeline['pipelines'][0]['flow']['nodes'] = nodes;
        updatedPipeline['pipelines'][0]['flow']['edges'] = edges;
        updatedPipeline['pipelines'][0]['flow']['viewport'] = getViewport();
        // Save pipeline in current model
        // This means the file can then been save on "disk"
        context.context.model.fromJSON(updatedPipeline);
        // const onConnect = useCallback((params) => setEdges((eds) => addEdge({ ...params, type: 'custom-edge' }, eds)), [setEdges]);
        const onConnect = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)((connection) => {
            // 👇 make adding edges undoable
            takeSnapshot();
            setEdges((edges) => (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.addEdge)({ ...connection, type: 'custom-edge' }, edges));
        }, [setEdges, takeSnapshot]);
        const getCategory = (nodeId) => {
            const node = nodes.find(node => node.id === nodeId);
            if (node) {
                return componentService.getComponent(node.type)._type;
            }
            return undefined;
        };
        const isValidConnection = (connection) => {
            const sourceCategory = getCategory(connection.source);
            const targetCategory = getCategory(connection.target);
            if ((sourceCategory === "pandas_df_to_documents_processor")) {
                return targetCategory.startsWith("documents");
            }
            else if (sourceCategory.startsWith("documents")) {
                return targetCategory.startsWith("documents");
            }
            else if (sourceCategory.startsWith("pandas_df")) {
                return targetCategory.startsWith("pandas_df");
            }
            else {
                return false;
            }
        };
        const onNodesDelete = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)((deleted) => {
            setEdges(deleted.reduce((acc, node) => {
                const incomers = (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.getIncomers)(node, nodes, edges);
                const outgoers = (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.getOutgoers)(node, nodes, edges);
                const connectedEdges = (0,reactflow__WEBPACK_IMPORTED_MODULE_6__.getConnectedEdges)([node], edges);
                const remainingEdges = acc.filter((edge) => !connectedEdges.includes(edge));
                const createdEdges = incomers.flatMap(({ id: source }) => outgoers.map(({ id: target }) => ({ id: `${source}->${target}`, source, target, type: 'custom-edge' })));
                return [...remainingEdges, ...createdEdges];
            }, edges));
            takeSnapshot();
        }, [nodes, edges, takeSnapshot]);
        const handleAddFileToPipeline = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)((location) => {
            var _a;
            const fileBrowser = defaultFileBrowser;
            // Only add file to pipeline if it is currently in focus
            if (((_a = shell.currentWidget) === null || _a === void 0 ? void 0 : _a.id) !== widgetId) {
                return;
            }
            if (reactFlowInstance && location) {
                const { height, width, transform: [transformX, transformY, zoomLevel] } = store.getState();
                const zoomMultiplier = 1 / zoomLevel;
                // Calculate the adjusted position based on the transformation values and zoom level
                const adjustedPosition = {
                    x: (location.x - transformX) * zoomMultiplier,
                    y: (location.y - transformY) * zoomMultiplier,
                };
                Array.from(fileBrowser.selectedItems()).forEach(async (item) => {
                    const filePath = item.path;
                    const fileExtension = item.name.split('.').pop();
                    if (fileExtension === "amcpn") {
                        const contentsManager = new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_4__.ContentsManager();
                        try {
                            const file = await contentsManager.get(filePath);
                            console.log('File %o:', file);
                            const content = file.content;
                            console.log('File Content:', content);
                            const fileData = JSON.parse(content);
                            console.log("fileData %o", fileData);
                            const { type: nodeType, data: nodeData } = fileData.component;
                            if (nodeType && nodeData) {
                                const newNode = {
                                    id: getNodeId(),
                                    type: nodeType,
                                    position: adjustedPosition,
                                    data: {
                                        ...nodeData,
                                        lastUpdated: Date.now()
                                    }
                                };
                                setNodes((nds) => nds.concat(newNode));
                            }
                            else {
                                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                                    title: 'Invalid Component',
                                    body: 'The selected file does not contain valid component data.',
                                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
                                });
                            }
                        }
                        catch (error) {
                            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                                title: 'Error Reading File',
                                body: `There was an error reading the file.`,
                                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
                            });
                        }
                        return;
                    }
                    const { id: nodeType, default: nodeDefaults } = _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_8__.PipelineService.getComponentIdForFileExtension(fileExtension, componentService);
                    // Check if nodeType exists
                    if (nodeType) {
                        const newNode = {
                            id: getNodeId(),
                            type: nodeType,
                            position: adjustedPosition,
                            data: {
                                filePath: _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_8__.PipelineService.getRelativePath(context.context.sessionContext.path, filePath),
                                lastUpdated: Date.now(),
                                ...(nodeDefaults || {}) // Merge nodeDefaults into the data field
                            }
                        };
                        // Add the new node to the pipeline
                        setNodes((nds) => nds.concat(newNode));
                    }
                    else {
                        // If nodeType doesn't exist, show the dialog
                        (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                            title: 'Unsupported File(s)',
                            body: 'Only supported files can be added to a pipeline.',
                            buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
                        });
                    }
                });
            }
            return;
        }, [defaultFileBrowser, shell, widgetId, reactFlowInstance]);
        const handleFileDrop = async (e) => {
            takeSnapshot();
            handleAddFileToPipeline({ x: e.offsetX, y: e.offsetY });
        };
        const onDragOver = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)((event) => {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'move';
        }, []);
        const onDrop = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)((event) => {
            takeSnapshot();
            event.preventDefault();
            const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
            const type = event.dataTransfer.getData('application/reactflow');
            const config = event.dataTransfer.getData('additionalData');
            // check if the dropped element is valid
            if (typeof type === 'undefined' || !type) {
                return;
            }
            const position = reactFlowInstance.project({
                x: event.clientX - reactFlowBounds.left,
                y: event.clientY - reactFlowBounds.top,
            });
            const newNode = {
                id: getNodeId(),
                type,
                position,
                data: {
                    ...config,
                    lastUpdated: Date.now(), // current timestamp in milliseconds
                }
            };
            setNodes((nds) => nds.concat(newNode));
        }, [reactFlowInstance]);
        const onViewportChange = (0,react__WEBPACK_IMPORTED_MODULE_5__.useCallback)((viewport) => {
            const updatedPipeline = { ...pipeline };
            updatedPipeline['pipelines'][0]['flow']['viewport'] = viewport;
            console.log("update viewport");
            context.context.model.fromJSON(updatedPipeline);
        }, [pipeline, context]);
        const proOptions = { hideAttribution: true };
        return (react__WEBPACK_IMPORTED_MODULE_5___default().createElement("div", { className: "reactflow-wrapper", "data-id": pipelineId, ref: reactFlowWrapper },
            react__WEBPACK_IMPORTED_MODULE_5___default().createElement(_Dropzone__WEBPACK_IMPORTED_MODULE_14__.Dropzone, { onDrop: handleFileDrop },
                react__WEBPACK_IMPORTED_MODULE_5___default().createElement((reactflow__WEBPACK_IMPORTED_MODULE_6___default()), { id: pipelineId, nodes: nodes, edges: edges, onNodesChange: onNodesChange, onNodesDelete: onNodesDelete, onEdgesDelete: onEdgesDelete, onEdgesChange: onEdgesChange, onConnect: onConnect, onNodeDragStart: onNodeDragStart, onSelectionDragStart: onSelectionDragStart, isValidConnection: isValidConnection, onDrop: onDrop, onDragOver: onDragOver, 
                    // onNodeDrag={onNodeDrag}
                    // onNodeDragStop={onNodeDragStop}
                    onInit: setRfInstance, edgeTypes: edgeTypes, nodeTypes: nodeTypes, snapToGrid: true, snapGrid: [15, 15], fitViewOptions: { minZoom: 0.5, maxZoom: 1.0, padding: 0.4 }, defaultViewport: initialViewport, 
                    // viewport={initialViewport}
                    // onViewportChange={onViewportChange}
                    deleteKeyCode: [], proOptions: proOptions },
                    react__WEBPACK_IMPORTED_MODULE_5___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_6__.Panel, { position: "top-right" }),
                    react__WEBPACK_IMPORTED_MODULE_5___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_6__.Controls, null,
                        react__WEBPACK_IMPORTED_MODULE_5___default().createElement(_ExportToImage__WEBPACK_IMPORTED_MODULE_15__["default"], { pipelineName: context.context.sessionContext.path, pipelineId: pipelineId }),
                        react__WEBPACK_IMPORTED_MODULE_5___default().createElement(_AutoLayout__WEBPACK_IMPORTED_MODULE_16__["default"], null)),
                    react__WEBPACK_IMPORTED_MODULE_5___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_6__.Background, { color: "#aaa", gap: 15 })))));
    }
    return (react__WEBPACK_IMPORTED_MODULE_5___default().createElement("div", { className: "canvas", id: "pipeline-panel" },
        react__WEBPACK_IMPORTED_MODULE_5___default().createElement(antd__WEBPACK_IMPORTED_MODULE_7__.ConfigProvider, { theme: {
                token: {
                    // Seed Token
                    colorPrimary: '#5F9B97',
                },
            } },
            react__WEBPACK_IMPORTED_MODULE_5___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_6__.ReactFlowProvider, null,
                react__WEBPACK_IMPORTED_MODULE_5___default().createElement(PipelineFlow, { context: context }),
                react__WEBPACK_IMPORTED_MODULE_5___default().createElement(_Sidebar__WEBPACK_IMPORTED_MODULE_17__["default"], { componentService: componentService })))));
};
class PipelineEditorFactory extends _jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_1__.ABCWidgetFactory {
    constructor(options) {
        super(options);
        this.browserFactory = options.browserFactory;
        this.defaultFileBrowser = options.defaultFileBrowser;
        this.shell = options.shell;
        this.toolbarRegistry = options.toolbarRegistry;
        this.commands = options.commands;
        this.settings = options.settings;
        this.componentService = options.componentService;
    }
    createNewWidget(context) {
        // Creates a blank widget with a DocumentWidget wrapper
        const props = {
            shell: this.shell,
            toolbarRegistry: this.toolbarRegistry,
            commands: this.commands,
            browserFactory: this.browserFactory,
            defaultFileBrowser: this.defaultFileBrowser,
            context: context,
            settings: this.settings,
            componentService: this.componentService,
        };
        let enableExecution = this.settings.get('enableExecution').composite;
        console.log(`Settings extension in PipelineEditor: enableExecution is set to '${enableExecution}'`);
        if (enableExecution) {
            context.sessionContext.kernelPreference = { autoStartDefault: true, name: 'python', shutdownOnDispose: false };
        }
        else {
            context.sessionContext.kernelPreference = { shouldStart: false, canStart: false, shutdownOnDispose: true };
        }
        const content = new PipelineEditorWidget(props);
        const widget = new _jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_1__.DocumentWidget({ content, context });
        // Add save button
        // const saveButton = DocToolbarItems.createSaveButton(this.commands, context.fileChanged);
        const saveButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            label: 'Save Pipeline',
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.saveIcon,
            onClick: () => {
                this.commands.execute('docmanager:save');
            }
        });
        widget.toolbar.addItem('save', saveButton);
        async function showCodeModal(code, commands) {
            const editorDiv = document.createElement('div');
            editorDiv.style.width = '100%';
            editorDiv.style.height = '500px';
            const widget = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Widget({ node: editorDiv });
            react_dom__WEBPACK_IMPORTED_MODULE_11___default().render(react__WEBPACK_IMPORTED_MODULE_5___default().createElement(_CodeEditor__WEBPACK_IMPORTED_MODULE_18__["default"], { code: code }), editorDiv);
            const saveAsFile = async () => {
                console.log("Before file");
                console.log("context %o", context);
                const file = await commands.execute('docmanager:new-untitled', { path: '/', type: 'file', ext: '.py' });
                console.log("before doc");
                const doc = await commands.execute('docmanager:open', { path: file.path });
                doc.context.model.fromString(code);
            };
            const result = await (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: 'Generated Python Code',
                body: widget,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'Close' }),
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.createButton({
                        label: 'Open in new file',
                        className: '',
                        accept: true
                    })],
            });
            console.log("result %o", result);
            if (result.button.label === 'Open in new file') {
                console.log("Before save as");
                await saveAsFile();
            }
            // Render the AceEditor inside the dialog
        }
        // Add generate code button
        const generateCodeButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            label: 'Export to Python code',
            iconLabel: 'Export to Python code',
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.buildIcon,
            onClick: async () => {
                const code = await _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_8__.CodeGenerator.generateCode(context.model.toString(), this.commands, this.componentService);
                showCodeModal(code, this.commands);
            }
        });
        widget.toolbar.addItem('generateCode', generateCodeButton);
        // Add run button
        const runButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            label: 'Run Pipeline',
            iconLabel: 'Run Pipeline',
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.runIcon,
            onClick: async () => {
                // First save document
                this.commands.execute('docmanager:save');
                // Second, generate code
                const code = _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_8__.CodeGenerator.generateCode(context.model.toString(), this.commands, this.componentService);
                this.commands.execute('pipeline-editor:run-pipeline', { code }).catch(reason => {
                    console.error(`An error occurred during the execution of 'pipeline-editor:run-pipeline'.\n${reason}`);
                });
            },
            enabled: enableExecution
        });
        widget.toolbar.addItem('runPipeline', runButton);
        // Add Metadata panel
        /*
        const previewPanel = new ToolbarButton({
          label: 'Metadata Panel',
          iconLabel: 'Metadata Panel',
          icon: inspectorIcon,
          onClick: async () => {
            // Call the command execution
            const command = 'metadatapanel:open';
            this.commands.execute(command, {}).catch(reason => {
              console.error(
                `An error occurred during the execution of ${command}.\n${reason}`
              );
            });
          }
        });
        widget.toolbar.addItem('openPreviewPanel', previewPanel);
        */
        // Add Log panel
        const logconsole = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            label: 'Console',
            iconLabel: 'Console',
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.listIcon,
            onClick: async () => {
                // Call the command execution
                const command = 'pipeline-console:open';
                this.commands.execute(command, {}).catch(reason => {
                    console.error(`An error occurred during the execution of ${command}.\n${reason}`);
                });
            },
            enabled: enableExecution
        });
        widget.toolbar.addItem('openlogconsole', logconsole);
        const kernelName = _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Toolbar.createKernelNameItem(props.context.sessionContext);
        const spacer = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.Toolbar.createSpacerItem();
        widget.toolbar.addItem('spacer', spacer);
        widget.toolbar.addItem('kernelName', kernelName);
        // add restart runtime button
        /*
        const restartButton = new ToolbarButton({
            label: 'Restart Runtime',
            iconLabel: 'Restart Runtime',
            icon: refreshIcon,
            onClick: async () => {
              // Call the command execution
              const command = 'pipeline-editor:restart-kernel';
              this.commands.execute(command, {}).catch(reason => {
              
              console.error(
                `An error occurred during the execution of ${command}.\n${reason}`
              );
            });
            }
        });
        widget.toolbar.addItem('restartKernel', restartButton);
        */
        widget.addClass(PIPELINE_CLASS);
        widget.title.icon = _icons__WEBPACK_IMPORTED_MODULE_19__.pipelineIcon;
        return widget;
    }
}


/***/ }),

/***/ "./lib/Sidebar.js":
/*!************************!*\
  !*** ./lib/Sidebar.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! antd */ "webpack/sharing/consume/default/antd/antd");
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(antd__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _ant_design_icons__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @ant-design/icons */ "../../node_modules/@ant-design/icons/es/icons/SearchOutlined.js");



const { DirectoryTree } = antd__WEBPACK_IMPORTED_MODULE_1__.Tree;
const { Search } = antd__WEBPACK_IMPORTED_MODULE_1__.Input;
const Sidebar = ({ componentService }) => {
    const [searchValue, setSearchValue] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)('');
    const [expandedKeys, setExpandedKeys] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const [autoExpandParent, setAutoExpandParent] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(true);
    const [components, setComponents] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        const fetchedComponents = componentService.getComponents();
        setComponents(fetchedComponents);
        console.log('Fetched components:', fetchedComponents);
    }, [componentService]);
    const onDragStart = (event, nodeType, config) => {
        event.dataTransfer.setData('application/reactflow', nodeType);
        event.dataTransfer.setData('additionalData', config);
        event.dataTransfer.effectAllowed = 'move';
    };
    const categorizedComponents = (0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => {
        const result = {};
        components.forEach(component => {
            let [category, subcategory] = component._category.split('.');
            if (!result[category]) {
                result[category] = {};
            }
            if (subcategory) {
                if (!result[category][subcategory]) {
                    result[category][subcategory] = [];
                }
                result[category][subcategory].push(component);
            }
            else {
                if (!result[category]['_']) {
                    result[category]['_'] = [];
                }
                result[category]['_'].push(component);
            }
        });
        console.log('Categorized components:', result);
        return result;
    }, [components]);
    const getTreeData = () => {
        return Object.keys(categorizedComponents).map((category, index) => {
            const subCategories = Object.keys(categorizedComponents[category]);
            let children = [];
            subCategories.forEach((subCat, subIndex) => {
                if (subCat === '_') {
                    children.push(...categorizedComponents[category][subCat].map((component, childIndex) => ({
                        title: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { draggable: true, className: "palette-component", onDragStart: (event) => onDragStart(event, component._id, component.getDefaultConfig ? component.getDefaultConfig() : ''), key: `category-${index}-item-${childIndex}` }, component._name)),
                        key: `category-${index}-item-${childIndex}`,
                        isLeaf: true,
                        icon: react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "anticon" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(component._icon.react, { height: "14px", width: "14px;" }))
                    })));
                }
                else {
                    children.push({
                        title: react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "palette-component-category" }, subCat.charAt(0).toUpperCase() + subCat.slice(1)),
                        key: `category-${index}-sub-${subIndex}`,
                        children: categorizedComponents[category][subCat].map((component, childIndex) => ({
                            title: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { draggable: true, className: "palette-component", onDragStart: (event) => onDragStart(event, component._id, component.getDefaultConfig ? component.getDefaultConfig() : ''), key: `category-${index}-sub-${subIndex}-item-${childIndex}` }, component._name)),
                            key: `category-${index}-sub-${subIndex}-item-${childIndex}`,
                            isLeaf: true,
                            icon: react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "anticon" },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(component._icon.react, { height: "14px", width: "14px;" }))
                        }))
                    });
                }
            });
            return {
                title: react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "palette-component-category" }, category.charAt(0).toUpperCase() + category.slice(1)),
                key: `category-${index}`,
                children: children
            };
        });
    };
    const filterTree = (data, searchValue) => {
        console.log('Filtering tree with search value:', searchValue);
        const filteredData = data
            .map((item) => {
            const newItem = { ...item };
            if (newItem.children) {
                newItem.children = filterTree(newItem.children, searchValue);
            }
            if (newItem.title.props.children.toLowerCase().includes(searchValue.toLowerCase()) ||
                (newItem.children && newItem.children.length > 0)) {
                return newItem;
            }
            return null;
        })
            .filter(item => item !== null);
        console.log('Filtered data:', filteredData);
        return filteredData;
    };
    const onSearch = (e) => {
        const { value } = e.target;
        setSearchValue(value);
        setAutoExpandParent(true);
    };
    const treeData = (0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(getTreeData, [categorizedComponents]);
    const filteredTreeData = (0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => {
        if (searchValue && searchValue.trim()) {
            console.log("Filter applied:", searchValue);
            return filterTree(treeData, searchValue);
        }
        else {
            console.log("No filter applied");
            return treeData;
        }
    }, [searchValue, treeData]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        const collectKeys = (data) => {
            return data.reduce((acc, item) => {
                // Add the current item's key to the accumulator array
                acc.push(item.key);
                // If the current item has children, recursively collect their keys
                if (item.children) {
                    acc.push(...collectKeys(item.children));
                }
                return acc; // Return the accumulated keys
            }, []);
        };
        // Collect keys based on the presence of a search value
        const keys = searchValue ? collectKeys(filteredTreeData) : Object.keys(categorizedComponents).map((category, index) => `category-${index}`);
        setExpandedKeys(keys); // Update the expanded keys state
    }, [searchValue, filteredTreeData, categorizedComponents]);
    const onExpand = (keys) => {
        setExpandedKeys(keys);
        setAutoExpandParent(false);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("aside", { className: "sidebar", title: 'Components' },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(antd__WEBPACK_IMPORTED_MODULE_1__.Space, { direction: "vertical", style: { marginTop: '10px', marginLeft: '10px', width: '90%', textAlign: 'center' } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(antd__WEBPACK_IMPORTED_MODULE_1__.Input, { placeholder: "Search components", onChange: onSearch, style: { marginBottom: 8 }, suffix: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_ant_design_icons__WEBPACK_IMPORTED_MODULE_2__["default"], { style: { color: 'rgba(0,0,0,.25)' } }) })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(DirectoryTree, { selectable: false, multiple: true, blockNode: true, autoExpandParent: autoExpandParent, expandedKeys: expandedKeys, onExpand: onExpand, treeData: filteredTreeData })));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Sidebar);


/***/ }),

/***/ "./lib/customEdge.js":
/*!***************************!*\
  !*** ./lib/customEdge.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ CustomEdge)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! reactflow */ "webpack/sharing/consume/default/reactflow/reactflow");
/* harmony import */ var reactflow__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(reactflow__WEBPACK_IMPORTED_MODULE_1__);


const onEdgeClick = (evt, id) => {
    evt.stopPropagation();
    alert(`remove ${id}`);
};
function CustomEdge({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style = {}, markerEnd, }) {
    const { setEdges } = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.useReactFlow)();
    const [edgePath, labelX, labelY] = (0,reactflow__WEBPACK_IMPORTED_MODULE_1__.getBezierPath)({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });
    const onEdgeClick = () => {
        setEdges((edges) => edges.filter((edge) => edge.id !== id));
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_1__.BaseEdge, { path: edgePath, markerEnd: markerEnd, style: style }),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(reactflow__WEBPACK_IMPORTED_MODULE_1__.EdgeLabelRenderer, null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: {
                    position: 'absolute',
                    transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                    fontSize: 12,
                    // everything inside EdgeLabelRenderer has no pointer events by default
                    // if you have an interactive element, set pointer-events: all
                    pointerEvents: 'all',
                }, className: "nodrag nopan" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("button", { className: "edgebutton", onClick: onEdgeClick }, "\u00D7")))));
}


/***/ }),

/***/ "./lib/icons.js":
/*!**********************!*\
  !*** ./lib/icons.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   alignIcon: () => (/* binding */ alignIcon),
/* harmony export */   apiIcon: () => (/* binding */ apiIcon),
/* harmony export */   componentIcon: () => (/* binding */ componentIcon),
/* harmony export */   exportIcon: () => (/* binding */ exportIcon),
/* harmony export */   filePlusIcon: () => (/* binding */ filePlusIcon),
/* harmony export */   fileTextIcon: () => (/* binding */ fileTextIcon),
/* harmony export */   monitorIcon: () => (/* binding */ monitorIcon),
/* harmony export */   pipelineBrandIcon: () => (/* binding */ pipelineBrandIcon),
/* harmony export */   pipelineCategoryIcon: () => (/* binding */ pipelineCategoryIcon),
/* harmony export */   pipelineIcon: () => (/* binding */ pipelineIcon)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _style_icons_file_text_24_svg__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../style/icons/file-text-24.svg */ "./style/icons/file-text-24.svg");
/* harmony import */ var _style_icons_file_plus_24_svg__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../style/icons/file-plus-24.svg */ "./style/icons/file-plus-24.svg");
/* harmony import */ var _style_icons_monitor_24_svg__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../style/icons/monitor-24.svg */ "./style/icons/monitor-24.svg");
/* harmony import */ var _style_icons_api_24_svg__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../style/icons/api-24.svg */ "./style/icons/api-24.svg");
/* harmony import */ var _style_icons_pipeline_brand_24_svg__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../style/icons/pipeline-brand-24.svg */ "./style/icons/pipeline-brand-24.svg");
/* harmony import */ var _style_icons_pipeline_brand_16_svg__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../style/icons/pipeline-brand-16.svg */ "./style/icons/pipeline-brand-16.svg");
/* harmony import */ var _style_icons_node_24_svg__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../style/icons/node-24.svg */ "./style/icons/node-24.svg");
/* harmony import */ var _style_icons_align_svg__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../style/icons/align.svg */ "./style/icons/align.svg");
/* harmony import */ var _style_icons_export_svg_svg__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../style/icons/export-svg.svg */ "./style/icons/export-svg.svg");










const fileTextIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:file-text-icon',
    svgstr: _style_icons_file_text_24_svg__WEBPACK_IMPORTED_MODULE_1__
});
const filePlusIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:file-plus-icon',
    svgstr: _style_icons_file_plus_24_svg__WEBPACK_IMPORTED_MODULE_2__
});
const monitorIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:monitor-icon',
    svgstr: _style_icons_monitor_24_svg__WEBPACK_IMPORTED_MODULE_3__
});
const apiIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:api-icon',
    svgstr: _style_icons_api_24_svg__WEBPACK_IMPORTED_MODULE_4__
});
const pipelineIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:pipeline-icon',
    svgstr: _style_icons_pipeline_brand_16_svg__WEBPACK_IMPORTED_MODULE_5__
});
const componentIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:component-icon',
    svgstr: _style_icons_node_24_svg__WEBPACK_IMPORTED_MODULE_6__
});
const pipelineBrandIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:pipelinenegative-icon',
    svgstr: _style_icons_pipeline_brand_16_svg__WEBPACK_IMPORTED_MODULE_5__
});
const pipelineCategoryIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:pipelineCategory-icon',
    svgstr: _style_icons_pipeline_brand_24_svg__WEBPACK_IMPORTED_MODULE_7__
});
const alignIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:align-icon',
    svgstr: _style_icons_align_svg__WEBPACK_IMPORTED_MODULE_8__
});
const exportIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'amphi:export-svg-icon',
    svgstr: _style_icons_export_svg_svg__WEBPACK_IMPORTED_MODULE_9__
});


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IPipelineTracker: () => (/* binding */ IPipelineTracker),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_9___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_9__);
/* harmony import */ var _version__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./version */ "./lib/version.js");
/* harmony import */ var _AboutDialog__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./AboutDialog */ "./lib/AboutDialog.js");
/* harmony import */ var _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @amphi/pipeline-components-manager */ "webpack/sharing/consume/default/@amphi/pipeline-components-manager");
/* harmony import */ var _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10___default = /*#__PURE__*/__webpack_require__.n(_amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__);
/* harmony import */ var _icons__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./icons */ "./lib/icons.js");
/* harmony import */ var _PipelineEditorWidget__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./PipelineEditorWidget */ "./lib/PipelineEditorWidget.js");
















/**
 * The command IDs used by the Amphi pipeline editor plugin.
 */
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.create = 'pipeline-editor:create-new';
    CommandIDs.restartPipelineKernel = 'pipeline-editor:restart-kernel';
    CommandIDs.runPipeline = 'pipeline-editor:run-pipeline';
    CommandIDs.runPipelineUntil = 'pipeline-editor:run-pipeline-until';
})(CommandIDs || (CommandIDs = {}));
const PIPELINE_FACTORY = 'Pipeline Editor';
const PIPELINE = 'amphi-pipeline';
const PIPELINE_EDITOR_NAMESPACE = 'amphi-pipeline-editor';
const EXTENSION_ID = '@amphi/pipeline-editor:extension';
const EXTENSION_TRACKER = 'pipeline-editor-tracker';
// Export a token so other extensions can require it
const IPipelineTracker = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_8__.Token(EXTENSION_TRACKER);
/**
 * Initialization data for the Pipeline Editor (DocumentWidget) extension.
 */
const pipelineEditor = {
    id: EXTENSION_ID,
    autoStart: true,
    requires: [
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette,
        _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_6__.IRenderMimeRegistry,
        _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_4__.ILauncher,
        _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_5__.IFileBrowserFactory,
        _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_5__.IDefaultFileBrowser,
        _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7__.IStatusBar,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer,
        _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__.IMainMenu,
        _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__.ISettingRegistry,
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.IToolbarWidgetRegistry,
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ISessionContextDialogs,
        _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_9__.IDocumentManager,
        _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__.ComponentManager
    ],
    provides: IPipelineTracker,
    activate: (app, palette, rendermime, launcher, browserFactory, defaultFileBrowser, statusBar, restorer, menu, settings, toolbarRegistry, sessionDialogs, manager, componentService) => {
        console.log("Amphi Pipeline Extension activation...");
        // Get app commands and define create-pipeline command
        const { commands } = app;
        const command = CommandIDs.create;
        // Pipeline Tracker
        const pipelineEditortracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.WidgetTracker({
            namespace: PIPELINE_EDITOR_NAMESPACE
        });
        let enableExecution;
        // Fetch the initial state of the settings.
        function loadSetting(setting) {
            // Read the settings and convert to the correct type
            enableExecution = setting.get('enableExecution').composite;
            console.log(`Settings extension: enableExecution is set to '${enableExecution}'`);
        }
        Promise.all([app.restored, settings.load(EXTENSION_ID)])
            .then(([, settings]) => {
            // Read the settings
            loadSetting(settings);
            // Listen for your plugin setting changes using Signal
            settings.changed.connect(loadSetting);
            // Set up new widget Factory for .ampln files
            const pipelineEditorFactory = new _PipelineEditorWidget__WEBPACK_IMPORTED_MODULE_11__.PipelineEditorFactory({
                name: PIPELINE_FACTORY,
                fileTypes: [PIPELINE],
                defaultFor: [PIPELINE],
                canStartKernel: true,
                preferKernel: true,
                shutdownOnClose: true,
                shell: app.shell,
                toolbarRegistry: toolbarRegistry,
                commands: app.commands,
                browserFactory: browserFactory,
                defaultFileBrowser: defaultFileBrowser,
                serviceManager: app.serviceManager,
                settings: settings,
                componentService: componentService
            });
            // Add the widget to the tracker when it's created
            pipelineEditorFactory.widgetCreated.connect((sender, widget) => {
                pipelineEditortracker.add(widget);
                // Notify the widget tracker if restore data needs to update
                widget.context.pathChanged.connect(() => {
                    pipelineEditortracker.save(widget);
                });
            });
            // Add the default behavior of opening the widget for .ampln files
            // First the Pipeline and then JSON (available)
            app.docRegistry.addFileType({
                name: 'amphi-pipeline',
                displayName: 'pipeline',
                extensions: ['.ampln'],
                icon: _icons__WEBPACK_IMPORTED_MODULE_12__.pipelineBrandIcon,
                fileFormat: 'text'
            }, [PIPELINE_FACTORY, 'JSON']);
            app.docRegistry.addWidgetFactory(pipelineEditorFactory);
            app.docRegistry.addFileType({
                name: 'amphi-component',
                displayName: 'component',
                extensions: ['.amcpn'],
                icon: _icons__WEBPACK_IMPORTED_MODULE_12__.componentIcon,
                fileFormat: 'text'
            }, ['JSON']);
            // Add command to create new Pipeline
            commands.addCommand(command, {
                label: args => args['isPalette'] || args['isContextMenu']
                    ? 'New Pipeline'
                    : 'New Pipeline',
                caption: 'Create a new pipeline',
                icon: (args) => (args['isPalette'] ? null : _icons__WEBPACK_IMPORTED_MODULE_12__.pipelineCategoryIcon),
                execute: async (args) => {
                    return commands.execute(_PipelineEditorWidget__WEBPACK_IMPORTED_MODULE_11__.commandIDs.newDocManager, {
                        type: 'file',
                        path: defaultFileBrowser.model.path,
                        ext: '.ampln'
                    })
                        .then(async (model) => {
                        const runtime_type = 'LOCAL';
                        const getPipelineId = () => `pipeline_${+new Date()}`;
                        const pipelineJson = {
                            doc_type: 'Amphi Pipeline',
                            version: '1',
                            json_schema: 'http://docs.amphi.ai/schemas/pipeline-v1-schema.json',
                            id: getPipelineId(),
                            pipelines: [
                                {
                                    id: 'primary',
                                    flow: {
                                        nodes: [],
                                        edges: [],
                                        viewport: {
                                            x: 0,
                                            y: 0,
                                            zoom: 1
                                        }
                                    },
                                    app_data: {
                                        ui_data: {
                                            comments: []
                                        },
                                        version: 1,
                                        runtime_type
                                    },
                                    runtime_ref: 'python'
                                }
                            ]
                        };
                        // Open Pipeline using Pipeline EditorFactory
                        const newWidget = await app.commands.execute(_PipelineEditorWidget__WEBPACK_IMPORTED_MODULE_11__.commandIDs.openDocManager, {
                            path: model.path,
                            factory: PIPELINE_FACTORY // Use PipelineEditorFactory
                        });
                        // Assign to the new widget context the pipeline JSON from above
                        newWidget.context.ready.then(() => {
                            newWidget.context.model.fromJSON(pipelineJson);
                            // Save this in the file
                            app.commands.execute(_PipelineEditorWidget__WEBPACK_IMPORTED_MODULE_11__.commandIDs.saveDocManager, {
                                path: model.path
                            });
                        });
                    });
                }
            });
            // Get the current widget and activate unless the args specify otherwise.
            function getCurrent(args) {
                const widget = pipelineEditortracker.currentWidget;
                const activate = args['activate'] !== false;
                if (activate && widget) {
                    app.shell.activateById(widget.id);
                }
                return widget !== null && widget !== void 0 ? widget : null;
            }
            function isEnabled() {
                return (pipelineEditortracker.currentWidget !== null &&
                    pipelineEditortracker.currentWidget === app.shell.currentWidget);
            }
            /**
             * Restart the Pipeline Kernel linked to the current Editor
             */
            commands.addCommand(CommandIDs.restartPipelineKernel, {
                label: 'Restart Runtime…',
                execute: async (args) => {
                    const current = getCurrent({ activate: false, ...args });
                    if (!current) {
                        return;
                    }
                    console.log(current.context.sessionContext);
                    try {
                        await current.context.sessionContext.restartKernel();
                    }
                    catch (error) {
                        console.error("Failed to restart runtime: ", error);
                    }
                },
                isEnabled
            });
            /**
             * Run Pipeline on Kernel linked to the current Editor
             */
            commands.addCommand(CommandIDs.runPipeline, {
                label: 'Run Pipeline',
                execute: args => {
                    // Delete Python variables for the metadata panel (reinitialization)
                    /*
                    const command = 'pipeline-metadata-panel:delete-all';
                    commands.execute(command, {}).catch(reason => {
                      console.error(
                        `An error occurred during the execution of ${command}.\n${reason}`
                      );
                    });
                    */
                    // First open log console
                    // Open in same panel as metadata panel is openned
                    if (args.datapanel) {
                        const command = 'metadatapanel:open';
                        commands.execute(command, {}).catch(reason => {
                            console.error(`An error occurred during the execution of ${command}.\n${reason}`);
                        });
                    }
                    else {
                        commands.execute('pipeline-console:open', {}).catch(reason => {
                            console.error(`An error occurred during the execution of ${command}.\n${reason}`);
                        });
                    }
                    const current = getCurrent(args);
                    if (!current) {
                        return;
                    }
                    if (!current.context.sessionContext.session) {
                        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.error('The pipeline cannot be run because the local Python engine cannot be found.', {
                            actions: [
                                { label: 'Try to reload the application and run again.', callback: () => location.reload() }
                            ],
                            autoClose: 6000
                        });
                        return;
                    }
                    if (current.context.sessionContext.hasNoKernel) {
                        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.error('The pipeline cannot be run because no processing engine can be found.', {
                            actions: [
                                { label: 'Try to reload the application and run again.', callback: () => location.reload() }
                            ],
                            autoClose: 6000
                        });
                        return;
                    }
                    if (!current.context.sessionContext) {
                        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.error('The pipeline cannot be run because the local Python engine cannot be found.', {
                            actions: [
                                { label: 'Try to reload the application and run again.', callback: () => location.reload() }
                            ],
                            autoClose: 6000
                        });
                        return;
                    }
                    // Second, install dependencies packages if needed
                    current.context.sessionContext.ready.then(async () => {
                        const code = args.code.toString();
                        let packages;
                        const imports = _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__.PipelineService.extractPythonImportPackages(code);
                        packages = _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__.PipelineService.extractPackageNames(imports);
                        const lines = code.split(/\r?\n/); // Split the code into lines
                        const dependencyLine = lines[2]; // Extract dependencies from the third line (index 2, as arrays are zero-indexed)
                        const dependencies = dependencyLine.startsWith("# Additional dependencies: ") // Assuming the structure is "# Additional imports: package1, package2, ..."
                            ? dependencyLine.split(': ')[1].split(',').map(pkg => pkg.trim())
                            : [];
                        packages = [...packages, ...dependencies];
                        if (packages.length > 0 && packages[0] != null && packages[0] !== '') {
                            const pips_code = _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__.PipelineService.getInstallCommandsFromPackageNames(packages).join('\n');
                            console.log("pips_code: " + pips_code);
                            // Install packages
                            try {
                                const future = current.context.sessionContext.session.kernel.requestExecute({ code: pips_code });
                                future.onIOPub = msg => {
                                    if (msg.header.msg_type === 'stream') {
                                        // Handle stream messages if necessary
                                    }
                                    else if (msg.header.msg_type === 'error') {
                                        // Handle error messages
                                        const errorMsg = msg;
                                        const errorOutput = errorMsg.content;
                                        console.error(`Received error: ${errorOutput.ename}: ${errorOutput.evalue}`);
                                    }
                                };
                                future.onDone = () => {
                                    console.log("Dependencies installed.");
                                };
                                await future.done;
                            }
                            catch (error) {
                                console.error(error);
                            }
                        }
                    });
                    // Third, run pipeline code
                    current.context.sessionContext.ready.then(async () => {
                        try {
                            // Create promise to track success or failure of the request
                            const delegate = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_8__.PromiseDelegate();
                            const start = performance.now();
                            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.promise(delegate.promise, {
                                // Message when the task is pending
                                pending: { message: 'Running...', options: { autoClose: false } },
                                // Message when the task finished successfully
                                success: {
                                    message: (result) => `Pipeline execution successful after ${result.delayInSeconds} seconds.`,
                                    options: {
                                        autoClose: 3000
                                    }
                                },
                                // Message when the task finished with errors
                                error: {
                                    message: () => 'Pipeline execution failed. Check error messages in the Log Console.',
                                    options: {
                                        actions: [
                                            {
                                                label: 'Log Console',
                                                callback: () => {
                                                    const command = 'pipeline-console:open';
                                                    commands.execute(command, {}).catch(reason => {
                                                        console.error(`An error occurred during the execution of ${command}.\n${reason}`);
                                                    });
                                                }
                                            }
                                        ],
                                        autoClose: 5000
                                    }
                                }
                            });
                            const pythonCodeWithSleep = `
import time
time.sleep(0.25)
${args.code}
`;
                            const future = current.context.sessionContext.session.kernel.requestExecute({ code: pythonCodeWithSleep });
                            console.log("future %o", future);
                            future.onReply = reply => {
                                const end = performance.now();
                                const delay = end - start;
                                const delayInSeconds = (delay / 1000).toFixed(1);
                                if (reply.content.status === "ok") {
                                    delegate.resolve({ delayInSeconds });
                                }
                                else {
                                    delegate.reject({ delayInSeconds });
                                }
                            };
                            future.onIOPub = msg => {
                                if (msg.header.msg_type === 'stream') {
                                    // Handle stream messages if necessary
                                }
                                else if (msg.header.msg_type === 'error') {
                                    // Handle error messages
                                    const errorMsg = msg;
                                    const errorOutput = errorMsg.content;
                                    console.error(`Received error: ${errorOutput.ename}: ${errorOutput.evalue}`);
                                }
                            };
                            future.onDone = () => {
                                const end = performance.now();
                                const delay = end - start;
                                const delayInSeconds = (delay / 1000).toFixed(1);
                                delegate.resolve({ delayInSeconds });
                            };
                            await future.done;
                        }
                        catch (error) {
                            console.error(error);
                        }
                    });
                },
                isEnabled
            });
            commands.addCommand('pipeline-editor:run-pipeline-until', {
                label: 'Run pipeline until ...',
                execute: async (args) => {
                    const current = getCurrent(args);
                    if (!current) {
                        return;
                    }
                    const nodeId = args.nodeId.toString();
                    const context = args.context;
                    const code = _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__.CodeGenerator.generateCodeUntil(current.context.model.toString(), commands, componentService, nodeId, context);
                    commands.execute('pipeline-editor:run-pipeline', { code }).catch(reason => {
                        console.error(`An error occurred during the execution of 'pipeline-editor:run-pipeline'.\n${reason}`);
                    });
                }
            });
            commands.addCommand('pipeline-editor:version', {
                label: 'About Amphi',
                execute: () => {
                    const { title, body } = (0,_AboutDialog__WEBPACK_IMPORTED_MODULE_13__.createAboutDialog)(_version__WEBPACK_IMPORTED_MODULE_14__.LIB_VERSION);
                    return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                        title,
                        body,
                        buttons: [
                            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.createButton({
                                label: 'Close',
                                className: 'jp-About-button jp-mod-reject jp-mod-styled',
                            }),
                        ],
                    });
                },
            });
            // Add the command to the context menu
            app.contextMenu.addItem({
                command: CommandIDs.create,
                selector: '.jp-DirListing-content',
                rank: 100,
            });
            // Add to palette
            palette.addItem({
                command: CommandIDs.create,
                category: 'Pipeline',
                args: { isPalette: true }
            });
            palette.addItem({
                command: 'pipeline-editor:version',
                category: 'Help',
                args: { isPalette: true }
            });
            // Components //
            // ----
            // ----
            // Copy Paste
            //const { cut, copy, paste, bufferedNodes } = useCopyPaste();
            // const canCopy = nodes.some(({ selected }) => selected);
            // const canPaste = bufferedNodes.length > 0;
            commands.addCommand('pipeline-editor-component:save-as-file', {
                execute: async (args) => {
                    const current = getCurrent(args);
                    if (!current) {
                        return;
                    }
                    const contextNode = app.contextMenuHitTest(node => !!node.dataset.id);
                    if (contextNode) {
                        const nodeId = contextNode.dataset.id; // Extract the node ID
                        // Assuming PipelineService.getNodeById is available
                        const nodeJson = _amphi_pipeline_components_manager__WEBPACK_IMPORTED_MODULE_10__.PipelineService.getNodeById(current.context.model.toString(), nodeId);
                        // Extract data and type attributes
                        const { data, type } = nodeJson;
                        const { lastUpdated, lastExecuted, ...filteredData } = data;
                        const componentJson = JSON.stringify({ component: { data: filteredData, type } });
                        const file = await commands.execute('docmanager:new-untitled', { path: '/', type: 'file', ext: '.amcpn' });
                        const doc = await commands.execute('docmanager:open', { path: file.path });
                        // Ensure the document context model is loaded
                        await doc.context.ready;
                        // Save componentJson string to the file
                        doc.context.model.fromString(componentJson);
                        await doc.context.save();
                        await commands.execute('docmanager:reload', { path: file.path });
                        await commands.execute('docmanager:rename');
                        // await commands.execute('docmanager:save', { path: file.path });
                    }
                },
                label: 'Save as file'
            });
            commands.addCommand('pipeline-editor-component:copy', {
                execute: async (args) => {
                    const contextNode = app.contextMenuHitTest(node => !!node.dataset.id);
                    if (contextNode) {
                        const nodeId = contextNode.getAttribute('data-id');
                        console.log(nodeId);
                    }
                },
                label: 'Copy'
            });
            commands.addCommand('pipeline-editor-component:cut', {
                execute: args => {
                    const contextNode = app.contextMenuHitTest(node => !!node.dataset.id);
                    if (contextNode) {
                        console.log(contextNode);
                    }
                },
                label: 'Cut'
            });
            commands.addCommand('pipeline-editor-component:paste', {
                execute: async (args) => {
                },
                label: 'Paste'
            });
            const contextMenuItems = [
                /*
                {
                  command: 'pipeline-editor-component:copy',
                  selector: '.component',
                  rank: 1,
                },
                {
                  command: 'pipeline-editor-component:cut',
                  selector: '.component',
                  rank: 2,
                },
                {
                  command: 'pipeline-editor-component:paste',
                  selector: '.component',
                  rank: 3,
                },
                */
                {
                    command: 'pipeline-editor-component:save-as-file',
                    selector: '.component',
                    rank: 3,
                },
            ];
            // Add each context menu item with the args function
            contextMenuItems.forEach(item => {
                app.contextMenu.addItem({
                    command: item.command,
                    selector: item.selector,
                    rank: item.rank
                });
            });
            // ----
            // ----
            // Add launcher
            if (launcher) {
                launcher.add({
                    command: CommandIDs.create,
                    category: 'Amphi',
                    rank: 3
                });
            }
        })
            .catch(reason => {
            console.error(`Something went wrong when reading the settings.\n${reason}`);
        });
        // Handle state restoration.
        if (restorer) {
            // When restoring the app, if the document was open, reopen it
            restorer.restore(pipelineEditortracker, {
                command: 'docmanager:open',
                args: widget => ({ path: widget.context.path, factory: PIPELINE_FACTORY }),
                name: widget => widget.context.path
            });
        }
        return pipelineEditortracker;
    },
};
/**
 * Export the plugins as default.
 */
const extensions = [
    pipelineEditor
];
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extensions);


/***/ }),

/***/ "./lib/version.js":
/*!************************!*\
  !*** ./lib/version.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   LIB_VERSION: () => (/* binding */ LIB_VERSION)
/* harmony export */ });
const LIB_VERSION = "0.5.91";


/***/ }),

/***/ "./style/icons/align.svg":
/*!*******************************!*\
  !*** ./style/icons/align.svg ***!
  \*******************************/
/***/ ((module) => {

module.exports = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->\n\n<svg\n   width=\"800px\"\n   height=\"800px\"\n   viewBox=\"0 0 24 24\"\n   fill=\"none\"\n   version=\"1.1\"\n   id=\"svg1\"\n   sodipodi:docname=\"align.svg\"\n   inkscape:version=\"1.3 (0e150ed, 2023-07-21)\"\n   xmlns:inkscape=\"http://www.inkscape.org/namespaces/inkscape\"\n   xmlns:sodipodi=\"http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd\"\n   xmlns=\"http://www.w3.org/2000/svg\"\n   xmlns:svg=\"http://www.w3.org/2000/svg\">\n  <defs\n     id=\"defs1\" />\n  <sodipodi:namedview\n     id=\"namedview1\"\n     pagecolor=\"#505050\"\n     bordercolor=\"#eeeeee\"\n     borderopacity=\"1\"\n     inkscape:showpageshadow=\"0\"\n     inkscape:pageopacity=\"0\"\n     inkscape:pagecheckerboard=\"0\"\n     inkscape:deskcolor=\"#505050\"\n     inkscape:zoom=\"0.295\"\n     inkscape:cx=\"400\"\n     inkscape:cy=\"401.69492\"\n     inkscape:window-width=\"1504\"\n     inkscape:window-height=\"780\"\n     inkscape:window-x=\"2301\"\n     inkscape:window-y=\"549\"\n     inkscape:window-maximized=\"0\"\n     inkscape:current-layer=\"svg1\" />\n  <path\n     d=\"M 22.81921,12 H 1.3615819 M 16.262712,6.0395476 v 0 c -0.329136,0 -0.596045,0.2668614 -0.596045,0.5960451 V 17.364407 c 0,0.329137 0.266909,0.596046 0.596045,0.596046 v 0 c 0.329137,0 0.596046,-0.266909 0.596046,-0.596046 V 6.6355928 c 0,-0.3291838 -0.266909,-0.5960452 -0.596046,-0.5960452 z M 7.918079,2.4632765 v 0 c -0.3291838,0 -0.5960452,0.2668613 -0.5960452,0.5960452 V 20.940679 c 0,0.329136 0.2668614,0.596045 0.5960452,0.596045 v 0 c 0.3291839,0 0.5960452,-0.266909 0.5960452,-0.596045 V 3.0593217 c 0,-0.3291839 -0.2668613,-0.5960452 -0.5960452,-0.5960452 z\"\n     stroke=\"#000000\"\n     stroke-width=\"2.38418\"\n     stroke-linecap=\"round\"\n     stroke-linejoin=\"round\"\n     id=\"path1\" />\n</svg>\n";

/***/ }),

/***/ "./style/icons/api-24.svg":
/*!********************************!*\
  !*** ./style/icons/api-24.svg ***!
  \********************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 24 24\"><path fill=\"currentColor\" fill-rule=\"evenodd\" d=\"M2 5a3 3 0 115.585 1.524l1.79 1.79.68-.68a2.75 2.75 0 013.89 0l.68.68 1.79-1.79a3 3 0 111.06 1.06l-1.79 1.791.681.68a2.75 2.75 0 010 3.89l-.68.68 1.79 1.79a3 3 0 11-1.06 1.06l-1.791-1.79-.68.681a2.75 2.75 0 01-3.89 0l-.68-.68-1.79 1.79a3 3 0 11-1.06-1.06l1.79-1.791-.681-.68a2.75 2.75 0 010-3.89l.68-.68-1.79-1.79A3 3 0 012 5zm3-1.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zm0 14a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM17.5 19a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0zM19 3.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zm-7.884 5.195a1.25 1.25 0 011.768 0l2.421 2.421a1.25 1.25 0 010 1.768l-2.421 2.421a1.25 1.25 0 01-1.768 0l-2.421-2.421a1.25 1.25 0 010-1.768l2.421-2.421z\" clip-rule=\"evenodd\"/></svg>";

/***/ }),

/***/ "./style/icons/export-svg.svg":
/*!************************************!*\
  !*** ./style/icons/export-svg.svg ***!
  \************************************/
/***/ ((module) => {

module.exports = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->\n\n<svg\n   fill=\"#000000\"\n   width=\"800px\"\n   height=\"800px\"\n   viewBox=\"0 0 24 24\"\n   id=\"export-2\"\n   data-name=\"Flat Line\"\n   class=\"icon flat-line\"\n   version=\"1.1\"\n   sodipodi:docname=\"export-svg.svg\"\n   inkscape:version=\"1.3 (0e150ed, 2023-07-21)\"\n   xmlns:inkscape=\"http://www.inkscape.org/namespaces/inkscape\"\n   xmlns:sodipodi=\"http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd\"\n   xmlns=\"http://www.w3.org/2000/svg\"\n   xmlns:svg=\"http://www.w3.org/2000/svg\">\n  <defs\n     id=\"defs1\" />\n  <sodipodi:namedview\n     id=\"namedview1\"\n     pagecolor=\"#505050\"\n     bordercolor=\"#eeeeee\"\n     borderopacity=\"1\"\n     inkscape:showpageshadow=\"0\"\n     inkscape:pageopacity=\"0\"\n     inkscape:pagecheckerboard=\"0\"\n     inkscape:deskcolor=\"#505050\"\n     inkscape:zoom=\"0.295\"\n     inkscape:cx=\"400\"\n     inkscape:cy=\"400\"\n     inkscape:window-width=\"2560\"\n     inkscape:window-height=\"1343\"\n     inkscape:window-x=\"1512\"\n     inkscape:window-y=\"149\"\n     inkscape:window-maximized=\"1\"\n     inkscape:current-layer=\"export-2\" />\n  <g\n     id=\"g1\"\n     transform=\"matrix(1.1983051,0,0,1.1983051,-2.3288136,-2.3288136)\">\n    <polyline\n       id=\"primary\"\n       points=\"15 3 21 3 21 9\"\n       style=\"fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round\" />\n    <line\n       id=\"primary-2\"\n       data-name=\"primary\"\n       x1=\"11\"\n       y1=\"13\"\n       x2=\"21\"\n       y2=\"3\"\n       style=\"fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round\" />\n    <path\n       id=\"primary-3\"\n       data-name=\"primary\"\n       d=\"m 21,13 v 7 a 1,1 0 0 1 -1,1 H 4 A 1,1 0 0 1 3,20 V 4 A 1,1 0 0 1 4,3 h 7\"\n       style=\"fill:none;stroke:#000000;stroke-width:2;stroke-linecap:round;stroke-linejoin:round\" />\n  </g>\n</svg>\n";

/***/ }),

/***/ "./style/icons/file-plus-24.svg":
/*!**************************************!*\
  !*** ./style/icons/file-plus-24.svg ***!
  \**************************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 24 24\"><g fill=\"currentColor\"><path d=\"M11.75 10.75a.75.75 0 01.75.75V14H15a.75.75 0 010 1.5h-2.5V18a.75.75 0 01-1.5 0v-2.5H8.5a.75.75 0 010-1.5H11v-2.5a.75.75 0 01.75-.75z\"/><path fill-rule=\"evenodd\" d=\"M5.75 1A2.75 2.75 0 003 3.75v16.5A2.75 2.75 0 005.75 23h12.5A2.75 2.75 0 0021 20.25V8.664c0-.464-.184-.909-.513-1.237l-5.914-5.914A1.75 1.75 0 0013.336 1H5.75zM4.5 3.75c0-.69.56-1.25 1.25-1.25H13v5.75c0 .414.336.75.75.75h5.75v11.25c0 .69-.56 1.25-1.25 1.25H5.75c-.69 0-1.25-.56-1.25-1.25V3.75zM18.44 7.5L14.5 3.56V7.5h3.94z\" clip-rule=\"evenodd\"/></g></svg>";

/***/ }),

/***/ "./style/icons/file-text-24.svg":
/*!**************************************!*\
  !*** ./style/icons/file-text-24.svg ***!
  \**************************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 24 24\"><g fill=\"currentColor\"><path d=\"M7.75 12a.75.75 0 000 1.5h8a.75.75 0 000-1.5h-8zM7 16.75a.75.75 0 01.75-.75h6a.75.75 0 010 1.5h-6a.75.75 0 01-.75-.75zM7.75 8a.75.75 0 000 1.5h2a.75.75 0 000-1.5h-2z\"/><path fill-rule=\"evenodd\" d=\"M3 3.75A2.75 2.75 0 015.75 1h7.586c.464 0 .909.184 1.237.513l5.914 5.914c.329.328.513.773.513 1.237V20.25A2.75 2.75 0 0118.25 23H5.75A2.75 2.75 0 013 20.25V3.75zM5.75 2.5c-.69 0-1.25.56-1.25 1.25v16.5c0 .69.56 1.25 1.25 1.25h12.5c.69 0 1.25-.56 1.25-1.25V9h-5.75a.75.75 0 01-.75-.75V2.5H5.75zm8.75 1.06l3.94 3.94H14.5V3.56z\" clip-rule=\"evenodd\"/></g></svg>";

/***/ }),

/***/ "./style/icons/monitor-24.svg":
/*!************************************!*\
  !*** ./style/icons/monitor-24.svg ***!
  \************************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 24 24\"><path fill=\"currentColor\" fill-rule=\"evenodd\" d=\"M1 4.75A2.75 2.75 0 013.75 2h16.5A2.75 2.75 0 0123 4.75v10.5A2.75 2.75 0 0120.25 18H12.5v2.5H16a.75.75 0 010 1.5H8a.75.75 0 010-1.5h3V18H3.75A2.75 2.75 0 011 15.25V4.75zM20.25 16.5c.69 0 1.25-.56 1.25-1.25V4.75c0-.69-.56-1.25-1.25-1.25H3.75c-.69 0-1.25.56-1.25 1.25v10.5c0 .69.56 1.25 1.25 1.25h16.5z\" clip-rule=\"evenodd\"/></svg>";

/***/ }),

/***/ "./style/icons/node-24.svg":
/*!*********************************!*\
  !*** ./style/icons/node-24.svg ***!
  \*********************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" fill=\"none\" viewBox=\"0 0 24 24\"><path fill=\"currentColor\" fill-rule=\"evenodd\" d=\"M7 9.25A2.75 2.75 0 019.75 6.5h5a2.75 2.75 0 012.75 2.75V11h4.75a.75.75 0 010 1.5H17.5v1.75A2.75 2.75 0 0114.75 17h-5A2.75 2.75 0 017 14.25V12.5H2.25a.75.75 0 010-1.5H7V9.25zm9 0C16 8.56 15.44 8 14.75 8h-5c-.69 0-1.25.56-1.25 1.25v5c0 .69.56 1.25 1.25 1.25h5c.69 0 1.25-.56 1.25-1.25v-5z\" clip-rule=\"evenodd\"/></svg>";

/***/ }),

/***/ "./style/icons/pipeline-brand-16.svg":
/*!*******************************************!*\
  !*** ./style/icons/pipeline-brand-16.svg ***!
  \*******************************************/
/***/ ((module) => {

module.exports = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<svg\n   width=\"16\"\n   height=\"16\"\n   fill=\"none\"\n   viewBox=\"0 0 16 16\"\n   version=\"1.1\"\n   id=\"svg1\"\n   sodipodi:docname=\"pipeline-brand-16.svg\"\n   inkscape:version=\"1.3 (0e150ed, 2023-07-21)\"\n   xmlns:inkscape=\"http://www.inkscape.org/namespaces/inkscape\"\n   xmlns:sodipodi=\"http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd\"\n   xmlns=\"http://www.w3.org/2000/svg\"\n   xmlns:svg=\"http://www.w3.org/2000/svg\">\n  <defs\n     id=\"defs1\" />\n  <sodipodi:namedview\n     id=\"namedview1\"\n     pagecolor=\"#505050\"\n     bordercolor=\"#eeeeee\"\n     borderopacity=\"1\"\n     inkscape:showpageshadow=\"0\"\n     inkscape:pageopacity=\"0\"\n     inkscape:pagecheckerboard=\"0\"\n     inkscape:deskcolor=\"#505050\"\n     inkscape:zoom=\"14.75\"\n     inkscape:cx=\"8\"\n     inkscape:cy=\"7.9661017\"\n     inkscape:window-width=\"1512\"\n     inkscape:window-height=\"874\"\n     inkscape:window-x=\"0\"\n     inkscape:window-y=\"32\"\n     inkscape:window-maximized=\"1\"\n     inkscape:current-layer=\"svg1\" />\n  <path\n     fill=\"currentColor\"\n     fill-rule=\"evenodd\"\n     d=\"M2.75 2.5A1.75 1.75 0 001 4.25v1C1 6.216 1.784 7 2.75 7h1a1.75 1.75 0 001.732-1.5H6.5a.75.75 0 01.75.75v3.5A2.25 2.25 0 009.5 12h1.018c.121.848.85 1.5 1.732 1.5h1A1.75 1.75 0 0015 11.75v-1A1.75 1.75 0 0013.25 9h-1a1.75 1.75 0 00-1.732 1.5H9.5a.75.75 0 01-.75-.75v-3.5A2.25 2.25 0 006.5 4H5.482A1.75 1.75 0 003.75 2.5h-1zM2.5 4.25A.25.25 0 012.75 4h1a.25.25 0 01.25.25v1a.25.25 0 01-.25.25h-1a.25.25 0 01-.25-.25v-1zm9.75 6.25a.25.25 0 00-.25.25v1c0 .138.112.25.25.25h1a.25.25 0 00.25-.25v-1a.25.25 0 00-.25-.25h-1z\"\n     clip-rule=\"evenodd\"\n     id=\"path1\"\n     style=\"fill:#5a8f7b;fill-opacity:1\" />\n</svg>\n";

/***/ }),

/***/ "./style/icons/pipeline-brand-24.svg":
/*!*******************************************!*\
  !*** ./style/icons/pipeline-brand-24.svg ***!
  \*******************************************/
/***/ ((module) => {

module.exports = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<svg\n   width=\"24\"\n   height=\"24\"\n   fill=\"none\"\n   viewBox=\"0 0 24 24\"\n   version=\"1.1\"\n   id=\"svg1\"\n   sodipodi:docname=\"pipeline-brand-24.svg\"\n   inkscape:version=\"1.3 (0e150ed, 2023-07-21)\"\n   xmlns:inkscape=\"http://www.inkscape.org/namespaces/inkscape\"\n   xmlns:sodipodi=\"http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd\"\n   xmlns=\"http://www.w3.org/2000/svg\"\n   xmlns:svg=\"http://www.w3.org/2000/svg\">\n  <defs\n     id=\"defs1\" />\n  <sodipodi:namedview\n     id=\"namedview1\"\n     pagecolor=\"#505050\"\n     bordercolor=\"#eeeeee\"\n     borderopacity=\"1\"\n     inkscape:showpageshadow=\"0\"\n     inkscape:pageopacity=\"0\"\n     inkscape:pagecheckerboard=\"0\"\n     inkscape:deskcolor=\"#505050\"\n     inkscape:zoom=\"9.8333333\"\n     inkscape:cx=\"12\"\n     inkscape:cy=\"11.949153\"\n     inkscape:window-width=\"1512\"\n     inkscape:window-height=\"874\"\n     inkscape:window-x=\"0\"\n     inkscape:window-y=\"32\"\n     inkscape:window-maximized=\"1\"\n     inkscape:current-layer=\"svg1\" />\n  <path\n     fill=\"currentColor\"\n     fill-rule=\"evenodd\"\n     d=\"M4.75 4.5A2.25 2.25 0 002.5 6.75v1A2.25 2.25 0 004.75 10h1a2.25 2.25 0 002.236-2H9.82c.967 0 1.75.784 1.75 1.75v4.5a3.25 3.25 0 003.25 3.25h1.195a2.25 2.25 0 002.236 2h1a2.25 2.25 0 002.25-2.25v-1A2.25 2.25 0 0019.25 14h-1a2.25 2.25 0 00-2.236 2h-1.195a1.75 1.75 0 01-1.75-1.75v-4.5A3.25 3.25 0 009.82 6.5H7.986a2.25 2.25 0 00-2.236-2h-1zM4 6.75A.75.75 0 014.75 6h1a.75.75 0 01.75.75v1a.75.75 0 01-.75.75h-1A.75.75 0 014 7.75v-1zm14.25 8.75a.75.75 0 00-.75.75v1c0 .414.336.75.75.75h1a.75.75 0 00.75-.75v-1a.75.75 0 00-.75-.75h-1z\"\n     clip-rule=\"evenodd\"\n     id=\"path1\"\n     style=\"fill:#5a8f7b;fill-opacity:1\" />\n</svg>\n";

/***/ })

}]);
//# sourceMappingURL=lib_index_js.94db23d119ca7147e3a8.js.map