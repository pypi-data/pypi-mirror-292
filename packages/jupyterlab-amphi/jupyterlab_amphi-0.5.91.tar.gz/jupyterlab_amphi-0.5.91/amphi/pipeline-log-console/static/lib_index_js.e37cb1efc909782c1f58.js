"use strict";
(self["webpackChunk_amphi_pipeline_log_console"] = self["webpackChunk_amphi_pipeline_log_console"] || []).push([["lib_index_js"],{

/***/ "./lib/DataView.js":
/*!*************************!*\
  !*** ./lib/DataView.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! antd */ "../../node_modules/antd/es/table/index.js");


const DataView = ({ htmlData }) => {
    const [dataSource, setDataSource] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const [columns, setColumns] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        const { data, headers } = htmlToJson(htmlData);
        setDataSource(data);
        setColumns(headers.map((header, index) => ({
            title: index === 0 ? '' : header,
            dataIndex: header,
            key: header,
            ...(index === 0 && { rowScope: 'row' }) // Add rowScope for the first column
        })));
    }, [htmlData]);
    return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(antd__WEBPACK_IMPORTED_MODULE_1__["default"], { dataSource: dataSource, columns: columns, pagination: false, size: "small" });
};
function htmlToJson(htmlString) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    // Extract headers from th inside thead, excluding the first one (index)
    let headers = Array.from(doc.querySelectorAll('table thead th')).slice(1).map(th => { var _a, _b; return (_b = (_a = th.textContent) === null || _a === void 0 ? void 0 : _a.trim()) !== null && _b !== void 0 ? _b : ""; });
    const rows = doc.querySelectorAll('table tbody tr');
    const data = Array.from(rows, row => {
        var _a, _b;
        const cells = row.querySelectorAll('th, td');
        const rowObj = {};
        // Capture the index from the first cell
        rowObj['index'] = (_b = (_a = cells[0].textContent) === null || _a === void 0 ? void 0 : _a.trim()) !== null && _b !== void 0 ? _b : "";
        // Map the rest of the cells to headers
        headers.forEach((header, idx) => {
            var _a, _b, _c;
            rowObj[header] = (_c = (_b = (_a = cells[idx + 1]) === null || _a === void 0 ? void 0 : _a.textContent) === null || _b === void 0 ? void 0 : _b.trim()) !== null && _c !== void 0 ? _c : "";
        });
        return rowObj;
    });
    return { data, headers: ['index', ...headers] }; // Set the first header to empty string
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DataView);


/***/ }),

/***/ "./lib/DocumentView.js":
/*!*****************************!*\
  !*** ./lib/DocumentView.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! antd */ "../../node_modules/antd/es/tree/index.js");


const parseHTMLToJSON = (htmlContent) => {
    console.log("htmlContent: %o", htmlContent);
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    const documentElements = doc.querySelectorAll('#documents > div._amphi_document');
    console.log("documentElements: %o", documentElements);
    const documents = [];
    documentElements.forEach((element) => {
        var _a, _b, _c;
        console.log("element: %o", element);
        const nbElement = element.querySelector('div._amphi_nb');
        const pageContentElement = element.querySelector('div._amphi_page_content');
        const metadataElement = element.querySelector('div._amphi_metadata');
        if (nbElement && pageContentElement && metadataElement) {
            const nb = ((_a = nbElement.textContent) === null || _a === void 0 ? void 0 : _a.trim()) || '';
            const pageContent = ((_b = pageContentElement.innerHTML) === null || _b === void 0 ? void 0 : _b.replace('<strong>Document Content:</strong>', '').trim()) || '';
            console.log("pageContent: %o", pageContent);
            let metadataText = ((_c = metadataElement.textContent) === null || _c === void 0 ? void 0 : _c.replace('Metadata:', '').trim()) || '';
            console.log("metadataText: %o", metadataText);
            let metadata;
            try {
                metadataText = metadataText.replace(/'/g, '"'); // Replace single quotes with double quotes
                metadata = JSON.parse(metadataText);
            }
            catch (e) {
                console.error("Error parsing metadata:", e);
                metadata = metadataText; // Fall back to raw text if parsing fails
            }
            documents.push({ nb, page_content: pageContent, metadata: metadata });
        }
    });
    console.log("documents: %o", documents);
    return documents;
};
const createTreeData = (documents) => {
    return documents.map((doc, index) => ({
        title: doc.nb,
        key: `doc-${index}`,
        children: [
            {
                title: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("pre", { style: { userSelect: 'text', cursor: 'text' } }, doc.page_content)),
                key: `doc-${index}-page-content`
            },
            {
                title: 'Metadata',
                key: `doc-${index}-metadata`,
                children: Object.entries(doc.metadata).map(([key, value]) => ({
                    title: `${key}: ${value}`,
                    key: `doc-${index}-metadata-${key}`
                }))
            }
        ]
    }));
};
const DocumentView = ({ htmlData }) => {
    const documents = parseHTMLToJSON(htmlData);
    const treeData = createTreeData(documents);
    console.log("Tree data %o", treeData);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(antd__WEBPACK_IMPORTED_MODULE_1__["default"], { defaultExpandedKeys: treeData.map(node => node.key), defaultSelectedKeys: treeData.map(node => node.key), defaultCheckedKeys: treeData.map(node => node.key), treeData: treeData }));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DocumentView);


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   PipelineConsoleHandler: () => (/* binding */ PipelineConsoleHandler)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);

class AbstractHandler {
    constructor(connector) {
        this._isDisposed = false;
        this._disposed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._rendermime = null;
        this._connector = connector;
    }
    get disposed() {
        return this._disposed;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    get rendermime() {
        return this._rendermime;
    }
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this._isDisposed = true;
        this._disposed.emit();
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal.clearData(this);
    }
}
/**
 * An object that handles code inspection.
 */
class PipelineConsoleHandler extends AbstractHandler {
    constructor(options) {
        var _a;
        super(options.connector);
        this._id = options.id;
        this._rendermime = (_a = options.rendermime) !== null && _a !== void 0 ? _a : null;
        this._ready = this._connector.ready;
        this._connector.kernelRestarted.connect((sender, kernelReady) => {
            const title = {
                contextName: '<b>Restarting kernel...</b> '
            };
            this._ready = this._connector.ready;
        });
    }
    get id() {
        return this._id;
    }
    get ready() {
        return this._ready;
    }
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _amphi_pipeline_editor__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @amphi/pipeline-editor */ "webpack/sharing/consume/default/@amphi/pipeline-editor");
/* harmony import */ var _amphi_pipeline_editor__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_amphi_pipeline_editor__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _kernelconnector__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./kernelconnector */ "./lib/kernelconnector.js");
/* harmony import */ var _logconsole__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./logconsole */ "./lib/logconsole.js");
/* harmony import */ var _manager__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./manager */ "./lib/manager.js");
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./tokens */ "./lib/tokens.js");












var CommandIDs;
(function (CommandIDs) {
    CommandIDs.open = 'pipeline-console:open';
})(CommandIDs || (CommandIDs = {}));
/**
 * A service providing variable introspection.
 */
const logsconsole = {
    id: '@amphi/pipeline-log-console:extension',
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILayoutRestorer, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILabShell, _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__.ISettingRegistry],
    provides: _tokens__WEBPACK_IMPORTED_MODULE_6__.IPipelineConsoleManager,
    autoStart: true,
    activate: (app, palette, restorer, labShell, settings) => {
        const manager = new _manager__WEBPACK_IMPORTED_MODULE_7__.LogConsoleManager();
        const category = 'Pipeline Console';
        const command = CommandIDs.open;
        const label = 'Pipeline Console';
        const namespace = 'pipeline-console';
        const tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.WidgetTracker({ namespace });
        let maxPreview = 80;
        function loadSetting(setting) {
            // Read the settings and convert to the correct type
            maxPreview = setting.get('maxPreview').composite;
            console.log(`Settings Example extension: maxPreview is set to '${maxPreview}'`);
        }
        Promise.all([app.restored, settings.load('@amphi/pipeline-log-console:extension')])
            .then(([, setting]) => {
            // Read the settings
            loadSetting(setting);
            // Listen for your plugin setting changes using Signal
            setting.changed.connect(loadSetting);
            /**
             * Create and track a new inspector.
             */
            function newPanel() {
                const panel = new _logconsole__WEBPACK_IMPORTED_MODULE_8__.PipelineConsolePanel();
                panel.id = 'amphi-logConsole';
                panel.title.label = 'Pipeline Console';
                panel.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.listIcon;
                panel.title.closable = true;
                panel.disposed.connect(() => {
                    if (manager.panel === panel) {
                        manager.panel = null;
                    }
                });
                //Track the inspector panel
                tracker.add(panel);
                return panel;
            }
            // Add command to palette
            app.commands.addCommand(command, {
                label,
                execute: () => {
                    const metadataPanelId = 'amphi-metadataPanel'; // Using the provided log console panel ID
                    let metadataPanel = null;
                    // Iterate over each widget in the 'main' area to find the log console
                    for (const widget of app.shell.widgets('main')) {
                        if (widget.id === metadataPanelId) {
                            metadataPanel = widget;
                            break;
                        }
                    }
                    if (!manager.panel || manager.panel.isDisposed) {
                        manager.panel = newPanel();
                    }
                    // Check if the metadata panel is found and is attached
                    if (metadataPanel && metadataPanel.isAttached) {
                        // If log console panel is open, add the preview panel as a tab next to it
                        if (!manager.panel.isAttached) {
                            app.shell.add(manager.panel, 'main', { ref: metadataPanel.id, mode: 'tab-after' });
                        }
                    }
                    else {
                        // If log console panel is not open, open the preview panel in split-bottom mode
                        if (!manager.panel.isAttached) {
                            app.shell.add(manager.panel, 'main', { mode: 'split-bottom' });
                        }
                    }
                    app.shell.activateById(manager.panel.id);
                }
            });
            palette.addItem({ command, category });
            app.commands.addCommand('pipeline-console:clear', {
                execute: () => {
                    manager.panel.clearLogs();
                },
                label: 'Clear Console'
            });
            app.commands.addCommand('pipeline-console:settings', {
                execute: () => {
                },
                label: 'Console Settings'
            });
            app.contextMenu.addItem({
                command: 'pipeline-console:clear',
                selector: '.amphi-Console',
                rank: 1
            });
        })
            .catch(reason => {
            console.error(`Something went wrong when reading the settings.\n${reason}`);
        });
        // Enable state restoration
        restorer.restore(tracker, {
            command,
            args: () => ({}),
            name: () => 'amphi-logConsole'
        });
        console.log('JupyterLab extension @amphi/pipeline-log-console is activated!');
        return manager;
    }
};
/**
 * An extension that registers pipelines for variable inspection.
 */
const pipelines = {
    id: '@amphi/pipeline-log-console:pipelines',
    requires: [_tokens__WEBPACK_IMPORTED_MODULE_6__.IPipelineConsoleManager, _amphi_pipeline_editor__WEBPACK_IMPORTED_MODULE_5__.IPipelineTracker, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILabShell],
    autoStart: true,
    activate: (app, manager, pipelines, labShell) => {
        const handlers = {};
        function formatLogDate(date) {
            const dateObj = new Date(date);
            return `${dateObj.toLocaleDateString()}\n${dateObj.toLocaleTimeString()}`;
        }
        /**
         * Subscribes to the creation of new pipelines. If a new pipeline is created, build a new handler for the pipelines.
         * Adds a promise for a instanced handler to the 'handlers' collection.
         */
        pipelines.widgetAdded.connect((sender, pipelinePanel) => {
            if (manager.hasHandler(pipelinePanel.context.sessionContext.path)) {
                handlers[pipelinePanel.id] = new Promise((resolve, reject) => {
                    resolve(manager.getHandler(pipelinePanel.context.sessionContext.path));
                });
            }
            else {
                handlers[pipelinePanel.id] = new Promise((resolve, reject) => {
                    const session = pipelinePanel.context.sessionContext;
                    // Create connector and init w script if it exists for kernel type.
                    const connector = new _kernelconnector__WEBPACK_IMPORTED_MODULE_9__.KernelConnector({ session });
                    const options = {
                        connector: connector,
                        id: session.path //Using the sessions path as an identifier for now.
                    };
                    const handler = new _handler__WEBPACK_IMPORTED_MODULE_10__.PipelineConsoleHandler(options);
                    manager.addHandler(handler);
                    pipelinePanel.disposed.connect(() => {
                        delete handlers[pipelinePanel.id];
                        handler.dispose();
                    });
                    handler.ready.then(() => {
                        resolve(handler);
                        connector.ready.then(async () => {
                            session.session.kernel.anyMessage.connect((sender, args) => {
                                if (manager.panel) {
                                    if (args.direction === 'recv') {
                                        // Filter and process kernel messages here
                                        // For example, args.msg.header.msg_type might be 'stream' for log messages
                                        // console.log("MESSAGE %o", args.msg);
                                        if (args.msg.header.msg_type === 'execute_result' || args.msg.header.msg_type === 'display_data') {
                                            // Assert the message type to IExecuteResultMsg or IDisplayDataMsg to access 'data'
                                            const content = args.msg.content;
                                            if (content.data['text/html']) {
                                                manager.panel.onNewLog(formatLogDate(args.msg.header.date), "data", content.data['text/html']);
                                            }
                                        }
                                        else if (args.msg.header.msg_type === 'stream') {
                                            const streamMsg = args.msg;
                                            if (streamMsg.content.text && streamMsg.content.text !== '\n') {
                                                // Wrap the text in a <pre> tag to preserve formatting
                                                const streamText = document.createElement('div');
                                                // manager.panel.onNewLog(formatLogDate(args.msg.header.date), "info", formattedText);
                                                // Use the sanitizer to safely render the traceback
                                                const options = {
                                                    host: streamText,
                                                    source: streamMsg.content.text,
                                                    sanitizer: new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Sanitizer(), // Use the default sanitizer
                                                };
                                                (0,_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__.renderText)(options).then(() => {
                                                    // Once the traceback is sanitized and rendered, append it to the errorContainer
                                                    // Convert the entire structure to HTML string if necessary
                                                    const streamHTML = streamText.outerHTML;
                                                    manager.panel.onNewLog(formatLogDate(args.msg.header.date), "info", streamHTML);
                                                });
                                            }
                                        }
                                        else if (args.msg.header.msg_type === 'error') {
                                            // Handle error messages
                                            const errorMsg = args.msg; // If using TypeScript
                                            const traceback = errorMsg.content.traceback.join('\n');
                                            const errorId = `traceback-${Date.now()}`; // Unique ID for the traceback container
                                            // Create a container for the error message and the link
                                            const errorContainer = document.createElement('div');
                                            const errorMessageText = `${errorMsg.content.evalue}`;
                                            // Ensure the link has a unique ID that matches the pattern for event delegation
                                            // Can do better here, ... TODO
                                            errorContainer.innerHTML = `<pre><span>${errorMessageText}</span><br><a href="#" style="text-decoration: underline; color: grey;" id="link-${errorId}" onClick="document.getElementById('${errorId}').style.display = document.getElementById('${errorId}').style.display === 'none' ? 'block' : 'none'; return false;">Show Traceback</a></pre>`;
                                            // Create a container for the traceback, initially hidden
                                            const tracebackContainer = document.createElement('pre');
                                            tracebackContainer.id = errorId;
                                            tracebackContainer.style.display = 'none';
                                            errorContainer.appendChild(tracebackContainer);
                                            // Use the sanitizer to safely render the traceback
                                            const options = {
                                                host: tracebackContainer,
                                                source: traceback,
                                                sanitizer: new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Sanitizer(), // Use the default sanitizer
                                            };
                                            (0,_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__.renderText)(options).then(() => {
                                                // Once the traceback is sanitized and rendered, append it to the errorContainer
                                                // Convert the entire structure to HTML string if necessary
                                                const errorHTML = errorContainer.outerHTML;
                                                manager.panel.onNewLog(formatLogDate(errorMsg.header.date), "error", errorHTML);
                                            });
                                        }
                                    }
                                }
                            });
                        });
                    });
                });
            }
            setSource(labShell);
        });
        const setSource = (sender, args) => {
            var _a;
            const widget = (_a = args === null || args === void 0 ? void 0 : args.newValue) !== null && _a !== void 0 ? _a : sender.currentWidget;
            if (!widget || !pipelines.has(widget)) {
                return;
            }
            const future = handlers[widget.id];
            future.then((source) => {
                if (source) {
                    manager.source = source;
                    // manager.source.performInspection();
                }
            });
        };
        /**
         * If focus window changes, checks whether new focus widget is a console.
         * In that case, retrieves the handler associated to the console after it has been
         * initialized and updates the manager with it.
         */
        setSource(labShell);
        labShell.currentChanged.connect(setSource);
    }
};
/**
 * Export the plugins as default.
 */
const plugins = [
    logsconsole,
    pipelines
];
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugins);


/***/ }),

/***/ "./lib/kernelconnector.js":
/*!********************************!*\
  !*** ./lib/kernelconnector.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   KernelConnector: () => (/* binding */ KernelConnector)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);

/**
 * Connector class that handles execute request to a kernel
 */
class KernelConnector {
    constructor(options) {
        this._kernelRestarted = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._session = options.session;
        this._session.statusChanged.connect((sender, newStatus) => {
            switch (newStatus) {
                case 'restarting':
                    this._kernelRestarted.emit(this._session.ready);
                    break;
                case 'autorestarting':
                    this._kernelRestarted.emit(this._session.ready);
                    break;
                default:
                    break;
            }
        });
    }
    get kernelRestarted() {
        return this._kernelRestarted;
    }
    get kernelLanguage() {
        var _a;
        if (!((_a = this._session.session) === null || _a === void 0 ? void 0 : _a.kernel)) {
            return Promise.resolve('');
        }
        return this._session.session.kernel.info.then(infoReply => {
            return infoReply.language_info.name;
        });
    }
    get kernelName() {
        return this._session.kernelDisplayName;
    }
    /**
     *  A Promise that is fulfilled when the session associated w/ the connector is ready.
     */
    get ready() {
        return this._session.ready;
    }
    /**
     *  A signal emitted for iopub messages of the kernel associated with the kernel.
     */
    get iopubMessage() {
        return this._session.iopubMessage;
    }
    execute(content) {
        var _a;
        if (!((_a = this._session.session) === null || _a === void 0 ? void 0 : _a.kernel)) {
            throw new Error('No session available.');
        }
        return this._session.session.kernel.requestExecute(content);
    }
}


/***/ }),

/***/ "./lib/logconsole.js":
/*!***************************!*\
  !*** ./lib/logconsole.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   PipelineConsolePanel: () => (/* binding */ PipelineConsolePanel)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-dom */ "webpack/sharing/consume/default/react-dom");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_dom__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react_dom_server__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-dom/server */ "../../node_modules/react-dom/server.browser.js");
/* harmony import */ var _DataView__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./DataView */ "./lib/DataView.js");
/* harmony import */ var _DocumentView__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./DocumentView */ "./lib/DocumentView.js");
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! antd */ "../../node_modules/antd/es/typography/index.js");
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! antd */ "../../node_modules/antd/es/space/index.js");
/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! antd */ "../../node_modules/antd/es/alert/index.js");
/* harmony import */ var _ant_design_icons__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @ant-design/icons */ "../../node_modules/@ant-design/icons/es/icons/LoadingOutlined.js");








const { Text } = antd__WEBPACK_IMPORTED_MODULE_4__["default"];
const TITLE_CLASS = 'amphi-Console-title';
const PANEL_CLASS = 'amphi-Console';
const TABLE_CLASS = 'amphi-Console-table';
const TABLE_BODY_CLASS = 'amphi-Console-content';
const TABLE_ROW_CLASS = 'amphi-Console-table-row';
const TABLE_DATE_CLASS = 'amphi-Console-date';
/**
 * A panel that renders the pipeline logs
 */
class PipelineConsolePanel extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor() {
        super();
        this._source = null;
        this.addClass(PANEL_CLASS);
        this._title = Private.createTitle();
        this._title.className = TITLE_CLASS;
        this._console = Private.createConsole();
        this._console.className = TABLE_CLASS;
        this.node.appendChild(this._title);
        this.node.appendChild(this._console);
    }
    get source() {
        return this._source;
    }
    set source(source) {
        if (this._source === source) {
            return;
        }
        //Remove old subscriptions
        if (this._source) {
            this._source.disposed.disconnect(this.onSourceDisposed, this);
        }
        this._source = source;
        //Subscribe to new object
        if (this._source) {
            this._source.disposed.connect(this.onSourceDisposed, this);
        }
    }
    /**
     * Dispose resources
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this.source = null;
        super.dispose();
    }
    onNewLog(date, level, content) {
        if (!this.isAttached) {
            return;
        }
        // Ensure the table footer exists
        if (!this._console.tFoot) {
            this._console.createTFoot();
            this._console.tFoot.className = TABLE_BODY_CLASS;
        }
        // Insert a new row at the beginning of the table footer
        let row = this._console.tFoot.insertRow(0); // Changed from -1 to 0
        row.className = `${TABLE_ROW_CLASS}`;
        // Add cells to the new row
        let cell = row.insertCell(0);
        let container;
        cell.innerHTML = `
    <span>
      ${react_dom_server__WEBPACK_IMPORTED_MODULE_3__.renderToString(react__WEBPACK_IMPORTED_MODULE_1___default().createElement(antd__WEBPACK_IMPORTED_MODULE_5__["default"], null,
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(Text, null, date)))}
    </span>
  `;
        cell.style.padding = "5px"; // Remove padding from the cell
        cell.className = TABLE_DATE_CLASS;
        const spinIndicator = react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_ant_design_icons__WEBPACK_IMPORTED_MODULE_6__["default"], { style: { fontSize: 24 }, spin: true });
        switch (level) {
            case "info":
                cell = row.insertCell(1);
                cell.style.padding = "5px"; // Remove padding from the cell
                container = document.createElement('div'); // Create a container for the React component
                cell.appendChild(container); // Append the container to the cell
                // Determine the alert type based on content
                let alertType = /SUCCESS/i.test(content)
                    ? "success"
                    : /ERROR|WARNING/i.test(content)
                        ? "warning"
                        : "info";
                console.log("content %o", content);
                react_dom__WEBPACK_IMPORTED_MODULE_2___default().render(react__WEBPACK_IMPORTED_MODULE_1___default().createElement(antd__WEBPACK_IMPORTED_MODULE_7__["default"], { showIcon: true, message: react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { dangerouslySetInnerHTML: { __html: content } }), type: alertType }), container);
                break;
            case "error":
                cell = row.insertCell(1);
                cell.style.padding = "5px"; // Remove padding from the cell
                container = document.createElement('div'); // Create a container for the React component
                cell.appendChild(container); // Append the container to the cell
                react_dom__WEBPACK_IMPORTED_MODULE_2___default().render(react__WEBPACK_IMPORTED_MODULE_1___default().createElement(antd__WEBPACK_IMPORTED_MODULE_7__["default"], { message: "Error", showIcon: true, description: react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { dangerouslySetInnerHTML: { __html: content.replace(/\n/g, '<br>').replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;') } }), type: "error" }), container);
                break;
            case "data":
                cell = row.insertCell(1);
                cell.style.padding = "5"; // Remove padding from the cell
                container = document.createElement('div'); // Create a container for the React component
                cell.appendChild(container); // Append the container to the cell
                const parser = new DOMParser();
                const doc = parser.parseFromString(content, 'text/html');
                const firstDiv = doc.querySelector('div');
                if (firstDiv && firstDiv.id === 'documents') {
                    react_dom__WEBPACK_IMPORTED_MODULE_2___default().render(react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_DocumentView__WEBPACK_IMPORTED_MODULE_8__["default"], { htmlData: content }), container);
                }
                else {
                    react_dom__WEBPACK_IMPORTED_MODULE_2___default().render(react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_DataView__WEBPACK_IMPORTED_MODULE_9__["default"], { htmlData: content }), container);
                }
                break;
            default:
                // Handle other cases or do nothing
                break;
        }
        // Scroll to the top
        this._console.parentElement.scrollTop = 0; // Changed to scroll to the top
    }
    clearLogs() {
        // Check if table footer exists and remove all its rows
        if (this._console.tFoot) {
            while (this._console.tFoot.rows.length > 0) {
                this._console.tFoot.deleteRow(0);
            }
        }
    }
    /**
     * Handle source disposed signals.
     */
    onSourceDisposed(sender, args) {
        this.source = null;
    }
}
var Private;
(function (Private) {
    const entityMap = new Map(Object.entries({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;'
    }));
    function escapeHtml(source) {
        return String(source).replace(/[&<>"'/]/g, (s) => entityMap.get(s));
    }
    Private.escapeHtml = escapeHtml;
    function createConsole() {
        const table = document.createElement('table');
        return table;
    }
    Private.createConsole = createConsole;
    function createTitle(header = '') {
        const title = document.createElement('p');
        title.innerHTML = header;
        return title;
    }
    Private.createTitle = createTitle;
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/manager.js":
/*!************************!*\
  !*** ./lib/manager.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   LogConsoleManager: () => (/* binding */ LogConsoleManager)
/* harmony export */ });
/**
 * A class that manages variable inspector widget instances and offers persistent
 * `IMetadataPanel` instance that other plugins can communicate with.
 */
class LogConsoleManager {
    constructor() {
        this._source = null;
        this._panel = null;
        this._handlers = {};
    }
    hasHandler(id) {
        if (this._handlers[id]) {
            return true;
        }
        else {
            return false;
        }
    }
    getHandler(id) {
        return this._handlers[id];
    }
    addHandler(handler) {
        this._handlers[handler.id] = handler;
    }
    /**
     * The current console panel.
     */
    get panel() {
        return this._panel;
    }
    set panel(panel) {
        if (this.panel === panel) {
            return;
        }
        this._panel = panel;
        if (panel && !panel.source) {
            panel.source = this._source;
        }
    }
    /**
     * The source of events the inspector panel listens for.
     */
    get source() {
        return this._source;
    }
    set source(source) {
        if (this._source === source) {
            return;
        }
        // remove subscriptions
        if (this._source) {
            this._source.disposed.disconnect(this._onSourceDisposed, this);
        }
        this._source = source;
        if (this._panel && !this._panel.isDisposed) {
            this._panel.source = this._source;
        }
        // Subscribe to new source
        if (this._source) {
            this._source.disposed.connect(this._onSourceDisposed, this);
        }
    }
    _onSourceDisposed() {
        this._source = null;
    }
}


/***/ }),

/***/ "./lib/tokens.js":
/*!***********************!*\
  !*** ./lib/tokens.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IPipelineConsole: () => (/* binding */ IPipelineConsole),
/* harmony export */   IPipelineConsoleManager: () => (/* binding */ IPipelineConsoleManager)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);

const IPipelineConsoleManager = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token('jupyterlab_extension/logconsole:IPipelineConsoleManager');
/**
 * The inspector panel token.
 */
const IPipelineConsole = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token('jupyterlab_extension/logconsole:IPipelineConsole');


/***/ })

}]);
//# sourceMappingURL=lib_index_js.e37cb1efc909782c1f58.js.map