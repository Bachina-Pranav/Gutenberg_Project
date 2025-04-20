// Build graph using vis‑network
const container = document.getElementById('network');
const data      = JSON.parse(document.getElementById('graph-data').textContent);

const network = new vis.Network(container, data, {
  nodes: {
    shape: 'dot', size: 14,
    font: { size: 14, face: 'Georgia' }
  },
  edges: {
    arrows: 'to',
    color: { color: '#999', highlight: '#555' }
  },
  physics: { hierarchicalRepulsion: { nodeDistance: 120 } },
  layout:  { hierarchical: { enabled: false } }
});

network.on('click', function (params) {
  if (params.nodes.length === 1) {
    const node = data.nodes.find(n => n.id === params.nodes[0]);
    if (node) window.location.href = `/post/${node.slug}`;
  }
}); 