"use strict";
(self["webpackChunkjupyterlab_pioneer"] = self["webpackChunkjupyterlab_pioneer"] || []).push([["lib_index_js"],{

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupyterlab-pioneer', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IJupyterLabPioneer: () => (/* binding */ IJupyterLabPioneer),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _producer__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./producer */ "./lib/producer.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");






const PLUGIN_ID = 'jupyterlab-pioneer:plugin';
const IJupyterLabPioneer = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_2__.Token(PLUGIN_ID);
class JupyterLabPioneer {
    constructor() {
        this.exporters = [];
    }
    async loadExporters(notebookPanel) {
        var _a;
        const config = (await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('config'));
        const activeEvents = config.activeEvents;
        const exporters = ((_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.getMetadata('exporters')) || config.exporters; // The exporters configuration in the notebook metadata overrides the configuration in the configuration file "jupyter_jupyterlab_pioneer_config.py"
        const processedExporters = activeEvents && activeEvents.length
            ? exporters.map(e => {
                if (!e.activeEvents) {
                    e.activeEvents = activeEvents;
                    return e;
                }
                else {
                    return e;
                }
            })
            : exporters.filter(e => e.activeEvents && e.activeEvents.length);
        // Exporters without specifying the corresponding activeEvents will use the global activeEvents configuration.
        // When the global activeEvents configuration is null, exporters that do not have corresponding activeEvents will be ignored.
        console.log(processedExporters);
        this.exporters = processedExporters;
    }
    async publishEvent(notebookPanel, eventDetail, exporter, logWholeNotebook) {
        var _a, _b;
        if (!notebookPanel) {
            throw Error('router is listening to a null notebook panel');
        }
        const requestBody = {
            eventDetail: eventDetail,
            notebookState: {
                sessionID: (_a = notebookPanel === null || notebookPanel === void 0 ? void 0 : notebookPanel.sessionContext.session) === null || _a === void 0 ? void 0 : _a.id,
                notebookPath: notebookPanel === null || notebookPanel === void 0 ? void 0 : notebookPanel.context.path,
                notebookContent: logWholeNotebook
                    ? (_b = notebookPanel === null || notebookPanel === void 0 ? void 0 : notebookPanel.model) === null || _b === void 0 ? void 0 : _b.toJSON()
                    : null // decide whether to log the entire notebook
            },
            exporter: exporter
        };
        const response = await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('export', {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
        console.log(response);
    }
}
const plugin = {
    id: PLUGIN_ID,
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker, _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__.IMainMenu],
    provides: IJupyterLabPioneer,
    activate: async (app, notebookTracker, mainMenu) => {
        const version = await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('version');
        console.log(`${PLUGIN_ID}: ${version}`);
        const config = (await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('config'));
        const pioneer = new JupyterLabPioneer();
        (0,_utils__WEBPACK_IMPORTED_MODULE_4__.addInfoToHelpMenu)(app, mainMenu, version);
        notebookTracker.widgetAdded.connect(async (_, notebookPanel) => {
            await notebookPanel.revealed;
            await notebookPanel.sessionContext.ready;
            await pioneer.loadExporters(notebookPanel);
            _producer__WEBPACK_IMPORTED_MODULE_5__.producerCollection.forEach(producer => {
                new producer().listen(notebookPanel, pioneer);
            });
        });
        (0,_utils__WEBPACK_IMPORTED_MODULE_4__.sendInfoNotification)(config.exporters, true);
        return pioneer;
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/producer.js":
/*!*************************!*\
  !*** ./lib/producer.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ActiveCellChangeEventProducer: () => (/* binding */ ActiveCellChangeEventProducer),
/* harmony export */   CellAddEventProducer: () => (/* binding */ CellAddEventProducer),
/* harmony export */   CellEditEventProducer: () => (/* binding */ CellEditEventProducer),
/* harmony export */   CellExecuteEventProducer: () => (/* binding */ CellExecuteEventProducer),
/* harmony export */   CellRemoveEventProducer: () => (/* binding */ CellRemoveEventProducer),
/* harmony export */   ClipboardCopyEventProducer: () => (/* binding */ ClipboardCopyEventProducer),
/* harmony export */   ClipboardCutEventProducer: () => (/* binding */ ClipboardCutEventProducer),
/* harmony export */   ClipboardPasteEventProducer: () => (/* binding */ ClipboardPasteEventProducer),
/* harmony export */   NotebookHiddenEventProducer: () => (/* binding */ NotebookHiddenEventProducer),
/* harmony export */   NotebookOpenEventProducer: () => (/* binding */ NotebookOpenEventProducer),
/* harmony export */   NotebookSaveEventProducer: () => (/* binding */ NotebookSaveEventProducer),
/* harmony export */   NotebookScrollEventProducer: () => (/* binding */ NotebookScrollEventProducer),
/* harmony export */   NotebookVisibleEventProducer: () => (/* binding */ NotebookVisibleEventProducer),
/* harmony export */   producerCollection: () => (/* binding */ producerCollection)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @codemirror/view */ "webpack/sharing/consume/default/@codemirror/view");
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_codemirror_view__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");



class ActiveCellChangeEventProducer {
    listen(notebookPanel, pioneer) {
        notebookPanel.content.activeCellChanged.connect(async (_, cell) => {
            if (cell && notebookPanel.content.widgets) {
                const activatedCell = {
                    id: cell === null || cell === void 0 ? void 0 : cell.model.id,
                    index: notebookPanel.content.widgets.findIndex(value => value === cell)
                };
                const event = {
                    eventName: ActiveCellChangeEventProducer.id,
                    eventTime: Date.now(),
                    eventInfo: {
                        cells: [activatedCell] // activated cell
                    }
                };
                pioneer.exporters.forEach(async (exporter) => {
                    var _a, _b, _c;
                    if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(ActiveCellChangeEventProducer.id)) {
                        await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == ActiveCellChangeEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    }
                });
            }
        });
    }
}
ActiveCellChangeEventProducer.id = 'ActiveCellChangeEvent';

class CellAddEventProducer {
    listen(notebookPanel, pioneer) {
        var _a;
        (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect(async (_, args) => {
            if (args.type === 'add') {
                const addedCell = {
                    id: args.newValues[0].id,
                    index: args.newIndex
                };
                const event = {
                    eventName: CellAddEventProducer.id,
                    eventTime: Date.now(),
                    eventInfo: {
                        cells: [addedCell]
                    }
                };
                pioneer.exporters.forEach(async (exporter) => {
                    var _a, _b, _c;
                    if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(CellAddEventProducer.id)) {
                        await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == CellAddEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    }
                });
            }
        });
    }
}
CellAddEventProducer.id = 'CellAddEvent';

class CellEditEventProducer {
    listen(notebookPanel, pioneer) {
        var _a, _b;
        const sendDoc = async (_, cell) => {
            var _a, _b;
            await (cell === null || cell === void 0 ? void 0 : cell.ready); // wait until cell is ready, to prevent errors when creating new cells
            const editor = cell === null || cell === void 0 ? void 0 : cell.editor;
            const event = {
                eventName: CellEditEventProducer.id,
                eventTime: Date.now(),
                eventInfo: {
                    index: notebookPanel.content.widgets.findIndex(value => value === cell),
                    doc: (_b = (_a = editor === null || editor === void 0 ? void 0 : editor.state) === null || _a === void 0 ? void 0 : _a.doc) === null || _b === void 0 ? void 0 : _b.toJSON() // send entire cell content if this is a new cell
                }
            };
            pioneer.exporters.forEach(async (exporter) => {
                var _a, _b, _c;
                if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(CellEditEventProducer.id)) {
                    await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == CellEditEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                }
            });
        };
        const addDocChangeListener = async (cell) => {
            await (cell === null || cell === void 0 ? void 0 : cell.ready); // wait until cell is ready, to prevent errors when creating new cells
            const editor = cell === null || cell === void 0 ? void 0 : cell.editor;
            editor === null || editor === void 0 ? void 0 : editor.injectExtension(_codemirror_view__WEBPACK_IMPORTED_MODULE_1__.EditorView.updateListener.of(async (v) => {
                if (v.docChanged) {
                    const event = {
                        eventName: CellEditEventProducer.id,
                        eventTime: Date.now(),
                        eventInfo: {
                            index: notebookPanel.content.widgets.findIndex(value => value === cell),
                            changes: v.changes.toJSON() // send changes
                        }
                    };
                    pioneer.exporters.forEach(async (exporter) => {
                        var _a;
                        if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(CellEditEventProducer.id)) {
                            await pioneer.publishEvent(notebookPanel, event, exporter, false // do not log whole notebook for doc changes
                            );
                        }
                    });
                }
            }));
        };
        (_a = notebookPanel === null || notebookPanel === void 0 ? void 0 : notebookPanel.content) === null || _a === void 0 ? void 0 : _a.widgets.forEach(cell => {
            addDocChangeListener(cell);
        }); // add listener to existing cells
        sendDoc(notebookPanel.content, notebookPanel.content.activeCell); // send initial active cell content
        (_b = notebookPanel.content.model) === null || _b === void 0 ? void 0 : _b.cells.changed.connect(async (_, args) => {
            var _a;
            if (args.type === 'add') {
                addDocChangeListener((_a = notebookPanel === null || notebookPanel === void 0 ? void 0 : notebookPanel.content) === null || _a === void 0 ? void 0 : _a.widgets[args.newIndex]);
            }
        }); // add doc change listener to cells created after initialization
        notebookPanel.content.activeCellChanged.connect(sendDoc); // send active cell content when active cell changes
    }
}
CellEditEventProducer.id = 'CellEditEvent';

class CellExecuteEventProducer {
    listen(notebookPanel, pioneer) {
        _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.executed.connect(async (_, args) => {
            if (notebookPanel.content === args.notebook) {
                const executedCell = {
                    id: args.cell.model.id,
                    index: args.notebook.widgets.findIndex(value => value == args.cell)
                };
                const event = {
                    eventName: CellExecuteEventProducer.id,
                    eventTime: Date.now(),
                    eventInfo: {
                        cells: [executedCell],
                        success: args.success,
                        kernelError: args.success ? null : args.error
                    }
                };
                pioneer.exporters.forEach(async (exporter) => {
                    var _a, _b, _c;
                    if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(CellExecuteEventProducer.id)) {
                        await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == CellExecuteEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    }
                });
            }
        });
    }
}
CellExecuteEventProducer.id = 'CellExecuteEvent';

class CellRemoveEventProducer {
    listen(notebookPanel, pioneer) {
        var _a;
        (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect(async (_, args) => {
            if (args.type === 'remove') {
                const removedCell = {
                    index: args.oldIndex
                };
                const event = {
                    eventName: CellRemoveEventProducer.id,
                    eventTime: Date.now(),
                    eventInfo: {
                        cells: [removedCell]
                    }
                };
                pioneer.exporters.forEach(async (exporter) => {
                    var _a, _b, _c;
                    if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(CellRemoveEventProducer.id)) {
                        await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == CellRemoveEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    }
                });
            }
        });
    }
}
CellRemoveEventProducer.id = 'CellRemoveEvent';

class ClipboardCopyEventProducer {
    listen(notebookPanel, pioneer) {
        notebookPanel.node.addEventListener('copy', async () => {
            var _a, _b;
            const cell = {
                id: (_a = notebookPanel.content.activeCell) === null || _a === void 0 ? void 0 : _a.model.id,
                index: notebookPanel.content.widgets.findIndex(value => value === notebookPanel.content.activeCell)
            };
            const text = (_b = document.getSelection()) === null || _b === void 0 ? void 0 : _b.toString();
            const event = {
                eventName: ClipboardCopyEventProducer.id,
                eventTime: Date.now(),
                eventInfo: {
                    cells: [cell],
                    selection: text
                }
            };
            pioneer.exporters.forEach(async (exporter) => {
                var _a, _b, _c;
                if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(ClipboardCopyEventProducer.id)) {
                    await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == ClipboardCopyEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                }
            });
        });
    }
}
ClipboardCopyEventProducer.id = 'ClipboardCopyEvent';

class ClipboardCutEventProducer {
    listen(notebookPanel, pioneer) {
        notebookPanel.node.addEventListener('cut', async () => {
            var _a, _b;
            const cell = {
                id: (_a = notebookPanel.content.activeCell) === null || _a === void 0 ? void 0 : _a.model.id,
                index: notebookPanel.content.widgets.findIndex(value => value === notebookPanel.content.activeCell)
            };
            const text = (_b = document.getSelection()) === null || _b === void 0 ? void 0 : _b.toString();
            const event = {
                eventName: ClipboardCutEventProducer.id,
                eventTime: Date.now(),
                eventInfo: {
                    cells: [cell],
                    selection: text
                }
            };
            pioneer.exporters.forEach(async (exporter) => {
                var _a, _b, _c;
                if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(ClipboardCutEventProducer.id)) {
                    await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == ClipboardCutEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                }
            });
        });
    }
}
ClipboardCutEventProducer.id = 'ClipboardCutEvent';

class ClipboardPasteEventProducer {
    listen(notebookPanel, pioneer) {
        notebookPanel.node.addEventListener('paste', async (e) => {
            var _a;
            const cell = {
                id: (_a = notebookPanel.content.activeCell) === null || _a === void 0 ? void 0 : _a.model.id,
                index: notebookPanel.content.widgets.findIndex(value => value === notebookPanel.content.activeCell)
            };
            const text = (e.clipboardData || window.clipboardData).getData('text');
            const event = {
                eventName: ClipboardPasteEventProducer.id,
                eventTime: Date.now(),
                eventInfo: {
                    cells: [cell],
                    selection: text
                }
            };
            pioneer.exporters.forEach(async (exporter) => {
                var _a, _b, _c;
                if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(ClipboardPasteEventProducer.id)) {
                    await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == ClipboardPasteEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                }
            });
        });
    }
}
ClipboardPasteEventProducer.id = 'ClipboardPasteEvent';

class NotebookHiddenEventProducer {
    listen(notebookPanel, pioneer) {
        document.addEventListener('visibilitychange', async (e) => {
            if (document.visibilityState === 'hidden' &&
                document.contains(notebookPanel.node)) {
                const event = {
                    eventName: NotebookHiddenEventProducer.id,
                    eventTime: Date.now(),
                    eventInfo: null
                };
                pioneer.exporters.forEach(async (exporter) => {
                    var _a, _b, _c;
                    if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(NotebookHiddenEventProducer.id)) {
                        await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == NotebookHiddenEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    }
                });
            }
        });
    }
}
NotebookHiddenEventProducer.id = 'NotebookHiddenEvent';

class NotebookOpenEventProducer {
    constructor() {
        this.produced = false;
    }
    async listen(notebookPanel, pioneer) {
        if (!this.produced) {
            const event = {
                eventName: NotebookOpenEventProducer.id,
                eventTime: Date.now(),
                eventInfo: {
                    environ: await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('environ')
                }
            };
            pioneer.exporters.forEach(async (exporter) => {
                var _a, _b, _c;
                if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(NotebookOpenEventProducer.id)) {
                    await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == NotebookOpenEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    this.produced = true;
                }
            });
        }
    }
}
NotebookOpenEventProducer.id = 'NotebookOpenEvent';

class NotebookSaveEventProducer {
    listen(notebookPanel, pioneer) {
        notebookPanel.context.saveState.connect(async (_, saveState) => {
            if (saveState.match('completed')) {
                const event = {
                    eventName: NotebookSaveEventProducer.id,
                    eventTime: Date.now(),
                    eventInfo: null
                };
                pioneer.exporters.forEach(async (exporter) => {
                    var _a, _b, _c;
                    if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(NotebookSaveEventProducer.id)) {
                        await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == NotebookSaveEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    }
                });
            }
        });
    }
}
NotebookSaveEventProducer.id = 'NotebookSaveEvent';

const getVisibleCells = (notebookPanel) => {
    const visibleCells = [];
    for (let index = 0; index < notebookPanel.content.widgets.length; index++) {
        const cell = notebookPanel.content.widgets[index];
        const cellTop = cell.node.offsetTop;
        const cellBottom = cell.node.offsetTop + cell.node.offsetHeight;
        const viewTop = notebookPanel.node.getElementsByClassName('jp-WindowedPanel-outer')[0].scrollTop;
        const viewBottom = notebookPanel.content.node.getElementsByClassName('jp-WindowedPanel-outer')[0].scrollTop +
            notebookPanel.content.node.getElementsByClassName('jp-WindowedPanel-outer')[0].clientHeight;
        if (cellTop <= viewBottom && cellBottom >= viewTop) {
            visibleCells.push({
                id: cell.model.id,
                index: index
            });
        }
    }
    return visibleCells;
};
class NotebookScrollEventProducer {
    constructor() {
        this.timeout = 0;
    }
    listen(notebookPanel, pioneer) {
        notebookPanel.node.getElementsByClassName('jp-WindowedPanel-outer')[0].addEventListener('scroll', async (e) => {
            e.stopPropagation();
            clearTimeout(this.timeout);
            await new Promise(resolve => (this.timeout = window.setTimeout(resolve, 1500))); // wait 1.5 seconds before preceding
            const event = {
                eventName: NotebookScrollEventProducer.id,
                eventTime: Date.now(),
                eventInfo: {
                    cells: getVisibleCells(notebookPanel)
                }
            };
            pioneer.exporters.forEach(async (exporter) => {
                var _a, _b, _c;
                if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(NotebookScrollEventProducer.id)) {
                    await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == NotebookScrollEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                }
            });
        });
    }
}
NotebookScrollEventProducer.id = 'NotebookScrollEvent';

class NotebookVisibleEventProducer {
    listen(notebookPanel, pioneer) {
        document.addEventListener('visibilitychange', async () => {
            if (document.visibilityState === 'visible' &&
                document.contains(notebookPanel.node)) {
                const event = {
                    eventName: NotebookVisibleEventProducer.id,
                    eventTime: Date.now(),
                    eventInfo: {
                        cells: getVisibleCells(notebookPanel)
                    }
                };
                pioneer.exporters.forEach(async (exporter) => {
                    var _a, _b, _c;
                    if ((_a = exporter.activeEvents) === null || _a === void 0 ? void 0 : _a.map(o => o.name).includes(NotebookVisibleEventProducer.id)) {
                        await pioneer.publishEvent(notebookPanel, event, exporter, (_c = (_b = exporter.activeEvents) === null || _b === void 0 ? void 0 : _b.find(o => o.name == NotebookVisibleEventProducer.id)) === null || _c === void 0 ? void 0 : _c.logWholeNotebook);
                    }
                });
            }
        });
    }
}
NotebookVisibleEventProducer.id = 'NotebookVisibleEvent';

const producerCollection = [
    ActiveCellChangeEventProducer,
    CellAddEventProducer,
    CellExecuteEventProducer,
    CellRemoveEventProducer,
    CellEditEventProducer,
    ClipboardCopyEventProducer,
    ClipboardCutEventProducer,
    ClipboardPasteEventProducer,
    NotebookHiddenEventProducer,
    NotebookOpenEventProducer,
    NotebookSaveEventProducer,
    NotebookScrollEventProducer,
    NotebookVisibleEventProducer
];


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   addInfoToHelpMenu: () => (/* binding */ addInfoToHelpMenu),
/* harmony export */   sendInfoNotification: () => (/* binding */ sendInfoNotification)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);


const sendInfoNotification = (exporters, isGlobal) => {
    const exporterMessage = exporters
        .map(each => { var _a; return ((_a = each.args) === null || _a === void 0 ? void 0 : _a.id) || each.type; })
        .join(' & ');
    let message;
    if (isGlobal && exporterMessage) {
        message = `Telemetry data is being logged to ${exporterMessage} through jupyterlab-pioneer. \n See Help menu -> JupyterLab Pioneer for more details.`;
    }
    else if (isGlobal && !exporterMessage) {
        message = `Telemetry data is being logged through jupyterlab-pioneer. \n See Help menu -> JupyterLab Pioneer for more details.`;
    }
    else {
        message = `Embedded telemetry settings loaded. Telemetry data is being logged to ${exporterMessage} now.`;
    }
    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.info(message, { autoClose: 20000 });
};
const addInfoToHelpMenu = (app, mainMenu, version) => {
    // Add extension info to help menu
    app.commands.addCommand('help:pioneer', {
        label: 'JupyterLab Pioneer',
        execute: () => {
            // Create the header of the dialog
            const title = (react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-About-header" },
                "JupyterLab Pioneer",
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: "jp-About-header-info" },
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-About-version-info" },
                        react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-About-version" },
                            "Version ",
                            version)))));
            // Create the body of the dialog
            const contributorsURL = 'https://github.com/educational-technology-collective/jupyterlab-pioneer/graphs/contributors';
            const docURL = 'https://jupyterlab-pioneer.readthedocs.io/en/latest/';
            const gitURL = 'https://github.com/educational-technology-collective/jupyterlab-pioneer';
            const externalLinks = (react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-About-externalLinks" },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("a", { href: contributorsURL, target: "_blank", rel: "noopener noreferrer", className: "jp-Button-flat" }, "CONTRIBUTOR LIST"),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("a", { href: docURL, target: "_blank", rel: "noopener noreferrer", className: "jp-Button-flat" }, "DOCUMENTATION"),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement("a", { href: gitURL, target: "_blank", rel: "noopener noreferrer", className: "jp-Button-flat" }, "GITHUB REPO")));
            const copyright = (react__WEBPACK_IMPORTED_MODULE_0__.createElement("span", { className: "jp-About-copyright" }, "\u00A9 2023 Educational Technology Collective"));
            const body = (react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: "jp-About-body" },
                externalLinks,
                copyright));
            return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                title,
                body,
                buttons: [
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.createButton({
                        label: 'Dismiss',
                        className: 'jp-About-button jp-mod-reject jp-mod-styled'
                    })
                ]
            });
        }
    });
    mainMenu.helpMenu.addGroup([{ command: 'help:pioneer' }]);
};


/***/ })

}]);
//# sourceMappingURL=lib_index_js.589ab0c63b0825fc8f14.js.map