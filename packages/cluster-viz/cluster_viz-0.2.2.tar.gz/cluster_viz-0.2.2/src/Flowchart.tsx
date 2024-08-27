/* eslint-disable @typescript-eslint/naming-convention */
import React, { Component, createRef } from 'react';
import { ReactWidget } from '@jupyterlab/ui-components';
import * as d3 from 'd3';
import colorScheme from './colorScheme';
import { NotebookCellWithID } from './VizComponent';

interface Node {
  x: number;
  y: number;
}

interface ClassNode extends Node {
  id: string;
}

interface ClusterNode extends Node {
  id: number;
  cluster: string;
  class: string;
  cell_id: number;
  notebook_id: number;
}

interface ClassLink {
  source: string;
  target: string;
}

interface ClusterLink {
  source: ClusterNode;
  target: ClusterNode;
}


interface Props { }

interface State {
  selectedCells: NotebookCellWithID[];
}

// function resizeSVG(svgRef: React.RefObject<SVGSVGElement>): void {
//   const svg = svgRef.current;

//   if (svg) {
//     // Get the bounds of the SVG content
//     const bbox = svg.getBBox();
//     console.log(bbox);

//     const newWidth = bbox.x + bbox.width + bbox.x;
//     const newHeight = bbox.y + bbox.height + bbox.y;
//     // Update the width and height using the size of the contents
//     svg.setAttribute("width", newWidth.toString());
//     svg.setAttribute("height", newHeight.toString());

//     console.log('Resized SVG to', newWidth.toString(), newHeight.toString());
//   } else {
//     console.error("SVG element not found.");
//   }
// }

class Flowchart extends Component<Props, State> {
  svgRef: React.RefObject<SVGSVGElement>;

  constructor(props: Props) {
    super(props);
    this.svgRef = createRef();
    this.state = {
      selectedCells: [],
    };
  }

  componentDidUpdate(prevProps: Props, prevState: State) {
    if (prevState.selectedCells !== this.state.selectedCells) {
      this.drawChart();
    }
  }

  updateSelectedCells = (newSelectedCells: NotebookCellWithID[]) => {
    this.setState({ selectedCells: newSelectedCells });
  };


  drawClassChart = () => {
    const { selectedCells } = this.state;
    if (selectedCells.length === 0) {
      return { width: 0, height: 0 };
    }

    const svg = d3.select(this.svgRef.current)
      .attr('width', 300)
      .attr('height', 1000);

    svg.selectAll('*').remove(); // Clear existing graph

    // Extract unique classes from selected cells
    const classes = selectedCells.map(cell => cell.class);
    const nodes: ClassNode[] = [];
    const nodesSet = new Set<string>();
    const links: ClassLink[] = [];
    let nodeCounter = 0;

    for (let i = 0; i < classes.length; i++) {
      if (!nodesSet.has(classes[i])) {
        nodes.push({ id: classes[i], x: 100, y: 50 + (nodeCounter++) * 100 });
        nodesSet.add(classes[i]);
      }
      if (i < classes.length - 1 && classes[i] !== classes[i + 1]) {
        links.push({ source: classes[i], target: classes[i + 1] });
      }
    }

    const nodeWidth = 120;
    const nodeHeight = 50;

    svg.selectAll('rect')
      .data(nodes)
      .enter()
      .append('rect')
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('width', nodeWidth)
      .attr('height', nodeHeight)
      .attr('rx', 10)
      .attr('ry', 10)
      .attr('fill', d => colorScheme[d.id] || '#69b3a2'); // Replace with your color logic

    svg.selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .attr('x', d => d.x + nodeWidth / 2)
      .attr('y', d => d.y + nodeHeight / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .text(d => d.id);

    const lineGenerator = d3.line()
      .curve(d3.curveBundle.beta(0.5));

    svg.selectAll('path')
      .data(links)
      .enter()
      .append('path')
      .attr('d', d => {
        const source = nodes.find(node => node.id === d.source);
        const target = nodes.find(node => node.id === d.target);
        if (source && target) {
          const isDirectNeighbor = nodes.indexOf(source) === nodes.indexOf(target) - 1;
          const midX = (source.x + target.x) / 2;
          const midY = (source.y + target.y) / 2;
          const distanceY = Math.abs(target.y - source.y); // Calculate the vertical distance between nodes

          if (isDirectNeighbor) {
            // Draw the link on the left (curved leftwards)
            return lineGenerator([
              [source.x, source.y + nodeHeight / 2],
              [midX - nodeWidth / 2, midY + nodeHeight / 2],
              [target.x, target.y + nodeHeight / 2]
            ] as [number, number][]);
          } else {
            // Draw the link on the right (curved rightwards)
            return lineGenerator([
              [source.x + nodeWidth, source.y + nodeHeight / 2],
              [midX + nodeWidth + distanceY / 4, midY], // Shift control point rightwards
              [target.x + nodeWidth, target.y + nodeHeight / 2]
            ] as [number, number][]);
          }
        }
        return '';
      })
      .attr('stroke', '#999')
      .attr('fill', 'none');

    // Calculate the required width and height
    const width = 300;  // Fixed width
    const height = nodeCounter * 100 + 50;  // Based on number of nodes

    return { width, height };
  }


  drawClusterChart = () => {
    const { selectedCells } = this.state;
    if (selectedCells.length === 0) {
      return { width: 0, height: 0 };
    }

    const svg = d3.select(this.svgRef.current);

    svg.selectAll('*').remove(); // Clear existing graph

    const nodes: ClusterNode[] = [];
    const links: ClusterLink[] = [];
    const circleRadius = 15;  // Set the circle radius here
    const arrowheadSize = 6; // Adjust this to the size of the arrowhead
    let yCounter = 0;

    // Generate nodes, sorting by the order in colorScheme
    const classGroups = d3.group(selectedCells, d => d.class);

    classGroups.forEach((cells, cls) => {
      cells.sort((a, b) => {
        const colorOrderA = Object.keys(colorScheme).indexOf(a.cluster);
        const colorOrderB = Object.keys(colorScheme).indexOf(b.cluster);
        return colorOrderA - colorOrderB;
      });

      const clusterSet = new Set();  // Create a set to track unique clusters

      for (let i = 0; i < cells.length; i++) {

        if (!clusterSet.has(cells[i].cluster)) {
          clusterSet.add(cells[i].cluster);
          const node: ClusterNode = {
            id: nodes.length + 1,
            cluster: cells[i].cluster,
            class: cls,
            x: -50 + clusterSet.size * 150,  // Horizontally position nodes with the same class next to each other
            y: 100 + yCounter * 150,  // Vertically space classes
            cell_id: cells[i].cell_id,
            notebook_id: cells[i].notebook_id,  // Add notebook_id to the node
          };
          nodes.push(node);
        }
      }
      yCounter++;  // Move to the next row for the next class
    });

    // Create links between consecutive cells by cell_id and notebook_id
    selectedCells.forEach((cell, index) => {
      if (index < selectedCells.length - 1) {
        const sourceNode = nodes.find(node => node.cluster === cell.cluster);
        const targetCell = selectedCells[index + 1];
        const targetNode = nodes.find(node => node.cluster === targetCell.cluster && sourceNode?.cluster !== node.cluster && node.notebook_id === targetCell.notebook_id);

        // Only create a link if both nodes belong to the same notebook_id
        if (sourceNode && targetNode) {
          links.push({ source: sourceNode, target: targetNode });
        }
      }
    });

    // Draw circles (nodes)
    svg.selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', circleRadius)
      .attr('fill', d => colorScheme[d.class] || '#69b3a2');  // Use color scheme based on class

    // Draw text labels (cluster names)
    svg.selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', '#000')  // Set text color to black
      .style('font-size', '10px')  // Set font size to smaller
      .each(function (d) {
        const words = d.cluster.split(' ');  // Split cluster name into words
        let tspan = d3.select(this).append('tspan')
          .attr('x', d.x)
          .attr('y', d.y + circleRadius + 10)
          .attr('dy', -2);  // Start at the correct vertical position

        for (let i = 0; i < words.length; i += 3) {
          let line = words.slice(i, i + 3).join(' ');  // Take 3 words at a time
          tspan.text(line);
          if (i + 3 < words.length) {  // If more words remain, add a new line
            tspan = d3.select(this).append('tspan')
              .attr('x', d.x)
              .attr('dy', '1.0em')  // Adjust line height
              .attr('text-anchor', 'middle')  // Keep text centered
              .attr('dominant-baseline', 'middle');
          }
        }
      });



    // Draw dotted curved arrows (links between consecutive cells)
    svg.selectAll('path')
      .data(links)
      .enter()
      .append('path')
      .attr('d', d => {
        const source = d.source;
        const target = d.target;

        // Calculate the angle of the line
        const angle = Math.atan2(target.y - source.y, target.x - source.x);

        // Calculate the start and end points on the edge of the circles
        const sourceX = source.x + circleRadius * Math.cos(angle);
        const sourceY = source.y + circleRadius * Math.sin(angle);
        const targetX = target.x - (circleRadius + arrowheadSize) * Math.cos(angle);
        const targetY = target.y - (circleRadius + arrowheadSize) * Math.sin(angle);

        // Calculate the control point for the curve
        const midX = (sourceX + targetX) / 2;
        const midY = (sourceY + targetY) / 2;
        const curvature = 50;  // Adjust this value to control the curvature
        const controlPointX = midX;
        const controlPointY = sourceY < targetY ? midY - curvature : midY + curvature;

        return d3.line().curve(d3.curveBasis)([
          [sourceX, sourceY],
          [controlPointX, controlPointY],
          [targetX, targetY]
        ]);
      })
      .attr('stroke', '#666')
      .attr('fill', 'none')
      .attr('stroke-dasharray', '4 2')  // Create dotted line (4px dash, 2px gap)
      .attr('marker-end', 'url(#arrowhead)');

    // Define arrowhead marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', arrowheadSize)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', arrowheadSize)
      .attr('markerHeight', arrowheadSize)
      .attr('xoverflow', 'visible')
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
      .attr('fill', '#666')
      .style('stroke', 'none');

    const width = Math.max(...nodes.map(node => node.x)) + circleRadius * 2 + 50;  // Plus padding
    const height = yCounter * 150 + circleRadius * 2 + 50;  // Based on number of classes

    return { width, height };
  }

  drawChart() {
    const { selectedCells } = this.state;
    console.log('Drawing chart for selected cells', selectedCells);
    if (selectedCells.length === 0) {
      return;
    }

    let dimensions: { width: number, height: number };

    if (selectedCells.length > 100) {
      dimensions = this.drawClassChart();
    } else {
      dimensions = this.drawClusterChart();
    }

    const svg = this.svgRef.current;
    if (svg) {
      svg.setAttribute("width", dimensions.width.toString());
      svg.setAttribute("height", dimensions.height.toString());
    }
  }


  render() {
    return (
      <svg width="800" height="1000" ref={this.svgRef}></svg>
    );
  }
}

export class FlowchartWidget extends ReactWidget {
  graph: React.RefObject<Flowchart>;

  constructor() {
    super();
    // this.addClass('flowchart-widget');
    this.graph = createRef();
  }

  public updateGraph(selectedCells: NotebookCellWithID[]): void {
    this.graph.current?.updateSelectedCells(selectedCells);
  }

  render(): JSX.Element {
    return (
      <div className="flowchart-widget">
        <Flowchart ref={this.graph} />
      </div>
    );
  }
}
