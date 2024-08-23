"use strict";
(self["webpackChunk_noworkflow_labextension"] = self["webpackChunk_noworkflow_labextension"] || []).push([["lib_index_js"],{

/***/ "../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/cjs.js!./style/index.css":
/*!****************************************************************************************************!*\
  !*** ../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/cjs.js!./style/index.css ***!
  \****************************************************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/runtime/sourceMaps.js */ "../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/runtime/api.js */ "../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/cjs.js!./base.css */ "../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/cjs.js!./style/base.css");
// Imports



var ___CSS_LOADER_EXPORT___ = _node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_jupyterlab_builder_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_jupyterlab_builder_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
// Module
___CSS_LOADER_EXPORT___.push([module.id, `
`, "",{"version":3,"sources":[],"names":[],"mappings":"","sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./lib/coderenderer.js":
/*!*****************************!*\
  !*** ./lib/coderenderer.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RenderedCode: () => (/* binding */ RenderedCode),
/* harmony export */   codeFactory: () => (/* binding */ codeFactory)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _noworkflow_utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @noworkflow/utils */ "webpack/sharing/consume/default/@noworkflow/utils/@noworkflow/utils");
/* harmony import */ var _noworkflow_utils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_noworkflow_utils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var codemirror__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! codemirror */ "webpack/sharing/consume/default/codemirror/codemirror");
/* harmony import */ var codemirror__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(codemirror__WEBPACK_IMPORTED_MODULE_2__);



/**
 * A widget for rendering data, for usage with rendermime.
 */
class RenderedCode extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    /**
     * Create a new widget for rendering
     */
    constructor(options) {
        super();
        this._mimeType = options.mimeType;
        this.addClass('jp-RenderedNowCode');
        this.div = document.createElement('div');
        this.node.appendChild(this.div);
    }
    /**
     * Render into this widget's node.
     */
    renderModel(model) {
        var self = this;
        return new Promise((resolve, reject) => {
            let data = model.data[this._mimeType];
            var code_id = (0,_noworkflow_utils__WEBPACK_IMPORTED_MODULE_1__.makeid)();
            var textarea = document.createElement('textarea');
            this.div.appendChild(textarea);
            textarea.id = code_id;
            textarea.value = data.code;
            self.code_mirror = codemirror__WEBPACK_IMPORTED_MODULE_2___default().fromTextArea(textarea, {
                lineNumbers: true,
                firstLineNumber: data.firstLineNumber,
                mode: "python",
                readOnly: true
            });
            self.code_mirror.setValue(data.code);
            var marks = data.marks;
            marks.forEach(function (mark) {
                var _a;
                (_a = self.code_mirror) === null || _a === void 0 ? void 0 : _a.markText.apply(self.code_mirror, mark);
            });
            if (data.showSelection) {
                var selection = document.createElement('input');
                selection.id = code_id + '-selection';
                selection.type = 'text';
                this.div.appendChild(selection);
                self.code_mirror.on('cursorActivity', function (cm) {
                    var tcursor = cm.getCursor(true);
                    var fcursor = cm.getCursor(false);
                    selection.value = ("[" + tcursor.line + ", " + tcursor.ch + "], " +
                        "[" + fcursor.line + ", " + fcursor.ch + "]");
                });
            }
            this.update();
            resolve();
        });
    }
    /**
     * A message handler invoked on an `'after-show'` message.
     */
    onAfterShow(msg) {
        this.update();
    }
    /**
     * A message handler invoked on a `'resize'` message.
     */
    onResize(msg) {
        this.update();
    }
    /**
     * A message handler invoked on an `'update-request'` message.
     */
    onUpdateRequest(msg) {
        // Update size after update
        var self = this;
        if (this.isVisible && self.code_mirror) {
            setTimeout(function () {
                var _a;
                (_a = self.code_mirror) === null || _a === void 0 ? void 0 : _a.refresh();
            }, 1);
        }
    }
}
/**
 * A mime renderer factory for data.
 */
const codeFactory = {
    safe: false,
    mimeTypes: ['application/noworkflow.code+json'],
    createRenderer: options => new RenderedCode(options)
};


/***/ }),

/***/ "./lib/historyrenderer.js":
/*!********************************!*\
  !*** ./lib/historyrenderer.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RenderedHistory: () => (/* binding */ RenderedHistory),
/* harmony export */   historyFactory: () => (/* binding */ historyFactory)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _noworkflow_history__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @noworkflow/history */ "webpack/sharing/consume/default/@noworkflow/history/@noworkflow/history");
/* harmony import */ var _noworkflow_history__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_noworkflow_history__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _noworkflow_utils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @noworkflow/utils */ "webpack/sharing/consume/default/@noworkflow/utils/@noworkflow/utils");
/* harmony import */ var _noworkflow_utils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_noworkflow_utils__WEBPACK_IMPORTED_MODULE_2__);



/**
 * A widget for rendering data, for usage with rendermime.
 */
class RenderedHistory extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    /**
     * Create a new widget for rendering
     */
    constructor(options) {
        super();
        this._mimeType = options.mimeType;
        this.addClass('jp-RenderedNowHistory');
        this.div = document.createElement('div');
        this.node.appendChild(this.div);
    }
    /**
     * Render into this widget's node.
     */
    renderModel(model) {
        return new Promise((resolve, reject) => {
            let data = model.data[this._mimeType];
            this.graph = new _noworkflow_history__WEBPACK_IMPORTED_MODULE_1__.HistoryGraph('history-' + (0,_noworkflow_utils__WEBPACK_IMPORTED_MODULE_2__.makeid)(), this.div, {
                width: data.width,
                height: data.height,
                hintMessage: ""
            });
            this.graph.load(data);
            this.update();
            resolve();
        });
    }
    /**
     * A message handler invoked on an `'after-show'` message.
     */
    onAfterShow(msg) {
        this.update();
    }
    /**
     * A message handler invoked on a `'resize'` message.
     */
    onResize(msg) {
        this.update();
    }
    /**
     * A message handler invoked on an `'update-request'` message.
     */
    onUpdateRequest(msg) {
        // Update size after update
        if (this.isVisible && this.graph) {
            let width = this.node.getBoundingClientRect().width - 24;
            this.graph.config.width = width;
            this.div.style.width = width + "px";
            this.graph.updateWindow();
        }
    }
}
/**
 * A mime renderer factory for data.
 */
const historyFactory = {
    safe: false,
    mimeTypes: ['application/noworkflow.history+json'],
    createRenderer: options => new RenderedHistory(options)
};


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
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");
/* harmony import */ var _historyrenderer__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./historyrenderer */ "./lib/historyrenderer.js");
/* harmony import */ var _trialrenderer__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./trialrenderer */ "./lib/trialrenderer.js");
/* harmony import */ var _coderenderer__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./coderenderer */ "./lib/coderenderer.js");




const TYPES = {
    'application/noworkflow.history+json': {
        name: 'noWorkflow History',
        extensions: ['.nowhistory'],
        factory: _historyrenderer__WEBPACK_IMPORTED_MODULE_1__.historyFactory
    },
    'application/noworkflow.trial+json': {
        name: 'noWorkflow Trial',
        extensions: ['.nowtrial'],
        factory: _trialrenderer__WEBPACK_IMPORTED_MODULE_2__.trialFactory
    },
    'application/noworkflow.code+json': {
        name: 'noWorkflow Code',
        extensions: ['.nowcode'],
        factory: _coderenderer__WEBPACK_IMPORTED_MODULE_3__.codeFactory
    }
};
/**
 * Extension definition.
 */
const extensions = Object.keys(TYPES).map(k => {
    const { name, factory } = TYPES[k];
    return {
        id: `jupyterlab-noworkflow:${name}`,
        rendererFactory: factory,
        rank: 100,
        dataType: 'json',
        fileTypes: [
            {
                name,
                mimeTypes: [k],
                extensions: TYPES[k].extensions
            }
        ],
        documentWidgetFactoryOptions: {
            name,
            primaryFileType: name,
            fileTypes: [name, 'json'],
            defaultFor: [name]
        }
    };
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extensions);


/***/ }),

/***/ "./lib/trialrenderer.js":
/*!******************************!*\
  !*** ./lib/trialrenderer.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RenderedTrial: () => (/* binding */ RenderedTrial),
/* harmony export */   trialFactory: () => (/* binding */ trialFactory)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _noworkflow_trial__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @noworkflow/trial */ "webpack/sharing/consume/default/@noworkflow/trial/@noworkflow/trial");
/* harmony import */ var _noworkflow_trial__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_noworkflow_trial__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _noworkflow_utils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @noworkflow/utils */ "webpack/sharing/consume/default/@noworkflow/utils/@noworkflow/utils");
/* harmony import */ var _noworkflow_utils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_noworkflow_utils__WEBPACK_IMPORTED_MODULE_2__);



/**
 * A widget for rendering data, for usage with rendermime.
 */
class RenderedTrial extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    /**
     * Create a new widget for rendering
     */
    constructor(options) {
        super();
        this._mimeType = options.mimeType;
        this.addClass('jp-RenderedNowTrial');
        this.div = document.createElement('div');
        this.node.appendChild(this.div);
    }
    /**
     * Render into this widget's node.
     */
    renderModel(model) {
        return new Promise((resolve, reject) => {
            let data = model.data[this._mimeType];
            this.graph = new _noworkflow_trial__WEBPACK_IMPORTED_MODULE_1__.TrialGraph('trial-' + (0,_noworkflow_utils__WEBPACK_IMPORTED_MODULE_2__.makeid)(), this.div, {
                width: data.width,
                height: data.height,
                genDataflow: false
            });
            this.graph.load(data, data.trial1, data.trial2);
            this.update();
            resolve();
        });
    }
    /**
     * A message handler invoked on an `'after-show'` message.
     */
    onAfterShow(msg) {
        this.update();
    }
    /**
     * A message handler invoked on a `'resize'` message.
     */
    onResize(msg) {
        this.update();
    }
    /**
     * A message handler invoked on an `'update-request'` message.
     */
    onUpdateRequest(msg) {
        // Update size after update
        if (this.isVisible && this.graph) {
            let width = this.node.getBoundingClientRect().width - 24;
            this.graph.config.width = width;
            this.div.style.width = width + "px";
            this.graph.updateWindow();
        }
    }
}
const trialFactory = {
    safe: false,
    mimeTypes: ['application/noworkflow.trial+json'],
    createRenderer: options => new RenderedTrial(options)
};


/***/ }),

/***/ "./style/index.css":
/*!*************************!*\
  !*** ./style/index.css ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !../../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/styleDomAPI.js */ "../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/styleDomAPI.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/insertBySelector.js */ "../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/insertBySelector.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js */ "../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! !../../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/insertStyleElement.js */ "../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/insertStyleElement.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! !../../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/styleTagTransform.js */ "../../node_modules/@jupyterlab/builder/node_modules/style-loader/dist/runtime/styleTagTransform.js");
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _node_modules_jupyterlab_builder_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! !!../../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/cjs.js!./index.css */ "../../node_modules/@jupyterlab/builder/node_modules/css-loader/dist/cjs.js!./style/index.css");

      
      
      
      
      
      
      
      
      

var options = {};

options.styleTagTransform = (_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default());
options.setAttributes = (_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default());

      options.insert = _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default().bind(null, "head");
    
options.domAPI = (_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default());
options.insertStyleElement = (_node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default());

var update = _node_modules_jupyterlab_builder_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_jupyterlab_builder_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"], options);




       /* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_jupyterlab_builder_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"] && _node_modules_jupyterlab_builder_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals ? _node_modules_jupyterlab_builder_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals : undefined);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.cc08504316485c558298.js.map