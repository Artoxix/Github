/* Rig des personnages, style 1 « Rond & doux » (planche personnage Seomastertech).
 *
 * Max : le personnage de la planche (costume navy, cravate bleue), redessiné à l'identique
 *       en pièces articulées : corps, bras en deux morceaux (épaule, coude), tête.
 * Sam : la gérante, dessinée avec la même construction (grosse tête, grandes mains,
 *       aplats sans contour, dégradés, grain léger).
 *
 * Comme en stop motion, les visages sont des pièces de remplacement : yeux, sourcils et
 * bouches sont des formes distinctes qu'on échange image par image (Rig.apply).
 * Aucune dépendance : les scènes appellent Rig.svg(), Rig.attach() puis Rig.apply(pose).
 */
(function () {
  const mix = (a, b, t) => {
    const p = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
    const ca = p(a), cb = p(b);
    return '#' + ca.map((v, i) => Math.round(v + (cb[i] - v) * t).toString(16).padStart(2, '0')).join('');
  };

  // Couleurs reprises de la planche (style 1) ; dérivés calculés comme dans la planche.
  const PALETTES = {
    max: { skin: '#F47A54', hair: '#8E5B34' },
    sam: { skin: '#E3A27C', hair: '#4A2C1A' },
  };
  function tones(who) {
    const { skin, hair } = PALETTES[who];
    return {
      skin, hair,
      skinLow: mix(skin, '#B8281A', 0.3),
      ear: mix(skin, '#C8301E', 0.15),
      earLine: mix(skin, '#6A1408', 0.55),
      neck: mix(skin, '#A82416', 0.4),
      nose: mix(skin, '#B8281A', 0.4),
      noseHi: mix(skin, '#FFFFFF', 0.25),
      lip: mix(skin, '#9A2214', 0.45),
      blush: mix(skin, '#E8344A', 0.35),
      hairLine: mix(hair, '#2A1408', 0.3),
      brow: mix(hair, '#1A0C06', 0.6),
    };
  }

  // ------------------------------------------------------------------ pièces communes
  const HEAD_FACE = (c, u) => `
    <ellipse cx="160" cy="186" rx="9" ry="7.5" fill="${c.nose}"/>
    <circle cx="157" cy="183" r="2.2" fill="${c.noseHi}"/>
    <g data-p="blush" opacity="0">
      <ellipse cx="110" cy="190" rx="16" ry="8.5" fill="${c.blush}"/>
      <ellipse cx="210" cy="190" rx="16" ry="8.5" fill="${c.blush}"/>
    </g>
    <g data-p="browL"><rect x="104" y="124" width="40" height="8" rx="4" fill="${c.brow}"/></g>
    <g data-p="browR"><rect x="176" y="124" width="40" height="8" rx="4" fill="${c.brow}"/></g>
    <g data-p="eyes-open">
      <path d="M104 156 C110 144 142 144 148 154 C146 168 132 172 122 171 C112 170 104 164 104 156 Z M172 154 C178 144 210 144 216 156 C216 164 208 170 198 171 C188 172 174 168 172 154 Z" fill="#FFFFFF"/>
      <g data-p="pupils">
        <circle cx="127" cy="159" r="11" fill="#111111"/><circle cx="193" cy="159" r="11" fill="#111111"/>
        <circle cx="131" cy="155" r="3.5" fill="#FFFFFF"/><circle cx="197" cy="155" r="3.5" fill="#FFFFFF"/>
      </g>
      ${u.lashes ? `<path d="M104 155 L95 149 M105 160 L96 158 M216 155 L225 149 M215 160 L224 158" stroke="#2A1408" stroke-width="3.5" stroke-linecap="round" fill="none"/>` : ''}
    </g>
    <g data-p="eyes-wide" opacity="0">
      <circle cx="126" cy="154" r="18" fill="#FFFFFF"/><circle cx="194" cy="154" r="18" fill="#FFFFFF"/>
      <circle cx="126" cy="155" r="7.5" fill="#111111"/><circle cx="194" cy="155" r="7.5" fill="#111111"/>
      <circle cx="128.5" cy="152.5" r="2.5" fill="#FFFFFF"/><circle cx="196.5" cy="152.5" r="2.5" fill="#FFFFFF"/>
    </g>
    <path data-p="eyes-happy" opacity="0" d="M108 162 Q126 140 144 162 M176 162 Q194 140 212 162" stroke="#111111" stroke-width="5.5" fill="none" stroke-linecap="round"/>
    <path data-p="eyes-closed" opacity="0" d="M106 157 Q126 167 146 157 M174 157 Q194 167 214 157" stroke="#111111" stroke-width="5" fill="none" stroke-linecap="round"/>
    <g data-p="eyes-wink" opacity="0">
      <path d="M108 156 Q126 168 144 154" stroke="#111111" stroke-width="5.5" fill="none" stroke-linecap="round"/>
      <path d="M172 154 C178 144 210 144 216 156 C216 164 208 170 198 171 C188 172 174 168 172 154 Z" fill="#FFFFFF"/>
      <circle cx="193" cy="158" r="11" fill="#111111"/><circle cx="197" cy="154" r="3.5" fill="#FFFFFF"/>
    </g>
    <g data-p="m-neutral">
      <path d="M147 209 Q160 206 173 209" stroke="#7A2516" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="M151 214 Q160 223 169 214 Q160 217 151 214 Z" fill="${c.lip}"/>
    </g>
    <path data-p="m-smile" opacity="0" d="M138 204 Q160 226 182 204" stroke="#7A2516" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path data-p="m-smirk" opacity="0" d="M144 210 Q166 218 184 200" stroke="#7A2516" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path data-p="m-frown" opacity="0" d="M144 218 Q160 204 176 218" stroke="#7A2516" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path data-p="m-wavy" opacity="0" d="M146 214 Q154 207 162 212 Q170 217 178 208" stroke="#7A2516" stroke-width="3.5" fill="none" stroke-linecap="round"/>
    <ellipse data-p="m-o" opacity="0" cx="160" cy="214" rx="10" ry="13" fill="#6E1C10"/>
    <g data-p="m-1" opacity="0">
      <path d="M146 206 Q160 203 174 206 Q170 220 160 221 Q150 220 146 206 Z" fill="#6E1C10"/>
    </g>
    <g data-p="m-2" opacity="0">
      <path d="M140 202 L180 202 Q178 228 160 229 Q142 228 140 202 Z" fill="#6E1C10"/>
      <path d="M142 202 L178 202 L177 209 Q160 211 143 209 Z" fill="#FFFFFF"/>
    </g>
    <g data-p="m-3" opacity="0">
      <path d="M134 198 L186 198 Q184 236 160 238 Q136 236 134 198 Z" fill="#6E1C10"/>
      <path d="M136 198 L184 198 L183 207 Q160 210 137 207 Z" fill="#FFFFFF"/>
      <path d="M146 228 Q160 216 174 228 Q168 237 160 237 Q152 237 146 228 Z" fill="#E8604E"/>
    </g>`;

  // Bras en deux pièces : épaule → coude (upper), coude → main (fore). Côté gauche de l'image.
  function armMarkup(side, sleeve, cuffOrSkin, c, u, hold) {
    const flip = side === 'R' ? 'transform="translate(320 0) scale(-1 1)"' : '';
    const upper = u.shortSleeve
      ? `<path d="M74 266 C52 274 44 300 44 326 L43 346 L88 346 L86 300 Z" fill="${sleeve}"/>
         <path d="M44 312 L87 312 M44 330 L88 330" stroke="#2D3B6B" stroke-width="5" fill="none"/>
         <path d="M45 344 L86 344 L85 366 L45 366 Z" fill="url(#hand-${u.uid})"/>`
      : `<path d="M74 266 C50 274 44 306 44 336 L43 366 L85 366 L86 304 Z" fill="${sleeve}"/>`;
    const fore = u.shortSleeve
      ? `<circle cx="65" cy="356" r="20" fill="${c.skin}"/>
         <path d="M45 352 L85 352 L83 432 L44 432 Z" fill="url(#hand-${u.uid})"/>`
      : `<circle cx="64" cy="354" r="21" fill="${sleeve}"/>
         <path d="M43 350 L85 350 L82 428 L42 428 Z" fill="${sleeve}"/>
         <path d="M42 418 L82 418 L82 430 L42 430 Z" fill="${cuffOrSkin}"/>`;
    return `<g ${flip}><g data-p="arm${side}"><g data-p="up${side}">${upper}</g>
      <g data-p="fore${side}">${fore}
        <g data-p="hold${side}">${hold ? (side === 'R' ? `<g transform="translate(124 0) scale(-1 1)">${hold}</g>` : hold) : ''}</g>
        <path d="M42 430 L82 430 C88 446 86 470 70 478 C56 484 40 474 38 458 C37 448 39 438 42 430 Z" fill="url(#hand-${u.uid})"/>
        <path d="M52 462 C56 468 62 470 68 468 M48 452 C52 457 58 459 64 458" stroke="#3A160E" stroke-width="2" fill="none" stroke-linecap="round"/>
      </g></g></g>`;
  }

  function maxMarkup(c, u) {
    return `
    <g data-p="legs">
      <path d="M94 436 L157 436 L154 624 L104 624 Z" fill="#26335E"/>
      <path d="M163 436 L226 436 L216 624 L166 624 Z" fill="#26335E"/>
      <path d="M157 470 L163 470 L163 624 L157 624 Z" fill="#1B2547"/>
      <path d="M100 616 L156 616 L158 646 C158 652 154 655 148 655 L90 655 C80 655 78 645 84 637 C90 629 96 624 100 616 Z" fill="#1F1B24"/>
      <path d="M220 616 L164 616 L162 646 C162 652 166 655 172 655 L230 655 C240 655 242 645 236 637 C230 629 224 624 220 616 Z" fill="#1F1B24"/>
    </g>
    <g data-p="torso">
      <path d="M140 210 L180 210 L180 252 L140 252 Z" fill="${c.neck}"/>
      <path d="M66 296 C66 262 90 248 128 244 L192 244 C230 248 254 262 254 296 L248 444 C248 452 242 456 234 456 L86 456 C78 456 72 452 72 444 Z" fill="url(#jacket-${u.uid})"/>
      <path d="M130 244 L190 244 L160 344 Z" fill="#FFFFFF"/>
      <path d="M130 244 L160 258 L146 274 Z M190 244 L160 258 L174 274 Z" fill="#F1E9E9"/>
      <path d="M153 256 L167 256 L165 270 L155 270 Z" fill="#2457C2"/>
      <path d="M155 270 L165 270 L172 322 L160 340 L148 322 Z" fill="#2F6BDB"/>
      <path d="M128 244 L104 290 L122 296 L112 308 L158 346 Z M192 244 L216 290 L198 296 L208 308 L162 346 Z" fill="#222D55"/>
      <circle cx="160" cy="372" r="4.5" fill="#151C38"/><circle cx="160" cy="410" r="4.5" fill="#151C38"/>
      <path d="M100 404 L130 404 M190 404 L220 404" stroke="#1B2447" stroke-width="3" stroke-linecap="round"/>
    </g>
    ${armMarkup('L', '#2B3969', '#FFFFFF', c, u, u.holdL)}
    ${armMarkup('R', '#2B3969', '#FFFFFF', c, u, u.holdR)}
    <g data-p="head">
      <ellipse cx="78" cy="160" rx="17" ry="22" fill="${c.ear}"/>
      <ellipse cx="242" cy="160" rx="17" ry="22" fill="${c.ear}"/>
      <path d="M84 150 C74 152 72 166 82 172 M236 150 C246 152 248 166 238 172" stroke="${c.earLine}" stroke-width="2" fill="none" stroke-linecap="round"/>
      <ellipse cx="160" cy="150" rx="84" ry="82" fill="url(#skin-${u.uid})"/>
      <path d="M80 150 C72 118 80 92 96 78 C90 66 92 56 100 46 C106 58 112 64 120 66 C118 52 124 40 136 30 C138 44 142 54 148 60 C152 44 160 30 176 20 C172 36 172 48 176 58 C184 46 196 38 212 34 C204 46 202 56 204 66 C214 62 226 62 236 66 C228 72 226 78 228 86 C244 100 250 124 242 150 L234 146 C234 130 230 118 222 110 C208 104 196 100 182 106 C168 98 152 102 140 106 C126 100 112 104 100 110 C92 120 88 134 86 148 Z" fill="${c.hair}" stroke="${c.hair}" stroke-width="5" stroke-linejoin="round"/>
      <path d="M126 78 C134 68 142 64 150 64 M168 62 C176 54 186 50 196 50 M106 92 C112 84 118 80 126 78" stroke="${c.hairLine}" stroke-width="3" fill="none" stroke-linecap="round"/>
      ${HEAD_FACE(c, u)}
    </g>`;
  }

  function samMarkup(c, u) {
    return `
    <g data-p="legs">
      <path d="M94 436 L157 436 L154 618 L104 618 Z" fill="#33415A"/>
      <path d="M163 436 L226 436 L216 618 L166 618 Z" fill="#33415A"/>
      <path d="M157 466 L163 466 L163 618 L157 618 Z" fill="#26324A"/>
      <path d="M103 600 L155 600 L154 618 L104 618 Z M165 600 L217 600 L216 618 L166 618 Z" fill="#4A5A78"/>
      <path d="M102 612 L156 612 L158 640 C158 646 154 648 148 648 L90 648 C82 648 79 640 84 632 C90 624 96 618 102 612 Z" fill="#FFFFFF"/>
      <path d="M218 612 L164 612 L162 640 C162 646 166 648 172 648 L230 648 C238 648 241 640 236 632 C230 624 224 618 218 612 Z" fill="#FFFFFF"/>
      <path d="M80 640 L160 640 L160 650 C160 654 156 656 150 656 L88 656 C82 656 78 652 80 640 Z M240 640 L160 640 L160 650 C160 654 164 656 170 656 L232 656 C238 656 242 652 240 640 Z" fill="#E2D6D6"/>
    </g>
    <g data-p="torso">
      <path d="M140 210 L180 210 L180 258 L140 258 Z" fill="${c.neck}"/>
      <clipPath id="tee-${u.uid}"><path d="M70 292 C70 262 92 250 130 246 L190 246 C228 250 250 262 250 292 L244 444 C244 452 238 456 230 456 L90 456 C82 456 76 452 76 444 Z"/></clipPath>
      <g clip-path="url(#tee-${u.uid})">
        <rect x="60" y="240" width="200" height="220" fill="#FBFAF7"/>
        <path d="M60 272 H260 M60 302 H260 M60 332 H260 M60 362 H260 M60 392 H260 M60 422 H260 M60 452 H260" stroke="#2D3B6B" stroke-width="9"/>
      </g>
      <path d="M134 246 Q160 270 186 246 Z" fill="${c.neck}"/>
      <path d="M126 248 L140 236 M194 248 L180 236" stroke="#C98F1E" stroke-width="6" stroke-linecap="round"/>
      <path d="M118 262 L202 262 L206 300 L224 300 L230 452 C230 460 224 464 216 464 L104 464 C96 464 90 460 90 452 L96 300 L114 300 Z" fill="url(#apron-${u.uid})"/>
      <path d="M128 330 L192 330 L190 376 C190 382 186 384 180 384 L140 384 C134 384 130 382 130 376 Z" fill="#E9A92A"/>
      <path d="M160 330 L160 384" stroke="#C98F1E" stroke-width="3"/>
      <path d="M96 300 L224 300" stroke="#E9A92A" stroke-width="6"/>
    </g>
    ${armMarkup('L', '#FBFAF7', '', c, u, u.holdL)}
    ${armMarkup('R', '#FBFAF7', '', c, u, u.holdR)}
    <g data-p="head">
      <circle cx="160" cy="44" r="36" fill="${c.hair}"/>
      <path d="M128 70 Q160 60 192 70" stroke="#F0506E" stroke-width="10" fill="none" stroke-linecap="round"/>
      <path d="M70 160 C66 92 106 56 160 56 C214 56 254 92 250 160 C250 198 246 220 236 230 L84 230 C74 220 70 198 70 160 Z" fill="${c.hair}"/>
      <ellipse cx="160" cy="150" rx="84" ry="82" fill="url(#skin-${u.uid})"/>
      <path d="M78 152 C70 104 104 66 160 66 C216 66 250 104 242 152 C234 126 216 106 188 98 C172 114 140 122 108 120 C96 128 86 140 78 152 Z" fill="${c.hair}" stroke="${c.hair}" stroke-width="4" stroke-linejoin="round"/>
      <path d="M76 136 C70 168 72 202 84 226 L100 226 C90 200 88 170 92 140 Z M244 136 C250 168 248 202 236 226 L220 226 C230 200 232 170 228 140 Z" fill="${c.hair}"/>
      <path d="M122 84 C138 76 156 74 172 78 M196 88 C212 96 224 108 232 124" stroke="${c.hairLine}" stroke-width="3" fill="none" stroke-linecap="round"/>
      ${HEAD_FACE(c, u)}
    </g>`;
  }

  let uidN = 0;
  /** Le SVG complet d'un personnage. opts : { holdL, holdR } = SVG d'un accessoire tenu en main. */
  function svg(who, opts = {}) {
    const c = tones(who);
    const u = { uid: `${who}${++uidN}`, lashes: who === 'sam', shortSleeve: who === 'sam', ...opts };
    const body = who === 'max' ? maxMarkup(c, u) : samMarkup(c, u);
    return `<svg viewBox="0 10 320 664" width="320" height="664" overflow="visible" aria-hidden="true">
      <defs>
        <linearGradient id="skin-${u.uid}" gradientUnits="userSpaceOnUse" x1="0" y1="68" x2="0" y2="232"><stop offset="0.35" stop-color="${c.skin}"/><stop offset="1" stop-color="${c.skinLow}"/></linearGradient>
        <linearGradient id="hand-${u.uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c.skin}"/><stop offset="1" stop-color="${c.skinLow}"/></linearGradient>
        <linearGradient id="jacket-${u.uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34437A"/><stop offset="1" stop-color="#27335F"/></linearGradient>
        <linearGradient id="apron-${u.uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFC845"/><stop offset="1" stop-color="#F2B232"/></linearGradient>
        <filter id="grain-${u.uid}" filterUnits="userSpaceOnUse" x="-280" y="-260" width="880" height="1000"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.22 0" result="na"/><feComposite in="na" in2="SourceGraphic" operator="in" result="g"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="g"/></feMerge></filter>
      </defs>
      <ellipse data-p="shadow" cx="160" cy="660" rx="104" ry="11" fill="#0E1A4F" opacity="0.13"/>
      <g data-p="body" filter="url(#grain-${u.uid})">${body}</g>
    </svg>`;
  }

  function attach(root) {
    const h = {};
    root.querySelectorAll('[data-p]').forEach((el) => { h[el.getAttribute('data-p')] = el; });
    return h;
  }

  // ------------------------------------------------------------------ humeurs (pièces de remplacement)
  // eyes : open | wide | happy | closed | wink ; mouth (bouche fermée) ; brows : [dyL, rotL, dyR, rotR]
  const MOODS = {
    neutral:   { eyes: 'open',  mouth: 'neutral', brows: [0, 0, 0, 0],      blush: 0 },
    listen:    { eyes: 'open',  mouth: 'smile',   brows: [-2, 0, -2, 0],    blush: 0 },
    happy:     { eyes: 'open',  mouth: 'smile',   brows: [-6, -4, -6, 4],   blush: 0.7 },
    joy:       { eyes: 'happy', mouth: 'm-3',     brows: [-10, -6, -10, 6], blush: 0.9 },
    surprised: { eyes: 'wide',  mouth: 'o',       brows: [-15, 0, -15, 0],  blush: 0 },
    perplexed: { eyes: 'open',  mouth: 'wavy',    brows: [-11, -10, 3, 8],  blush: 0 },
    serious:   { eyes: 'open',  mouth: 'neutral', brows: [3, 6, 3, -6],     blush: 0 },
    sad:       { eyes: 'open',  mouth: 'frown',   brows: [-4, -14, -4, 14], blush: 0 },
    confident: { eyes: 'open',  mouth: 'smirk',   brows: [3, 2, -7, 6],     blush: 0.3 },
    wink:      { eyes: 'wink',  mouth: 'smirk',   brows: [3, 2, -7, 6],     blush: 0.5 },
    curious:   { eyes: 'open',  mouth: 'o',       brows: [-8, -4, -3, 4],   blush: 0 },
  };
  const EYES = ['open', 'wide', 'happy', 'closed', 'wink'];
  const MOUTHS = ['m-neutral', 'm-smile', 'm-smirk', 'm-frown', 'm-wavy', 'm-o', 'm-1', 'm-2', 'm-3'];

  const show = (el, on) => el && el.setAttribute('opacity', on ? 1 : 0);

  /** Pose une image. p : { lean, squash, dx, dy, head, headDy, arm:{L:[a,b],R:[a,b]},
   *  mood, talk (0-3), blink, look:[x,y] }. Angles en degrés, bras « vers l'extérieur » positifs. */
  function apply(h, p) {
    const mood = MOODS[p.mood || 'neutral'];
    const sq = p.squash || 1;
    h.body.setAttribute('transform',
      `translate(${p.dx || 0} ${p.dy || 0}) rotate(${p.lean || 0} 160 655) translate(160 655) scale(${1 / Math.sqrt(sq)} ${sq}) translate(-160 -655)`);
    h.shadow.setAttribute('transform', `translate(${p.dx || 0} 0)`);
    h.head.setAttribute('transform', `translate(0 ${p.headDy || 0}) rotate(${p.head || 0} 160 236)`);
    for (const s of ['L', 'R']) {
      const [a, b] = (p.arm && p.arm[s]) || [4, 0];
      const px = s === 'L' ? 66 : 66;   // le bras droit est un bras gauche retourné
      h['arm' + s].setAttribute('transform', `rotate(${a} ${px} 288)`);
      h['fore' + s].setAttribute('transform', `rotate(${b} 64 354)`);
      // l'objet tenu reste droit quel que soit l'angle du bras
      if (h['hold' + s]) h['hold' + s].setAttribute('transform', `rotate(${-(a + b)} 62 456)`);
    }
    // yeux
    let eyes = mood.eyes;
    if (p.blink && (eyes === 'open' || eyes === 'wide')) eyes = 'closed';
    EYES.forEach((e) => show(h['eyes-' + e], e === eyes));
    const [lx, ly] = p.look || [0, 0];
    h.pupils.setAttribute('transform', `translate(${lx} ${ly})`);
    // sourcils
    const [dyL, rL, dyR, rR] = mood.brows;
    h.browL.setAttribute('transform', `translate(0 ${dyL}) rotate(${rL} 124 128)`);
    h.browR.setAttribute('transform', `translate(0 ${dyR}) rotate(${rR} 196 128)`);
    h.blush.setAttribute('opacity', mood.blush);
    // bouche : parole (1-3) sinon la bouche de l'humeur
    let m = p.talk ? 'm-' + p.talk : (mood.mouth.startsWith('m-') ? mood.mouth : 'm-' + mood.mouth);
    MOUTHS.forEach((k) => show(h[k], k === m));
  }

  // ------------------------------------------------------------------ outils de minutage
  function prng(seed) {   // mulberry32
    return function () {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const back = (x) => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };

  /** Valeur d'une piste [[t, v, durée?], …] à l'instant t : chaque clé part de la précédente
   *  et l'atteint en `durée` s (0.25 par défaut) avec un dépassement léger (anticipation/settle). */
  function track(keys, t, def) {
    if (keys && keys.length && keys[0][0] <= 0) def = keys[0][1];   // une clé à 0 s est l'état de départ
    let from = def, to = def, k0 = 0, dur = 1;
    const at = (x) => lerp(from, to, back(Math.min(1, Math.max(0, (x - k0) / dur))));
    for (const [kt, v, d = 0.25] of keys || []) {
      if (t < kt) break;
      from = at(kt);
      to = v; k0 = kt; dur = d;
    }
    return at(t);
  }
  function lerp(a, b, x) {
    if (Array.isArray(a)) return a.map((v, i) => lerp(v, b[i], x));
    if (typeof a === 'object' && a) { const o = {}; for (const k in a) o[k] = lerp(a[k], b[k], x); return o; }
    return a + (b - a) * x;
  }
  /** Valeur discrète (humeur…) : la dernière clé passée. */
  function step(keys, t, def) {
    let v = def;
    for (const [kt, val] of keys) { if (t >= kt) v = val; else break; }
    return v;
  }

  /** Position de la main dans le repère du SVG (viewBox), pour un bras (a, b) donné. */
  function hand(side, a, b) {
    const rot = (x, y, cx, cy, d) => {
      const r = (d * Math.PI) / 180, c = Math.cos(r), s = Math.sin(r);
      return [cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c];
    };
    let [x, y] = rot(62, 456, 64, 354, b);
    [x, y] = rot(x, y, 66, 288, a);
    return side === 'R' ? [320 - x, y] : [x, y];
  }

  window.Rig = { svg, attach, apply, hand, track, step, prng, ease, mix, MOODS };
})();
