// console.log("inside graph.js: ", location.origin);

const graphOriginalWidth = 1536 + 700, // this is the size of graph image on original screen.
  graphOriginalHeight = 731 + 700; // it will be used for scaling to our current screen size

const offsetBorderTop = $(window).width() * 0.03; // 3%
const offsetBorderLeft = $(window).width() * 0.06; // 6%

const nodesList = [
  [26, 371], // cam 1
  [318, 61], // cam 2
  [347, 435], // cam 3
  [238, 721], // cam 4
  [742, 603], // cam 5
  [724, 338], // cam 6
  [659, 100], // cam 7
  [883, 765], // cam 8
  [1243, 712], // cam 9
  [1034, 385], // cam 10
  [1016, 35], // cam 11
  [1402, 259], // cam 12
  [1490, 73], // cam 13
  [1755, 294], // cam 14
  [1422, 506], // cam 15
  [1661, 612], // cam 16
];

const edgesList = [
  [1, 2],
  [1, 3],
  [1, 4],
  [2, 3],
  [2, 7],
  [3, 4],
  [3, 5],
  [3, 6],
  [4, 5],
  [4, 8],
  [5, 10],
  [5, 9],
  [6, 7],
  [6, 10],
  [6, 11],
  [7, 11],
  [8, 9],
  [9, 15],
  [9, 16],
  [10, 12],
  [10, 15],
  [11, 12],
  [11, 13],
  [12, 13],
  [12, 15],
  [13, 14],
  [14, 15],
  [14, 16],
  [15, 16],
];

// var visitedNodesList = document.getElementById('vehiclePath').innerHTML;
// console.log(visitedNodesList);
var visitedNodes = []; // MUST be passed IN ORDER of visit

var timeStamp = [];

var visitedEdges = [];

var missedEdges = [];

function createNode(coordinate, index) {
  $("body").append(
    `<div id=C${index + 1} class="fa-stack graph-node fa-1.4rem">
          <i class="fas fa-circle fa-stack-2x"></i>
          <p class="fas fa-stack-1x">C${index + 1}</p>
        </div>`
  );
}

function updateNodeCoordinate(coordinate, index) {
  let x =
    (coordinate[0] * $(window).width()) / graphOriginalWidth + offsetBorderLeft;
  y =
    (coordinate[1] * $(window).height() * 1.38) / graphOriginalHeight +
    offsetBorderTop;
  let pos = $(".graph").offset();
  x += pos.left;
  y += pos.top;
  $(`#C${index + 1}`).offset({ top: y, left: x });
  // $(".graph").html($(".graph").html());
}

function createEdge(edge, index) {
  let n1_name = edge[0],
    n2_name = edge[1];
  $(".graph").append(
    `<line id="${n1_name}_${n2_name}" class="graph-edge" ></line>`
  );
  // $(".graph").html($(".graph").html());
}

function connectEdge(edge) {
  let node1 = `#C${edge[0]}`,
    node2 = `#C${edge[1]}`;

  let x1 = $(node1).offset().left + $(node1).width() / 2,
    y1 = $(node1).offset().top + $(node1).height() / 2,
    x2 = $(node2).offset().left + $(node2).width() / 2,
    y2 = $(node2).offset().top + $(node2).height() / 2;

  $(`#${edge[0]}_${edge[1]}`)
    .attr("x1", x1)
    .attr("y1", y1)
    .attr("x2", x2)
    .attr("y2", y2);
  // $(".graph").html($(".graph").html());
}

function createGraph() {
  /**
   * create bones and frames of graph.
   * This will create nodes and edges, and then
   * using promise, update the positions.
   * Call as: createGraph().then(updateGraph())
   */
  nodesList.forEach(createNode);
  edgesList.forEach(createEdge);
  return new Promise((myResolve) => {
    // myResolve();
    $("body").html($("body").html());
    setTimeout(myResolve, 100);
  });
}

function updateGraph() {
  /**
   * Graph must be created first.This function will
   * update graph positioning on events like screen-resize
   */
  nodesList.forEach(updateNodeCoordinate);
  edgesList.forEach(connectEdge);
  missedEdges.forEach(connectEdge);
  if (visitedNodes) {
    updateToolTip(visitedNodes[0], 0);
    updateToolTip(
      visitedNodes[visitedNodes.length - 1],
      visitedNodes.length - 1
    );
  }
  visitedNodes.forEach((node, index) => {
    updateToolTip(node, index, (onHover = true));
  });

  $("body").html($("body").html());

  visitedNodes.forEach((node, index) => {
    $(`#C${node}`).hover(
      () => {
        console.log(`mouse in: ${node}`);
        $(`.tooltip.tooltip-node-${node}.tooltip-time-${index}`).css(
          "visibility",
          "visible"
        );
      },
      () => {
        console.log(`mouse out: ${node}`);
        $(`.tooltip.tooltip-node-${node}.tooltip-time-${index}`).css(
          "visibility",
          "hidden"
        );
      }
    );
  });
}

function createMissedEdge(edge) {
  $(".graph").append(
    `<line id="${edge[0]}_${edge[1]}" class="graph-edge missed-edge" ></line>`
  );
  setTimeout(() => {
    connectEdge(edge);
  }, 10);
}

function addToolTip(node, label, index, onHover = false) {
  if (onHover) {
    $("body").append(
      `<div class="tooltip tooltip-node-${node} tooltip-time-${index}" style="visibility:hidden;">
      <span class="tooltiptext">${label}</span>
    </div>`
    );
  } else {
    $("body").append(
      `<div class="tooltip tooltip-node-${node}-${index}">
      <span class="tooltiptext">${label}</span>
    </div>`
    );
  }
}

function updateToolTip(node, index, onHover = false) {
  let pos = $(`#C${node}`).offset();
  let offX = 0,
    offY = 0,
    offset = 100,
    temp = index * 5;
  offY = Math.min(offset, temp);
  if (temp > offset) {
    offX = Math.floor(temp / offset) * 30;
  }

  if (onHover) {
    $(`.tooltip-node-${node}.tooltip-time-${index}`).offset({
      top: pos.top - offY,
      left: pos.left + offX,
    });
  } else {
    $(`.tooltip-node-${node}-${index}`).offset({
      top: pos.top + offY,
      left: pos.left + offX,
    });
  }
}

function markVisitedPath() {
  visitedNodes.forEach((node, index) => {
    $(`#C${node}`).addClass("visited-node");
    let str = $(`#C${node} p`).text() + "|" + (index + 1);
    // console.log(str);
    $(`#C${node} p`).text(str);
    $(`#C${node} p`).css({ "font-size": "0.8rem" });
    addToolTip(
      node,
      `@Time:&nbsp;${timeStamp[index]}`,
      (index = index),
      (onHover = true)
    );
  });
  visitedEdges.forEach((edge) => {
    let dir = edge[2];
    $(`#${edge[0]}_${edge[1]}`).addClass("visited-edge");
    if (dir) {
      // console.log("modifying edge: ", edge);
      $(`#${edge[0]}_${edge[1]}`).css({
        animation: "edgeReversed 5s linear infinite",
      });
    }
  });
  missedEdges.forEach(createMissedEdge);
  addToolTip(visitedNodes[0], "Start", 0);
  addToolTip(
    visitedNodes[visitedNodes.length - 1],
    "End",
    visitedNodes.length - 1
  );
  updateGraph();
}

function findEdges() {
  /**
   * This will find edges which are connected to nodes
   * If two nodes are directly connected by an edge, they
   * will be pushed in 'visitedEdges' global list. Otherwise
   * if there is no direct edge between them than it will
   * push them in 'missedEdges' global list.
   */
  function check(a, b) {
    /**
     * edges are defined in graph in only one way, howver they are
     * undirected. So, a third parameter is provided as direction while
     * coloring
     */
    for (let i = 0; i < edgesList.length; i++) {
      if (edgesList[i][0] === a && edgesList[i][1] === b) {
        return [a, b, 0]; // non-reverse
      }
      if (edgesList[i][0] === b && edgesList[i][1] === a) {
        return [b, a, 1]; // reverse-direction
      }
    }
    return null;
  }
  let a, b;
  for (let i = 0; i < visitedNodes.length - 1; i++) {
    a = visitedNodes[i];
    b = visitedNodes[i + 1];
    edge = check(a, b);
    if (edge) {
      visitedEdges.push(edge);
    } else {
      missedEdges.push([a, b]);
    }
  }
  return new Promise((myResolve) => {
    setTimeout(myResolve, 2000);
  });
}

/*************************************************
 *  This section is used to render the graph corectly on the screen.
 * It will make sure that the nodes-layer and the edges-layer sync up
 * correctly.
 */
$(document).ready(function () {
  createGraph().then(updateGraph);
});

$(window).resize(function () {
  updateGraph();
});

/************************************************
 * This section is used to find the traced path/edges and color them
 * First find traced path by "findEdges()" and then color the graph
 * using "markVisitedPath()" (this will internally call updateGraph()
 * in end to fix the "missedEdges")
 */

// findEdges().then(markVisitedPath);

function vehiclePathFromParent(vehiclePath, timeStampNodes) {
  visitedNodes = vehiclePath;
  timeStamp = timeStampNodes;
  // console.log(visitedNodes);
  // updateGraph();
  findEdges().then(markVisitedPath);
}
