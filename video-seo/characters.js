// Personnages "3D jouet" en SVG, découpés en groupes animables (tête, bras, bouche, yeux).
// character(opts) renvoie le markup SVG d'un personnage dans un repère 400 x 900 (sol à y = 882).

const SKIN = { base: '#F6CDB0', light: '#FFE3CF', dark: '#E2A988', blush: '#FF8F86' };

const HAIR_COLORS = {
  darkBrown: { base: '#3A2618', light: '#6E4B33', dark: '#1E130B' },
  lightBrown: { base: '#A8774C', light: '#D9AC7C', dark: '#73502F' },
};

let UID = 0;

function shade(hex, amt) { // amt > 0 éclaircit, < 0 assombrit
  const n = parseInt(hex.slice(1), 16);
  let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  const f = v => Math.round(amt > 0 ? v + (255 - v) * amt : v * (1 + amt));
  r = f(r); g = f(g); b = f(b);
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

// tube 3D : ombre, base, reflet
function tube(d, color, w, id) {
  return `<path d="${d}" stroke="${shade(color, -0.28)}" stroke-width="${w + 4}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="${d}" stroke="url(#${id})" stroke-width="${w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="${d}" stroke="${shade(color, 0.45)}" stroke-opacity=".35" stroke-width="${w * 0.28}" fill="none" stroke-linecap="round" stroke-linejoin="round" transform="translate(-${w * 0.18},-2)"/>`;
}

function lin(id, c1, c2, x2 = 1, y2 = 0) {
  return `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient>`;
}
function rad(id, c1, c2, cx = 0.38, cy = 0.32, r = 0.75) {
  return `<radialGradient id="${id}" cx="${cx}" cy="${cy}" r="${r}"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></radialGradient>`;
}

// ------------------------------------------------------------------ cheveux
function curlyHair(p, hc, style) {
  // style: 'tight' | 'volume' | 'fade'
  const big = style === 'volume' ? 1.25 : style === 'tight' ? 0.85 : 0.9;
  const R0 = style === 'volume' ? 98 : 86;
  const curls = [];
  const ring = (R, a0, a1, n, r, cy = 200) => {
    for (let i = 0; i < n; i++) {
      const a = (a0 + (a1 - a0) * i / (n - 1)) * Math.PI / 180;
      const jitter = ((i * 37) % 7 - 3);
      curls.push([200 + Math.cos(a) * R + jitter, cy + Math.sin(a) * R * 0.92 + ((i * 53) % 5 - 2), r * big * (0.9 + ((i * 29) % 5) / 20)]);
    }
  };
  const sideA0 = style === 'fade' ? 205 : 190, sideA1 = style === 'fade' ? 335 : 350;
  ring(R0, sideA0, sideA1, style === 'volume' ? 13 : 15, 24);
  ring(R0 - 24, 212, 328, 10, 22);
  ring(R0 - 46, 230, 310, 6, 20);
  // boucles sur le front
  const fr = style === 'volume' ? [[150, 140], [178, 128], [206, 132], [234, 126], [258, 142]] : [[156, 140], [184, 132], [214, 134], [244, 140]];
  fr.forEach(([x, y]) => curls.push([x, y + (style === 'volume' ? 4 : 0), 17 * big]));
  let s = '';
  // masse arrière
  const back = style === 'volume'
    ? `<ellipse cx="200" cy="158" rx="${R0 + 12}" ry="${R0 - 4}" fill="${hc.dark}"/>`
    : `<ellipse cx="200" cy="168" rx="${R0}" ry="${R0 - 18}" fill="${hc.dark}"/>`;
  if (style === 'fade') { // côtés dégradés courts
    s += `<path d="M124 150 Q118 200 128 236 L140 236 Q134 196 140 150 Z" fill="${hc.base}" opacity=".55"/>
          <path d="M276 150 Q282 200 272 236 L260 236 Q266 196 260 150 Z" fill="${hc.base}" opacity=".55"/>`;
  }
  curls.forEach(([x, y, r], i) => {
    s += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="url(#${p}curl)"/>`;
    s += `<path d="M${(x - r * 0.45).toFixed(1)} ${(y - r * 0.1).toFixed(1)} a${(r * 0.45).toFixed(1)} ${(r * 0.45).toFixed(1)} 0 1 1 ${(r * 0.55).toFixed(1)} ${(r * 0.4).toFixed(1)}" stroke="${hc.light}" stroke-opacity=".55" stroke-width="2.6" fill="none" stroke-linecap="round"/>`;
  });
  return { back, front: s, defs: rad(`${p}curl`, hc.light, hc.dark, 0.35, 0.3, 0.8) };
}

function wavyHair(p, hc, style) {
  // style: 'side' | 'middle' | 'quiff'
  const defs = lin(`${p}hair`, hc.light, hc.dark, 0.6, 1) + lin(`${p}hair2`, shade(hc.light, 0.1), hc.base, 0.3, 1);
  const back = `<path d="M118 222 C104 120 158 76 205 78 C258 80 298 122 282 222 C276 196 270 176 262 164 L138 164 C130 178 124 196 118 222 Z" fill="url(#${p}hair)"/>`;
  let front = '';
  const strand = d => `<path d="${d}" stroke="${hc.light}" stroke-opacity=".6" stroke-width="3" fill="none" stroke-linecap="round"/>`;
  const dstrand = d => `<path d="${d}" stroke="${hc.dark}" stroke-opacity=".45" stroke-width="2.5" fill="none" stroke-linecap="round"/>`;
  if (style === 'side') {
    front += `<path d="M126 176 C118 118 160 86 206 86 C250 86 286 112 282 168 C272 150 258 142 244 146 C250 158 248 170 240 178 C230 156 210 146 186 150 C170 152 156 160 148 172 C146 160 150 150 156 142 C142 148 132 160 126 176 Z" fill="url(#${p}hair2)"/>`;
    front += strand('M168 100 C200 92 240 98 262 122') + strand('M180 116 C210 110 236 120 248 140') + dstrand('M162 92 C156 110 156 126 166 140');
    front += dstrand('M212 136 C222 140 232 150 238 166');
    front += `<path d="M236 148 C252 150 262 164 258 184 C254 172 246 164 236 162 Z" fill="url(#${p}hair2)"/>`;
    front += `<path d="M150 158 C140 170 136 186 140 200 C128 186 130 166 140 154 Z" fill="url(#${p}hair2)"/>`;
  } else if (style === 'middle') {
    front += `<path d="M124 186 C114 118 158 84 200 86 C242 84 288 118 276 186 C270 166 262 154 250 148 C254 162 252 172 246 180 C238 156 222 140 202 130 C180 140 162 156 154 180 C148 172 146 162 150 148 C138 154 128 168 124 186 Z" fill="url(#${p}hair2)"/>`;
    front += strand('M196 94 C176 104 160 124 156 150') + strand('M206 94 C228 104 244 124 248 150') + dstrand('M200 92 L202 128');
    front += strand('M182 112 C170 126 166 140 168 156') + strand('M220 112 C232 126 236 140 234 156');
    front += `<path d="M154 172 C140 178 134 194 140 210 C126 196 128 176 140 164 Z" fill="url(#${p}hair2)"/>`;
    front += `<path d="M246 172 C260 178 266 194 260 210 C274 196 272 176 260 164 Z" fill="url(#${p}hair2)"/>`;
  } else { // quiff
    front += `<path d="M126 182 C114 112 150 62 208 58 C262 56 298 102 282 178 C276 158 266 146 252 140 C236 150 216 156 196 154 C174 152 156 156 144 166 C136 170 130 176 126 182 Z" fill="url(#${p}hair2)"/>`;
    front += `<path d="M146 160 C150 120 180 90 224 88 C246 88 262 96 272 108 C248 104 222 110 206 126 C190 136 166 144 146 160 Z" fill="${hc.light}" opacity=".35"/>`;
    front += strand('M156 150 C164 118 196 92 238 92') + strand('M178 146 C192 120 222 104 258 108') + strand('M206 148 C222 128 246 118 270 124');
    front += dstrand('M168 154 C178 132 200 114 226 108') + dstrand('M236 146 C248 136 262 132 276 136');
  }
  return { back, front, defs };
}

// ------------------------------------------------------------------ tenues
function outfit(p, o) {
  const defs = [];
  const g = (id, c) => { defs.push(lin(`${p}${id}`, shade(c, 0.12), shade(c, -0.18), 1, 0.2)); return `url(#${p}${id})`; };
  const top = g('top', o.top), pants = g('pants', o.pants);
  defs.push(lin(`${p}armTop`, shade(o.sleeve || o.top, 0.1), shade(o.sleeve || o.top, -0.1)));
  defs.push(lin(`${p}armSkin`, SKIN.light, SKIN.base));
  defs.push(rad(`${p}hand`, SKIN.light, SKIN.dark, 0.4, 0.35, 0.8));
  defs.push(rad(`${p}shoe`, shade(o.shoes, 0.25), shade(o.shoes, -0.25), 0.4, 0.3, 0.9));
  let legs = '', body = '', detail = '';
  // jambes
  legs += `<path d="M150 580 L198 580 L197 854 L152 854 Z" fill="${pants}"/>
           <path d="M202 580 L250 580 L248 854 L203 854 Z" fill="${pants}"/>
           <path d="M176 600 L175 850" stroke="${shade(o.pants, -0.25)}" stroke-opacity=".35" stroke-width="3"/>
           <path d="M226 600 L227 850" stroke="${shade(o.pants, -0.25)}" stroke-opacity=".35" stroke-width="3"/>
           <path d="M199 590 L199 700" stroke="${shade(o.pants, -0.4)}" stroke-opacity=".5" stroke-width="3"/>`;
  // chaussures
  const sneaker = o.shoeType === 'sneaker';
  legs += `<path d="M144 852 C144 842 202 842 202 852 L204 872 C204 884 140 886 140 872 Z" fill="url(#${p}shoe)"/>
           <path d="M198 852 C198 842 256 842 256 852 L260 872 C260 886 196 884 196 872 Z" fill="url(#${p}shoe)"/>`;
  if (sneaker) legs += `<path d="M140 874 C150 884 196 884 204 874 L204 878 C196 890 148 890 140 878 Z" fill="#E8EAF2"/>
           <path d="M196 874 C204 884 250 884 260 874 L260 878 C252 890 204 890 196 878 Z" fill="#E8EAF2"/>`;

  const torso = `M126 344 Q200 320 274 344 Q300 352 302 384 L304 604 Q304 618 290 618 L110 618 Q96 618 96 604 L98 384 Q100 352 126 344 Z`;
  if (o.type === 'suit' || o.type === 'blazer') {
    const inner = o.type === 'suit' ? (o.shirt || '#F4F6FB') : (o.tee || '#FFFFFF');
    body += `<path d="${torso}" fill="${top}"/>`;
    body += `<path d="M166 338 L234 338 L228 618 L172 618 Z" fill="${inner}"/>`;
    body += `<path d="M172 600 L228 600 L228 618 L172 618 Z" fill="${shade(inner, -0.08)}"/>`;
    if (o.type === 'suit') {
      body += `<rect x="172" y="566" width="56" height="16" fill="${o.belt || '#6B4228'}"/><rect x="192" y="565" width="16" height="18" rx="3" fill="none" stroke="#C9A55A" stroke-width="3"/>`;
      body += `<path d="M178 330 L200 352 L186 370 Z" fill="${inner}" stroke="${shade(inner, -0.15)}" stroke-width="1.5"/><path d="M222 330 L200 352 L214 370 Z" fill="${inner}" stroke="${shade(inner, -0.15)}" stroke-width="1.5"/>`;
      if (o.tie) body += `<path d="M195 352 L205 352 L210 364 L206 470 L200 482 L194 470 L190 364 Z" fill="${o.tie}"/>`;
      else [400, 450, 500].forEach(y => { body += `<circle cx="200" cy="${y}" r="3" fill="${shade(inner, -0.2)}"/>`; });
    } else {
      body += `<path d="M178 338 Q200 362 222 338" fill="none" stroke="${shade(inner, -0.15)}" stroke-width="3"/>`;
      if (o.teeLogo) body += `<g transform="translate(184 400) scale(.25)">${o.teeLogo}</g>`;
    }
    // revers
    body += `<path d="M166 338 L198 470 L180 618 L156 618 L150 360 Z" fill="${shade(o.top, -0.08)}"/>
             <path d="M234 338 L202 470 L220 618 L244 618 L250 360 Z" fill="${shade(o.top, -0.08)}"/>
             <path d="M166 338 L198 470 L178 410 L156 392 Z" fill="${shade(o.top, 0.15)}" opacity=".55"/>
             <path d="M234 338 L202 470 L222 410 L244 392 Z" fill="${shade(o.top, 0.15)}" opacity=".55"/>
             <path d="M262 420 L286 420" stroke="${shade(o.top, -0.3)}" stroke-width="3" stroke-linecap="round"/>`;
    if (o.pocketSquare) body += `<path d="M258 418 L268 404 L276 418 Z" fill="${o.pocketSquare}"/>`;
  } else if (o.type === 'overall') {
    body += `<path d="${torso}" fill="${top}"/>`;
    body += `<path d="M176 336 L200 360 L224 336 L236 344 L200 384 L164 344 Z" fill="${shade(o.top, -0.15)}"/>`;
    body += `<path d="M200 382 L200 618" stroke="${shade(o.top, -0.35)}" stroke-width="3"/><path d="M196 384 L204 384 L204 410 L196 410 Z" fill="#C8CDD8"/>`;
    body += `<rect x="96" y="470" width="208" height="14" fill="${o.stripe || '#F28C28'}"/><rect x="96" y="474" width="208" height="5" fill="#E9EEF5" opacity=".9"/>`;
    body += `<rect x="216" y="404" width="62" height="48" rx="6" fill="${shade(o.top, -0.1)}"/><path d="M216 414 L278 414" stroke="${shade(o.top, -0.3)}" stroke-width="2"/>`;
    body += `<rect x="226" y="372" width="44" height="22" rx="4" fill="#FFFFFF"/><text x="248" y="388" font-family="Poppins" font-weight="700" font-size="12" text-anchor="middle" fill="${o.top}">${o.patch || 'GARAGE'}</text>`;
    body += `<path d="M112 560 L140 560 L140 612 L112 612 Z" fill="#D9473C" opacity=".85"/>`; // chiffon
    body += `<rect x="96" y="564" width="208" height="14" fill="${shade(o.top, -0.2)}"/>`;
  } else if (o.type === 'hoodie') {
    body += `<path d="${torso}" fill="${top}"/>`;
    body += `<path d="M150 336 C160 372 240 372 250 336 C240 356 160 356 150 336 Z" fill="${shade(o.top, -0.2)}"/>`;
    body += `<path d="M140 338 C150 384 250 384 260 338" fill="none" stroke="${shade(o.top, 0.15)}" stroke-width="10" stroke-linecap="round"/>`;
    body += `<path d="M186 372 L184 432 M214 372 L216 432" stroke="#F2F2F2" stroke-width="4" stroke-linecap="round"/>`;
    body += `<path d="M146 506 L254 506 L268 580 L132 580 Z" fill="${shade(o.top, -0.08)}"/><path d="M146 506 L254 506" stroke="${shade(o.top, -0.25)}" stroke-width="3"/>`;
    body += `<rect x="96" y="596" width="208" height="22" rx="8" fill="${shade(o.top, -0.15)}"/>`;
    if (o.chestLogo) body += `<g transform="translate(220 410) scale(.28)">${o.chestLogo}</g>`;
  } else if (o.type === 'polo') {
    body += `<path d="${torso}" fill="${top}"/>`;
    body += `<path d="M168 330 L200 356 L232 330 L242 346 L206 374 L194 374 L158 346 Z" fill="${shade(o.top, 0.12)}"/>`;
    body += `<path d="M194 356 L206 356 L206 430 L194 430 Z" fill="${shade(o.top, -0.1)}"/><circle cx="200" cy="378" r="3" fill="#fff"/><circle cx="200" cy="404" r="3" fill="#fff"/>`;
    body += `<rect x="96" y="602" width="208" height="16" rx="6" fill="${shade(o.top, -0.15)}"/>`;
    if (o.chestLogo) body += `<g transform="translate(228 392) scale(.3)">${o.chestLogo}</g>`;
  }
  // ombre sous le menton
  body += `<path d="M168 332 Q200 356 232 332 Q200 346 168 332 Z" fill="#000" opacity=".12"/>`;
  return { legs, body, detail, defs: defs.join('') };
}

// ------------------------------------------------------------------ bras
function arms(p, o, pose) {
  const sleeveShort = o.type === 'polo';
  const c = o.sleeve || o.top;
  const L = { sh: [112, 362], el: [94, 470], ha: [100, 560] };
  const R = pose === 'thumb' ? { sh: [288, 362], el: [324, 468], ha: [352, 418] }
          : pose === 'wave' ? { sh: [288, 362], el: [330, 440], ha: [346, 330] }
          : pose === 'point' ? { sh: [288, 362], el: [330, 452], ha: [384, 420] }
          : { sh: [288, 362], el: [306, 470], ha: [300, 560] };
  const arm = (a, side) => {
    const up = `M${a.sh} L${a.el}`, fore = `M${a.el} L${a.ha}`;
    let s = '';
    if (sleeveShort) {
      const mid = [(a.sh[0] + a.el[0]) / 2, (a.sh[1] + a.el[1]) / 2];
      s += tube(`M${a.el} L${a.ha}`, SKIN.base, 30, `${p}armSkin`);
      s += tube(`M${mid} L${a.el}`, SKIN.base, 32, `${p}armSkin`);
      s += tube(`M${a.sh} L${mid}`, c, 46, `${p}armTop`);
    } else {
      s += tube(fore, c, 40, `${p}armTop`);
      s += tube(up, c, 44, `${p}armTop`);
      s += `<circle cx="${a.ha[0]}" cy="${a.ha[1]}" r="21" fill="${shade(c, -0.3)}"/>`; // poignet
    }
    // main
    const [hx, hy] = a.ha;
    if (side === 'R' && pose === 'thumb') {
      s += `<rect x="${hx - 7}" y="${hy - 42}" width="15" height="30" rx="7.5" fill="url(#${p}hand)"/>`;
      s += `<ellipse cx="${hx}" cy="${hy}" rx="20" ry="22" fill="url(#${p}hand)"/>`;
      s += `<path d="M${hx - 14} ${hy - 4} L${hx + 14} ${hy - 4} M${hx - 14} ${hy + 6} L${hx + 14} ${hy + 6}" stroke="${SKIN.dark}" stroke-width="2" stroke-linecap="round" opacity=".7"/>`;
    } else if (side === 'R' && pose === 'wave') {
      s += `<ellipse cx="${hx}" cy="${hy}" rx="21" ry="26" fill="url(#${p}hand)"/>`;
      [-12, -4, 4, 12].forEach((dx, i) => { s += `<rect x="${hx + dx - 4}" y="${hy - 44 + Math.abs(i - 1.5) * 3}" width="9" height="26" rx="4.5" fill="url(#${p}hand)"/>`; });
      s += `<rect x="${hx - 30}" y="${hy - 6}" width="22" height="10" rx="5" fill="url(#${p}hand)" transform="rotate(-30 ${hx - 20} ${hy})"/>`;
    } else if (side === 'R' && pose === 'point') {
      s += `<ellipse cx="${hx}" cy="${hy}" rx="20" ry="20" fill="url(#${p}hand)"/>`;
      s += `<rect x="${hx + 6}" y="${hy - 26}" width="11" height="30" rx="5.5" fill="url(#${p}hand)" transform="rotate(35 ${hx + 11} ${hy - 6})"/>`;
    } else {
      s += `<ellipse cx="${hx}" cy="${hy + 2}" rx="19" ry="22" fill="url(#${p}hand)"/>`;
    }
    if (o.prop && side === 'R' && pose !== 'thumb' && pose !== 'wave') s += o.prop(hx, hy);
    return s;
  };
  return { left: arm(L, 'L'), right: arm(R, 'R') };
}

// ------------------------------------------------------------------ tête
function head(p, opts) {
  const hc = HAIR_COLORS[opts.hairColor];
  const hair = opts.hair.startsWith('curly') ? curlyHair(p, hc, opts.hair.split('-')[1]) : wavyHair(p, hc, opts.hair.split('-')[1]);
  const defs = rad(`${p}face`, SKIN.light, SKIN.dark, 0.4, 0.35, 0.78) + lin(`${p}neck`, SKIN.dark, SKIN.base, 0, 1) + hair.defs;
  let s = '';
  s += `<rect x="182" y="290" width="36" height="56" rx="10" fill="url(#${p}neck)"/>`;
  s += hair.back;
  s += `<ellipse cx="127" cy="222" rx="14" ry="20" fill="${SKIN.base}"/><ellipse cx="129" cy="222" rx="7" ry="11" fill="${SKIN.dark}" opacity=".6"/>`;
  s += `<ellipse cx="273" cy="222" rx="14" ry="20" fill="${SKIN.base}"/><ellipse cx="271" cy="222" rx="7" ry="11" fill="${SKIN.dark}" opacity=".6"/>`;
  s += `<path d="M126 200 C126 140 160 114 200 114 C240 114 274 140 274 200 C274 258 244 302 200 302 C156 302 126 258 126 200 Z" fill="url(#${p}face)"/>`;
  if (opts.stubble) s += `<path d="M138 236 C146 290 176 302 200 302 C224 302 254 290 262 236 C252 270 232 284 200 284 C168 284 148 270 138 236 Z" fill="${hc.dark}" opacity=".18"/>`;
  // joues
  s += `<ellipse cx="160" cy="252" rx="14" ry="8" fill="${SKIN.blush}" opacity=".28"/><ellipse cx="240" cy="252" rx="14" ry="8" fill="${SKIN.blush}" opacity=".28"/>`;
  // yeux (groupe à cligner)
  s += `<g class="eyes" style="transform-box:fill-box;transform-origin:center">
    <ellipse cx="175" cy="212" rx="7.5" ry="10" fill="#2B1D16"/><ellipse cx="225" cy="212" rx="7.5" ry="10" fill="#2B1D16"/>
    <circle cx="177.5" cy="208" r="2.6" fill="#fff"/><circle cx="227.5" cy="208" r="2.6" fill="#fff"/></g>`;
  s += `<path d="M161 191 Q175 183 189 189" stroke="${hc.dark}" stroke-width="6" fill="none" stroke-linecap="round"/>
        <path d="M211 189 Q225 183 239 191" stroke="${hc.dark}" stroke-width="6" fill="none" stroke-linecap="round"/>`;
  // nez
  s += `<ellipse cx="200" cy="240" rx="9" ry="7" fill="${SKIN.dark}" opacity=".55"/><ellipse cx="198" cy="237" rx="4" ry="2.6" fill="#fff" opacity=".35"/>`;
  // bouches (visèmes) : une seule visible à la fois
  s += `<g class="mouth m-smile"><path d="M180 260 Q200 290 220 260 Q200 267 180 260 Z" fill="#7A2A2A"/><path d="M184 262 Q200 268 216 262 L214 267 Q200 271 186 267 Z" fill="#fff"/><ellipse cx="200" cy="278" rx="8" ry="4" fill="#E06A6A"/></g>`;
  s += `<g class="mouth m-closed" style="display:none"><path d="M184 264 Q200 274 216 264" stroke="#7A2A2A" stroke-width="4" fill="none" stroke-linecap="round"/></g>`;
  s += `<g class="mouth m-open" style="display:none"><ellipse cx="200" cy="270" rx="15" ry="13" fill="#7A2A2A"/><path d="M188 262 Q200 258 212 262 L211 266 Q200 263 189 266 Z" fill="#fff"/><ellipse cx="200" cy="278" rx="8" ry="4" fill="#E06A6A"/></g>`;
  s += `<g class="mouth m-o" style="display:none"><ellipse cx="200" cy="270" rx="9" ry="11" fill="#7A2A2A"/></g>`;
  s += hair.front;
  if (opts.glasses) s += `<g fill="none" stroke="#1E2233" stroke-width="4"><rect x="156" y="198" width="38" height="30" rx="12"/><rect x="206" y="198" width="38" height="30" rx="12"/><path d="M194 210 Q200 205 206 210"/></g>
    <rect x="160" y="202" width="14" height="6" rx="3" fill="#fff" opacity=".35"/><rect x="210" y="202" width="14" height="6" rx="3" fill="#fff" opacity=".35"/>`;
  if (opts.cap) s += opts.cap;
  return { s, defs };
}

function character(opts) {
  const p = `c${UID++}_`;
  const o = outfit(p, opts.outfit);
  const a = arms(p, opts.outfit, opts.pose || 'thumb');
  const h = head(p, opts);
  return `<svg viewBox="0 0 400 900" width="${opts.w || 400}" height="${(opts.w || 400) * 2.25}" style="overflow:visible">
  <defs>${o.defs}${h.defs}<filter id="${p}blur"><feGaussianBlur stdDeviation="6"/></filter></defs>
  <ellipse cx="200" cy="884" rx="120" ry="14" fill="#1B2240" opacity=".18" filter="url(#${p}blur)"/>
  <g class="legs">${o.legs}</g>
  <g class="body">${o.body}</g>
  <g class="armL">${a.left}</g>
  <g class="head" transform="translate(200 300) scale(1.22) translate(-200 -300)">${h.s}</g>
  <g class="armR">${a.right}</g>
  </svg>`;
}

const MINI_LOGO = `<rect x="57" y="19" width="69" height="67" rx="33" fill="#7E5CFF"/><rect x="30" y="7" width="65" height="79" rx="32" fill="#2E7BF6"/><rect x="6" y="32" width="58" height="54" rx="27" fill="#7FE6FF"/>`;
const WRENCH = (x, y) => `<g transform="translate(${x - 6} ${y - 70}) rotate(12)"><rect x="0" y="0" width="12" height="70" rx="6" fill="#B9C1CF"/><path d="M-10 -6 a16 16 0 1 1 32 0 l-8 0 l0 10 l-16 0 l0 -10 Z" fill="#B9C1CF"/></g>`;

if (typeof module !== 'undefined') module.exports = { character, MINI_LOGO, WRENCH, HAIR_COLORS, SKIN };
