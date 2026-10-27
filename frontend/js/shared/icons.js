// SVG de línea del prototipo de Figma (Feather). Se crean con createElementNS: nada de innerHTML.
const SVG_NS = 'http://www.w3.org/2000/svg';

const SHAPES = {
  home: [
    ['path', { d: 'M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z' }],
    ['polyline', { points: '9 22 9 12 15 12 15 22' }],
  ],
  users: [
    ['path', { d: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2' }],
    ['circle', { cx: 9, cy: 7, r: 4 }],
    ['path', { d: 'M23 21v-2a4 4 0 00-3-3.87' }],
    ['path', { d: 'M16 3.13a4 4 0 010 7.75' }],
  ],
  box: [
    [
      'path',
      {
        d: 'M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z',
      },
    ],
    ['polyline', { points: '3.27 6.96 12 12.01 20.73 6.96' }],
    ['line', { x1: 12, y1: 22.08, x2: 12, y2: 12 }],
  ],
  userCheck: [
    ['path', { d: 'M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2' }],
    ['circle', { cx: 8.5, cy: 7, r: 4 }],
    ['polyline', { points: '17 11 19 13 23 9' }],
  ],
  // No está en el prototipo: Feather "truck" para Proveedores (DESIGN.md §4)
  truck: [
    ['rect', { x: 1, y: 3, width: 15, height: 13 }],
    ['polygon', { points: '16 8 20 8 23 11 23 16 16 16 16 8' }],
    ['circle', { cx: 5.5, cy: 18.5, r: 2.5 }],
    ['circle', { cx: 18.5, cy: 18.5, r: 2.5 }],
  ],
  fileText: [
    ['path', { d: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z' }],
    ['polyline', { points: '14 2 14 8 20 8' }],
    ['line', { x1: 16, y1: 13, x2: 8, y2: 13 }],
    ['line', { x1: 16, y1: 17, x2: 8, y2: 17 }],
    ['polyline', { points: '10 9 9 9 8 9' }],
  ],
  creditCard: [
    ['rect', { x: 1, y: 4, width: 22, height: 16, rx: 2, ry: 2 }],
    ['line', { x1: 1, y1: 10, x2: 23, y2: 10 }],
  ],
  barChart: [
    ['line', { x1: 18, y1: 20, x2: 18, y2: 10 }],
    ['line', { x1: 12, y1: 20, x2: 12, y2: 4 }],
    ['line', { x1: 6, y1: 20, x2: 6, y2: 14 }],
  ],
  shield: [['path', { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z' }]],
  logOut: [
    ['path', { d: 'M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4' }],
    ['polyline', { points: '16 17 21 12 16 7' }],
    ['line', { x1: 21, y1: 12, x2: 9, y2: 12 }],
  ],
  bell: [
    ['path', { d: 'M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9' }],
    ['path', { d: 'M13.73 21a2 2 0 01-3.46 0' }],
  ],
};

export function icon(name, size = 18) {
  const svg = document.createElementNS(SVG_NS, 'svg');
  const attrs = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    'stroke-width': 2,
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'aria-hidden': 'true',
  };
  for (const [key, value] of Object.entries(attrs)) svg.setAttribute(key, value);
  for (const [tag, shapeAttrs] of SHAPES[name]) {
    const shape = document.createElementNS(SVG_NS, tag);
    for (const [key, value] of Object.entries(shapeAttrs)) shape.setAttribute(key, value);
    svg.append(shape);
  }
  return svg;
}
