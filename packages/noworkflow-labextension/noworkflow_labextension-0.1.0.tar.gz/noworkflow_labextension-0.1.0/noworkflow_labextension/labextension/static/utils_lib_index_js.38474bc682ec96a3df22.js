"use strict";
(self["webpackChunk_noworkflow_labextension"] = self["webpackChunk_noworkflow_labextension"] || []).push([["utils_lib_index_js"],{

/***/ "../../node_modules/d3-dsv/src/csv.js":
/*!********************************************!*\
  !*** ../../node_modules/d3-dsv/src/csv.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   csvFormat: () => (/* binding */ csvFormat),
/* harmony export */   csvFormatBody: () => (/* binding */ csvFormatBody),
/* harmony export */   csvFormatRow: () => (/* binding */ csvFormatRow),
/* harmony export */   csvFormatRows: () => (/* binding */ csvFormatRows),
/* harmony export */   csvFormatValue: () => (/* binding */ csvFormatValue),
/* harmony export */   csvParse: () => (/* binding */ csvParse),
/* harmony export */   csvParseRows: () => (/* binding */ csvParseRows)
/* harmony export */ });
/* harmony import */ var _dsv_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./dsv.js */ "../../node_modules/d3-dsv/src/dsv.js");


var csv = (0,_dsv_js__WEBPACK_IMPORTED_MODULE_0__["default"])(",");

var csvParse = csv.parse;
var csvParseRows = csv.parseRows;
var csvFormat = csv.format;
var csvFormatBody = csv.formatBody;
var csvFormatRows = csv.formatRows;
var csvFormatRow = csv.formatRow;
var csvFormatValue = csv.formatValue;


/***/ }),

/***/ "../../node_modules/d3-dsv/src/dsv.js":
/*!********************************************!*\
  !*** ../../node_modules/d3-dsv/src/dsv.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
var EOL = {},
    EOF = {},
    QUOTE = 34,
    NEWLINE = 10,
    RETURN = 13;

function objectConverter(columns) {
  return new Function("d", "return {" + columns.map(function(name, i) {
    return JSON.stringify(name) + ": d[" + i + "] || \"\"";
  }).join(",") + "}");
}

function customConverter(columns, f) {
  var object = objectConverter(columns);
  return function(row, i) {
    return f(object(row), i, columns);
  };
}

// Compute unique columns in order of discovery.
function inferColumns(rows) {
  var columnSet = Object.create(null),
      columns = [];

  rows.forEach(function(row) {
    for (var column in row) {
      if (!(column in columnSet)) {
        columns.push(columnSet[column] = column);
      }
    }
  });

  return columns;
}

function pad(value, width) {
  var s = value + "", length = s.length;
  return length < width ? new Array(width - length + 1).join(0) + s : s;
}

function formatYear(year) {
  return year < 0 ? "-" + pad(-year, 6)
    : year > 9999 ? "+" + pad(year, 6)
    : pad(year, 4);
}

function formatDate(date) {
  var hours = date.getUTCHours(),
      minutes = date.getUTCMinutes(),
      seconds = date.getUTCSeconds(),
      milliseconds = date.getUTCMilliseconds();
  return isNaN(date) ? "Invalid Date"
      : formatYear(date.getUTCFullYear(), 4) + "-" + pad(date.getUTCMonth() + 1, 2) + "-" + pad(date.getUTCDate(), 2)
      + (milliseconds ? "T" + pad(hours, 2) + ":" + pad(minutes, 2) + ":" + pad(seconds, 2) + "." + pad(milliseconds, 3) + "Z"
      : seconds ? "T" + pad(hours, 2) + ":" + pad(minutes, 2) + ":" + pad(seconds, 2) + "Z"
      : minutes || hours ? "T" + pad(hours, 2) + ":" + pad(minutes, 2) + "Z"
      : "");
}

/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(delimiter) {
  var reFormat = new RegExp("[\"" + delimiter + "\n\r]"),
      DELIMITER = delimiter.charCodeAt(0);

  function parse(text, f) {
    var convert, columns, rows = parseRows(text, function(row, i) {
      if (convert) return convert(row, i - 1);
      columns = row, convert = f ? customConverter(row, f) : objectConverter(row);
    });
    rows.columns = columns || [];
    return rows;
  }

  function parseRows(text, f) {
    var rows = [], // output rows
        N = text.length,
        I = 0, // current character index
        n = 0, // current line number
        t, // current token
        eof = N <= 0, // current token followed by EOF?
        eol = false; // current token followed by EOL?

    // Strip the trailing newline.
    if (text.charCodeAt(N - 1) === NEWLINE) --N;
    if (text.charCodeAt(N - 1) === RETURN) --N;

    function token() {
      if (eof) return EOF;
      if (eol) return eol = false, EOL;

      // Unescape quotes.
      var i, j = I, c;
      if (text.charCodeAt(j) === QUOTE) {
        while (I++ < N && text.charCodeAt(I) !== QUOTE || text.charCodeAt(++I) === QUOTE);
        if ((i = I) >= N) eof = true;
        else if ((c = text.charCodeAt(I++)) === NEWLINE) eol = true;
        else if (c === RETURN) { eol = true; if (text.charCodeAt(I) === NEWLINE) ++I; }
        return text.slice(j + 1, i - 1).replace(/""/g, "\"");
      }

      // Find next delimiter or newline.
      while (I < N) {
        if ((c = text.charCodeAt(i = I++)) === NEWLINE) eol = true;
        else if (c === RETURN) { eol = true; if (text.charCodeAt(I) === NEWLINE) ++I; }
        else if (c !== DELIMITER) continue;
        return text.slice(j, i);
      }

      // Return last token before EOF.
      return eof = true, text.slice(j, N);
    }

    while ((t = token()) !== EOF) {
      var row = [];
      while (t !== EOL && t !== EOF) row.push(t), t = token();
      if (f && (row = f(row, n++)) == null) continue;
      rows.push(row);
    }

    return rows;
  }

  function preformatBody(rows, columns) {
    return rows.map(function(row) {
      return columns.map(function(column) {
        return formatValue(row[column]);
      }).join(delimiter);
    });
  }

  function format(rows, columns) {
    if (columns == null) columns = inferColumns(rows);
    return [columns.map(formatValue).join(delimiter)].concat(preformatBody(rows, columns)).join("\n");
  }

  function formatBody(rows, columns) {
    if (columns == null) columns = inferColumns(rows);
    return preformatBody(rows, columns).join("\n");
  }

  function formatRows(rows) {
    return rows.map(formatRow).join("\n");
  }

  function formatRow(row) {
    return row.map(formatValue).join(delimiter);
  }

  function formatValue(value) {
    return value == null ? ""
        : value instanceof Date ? formatDate(value)
        : reFormat.test(value += "") ? "\"" + value.replace(/"/g, "\"\"") + "\""
        : value;
  }

  return {
    parse: parse,
    parseRows: parseRows,
    format: format,
    formatBody: formatBody,
    formatRows: formatRows,
    formatRow: formatRow,
    formatValue: formatValue
  };
}


/***/ }),

/***/ "../../node_modules/d3-dsv/src/tsv.js":
/*!********************************************!*\
  !*** ../../node_modules/d3-dsv/src/tsv.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   tsvFormat: () => (/* binding */ tsvFormat),
/* harmony export */   tsvFormatBody: () => (/* binding */ tsvFormatBody),
/* harmony export */   tsvFormatRow: () => (/* binding */ tsvFormatRow),
/* harmony export */   tsvFormatRows: () => (/* binding */ tsvFormatRows),
/* harmony export */   tsvFormatValue: () => (/* binding */ tsvFormatValue),
/* harmony export */   tsvParse: () => (/* binding */ tsvParse),
/* harmony export */   tsvParseRows: () => (/* binding */ tsvParseRows)
/* harmony export */ });
/* harmony import */ var _dsv_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./dsv.js */ "../../node_modules/d3-dsv/src/dsv.js");


var tsv = (0,_dsv_js__WEBPACK_IMPORTED_MODULE_0__["default"])("\t");

var tsvParse = tsv.parse;
var tsvParseRows = tsv.parseRows;
var tsvFormat = tsv.format;
var tsvFormatBody = tsv.formatBody;
var tsvFormatRows = tsv.formatRows;
var tsvFormatRow = tsv.formatRow;
var tsvFormatValue = tsv.formatValue;


/***/ }),

/***/ "../../node_modules/d3-fetch/src/blob.js":
/*!***********************************************!*\
  !*** ../../node_modules/d3-fetch/src/blob.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
function responseBlob(response) {
  if (!response.ok) throw new Error(response.status + " " + response.statusText);
  return response.blob();
}

/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(input, init) {
  return fetch(input, init).then(responseBlob);
}


/***/ }),

/***/ "../../node_modules/d3-fetch/src/buffer.js":
/*!*************************************************!*\
  !*** ../../node_modules/d3-fetch/src/buffer.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
function responseArrayBuffer(response) {
  if (!response.ok) throw new Error(response.status + " " + response.statusText);
  return response.arrayBuffer();
}

/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(input, init) {
  return fetch(input, init).then(responseArrayBuffer);
}


/***/ }),

/***/ "../../node_modules/d3-fetch/src/dsv.js":
/*!**********************************************!*\
  !*** ../../node_modules/d3-fetch/src/dsv.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   csv: () => (/* binding */ csv),
/* harmony export */   "default": () => (/* binding */ dsv),
/* harmony export */   tsv: () => (/* binding */ tsv)
/* harmony export */ });
/* harmony import */ var d3_dsv__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! d3-dsv */ "../../node_modules/d3-dsv/src/dsv.js");
/* harmony import */ var d3_dsv__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! d3-dsv */ "../../node_modules/d3-dsv/src/csv.js");
/* harmony import */ var d3_dsv__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! d3-dsv */ "../../node_modules/d3-dsv/src/tsv.js");
/* harmony import */ var _text_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./text.js */ "../../node_modules/d3-fetch/src/text.js");



function dsvParse(parse) {
  return function(input, init, row) {
    if (arguments.length === 2 && typeof init === "function") row = init, init = undefined;
    return (0,_text_js__WEBPACK_IMPORTED_MODULE_0__["default"])(input, init).then(function(response) {
      return parse(response, row);
    });
  };
}

function dsv(delimiter, input, init, row) {
  if (arguments.length === 3 && typeof init === "function") row = init, init = undefined;
  var format = (0,d3_dsv__WEBPACK_IMPORTED_MODULE_1__["default"])(delimiter);
  return (0,_text_js__WEBPACK_IMPORTED_MODULE_0__["default"])(input, init).then(function(response) {
    return format.parse(response, row);
  });
}

var csv = dsvParse(d3_dsv__WEBPACK_IMPORTED_MODULE_2__.csvParse);
var tsv = dsvParse(d3_dsv__WEBPACK_IMPORTED_MODULE_3__.tsvParse);


/***/ }),

/***/ "../../node_modules/d3-fetch/src/image.js":
/*!************************************************!*\
  !*** ../../node_modules/d3-fetch/src/image.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(input, init) {
  return new Promise(function(resolve, reject) {
    var image = new Image;
    for (var key in init) image[key] = init[key];
    image.onerror = reject;
    image.onload = function() { resolve(image); };
    image.src = input;
  });
}


/***/ }),

/***/ "../../node_modules/d3-fetch/src/index.js":
/*!************************************************!*\
  !*** ../../node_modules/d3-fetch/src/index.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   blob: () => (/* reexport safe */ _blob_js__WEBPACK_IMPORTED_MODULE_0__["default"]),
/* harmony export */   buffer: () => (/* reexport safe */ _buffer_js__WEBPACK_IMPORTED_MODULE_1__["default"]),
/* harmony export */   csv: () => (/* reexport safe */ _dsv_js__WEBPACK_IMPORTED_MODULE_2__.csv),
/* harmony export */   dsv: () => (/* reexport safe */ _dsv_js__WEBPACK_IMPORTED_MODULE_2__["default"]),
/* harmony export */   html: () => (/* reexport safe */ _xml_js__WEBPACK_IMPORTED_MODULE_6__.html),
/* harmony export */   image: () => (/* reexport safe */ _image_js__WEBPACK_IMPORTED_MODULE_3__["default"]),
/* harmony export */   json: () => (/* reexport safe */ _json_js__WEBPACK_IMPORTED_MODULE_4__["default"]),
/* harmony export */   svg: () => (/* reexport safe */ _xml_js__WEBPACK_IMPORTED_MODULE_6__.svg),
/* harmony export */   text: () => (/* reexport safe */ _text_js__WEBPACK_IMPORTED_MODULE_5__["default"]),
/* harmony export */   tsv: () => (/* reexport safe */ _dsv_js__WEBPACK_IMPORTED_MODULE_2__.tsv),
/* harmony export */   xml: () => (/* reexport safe */ _xml_js__WEBPACK_IMPORTED_MODULE_6__["default"])
/* harmony export */ });
/* harmony import */ var _blob_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./blob.js */ "../../node_modules/d3-fetch/src/blob.js");
/* harmony import */ var _buffer_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./buffer.js */ "../../node_modules/d3-fetch/src/buffer.js");
/* harmony import */ var _dsv_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./dsv.js */ "../../node_modules/d3-fetch/src/dsv.js");
/* harmony import */ var _image_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./image.js */ "../../node_modules/d3-fetch/src/image.js");
/* harmony import */ var _json_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./json.js */ "../../node_modules/d3-fetch/src/json.js");
/* harmony import */ var _text_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./text.js */ "../../node_modules/d3-fetch/src/text.js");
/* harmony import */ var _xml_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./xml.js */ "../../node_modules/d3-fetch/src/xml.js");









/***/ }),

/***/ "../../node_modules/d3-fetch/src/json.js":
/*!***********************************************!*\
  !*** ../../node_modules/d3-fetch/src/json.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
function responseJson(response) {
  if (!response.ok) throw new Error(response.status + " " + response.statusText);
  if (response.status === 204 || response.status === 205) return;
  return response.json();
}

/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(input, init) {
  return fetch(input, init).then(responseJson);
}


/***/ }),

/***/ "../../node_modules/d3-fetch/src/text.js":
/*!***********************************************!*\
  !*** ../../node_modules/d3-fetch/src/text.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* export default binding */ __WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
function responseText(response) {
  if (!response.ok) throw new Error(response.status + " " + response.statusText);
  return response.text();
}

/* harmony default export */ function __WEBPACK_DEFAULT_EXPORT__(input, init) {
  return fetch(input, init).then(responseText);
}


/***/ }),

/***/ "../../node_modules/d3-fetch/src/xml.js":
/*!**********************************************!*\
  !*** ../../node_modules/d3-fetch/src/xml.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   html: () => (/* binding */ html),
/* harmony export */   svg: () => (/* binding */ svg)
/* harmony export */ });
/* harmony import */ var _text_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./text.js */ "../../node_modules/d3-fetch/src/text.js");


function parser(type) {
  return (input, init) => (0,_text_js__WEBPACK_IMPORTED_MODULE_0__["default"])(input, init)
    .then(text => (new DOMParser).parseFromString(text, type));
}

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (parser("application/xml"));

var html = parser("text/html");

var svg = parser("image/svg+xml");


/***/ }),

/***/ "../utils/lib/d3svg.js":
/*!*****************************!*\
  !*** ../utils/lib/d3svg.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.diagonal = diagonal;
/**
  * Create diagonal line between two nodes
  */
function diagonal(s, d) {
    if (s.dy == undefined) {
        s.dy = 0;
    }
    if (d.dy == undefined) {
        d.dy = 0;
    }
    let path = `M ${s.x} ${(s.y + s.dy)}
          C ${(s.x + d.x) / 2} ${(s.y + s.dy)},
            ${(s.x + d.x) / 2} ${(d.y + d.dy)},
            ${d.x} ${(d.y + d.dy)}`;
    return path;
}


/***/ }),

/***/ "../utils/lib/index.js":
/*!*****************************!*\
  !*** ../utils/lib/index.js ***!
  \*****************************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {


var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
__exportStar(__webpack_require__(/*! ./d3svg */ "../utils/lib/d3svg.js"), exports);
__exportStar(__webpack_require__(/*! ./random */ "../utils/lib/random.js"), exports);
__exportStar(__webpack_require__(/*! ./text */ "../utils/lib/text.js"), exports);
__exportStar(__webpack_require__(/*! ./web */ "../utils/lib/web.js"), exports);


/***/ }),

/***/ "../utils/lib/random.js":
/*!******************************!*\
  !*** ../utils/lib/random.js ***!
  \******************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.makeid = makeid;
function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}


/***/ }),

/***/ "../utils/lib/text.js":
/*!****************************!*\
  !*** ../utils/lib/text.js ***!
  \****************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.wrap = wrap;
const d3_selection_1 = __webpack_require__(/*! d3-selection */ "../../node_modules/d3-selection/src/index.js");
function wrap(text, width) {
    text.each(function () {
        var text = (0, d3_selection_1.select)(this), words = text.text().split(/(?=_)/).reverse(), word, line = [], lineNumber = 0, lineHeight = 1.1, // ems
        y = text.attr("y"), dy = parseFloat(text.attr("dy")), tspan = text.text(null).append("tspan").attr("x", 10).attr("y", y).attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(""));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(""));
                line = [word];
                tspan = text.append("tspan").attr("x", 10).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
            }
        }
    });
}


/***/ }),

/***/ "../utils/lib/web.js":
/*!***************************!*\
  !*** ../utils/lib/web.js ***!
  \***************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.json = json;
const d3_fetch_1 = __webpack_require__(/*! d3-fetch */ "../../node_modules/d3-fetch/src/index.js");
function json(innertext, sub, url, fn) {
    let i = document.createElement('i');
    i.classList.add("loading");
    i.classList.add("fa");
    i.classList.add("fa-spinner");
    i.classList.add("fa-pulse");
    sub.innerHTML = "";
    sub.appendChild(i);
    sub.onclick = function () {
        json(innertext, sub, url, fn);
    };
    (0, d3_fetch_1.json)(url).then(function (data) {
        sub.onclick = function () {
        };
        fn(data);
    }).catch(function (error) {
        i.classList.remove("fa-spinner");
        i.classList.remove("fa-pulse");
        i.classList.add("fa-refresh");
        i.classList.add("connection-error");
        let text = document.createElement('span');
        text.classList.add("error-text");
        text.innerHTML = innertext;
        i.appendChild(text);
    });
}


/***/ })

}]);
//# sourceMappingURL=utils_lib_index_js.38474bc682ec96a3df22.js.map