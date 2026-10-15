// Quartier en 3D isométrique (style diorama low-poly) : projection, volumes ombrés, bâtiments,
// mobilier urbain, voitures et piétons.
// Repère monde : x vers la droite-bas, y vers la gauche-bas, z vers le haut (1 unité = K px).
const ISO = (() => {
  const K = 7.0, C = Math.cos(Math.PI / 6) * K, S = 0.5 * K, X0 = 400, Y0 = 310;
  const LEON_X = 15, MARCEL_X = 61;       // façades des deux garages (30 unités de large)
  const p = (x, y, z = 0) => [X0 + (x - y) * C, Y0 + (x + y) * S - z * K];
  const f1 = v => v.toFixed(1);
  const pts = a => a.map(([x, y, z]) => p(x, y, z).map(f1).join(',')).join(' ');
  const poly = (a, fill, extra = '') => `<polygon points="${pts(a)}" fill="${fill}" stroke="${fill}" stroke-width=".5" stroke-linejoin="round" ${extra}/>`;

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
  const yFace = (x0, yf, z0) => { const [ox, oy] = p(x0, yf, z0); return `matrix(${C},${S},0,${K},${f1(ox)},${f1(oy)})`; };
  // repère local d'une face droite (plan x = xf) : u le long de -y (lecture de gauche à droite)
  const xFace = (xf, y1, z0) => { const [ox, oy] = p(xf, y1, z0); return `matrix(${C},${-S},0,${K},${f1(ox)},${f1(oy)})`; };
  // rectangle sur une face : u de a à b, v de c à d
  const fr = (a, b, c, d, fill, extra = '') => `<rect x="${a}" y="${-d}" width="${(b - a).toFixed(2)}" height="${(d - c).toFixed(2)}" fill="${fill}" ${extra}/>`;
  // fenêtre avec cadre, reflet et appui
  const win = (a, b, c, d, glass = '#9CCBF2', frame = '#FFFFFF') =>
    fr(a - .2, b + .2, c - .2, d + .2, frame) + fr(a, b, c, d, glass)
    + `<polygon points="${a},${-c - (d - c) * .55} ${a + (b - a) * .45},${-d} ${a + (b - a) * .75},${-d} ${a},${-c - (d - c) * .1}" fill="#fff" opacity=".35"/>`
    + fr(a - .35, b + .35, c - .45, c - .2, shade(frame, -0.15));

  function disc(x, y, z, r, fill, n = 14, extra = '') {
    const a = Array.from({ length: n }, (_, i) => [x + r * Math.cos(i / n * Math.PI * 2), y + r * Math.sin(i / n * Math.PI * 2), z]);
    return poly(a, fill, extra);
  }

  // cône vu en iso : moitié gauche éclairée, moitié droite à l'ombre
  function cone(x, y, z, r, h, col) {
    const [ax, ay] = p(x, y, z + h);
    const arc = (a0, a1) => Array.from({ length: 7 }, (_, i) => { const a = a0 + (a1 - a0) * i / 6; return p(x + r * Math.cos(a), y + r * Math.sin(a), z); });
    const L = arc(Math.PI * .75, Math.PI * .25), R = arc(Math.PI * .25, -Math.PI * .25);
    const P2 = a => a.map(q => q.map(f1).join(',')).join(' ');
    return `<polygon points="${f1(ax)},${f1(ay)} ${P2(L)}" fill="${shade(col, 0.1)}"/><polygon points="${f1(ax)},${f1(ay)} ${P2(R)}" fill="${shade(col, -0.22)}"/>`;
  }

  function tree(x, y, s = 1, col = '#5FA36A') {
    let g = box(x - .4 * s, y - .4 * s, 0, .8 * s, .8 * s, 3 * s, '#8A6248');
    const blob = (cx, cy, cz, r, h) => {
      const top = [cx, cy, cz + h], bot = [cx, cy, cz - h * .7];
      const W = [cx - r, cy, cz], N = [cx, cy - r, cz], E = [cx + r, cy, cz], Sx = [cx, cy + r, cz];
      return poly([top, W, Sx], shade(col, 0.12)) + poly([top, Sx, E], shade(col, -0.18)) + poly([top, N, W], shade(col, 0.3)) + poly([top, E, N], shade(col, 0.04))
        + poly([bot, W, Sx], shade(col, -0.1)) + poly([bot, Sx, E], shade(col, -0.32));
    };
    g += blob(x, y, 6 * s, 3.2 * s, 3.4 * s) + blob(x + 1 * s, y + 1 * s, 8.4 * s, 2.2 * s, 2.4 * s);
    return g;
  }

  function pine(x, y, s = 1, col = '#3F7F5A') {
    let g = box(x - .35 * s, y - .35 * s, 0, .7 * s, .7 * s, 2.4 * s, '#7A5640');
    [[2.2, 3.4, 5.2], [5, 2.7, 4.4], [7.6, 1.9, 3.8]].forEach(([z, r, h]) => { g += cone(x, y, z * s, r * s, h * s, col); });
    return g;
  }

  // auvent rayé sur une façade avant (y = yf) entre u = a et u = b (x0 = origine de la façade)
  function awning(x0, a, b, yf, zt, cols, depth = 2.4) {
    let g = '';
    const n = Math.max(2, Math.round((b - a) / 1.2));
    for (let i = 0; i < n; i++) {
      const u0 = x0 + a + (b - a) * i / n, u1 = x0 + a + (b - a) * (i + 1) / n, c = cols[i % 2];
      g += poly([[u0, yf, zt], [u1, yf, zt], [u1, yf + depth, zt - 1.6], [u0, yf + depth, zt - 1.6]], shade(c, 0.08));
      g += poly([[u0, yf + depth, zt - 1.6], [u1, yf + depth, zt - 1.6], [u1, yf + depth, zt - 2.3], [u0, yf + depth, zt - 2.3]], shade(c, -0.05));
    }
    g += poly([[x0 + b, yf, zt], [x0 + b, yf + depth, zt - 1.6], [x0 + b, yf + depth, zt - 2.3], [x0 + b, yf, zt - .7]], shade(cols[0], -0.3));
    return g;
  }

  function waterTank(x, y, z) {
    let g = '';
    [[0, 0], [1.6, 0], [0, 1.6], [1.6, 1.6]].forEach(([a, b]) => { g += box(x + a, y + b, z, .25, .25, 2, '#6B5444'); });
    g += box(x - .1, y - .1, z + 2, 2, 2, 2.6, '#8C6A52', { top: '#A88468' });
    g += cone(x + .9, y + .9, z + 4.6, 1.5, 1.2, '#6E7A8C');
    return g;
  }

  // ---------------------------------------------------------------- bâtiments
  function garage(x0, name, wall, signGrad, id, open) {
    const y0 = 12, dx = 30, dy = 24, h = 19, yf = y0 + dy, xr = x0 + dx;
    let g = `<g id="${id}">`;
    g += box(x0, y0, 0, dx, dy, h, wall);
    g += box(x0, y0, h, dx, dy, .9, shade(wall, -0.06));
    g += box(x0 + 1, y0 + 1, h, dx - 2, dy - 2, .45, '#B7BDCB');
    g += box(x0 + 4, y0 + 3, h + .45, 5, 4, 2.4, '#DDE1EA') + box(x0 + 11, y0 + 3, h + .45, 3, 3, 1.6, '#C9CED9');
    g += box(x0 + 17, y0 + 11, h + .45, 8, 6, 1.2, '#9AA3BA', { top: '#5A6A9C' }) + box(x0 + 13, y0 + 15, h + .45, 1.2, 1.2, 3.4, '#C9CFDF');
    // façade avant
    g += `<g transform="${yFace(x0, yf, 0)}">`;
    g += fr(0, dx, 0, .8, shade(wall, -0.12));                                  // soubassement
    if (open) {
      g += fr(2.5, 17, 0, 11, '#252B44') + fr(2.5, 17, 0, 1.2, '#363D5C') + fr(4.5, 15, 9.4, 9.9, '#FFE7A0');
      g += fr(4.4, 5, 0, 7, '#F2C94C') + fr(14.5, 15.1, 0, 7, '#F2C94C') + fr(4.4, 15.1, 6.4, 7, '#F2C94C', 'opacity=".8"');
      g += fr(2.5, 17, 10, 11, '#C9D1E6') + fr(2.5, 17, 10, 10.25, '#AEB8D3');
    } else {
      g += fr(2.5, 17, 0, 11, '#C9D1E6') + Array.from({ length: 11 }, (_, i) => fr(2.5, 17, .5 + i * 1, .78 + i * 1, '#AEB8D3')).join('');
    }
    g += fr(2, 17.5, 11, 11.6, shade(wall, -0.3));
    g += fr(19, 23.5, 0, 8.5, '#8E9AC0') + fr(22.6, 23.1, 3.8, 4.6, '#F2F4FA') + fr(19.3, 23.2, 5.5, 8.2, '#BFE0FF', 'opacity=".55"');
    g += win(24.6, 28.2, 3, 9.2);
    g += `<rect x="2" y="-19" width="26" height="5.2" rx=".6" fill="url(#${signGrad})"/>`;
    g += `<text x="15" y="-15.4" text-anchor="middle" font-family="Poppins" font-weight="800" font-size="2.6" fill="#fff" letter-spacing=".08">${name}</text>`;
    g += `<g class="badgeSlot"></g></g>`;
    // façade droite
    g += `<g transform="${xFace(xr, yf, 0)}">${fr(0, dy, 0, .8, shade(wall, -0.3))}${[3, 9.5, 16].map(u => win(u, u + 4, 6, 10.5, '#86B6E0', shade(wall, -0.1))).join('')}</g>`;
    return g + '</g>';
  }

  // immeuble : grille de fenêtres sur les deux faces visibles, rez-de-chaussée commerçant en option
  function apartment(x0, y0, dx, dy, h, col, o = {}) {
    const yf = y0 + dy, xr = x0 + dx, floorH = o.floorH || 4.2, gf = o.shop ? 7 : 1.5;
    let g = box(x0, y0, 0, dx, dy, h, col);
    g += box(x0 - .2, y0 - .2, h, dx + .4, dy + .4, .8, shade(col, -0.1));
    if (o.roof !== false) {
      g += box(x0 + 1, y0 + 1, h + .8, Math.min(4, dx - 2), 3, 1.8, '#C9CED9');
      if (o.tank) g += waterTank(x0 + dx - 4.5, y0 + 1.5, h + .8);
    }
    const glass = o.glass || '#9CCBF2', frame = o.frame || '#FFFFFF';
    const rows = [];
    for (let z = gf + 1.2; z + 2.6 < h - .6; z += floorH) rows.push(z);
    const cols = (w, wW, gap) => { const n = Math.max(1, Math.floor((w - 1.2) / (wW + gap))); const pad = (w - n * wW - (n - 1) * gap) / 2; return Array.from({ length: n }, (_, i) => pad + i * (wW + gap)); };
    const wW = o.winW || 2.1, wH = o.winH || 2.6;
    let fa = `<g transform="${yFace(x0, yf, 0)}">`;
    rows.forEach((z, r) => { fa += fr(0, dx, z - 1.1, z - .95, shade(col, -0.08)); cols(dx, wW, 1.4).forEach(u => { fa += win(u, u + wW, z, z + wH, glass, frame); }); });
    if (o.shop) {
      fa += fr(0, dx, 0, 5.6, o.shop.wall || shade(col, -0.18));
      fa += win(.9, dx * .55, .6, 4, '#CFE7FF', o.shop.frame || '#2F3A5C') + fr(dx * .62, dx * .62 + 2.2, 0, 4.6, o.shop.door || '#2F3A5C');
      fa += fr(0, dx, 5.6, 7.6, o.shop.wall || shade(col, -0.18));
      if (o.shop.name) fa += `<rect x=".6" y="-7.5" width="${dx - 1.2}" height="1.4" rx=".2" fill="${o.shop.sign || '#2F3A5C'}"/><text x="${dx / 2}" y="-6.43" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="1" fill="#fff" letter-spacing=".05">${o.shop.name}</text>`;
    } else if (o.door !== false) {
      fa += fr(dx / 2 - 1.2, dx / 2 + 1.2, 0, 3.6, shade(col, -0.45)) + fr(dx / 2 - 1.6, dx / 2 + 1.6, 3.6, 4, shade(col, -0.25));
    }
    fa += '</g>';
    let fb = `<g transform="${xFace(xr, yf, 0)}">`;
    rows.forEach(z => { fb += fr(0, dy, z - 1.1, z - .95, shade(col, -0.3)); cols(dy, wW, 1.6).forEach(u => { fb += win(u, u + wW, z, z + wH, shade(glass, -0.12), shade(frame, -0.18)); }); });
    fb += '</g>';
    g += fa + fb;
    if (o.shop && o.shop.awning) g += awning(x0, .3, dx - .3, yf, 5.9, o.shop.awning);
    return g;
  }

  // maison à toit à deux pans (faîtage le long de x)
  function house(x0, y0, dx, dy, hw, hr, wall, roof) {
    const x1 = x0 + dx, y1 = y0 + dy, ym = y0 + dy / 2;
    let g = box(x0, y0, 0, dx, dy, hw, wall);
    g += poly([[x1, y0, hw], [x1, y1, hw], [x1, ym, hr]], shade(wall, -0.24));                 // pignon
    g += poly([[x0 - .4, ym, hr], [x1 + .4, ym, hr], [x1 + .4, y0 - .6, hw - .5], [x0 - .4, y0 - .6, hw - .5]], shade(roof, 0.12));
    g += box(x0 + 2, y0 + 3, hw, 1.4, 1.4, (hr - hw) + 2, '#B9876B');                           // cheminée
    g += poly([[x0 - .4, ym, hr], [x1 + .4, ym, hr], [x1 + .4, y1 + .8, hw - .6], [x0 - .4, y1 + .8, hw - .6]], roof);
    g += poly([[x1 + .4, ym, hr], [x1 + .4, y1 + .8, hw - .6], [x1 + .4, y1 + .8, hw - 1], [x1 + .4, ym, hr - .4]], shade(roof, -0.3));
    g += `<g transform="${yFace(x0, y1, 0)}">${fr(0, dx, 0, .7, shade(wall, -0.15))}${win(1.2, 4, 3, 6.6, '#9CCBF2', '#fff')}${fr(5.2, 7.6, 0, 5.6, '#6B4C3B')}${fr(7.2, 7.5, 2.6, 3, '#F2C94C')}${win(8.6, 10.2, 3, 6.6, '#9CCBF2', '#fff')}</g>`;
    g += `<g transform="${xFace(x1, y1, 0)}">${win(3, 6, 3, 6.6, '#86B6E0', '#E8E2D8')}${win(10, 13, 3, 6.6, '#86B6E0', '#E8E2D8')}${win(7.4, 9.6, 10.2, 12.4, '#86B6E0', '#E8E2D8')}</g>`;
    return g;
  }

  // ---------------------------------------------------------------- mobilier urbain
  const lamp = (x, y) => box(x - .2, y - .2, .6, .4, .4, 9.5, '#3A4160') + box(x - .2, y, 9.6, .4, 2.4, .35, '#3A4160') + box(x - .55, y + 1.7, 9.1, 1.1, 1.1, .5, '#FFE7A0', { top: '#3A4160' });
  const bench = (x, y) => box(x, y, .6, 3.4, .3, 1.5, '#7A5640') + box(x, y + .3, 1.2, 3.4, 1.1, .25, '#A5784F') + box(x + .2, y + .4, .6, .25, .8, .6, '#3A4160') + box(x + 2.95, y + .4, .6, .25, .8, .6, '#3A4160');
  const bin = (x, y) => box(x, y, .6, 1, 1, 1.6, '#4C8B6A');
  const hydrant = (x, y) => box(x, y, .6, .7, .7, 1.4, '#E04A3F') + box(x + .1, y + .1, 2, .5, .5, .35, '#B83A30');
  const umbrella = (x, y, cols) => box(x - .12, y - .12, .6, .24, .24, 4.4, '#ECEDF2') + box(x - .8, y - .8, .6, 1.6, 1.6, 1.8, '#FFFFFF', { top: '#F3F4F8' })
    + cone(x, y, 4.6, 2.2, 1, cols[0]) + box(x + 1.2, y - .3, .6, .8, .8, 1.2, '#7A5640');

  // ---------------------------------------------------------------- voitures et piétons
  function car(col, orient = 'x') {
    const L = 10, Wd = 4.6;
    const [dx, dy] = orient === 'x' ? [L, Wd] : [Wd, L];
    const x0 = -dx / 2, y0 = -dy / 2;
    let g = `<ellipse cx="${f1(p(0, 0, 0)[0])}" cy="${f1(p(0, 0, 0)[1] + 4)}" rx="${K * 6}" ry="${K * 2.4}" fill="#1B2240" opacity=".22"/>`;
    const wheel = (wx, wy) => orient === 'x'
      ? `<g transform="${yFace(wx, wy, 0)}"><circle cx="0" cy="-1" r="1.05" fill="#1E2236"/><circle cx="0" cy="-1" r=".45" fill="#C9CFDF"/></g>`
      : `<g transform="${xFace(wx, wy, 0)}"><circle cx="0" cy="-1" r="1.05" fill="#1E2236"/><circle cx="0" cy="-1" r=".45" fill="#C9CFDF"/></g>`;
    g += box(x0 + .3, y0 + .3, .35, dx - .6, dy - .6, .9, '#2A2F45');
    g += box(x0, y0, .9, dx, dy, 1.7, col);
    if (orient === 'x') g += wheel(x0 + 2.2, y0 + dy) + wheel(x0 + dx - 2.2, y0 + dy);
    else g += wheel(x0 + dx, y0 + dy - 2.2) + wheel(x0 + dx, y0 + 2.2);
    const [cx0, cy0, cdx, cdy] = orient === 'x' ? [x0 + 2.4, y0 + .45, 5, dy - .9] : [x0 + .45, y0 + 2.4, dx - .9, 5];
    g += box(cx0, cy0, 2.6, cdx, cdy, 1.6, '#BFE0FF', { top: shade(col, 0.15), left: '#9CCBF2', right: '#7FB2E0' });
    if (orient === 'x') g += `<g transform="${yFace(x0, y0 + dy, 0)}">${fr(.15, .9, 1.5, 2.2, '#FFF3B0')}${fr(dx - .9, dx - .15, 1.5, 2.2, '#FF6B6B')}</g>`;
    else g += `<g transform="${xFace(x0 + dx, y0 + dy, 0)}">${fr(.15, .9, 1.5, 2.2, '#FFF3B0')}${fr(dy - .9, dy - .15, 1.5, 2.2, '#FF6B6B')}</g>`;
    return g;
  }

  // piéton low-poly (coordonnées monde absolues) ; phase = cycle de marche, 0 = immobile
  function person(x, y, phase, o) {
    const sw = .55 * Math.sin(phase) * (o.walk ? 1 : 0), bob = o.walk ? .1 * Math.abs(Math.cos(phase)) : 0, d = o.dir || 1;
    const [sx, sy] = p(x, y, 0);
    let g = `<ellipse cx="${f1(sx)}" cy="${f1(sy)}" rx="${(K * 1.1).toFixed(1)}" ry="${(K * .55).toFixed(1)}" fill="#1B2240" opacity=".2"/>`;
    g += box(x - .22 - sw * d, y - .5, 0, .44, .44, 1.8 + bob, o.pants);               // jambe arrière
    g += box(x - .2 + sw * d * .8 * -1, y - .95, 2.1 + bob, .36, .36, 1.4, shade(o.shirt, -0.15)); // bras arrière
    g += box(x - .22 + sw * d, y + .06, 0, .44, .44, 1.8 + bob, shade(o.pants, 0.08));  // jambe avant
    g += box(x - .5, y - .62, 1.8 + bob, 1, 1.24, 1.75, o.shirt);                        // buste
    g += box(x - .2 + sw * d * .8, y + .62, 2.1 + bob, .36, .36, 1.4, o.shirt);          // bras avant
    const [hx, hy] = p(x, y, 4.15 + bob), r = (K * .62).toFixed(1);
    g += `<circle cx="${f1(hx)}" cy="${f1(hy)}" r="${r}" fill="${o.skin}"/>`;
    g += `<path d="M${f1(hx - K * .64)} ${f1(hy - K * .05)} A${(K * .64).toFixed(1)} ${(K * .64).toFixed(1)} 0 0 1 ${f1(hx + K * .64)} ${f1(hy - K * .05)} Q${f1(hx)} ${f1(hy - K * .32)} ${f1(hx - K * .64)} ${f1(hy - K * .05)} Z" fill="${o.hair}"/>`;
    return g;
  }

  // ---------------------------------------------------------------- la scène
  const XMAX = 106, YMAX = 62;
  // éléments posés au sol et triés en profondeur avec les voitures et les piétons
  const PROPS = [];
  const prop = (x, y, svg) => PROPS.push({ k: x + y, svg });

  function street() {
    let s = '';
    s += `<ellipse cx="${f1(p(53, 31, 0)[0])}" cy="${f1(p(53, 31, 0)[1] + 80)}" rx="620" ry="180" fill="#1B2240" opacity=".14" filter="url(#soft)"/>`;
    s += box(0, 0, -5, XMAX, YMAX, 5, '#D9DCE4', { left: '#A7ADC0', right: '#8F95AB' });
    s += box(0, 0, 0, XMAX, 12.5, .12, '#A9D49B');                                 // pelouse à l'arrière
    s += box(0, 36, 0, XMAX, 6, .6, '#ECE8E0', { left: '#CFC9BE' });                 // trottoir
    s += Array.from({ length: 18 }, (_, i) => poly([[i * 6, 36, .61], [i * 6 + .12, 36, .61], [i * 6 + .12, 42, .61], [i * 6, 42, .61]], '#D9D3C8')).join('');
    s += box(0, 42, 0, XMAX, 20, .25, '#5C6378', { left: '#4A5066' });              // chaussée
    s += Array.from({ length: 11 }, (_, i) => box(12 + i * 8.6, 51.6, .25, 4.2, .8, .02, '#F2C94C')).join('');
    s += Array.from({ length: 8 }, (_, i) => box(2.5, 43 + i * 2.3, .25, 6.5, 1.1, .02, '#F4F5F8')).join('');   // passage piéton
    s += disc(34, 50, .27, 1.3, '#4A5066') + disc(80, 57, .27, 1.3, '#4A5066');
    // rangée arrière : immeubles plus clairs (perspective atmosphérique)
    s += pine(1.8, 3, 1.1) + pine(1.5, 8.5, .9, '#4C8E66');
    s += apartment(4, 1, 14, 10, 34, '#E9DECB', { glass: '#BCD8F0', door: false, tank: true });
    s += apartment(20, 2, 13, 9, 42, '#B9CDE6', { glass: '#DCEBFA', frame: '#E8EEF8', door: false, winW: 2.4, floorH: 3.8 });
    s += apartment(35, 1, 14, 10, 30, '#EBC2B2', { glass: '#BCD8F0', door: false, tank: true });
    s += apartment(51, 2, 14, 9, 38, '#F1E0AE', { glass: '#BCD8F0', door: false });
    s += apartment(67, 1, 14, 10, 32, '#C9D6E0', { glass: '#DCEBFA', door: false, tank: true });
    s += apartment(83, 2, 16, 9, 26, '#DCCBD6', { glass: '#BCD8F0', door: false });
    s += pine(103, 4, 1.1) + tree(102.5, 9.5, .85, '#58996A');
    // rangée avant : maison, garage Léon, immeuble-boulangerie, garage Marcel, café
    s += house(2, 17, 11, 17, 10, 15.5, '#F3D9B1', '#C8664A');
    s += garage(LEON_X, 'GARAGE LÉON', '#F4EEE3', 'gBrand', 'gL', true);
    s += apartment(47, 14, 12, 20, 29, '#E9B949', { tank: true, shop: { name: 'BOULANGERIE', sign: '#8A4B2A', wall: '#F6E7CF', frame: '#8A4B2A', door: '#8A4B2A', awning: ['#E2574C', '#FFFFFF'] } });
    s += garage(MARCEL_X, 'GARAGE MARCEL', '#D88A5F', 'gWarm', 'gM', false);
    s += apartment(93, 18, 11, 16, 11, '#7FB7A4', { roof: false, shop: { name: 'CAFÉ', sign: '#2F5D50', wall: '#EAF4F0', frame: '#2F5D50', door: '#2F5D50', awning: ['#2F8F6B', '#FFFFFF'] } });
    // mobilier urbain (trié en profondeur avec les éléments animés)
    PROPS.length = 0;
    [14, 46, 60, 92].forEach(x => prop(x, 41.3, lamp(x, 41.3)));
    prop(8, 40.4, box(7, 39.4, .6, 2, 2, 1, '#B8BDC9') + tree(8, 40.4, .7, '#6BAF73'));
    prop(53, 40.4, box(52, 39.4, .6, 2, 2, 1, '#B8BDC9') + tree(53, 40.4, .7, '#64A86E'));
    prop(55, 37.2, bench(54.6, 36.9));
    prop(59.6, 37.4, bin(59.2, 36.9));
    prop(45.2, 40.6, hydrant(44.9, 40.3));
    prop(96, 37.6, umbrella(96, 37.6, ['#2F8F6B']));
    prop(101, 37.6, umbrella(101, 37.6, ['#E2574C']));
    prop(104.5, 40.6, box(104, 40.1, .6, 1, 1, 1.6, '#4C8B6A'));
    s += `<g id="dyn"></g>`;
    s += `<g id="tumble"><circle cx="0" cy="0" r="15" fill="none" stroke="#B08A5A" stroke-width="3" stroke-dasharray="9 6"/><circle cx="0" cy="0" r="9" fill="none" stroke="#C9A46E" stroke-width="2.5" stroke-dasharray="7 5"/><path d="M-11 -5 L9 7 M-7 10 L8 -10" stroke="#B08A5A" stroke-width="2.5"/></g>`;
    s += `<g id="zz" font-family="Poppins" font-weight="800" fill="#8A93B5"><text x="0" y="0" font-size="36">z</text><text x="24" y="-24" font-size="46">Z</text></g>`;
    return s;
  }

  return { K, p, box, car, person, tree, street, yFace, fr, shade, PROPS, LEON_X, MARCEL_X, XMAX };
})();
