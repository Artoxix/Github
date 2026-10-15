// Rue en 3D isométrique (style diorama low-poly) : projection, volumes ombrés, voitures, arbres.
// Repère monde : x vers la droite-bas, y vers la gauche-bas, z vers le haut (1 unité = K px).
const ISO = (() => {
  const K = 7.8, C = Math.cos(Math.PI / 6) * K, S = 0.5 * K, X0 = 452, Y0 = 240;
  const p = (x, y, z = 0) => [X0 + (x - y) * C, Y0 + (x + y) * S - z * K];
  const pts = a => a.map(([x, y, z]) => p(x, y, z).map(v => v.toFixed(1)).join(',')).join(' ');
  const poly = (a, fill, extra = '') => `<polygon points="${pts(a)}" fill="${fill}" stroke="${fill}" stroke-width=".6" stroke-linejoin="round" ${extra}/>`;

  function shade(hex, amt) {
    const n = parseInt(hex.slice(1), 16);
    const f = v => Math.round(amt > 0 ? v + (255 - v) * amt : v * (1 + amt));
    const r = f(n >> 16), g = f((n >> 8) & 255), b = f(n & 255);
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }

  // pavé : dessus éclairé, face avant-gauche (y max) en couleur de base, face avant-droite (x max) dans l'ombre
  function box(x0, y0, z0, dx, dy, dz, col, { top, left, right } = {}) {
    const x1 = x0 + dx, y1 = y0 + dy, z1 = z0 + dz;
    return poly([[x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0]], left || col)
      + poly([[x1, y0, z1], [x1, y1, z1], [x1, y1, z0], [x1, y0, z0]], right || shade(col, -0.24))
      + poly([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], top || shade(col, 0.2));
  }

  // repère local d'une face avant (plan y = yf) : u le long de x, v vers le haut
  const yFace = (x0, yf, z0) => { const [ox, oy] = p(x0, yf, z0); return `matrix(${C},${S},0,${K},${ox},${oy})`; };
  // repère local d'une face droite (plan x = xf) : u le long de -y (lecture de gauche à droite)
  const xFace = (xf, y1, z0) => { const [ox, oy] = p(xf, y1, z0); return `matrix(${C},${-S},0,${K},${ox},${oy})`; };
  // rectangle sur une face : u de a à b, v de c à d (v vers le haut → y local = -v)
  const fr = (a, b, c, d, fill, extra = '') => `<rect x="${a}" y="${-d}" width="${b - a}" height="${d - c}" fill="${fill}" ${extra}/>`;

  function tree(x, y, s = 1, col = '#5FA36A') {
    let g = box(x - .4 * s, y - .4 * s, 0, .8 * s, .8 * s, 3.2 * s, '#8A6248');
    // houppier facetté : octaèdre aplati vu en iso
    const cz = 3.2 * s + 3.4 * s, r = 3.4 * s, h = 3.6 * s;
    const top = [x, y, cz + h], bot = [x, y, cz - h * .7];
    const ring = [[x - r, y, cz], [x, y - r, cz], [x + r, y, cz], [x, y + r, cz]];
    const [W, N, E, Sx] = ring;
    g += poly([top, W, Sx], shade(col, 0.12)) + poly([top, Sx, E], shade(col, -0.18)) + poly([top, N, W], shade(col, 0.3)) + poly([top, E, N], shade(col, 0.05));
    g += poly([bot, W, Sx], shade(col, -0.12)) + poly([bot, Sx, E], shade(col, -0.35));
    return `<g>${g}</g>`;
  }

  // voiture isométrique : orientée le long de x ('x') ou de y ('y'), origine au centre au sol
  function car(col, orient = 'x') {
    const L = 10, Wd = 4.6;
    const [dx, dy] = orient === 'x' ? [L, Wd] : [Wd, L];
    const x0 = -dx / 2, y0 = -dy / 2;
    let g = `<ellipse cx="${p(0, 0, 0)[0]}" cy="${p(0, 0, 0)[1] + 4}" rx="${K * 6}" ry="${K * 2.4}" fill="#1B2240" opacity=".22"/>`;
    // roues (côté visible)
    const wheel = (wx, wy) => orient === 'x'
      ? `<g transform="${yFace(wx, wy, 0)}"><circle cx="0" cy="-1" r="1.05" fill="#1E2236"/><circle cx="0" cy="-1" r=".45" fill="#C9CFDF"/></g>`
      : `<g transform="${xFace(wx, wy, 0)}"><circle cx="0" cy="-1" r="1.05" fill="#1E2236"/><circle cx="0" cy="-1" r=".45" fill="#C9CFDF"/></g>`;
    g += box(x0 + .3, y0 + .3, .35, dx - .6, dy - .6, .9, '#2A2F45');
    g += box(x0, y0, .9, dx, dy, 1.7, col);
    if (orient === 'x') { g += wheel(x0 + 2.2, y0 + dy) + wheel(x0 + dx - 2.2, y0 + dy); }
    else { g += wheel(x0 + dx, y0 + dy - 2.2) + wheel(x0 + dx, y0 + 2.2); }
    // habitacle
    const [cx0, cy0, cdx, cdy] = orient === 'x' ? [x0 + 2.4, y0 + .45, 5, dy - .9] : [x0 + .45, y0 + 2.4, dx - .9, 5];
    g += box(cx0, cy0, 2.6, cdx, cdy, 1.6, '#BFE0FF', { top: shade(col, 0.15), left: '#9CCBF2', right: '#7FB2E0' });
    // phares / feux
    if (orient === 'x') g += `<g transform="${yFace(x0, y0 + dy, 0)}">${fr(.15, .9, 1.5, 2.2, '#FFF3B0')}${fr(dx - .9, dx - .15, 1.5, 2.2, '#FF6B6B')}</g>`;
    else g += `<g transform="${xFace(x0 + dx, y0 + dy, 0)}">${fr(.15, .9, 1.5, 2.2, '#FFF3B0')}${fr(dy - .9, dy - .15, 1.5, 2.2, '#FF6B6B')}</g>`;
    return g;
  }

  function garage(x0, name, wall, signGrad, id) {
    const y0 = 12, dx = 36, dy = 24, h = 20, yf = y0 + dy, xr = x0 + dx;
    let g = `<g id="${id}">`;
    g += box(x0, y0, 0, dx, dy, h, wall);
    // acrotère + toit
    g += box(x0, y0, h, dx, dy, .9, shade(wall, -0.06));
    g += box(x0 + 1, y0 + 1, h, dx - 2, dy - 2, .5, '#B7BDCB');
    g += box(x0 + 5, y0 + 4, h + .5, 6, 4, 2.6, '#DDE1EA') + box(x0 + 22, y0 + 12, h + .5, 8, 6, 1.4, '#9AA3BA', { top: '#5A6A9C' });
    g += box(x0 + 15, y0 + 5, h + .5, 1.4, 1.4, 4, '#C9CFDF');
    // façade avant
    g += `<g transform="${yFace(x0, yf, 0)}">`;
    g += fr(3, 21, 0, 12, '#C9D1E6') + Array.from({ length: 11 }, (_, i) => fr(3, 21, .6 + i * 1.05, .9 + i * 1.05, '#AEB8D3')).join('');
    g += `<rect class="door" x="3" y="-12" width="18" height="12" fill="#2A3150" opacity="0"/>`;
    g += fr(2.4, 21.6, 12, 12.6, shade(wall, -0.3));
    g += fr(24, 29, 0, 8.5, '#8E9AC0') + fr(28.2, 28.7, 3.8, 4.6, '#F2F4FA');
    g += fr(30, 34.5, 3, 9.5, '#BFE0FF') + fr(30, 34.5, 6.1, 6.4, '#fff', 'opacity=".6"');
    g += `<rect x="2.5" y="-19" width="31" height="5.4" rx=".6" fill="url(#${signGrad})"/>`;
    g += `<text x="18" y="-15" text-anchor="middle" font-family="Poppins" font-weight="800" font-size="3" fill="#fff" letter-spacing=".1">${name}</text>`;
    g += `<g class="badgeSlot"></g></g>`;
    // façade droite : fenêtres
    g += `<g transform="${xFace(xr, yf, 0)}">${[3, 9, 15].map(u => fr(u, u + 4, 8, 13, '#9CCBF2') + fr(u, u + 4, 14.5, 17, '#9CCBF2')).join('')}</g>`;
    return g + '</g>';
  }

  function street() {
    let s = '';
    // ombre du diorama + socle
    s += `<ellipse cx="${p(44, 31, 0)[0]}" cy="${p(44, 31, 0)[1] + 70}" rx="600" ry="170" fill="#1B2240" opacity=".14" filter="url(#soft)"/>`;
    s += box(0, 0, -5, 88, 62, 5, '#A9D49B', { left: '#7FA86F', right: '#6A9160' });
    // allée arrière (parking)
    s += box(6, 2, 0, 76, 9, .15, '#D9DCE3');
    s += box(0, 36, 0, 88, 6, .6, '#E6E2DA', { left: '#CFC9BE' });
    s += box(0, 42, 0, 88, 20, .25, '#5C6378', { left: '#4A5066' });
    s += Array.from({ length: 10 }, (_, i) => box(2.5 + i * 8.6, 51.6, .25, 4.2, .8, .02, '#F2C94C')).join('');
    // arbres arrière + bâtiments + arbres de l'allée
    s += tree(3, 5, 1) + tree(34, 3, .9, '#6BAF73') + tree(58, 4, 1.05, '#58996A') + tree(85, 8, .95);
    s += garage(5, 'GARAGE LÉON', '#F4EEE3', 'gBrand', 'gL');
    s += garage(47, 'GARAGE MARCEL', '#D88A5F', 'gWarm', 'gM');
    // lampadaires
    [[2, 39], [44, 39], [86, 39]].forEach(([x, y]) => { s += box(x - .25, y - .25, .6, .5, .5, 9, '#3A4160') + box(x - .6, y - .6, 9.6, 1.2, 1.2, .6, '#FFE7A0'); });
    s += `<g id="cars"></g>`;
    s += `<g id="tumble"><circle cx="0" cy="0" r="16" fill="none" stroke="#B08A5A" stroke-width="3" stroke-dasharray="9 6"/><circle cx="0" cy="0" r="10" fill="none" stroke="#C9A46E" stroke-width="2.5" stroke-dasharray="7 5"/><path d="M-12 -5 L10 7 M-7 11 L8 -11" stroke="#B08A5A" stroke-width="2.5"/></g>`;
    s += `<g id="zz" font-family="Poppins" font-weight="800" fill="#8A93B5"><text x="0" y="0" font-size="40">z</text><text x="26" y="-26" font-size="52">Z</text></g>`;
    return s;
  }

  return { K, p, box, car, tree, street, yFace, fr, shade };
})();
