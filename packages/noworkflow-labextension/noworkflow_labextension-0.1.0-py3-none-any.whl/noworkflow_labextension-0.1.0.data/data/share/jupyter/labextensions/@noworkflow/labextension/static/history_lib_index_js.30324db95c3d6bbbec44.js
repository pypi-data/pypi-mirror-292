"use strict";
(self["webpackChunk_noworkflow_labextension"] = self["webpackChunk_noworkflow_labextension"] || []).push([["history_lib_index_js"],{

/***/ "../history/lib/config.js":
/*!********************************!*\
  !*** ../history/lib/config.js ***!
  \********************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));


/***/ }),

/***/ "../history/lib/graph.js":
/*!*******************************!*\
  !*** ../history/lib/graph.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.HistoryGraph = void 0;
__webpack_require__(/*! d3-transition */ "../../node_modules/d3-transition/src/index.js");
const d3_color_1 = __webpack_require__(/*! d3-color */ "../../node_modules/d3-color/src/index.js");
const d3_scale_1 = __webpack_require__(/*! d3-scale */ "../../node_modules/d3-scale/src/index.js");
const d3_scale_chromatic_1 = __webpack_require__(/*! d3-scale-chromatic */ "../../node_modules/d3-scale-chromatic/src/index.js");
const d3_selection_1 = __webpack_require__(/*! d3-selection */ "../../node_modules/d3-selection/src/index.js");
const d3_zoom_1 = __webpack_require__(/*! d3-zoom */ "../../node_modules/d3-zoom/src/index.js");
const fs = __webpack_require__(/*! file-saver */ "../../node_modules/file-saver/dist/FileSaver.min.js");
class HistoryGraph {
    constructor(graphId, div, config = {}) {
        this.nodes = [];
        this.versionNodes = [];
        this.edges = [];
        this.maxX = 0;
        this.maxY = 0;
        this.maxId = 0;
        this.i = 0;
        var defaultConfig = {
            customSelectNode: (g, d) => false,
            customCtrlClick: (g, d) => false,
            customForm: (g, form) => null,
            customSize: (g) => [g.config.width, g.config.height],
            customWindowTabCommand: (trialIdSimplified, trialId, command) => false,
            hintMessage: "Ctrl+Shift click or ⌘+Shift click to diff trials",
            width: 200,
            height: 100,
            radius: 20,
            moveX: 20,
            moveY: 25,
            moveY2: 10,
            spacing: 17,
            margin: 50,
            fontSize: 10,
            useTooltip: false,
        };
        this.config = Object.assign({}, defaultConfig, config);
        this.graphId = graphId;
        this.zoom = (0, d3_zoom_1.zoom)()
            .on("zoom", (event) => {
            return this.zoomFunction(event);
        })
            .on("start", () => (0, d3_selection_1.select)('body').style("cursor", "move"))
            .on("end", () => (0, d3_selection_1.select)('body').style("cursor", "auto"))
            .wheelDelta(function () {
            const e = event;
            return -e.deltaY * (e.deltaMode ? 120 : 1) / 2000;
        });
        this.div = (0, d3_selection_1.select)(div);
        let form = (0, d3_selection_1.select)(div)
            .append("form")
            .classed("history-toolbar", true);
        this.svg = (0, d3_selection_1.select)(div)
            .append("div")
            .append("svg")
            .attr("width", this.config.width)
            .attr("height", this.config.height)
            .call(this.zoom)
            .on("mouseup", () => this.svgMouseUp());
        this.state = {
            selectedNode: null,
            mouseDownNode: null,
            justScale: false
        };
        // Tooltip
        this.tooltipDiv = (0, d3_selection_1.select)("body").append("div")
            .classed("now-tooltip now-history-tooltip", true)
            .style("opacity", 0)
            .style("max-width", "250px")
            .on("mouseout", () => {
            this.closeTooltip();
        });
        this.createToolbar(form);
        this.createMarker('end-arrow', 'endarrow', '#000');
        this.g = this.svg.append("g")
            .attr("id", this._graphId())
            .attr("transform", "translate(0,0)")
            .classed('HistoryGraph', true);
    }
    createToolbar(form) {
        let formdiv = form.append("div")
            .classed("buttons", true);
        this.config.customForm(this, formdiv);
        // Reset zoom
        formdiv.append("a")
            .classed("toollink", true)
            .attr("id", "history-" + this.graphId + "-history-zoom")
            .attr("href", "#")
            .attr("title", "Restore zoom")
            .on("click", () => this.restorePosition())
            .append("i")
            .classed("fa fa-eye", true);
        // Toggle Tooltips
        let tooltipsToggle = formdiv.append("input")
            .attr("id", "history-" + this.graphId + "-toolbar-tooltips")
            .attr("type", "checkbox")
            .attr("name", "history-toolbar-tooltips")
            .attr("value", "show")
            .property("checked", this.config.useTooltip)
            .on("change", () => {
            this.closeTooltip();
            this.config.useTooltip = tooltipsToggle.property("checked");
        });
        formdiv.append("label")
            .attr("for", "history-" + this.graphId + "-toolbar-tooltips")
            .attr("title", "Show tooltips on mouse hover")
            .append("i")
            .classed("fa fa-comment", true);
        // Download SVG
        formdiv.append("a")
            .classed("toollink", true)
            .attr("id", "history-" + this.graphId + "-download")
            .attr("href", "#")
            .attr("title", "Download graph SVG")
            .on("click", () => {
            this.download();
        })
            .append("i")
            .classed("fa fa-download", true);
        // Set Font Size
        let fontToggle = formdiv.append("input")
            .attr("id", "history-" + this.graphId + "-toolbar-fonts")
            .attr("type", "checkbox")
            .attr("name", "history-toolbar-fonts")
            .attr("value", "show")
            .property("checked", false)
            .on("change", () => {
            let display = fontToggle.property("checked") ? "inline-block" : "none";
            fontSize.style("display", display);
        });
        formdiv.append("label")
            .attr("for", "history-" + this.graphId + "-toolbar-fonts")
            .attr("title", "Set font size")
            .append("i")
            .classed("fa fa-font", true);
        let fontSize = formdiv.append("input")
            .attr("type", "number")
            .attr("value", this.config.fontSize)
            .style("width", "50px")
            .style("display", "none")
            .attr("title", "Node font size")
            .on("change", () => {
            this.config.fontSize = fontSize.property("value");
            this.svg.selectAll("text.trial-id")
                .attr("font-size", this.config.fontSize);
        });
        // Submit
        formdiv.append("input")
            .attr("type", "submit")
            .attr("name", "prevent-enter")
            .attr("onclick", "return false;")
            .style("display", "none");
        formdiv.append("div");
        formdiv.append("div")
            .text(this.config.hintMessage)
            .style('font-family', 'sans-serif')
            .style('font-size', '12px')
            .style('pointer-events', 'none');
    }
    load(data) {
        let nodes = [], otherNodes = [], edges = [], spacing = this.config.spacing, margin = this.config.margin;
        let spacing2 = 2 * spacing, spacing4 = 4 * spacing, start = margin, max = 0, id = 0, last = data.nodes.length - 1, tid = 0, useVersion = false;
        let levels = [];
        for (var i = 0; i <= last; i++) {
            let node = data.nodes[i];
            var previous = levels[node.level];
            if (previous == undefined) {
                previous = -1;
            }
            var trials = node.trials;
            if (trials == undefined) {
                trials = [];
            }
            levels[node.level] = Math.max(previous, trials.length);
        }
        let levelsy = [];
        var current = margin;
        for (var i = 0; i <= levels.length; i++) {
            levelsy[i] = current;
            current += spacing2 + levels[i] * spacing2;
        }
        for (var i = 0; i <= last; i++) {
            let node = data.nodes[i];
            let x = start + spacing4 * id;
            let y = levelsy[node.level];
            var new_node = {
                id: id,
                display: node.display,
                x: x,
                y: y,
                title: node.id.toString(),
                info: node,
                radius: this.config.radius,
                gradient: false,
                status: node.status
            };
            nodes.push(new_node);
            if (typeof (node.trials) != "undefined") {
                useVersion = true;
                for (var j = 0; j < node.trials.length; j++) {
                    let trialNode = node.trials[j];
                    let ny = y + (j + 1) * spacing2 + spacing;
                    otherNodes.push({
                        id: tid,
                        display: trialNode.display,
                        x: x + this.config.radius / 2,
                        y: ny,
                        title: trialNode.id.toString(),
                        info: trialNode,
                        tooltip: trialNode.tooltip,
                        radius: this.config.radius / 2,
                        gradient: true,
                        status: trialNode.status
                    });
                    tid += 1;
                    max = Math.max(max, y);
                }
            }
            else {
                new_node.tooltip = node.tooltip;
            }
            max = Math.max(max, y);
            this.maxX = x;
            id += 1;
        }
        max += spacing2;
        this.maxY = max;
        this.maxId = Math.max(tid, id);
        for (var i = 0; i < data.edges.length; i++) {
            let edge = Object.assign({}, data.edges[i]);
            edge.id = edge.source + "-" + edge.target;
            edge.source = nodes[edge.source];
            edge.target = nodes[edge.target];
            if (edge.source != edge.target) {
                edges.push(edge);
            }
        }
        if (useVersion) {
            this.nodes = otherNodes;
            this.versionNodes = nodes;
        }
        else {
            this.nodes = nodes;
            this.versionNodes = [];
        }
        this.edges = edges;
        this.updateWindow();
        this.restorePosition();
        this.update();
        this.menuOnRightClick();
        return nodes;
    }
    updateWindow() {
        let size = this.config.customSize(this);
        this.config.width = size[0];
        this.config.height = size[1];
        this.svg
            .attr("width", size[0])
            .attr("height", size[1]);
    }
    update() {
        var nodes = this.g.selectAll('g.node')
            .data(this.nodes, (d) => d.id);
        var edges = this.g.selectAll('g.link')
            .data(this.edges, (d) => d.id);
        var version = this.g.selectAll('g.version')
            .data(this.versionNodes, (d) => d.id);
        this.updateNodes(nodes);
        this.updateVersionNodes(version);
        this.updateLinks(edges);
    }
    restorePosition() {
        let scale = this.config.height / this.maxY;
        if (scale <= 1.0) {
            this.svg.call(this.zoom.transform, d3_zoom_1.zoomIdentity
                .translate(this.config.width
                - this.maxX * scale
                - this.config.margin, 0)
                .scale(scale));
        }
        else {
            this.svg.call(this.zoom.transform, d3_zoom_1.zoomIdentity
                .scale(1)
                .translate(this.config.width
                - this.maxX
                - this.config.margin, 0));
        }
        this.state.justScale = false;
    }
    selectNode(node) {
        this.state.selectedNode = node;
        this.config.customSelectNode(this, node);
        this.svg.selectAll('.node[attr-trial="' + node.title + '"] > rect')
            .attr('stroke', 'rgb(200, 238, 241)')
            .classed('selected', true);
    }
    selectTrial(trialId) {
        for (var node of this.nodes) {
            if (node.title == trialId) {
                this.selectNode(node);
                return;
            }
        }
    }
    download(name) {
        var isFileSaverSupported = false;
        try {
            isFileSaverSupported = !!new Blob();
        }
        catch (e) {
            alert("blob not supported");
        }
        name = (name === undefined) ? "history.svg" : name;
        let gnode = this.g.node();
        var bbox = gnode.getBBox();
        var width = this.svg.attr("width"), height = this.svg.attr("height");
        this.g.attr("transform", "translate(" + (-bbox.x + 5) + ", " + (-bbox.y + 5) + ")");
        let svgNode = this.svg
            .attr("title", "Trial")
            .attr("version", 1.1)
            .attr("width", bbox.width + 10)
            .attr("height", bbox.height + 10)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .node();
        var html = svgNode.parentNode.innerHTML;
        html = '<svg xmlns:xlink="http://www.w3.org/1999/xlink" ' + html.slice(4);
        this.svg
            .attr("width", width)
            .attr("height", height);
        this.g.attr("transform", this.transform);
        if (isFileSaverSupported) {
            var blob = new Blob([html], { type: "image/svg+xml" });
            fs.saveAs(blob, name);
        }
    }
    closeTooltip() {
        this.tooltipDiv.transition()
            .duration(500)
            .style("opacity", 0);
        this.tooltipDiv.classed("hidden", true);
    }
    showTooltip(event, d) {
        if (typeof (d.tooltip) == "undefined") {
            return;
        }
        this.tooltipDiv.classed("hidden", false);
        this.tooltipDiv.transition()
            .duration(200)
            .style("opacity", 0.9);
        this.tooltipDiv.html(d.tooltip)
            .style("left", (event.pageX - 3) + "px")
            .style("top", (event.pageY - 28) + "px");
    }
    createMarker(name, cls, fill) {
        this.svg.append("svg:defs").selectAll("marker")
            .data([name])
            .enter().append("svg:marker")
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 6)
            .attr("refY", 0)
            .attr("markerWidth", 3)
            .attr("markerHeight", 3)
            .attr("orient", "auto")
            .append("svg:path")
            .classed(cls, true)
            .attr("fill", fill)
            .attr("d", "M0,-5L10,0L0,5");
    }
    unselectNode() {
        this.g.selectAll('g.node').filter((cd) => {
            if (this.state.selectedNode == null) {
                return false;
            }
            return cd.id === this.state.selectedNode.id;
        }).select('rect')
            .classed('selected', false)
            .attr("stroke", "#000");
        this.state.selectedNode = null;
    }
    nodeMouseDown(event, d3node, d) {
        event.stopPropagation();
        this.state.mouseDownNode = d;
        this.closeTooltip();
    }
    nodeMouseUp(event, d3node, d) {
        event.stopPropagation();
        if (!this.state.mouseDownNode) {
            return;
        }
        if (this.state.justScale) {
            this.state.justScale = false;
        }
        else {
            if (event.ctrlKey || event.shiftKey || event.altKey) {
                this.config.customCtrlClick(this, d);
                return;
            }
            if (this.state.selectedNode) {
                this.unselectNode();
            }
            d3node
                .attr('stroke', 'rgb(200, 238, 241)')
                .classed('selected', true);
            this.state.selectedNode = d;
            this.config.customSelectNode(this, d);
        }
        this.state.mouseDownNode = null;
    }
    svgMouseUp() {
        if (this.state.justScale) {
            this.state.justScale = false;
        }
    }
    updateVersionNodes(nodes) {
        var nodeEnter = nodes.enter().append("g")
            .classed("version", true)
            .attr("attr-trialid", (d) => d.title)
            .attr("transform", (d) => {
            return "translate(" + 0 + "," + 0 + ")";
        });
        // Circle for new nodes
        nodeEnter.append('rect')
            .attr("transform", (d) => {
            return "translate(" + d.x + "," + d.y + ")";
        })
            .attr('width', (d) => 2 * d.radius)
            .attr('height', (d) => 2 * d.radius)
            .attr('rx', 0)
            .attr('ry', 0)
            //.attr('r', )
            .attr("stroke", "#000")
            .attr("stroke-width", "2.5px")
            .attr("fill", "#F6FBFF")
            .attr("stroke", "#000")
            .attr("stroke-width", "2.5px");
        nodeEnter.append('text')
            .classed('trial-id', true)
            .attr('font-family', 'sans-serif')
            .attr('font-size', this.config.fontSize + 'px')
            .attr('pointer-events', 'none')
            .attr('x', (d) => d.radius)
            .attr('y', (d) => d.radius + 4)
            .attr('stroke', '#000')
            .attr('text-anchor', 'middle')
            //.attr('font-weight', 'bold')
            .attr("transform", (d) => {
            return "translate(" + d.x + "," + d.y + ")";
        }).text((d) => d.display);
        nodeEnter.merge(nodes); // nodeUpdate
        nodes.exit().remove(); // nodeExit
    }
    updateNodes(nodes) {
        let self = this;
        var nodeEnter = nodes.enter().append("g")
            .classed("node", true)
            .attr("attr-trialid", (d) => d.title)
            .attr("cursor", "pointer")
            .attr("transform", (d) => {
            return "translate(" + 0 + "," + 0 + ")";
        });
        // Circle for new nodes
        nodeEnter.append('rect')
            .attr("transform", (d) => {
            return "translate(" + d.x + "," + d.y + ")";
        })
            .attr('cursor', 'pointer')
            .attr('title', (d) => d.info.display)
            .attr('width', (d) => 2 * d.radius)
            .attr('height', (d) => 2 * d.radius)
            .attr('rx', (d) => 2 * d.radius)
            .attr('ry', (d) => 2 * d.radius)
            //.attr('r', )
            .attr("stroke", "#000")
            .attr("stroke-width", "2.5px")
            .attr("fill", function (d) {
            var proportion = Math.round(200 * (1.0 - (parseInt(d.title) / self.maxId)) + 50);
            if (d.status === 'unfinished') {
                return d.gradient ? (0, d3_color_1.rgb)(255, proportion, proportion, 255).toString() : "rgb(238, 200, 241)";
            }
            if (d.status === 'finished') {
                return d.gradient ? (0, d3_color_1.rgb)(proportion, proportion, proportion, 255).toString() : "#F6FBFF";
            }
            if (d.status === 'backup') {
                return d.gradient ? (0, d3_color_1.rgb)(255, 255, proportion, 255).toString() : "rgb(241, 238, 200)";
            }
            return '#666';
        })
            .attr("stroke", function (d) {
            return ((0, d3_selection_1.select)(this).classed('selected')) ? 'rgb(200, 238, 241)' : "#000";
        })
            .attr("stroke-width", "2.5px")
            .on('mousedown', function (event, d) {
            self.nodeMouseDown(event, (0, d3_selection_1.select)(this), d);
        }).on('click', function (event, d) {
            self.nodeMouseUp(event, (0, d3_selection_1.select)(this), d);
        }).on('mouseover', function (event, d) {
            if (!self.state.mouseDownNode && self.config.useTooltip) {
                self.closeTooltip();
                self.showTooltip(event, d);
            }
            (0, d3_selection_1.select)(this)
                .attr('stroke', 'rgb(200, 238, 241)');
        }).on('mouseout', function (event, d) {
            (0, d3_selection_1.select)(this)
                .attr("stroke", (d) => {
                return ((0, d3_selection_1.select)(this).classed('selected')) ? 'rgb(200, 238, 241)' : "#000";
            });
        })
            .classed("custom-menu", true);
        nodeEnter.append('text')
            .classed('trial-id', true)
            .attr('font-family', 'sans-serif')
            .attr('font-size', this.config.fontSize + 'px')
            .attr('pointer-events', 'none')
            .attr('x', (d) => d.radius)
            .attr('y', (d) => d.radius + 4)
            .attr('stroke', '#000')
            .attr('text-anchor', 'middle')
            //.attr('font-weight', 'bold')
            .attr("transform", (d) => {
            return "translate(" + d.x + "," + d.y + ")";
        }).text((d) => d.gradient ? "" : d.display);
        nodeEnter.merge(nodes); // nodeUpdate
        nodes.exit().remove(); // nodeExit
    }
    updateLinks(link) {
        // Enter any new links
        let colors = (0, d3_scale_1.scaleOrdinal)(d3_scale_chromatic_1.schemeCategory10);
        var linkEnter = link.enter().insert('path', 'g')
            .classed('link', true)
            .attr('cursor', 'crosshair')
            .attr('fill', 'none')
            .attr('stroke', '#000')
            .attr('stroke-width', '4px');
        linkEnter
            .attr("d", (d) => {
            var deltaX = d.target.x - d.source.x, deltaY = d.target.y - d.source.y, dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY), normX = deltaX / dist, normY = deltaY / dist, sourcePadding = this.config.radius - 5, targetPadding = this.config.radius + (d.right ? 3 : -5), sourceX = d.source.x + this.config.radius + (sourcePadding * normX), sourceY = d.source.y + this.config.radius + (sourcePadding * normY), targetX = d.target.x + this.config.radius - (targetPadding * normX), targetY = d.target.y + this.config.radius - (targetPadding * normY);
            var step = 0;
            if (d.level > 0) {
                step += this.config.moveY;
                step += (d.level - 1) * this.config.moveY2;
            }
            return `M ${sourceX}, ${sourceY}
          C ${(sourceX - this.config.moveX / 2)} ${sourceY}
            ${(sourceX - this.config.moveX / 2)} ${(sourceY + 3 * step / 4)}
            ${(sourceX - this.config.moveX)} ${(sourceY + step)}
          L ${(sourceX - this.config.moveX)} ${(sourceY + step)}
            ${(targetX + this.config.moveX)} ${(sourceY + step)}
          C ${(targetX + this.config.moveX / 2)} ${(sourceY + 3 * step / 4)}
            ${(targetX + this.config.moveX / 2)} ${sourceY}
            ${targetX}, ${targetY}`;
        })
            .attr('marker-end', (d) => {
            return d.right ? 'url(#end-arrow)' : '';
        })
            .attr('stroke', (d) => {
            return (0, d3_color_1.rgb)(colors(d.level.toString())).darker().toString();
        });
        // Update
        linkEnter.merge(link); // linkUpdate
        // Remove any exiting links
        link.exit().remove(); // linkExit
    }
    zoomFunction(event) {
        this.state.justScale = true;
        this.closeTooltip();
        this.transform = event.transform;
        this.g.attr("transform", event.transform);
    }
    _graphId() {
        return "history-graph-" + this.graphId;
    }
    menuOnRightClick() {
        let rightClickMenu = document.getElementById("context-menu");
        // Set up an event handler for the documnt right click
        document.addEventListener("contextmenu", function (event) {
            var _a;
            //open right click menu
            let target = event.target;
            if (target && target.classList.contains("custom-menu")) {
                event.preventDefault();
                if (rightClickMenu) {
                    rightClickMenu.setAttribute("selected-trial", (_a = target.parentElement) === null || _a === void 0 ? void 0 : _a.getAttribute("attr-trialid"));
                    rightClickMenu.setAttribute("selected-trial-simplified", target.getAttribute("title"));
                    rightClickMenu.style.top = (event.pageY - 10).toString();
                    rightClickMenu.style.left = (event.pageX - 90).toString();
                    rightClickMenu.style.display = "block";
                    rightClickMenu.classList.add("show");
                }
            }
        });
        // close the menu
        document.addEventListener("click", function (event) {
            if (rightClickMenu) {
                rightClickMenu.style.display = "none";
                rightClickMenu.classList.remove("show");
            }
        });
    }
}
exports.HistoryGraph = HistoryGraph;


/***/ }),

/***/ "../history/lib/index.js":
/*!*******************************!*\
  !*** ../history/lib/index.js ***!
  \*******************************/
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
__exportStar(__webpack_require__(/*! ./config */ "../history/lib/config.js"), exports);
__exportStar(__webpack_require__(/*! ./structures */ "../history/lib/structures.js"), exports);
__exportStar(__webpack_require__(/*! ./graph */ "../history/lib/graph.js"), exports);


/***/ }),

/***/ "../history/lib/structures.js":
/*!************************************!*\
  !*** ../history/lib/structures.js ***!
  \************************************/
/***/ ((__unused_webpack_module, exports) => {


Object.defineProperty(exports, "__esModule", ({ value: true }));


/***/ })

}]);
//# sourceMappingURL=history_lib_index_js.30324db95c3d6bbbec44.js.map