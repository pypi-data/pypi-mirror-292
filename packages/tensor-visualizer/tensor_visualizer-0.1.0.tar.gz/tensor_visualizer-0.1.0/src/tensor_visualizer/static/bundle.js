var ef = Object.defineProperty;
var tf = (e, n, t) => n in e ? ef(e, n, { enumerable: !0, configurable: !0, writable: !0, value: t }) : e[n] = t;
var pe = (e, n, t) => tf(e, typeof n != "symbol" ? n + "" : n, t);
/*! pako 2.1.0 https://github.com/nodeca/pako @license (MIT AND Zlib) */
function _t(e) {
  let n = e.length;
  for (; --n >= 0; )
    e[n] = 0;
}
const nf = 0, el = 1, af = 2, lf = 3, ff = 258, ni = 29, Ht = 256, St = Ht + 1 + ni, it = 30, ii = 19, tl = 2 * St + 1, Oe = 15, wn = 16, rf = 7, ai = 256, nl = 16, il = 17, al = 18, $n = (
  /* extra bits for each length code */
  new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0])
), en = (
  /* extra bits for each distance code */
  new Uint8Array([0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13])
), of = (
  /* extra bits for each bit length code */
  new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 7])
), ll = new Uint8Array([16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]), sf = 512, ze = new Array((St + 2) * 2);
_t(ze);
const kt = new Array(it * 2);
_t(kt);
const zt = new Array(sf);
_t(zt);
const Nt = new Array(ff - lf + 1);
_t(Nt);
const li = new Array(ni);
_t(li);
const an = new Array(it);
_t(an);
function xn(e, n, t, i, a) {
  this.static_tree = e, this.extra_bits = n, this.extra_base = t, this.elems = i, this.max_length = a, this.has_stree = e && e.length;
}
let fl, rl, ol;
function vn(e, n) {
  this.dyn_tree = e, this.max_code = 0, this.stat_desc = n;
}
const sl = (e) => e < 256 ? zt[e] : zt[256 + (e >>> 7)], Rt = (e, n) => {
  e.pending_buf[e.pending++] = n & 255, e.pending_buf[e.pending++] = n >>> 8 & 255;
}, ne = (e, n, t) => {
  e.bi_valid > wn - t ? (e.bi_buf |= n << e.bi_valid & 65535, Rt(e, e.bi_buf), e.bi_buf = n >> wn - e.bi_valid, e.bi_valid += t - wn) : (e.bi_buf |= n << e.bi_valid & 65535, e.bi_valid += t);
}, ve = (e, n, t) => {
  ne(
    e,
    t[n * 2],
    t[n * 2 + 1]
    /*.Len*/
  );
}, cl = (e, n) => {
  let t = 0;
  do
    t |= e & 1, e >>>= 1, t <<= 1;
  while (--n > 0);
  return t >>> 1;
}, cf = (e) => {
  e.bi_valid === 16 ? (Rt(e, e.bi_buf), e.bi_buf = 0, e.bi_valid = 0) : e.bi_valid >= 8 && (e.pending_buf[e.pending++] = e.bi_buf & 255, e.bi_buf >>= 8, e.bi_valid -= 8);
}, df = (e, n) => {
  const t = n.dyn_tree, i = n.max_code, a = n.stat_desc.static_tree, l = n.stat_desc.has_stree, f = n.stat_desc.extra_bits, r = n.stat_desc.extra_base, s = n.stat_desc.max_length;
  let o, c, h, d, u, _, v = 0;
  for (d = 0; d <= Oe; d++)
    e.bl_count[d] = 0;
  for (t[e.heap[e.heap_max] * 2 + 1] = 0, o = e.heap_max + 1; o < tl; o++)
    c = e.heap[o], d = t[t[c * 2 + 1] * 2 + 1] + 1, d > s && (d = s, v++), t[c * 2 + 1] = d, !(c > i) && (e.bl_count[d]++, u = 0, c >= r && (u = f[c - r]), _ = t[c * 2], e.opt_len += _ * (d + u), l && (e.static_len += _ * (a[c * 2 + 1] + u)));
  if (v !== 0) {
    do {
      for (d = s - 1; e.bl_count[d] === 0; )
        d--;
      e.bl_count[d]--, e.bl_count[d + 1] += 2, e.bl_count[s]--, v -= 2;
    } while (v > 0);
    for (d = s; d !== 0; d--)
      for (c = e.bl_count[d]; c !== 0; )
        h = e.heap[--o], !(h > i) && (t[h * 2 + 1] !== d && (e.opt_len += (d - t[h * 2 + 1]) * t[h * 2], t[h * 2 + 1] = d), c--);
  }
}, dl = (e, n, t) => {
  const i = new Array(Oe + 1);
  let a = 0, l, f;
  for (l = 1; l <= Oe; l++)
    a = a + t[l - 1] << 1, i[l] = a;
  for (f = 0; f <= n; f++) {
    let r = e[f * 2 + 1];
    r !== 0 && (e[f * 2] = cl(i[r]++, r));
  }
}, hf = () => {
  let e, n, t, i, a;
  const l = new Array(Oe + 1);
  for (t = 0, i = 0; i < ni - 1; i++)
    for (li[i] = t, e = 0; e < 1 << $n[i]; e++)
      Nt[t++] = i;
  for (Nt[t - 1] = i, a = 0, i = 0; i < 16; i++)
    for (an[i] = a, e = 0; e < 1 << en[i]; e++)
      zt[a++] = i;
  for (a >>= 7; i < it; i++)
    for (an[i] = a << 7, e = 0; e < 1 << en[i] - 7; e++)
      zt[256 + a++] = i;
  for (n = 0; n <= Oe; n++)
    l[n] = 0;
  for (e = 0; e <= 143; )
    ze[e * 2 + 1] = 8, e++, l[8]++;
  for (; e <= 255; )
    ze[e * 2 + 1] = 9, e++, l[9]++;
  for (; e <= 279; )
    ze[e * 2 + 1] = 7, e++, l[7]++;
  for (; e <= 287; )
    ze[e * 2 + 1] = 8, e++, l[8]++;
  for (dl(ze, St + 1, l), e = 0; e < it; e++)
    kt[e * 2 + 1] = 5, kt[e * 2] = cl(e, 5);
  fl = new xn(ze, $n, Ht + 1, St, Oe), rl = new xn(kt, en, 0, it, Oe), ol = new xn(new Array(0), of, 0, ii, rf);
}, hl = (e) => {
  let n;
  for (n = 0; n < St; n++)
    e.dyn_ltree[n * 2] = 0;
  for (n = 0; n < it; n++)
    e.dyn_dtree[n * 2] = 0;
  for (n = 0; n < ii; n++)
    e.bl_tree[n * 2] = 0;
  e.dyn_ltree[ai * 2] = 1, e.opt_len = e.static_len = 0, e.sym_next = e.matches = 0;
}, ul = (e) => {
  e.bi_valid > 8 ? Rt(e, e.bi_buf) : e.bi_valid > 0 && (e.pending_buf[e.pending++] = e.bi_buf), e.bi_buf = 0, e.bi_valid = 0;
}, wi = (e, n, t, i) => {
  const a = n * 2, l = t * 2;
  return e[a] < e[l] || e[a] === e[l] && i[n] <= i[t];
}, yn = (e, n, t) => {
  const i = e.heap[t];
  let a = t << 1;
  for (; a <= e.heap_len && (a < e.heap_len && wi(n, e.heap[a + 1], e.heap[a], e.depth) && a++, !wi(n, i, e.heap[a], e.depth)); )
    e.heap[t] = e.heap[a], t = a, a <<= 1;
  e.heap[t] = i;
}, xi = (e, n, t) => {
  let i, a, l = 0, f, r;
  if (e.sym_next !== 0)
    do
      i = e.pending_buf[e.sym_buf + l++] & 255, i += (e.pending_buf[e.sym_buf + l++] & 255) << 8, a = e.pending_buf[e.sym_buf + l++], i === 0 ? ve(e, a, n) : (f = Nt[a], ve(e, f + Ht + 1, n), r = $n[f], r !== 0 && (a -= li[f], ne(e, a, r)), i--, f = sl(i), ve(e, f, t), r = en[f], r !== 0 && (i -= an[f], ne(e, i, r)));
    while (l < e.sym_next);
  ve(e, ai, n);
}, Bn = (e, n) => {
  const t = n.dyn_tree, i = n.stat_desc.static_tree, a = n.stat_desc.has_stree, l = n.stat_desc.elems;
  let f, r, s = -1, o;
  for (e.heap_len = 0, e.heap_max = tl, f = 0; f < l; f++)
    t[f * 2] !== 0 ? (e.heap[++e.heap_len] = s = f, e.depth[f] = 0) : t[f * 2 + 1] = 0;
  for (; e.heap_len < 2; )
    o = e.heap[++e.heap_len] = s < 2 ? ++s : 0, t[o * 2] = 1, e.depth[o] = 0, e.opt_len--, a && (e.static_len -= i[o * 2 + 1]);
  for (n.max_code = s, f = e.heap_len >> 1; f >= 1; f--)
    yn(e, t, f);
  o = l;
  do
    f = e.heap[
      1
      /*SMALLEST*/
    ], e.heap[
      1
      /*SMALLEST*/
    ] = e.heap[e.heap_len--], yn(
      e,
      t,
      1
      /*SMALLEST*/
    ), r = e.heap[
      1
      /*SMALLEST*/
    ], e.heap[--e.heap_max] = f, e.heap[--e.heap_max] = r, t[o * 2] = t[f * 2] + t[r * 2], e.depth[o] = (e.depth[f] >= e.depth[r] ? e.depth[f] : e.depth[r]) + 1, t[f * 2 + 1] = t[r * 2 + 1] = o, e.heap[
      1
      /*SMALLEST*/
    ] = o++, yn(
      e,
      t,
      1
      /*SMALLEST*/
    );
  while (e.heap_len >= 2);
  e.heap[--e.heap_max] = e.heap[
    1
    /*SMALLEST*/
  ], df(e, n), dl(t, s, e.bl_count);
}, vi = (e, n, t) => {
  let i, a = -1, l, f = n[0 * 2 + 1], r = 0, s = 7, o = 4;
  for (f === 0 && (s = 138, o = 3), n[(t + 1) * 2 + 1] = 65535, i = 0; i <= t; i++)
    l = f, f = n[(i + 1) * 2 + 1], !(++r < s && l === f) && (r < o ? e.bl_tree[l * 2] += r : l !== 0 ? (l !== a && e.bl_tree[l * 2]++, e.bl_tree[nl * 2]++) : r <= 10 ? e.bl_tree[il * 2]++ : e.bl_tree[al * 2]++, r = 0, a = l, f === 0 ? (s = 138, o = 3) : l === f ? (s = 6, o = 3) : (s = 7, o = 4));
}, yi = (e, n, t) => {
  let i, a = -1, l, f = n[0 * 2 + 1], r = 0, s = 7, o = 4;
  for (f === 0 && (s = 138, o = 3), i = 0; i <= t; i++)
    if (l = f, f = n[(i + 1) * 2 + 1], !(++r < s && l === f)) {
      if (r < o)
        do
          ve(e, l, e.bl_tree);
        while (--r !== 0);
      else l !== 0 ? (l !== a && (ve(e, l, e.bl_tree), r--), ve(e, nl, e.bl_tree), ne(e, r - 3, 2)) : r <= 10 ? (ve(e, il, e.bl_tree), ne(e, r - 3, 3)) : (ve(e, al, e.bl_tree), ne(e, r - 11, 7));
      r = 0, a = l, f === 0 ? (s = 138, o = 3) : l === f ? (s = 6, o = 3) : (s = 7, o = 4);
    }
}, uf = (e) => {
  let n;
  for (vi(e, e.dyn_ltree, e.l_desc.max_code), vi(e, e.dyn_dtree, e.d_desc.max_code), Bn(e, e.bl_desc), n = ii - 1; n >= 3 && e.bl_tree[ll[n] * 2 + 1] === 0; n--)
    ;
  return e.opt_len += 3 * (n + 1) + 5 + 5 + 4, n;
}, _f = (e, n, t, i) => {
  let a;
  for (ne(e, n - 257, 5), ne(e, t - 1, 5), ne(e, i - 4, 4), a = 0; a < i; a++)
    ne(e, e.bl_tree[ll[a] * 2 + 1], 3);
  yi(e, e.dyn_ltree, n - 1), yi(e, e.dyn_dtree, t - 1);
}, bf = (e) => {
  let n = 4093624447, t;
  for (t = 0; t <= 31; t++, n >>>= 1)
    if (n & 1 && e.dyn_ltree[t * 2] !== 0)
      return 0;
  if (e.dyn_ltree[9 * 2] !== 0 || e.dyn_ltree[10 * 2] !== 0 || e.dyn_ltree[13 * 2] !== 0)
    return 1;
  for (t = 32; t < Ht; t++)
    if (e.dyn_ltree[t * 2] !== 0)
      return 1;
  return 0;
};
let ki = !1;
const gf = (e) => {
  ki || (hf(), ki = !0), e.l_desc = new vn(e.dyn_ltree, fl), e.d_desc = new vn(e.dyn_dtree, rl), e.bl_desc = new vn(e.bl_tree, ol), e.bi_buf = 0, e.bi_valid = 0, hl(e);
}, _l = (e, n, t, i) => {
  ne(e, (nf << 1) + (i ? 1 : 0), 3), ul(e), Rt(e, t), Rt(e, ~t), t && e.pending_buf.set(e.window.subarray(n, n + t), e.pending), e.pending += t;
}, mf = (e) => {
  ne(e, el << 1, 3), ve(e, ai, ze), cf(e);
}, pf = (e, n, t, i) => {
  let a, l, f = 0;
  e.level > 0 ? (e.strm.data_type === 2 && (e.strm.data_type = bf(e)), Bn(e, e.l_desc), Bn(e, e.d_desc), f = uf(e), a = e.opt_len + 3 + 7 >>> 3, l = e.static_len + 3 + 7 >>> 3, l <= a && (a = l)) : a = l = t + 5, t + 4 <= a && n !== -1 ? _l(e, n, t, i) : e.strategy === 4 || l === a ? (ne(e, (el << 1) + (i ? 1 : 0), 3), xi(e, ze, kt)) : (ne(e, (af << 1) + (i ? 1 : 0), 3), _f(e, e.l_desc.max_code + 1, e.d_desc.max_code + 1, f + 1), xi(e, e.dyn_ltree, e.dyn_dtree)), hl(e), i && ul(e);
}, wf = (e, n, t) => (e.pending_buf[e.sym_buf + e.sym_next++] = n, e.pending_buf[e.sym_buf + e.sym_next++] = n >> 8, e.pending_buf[e.sym_buf + e.sym_next++] = t, n === 0 ? e.dyn_ltree[t * 2]++ : (e.matches++, n--, e.dyn_ltree[(Nt[t] + Ht + 1) * 2]++, e.dyn_dtree[sl(n) * 2]++), e.sym_next === e.sym_end);
var xf = gf, vf = _l, yf = pf, kf = wf, Ef = mf, Af = {
  _tr_init: xf,
  _tr_stored_block: vf,
  _tr_flush_block: yf,
  _tr_tally: kf,
  _tr_align: Ef
};
const Mf = (e, n, t, i) => {
  let a = e & 65535 | 0, l = e >>> 16 & 65535 | 0, f = 0;
  for (; t !== 0; ) {
    f = t > 2e3 ? 2e3 : t, t -= f;
    do
      a = a + n[i++] | 0, l = l + a | 0;
    while (--f);
    a %= 65521, l %= 65521;
  }
  return a | l << 16 | 0;
};
var Tt = Mf;
const Sf = () => {
  let e, n = [];
  for (var t = 0; t < 256; t++) {
    e = t;
    for (var i = 0; i < 8; i++)
      e = e & 1 ? 3988292384 ^ e >>> 1 : e >>> 1;
    n[t] = e;
  }
  return n;
}, zf = new Uint32Array(Sf()), Nf = (e, n, t, i) => {
  const a = zf, l = i + t;
  e ^= -1;
  for (let f = i; f < l; f++)
    e = e >>> 8 ^ a[(e ^ n[f]) & 255];
  return e ^ -1;
};
var q = Nf, ft = {
  2: "need dictionary",
  /* Z_NEED_DICT       2  */
  1: "stream end",
  /* Z_STREAM_END      1  */
  0: "",
  /* Z_OK              0  */
  "-1": "file error",
  /* Z_ERRNO         (-1) */
  "-2": "stream error",
  /* Z_STREAM_ERROR  (-2) */
  "-3": "data error",
  /* Z_DATA_ERROR    (-3) */
  "-4": "insufficient memory",
  /* Z_MEM_ERROR     (-4) */
  "-5": "buffer error",
  /* Z_BUF_ERROR     (-5) */
  "-6": "incompatible version"
  /* Z_VERSION_ERROR (-6) */
}, $t = {
  /* Allowed flush values; see deflate() and inflate() below for details */
  Z_NO_FLUSH: 0,
  Z_PARTIAL_FLUSH: 1,
  Z_SYNC_FLUSH: 2,
  Z_FULL_FLUSH: 3,
  Z_FINISH: 4,
  Z_BLOCK: 5,
  Z_TREES: 6,
  /* Return codes for the compression/decompression functions. Negative values
  * are errors, positive values are used for special but normal events.
  */
  Z_OK: 0,
  Z_STREAM_END: 1,
  Z_NEED_DICT: 2,
  Z_ERRNO: -1,
  Z_STREAM_ERROR: -2,
  Z_DATA_ERROR: -3,
  Z_MEM_ERROR: -4,
  Z_BUF_ERROR: -5,
  //Z_VERSION_ERROR: -6,
  /* compression levels */
  Z_NO_COMPRESSION: 0,
  Z_BEST_SPEED: 1,
  Z_BEST_COMPRESSION: 9,
  Z_DEFAULT_COMPRESSION: -1,
  Z_FILTERED: 1,
  Z_HUFFMAN_ONLY: 2,
  Z_RLE: 3,
  Z_FIXED: 4,
  Z_DEFAULT_STRATEGY: 0,
  /* Possible values of the data_type field (though see inflate()) */
  Z_BINARY: 0,
  Z_TEXT: 1,
  //Z_ASCII:                1, // = Z_TEXT (deprecated)
  Z_UNKNOWN: 2,
  /* The deflate compression method */
  Z_DEFLATED: 8
  //Z_NULL:                 null // Use -1 or null inline, depending on var type
};
const { _tr_init: Rf, _tr_stored_block: Pn, _tr_flush_block: Tf, _tr_tally: Ie, _tr_align: Df } = Af, {
  Z_NO_FLUSH: Le,
  Z_PARTIAL_FLUSH: If,
  Z_FULL_FLUSH: Lf,
  Z_FINISH: ce,
  Z_BLOCK: Ei,
  Z_OK: Q,
  Z_STREAM_END: Ai,
  Z_STREAM_ERROR: Ee,
  Z_DATA_ERROR: Cf,
  Z_BUF_ERROR: kn,
  Z_DEFAULT_COMPRESSION: Zf,
  Z_FILTERED: Of,
  Z_HUFFMAN_ONLY: Kt,
  Z_RLE: Uf,
  Z_FIXED: Ff,
  Z_DEFAULT_STRATEGY: Hf,
  Z_UNKNOWN: $f,
  Z_DEFLATED: _n
} = $t, Bf = 9, Pf = 15, jf = 8, Xf = 29, Kf = 256, jn = Kf + 1 + Xf, Yf = 30, Gf = 19, Vf = 2 * jn + 1, qf = 15, F = 3, De = 258, Ae = De + F + 1, Wf = 32, rt = 42, fi = 57, Xn = 69, Kn = 73, Yn = 91, Gn = 103, Ue = 113, vt = 666, ee = 1, bt = 2, Pe = 3, gt = 4, Jf = 3, Fe = (e, n) => (e.msg = ft[n], n), Mi = (e) => e * 2 - (e > 4 ? 9 : 0), Te = (e) => {
  let n = e.length;
  for (; --n >= 0; )
    e[n] = 0;
}, Qf = (e) => {
  let n, t, i, a = e.w_size;
  n = e.hash_size, i = n;
  do
    t = e.head[--i], e.head[i] = t >= a ? t - a : 0;
  while (--n);
  n = a, i = n;
  do
    t = e.prev[--i], e.prev[i] = t >= a ? t - a : 0;
  while (--n);
};
let er = (e, n, t) => (n << e.hash_shift ^ t) & e.hash_mask, Ce = er;
const ae = (e) => {
  const n = e.state;
  let t = n.pending;
  t > e.avail_out && (t = e.avail_out), t !== 0 && (e.output.set(n.pending_buf.subarray(n.pending_out, n.pending_out + t), e.next_out), e.next_out += t, n.pending_out += t, e.total_out += t, e.avail_out -= t, n.pending -= t, n.pending === 0 && (n.pending_out = 0));
}, le = (e, n) => {
  Tf(e, e.block_start >= 0 ? e.block_start : -1, e.strstart - e.block_start, n), e.block_start = e.strstart, ae(e.strm);
}, $ = (e, n) => {
  e.pending_buf[e.pending++] = n;
}, wt = (e, n) => {
  e.pending_buf[e.pending++] = n >>> 8 & 255, e.pending_buf[e.pending++] = n & 255;
}, Vn = (e, n, t, i) => {
  let a = e.avail_in;
  return a > i && (a = i), a === 0 ? 0 : (e.avail_in -= a, n.set(e.input.subarray(e.next_in, e.next_in + a), t), e.state.wrap === 1 ? e.adler = Tt(e.adler, n, a, t) : e.state.wrap === 2 && (e.adler = q(e.adler, n, a, t)), e.next_in += a, e.total_in += a, a);
}, bl = (e, n) => {
  let t = e.max_chain_length, i = e.strstart, a, l, f = e.prev_length, r = e.nice_match;
  const s = e.strstart > e.w_size - Ae ? e.strstart - (e.w_size - Ae) : 0, o = e.window, c = e.w_mask, h = e.prev, d = e.strstart + De;
  let u = o[i + f - 1], _ = o[i + f];
  e.prev_length >= e.good_match && (t >>= 2), r > e.lookahead && (r = e.lookahead);
  do
    if (a = n, !(o[a + f] !== _ || o[a + f - 1] !== u || o[a] !== o[i] || o[++a] !== o[i + 1])) {
      i += 2, a++;
      do
        ;
      while (o[++i] === o[++a] && o[++i] === o[++a] && o[++i] === o[++a] && o[++i] === o[++a] && o[++i] === o[++a] && o[++i] === o[++a] && o[++i] === o[++a] && o[++i] === o[++a] && i < d);
      if (l = De - (d - i), i = d - De, l > f) {
        if (e.match_start = n, f = l, l >= r)
          break;
        u = o[i + f - 1], _ = o[i + f];
      }
    }
  while ((n = h[n & c]) > s && --t !== 0);
  return f <= e.lookahead ? f : e.lookahead;
}, ot = (e) => {
  const n = e.w_size;
  let t, i, a;
  do {
    if (i = e.window_size - e.lookahead - e.strstart, e.strstart >= n + (n - Ae) && (e.window.set(e.window.subarray(n, n + n - i), 0), e.match_start -= n, e.strstart -= n, e.block_start -= n, e.insert > e.strstart && (e.insert = e.strstart), Qf(e), i += n), e.strm.avail_in === 0)
      break;
    if (t = Vn(e.strm, e.window, e.strstart + e.lookahead, i), e.lookahead += t, e.lookahead + e.insert >= F)
      for (a = e.strstart - e.insert, e.ins_h = e.window[a], e.ins_h = Ce(e, e.ins_h, e.window[a + 1]); e.insert && (e.ins_h = Ce(e, e.ins_h, e.window[a + F - 1]), e.prev[a & e.w_mask] = e.head[e.ins_h], e.head[e.ins_h] = a, a++, e.insert--, !(e.lookahead + e.insert < F)); )
        ;
  } while (e.lookahead < Ae && e.strm.avail_in !== 0);
}, gl = (e, n) => {
  let t = e.pending_buf_size - 5 > e.w_size ? e.w_size : e.pending_buf_size - 5, i, a, l, f = 0, r = e.strm.avail_in;
  do {
    if (i = 65535, l = e.bi_valid + 42 >> 3, e.strm.avail_out < l || (l = e.strm.avail_out - l, a = e.strstart - e.block_start, i > a + e.strm.avail_in && (i = a + e.strm.avail_in), i > l && (i = l), i < t && (i === 0 && n !== ce || n === Le || i !== a + e.strm.avail_in)))
      break;
    f = n === ce && i === a + e.strm.avail_in ? 1 : 0, Pn(e, 0, 0, f), e.pending_buf[e.pending - 4] = i, e.pending_buf[e.pending - 3] = i >> 8, e.pending_buf[e.pending - 2] = ~i, e.pending_buf[e.pending - 1] = ~i >> 8, ae(e.strm), a && (a > i && (a = i), e.strm.output.set(e.window.subarray(e.block_start, e.block_start + a), e.strm.next_out), e.strm.next_out += a, e.strm.avail_out -= a, e.strm.total_out += a, e.block_start += a, i -= a), i && (Vn(e.strm, e.strm.output, e.strm.next_out, i), e.strm.next_out += i, e.strm.avail_out -= i, e.strm.total_out += i);
  } while (f === 0);
  return r -= e.strm.avail_in, r && (r >= e.w_size ? (e.matches = 2, e.window.set(e.strm.input.subarray(e.strm.next_in - e.w_size, e.strm.next_in), 0), e.strstart = e.w_size, e.insert = e.strstart) : (e.window_size - e.strstart <= r && (e.strstart -= e.w_size, e.window.set(e.window.subarray(e.w_size, e.w_size + e.strstart), 0), e.matches < 2 && e.matches++, e.insert > e.strstart && (e.insert = e.strstart)), e.window.set(e.strm.input.subarray(e.strm.next_in - r, e.strm.next_in), e.strstart), e.strstart += r, e.insert += r > e.w_size - e.insert ? e.w_size - e.insert : r), e.block_start = e.strstart), e.high_water < e.strstart && (e.high_water = e.strstart), f ? gt : n !== Le && n !== ce && e.strm.avail_in === 0 && e.strstart === e.block_start ? bt : (l = e.window_size - e.strstart, e.strm.avail_in > l && e.block_start >= e.w_size && (e.block_start -= e.w_size, e.strstart -= e.w_size, e.window.set(e.window.subarray(e.w_size, e.w_size + e.strstart), 0), e.matches < 2 && e.matches++, l += e.w_size, e.insert > e.strstart && (e.insert = e.strstart)), l > e.strm.avail_in && (l = e.strm.avail_in), l && (Vn(e.strm, e.window, e.strstart, l), e.strstart += l, e.insert += l > e.w_size - e.insert ? e.w_size - e.insert : l), e.high_water < e.strstart && (e.high_water = e.strstart), l = e.bi_valid + 42 >> 3, l = e.pending_buf_size - l > 65535 ? 65535 : e.pending_buf_size - l, t = l > e.w_size ? e.w_size : l, a = e.strstart - e.block_start, (a >= t || (a || n === ce) && n !== Le && e.strm.avail_in === 0 && a <= l) && (i = a > l ? l : a, f = n === ce && e.strm.avail_in === 0 && i === a ? 1 : 0, Pn(e, e.block_start, i, f), e.block_start += i, ae(e.strm)), f ? Pe : ee);
}, En = (e, n) => {
  let t, i;
  for (; ; ) {
    if (e.lookahead < Ae) {
      if (ot(e), e.lookahead < Ae && n === Le)
        return ee;
      if (e.lookahead === 0)
        break;
    }
    if (t = 0, e.lookahead >= F && (e.ins_h = Ce(e, e.ins_h, e.window[e.strstart + F - 1]), t = e.prev[e.strstart & e.w_mask] = e.head[e.ins_h], e.head[e.ins_h] = e.strstart), t !== 0 && e.strstart - t <= e.w_size - Ae && (e.match_length = bl(e, t)), e.match_length >= F)
      if (i = Ie(e, e.strstart - e.match_start, e.match_length - F), e.lookahead -= e.match_length, e.match_length <= e.max_lazy_match && e.lookahead >= F) {
        e.match_length--;
        do
          e.strstart++, e.ins_h = Ce(e, e.ins_h, e.window[e.strstart + F - 1]), t = e.prev[e.strstart & e.w_mask] = e.head[e.ins_h], e.head[e.ins_h] = e.strstart;
        while (--e.match_length !== 0);
        e.strstart++;
      } else
        e.strstart += e.match_length, e.match_length = 0, e.ins_h = e.window[e.strstart], e.ins_h = Ce(e, e.ins_h, e.window[e.strstart + 1]);
    else
      i = Ie(e, 0, e.window[e.strstart]), e.lookahead--, e.strstart++;
    if (i && (le(e, !1), e.strm.avail_out === 0))
      return ee;
  }
  return e.insert = e.strstart < F - 1 ? e.strstart : F - 1, n === ce ? (le(e, !0), e.strm.avail_out === 0 ? Pe : gt) : e.sym_next && (le(e, !1), e.strm.avail_out === 0) ? ee : bt;
}, We = (e, n) => {
  let t, i, a;
  for (; ; ) {
    if (e.lookahead < Ae) {
      if (ot(e), e.lookahead < Ae && n === Le)
        return ee;
      if (e.lookahead === 0)
        break;
    }
    if (t = 0, e.lookahead >= F && (e.ins_h = Ce(e, e.ins_h, e.window[e.strstart + F - 1]), t = e.prev[e.strstart & e.w_mask] = e.head[e.ins_h], e.head[e.ins_h] = e.strstart), e.prev_length = e.match_length, e.prev_match = e.match_start, e.match_length = F - 1, t !== 0 && e.prev_length < e.max_lazy_match && e.strstart - t <= e.w_size - Ae && (e.match_length = bl(e, t), e.match_length <= 5 && (e.strategy === Of || e.match_length === F && e.strstart - e.match_start > 4096) && (e.match_length = F - 1)), e.prev_length >= F && e.match_length <= e.prev_length) {
      a = e.strstart + e.lookahead - F, i = Ie(e, e.strstart - 1 - e.prev_match, e.prev_length - F), e.lookahead -= e.prev_length - 1, e.prev_length -= 2;
      do
        ++e.strstart <= a && (e.ins_h = Ce(e, e.ins_h, e.window[e.strstart + F - 1]), t = e.prev[e.strstart & e.w_mask] = e.head[e.ins_h], e.head[e.ins_h] = e.strstart);
      while (--e.prev_length !== 0);
      if (e.match_available = 0, e.match_length = F - 1, e.strstart++, i && (le(e, !1), e.strm.avail_out === 0))
        return ee;
    } else if (e.match_available) {
      if (i = Ie(e, 0, e.window[e.strstart - 1]), i && le(e, !1), e.strstart++, e.lookahead--, e.strm.avail_out === 0)
        return ee;
    } else
      e.match_available = 1, e.strstart++, e.lookahead--;
  }
  return e.match_available && (i = Ie(e, 0, e.window[e.strstart - 1]), e.match_available = 0), e.insert = e.strstart < F - 1 ? e.strstart : F - 1, n === ce ? (le(e, !0), e.strm.avail_out === 0 ? Pe : gt) : e.sym_next && (le(e, !1), e.strm.avail_out === 0) ? ee : bt;
}, tr = (e, n) => {
  let t, i, a, l;
  const f = e.window;
  for (; ; ) {
    if (e.lookahead <= De) {
      if (ot(e), e.lookahead <= De && n === Le)
        return ee;
      if (e.lookahead === 0)
        break;
    }
    if (e.match_length = 0, e.lookahead >= F && e.strstart > 0 && (a = e.strstart - 1, i = f[a], i === f[++a] && i === f[++a] && i === f[++a])) {
      l = e.strstart + De;
      do
        ;
      while (i === f[++a] && i === f[++a] && i === f[++a] && i === f[++a] && i === f[++a] && i === f[++a] && i === f[++a] && i === f[++a] && a < l);
      e.match_length = De - (l - a), e.match_length > e.lookahead && (e.match_length = e.lookahead);
    }
    if (e.match_length >= F ? (t = Ie(e, 1, e.match_length - F), e.lookahead -= e.match_length, e.strstart += e.match_length, e.match_length = 0) : (t = Ie(e, 0, e.window[e.strstart]), e.lookahead--, e.strstart++), t && (le(e, !1), e.strm.avail_out === 0))
      return ee;
  }
  return e.insert = 0, n === ce ? (le(e, !0), e.strm.avail_out === 0 ? Pe : gt) : e.sym_next && (le(e, !1), e.strm.avail_out === 0) ? ee : bt;
}, nr = (e, n) => {
  let t;
  for (; ; ) {
    if (e.lookahead === 0 && (ot(e), e.lookahead === 0)) {
      if (n === Le)
        return ee;
      break;
    }
    if (e.match_length = 0, t = Ie(e, 0, e.window[e.strstart]), e.lookahead--, e.strstart++, t && (le(e, !1), e.strm.avail_out === 0))
      return ee;
  }
  return e.insert = 0, n === ce ? (le(e, !0), e.strm.avail_out === 0 ? Pe : gt) : e.sym_next && (le(e, !1), e.strm.avail_out === 0) ? ee : bt;
};
function we(e, n, t, i, a) {
  this.good_length = e, this.max_lazy = n, this.nice_length = t, this.max_chain = i, this.func = a;
}
const yt = [
  /*      good lazy nice chain */
  new we(0, 0, 0, 0, gl),
  /* 0 store only */
  new we(4, 4, 8, 4, En),
  /* 1 max speed, no lazy matches */
  new we(4, 5, 16, 8, En),
  /* 2 */
  new we(4, 6, 32, 32, En),
  /* 3 */
  new we(4, 4, 16, 16, We),
  /* 4 lazy matches */
  new we(8, 16, 32, 32, We),
  /* 5 */
  new we(8, 16, 128, 128, We),
  /* 6 */
  new we(8, 32, 128, 256, We),
  /* 7 */
  new we(32, 128, 258, 1024, We),
  /* 8 */
  new we(32, 258, 258, 4096, We)
  /* 9 max compression */
], ir = (e) => {
  e.window_size = 2 * e.w_size, Te(e.head), e.max_lazy_match = yt[e.level].max_lazy, e.good_match = yt[e.level].good_length, e.nice_match = yt[e.level].nice_length, e.max_chain_length = yt[e.level].max_chain, e.strstart = 0, e.block_start = 0, e.lookahead = 0, e.insert = 0, e.match_length = e.prev_length = F - 1, e.match_available = 0, e.ins_h = 0;
};
function ar() {
  this.strm = null, this.status = 0, this.pending_buf = null, this.pending_buf_size = 0, this.pending_out = 0, this.pending = 0, this.wrap = 0, this.gzhead = null, this.gzindex = 0, this.method = _n, this.last_flush = -1, this.w_size = 0, this.w_bits = 0, this.w_mask = 0, this.window = null, this.window_size = 0, this.prev = null, this.head = null, this.ins_h = 0, this.hash_size = 0, this.hash_bits = 0, this.hash_mask = 0, this.hash_shift = 0, this.block_start = 0, this.match_length = 0, this.prev_match = 0, this.match_available = 0, this.strstart = 0, this.match_start = 0, this.lookahead = 0, this.prev_length = 0, this.max_chain_length = 0, this.max_lazy_match = 0, this.level = 0, this.strategy = 0, this.good_match = 0, this.nice_match = 0, this.dyn_ltree = new Uint16Array(Vf * 2), this.dyn_dtree = new Uint16Array((2 * Yf + 1) * 2), this.bl_tree = new Uint16Array((2 * Gf + 1) * 2), Te(this.dyn_ltree), Te(this.dyn_dtree), Te(this.bl_tree), this.l_desc = null, this.d_desc = null, this.bl_desc = null, this.bl_count = new Uint16Array(qf + 1), this.heap = new Uint16Array(2 * jn + 1), Te(this.heap), this.heap_len = 0, this.heap_max = 0, this.depth = new Uint16Array(2 * jn + 1), Te(this.depth), this.sym_buf = 0, this.lit_bufsize = 0, this.sym_next = 0, this.sym_end = 0, this.opt_len = 0, this.static_len = 0, this.matches = 0, this.insert = 0, this.bi_buf = 0, this.bi_valid = 0;
}
const Bt = (e) => {
  if (!e)
    return 1;
  const n = e.state;
  return !n || n.strm !== e || n.status !== rt && //#ifdef GZIP
  n.status !== fi && //#endif
  n.status !== Xn && n.status !== Kn && n.status !== Yn && n.status !== Gn && n.status !== Ue && n.status !== vt ? 1 : 0;
}, ml = (e) => {
  if (Bt(e))
    return Fe(e, Ee);
  e.total_in = e.total_out = 0, e.data_type = $f;
  const n = e.state;
  return n.pending = 0, n.pending_out = 0, n.wrap < 0 && (n.wrap = -n.wrap), n.status = //#ifdef GZIP
  n.wrap === 2 ? fi : (
    //#endif
    n.wrap ? rt : Ue
  ), e.adler = n.wrap === 2 ? 0 : 1, n.last_flush = -2, Rf(n), Q;
}, pl = (e) => {
  const n = ml(e);
  return n === Q && ir(e.state), n;
}, lr = (e, n) => Bt(e) || e.state.wrap !== 2 ? Ee : (e.state.gzhead = n, Q), wl = (e, n, t, i, a, l) => {
  if (!e)
    return Ee;
  let f = 1;
  if (n === Zf && (n = 6), i < 0 ? (f = 0, i = -i) : i > 15 && (f = 2, i -= 16), a < 1 || a > Bf || t !== _n || i < 8 || i > 15 || n < 0 || n > 9 || l < 0 || l > Ff || i === 8 && f !== 1)
    return Fe(e, Ee);
  i === 8 && (i = 9);
  const r = new ar();
  return e.state = r, r.strm = e, r.status = rt, r.wrap = f, r.gzhead = null, r.w_bits = i, r.w_size = 1 << r.w_bits, r.w_mask = r.w_size - 1, r.hash_bits = a + 7, r.hash_size = 1 << r.hash_bits, r.hash_mask = r.hash_size - 1, r.hash_shift = ~~((r.hash_bits + F - 1) / F), r.window = new Uint8Array(r.w_size * 2), r.head = new Uint16Array(r.hash_size), r.prev = new Uint16Array(r.w_size), r.lit_bufsize = 1 << a + 6, r.pending_buf_size = r.lit_bufsize * 4, r.pending_buf = new Uint8Array(r.pending_buf_size), r.sym_buf = r.lit_bufsize, r.sym_end = (r.lit_bufsize - 1) * 3, r.level = n, r.strategy = l, r.method = t, pl(e);
}, fr = (e, n) => wl(e, n, _n, Pf, jf, Hf), rr = (e, n) => {
  if (Bt(e) || n > Ei || n < 0)
    return e ? Fe(e, Ee) : Ee;
  const t = e.state;
  if (!e.output || e.avail_in !== 0 && !e.input || t.status === vt && n !== ce)
    return Fe(e, e.avail_out === 0 ? kn : Ee);
  const i = t.last_flush;
  if (t.last_flush = n, t.pending !== 0) {
    if (ae(e), e.avail_out === 0)
      return t.last_flush = -1, Q;
  } else if (e.avail_in === 0 && Mi(n) <= Mi(i) && n !== ce)
    return Fe(e, kn);
  if (t.status === vt && e.avail_in !== 0)
    return Fe(e, kn);
  if (t.status === rt && t.wrap === 0 && (t.status = Ue), t.status === rt) {
    let a = _n + (t.w_bits - 8 << 4) << 8, l = -1;
    if (t.strategy >= Kt || t.level < 2 ? l = 0 : t.level < 6 ? l = 1 : t.level === 6 ? l = 2 : l = 3, a |= l << 6, t.strstart !== 0 && (a |= Wf), a += 31 - a % 31, wt(t, a), t.strstart !== 0 && (wt(t, e.adler >>> 16), wt(t, e.adler & 65535)), e.adler = 1, t.status = Ue, ae(e), t.pending !== 0)
      return t.last_flush = -1, Q;
  }
  if (t.status === fi) {
    if (e.adler = 0, $(t, 31), $(t, 139), $(t, 8), t.gzhead)
      $(
        t,
        (t.gzhead.text ? 1 : 0) + (t.gzhead.hcrc ? 2 : 0) + (t.gzhead.extra ? 4 : 0) + (t.gzhead.name ? 8 : 0) + (t.gzhead.comment ? 16 : 0)
      ), $(t, t.gzhead.time & 255), $(t, t.gzhead.time >> 8 & 255), $(t, t.gzhead.time >> 16 & 255), $(t, t.gzhead.time >> 24 & 255), $(t, t.level === 9 ? 2 : t.strategy >= Kt || t.level < 2 ? 4 : 0), $(t, t.gzhead.os & 255), t.gzhead.extra && t.gzhead.extra.length && ($(t, t.gzhead.extra.length & 255), $(t, t.gzhead.extra.length >> 8 & 255)), t.gzhead.hcrc && (e.adler = q(e.adler, t.pending_buf, t.pending, 0)), t.gzindex = 0, t.status = Xn;
    else if ($(t, 0), $(t, 0), $(t, 0), $(t, 0), $(t, 0), $(t, t.level === 9 ? 2 : t.strategy >= Kt || t.level < 2 ? 4 : 0), $(t, Jf), t.status = Ue, ae(e), t.pending !== 0)
      return t.last_flush = -1, Q;
  }
  if (t.status === Xn) {
    if (t.gzhead.extra) {
      let a = t.pending, l = (t.gzhead.extra.length & 65535) - t.gzindex;
      for (; t.pending + l > t.pending_buf_size; ) {
        let r = t.pending_buf_size - t.pending;
        if (t.pending_buf.set(t.gzhead.extra.subarray(t.gzindex, t.gzindex + r), t.pending), t.pending = t.pending_buf_size, t.gzhead.hcrc && t.pending > a && (e.adler = q(e.adler, t.pending_buf, t.pending - a, a)), t.gzindex += r, ae(e), t.pending !== 0)
          return t.last_flush = -1, Q;
        a = 0, l -= r;
      }
      let f = new Uint8Array(t.gzhead.extra);
      t.pending_buf.set(f.subarray(t.gzindex, t.gzindex + l), t.pending), t.pending += l, t.gzhead.hcrc && t.pending > a && (e.adler = q(e.adler, t.pending_buf, t.pending - a, a)), t.gzindex = 0;
    }
    t.status = Kn;
  }
  if (t.status === Kn) {
    if (t.gzhead.name) {
      let a = t.pending, l;
      do {
        if (t.pending === t.pending_buf_size) {
          if (t.gzhead.hcrc && t.pending > a && (e.adler = q(e.adler, t.pending_buf, t.pending - a, a)), ae(e), t.pending !== 0)
            return t.last_flush = -1, Q;
          a = 0;
        }
        t.gzindex < t.gzhead.name.length ? l = t.gzhead.name.charCodeAt(t.gzindex++) & 255 : l = 0, $(t, l);
      } while (l !== 0);
      t.gzhead.hcrc && t.pending > a && (e.adler = q(e.adler, t.pending_buf, t.pending - a, a)), t.gzindex = 0;
    }
    t.status = Yn;
  }
  if (t.status === Yn) {
    if (t.gzhead.comment) {
      let a = t.pending, l;
      do {
        if (t.pending === t.pending_buf_size) {
          if (t.gzhead.hcrc && t.pending > a && (e.adler = q(e.adler, t.pending_buf, t.pending - a, a)), ae(e), t.pending !== 0)
            return t.last_flush = -1, Q;
          a = 0;
        }
        t.gzindex < t.gzhead.comment.length ? l = t.gzhead.comment.charCodeAt(t.gzindex++) & 255 : l = 0, $(t, l);
      } while (l !== 0);
      t.gzhead.hcrc && t.pending > a && (e.adler = q(e.adler, t.pending_buf, t.pending - a, a));
    }
    t.status = Gn;
  }
  if (t.status === Gn) {
    if (t.gzhead.hcrc) {
      if (t.pending + 2 > t.pending_buf_size && (ae(e), t.pending !== 0))
        return t.last_flush = -1, Q;
      $(t, e.adler & 255), $(t, e.adler >> 8 & 255), e.adler = 0;
    }
    if (t.status = Ue, ae(e), t.pending !== 0)
      return t.last_flush = -1, Q;
  }
  if (e.avail_in !== 0 || t.lookahead !== 0 || n !== Le && t.status !== vt) {
    let a = t.level === 0 ? gl(t, n) : t.strategy === Kt ? nr(t, n) : t.strategy === Uf ? tr(t, n) : yt[t.level].func(t, n);
    if ((a === Pe || a === gt) && (t.status = vt), a === ee || a === Pe)
      return e.avail_out === 0 && (t.last_flush = -1), Q;
    if (a === bt && (n === If ? Df(t) : n !== Ei && (Pn(t, 0, 0, !1), n === Lf && (Te(t.head), t.lookahead === 0 && (t.strstart = 0, t.block_start = 0, t.insert = 0))), ae(e), e.avail_out === 0))
      return t.last_flush = -1, Q;
  }
  return n !== ce ? Q : t.wrap <= 0 ? Ai : (t.wrap === 2 ? ($(t, e.adler & 255), $(t, e.adler >> 8 & 255), $(t, e.adler >> 16 & 255), $(t, e.adler >> 24 & 255), $(t, e.total_in & 255), $(t, e.total_in >> 8 & 255), $(t, e.total_in >> 16 & 255), $(t, e.total_in >> 24 & 255)) : (wt(t, e.adler >>> 16), wt(t, e.adler & 65535)), ae(e), t.wrap > 0 && (t.wrap = -t.wrap), t.pending !== 0 ? Q : Ai);
}, or = (e) => {
  if (Bt(e))
    return Ee;
  const n = e.state.status;
  return e.state = null, n === Ue ? Fe(e, Cf) : Q;
}, sr = (e, n) => {
  let t = n.length;
  if (Bt(e))
    return Ee;
  const i = e.state, a = i.wrap;
  if (a === 2 || a === 1 && i.status !== rt || i.lookahead)
    return Ee;
  if (a === 1 && (e.adler = Tt(e.adler, n, t, 0)), i.wrap = 0, t >= i.w_size) {
    a === 0 && (Te(i.head), i.strstart = 0, i.block_start = 0, i.insert = 0);
    let s = new Uint8Array(i.w_size);
    s.set(n.subarray(t - i.w_size, t), 0), n = s, t = i.w_size;
  }
  const l = e.avail_in, f = e.next_in, r = e.input;
  for (e.avail_in = t, e.next_in = 0, e.input = n, ot(i); i.lookahead >= F; ) {
    let s = i.strstart, o = i.lookahead - (F - 1);
    do
      i.ins_h = Ce(i, i.ins_h, i.window[s + F - 1]), i.prev[s & i.w_mask] = i.head[i.ins_h], i.head[i.ins_h] = s, s++;
    while (--o);
    i.strstart = s, i.lookahead = F - 1, ot(i);
  }
  return i.strstart += i.lookahead, i.block_start = i.strstart, i.insert = i.lookahead, i.lookahead = 0, i.match_length = i.prev_length = F - 1, i.match_available = 0, e.next_in = f, e.input = r, e.avail_in = l, i.wrap = a, Q;
};
var cr = fr, dr = wl, hr = pl, ur = ml, _r = lr, br = rr, gr = or, mr = sr, pr = "pako deflate (from Nodeca project)", Et = {
  deflateInit: cr,
  deflateInit2: dr,
  deflateReset: hr,
  deflateResetKeep: ur,
  deflateSetHeader: _r,
  deflate: br,
  deflateEnd: gr,
  deflateSetDictionary: mr,
  deflateInfo: pr
};
const wr = (e, n) => Object.prototype.hasOwnProperty.call(e, n);
var xr = function(e) {
  const n = Array.prototype.slice.call(arguments, 1);
  for (; n.length; ) {
    const t = n.shift();
    if (t) {
      if (typeof t != "object")
        throw new TypeError(t + "must be non-object");
      for (const i in t)
        wr(t, i) && (e[i] = t[i]);
    }
  }
  return e;
}, vr = (e) => {
  let n = 0;
  for (let i = 0, a = e.length; i < a; i++)
    n += e[i].length;
  const t = new Uint8Array(n);
  for (let i = 0, a = 0, l = e.length; i < l; i++) {
    let f = e[i];
    t.set(f, a), a += f.length;
  }
  return t;
}, bn = {
  assign: xr,
  flattenChunks: vr
};
let xl = !0;
try {
  String.fromCharCode.apply(null, new Uint8Array(1));
} catch {
  xl = !1;
}
const Dt = new Uint8Array(256);
for (let e = 0; e < 256; e++)
  Dt[e] = e >= 252 ? 6 : e >= 248 ? 5 : e >= 240 ? 4 : e >= 224 ? 3 : e >= 192 ? 2 : 1;
Dt[254] = Dt[254] = 1;
var yr = (e) => {
  if (typeof TextEncoder == "function" && TextEncoder.prototype.encode)
    return new TextEncoder().encode(e);
  let n, t, i, a, l, f = e.length, r = 0;
  for (a = 0; a < f; a++)
    t = e.charCodeAt(a), (t & 64512) === 55296 && a + 1 < f && (i = e.charCodeAt(a + 1), (i & 64512) === 56320 && (t = 65536 + (t - 55296 << 10) + (i - 56320), a++)), r += t < 128 ? 1 : t < 2048 ? 2 : t < 65536 ? 3 : 4;
  for (n = new Uint8Array(r), l = 0, a = 0; l < r; a++)
    t = e.charCodeAt(a), (t & 64512) === 55296 && a + 1 < f && (i = e.charCodeAt(a + 1), (i & 64512) === 56320 && (t = 65536 + (t - 55296 << 10) + (i - 56320), a++)), t < 128 ? n[l++] = t : t < 2048 ? (n[l++] = 192 | t >>> 6, n[l++] = 128 | t & 63) : t < 65536 ? (n[l++] = 224 | t >>> 12, n[l++] = 128 | t >>> 6 & 63, n[l++] = 128 | t & 63) : (n[l++] = 240 | t >>> 18, n[l++] = 128 | t >>> 12 & 63, n[l++] = 128 | t >>> 6 & 63, n[l++] = 128 | t & 63);
  return n;
};
const kr = (e, n) => {
  if (n < 65534 && e.subarray && xl)
    return String.fromCharCode.apply(null, e.length === n ? e : e.subarray(0, n));
  let t = "";
  for (let i = 0; i < n; i++)
    t += String.fromCharCode(e[i]);
  return t;
};
var Er = (e, n) => {
  const t = n || e.length;
  if (typeof TextDecoder == "function" && TextDecoder.prototype.decode)
    return new TextDecoder().decode(e.subarray(0, n));
  let i, a;
  const l = new Array(t * 2);
  for (a = 0, i = 0; i < t; ) {
    let f = e[i++];
    if (f < 128) {
      l[a++] = f;
      continue;
    }
    let r = Dt[f];
    if (r > 4) {
      l[a++] = 65533, i += r - 1;
      continue;
    }
    for (f &= r === 2 ? 31 : r === 3 ? 15 : 7; r > 1 && i < t; )
      f = f << 6 | e[i++] & 63, r--;
    if (r > 1) {
      l[a++] = 65533;
      continue;
    }
    f < 65536 ? l[a++] = f : (f -= 65536, l[a++] = 55296 | f >> 10 & 1023, l[a++] = 56320 | f & 1023);
  }
  return kr(l, a);
}, Ar = (e, n) => {
  n = n || e.length, n > e.length && (n = e.length);
  let t = n - 1;
  for (; t >= 0 && (e[t] & 192) === 128; )
    t--;
  return t < 0 || t === 0 ? n : t + Dt[e[t]] > n ? t : n;
}, It = {
  string2buf: yr,
  buf2string: Er,
  utf8border: Ar
};
function Mr() {
  this.input = null, this.next_in = 0, this.avail_in = 0, this.total_in = 0, this.output = null, this.next_out = 0, this.avail_out = 0, this.total_out = 0, this.msg = "", this.state = null, this.data_type = 2, this.adler = 0;
}
var vl = Mr;
const yl = Object.prototype.toString, {
  Z_NO_FLUSH: Sr,
  Z_SYNC_FLUSH: zr,
  Z_FULL_FLUSH: Nr,
  Z_FINISH: Rr,
  Z_OK: ln,
  Z_STREAM_END: Tr,
  Z_DEFAULT_COMPRESSION: Dr,
  Z_DEFAULT_STRATEGY: Ir,
  Z_DEFLATED: Lr
} = $t;
function ri(e) {
  this.options = bn.assign({
    level: Dr,
    method: Lr,
    chunkSize: 16384,
    windowBits: 15,
    memLevel: 8,
    strategy: Ir
  }, e || {});
  let n = this.options;
  n.raw && n.windowBits > 0 ? n.windowBits = -n.windowBits : n.gzip && n.windowBits > 0 && n.windowBits < 16 && (n.windowBits += 16), this.err = 0, this.msg = "", this.ended = !1, this.chunks = [], this.strm = new vl(), this.strm.avail_out = 0;
  let t = Et.deflateInit2(
    this.strm,
    n.level,
    n.method,
    n.windowBits,
    n.memLevel,
    n.strategy
  );
  if (t !== ln)
    throw new Error(ft[t]);
  if (n.header && Et.deflateSetHeader(this.strm, n.header), n.dictionary) {
    let i;
    if (typeof n.dictionary == "string" ? i = It.string2buf(n.dictionary) : yl.call(n.dictionary) === "[object ArrayBuffer]" ? i = new Uint8Array(n.dictionary) : i = n.dictionary, t = Et.deflateSetDictionary(this.strm, i), t !== ln)
      throw new Error(ft[t]);
    this._dict_set = !0;
  }
}
ri.prototype.push = function(e, n) {
  const t = this.strm, i = this.options.chunkSize;
  let a, l;
  if (this.ended)
    return !1;
  for (n === ~~n ? l = n : l = n === !0 ? Rr : Sr, typeof e == "string" ? t.input = It.string2buf(e) : yl.call(e) === "[object ArrayBuffer]" ? t.input = new Uint8Array(e) : t.input = e, t.next_in = 0, t.avail_in = t.input.length; ; ) {
    if (t.avail_out === 0 && (t.output = new Uint8Array(i), t.next_out = 0, t.avail_out = i), (l === zr || l === Nr) && t.avail_out <= 6) {
      this.onData(t.output.subarray(0, t.next_out)), t.avail_out = 0;
      continue;
    }
    if (a = Et.deflate(t, l), a === Tr)
      return t.next_out > 0 && this.onData(t.output.subarray(0, t.next_out)), a = Et.deflateEnd(this.strm), this.onEnd(a), this.ended = !0, a === ln;
    if (t.avail_out === 0) {
      this.onData(t.output);
      continue;
    }
    if (l > 0 && t.next_out > 0) {
      this.onData(t.output.subarray(0, t.next_out)), t.avail_out = 0;
      continue;
    }
    if (t.avail_in === 0) break;
  }
  return !0;
};
ri.prototype.onData = function(e) {
  this.chunks.push(e);
};
ri.prototype.onEnd = function(e) {
  e === ln && (this.result = bn.flattenChunks(this.chunks)), this.chunks = [], this.err = e, this.msg = this.strm.msg;
};
const Yt = 16209, Cr = 16191;
var Zr = function(n, t) {
  let i, a, l, f, r, s, o, c, h, d, u, _, v, y, A, x, k, g, p, R, z, E, m, T;
  const w = n.state;
  i = n.next_in, m = n.input, a = i + (n.avail_in - 5), l = n.next_out, T = n.output, f = l - (t - n.avail_out), r = l + (n.avail_out - 257), s = w.dmax, o = w.wsize, c = w.whave, h = w.wnext, d = w.window, u = w.hold, _ = w.bits, v = w.lencode, y = w.distcode, A = (1 << w.lenbits) - 1, x = (1 << w.distbits) - 1;
  e:
    do {
      _ < 15 && (u += m[i++] << _, _ += 8, u += m[i++] << _, _ += 8), k = v[u & A];
      t:
        for (; ; ) {
          if (g = k >>> 24, u >>>= g, _ -= g, g = k >>> 16 & 255, g === 0)
            T[l++] = k & 65535;
          else if (g & 16) {
            p = k & 65535, g &= 15, g && (_ < g && (u += m[i++] << _, _ += 8), p += u & (1 << g) - 1, u >>>= g, _ -= g), _ < 15 && (u += m[i++] << _, _ += 8, u += m[i++] << _, _ += 8), k = y[u & x];
            n:
              for (; ; ) {
                if (g = k >>> 24, u >>>= g, _ -= g, g = k >>> 16 & 255, g & 16) {
                  if (R = k & 65535, g &= 15, _ < g && (u += m[i++] << _, _ += 8, _ < g && (u += m[i++] << _, _ += 8)), R += u & (1 << g) - 1, R > s) {
                    n.msg = "invalid distance too far back", w.mode = Yt;
                    break e;
                  }
                  if (u >>>= g, _ -= g, g = l - f, R > g) {
                    if (g = R - g, g > c && w.sane) {
                      n.msg = "invalid distance too far back", w.mode = Yt;
                      break e;
                    }
                    if (z = 0, E = d, h === 0) {
                      if (z += o - g, g < p) {
                        p -= g;
                        do
                          T[l++] = d[z++];
                        while (--g);
                        z = l - R, E = T;
                      }
                    } else if (h < g) {
                      if (z += o + h - g, g -= h, g < p) {
                        p -= g;
                        do
                          T[l++] = d[z++];
                        while (--g);
                        if (z = 0, h < p) {
                          g = h, p -= g;
                          do
                            T[l++] = d[z++];
                          while (--g);
                          z = l - R, E = T;
                        }
                      }
                    } else if (z += h - g, g < p) {
                      p -= g;
                      do
                        T[l++] = d[z++];
                      while (--g);
                      z = l - R, E = T;
                    }
                    for (; p > 2; )
                      T[l++] = E[z++], T[l++] = E[z++], T[l++] = E[z++], p -= 3;
                    p && (T[l++] = E[z++], p > 1 && (T[l++] = E[z++]));
                  } else {
                    z = l - R;
                    do
                      T[l++] = T[z++], T[l++] = T[z++], T[l++] = T[z++], p -= 3;
                    while (p > 2);
                    p && (T[l++] = T[z++], p > 1 && (T[l++] = T[z++]));
                  }
                } else if (g & 64) {
                  n.msg = "invalid distance code", w.mode = Yt;
                  break e;
                } else {
                  k = y[(k & 65535) + (u & (1 << g) - 1)];
                  continue n;
                }
                break;
              }
          } else if (g & 64)
            if (g & 32) {
              w.mode = Cr;
              break e;
            } else {
              n.msg = "invalid literal/length code", w.mode = Yt;
              break e;
            }
          else {
            k = v[(k & 65535) + (u & (1 << g) - 1)];
            continue t;
          }
          break;
        }
    } while (i < a && l < r);
  p = _ >> 3, i -= p, _ -= p << 3, u &= (1 << _) - 1, n.next_in = i, n.next_out = l, n.avail_in = i < a ? 5 + (a - i) : 5 - (i - a), n.avail_out = l < r ? 257 + (r - l) : 257 - (l - r), w.hold = u, w.bits = _;
};
const Je = 15, Si = 852, zi = 592, Ni = 0, An = 1, Ri = 2, Or = new Uint16Array([
  /* Length codes 257..285 base */
  3,
  4,
  5,
  6,
  7,
  8,
  9,
  10,
  11,
  13,
  15,
  17,
  19,
  23,
  27,
  31,
  35,
  43,
  51,
  59,
  67,
  83,
  99,
  115,
  131,
  163,
  195,
  227,
  258,
  0,
  0
]), Ur = new Uint8Array([
  /* Length codes 257..285 extra */
  16,
  16,
  16,
  16,
  16,
  16,
  16,
  16,
  17,
  17,
  17,
  17,
  18,
  18,
  18,
  18,
  19,
  19,
  19,
  19,
  20,
  20,
  20,
  20,
  21,
  21,
  21,
  21,
  16,
  72,
  78
]), Fr = new Uint16Array([
  /* Distance codes 0..29 base */
  1,
  2,
  3,
  4,
  5,
  7,
  9,
  13,
  17,
  25,
  33,
  49,
  65,
  97,
  129,
  193,
  257,
  385,
  513,
  769,
  1025,
  1537,
  2049,
  3073,
  4097,
  6145,
  8193,
  12289,
  16385,
  24577,
  0,
  0
]), Hr = new Uint8Array([
  /* Distance codes 0..29 extra */
  16,
  16,
  16,
  16,
  17,
  17,
  18,
  18,
  19,
  19,
  20,
  20,
  21,
  21,
  22,
  22,
  23,
  23,
  24,
  24,
  25,
  25,
  26,
  26,
  27,
  27,
  28,
  28,
  29,
  29,
  64,
  64
]), $r = (e, n, t, i, a, l, f, r) => {
  const s = r.bits;
  let o = 0, c = 0, h = 0, d = 0, u = 0, _ = 0, v = 0, y = 0, A = 0, x = 0, k, g, p, R, z, E = null, m;
  const T = new Uint16Array(Je + 1), w = new Uint16Array(Je + 1);
  let I = null, N, O, V;
  for (o = 0; o <= Je; o++)
    T[o] = 0;
  for (c = 0; c < i; c++)
    T[n[t + c]]++;
  for (u = s, d = Je; d >= 1 && T[d] === 0; d--)
    ;
  if (u > d && (u = d), d === 0)
    return a[l++] = 1 << 24 | 64 << 16 | 0, a[l++] = 1 << 24 | 64 << 16 | 0, r.bits = 1, 0;
  for (h = 1; h < d && T[h] === 0; h++)
    ;
  for (u < h && (u = h), y = 1, o = 1; o <= Je; o++)
    if (y <<= 1, y -= T[o], y < 0)
      return -1;
  if (y > 0 && (e === Ni || d !== 1))
    return -1;
  for (w[1] = 0, o = 1; o < Je; o++)
    w[o + 1] = w[o] + T[o];
  for (c = 0; c < i; c++)
    n[t + c] !== 0 && (f[w[n[t + c]]++] = c);
  if (e === Ni ? (E = I = f, m = 20) : e === An ? (E = Or, I = Ur, m = 257) : (E = Fr, I = Hr, m = 0), x = 0, c = 0, o = h, z = l, _ = u, v = 0, p = -1, A = 1 << u, R = A - 1, e === An && A > Si || e === Ri && A > zi)
    return 1;
  for (; ; ) {
    N = o - v, f[c] + 1 < m ? (O = 0, V = f[c]) : f[c] >= m ? (O = I[f[c] - m], V = E[f[c] - m]) : (O = 96, V = 0), k = 1 << o - v, g = 1 << _, h = g;
    do
      g -= k, a[z + (x >> v) + g] = N << 24 | O << 16 | V | 0;
    while (g !== 0);
    for (k = 1 << o - 1; x & k; )
      k >>= 1;
    if (k !== 0 ? (x &= k - 1, x += k) : x = 0, c++, --T[o] === 0) {
      if (o === d)
        break;
      o = n[t + f[c]];
    }
    if (o > u && (x & R) !== p) {
      for (v === 0 && (v = u), z += h, _ = o - v, y = 1 << _; _ + v < d && (y -= T[_ + v], !(y <= 0)); )
        _++, y <<= 1;
      if (A += 1 << _, e === An && A > Si || e === Ri && A > zi)
        return 1;
      p = x & R, a[p] = u << 24 | _ << 16 | z - l | 0;
    }
  }
  return x !== 0 && (a[z + x] = o - v << 24 | 64 << 16 | 0), r.bits = u, 0;
};
var At = $r;
const Br = 0, kl = 1, El = 2, {
  Z_FINISH: Ti,
  Z_BLOCK: Pr,
  Z_TREES: Gt,
  Z_OK: je,
  Z_STREAM_END: jr,
  Z_NEED_DICT: Xr,
  Z_STREAM_ERROR: he,
  Z_DATA_ERROR: Al,
  Z_MEM_ERROR: Ml,
  Z_BUF_ERROR: Kr,
  Z_DEFLATED: Di
} = $t, gn = 16180, Ii = 16181, Li = 16182, Ci = 16183, Zi = 16184, Oi = 16185, Ui = 16186, Fi = 16187, Hi = 16188, $i = 16189, fn = 16190, Se = 16191, Mn = 16192, Bi = 16193, Sn = 16194, Pi = 16195, ji = 16196, Xi = 16197, Ki = 16198, Vt = 16199, qt = 16200, Yi = 16201, Gi = 16202, Vi = 16203, qi = 16204, Wi = 16205, zn = 16206, Ji = 16207, Qi = 16208, X = 16209, Sl = 16210, zl = 16211, Yr = 852, Gr = 592, Vr = 15, qr = Vr, ea = (e) => (e >>> 24 & 255) + (e >>> 8 & 65280) + ((e & 65280) << 8) + ((e & 255) << 24);
function Wr() {
  this.strm = null, this.mode = 0, this.last = !1, this.wrap = 0, this.havedict = !1, this.flags = 0, this.dmax = 0, this.check = 0, this.total = 0, this.head = null, this.wbits = 0, this.wsize = 0, this.whave = 0, this.wnext = 0, this.window = null, this.hold = 0, this.bits = 0, this.length = 0, this.offset = 0, this.extra = 0, this.lencode = null, this.distcode = null, this.lenbits = 0, this.distbits = 0, this.ncode = 0, this.nlen = 0, this.ndist = 0, this.have = 0, this.next = null, this.lens = new Uint16Array(320), this.work = new Uint16Array(288), this.lendyn = null, this.distdyn = null, this.sane = 0, this.back = 0, this.was = 0;
}
const Xe = (e) => {
  if (!e)
    return 1;
  const n = e.state;
  return !n || n.strm !== e || n.mode < gn || n.mode > zl ? 1 : 0;
}, Nl = (e) => {
  if (Xe(e))
    return he;
  const n = e.state;
  return e.total_in = e.total_out = n.total = 0, e.msg = "", n.wrap && (e.adler = n.wrap & 1), n.mode = gn, n.last = 0, n.havedict = 0, n.flags = -1, n.dmax = 32768, n.head = null, n.hold = 0, n.bits = 0, n.lencode = n.lendyn = new Int32Array(Yr), n.distcode = n.distdyn = new Int32Array(Gr), n.sane = 1, n.back = -1, je;
}, Rl = (e) => {
  if (Xe(e))
    return he;
  const n = e.state;
  return n.wsize = 0, n.whave = 0, n.wnext = 0, Nl(e);
}, Tl = (e, n) => {
  let t;
  if (Xe(e))
    return he;
  const i = e.state;
  return n < 0 ? (t = 0, n = -n) : (t = (n >> 4) + 5, n < 48 && (n &= 15)), n && (n < 8 || n > 15) ? he : (i.window !== null && i.wbits !== n && (i.window = null), i.wrap = t, i.wbits = n, Rl(e));
}, Dl = (e, n) => {
  if (!e)
    return he;
  const t = new Wr();
  e.state = t, t.strm = e, t.window = null, t.mode = gn;
  const i = Tl(e, n);
  return i !== je && (e.state = null), i;
}, Jr = (e) => Dl(e, qr);
let ta = !0, Nn, Rn;
const Qr = (e) => {
  if (ta) {
    Nn = new Int32Array(512), Rn = new Int32Array(32);
    let n = 0;
    for (; n < 144; )
      e.lens[n++] = 8;
    for (; n < 256; )
      e.lens[n++] = 9;
    for (; n < 280; )
      e.lens[n++] = 7;
    for (; n < 288; )
      e.lens[n++] = 8;
    for (At(kl, e.lens, 0, 288, Nn, 0, e.work, { bits: 9 }), n = 0; n < 32; )
      e.lens[n++] = 5;
    At(El, e.lens, 0, 32, Rn, 0, e.work, { bits: 5 }), ta = !1;
  }
  e.lencode = Nn, e.lenbits = 9, e.distcode = Rn, e.distbits = 5;
}, Il = (e, n, t, i) => {
  let a;
  const l = e.state;
  return l.window === null && (l.wsize = 1 << l.wbits, l.wnext = 0, l.whave = 0, l.window = new Uint8Array(l.wsize)), i >= l.wsize ? (l.window.set(n.subarray(t - l.wsize, t), 0), l.wnext = 0, l.whave = l.wsize) : (a = l.wsize - l.wnext, a > i && (a = i), l.window.set(n.subarray(t - i, t - i + a), l.wnext), i -= a, i ? (l.window.set(n.subarray(t - i, t), 0), l.wnext = i, l.whave = l.wsize) : (l.wnext += a, l.wnext === l.wsize && (l.wnext = 0), l.whave < l.wsize && (l.whave += a))), 0;
}, eo = (e, n) => {
  let t, i, a, l, f, r, s, o, c, h, d, u, _, v, y = 0, A, x, k, g, p, R, z, E;
  const m = new Uint8Array(4);
  let T, w;
  const I = (
    /* permutation of code lengths */
    new Uint8Array([16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15])
  );
  if (Xe(e) || !e.output || !e.input && e.avail_in !== 0)
    return he;
  t = e.state, t.mode === Se && (t.mode = Mn), f = e.next_out, a = e.output, s = e.avail_out, l = e.next_in, i = e.input, r = e.avail_in, o = t.hold, c = t.bits, h = r, d = s, E = je;
  e:
    for (; ; )
      switch (t.mode) {
        case gn:
          if (t.wrap === 0) {
            t.mode = Mn;
            break;
          }
          for (; c < 16; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          if (t.wrap & 2 && o === 35615) {
            t.wbits === 0 && (t.wbits = 15), t.check = 0, m[0] = o & 255, m[1] = o >>> 8 & 255, t.check = q(t.check, m, 2, 0), o = 0, c = 0, t.mode = Ii;
            break;
          }
          if (t.head && (t.head.done = !1), !(t.wrap & 1) || /* check if zlib header allowed */
          (((o & 255) << 8) + (o >> 8)) % 31) {
            e.msg = "incorrect header check", t.mode = X;
            break;
          }
          if ((o & 15) !== Di) {
            e.msg = "unknown compression method", t.mode = X;
            break;
          }
          if (o >>>= 4, c -= 4, z = (o & 15) + 8, t.wbits === 0 && (t.wbits = z), z > 15 || z > t.wbits) {
            e.msg = "invalid window size", t.mode = X;
            break;
          }
          t.dmax = 1 << t.wbits, t.flags = 0, e.adler = t.check = 1, t.mode = o & 512 ? $i : Se, o = 0, c = 0;
          break;
        case Ii:
          for (; c < 16; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          if (t.flags = o, (t.flags & 255) !== Di) {
            e.msg = "unknown compression method", t.mode = X;
            break;
          }
          if (t.flags & 57344) {
            e.msg = "unknown header flags set", t.mode = X;
            break;
          }
          t.head && (t.head.text = o >> 8 & 1), t.flags & 512 && t.wrap & 4 && (m[0] = o & 255, m[1] = o >>> 8 & 255, t.check = q(t.check, m, 2, 0)), o = 0, c = 0, t.mode = Li;
        case Li:
          for (; c < 32; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          t.head && (t.head.time = o), t.flags & 512 && t.wrap & 4 && (m[0] = o & 255, m[1] = o >>> 8 & 255, m[2] = o >>> 16 & 255, m[3] = o >>> 24 & 255, t.check = q(t.check, m, 4, 0)), o = 0, c = 0, t.mode = Ci;
        case Ci:
          for (; c < 16; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          t.head && (t.head.xflags = o & 255, t.head.os = o >> 8), t.flags & 512 && t.wrap & 4 && (m[0] = o & 255, m[1] = o >>> 8 & 255, t.check = q(t.check, m, 2, 0)), o = 0, c = 0, t.mode = Zi;
        case Zi:
          if (t.flags & 1024) {
            for (; c < 16; ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            t.length = o, t.head && (t.head.extra_len = o), t.flags & 512 && t.wrap & 4 && (m[0] = o & 255, m[1] = o >>> 8 & 255, t.check = q(t.check, m, 2, 0)), o = 0, c = 0;
          } else t.head && (t.head.extra = null);
          t.mode = Oi;
        case Oi:
          if (t.flags & 1024 && (u = t.length, u > r && (u = r), u && (t.head && (z = t.head.extra_len - t.length, t.head.extra || (t.head.extra = new Uint8Array(t.head.extra_len)), t.head.extra.set(
            i.subarray(
              l,
              // extra field is limited to 65536 bytes
              // - no need for additional size check
              l + u
            ),
            /*len + copy > state.head.extra_max - len ? state.head.extra_max : copy,*/
            z
          )), t.flags & 512 && t.wrap & 4 && (t.check = q(t.check, i, u, l)), r -= u, l += u, t.length -= u), t.length))
            break e;
          t.length = 0, t.mode = Ui;
        case Ui:
          if (t.flags & 2048) {
            if (r === 0)
              break e;
            u = 0;
            do
              z = i[l + u++], t.head && z && t.length < 65536 && (t.head.name += String.fromCharCode(z));
            while (z && u < r);
            if (t.flags & 512 && t.wrap & 4 && (t.check = q(t.check, i, u, l)), r -= u, l += u, z)
              break e;
          } else t.head && (t.head.name = null);
          t.length = 0, t.mode = Fi;
        case Fi:
          if (t.flags & 4096) {
            if (r === 0)
              break e;
            u = 0;
            do
              z = i[l + u++], t.head && z && t.length < 65536 && (t.head.comment += String.fromCharCode(z));
            while (z && u < r);
            if (t.flags & 512 && t.wrap & 4 && (t.check = q(t.check, i, u, l)), r -= u, l += u, z)
              break e;
          } else t.head && (t.head.comment = null);
          t.mode = Hi;
        case Hi:
          if (t.flags & 512) {
            for (; c < 16; ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            if (t.wrap & 4 && o !== (t.check & 65535)) {
              e.msg = "header crc mismatch", t.mode = X;
              break;
            }
            o = 0, c = 0;
          }
          t.head && (t.head.hcrc = t.flags >> 9 & 1, t.head.done = !0), e.adler = t.check = 0, t.mode = Se;
          break;
        case $i:
          for (; c < 32; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          e.adler = t.check = ea(o), o = 0, c = 0, t.mode = fn;
        case fn:
          if (t.havedict === 0)
            return e.next_out = f, e.avail_out = s, e.next_in = l, e.avail_in = r, t.hold = o, t.bits = c, Xr;
          e.adler = t.check = 1, t.mode = Se;
        case Se:
          if (n === Pr || n === Gt)
            break e;
        case Mn:
          if (t.last) {
            o >>>= c & 7, c -= c & 7, t.mode = zn;
            break;
          }
          for (; c < 3; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          switch (t.last = o & 1, o >>>= 1, c -= 1, o & 3) {
            case 0:
              t.mode = Bi;
              break;
            case 1:
              if (Qr(t), t.mode = Vt, n === Gt) {
                o >>>= 2, c -= 2;
                break e;
              }
              break;
            case 2:
              t.mode = ji;
              break;
            case 3:
              e.msg = "invalid block type", t.mode = X;
          }
          o >>>= 2, c -= 2;
          break;
        case Bi:
          for (o >>>= c & 7, c -= c & 7; c < 32; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          if ((o & 65535) !== (o >>> 16 ^ 65535)) {
            e.msg = "invalid stored block lengths", t.mode = X;
            break;
          }
          if (t.length = o & 65535, o = 0, c = 0, t.mode = Sn, n === Gt)
            break e;
        case Sn:
          t.mode = Pi;
        case Pi:
          if (u = t.length, u) {
            if (u > r && (u = r), u > s && (u = s), u === 0)
              break e;
            a.set(i.subarray(l, l + u), f), r -= u, l += u, s -= u, f += u, t.length -= u;
            break;
          }
          t.mode = Se;
          break;
        case ji:
          for (; c < 14; ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          if (t.nlen = (o & 31) + 257, o >>>= 5, c -= 5, t.ndist = (o & 31) + 1, o >>>= 5, c -= 5, t.ncode = (o & 15) + 4, o >>>= 4, c -= 4, t.nlen > 286 || t.ndist > 30) {
            e.msg = "too many length or distance symbols", t.mode = X;
            break;
          }
          t.have = 0, t.mode = Xi;
        case Xi:
          for (; t.have < t.ncode; ) {
            for (; c < 3; ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            t.lens[I[t.have++]] = o & 7, o >>>= 3, c -= 3;
          }
          for (; t.have < 19; )
            t.lens[I[t.have++]] = 0;
          if (t.lencode = t.lendyn, t.lenbits = 7, T = { bits: t.lenbits }, E = At(Br, t.lens, 0, 19, t.lencode, 0, t.work, T), t.lenbits = T.bits, E) {
            e.msg = "invalid code lengths set", t.mode = X;
            break;
          }
          t.have = 0, t.mode = Ki;
        case Ki:
          for (; t.have < t.nlen + t.ndist; ) {
            for (; y = t.lencode[o & (1 << t.lenbits) - 1], A = y >>> 24, x = y >>> 16 & 255, k = y & 65535, !(A <= c); ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            if (k < 16)
              o >>>= A, c -= A, t.lens[t.have++] = k;
            else {
              if (k === 16) {
                for (w = A + 2; c < w; ) {
                  if (r === 0)
                    break e;
                  r--, o += i[l++] << c, c += 8;
                }
                if (o >>>= A, c -= A, t.have === 0) {
                  e.msg = "invalid bit length repeat", t.mode = X;
                  break;
                }
                z = t.lens[t.have - 1], u = 3 + (o & 3), o >>>= 2, c -= 2;
              } else if (k === 17) {
                for (w = A + 3; c < w; ) {
                  if (r === 0)
                    break e;
                  r--, o += i[l++] << c, c += 8;
                }
                o >>>= A, c -= A, z = 0, u = 3 + (o & 7), o >>>= 3, c -= 3;
              } else {
                for (w = A + 7; c < w; ) {
                  if (r === 0)
                    break e;
                  r--, o += i[l++] << c, c += 8;
                }
                o >>>= A, c -= A, z = 0, u = 11 + (o & 127), o >>>= 7, c -= 7;
              }
              if (t.have + u > t.nlen + t.ndist) {
                e.msg = "invalid bit length repeat", t.mode = X;
                break;
              }
              for (; u--; )
                t.lens[t.have++] = z;
            }
          }
          if (t.mode === X)
            break;
          if (t.lens[256] === 0) {
            e.msg = "invalid code -- missing end-of-block", t.mode = X;
            break;
          }
          if (t.lenbits = 9, T = { bits: t.lenbits }, E = At(kl, t.lens, 0, t.nlen, t.lencode, 0, t.work, T), t.lenbits = T.bits, E) {
            e.msg = "invalid literal/lengths set", t.mode = X;
            break;
          }
          if (t.distbits = 6, t.distcode = t.distdyn, T = { bits: t.distbits }, E = At(El, t.lens, t.nlen, t.ndist, t.distcode, 0, t.work, T), t.distbits = T.bits, E) {
            e.msg = "invalid distances set", t.mode = X;
            break;
          }
          if (t.mode = Vt, n === Gt)
            break e;
        case Vt:
          t.mode = qt;
        case qt:
          if (r >= 6 && s >= 258) {
            e.next_out = f, e.avail_out = s, e.next_in = l, e.avail_in = r, t.hold = o, t.bits = c, Zr(e, d), f = e.next_out, a = e.output, s = e.avail_out, l = e.next_in, i = e.input, r = e.avail_in, o = t.hold, c = t.bits, t.mode === Se && (t.back = -1);
            break;
          }
          for (t.back = 0; y = t.lencode[o & (1 << t.lenbits) - 1], A = y >>> 24, x = y >>> 16 & 255, k = y & 65535, !(A <= c); ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          if (x && !(x & 240)) {
            for (g = A, p = x, R = k; y = t.lencode[R + ((o & (1 << g + p) - 1) >> g)], A = y >>> 24, x = y >>> 16 & 255, k = y & 65535, !(g + A <= c); ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            o >>>= g, c -= g, t.back += g;
          }
          if (o >>>= A, c -= A, t.back += A, t.length = k, x === 0) {
            t.mode = Wi;
            break;
          }
          if (x & 32) {
            t.back = -1, t.mode = Se;
            break;
          }
          if (x & 64) {
            e.msg = "invalid literal/length code", t.mode = X;
            break;
          }
          t.extra = x & 15, t.mode = Yi;
        case Yi:
          if (t.extra) {
            for (w = t.extra; c < w; ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            t.length += o & (1 << t.extra) - 1, o >>>= t.extra, c -= t.extra, t.back += t.extra;
          }
          t.was = t.length, t.mode = Gi;
        case Gi:
          for (; y = t.distcode[o & (1 << t.distbits) - 1], A = y >>> 24, x = y >>> 16 & 255, k = y & 65535, !(A <= c); ) {
            if (r === 0)
              break e;
            r--, o += i[l++] << c, c += 8;
          }
          if (!(x & 240)) {
            for (g = A, p = x, R = k; y = t.distcode[R + ((o & (1 << g + p) - 1) >> g)], A = y >>> 24, x = y >>> 16 & 255, k = y & 65535, !(g + A <= c); ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            o >>>= g, c -= g, t.back += g;
          }
          if (o >>>= A, c -= A, t.back += A, x & 64) {
            e.msg = "invalid distance code", t.mode = X;
            break;
          }
          t.offset = k, t.extra = x & 15, t.mode = Vi;
        case Vi:
          if (t.extra) {
            for (w = t.extra; c < w; ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            t.offset += o & (1 << t.extra) - 1, o >>>= t.extra, c -= t.extra, t.back += t.extra;
          }
          if (t.offset > t.dmax) {
            e.msg = "invalid distance too far back", t.mode = X;
            break;
          }
          t.mode = qi;
        case qi:
          if (s === 0)
            break e;
          if (u = d - s, t.offset > u) {
            if (u = t.offset - u, u > t.whave && t.sane) {
              e.msg = "invalid distance too far back", t.mode = X;
              break;
            }
            u > t.wnext ? (u -= t.wnext, _ = t.wsize - u) : _ = t.wnext - u, u > t.length && (u = t.length), v = t.window;
          } else
            v = a, _ = f - t.offset, u = t.length;
          u > s && (u = s), s -= u, t.length -= u;
          do
            a[f++] = v[_++];
          while (--u);
          t.length === 0 && (t.mode = qt);
          break;
        case Wi:
          if (s === 0)
            break e;
          a[f++] = t.length, s--, t.mode = qt;
          break;
        case zn:
          if (t.wrap) {
            for (; c < 32; ) {
              if (r === 0)
                break e;
              r--, o |= i[l++] << c, c += 8;
            }
            if (d -= s, e.total_out += d, t.total += d, t.wrap & 4 && d && (e.adler = t.check = /*UPDATE_CHECK(state.check, put - _out, _out);*/
            t.flags ? q(t.check, a, d, f - d) : Tt(t.check, a, d, f - d)), d = s, t.wrap & 4 && (t.flags ? o : ea(o)) !== t.check) {
              e.msg = "incorrect data check", t.mode = X;
              break;
            }
            o = 0, c = 0;
          }
          t.mode = Ji;
        case Ji:
          if (t.wrap && t.flags) {
            for (; c < 32; ) {
              if (r === 0)
                break e;
              r--, o += i[l++] << c, c += 8;
            }
            if (t.wrap & 4 && o !== (t.total & 4294967295)) {
              e.msg = "incorrect length check", t.mode = X;
              break;
            }
            o = 0, c = 0;
          }
          t.mode = Qi;
        case Qi:
          E = jr;
          break e;
        case X:
          E = Al;
          break e;
        case Sl:
          return Ml;
        case zl:
        default:
          return he;
      }
  return e.next_out = f, e.avail_out = s, e.next_in = l, e.avail_in = r, t.hold = o, t.bits = c, (t.wsize || d !== e.avail_out && t.mode < X && (t.mode < zn || n !== Ti)) && Il(e, e.output, e.next_out, d - e.avail_out), h -= e.avail_in, d -= e.avail_out, e.total_in += h, e.total_out += d, t.total += d, t.wrap & 4 && d && (e.adler = t.check = /*UPDATE_CHECK(state.check, strm.next_out - _out, _out);*/
  t.flags ? q(t.check, a, d, e.next_out - d) : Tt(t.check, a, d, e.next_out - d)), e.data_type = t.bits + (t.last ? 64 : 0) + (t.mode === Se ? 128 : 0) + (t.mode === Vt || t.mode === Sn ? 256 : 0), (h === 0 && d === 0 || n === Ti) && E === je && (E = Kr), E;
}, to = (e) => {
  if (Xe(e))
    return he;
  let n = e.state;
  return n.window && (n.window = null), e.state = null, je;
}, no = (e, n) => {
  if (Xe(e))
    return he;
  const t = e.state;
  return t.wrap & 2 ? (t.head = n, n.done = !1, je) : he;
}, io = (e, n) => {
  const t = n.length;
  let i, a, l;
  return Xe(e) || (i = e.state, i.wrap !== 0 && i.mode !== fn) ? he : i.mode === fn && (a = 1, a = Tt(a, n, t, 0), a !== i.check) ? Al : (l = Il(e, n, t, t), l ? (i.mode = Sl, Ml) : (i.havedict = 1, je));
};
var ao = Rl, lo = Tl, fo = Nl, ro = Jr, oo = Dl, so = eo, co = to, ho = no, uo = io, _o = "pako inflate (from Nodeca project)", Ne = {
  inflateReset: ao,
  inflateReset2: lo,
  inflateResetKeep: fo,
  inflateInit: ro,
  inflateInit2: oo,
  inflate: so,
  inflateEnd: co,
  inflateGetHeader: ho,
  inflateSetDictionary: uo,
  inflateInfo: _o
};
function bo() {
  this.text = 0, this.time = 0, this.xflags = 0, this.os = 0, this.extra = null, this.extra_len = 0, this.name = "", this.comment = "", this.hcrc = 0, this.done = !1;
}
var go = bo;
const Ll = Object.prototype.toString, {
  Z_NO_FLUSH: mo,
  Z_FINISH: po,
  Z_OK: Lt,
  Z_STREAM_END: Tn,
  Z_NEED_DICT: Dn,
  Z_STREAM_ERROR: wo,
  Z_DATA_ERROR: na,
  Z_MEM_ERROR: xo
} = $t;
function Pt(e) {
  this.options = bn.assign({
    chunkSize: 1024 * 64,
    windowBits: 15,
    to: ""
  }, e || {});
  const n = this.options;
  n.raw && n.windowBits >= 0 && n.windowBits < 16 && (n.windowBits = -n.windowBits, n.windowBits === 0 && (n.windowBits = -15)), n.windowBits >= 0 && n.windowBits < 16 && !(e && e.windowBits) && (n.windowBits += 32), n.windowBits > 15 && n.windowBits < 48 && (n.windowBits & 15 || (n.windowBits |= 15)), this.err = 0, this.msg = "", this.ended = !1, this.chunks = [], this.strm = new vl(), this.strm.avail_out = 0;
  let t = Ne.inflateInit2(
    this.strm,
    n.windowBits
  );
  if (t !== Lt)
    throw new Error(ft[t]);
  if (this.header = new go(), Ne.inflateGetHeader(this.strm, this.header), n.dictionary && (typeof n.dictionary == "string" ? n.dictionary = It.string2buf(n.dictionary) : Ll.call(n.dictionary) === "[object ArrayBuffer]" && (n.dictionary = new Uint8Array(n.dictionary)), n.raw && (t = Ne.inflateSetDictionary(this.strm, n.dictionary), t !== Lt)))
    throw new Error(ft[t]);
}
Pt.prototype.push = function(e, n) {
  const t = this.strm, i = this.options.chunkSize, a = this.options.dictionary;
  let l, f, r;
  if (this.ended) return !1;
  for (n === ~~n ? f = n : f = n === !0 ? po : mo, Ll.call(e) === "[object ArrayBuffer]" ? t.input = new Uint8Array(e) : t.input = e, t.next_in = 0, t.avail_in = t.input.length; ; ) {
    for (t.avail_out === 0 && (t.output = new Uint8Array(i), t.next_out = 0, t.avail_out = i), l = Ne.inflate(t, f), l === Dn && a && (l = Ne.inflateSetDictionary(t, a), l === Lt ? l = Ne.inflate(t, f) : l === na && (l = Dn)); t.avail_in > 0 && l === Tn && t.state.wrap > 0 && e[t.next_in] !== 0; )
      Ne.inflateReset(t), l = Ne.inflate(t, f);
    switch (l) {
      case wo:
      case na:
      case Dn:
      case xo:
        return this.onEnd(l), this.ended = !0, !1;
    }
    if (r = t.avail_out, t.next_out && (t.avail_out === 0 || l === Tn))
      if (this.options.to === "string") {
        let s = It.utf8border(t.output, t.next_out), o = t.next_out - s, c = It.buf2string(t.output, s);
        t.next_out = o, t.avail_out = i - o, o && t.output.set(t.output.subarray(s, s + o), 0), this.onData(c);
      } else
        this.onData(t.output.length === t.next_out ? t.output : t.output.subarray(0, t.next_out));
    if (!(l === Lt && r === 0)) {
      if (l === Tn)
        return l = Ne.inflateEnd(this.strm), this.onEnd(l), this.ended = !0, !0;
      if (t.avail_in === 0) break;
    }
  }
  return !0;
};
Pt.prototype.onData = function(e) {
  this.chunks.push(e);
};
Pt.prototype.onEnd = function(e) {
  e === Lt && (this.options.to === "string" ? this.result = this.chunks.join("") : this.result = bn.flattenChunks(this.chunks)), this.chunks = [], this.err = e, this.msg = this.strm.msg;
};
function oi(e, n) {
  const t = new Pt(n);
  if (t.push(e), t.err) throw t.msg || ft[t.err];
  return t.result;
}
function vo(e, n) {
  return n = n || {}, n.raw = !0, oi(e, n);
}
var yo = Pt, ko = oi, Eo = vo, Ao = oi, Mo = $t, So = {
  Inflate: yo,
  inflate: ko,
  inflateRaw: Eo,
  ungzip: Ao,
  constants: Mo
};
const { Inflate: qs, inflate: zo, inflateRaw: Ws, ungzip: Js } = So;
var No = zo;
function Ro(e) {
  let n = atob(e), t = new Uint8Array(n.length);
  for (let i = 0; i < n.length; i++)
    t[i] = n.charCodeAt(i);
  return t;
}
class tt {
  /** Create a tensor.
   * @param shape the tensor's shape, e.g., [10, 10, 20, 10].
   * @param dtype the data type, e.g., float32.
   * @param buffer an ArrayBuffer-like object that stores the binary data of the tensor.
   */
  constructor(n, t, i) {
    pe(this, "shape");
    pe(this, "strides");
    pe(this, "dtype");
    pe(this, "storage");
    this.shape = n, this.dtype = t, this.strides = [];
    let a = 1;
    for (let f = n.length - 1; f >= 0; f--)
      this.strides.unshift(a), a *= this.shape[f];
    let l = a;
    switch (t) {
      case "int8":
        this.storage = i == null ? new Int8Array(l) : new Int8Array(i);
        break;
      case "uint8":
        this.storage = i == null ? new Uint8Array(l) : new Uint8Array(i);
        break;
      case "int16":
        this.storage = i == null ? new Int16Array(l) : new Int16Array(i);
        break;
      case "uint16":
        this.storage = i == null ? new Uint16Array(l) : new Uint16Array(i);
        break;
      case "int32":
        this.storage = i == null ? new Int32Array(l) : new Int32Array(i);
        break;
      case "uint32":
        this.storage = i == null ? new Uint32Array(l) : new Uint32Array(i);
        break;
      case "float32":
        this.storage = i == null ? new Float32Array(l) : new Float32Array(i);
        break;
      case "float64":
        this.storage = i == null ? new Float64Array(l) : new Float64Array(i);
        break;
      default:
        throw new Error("unknown data type " + t);
    }
  }
  /** Create a tensor from JSON data. */
  static fromJSON(n) {
    let t = Ro(n.data);
    switch (n.compression) {
      case "zlib":
        t = No(t);
        break;
    }
    if (n.shuffle != null) {
      let i = new Uint8Array(t.length), a = n.shuffle, l = t.length / a;
      for (let f = 0; f < t.length; f += a) {
        let r = f / a;
        for (let s = 0; s < a; s++)
          i[f + s] = t[r + l * s];
      }
      t = i;
    }
    return new tt(n.shape, n.dtype, t.buffer);
  }
  offset(...n) {
    let t = 0, i = this.strides;
    for (let a = 0; a < i.length; a++)
      t += n[a] * i[a];
    return t;
  }
  at(...n) {
    return this.storage[this.offset(...n)];
  }
  get(...n) {
    let t = this;
    for (let i of n)
      t = t.sliceFirstDimension(i);
    return t;
  }
  extents() {
    let n = 0, t = 1 / 0, i = -1 / 0, a = this.storage;
    for (let l = 0; l < a.length; l++) {
      let f = this.storage[l];
      f < t && (t = f), f > 0 && f < n && (n = f), f > i && (i = f);
    }
    return { min: t, max: i, minPositive: n };
  }
  clone() {
    let n = this.storage.slice();
    return new tt(this.shape.slice(), this.dtype, n.buffer);
  }
  sliceFirstDimension(n) {
    let t = this.storage.length / this.shape[0], i = n * t;
    return new tt(this.shape.slice(1), this.dtype, this.storage.subarray(i, i + t));
  }
  /** Perform a reduce operation at a given dimension, return the resulting tensor.
   * @param dimension the index to the dimension to reduce.
   * @param operation the reduce operation.
   * @returns a tensor where the given dimension is reduced.
   */
  reduce(n, t, i) {
    let a = this.shape[n], l = 1;
    for (let c = this.shape.length - 1; c > n; c--)
      l *= this.shape[c];
    let f = this.shape.slice();
    f[n] = 1;
    let r = new tt(f, i ?? this.dtype), s = 0, o = 0;
    for (; s < r.storage.length; ) {
      let c = r.storage.subarray(s, s + l);
      for (let h = 0; h < a; h++) {
        let d = this.storage.subarray(o, o + l);
        if (h == 0)
          c.set(d);
        else
          for (let u = 0; u < l; u++)
            c[u] = t(c[u], d[u]);
        o += l;
      }
      s += l;
    }
    return r;
  }
  sum(n) {
    return this.reduce(n, (t, i) => t + i);
  }
  mean(n) {
    let t = this.shape[n], i = this.sum(n);
    for (let a = 0; a < i.storage.length; a++)
      i.storage[a] /= t;
    return i;
  }
  min(n) {
    return this.reduce(n, (t, i) => Math.min(t, i));
  }
  max(n) {
    return this.reduce(n, (t, i) => Math.max(t, i));
  }
}
function fe() {
}
function Cl(e) {
  return e();
}
function ia() {
  return /* @__PURE__ */ Object.create(null);
}
function Ke(e) {
  e.forEach(Cl);
}
function Zl(e) {
  return typeof e == "function";
}
function Ye(e, n) {
  return e != e ? n == n : e !== n || e && typeof e == "object" || typeof e == "function";
}
function To(e) {
  return Object.keys(e).length === 0;
}
function S(e, n) {
  e.appendChild(n);
}
function jt(e, n, t) {
  const i = Do(e);
  if (!i.getElementById(n)) {
    const a = D("style");
    a.id = n, a.textContent = t, Io(i, a);
  }
}
function Do(e) {
  if (!e) return document;
  const n = e.getRootNode ? e.getRootNode() : e.ownerDocument;
  return n && /** @type {ShadowRoot} */
  n.host ? (
    /** @type {ShadowRoot} */
    n
  ) : e.ownerDocument;
}
function Io(e, n) {
  return S(
    /** @type {Document} */
    e.head || e,
    n
  ), n.sheet;
}
function C(e, n, t) {
  e.insertBefore(n, t || null);
}
function L(e) {
  e.parentNode && e.parentNode.removeChild(e);
}
function mt(e, n) {
  for (let t = 0; t < e.length; t += 1)
    e[t] && e[t].d(n);
}
function D(e) {
  return document.createElement(e);
}
function G(e) {
  return document.createElementNS("http://www.w3.org/2000/svg", e);
}
function j(e) {
  return document.createTextNode(e);
}
function K() {
  return j(" ");
}
function Ze() {
  return j("");
}
function ye(e, n, t, i) {
  return e.addEventListener(n, t, i), () => e.removeEventListener(n, t, i);
}
function b(e, n, t) {
  t == null ? e.removeAttribute(n) : e.getAttribute(n) !== t && e.setAttribute(n, t);
}
function Lo(e) {
  return e === "" ? null : +e;
}
function Co(e) {
  return Array.from(e.childNodes);
}
function W(e, n) {
  n = "" + n, e.data !== n && (e.data = /** @type {string} */
  n);
}
function de(e, n) {
  e.value = n ?? "";
}
function M(e, n, t, i) {
  t == null ? e.style.removeProperty(n) : e.style.setProperty(n, t, "");
}
function st(e, n, t) {
  for (let i = 0; i < e.options.length; i += 1) {
    const a = e.options[i];
    if (a.__value === n) {
      a.selected = !0;
      return;
    }
  }
  (!t || n !== void 0) && (e.selectedIndex = -1);
}
function In(e) {
  const n = e.querySelector(":checked");
  return n && n.__value;
}
function Ln(e, n, t) {
  e.classList.toggle(n, !!t);
}
function Zo(e, n, { bubbles: t = !1, cancelable: i = !1 } = {}) {
  return new CustomEvent(e, { detail: n, bubbles: t, cancelable: i });
}
let Ct;
function Mt(e) {
  Ct = e;
}
function si() {
  if (!Ct) throw new Error("Function called outside component initialization");
  return Ct;
}
function Oo(e) {
  si().$$.before_update.push(e);
}
function ci(e) {
  si().$$.after_update.push(e);
}
function Ol() {
  const e = si();
  return (n, t, { cancelable: i = !1 } = {}) => {
    const a = e.$$.callbacks[n];
    if (a) {
      const l = Zo(
        /** @type {string} */
        n,
        t,
        { cancelable: i }
      );
      return a.slice().forEach((f) => {
        f.call(e, l);
      }), !l.defaultPrevented;
    }
    return !0;
  };
}
const et = [], Zt = [];
let at = [];
const aa = [], Uo = /* @__PURE__ */ Promise.resolve();
let qn = !1;
function Fo() {
  qn || (qn = !0, Uo.then(Ul));
}
function ct(e) {
  at.push(e);
}
const Cn = /* @__PURE__ */ new Set();
let Qe = 0;
function Ul() {
  if (Qe !== 0)
    return;
  const e = Ct;
  do {
    try {
      for (; Qe < et.length; ) {
        const n = et[Qe];
        Qe++, Mt(n), Ho(n.$$);
      }
    } catch (n) {
      throw et.length = 0, Qe = 0, n;
    }
    for (Mt(null), et.length = 0, Qe = 0; Zt.length; ) Zt.pop()();
    for (let n = 0; n < at.length; n += 1) {
      const t = at[n];
      Cn.has(t) || (Cn.add(t), t());
    }
    at.length = 0;
  } while (et.length);
  for (; aa.length; )
    aa.pop()();
  qn = !1, Cn.clear(), Mt(e);
}
function Ho(e) {
  if (e.fragment !== null) {
    e.update(), Ke(e.before_update);
    const n = e.dirty;
    e.dirty = [-1], e.fragment && e.fragment.p(e.ctx, n), e.after_update.forEach(ct);
  }
}
function $o(e) {
  const n = [], t = [];
  at.forEach((i) => e.indexOf(i) === -1 ? n.push(i) : t.push(i)), t.forEach((i) => i()), at = n;
}
const tn = /* @__PURE__ */ new Set();
let He;
function be() {
  He = {
    r: 0,
    c: [],
    p: He
    // parent group
  };
}
function ge() {
  He.r || Ke(He.c), He = He.p;
}
function Z(e, n) {
  e && e.i && (tn.delete(e), e.i(n));
}
function H(e, n, t, i) {
  if (e && e.o) {
    if (tn.has(e)) return;
    tn.add(e), He.c.push(() => {
      tn.delete(e), i && (t && e.d(1), i());
    }), e.o(n);
  } else i && i();
}
function me(e) {
  return (e == null ? void 0 : e.length) !== void 0 ? e : Array.from(e);
}
function ue(e) {
  e && e.c();
}
function re(e, n, t) {
  const { fragment: i, after_update: a } = e.$$;
  i && i.m(n, t), ct(() => {
    const l = e.$$.on_mount.map(Cl).filter(Zl);
    e.$$.on_destroy ? e.$$.on_destroy.push(...l) : Ke(l), e.$$.on_mount = [];
  }), a.forEach(ct);
}
function oe(e, n) {
  const t = e.$$;
  t.fragment !== null && ($o(t.after_update), Ke(t.on_destroy), t.fragment && t.fragment.d(n), t.on_destroy = t.fragment = null, t.ctx = []);
}
function Bo(e, n) {
  e.$$.dirty[0] === -1 && (et.push(e), Fo(), e.$$.dirty.fill(0)), e.$$.dirty[n / 31 | 0] |= 1 << n % 31;
}
function Ge(e, n, t, i, a, l, f = null, r = [-1]) {
  const s = Ct;
  Mt(e);
  const o = e.$$ = {
    fragment: null,
    ctx: [],
    // state
    props: l,
    update: fe,
    not_equal: a,
    bound: ia(),
    // lifecycle
    on_mount: [],
    on_destroy: [],
    on_disconnect: [],
    before_update: [],
    after_update: [],
    context: new Map(n.context || (s ? s.$$.context : [])),
    // everything else
    callbacks: ia(),
    dirty: r,
    skip_bound: !1,
    root: n.target || s.$$.root
  };
  f && f(o.root);
  let c = !1;
  if (o.ctx = t ? t(e, n.props || {}, (h, d, ...u) => {
    const _ = u.length ? u[0] : d;
    return o.ctx && a(o.ctx[h], o.ctx[h] = _) && (!o.skip_bound && o.bound[h] && o.bound[h](_), c && Bo(e, h)), d;
  }) : [], o.update(), c = !0, Ke(o.before_update), o.fragment = i ? i(o.ctx) : !1, n.target) {
    if (n.hydrate) {
      const h = Co(n.target);
      o.fragment && o.fragment.l(h), h.forEach(L);
    } else
      o.fragment && o.fragment.c();
    n.intro && Z(e.$$.fragment), re(e, n.target, n.anchor), Ul();
  }
  Mt(s);
}
class Ve {
  constructor() {
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    pe(this, "$$");
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    pe(this, "$$set");
  }
  /** @returns {void} */
  $destroy() {
    oe(this, 1), this.$destroy = fe;
  }
  /**
   * @template {Extract<keyof Events, string>} K
   * @param {K} type
   * @param {((e: Events[K]) => void) | null | undefined} callback
   * @returns {() => void}
   */
  $on(n, t) {
    if (!Zl(t))
      return fe;
    const i = this.$$.callbacks[n] || (this.$$.callbacks[n] = []);
    return i.push(t), () => {
      const a = i.indexOf(t);
      a !== -1 && i.splice(a, 1);
    };
  }
  /**
   * @param {Partial<Props>} props
   * @returns {void}
   */
  $set(n) {
    this.$$set && !To(n) && (this.$$.skip_bound = !0, this.$$set(n), this.$$.skip_bound = !1);
  }
}
const Po = "4";
typeof window < "u" && (window.__svelte || (window.__svelte = { v: /* @__PURE__ */ new Set() })).v.add(Po);
function qe(e) {
  for (var n = e.length / 6 | 0, t = new Array(n), i = 0; i < n; ) t[i] = "#" + e.slice(i * 6, ++i * 6);
  return t;
}
function di(e, n, t) {
  e.prototype = n.prototype = t, t.constructor = e;
}
function Fl(e, n) {
  var t = Object.create(e.prototype);
  for (var i in n) t[i] = n[i];
  return t;
}
function Xt() {
}
var Ot = 0.7, rn = 1 / Ot, lt = "\\s*([+-]?\\d+)\\s*", Ut = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*", Me = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*", jo = /^#([0-9a-f]{3,8})$/, Xo = new RegExp(`^rgb\\(${lt},${lt},${lt}\\)$`), Ko = new RegExp(`^rgb\\(${Me},${Me},${Me}\\)$`), Yo = new RegExp(`^rgba\\(${lt},${lt},${lt},${Ut}\\)$`), Go = new RegExp(`^rgba\\(${Me},${Me},${Me},${Ut}\\)$`), Vo = new RegExp(`^hsl\\(${Ut},${Me},${Me}\\)$`), qo = new RegExp(`^hsla\\(${Ut},${Me},${Me},${Ut}\\)$`), la = {
  aliceblue: 15792383,
  antiquewhite: 16444375,
  aqua: 65535,
  aquamarine: 8388564,
  azure: 15794175,
  beige: 16119260,
  bisque: 16770244,
  black: 0,
  blanchedalmond: 16772045,
  blue: 255,
  blueviolet: 9055202,
  brown: 10824234,
  burlywood: 14596231,
  cadetblue: 6266528,
  chartreuse: 8388352,
  chocolate: 13789470,
  coral: 16744272,
  cornflowerblue: 6591981,
  cornsilk: 16775388,
  crimson: 14423100,
  cyan: 65535,
  darkblue: 139,
  darkcyan: 35723,
  darkgoldenrod: 12092939,
  darkgray: 11119017,
  darkgreen: 25600,
  darkgrey: 11119017,
  darkkhaki: 12433259,
  darkmagenta: 9109643,
  darkolivegreen: 5597999,
  darkorange: 16747520,
  darkorchid: 10040012,
  darkred: 9109504,
  darksalmon: 15308410,
  darkseagreen: 9419919,
  darkslateblue: 4734347,
  darkslategray: 3100495,
  darkslategrey: 3100495,
  darkturquoise: 52945,
  darkviolet: 9699539,
  deeppink: 16716947,
  deepskyblue: 49151,
  dimgray: 6908265,
  dimgrey: 6908265,
  dodgerblue: 2003199,
  firebrick: 11674146,
  floralwhite: 16775920,
  forestgreen: 2263842,
  fuchsia: 16711935,
  gainsboro: 14474460,
  ghostwhite: 16316671,
  gold: 16766720,
  goldenrod: 14329120,
  gray: 8421504,
  green: 32768,
  greenyellow: 11403055,
  grey: 8421504,
  honeydew: 15794160,
  hotpink: 16738740,
  indianred: 13458524,
  indigo: 4915330,
  ivory: 16777200,
  khaki: 15787660,
  lavender: 15132410,
  lavenderblush: 16773365,
  lawngreen: 8190976,
  lemonchiffon: 16775885,
  lightblue: 11393254,
  lightcoral: 15761536,
  lightcyan: 14745599,
  lightgoldenrodyellow: 16448210,
  lightgray: 13882323,
  lightgreen: 9498256,
  lightgrey: 13882323,
  lightpink: 16758465,
  lightsalmon: 16752762,
  lightseagreen: 2142890,
  lightskyblue: 8900346,
  lightslategray: 7833753,
  lightslategrey: 7833753,
  lightsteelblue: 11584734,
  lightyellow: 16777184,
  lime: 65280,
  limegreen: 3329330,
  linen: 16445670,
  magenta: 16711935,
  maroon: 8388608,
  mediumaquamarine: 6737322,
  mediumblue: 205,
  mediumorchid: 12211667,
  mediumpurple: 9662683,
  mediumseagreen: 3978097,
  mediumslateblue: 8087790,
  mediumspringgreen: 64154,
  mediumturquoise: 4772300,
  mediumvioletred: 13047173,
  midnightblue: 1644912,
  mintcream: 16121850,
  mistyrose: 16770273,
  moccasin: 16770229,
  navajowhite: 16768685,
  navy: 128,
  oldlace: 16643558,
  olive: 8421376,
  olivedrab: 7048739,
  orange: 16753920,
  orangered: 16729344,
  orchid: 14315734,
  palegoldenrod: 15657130,
  palegreen: 10025880,
  paleturquoise: 11529966,
  palevioletred: 14381203,
  papayawhip: 16773077,
  peachpuff: 16767673,
  peru: 13468991,
  pink: 16761035,
  plum: 14524637,
  powderblue: 11591910,
  purple: 8388736,
  rebeccapurple: 6697881,
  red: 16711680,
  rosybrown: 12357519,
  royalblue: 4286945,
  saddlebrown: 9127187,
  salmon: 16416882,
  sandybrown: 16032864,
  seagreen: 3050327,
  seashell: 16774638,
  sienna: 10506797,
  silver: 12632256,
  skyblue: 8900331,
  slateblue: 6970061,
  slategray: 7372944,
  slategrey: 7372944,
  snow: 16775930,
  springgreen: 65407,
  steelblue: 4620980,
  tan: 13808780,
  teal: 32896,
  thistle: 14204888,
  tomato: 16737095,
  turquoise: 4251856,
  violet: 15631086,
  wheat: 16113331,
  white: 16777215,
  whitesmoke: 16119285,
  yellow: 16776960,
  yellowgreen: 10145074
};
di(Xt, dt, {
  copy(e) {
    return Object.assign(new this.constructor(), this, e);
  },
  displayable() {
    return this.rgb().displayable();
  },
  hex: fa,
  // Deprecated! Use color.formatHex.
  formatHex: fa,
  formatHex8: Wo,
  formatHsl: Jo,
  formatRgb: ra,
  toString: ra
});
function fa() {
  return this.rgb().formatHex();
}
function Wo() {
  return this.rgb().formatHex8();
}
function Jo() {
  return Hl(this).formatHsl();
}
function ra() {
  return this.rgb().formatRgb();
}
function dt(e) {
  var n, t;
  return e = (e + "").trim().toLowerCase(), (n = jo.exec(e)) ? (t = n[1].length, n = parseInt(n[1], 16), t === 6 ? oa(n) : t === 3 ? new ie(n >> 8 & 15 | n >> 4 & 240, n >> 4 & 15 | n & 240, (n & 15) << 4 | n & 15, 1) : t === 8 ? Wt(n >> 24 & 255, n >> 16 & 255, n >> 8 & 255, (n & 255) / 255) : t === 4 ? Wt(n >> 12 & 15 | n >> 8 & 240, n >> 8 & 15 | n >> 4 & 240, n >> 4 & 15 | n & 240, ((n & 15) << 4 | n & 15) / 255) : null) : (n = Xo.exec(e)) ? new ie(n[1], n[2], n[3], 1) : (n = Ko.exec(e)) ? new ie(n[1] * 255 / 100, n[2] * 255 / 100, n[3] * 255 / 100, 1) : (n = Yo.exec(e)) ? Wt(n[1], n[2], n[3], n[4]) : (n = Go.exec(e)) ? Wt(n[1] * 255 / 100, n[2] * 255 / 100, n[3] * 255 / 100, n[4]) : (n = Vo.exec(e)) ? da(n[1], n[2] / 100, n[3] / 100, 1) : (n = qo.exec(e)) ? da(n[1], n[2] / 100, n[3] / 100, n[4]) : la.hasOwnProperty(e) ? oa(la[e]) : e === "transparent" ? new ie(NaN, NaN, NaN, 0) : null;
}
function oa(e) {
  return new ie(e >> 16 & 255, e >> 8 & 255, e & 255, 1);
}
function Wt(e, n, t, i) {
  return i <= 0 && (e = n = t = NaN), new ie(e, n, t, i);
}
function Qo(e) {
  return e instanceof Xt || (e = dt(e)), e ? (e = e.rgb(), new ie(e.r, e.g, e.b, e.opacity)) : new ie();
}
function on(e, n, t, i) {
  return arguments.length === 1 ? Qo(e) : new ie(e, n, t, i ?? 1);
}
function ie(e, n, t, i) {
  this.r = +e, this.g = +n, this.b = +t, this.opacity = +i;
}
di(ie, on, Fl(Xt, {
  brighter(e) {
    return e = e == null ? rn : Math.pow(rn, e), new ie(this.r * e, this.g * e, this.b * e, this.opacity);
  },
  darker(e) {
    return e = e == null ? Ot : Math.pow(Ot, e), new ie(this.r * e, this.g * e, this.b * e, this.opacity);
  },
  rgb() {
    return this;
  },
  clamp() {
    return new ie(Be(this.r), Be(this.g), Be(this.b), sn(this.opacity));
  },
  displayable() {
    return -0.5 <= this.r && this.r < 255.5 && -0.5 <= this.g && this.g < 255.5 && -0.5 <= this.b && this.b < 255.5 && 0 <= this.opacity && this.opacity <= 1;
  },
  hex: sa,
  // Deprecated! Use color.formatHex.
  formatHex: sa,
  formatHex8: e0,
  formatRgb: ca,
  toString: ca
}));
function sa() {
  return `#${$e(this.r)}${$e(this.g)}${$e(this.b)}`;
}
function e0() {
  return `#${$e(this.r)}${$e(this.g)}${$e(this.b)}${$e((isNaN(this.opacity) ? 1 : this.opacity) * 255)}`;
}
function ca() {
  const e = sn(this.opacity);
  return `${e === 1 ? "rgb(" : "rgba("}${Be(this.r)}, ${Be(this.g)}, ${Be(this.b)}${e === 1 ? ")" : `, ${e})`}`;
}
function sn(e) {
  return isNaN(e) ? 1 : Math.max(0, Math.min(1, e));
}
function Be(e) {
  return Math.max(0, Math.min(255, Math.round(e) || 0));
}
function $e(e) {
  return e = Be(e), (e < 16 ? "0" : "") + e.toString(16);
}
function da(e, n, t, i) {
  return i <= 0 ? e = n = t = NaN : t <= 0 || t >= 1 ? e = n = NaN : n <= 0 && (e = NaN), new _e(e, n, t, i);
}
function Hl(e) {
  if (e instanceof _e) return new _e(e.h, e.s, e.l, e.opacity);
  if (e instanceof Xt || (e = dt(e)), !e) return new _e();
  if (e instanceof _e) return e;
  e = e.rgb();
  var n = e.r / 255, t = e.g / 255, i = e.b / 255, a = Math.min(n, t, i), l = Math.max(n, t, i), f = NaN, r = l - a, s = (l + a) / 2;
  return r ? (n === l ? f = (t - i) / r + (t < i) * 6 : t === l ? f = (i - n) / r + 2 : f = (n - t) / r + 4, r /= s < 0.5 ? l + a : 2 - l - a, f *= 60) : r = s > 0 && s < 1 ? 0 : f, new _e(f, r, s, e.opacity);
}
function t0(e, n, t, i) {
  return arguments.length === 1 ? Hl(e) : new _e(e, n, t, i ?? 1);
}
function _e(e, n, t, i) {
  this.h = +e, this.s = +n, this.l = +t, this.opacity = +i;
}
di(_e, t0, Fl(Xt, {
  brighter(e) {
    return e = e == null ? rn : Math.pow(rn, e), new _e(this.h, this.s, this.l * e, this.opacity);
  },
  darker(e) {
    return e = e == null ? Ot : Math.pow(Ot, e), new _e(this.h, this.s, this.l * e, this.opacity);
  },
  rgb() {
    var e = this.h % 360 + (this.h < 0) * 360, n = isNaN(e) || isNaN(this.s) ? 0 : this.s, t = this.l, i = t + (t < 0.5 ? t : 1 - t) * n, a = 2 * t - i;
    return new ie(
      Zn(e >= 240 ? e - 240 : e + 120, a, i),
      Zn(e, a, i),
      Zn(e < 120 ? e + 240 : e - 120, a, i),
      this.opacity
    );
  },
  clamp() {
    return new _e(ha(this.h), Jt(this.s), Jt(this.l), sn(this.opacity));
  },
  displayable() {
    return (0 <= this.s && this.s <= 1 || isNaN(this.s)) && 0 <= this.l && this.l <= 1 && 0 <= this.opacity && this.opacity <= 1;
  },
  formatHsl() {
    const e = sn(this.opacity);
    return `${e === 1 ? "hsl(" : "hsla("}${ha(this.h)}, ${Jt(this.s) * 100}%, ${Jt(this.l) * 100}%${e === 1 ? ")" : `, ${e})`}`;
  }
}));
function ha(e) {
  return e = (e || 0) % 360, e < 0 ? e + 360 : e;
}
function Jt(e) {
  return Math.max(0, Math.min(1, e || 0));
}
function Zn(e, n, t) {
  return (e < 60 ? n + (t - n) * e / 60 : e < 180 ? t : e < 240 ? n + (t - n) * (240 - e) / 60 : n) * 255;
}
function n0(e, n, t, i, a) {
  var l = e * e, f = l * e;
  return ((1 - 3 * e + 3 * l - f) * n + (4 - 6 * l + 3 * f) * t + (1 + 3 * e + 3 * l - 3 * f) * i + f * a) / 6;
}
function i0(e) {
  var n = e.length - 1;
  return function(t) {
    var i = t <= 0 ? t = 0 : t >= 1 ? (t = 1, n - 1) : Math.floor(t * n), a = e[i], l = e[i + 1], f = i > 0 ? e[i - 1] : 2 * a - l, r = i < n - 1 ? e[i + 2] : 2 * l - a;
    return n0((t - i / n) * n, f, a, l, r);
  };
}
const hi = (e) => () => e;
function a0(e, n) {
  return function(t) {
    return e + t * n;
  };
}
function l0(e, n, t) {
  return e = Math.pow(e, t), n = Math.pow(n, t) - e, t = 1 / t, function(i) {
    return Math.pow(e + i * n, t);
  };
}
function f0(e) {
  return (e = +e) == 1 ? $l : function(n, t) {
    return t - n ? l0(n, t, e) : hi(isNaN(n) ? t : n);
  };
}
function $l(e, n) {
  var t = n - e;
  return t ? a0(e, t) : hi(isNaN(e) ? n : e);
}
const ua = function e(n) {
  var t = f0(n);
  function i(a, l) {
    var f = t((a = on(a)).r, (l = on(l)).r), r = t(a.g, l.g), s = t(a.b, l.b), o = $l(a.opacity, l.opacity);
    return function(c) {
      return a.r = f(c), a.g = r(c), a.b = s(c), a.opacity = o(c), a + "";
    };
  }
  return i.gamma = e, i;
}(1);
function r0(e) {
  return function(n) {
    var t = n.length, i = new Array(t), a = new Array(t), l = new Array(t), f, r;
    for (f = 0; f < t; ++f)
      r = on(n[f]), i[f] = r.r || 0, a[f] = r.g || 0, l[f] = r.b || 0;
    return i = e(i), a = e(a), l = e(l), r.opacity = 1, function(s) {
      return r.r = i(s), r.g = a(s), r.b = l(s), r + "";
    };
  };
}
var o0 = r0(i0);
function s0(e, n) {
  n || (n = []);
  var t = e ? Math.min(n.length, e.length) : 0, i = n.slice(), a;
  return function(l) {
    for (a = 0; a < t; ++a) i[a] = e[a] * (1 - l) + n[a] * l;
    return i;
  };
}
function c0(e) {
  return ArrayBuffer.isView(e) && !(e instanceof DataView);
}
function d0(e, n) {
  var t = n ? n.length : 0, i = e ? Math.min(t, e.length) : 0, a = new Array(i), l = new Array(t), f;
  for (f = 0; f < i; ++f) a[f] = ui(e[f], n[f]);
  for (; f < t; ++f) l[f] = n[f];
  return function(r) {
    for (f = 0; f < i; ++f) l[f] = a[f](r);
    return l;
  };
}
function h0(e, n) {
  var t = /* @__PURE__ */ new Date();
  return e = +e, n = +n, function(i) {
    return t.setTime(e * (1 - i) + n * i), t;
  };
}
function cn(e, n) {
  return e = +e, n = +n, function(t) {
    return e * (1 - t) + n * t;
  };
}
function u0(e, n) {
  var t = {}, i = {}, a;
  (e === null || typeof e != "object") && (e = {}), (n === null || typeof n != "object") && (n = {});
  for (a in n)
    a in e ? t[a] = ui(e[a], n[a]) : i[a] = n[a];
  return function(l) {
    for (a in t) i[a] = t[a](l);
    return i;
  };
}
var Wn = /[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g, On = new RegExp(Wn.source, "g");
function _0(e) {
  return function() {
    return e;
  };
}
function b0(e) {
  return function(n) {
    return e(n) + "";
  };
}
function g0(e, n) {
  var t = Wn.lastIndex = On.lastIndex = 0, i, a, l, f = -1, r = [], s = [];
  for (e = e + "", n = n + ""; (i = Wn.exec(e)) && (a = On.exec(n)); )
    (l = a.index) > t && (l = n.slice(t, l), r[f] ? r[f] += l : r[++f] = l), (i = i[0]) === (a = a[0]) ? r[f] ? r[f] += a : r[++f] = a : (r[++f] = null, s.push({ i: f, x: cn(i, a) })), t = On.lastIndex;
  return t < n.length && (l = n.slice(t), r[f] ? r[f] += l : r[++f] = l), r.length < 2 ? s[0] ? b0(s[0].x) : _0(n) : (n = s.length, function(o) {
    for (var c = 0, h; c < n; ++c) r[(h = s[c]).i] = h.x(o);
    return r.join("");
  });
}
function ui(e, n) {
  var t = typeof n, i;
  return n == null || t === "boolean" ? hi(n) : (t === "number" ? cn : t === "string" ? (i = dt(n)) ? (n = i, ua) : g0 : n instanceof dt ? ua : n instanceof Date ? h0 : c0(n) ? s0 : Array.isArray(n) ? d0 : typeof n.valueOf != "function" && typeof n.toString != "function" || isNaN(n) ? u0 : cn)(e, n);
}
function m0(e, n) {
  return e = +e, n = +n, function(t) {
    return Math.round(e * (1 - t) + n * t);
  };
}
const _i = (e) => o0(e[e.length - 1]);
var p0 = new Array(3).concat(
  "ef8a62f7f7f767a9cf",
  "ca0020f4a58292c5de0571b0",
  "ca0020f4a582f7f7f792c5de0571b0",
  "b2182bef8a62fddbc7d1e5f067a9cf2166ac",
  "b2182bef8a62fddbc7f7f7f7d1e5f067a9cf2166ac",
  "b2182bd6604df4a582fddbc7d1e5f092c5de4393c32166ac",
  "b2182bd6604df4a582fddbc7f7f7f7d1e5f092c5de4393c32166ac",
  "67001fb2182bd6604df4a582fddbc7d1e5f092c5de4393c32166ac053061",
  "67001fb2182bd6604df4a582fddbc7f7f7f7d1e5f092c5de4393c32166ac053061"
).map(qe);
const _a = _i(p0);
var w0 = new Array(3).concat(
  "deebf79ecae13182bd",
  "eff3ffbdd7e76baed62171b5",
  "eff3ffbdd7e76baed63182bd08519c",
  "eff3ffc6dbef9ecae16baed63182bd08519c",
  "eff3ffc6dbef9ecae16baed64292c62171b5084594",
  "f7fbffdeebf7c6dbef9ecae16baed64292c62171b5084594",
  "f7fbffdeebf7c6dbef9ecae16baed64292c62171b508519c08306b"
).map(qe);
const x0 = _i(w0);
var v0 = new Array(3).concat(
  "f0f0f0bdbdbd636363",
  "f7f7f7cccccc969696525252",
  "f7f7f7cccccc969696636363252525",
  "f7f7f7d9d9d9bdbdbd969696636363252525",
  "f7f7f7d9d9d9bdbdbd969696737373525252252525",
  "fffffff0f0f0d9d9d9bdbdbd969696737373525252252525",
  "fffffff0f0f0d9d9d9bdbdbd969696737373525252252525000000"
).map(qe);
const ba = _i(v0);
function y0(e) {
  return e = Math.max(0, Math.min(1, e)), "rgb(" + Math.max(0, Math.min(255, Math.round(-4.54 - e * (35.34 - e * (2381.73 - e * (6402.7 - e * (7024.72 - e * 2710.57))))))) + ", " + Math.max(0, Math.min(255, Math.round(32.49 + e * (170.73 + e * (52.82 - e * (131.46 - e * (176.58 - e * 67.37))))))) + ", " + Math.max(0, Math.min(255, Math.round(81.24 + e * (442.36 - e * (2482.43 - e * (6167.24 - e * (6614.94 - e * 2475.67))))))) + ")";
}
function k0(e) {
  return e = Math.max(0, Math.min(1, e)), "rgb(" + Math.max(0, Math.min(255, Math.round(34.61 + e * (1172.33 - e * (10793.56 - e * (33300.12 - e * (38394.49 - e * 14825.05))))))) + ", " + Math.max(0, Math.min(255, Math.round(23.31 + e * (557.33 + e * (1225.33 - e * (3574.96 - e * (1073.77 + e * 707.56))))))) + ", " + Math.max(0, Math.min(255, Math.round(27.2 + e * (3211.1 - e * (15327.97 - e * (27814 - e * (22569.18 - e * 6838.66))))))) + ")";
}
function mn(e) {
  var n = e.length;
  return function(t) {
    return e[Math.max(0, Math.min(n - 1, Math.floor(t * n)))];
  };
}
const E0 = mn(qe("44015444025645045745055946075a46085c460a5d460b5e470d60470e6147106347116447136548146748166848176948186a481a6c481b6d481c6e481d6f481f70482071482173482374482475482576482677482878482979472a7a472c7a472d7b472e7c472f7d46307e46327e46337f463480453581453781453882443983443a83443b84433d84433e85423f854240864241864142874144874045884046883f47883f48893e49893e4a893e4c8a3d4d8a3d4e8a3c4f8a3c508b3b518b3b528b3a538b3a548c39558c39568c38588c38598c375a8c375b8d365c8d365d8d355e8d355f8d34608d34618d33628d33638d32648e32658e31668e31678e31688e30698e306a8e2f6b8e2f6c8e2e6d8e2e6e8e2e6f8e2d708e2d718e2c718e2c728e2c738e2b748e2b758e2a768e2a778e2a788e29798e297a8e297b8e287c8e287d8e277e8e277f8e27808e26818e26828e26828e25838e25848e25858e24868e24878e23888e23898e238a8d228b8d228c8d228d8d218e8d218f8d21908d21918c20928c20928c20938c1f948c1f958b1f968b1f978b1f988b1f998a1f9a8a1e9b8a1e9c891e9d891f9e891f9f881fa0881fa1881fa1871fa28720a38620a48621a58521a68522a78522a88423a98324aa8325ab8225ac8226ad8127ad8128ae8029af7f2ab07f2cb17e2db27d2eb37c2fb47c31b57b32b67a34b67935b77937b87838b9773aba763bbb753dbc743fbc7340bd7242be7144bf7046c06f48c16e4ac16d4cc26c4ec36b50c46a52c56954c56856c66758c7655ac8645cc8635ec96260ca6063cb5f65cb5e67cc5c69cd5b6ccd5a6ece5870cf5773d05675d05477d1537ad1517cd2507fd34e81d34d84d44b86d54989d5488bd6468ed64590d74393d74195d84098d83e9bd93c9dd93ba0da39a2da37a5db36a8db34aadc32addc30b0dd2fb2dd2db5de2bb8de29bade28bddf26c0df25c2df23c5e021c8e020cae11fcde11dd0e11cd2e21bd5e21ad8e219dae319dde318dfe318e2e418e5e419e7e419eae51aece51befe51cf1e51df4e61ef6e620f8e621fbe723fde725"));
mn(qe("00000401000501010601010802010902020b02020d03030f03031204041405041606051806051a07061c08071e0907200a08220b09240c09260d0a290e0b2b100b2d110c2f120d31130d34140e36150e38160f3b180f3d19103f1a10421c10441d11471e114920114b21114e22115024125325125527125829115a2a115c2c115f2d11612f116331116533106734106936106b38106c390f6e3b0f703d0f713f0f72400f74420f75440f764510774710784910784a10794c117a4e117b4f127b51127c52137c54137d56147d57157e59157e5a167e5c167f5d177f5f187f601880621980641a80651a80671b80681c816a1c816b1d816d1d816e1e81701f81721f817320817521817621817822817922827b23827c23827e24828025828125818326818426818627818827818928818b29818c29818e2a81902a81912b81932b80942c80962c80982d80992d809b2e7f9c2e7f9e2f7fa02f7fa1307ea3307ea5317ea6317da8327daa337dab337cad347cae347bb0357bb2357bb3367ab5367ab73779b83779ba3878bc3978bd3977bf3a77c03a76c23b75c43c75c53c74c73d73c83e73ca3e72cc3f71cd4071cf4070d0416fd2426fd3436ed5446dd6456cd8456cd9466bdb476adc4869de4968df4a68e04c67e24d66e34e65e44f64e55064e75263e85362e95462ea5661eb5760ec5860ed5a5fee5b5eef5d5ef05f5ef1605df2625df2645cf3655cf4675cf4695cf56b5cf66c5cf66e5cf7705cf7725cf8745cf8765cf9785df9795df97b5dfa7d5efa7f5efa815ffb835ffb8560fb8761fc8961fc8a62fc8c63fc8e64fc9065fd9266fd9467fd9668fd9869fd9a6afd9b6bfe9d6cfe9f6dfea16efea36ffea571fea772fea973feaa74feac76feae77feb078feb27afeb47bfeb67cfeb77efeb97ffebb81febd82febf84fec185fec287fec488fec68afec88cfeca8dfecc8ffecd90fecf92fed194fed395fed597fed799fed89afdda9cfddc9efddea0fde0a1fde2a3fde3a5fde5a7fde7a9fde9aafdebacfcecaefceeb0fcf0b2fcf2b4fcf4b6fcf6b8fcf7b9fcf9bbfcfbbdfcfdbf"));
var A0 = mn(qe("00000401000501010601010802010a02020c02020e03021004031204031405041706041907051b08051d09061f0a07220b07240c08260d08290e092b10092d110a30120a32140b34150b37160b39180c3c190c3e1b0c411c0c431e0c451f0c48210c4a230c4c240c4f260c51280b53290b552b0b572d0b592f0a5b310a5c320a5e340a5f3609613809623909633b09643d09653e0966400a67420a68440a68450a69470b6a490b6a4a0c6b4c0c6b4d0d6c4f0d6c510e6c520e6d540f6d550f6d57106e59106e5a116e5c126e5d126e5f136e61136e62146e64156e65156e67166e69166e6a176e6c186e6d186e6f196e71196e721a6e741a6e751b6e771c6d781c6d7a1d6d7c1d6d7d1e6d7f1e6c801f6c82206c84206b85216b87216b88226a8a226a8c23698d23698f24699025689225689326679526679727669827669a28659b29649d29649f2a63a02a63a22b62a32c61a52c60a62d60a82e5fa92e5eab2f5ead305dae305cb0315bb1325ab3325ab43359b63458b73557b93556ba3655bc3754bd3853bf3952c03a51c13a50c33b4fc43c4ec63d4dc73e4cc83f4bca404acb4149cc4248ce4347cf4446d04545d24644d34743d44842d54a41d74b3fd84c3ed94d3dda4e3cdb503bdd513ade5238df5337e05536e15635e25734e35933e45a31e55c30e65d2fe75e2ee8602de9612bea632aeb6429eb6628ec6726ed6925ee6a24ef6c23ef6e21f06f20f1711ff1731df2741cf3761bf37819f47918f57b17f57d15f67e14f68013f78212f78410f8850ff8870ef8890cf98b0bf98c0af98e09fa9008fa9207fa9407fb9606fb9706fb9906fb9b06fb9d07fc9f07fca108fca309fca50afca60cfca80dfcaa0ffcac11fcae12fcb014fcb216fcb418fbb61afbb81dfbba1ffbbc21fbbe23fac026fac228fac42afac62df9c72ff9c932f9cb35f8cd37f8cf3af7d13df7d340f6d543f6d746f5d949f5db4cf4dd4ff4df53f4e156f3e35af3e55df2e661f2e865f2ea69f1ec6df1ed71f1ef75f1f179f2f27df2f482f3f586f3f68af4f88ef5f992f6fa96f8fb9af9fc9dfafda1fcffa4")), M0 = mn(qe("0d088710078813078916078a19068c1b068d1d068e20068f2206902406912605912805922a05932c05942e05952f059631059733059735049837049938049a3a049a3c049b3e049c3f049c41049d43039e44039e46039f48039f4903a04b03a14c02a14e02a25002a25102a35302a35502a45601a45801a45901a55b01a55c01a65e01a66001a66100a76300a76400a76600a76700a86900a86a00a86c00a86e00a86f00a87100a87201a87401a87501a87701a87801a87a02a87b02a87d03a87e03a88004a88104a78305a78405a78606a68707a68808a68a09a58b0aa58d0ba58e0ca48f0da4910ea3920fa39410a29511a19613a19814a099159f9a169f9c179e9d189d9e199da01a9ca11b9ba21d9aa31e9aa51f99a62098a72197a82296aa2395ab2494ac2694ad2793ae2892b02991b12a90b22b8fb32c8eb42e8db52f8cb6308bb7318ab83289ba3388bb3488bc3587bd3786be3885bf3984c03a83c13b82c23c81c33d80c43e7fc5407ec6417dc7427cc8437bc9447aca457acb4679cc4778cc4977cd4a76ce4b75cf4c74d04d73d14e72d24f71d35171d45270d5536fd5546ed6556dd7566cd8576bd9586ada5a6ada5b69db5c68dc5d67dd5e66de5f65de6164df6263e06363e16462e26561e26660e3685fe4695ee56a5de56b5de66c5ce76e5be76f5ae87059e97158e97257ea7457eb7556eb7655ec7754ed7953ed7a52ee7b51ef7c51ef7e50f07f4ff0804ef1814df1834cf2844bf3854bf3874af48849f48948f58b47f58c46f68d45f68f44f79044f79143f79342f89441f89540f9973ff9983ef99a3efa9b3dfa9c3cfa9e3bfb9f3afba139fba238fca338fca537fca636fca835fca934fdab33fdac33fdae32fdaf31fdb130fdb22ffdb42ffdb52efeb72dfeb82cfeba2cfebb2bfebd2afebe2afec029fdc229fdc328fdc527fdc627fdc827fdca26fdcb26fccd25fcce25fcd025fcd225fbd324fbd524fbd724fad824fada24f9dc24f9dd25f8df25f8e125f7e225f7e425f6e626f6e826f5e926f5eb27f4ed27f3ee27f3f027f2f227f1f426f1f525f0f724f0f921"));
function xe(e) {
  return (n) => {
    let t = dt(e(n)).rgb();
    return { r: t.r, g: t.g, b: t.b, a: t.opacity * 255 };
  };
}
let S0 = [
  "Viridis",
  "Cividis",
  "Inferno",
  "Plasma",
  "Blues",
  "Turbo",
  "Greys",
  "RdBu",
  "BuRd"
];
function Bl(e) {
  switch (e.toLowerCase()) {
    case "viridis":
      return xe(E0);
    case "cividis":
      return xe(y0);
    case "inferno":
      return xe(A0);
    case "plasma":
      return xe(M0);
    case "blues":
      return xe(x0);
    case "turbo":
      return xe(k0);
    case "greys":
      return xe(ba);
    case "rdbu":
      return xe(_a);
    case "burd":
      return xe((n) => _a(1 - n));
    default:
      return console.warn(`Unknown color scheme '${e}', fall back to 'greys'.`), xe(ba);
  }
}
class Pl {
  constructor(n, t = 256, i = { r: 0, g: 0, b: 0, a: 0 }) {
    pe(this, "data");
    pe(this, "count");
    pe(this, "fallback");
    let a = new Uint8Array(t * 4), l = 0;
    for (let f = 0; f < t; f++) {
      let r = f / (t - 1), { r: s, g: o, b: c, a: h } = n(r);
      a[l++] = s, a[l++] = o, a[l++] = c, a[l++] = h;
    }
    this.count = t, this.data = a, this.fallback = i;
  }
  interpolate(n) {
    let t = this.data, i = this.count, a = n * (i - 1);
    if (!isFinite(a))
      return this.fallback;
    a = Math.max(0, Math.min(a, i - 1));
    let l = Math.floor(a), f = a - l, r = Math.min(l + 1, i - 1), s = 1 - f, o = f;
    return l *= 4, r *= 4, {
      r: t[l] * s + t[r] * o,
      g: t[l + 1] * s + t[r + 1] * o,
      b: t[l + 2] * s + t[r + 2] * o,
      a: t[l + 3] * s + t[r + 3] * o
    };
  }
  bytes() {
    return this.data;
  }
  get length() {
    return this.count;
  }
}
function z0(e) {
  let n = 800, t = 600, i = 20, a = 480, l = e[e.length - 1], f = e[e.length - 2], r = 1;
  return l < a && (r = Math.max(r, a / l)), f < a && (r = Math.max(r, a / f)), r > i && (r = i), r = Math.floor(r), l *= r, f *= r, l = Math.min(n, l), f = Math.min(t, f), { width: l, height: f };
}
function N0(e, n) {
  if (e.min < 0 && e.max > 0) {
    let t = Math.max(-e.min, e.max);
    return [-t, t];
  } else {
    let t = !1, i = e.min, a = e.max;
    return n == "linear" && Math.abs(a - i) > Math.abs(a) * 0.1 && (t = !0), n == "log" && (i = e.minPositive > 0 ? e.minPositive : a * 1e-4), t && (a < 0 ? a = 0 : i > 0 && (i = 0)), [i, a];
  }
}
function R0(e) {
  return e[0] < 0 ? "burd" : "turbo";
}
function jl(e, n = void 0) {
  let t = (n == null ? void 0 : n.type) ?? "linear", i = (n == null ? void 0 : n.domain) ?? N0(e.extents(), t), a = (n == null ? void 0 : n.scheme) ?? R0(i);
  return { type: t, domain: i, scheme: a };
}
function T0(e, n, t, i, a, l) {
  let f = 0;
  for (let r = 0; r < e.length; r++) {
    let s = e[r], o = (l ? Math.log(s) : s) * i + a, c = t.interpolate(o);
    n[f++] = c.r, n[f++] = c.g, n[f++] = c.b, n[f++] = c.a;
  }
}
function D0(e, n, t) {
  let i = e.getContext("2d"), a = n.shape[1], l = n.shape[0], f = new ImageData(a, l), r = new Pl(Bl(t.scheme), 128), s = t.type == "log", o, c, [h, d] = t.domain;
  s ? (o = 1 / (Math.log(d) - Math.log(h)), c = -Math.log(h) * o) : (o = 1 / (d - h), c = -h * o), T0(n.storage, f.data, r, o, c, s), i.putImageData(f, 0, 0);
}
function nn(e, n) {
  return e == null || n == null ? NaN : e < n ? -1 : e > n ? 1 : e >= n ? 0 : NaN;
}
function I0(e, n) {
  return e == null || n == null ? NaN : n < e ? -1 : n > e ? 1 : n >= e ? 0 : NaN;
}
function Xl(e) {
  let n, t, i;
  e.length !== 2 ? (n = nn, t = (r, s) => nn(e(r), s), i = (r, s) => e(r) - s) : (n = e === nn || e === I0 ? e : L0, t = e, i = e);
  function a(r, s, o = 0, c = r.length) {
    if (o < c) {
      if (n(s, s) !== 0) return c;
      do {
        const h = o + c >>> 1;
        t(r[h], s) < 0 ? o = h + 1 : c = h;
      } while (o < c);
    }
    return o;
  }
  function l(r, s, o = 0, c = r.length) {
    if (o < c) {
      if (n(s, s) !== 0) return c;
      do {
        const h = o + c >>> 1;
        t(r[h], s) <= 0 ? o = h + 1 : c = h;
      } while (o < c);
    }
    return o;
  }
  function f(r, s, o = 0, c = r.length) {
    const h = a(r, s, o, c - 1);
    return h > o && i(r[h - 1], s) > -i(r[h], s) ? h - 1 : h;
  }
  return { left: a, center: f, right: l };
}
function L0() {
  return 0;
}
function C0(e) {
  return e === null ? NaN : +e;
}
const Z0 = Xl(nn), O0 = Z0.right;
Xl(C0).center;
const U0 = Math.sqrt(50), F0 = Math.sqrt(10), H0 = Math.sqrt(2);
function dn(e, n, t) {
  const i = (n - e) / Math.max(0, t), a = Math.floor(Math.log10(i)), l = i / Math.pow(10, a), f = l >= U0 ? 10 : l >= F0 ? 5 : l >= H0 ? 2 : 1;
  let r, s, o;
  return a < 0 ? (o = Math.pow(10, -a) / f, r = Math.round(e * o), s = Math.round(n * o), r / o < e && ++r, s / o > n && --s, o = -o) : (o = Math.pow(10, a) * f, r = Math.round(e / o), s = Math.round(n / o), r * o < e && ++r, s * o > n && --s), s < r && 0.5 <= t && t < 2 ? dn(e, n, t * 2) : [r, s, o];
}
function Jn(e, n, t) {
  if (n = +n, e = +e, t = +t, !(t > 0)) return [];
  if (e === n) return [e];
  const i = n < e, [a, l, f] = i ? dn(n, e, t) : dn(e, n, t);
  if (!(l >= a)) return [];
  const r = l - a + 1, s = new Array(r);
  if (i)
    if (f < 0) for (let o = 0; o < r; ++o) s[o] = (l - o) / -f;
    else for (let o = 0; o < r; ++o) s[o] = (l - o) * f;
  else if (f < 0) for (let o = 0; o < r; ++o) s[o] = (a + o) / -f;
  else for (let o = 0; o < r; ++o) s[o] = (a + o) * f;
  return s;
}
function Qn(e, n, t) {
  return n = +n, e = +e, t = +t, dn(e, n, t)[2];
}
function $0(e, n, t) {
  n = +n, e = +e, t = +t;
  const i = n < e, a = i ? Qn(n, e, t) : Qn(e, n, t);
  return (i ? -1 : 1) * (a < 0 ? 1 / -a : a);
}
function Kl(e, n) {
  switch (arguments.length) {
    case 0:
      break;
    case 1:
      this.range(e);
      break;
    default:
      this.range(n).domain(e);
      break;
  }
  return this;
}
function B0(e) {
  return function() {
    return e;
  };
}
function P0(e) {
  return +e;
}
var ga = [0, 1];
function nt(e) {
  return e;
}
function ei(e, n) {
  return (n -= e = +e) ? function(t) {
    return (t - e) / n;
  } : B0(isNaN(n) ? NaN : 0.5);
}
function j0(e, n) {
  var t;
  return e > n && (t = e, e = n, n = t), function(i) {
    return Math.max(e, Math.min(n, i));
  };
}
function X0(e, n, t) {
  var i = e[0], a = e[1], l = n[0], f = n[1];
  return a < i ? (i = ei(a, i), l = t(f, l)) : (i = ei(i, a), l = t(l, f)), function(r) {
    return l(i(r));
  };
}
function K0(e, n, t) {
  var i = Math.min(e.length, n.length) - 1, a = new Array(i), l = new Array(i), f = -1;
  for (e[i] < e[0] && (e = e.slice().reverse(), n = n.slice().reverse()); ++f < i; )
    a[f] = ei(e[f], e[f + 1]), l[f] = t(n[f], n[f + 1]);
  return function(r) {
    var s = O0(e, r, 1, i) - 1;
    return l[s](a[s](r));
  };
}
function Yl(e, n) {
  return n.domain(e.domain()).range(e.range()).interpolate(e.interpolate()).clamp(e.clamp()).unknown(e.unknown());
}
function Gl() {
  var e = ga, n = ga, t = ui, i, a, l, f = nt, r, s, o;
  function c() {
    var d = Math.min(e.length, n.length);
    return f !== nt && (f = j0(e[0], e[d - 1])), r = d > 2 ? K0 : X0, s = o = null, h;
  }
  function h(d) {
    return d == null || isNaN(d = +d) ? l : (s || (s = r(e.map(i), n, t)))(i(f(d)));
  }
  return h.invert = function(d) {
    return f(a((o || (o = r(n, e.map(i), cn)))(d)));
  }, h.domain = function(d) {
    return arguments.length ? (e = Array.from(d, P0), c()) : e.slice();
  }, h.range = function(d) {
    return arguments.length ? (n = Array.from(d), c()) : n.slice();
  }, h.rangeRound = function(d) {
    return n = Array.from(d), t = m0, c();
  }, h.clamp = function(d) {
    return arguments.length ? (f = d ? !0 : nt, c()) : f !== nt;
  }, h.interpolate = function(d) {
    return arguments.length ? (t = d, c()) : t;
  }, h.unknown = function(d) {
    return arguments.length ? (l = d, h) : l;
  }, function(d, u) {
    return i = d, a = u, c();
  };
}
function Y0() {
  return Gl()(nt, nt);
}
function G0(e) {
  return Math.abs(e = Math.round(e)) >= 1e21 ? e.toLocaleString("en").replace(/,/g, "") : e.toString(10);
}
function hn(e, n) {
  if ((t = (e = n ? e.toExponential(n - 1) : e.toExponential()).indexOf("e")) < 0) return null;
  var t, i = e.slice(0, t);
  return [
    i.length > 1 ? i[0] + i.slice(2) : i,
    +e.slice(t + 1)
  ];
}
function ht(e) {
  return e = hn(Math.abs(e)), e ? e[1] : NaN;
}
function V0(e, n) {
  return function(t, i) {
    for (var a = t.length, l = [], f = 0, r = e[0], s = 0; a > 0 && r > 0 && (s + r + 1 > i && (r = Math.max(1, i - s)), l.push(t.substring(a -= r, a + r)), !((s += r + 1) > i)); )
      r = e[f = (f + 1) % e.length];
    return l.reverse().join(n);
  };
}
function q0(e) {
  return function(n) {
    return n.replace(/[0-9]/g, function(t) {
      return e[+t];
    });
  };
}
var W0 = /^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;
function Ft(e) {
  if (!(n = W0.exec(e))) throw new Error("invalid format: " + e);
  var n;
  return new bi({
    fill: n[1],
    align: n[2],
    sign: n[3],
    symbol: n[4],
    zero: n[5],
    width: n[6],
    comma: n[7],
    precision: n[8] && n[8].slice(1),
    trim: n[9],
    type: n[10]
  });
}
Ft.prototype = bi.prototype;
function bi(e) {
  this.fill = e.fill === void 0 ? " " : e.fill + "", this.align = e.align === void 0 ? ">" : e.align + "", this.sign = e.sign === void 0 ? "-" : e.sign + "", this.symbol = e.symbol === void 0 ? "" : e.symbol + "", this.zero = !!e.zero, this.width = e.width === void 0 ? void 0 : +e.width, this.comma = !!e.comma, this.precision = e.precision === void 0 ? void 0 : +e.precision, this.trim = !!e.trim, this.type = e.type === void 0 ? "" : e.type + "";
}
bi.prototype.toString = function() {
  return this.fill + this.align + this.sign + this.symbol + (this.zero ? "0" : "") + (this.width === void 0 ? "" : Math.max(1, this.width | 0)) + (this.comma ? "," : "") + (this.precision === void 0 ? "" : "." + Math.max(0, this.precision | 0)) + (this.trim ? "~" : "") + this.type;
};
function J0(e) {
  e: for (var n = e.length, t = 1, i = -1, a; t < n; ++t)
    switch (e[t]) {
      case ".":
        i = a = t;
        break;
      case "0":
        i === 0 && (i = t), a = t;
        break;
      default:
        if (!+e[t]) break e;
        i > 0 && (i = 0);
        break;
    }
  return i > 0 ? e.slice(0, i) + e.slice(a + 1) : e;
}
var Vl;
function Q0(e, n) {
  var t = hn(e, n);
  if (!t) return e + "";
  var i = t[0], a = t[1], l = a - (Vl = Math.max(-8, Math.min(8, Math.floor(a / 3))) * 3) + 1, f = i.length;
  return l === f ? i : l > f ? i + new Array(l - f + 1).join("0") : l > 0 ? i.slice(0, l) + "." + i.slice(l) : "0." + new Array(1 - l).join("0") + hn(e, Math.max(0, n + l - 1))[0];
}
function ma(e, n) {
  var t = hn(e, n);
  if (!t) return e + "";
  var i = t[0], a = t[1];
  return a < 0 ? "0." + new Array(-a).join("0") + i : i.length > a + 1 ? i.slice(0, a + 1) + "." + i.slice(a + 1) : i + new Array(a - i.length + 2).join("0");
}
const pa = {
  "%": (e, n) => (e * 100).toFixed(n),
  b: (e) => Math.round(e).toString(2),
  c: (e) => e + "",
  d: G0,
  e: (e, n) => e.toExponential(n),
  f: (e, n) => e.toFixed(n),
  g: (e, n) => e.toPrecision(n),
  o: (e) => Math.round(e).toString(8),
  p: (e, n) => ma(e * 100, n),
  r: ma,
  s: Q0,
  X: (e) => Math.round(e).toString(16).toUpperCase(),
  x: (e) => Math.round(e).toString(16)
};
function wa(e) {
  return e;
}
var xa = Array.prototype.map, va = ["y", "z", "a", "f", "p", "n", "µ", "m", "", "k", "M", "G", "T", "P", "E", "Z", "Y"];
function es(e) {
  var n = e.grouping === void 0 || e.thousands === void 0 ? wa : V0(xa.call(e.grouping, Number), e.thousands + ""), t = e.currency === void 0 ? "" : e.currency[0] + "", i = e.currency === void 0 ? "" : e.currency[1] + "", a = e.decimal === void 0 ? "." : e.decimal + "", l = e.numerals === void 0 ? wa : q0(xa.call(e.numerals, String)), f = e.percent === void 0 ? "%" : e.percent + "", r = e.minus === void 0 ? "−" : e.minus + "", s = e.nan === void 0 ? "NaN" : e.nan + "";
  function o(h) {
    h = Ft(h);
    var d = h.fill, u = h.align, _ = h.sign, v = h.symbol, y = h.zero, A = h.width, x = h.comma, k = h.precision, g = h.trim, p = h.type;
    p === "n" ? (x = !0, p = "g") : pa[p] || (k === void 0 && (k = 12), g = !0, p = "g"), (y || d === "0" && u === "=") && (y = !0, d = "0", u = "=");
    var R = v === "$" ? t : v === "#" && /[boxX]/.test(p) ? "0" + p.toLowerCase() : "", z = v === "$" ? i : /[%p]/.test(p) ? f : "", E = pa[p], m = /[defgprs%]/.test(p);
    k = k === void 0 ? 6 : /[gprs]/.test(p) ? Math.max(1, Math.min(21, k)) : Math.max(0, Math.min(20, k));
    function T(w) {
      var I = R, N = z, O, V, se;
      if (p === "c")
        N = E(w) + N, w = "";
      else {
        w = +w;
        var U = w < 0 || 1 / w < 0;
        if (w = isNaN(w) ? s : E(Math.abs(w), k), g && (w = J0(w)), U && +w == 0 && _ !== "+" && (U = !1), I = (U ? _ === "(" ? _ : r : _ === "-" || _ === "(" ? "" : _) + I, N = (p === "s" ? va[8 + Vl / 3] : "") + N + (U && _ === "(" ? ")" : ""), m) {
          for (O = -1, V = w.length; ++O < V; )
            if (se = w.charCodeAt(O), 48 > se || se > 57) {
              N = (se === 46 ? a + w.slice(O + 1) : w.slice(O)) + N, w = w.slice(0, O);
              break;
            }
        }
      }
      x && !y && (w = n(w, 1 / 0));
      var Y = I.length + w.length + N.length, J = Y < A ? new Array(A - Y + 1).join(d) : "";
      switch (x && y && (w = n(J + w, J.length ? A - N.length : 1 / 0), J = ""), u) {
        case "<":
          w = I + w + N + J;
          break;
        case "=":
          w = I + J + w + N;
          break;
        case "^":
          w = J.slice(0, Y = J.length >> 1) + I + w + N + J.slice(Y);
          break;
        default:
          w = J + I + w + N;
          break;
      }
      return l(w);
    }
    return T.toString = function() {
      return h + "";
    }, T;
  }
  function c(h, d) {
    var u = o((h = Ft(h), h.type = "f", h)), _ = Math.max(-8, Math.min(8, Math.floor(ht(d) / 3))) * 3, v = Math.pow(10, -_), y = va[8 + _ / 3];
    return function(A) {
      return u(v * A) + y;
    };
  }
  return {
    format: o,
    formatPrefix: c
  };
}
var Qt, gi, ql;
ts({
  thousands: ",",
  grouping: [3],
  currency: ["$", ""]
});
function ts(e) {
  return Qt = es(e), gi = Qt.format, ql = Qt.formatPrefix, Qt;
}
function ns(e) {
  return Math.max(0, -ht(Math.abs(e)));
}
function is(e, n) {
  return Math.max(0, Math.max(-8, Math.min(8, Math.floor(ht(n) / 3))) * 3 - ht(Math.abs(e)));
}
function as(e, n) {
  return e = Math.abs(e), n = Math.abs(n) - e, Math.max(0, ht(n) - ht(e)) + 1;
}
function ls(e, n, t, i) {
  var a = $0(e, n, t), l;
  switch (i = Ft(i ?? ",f"), i.type) {
    case "s": {
      var f = Math.max(Math.abs(e), Math.abs(n));
      return i.precision == null && !isNaN(l = is(a, f)) && (i.precision = l), ql(i, f);
    }
    case "":
    case "e":
    case "g":
    case "p":
    case "r": {
      i.precision == null && !isNaN(l = as(a, Math.max(Math.abs(e), Math.abs(n)))) && (i.precision = l - (i.type === "e"));
      break;
    }
    case "f":
    case "%": {
      i.precision == null && !isNaN(l = ns(a)) && (i.precision = l - (i.type === "%") * 2);
      break;
    }
  }
  return gi(i);
}
function fs(e) {
  var n = e.domain;
  return e.ticks = function(t) {
    var i = n();
    return Jn(i[0], i[i.length - 1], t ?? 10);
  }, e.tickFormat = function(t, i) {
    var a = n();
    return ls(a[0], a[a.length - 1], t ?? 10, i);
  }, e.nice = function(t) {
    t == null && (t = 10);
    var i = n(), a = 0, l = i.length - 1, f = i[a], r = i[l], s, o, c = 10;
    for (r < f && (o = f, f = r, r = o, o = a, a = l, l = o); c-- > 0; ) {
      if (o = Qn(f, r, t), o === s)
        return i[a] = f, i[l] = r, n(i);
      if (o > 0)
        f = Math.floor(f / o) * o, r = Math.ceil(r / o) * o;
      else if (o < 0)
        f = Math.ceil(f * o) / o, r = Math.floor(r * o) / o;
      else
        break;
      s = o;
    }
    return e;
  }, e;
}
function un() {
  var e = Y0();
  return e.copy = function() {
    return Yl(e, un());
  }, Kl.apply(e, arguments), fs(e);
}
function rs(e, n) {
  e = e.slice();
  var t = 0, i = e.length - 1, a = e[t], l = e[i], f;
  return l < a && (f = t, t = i, i = f, f = a, a = l, l = f), e[t] = n.floor(a), e[i] = n.ceil(l), e;
}
function ya(e) {
  return Math.log(e);
}
function ka(e) {
  return Math.exp(e);
}
function os(e) {
  return -Math.log(-e);
}
function ss(e) {
  return -Math.exp(-e);
}
function cs(e) {
  return isFinite(e) ? +("1e" + e) : e < 0 ? 0 : e;
}
function ds(e) {
  return e === 10 ? cs : e === Math.E ? Math.exp : (n) => Math.pow(e, n);
}
function hs(e) {
  return e === Math.E ? Math.log : e === 10 && Math.log10 || e === 2 && Math.log2 || (e = Math.log(e), (n) => Math.log(n) / e);
}
function Ea(e) {
  return (n, t) => -e(-n, t);
}
function us(e) {
  const n = e(ya, ka), t = n.domain;
  let i = 10, a, l;
  function f() {
    return a = hs(i), l = ds(i), t()[0] < 0 ? (a = Ea(a), l = Ea(l), e(os, ss)) : e(ya, ka), n;
  }
  return n.base = function(r) {
    return arguments.length ? (i = +r, f()) : i;
  }, n.domain = function(r) {
    return arguments.length ? (t(r), f()) : t();
  }, n.ticks = (r) => {
    const s = t();
    let o = s[0], c = s[s.length - 1];
    const h = c < o;
    h && ([o, c] = [c, o]);
    let d = a(o), u = a(c), _, v;
    const y = r == null ? 10 : +r;
    let A = [];
    if (!(i % 1) && u - d < y) {
      if (d = Math.floor(d), u = Math.ceil(u), o > 0) {
        for (; d <= u; ++d)
          for (_ = 1; _ < i; ++_)
            if (v = d < 0 ? _ / l(-d) : _ * l(d), !(v < o)) {
              if (v > c) break;
              A.push(v);
            }
      } else for (; d <= u; ++d)
        for (_ = i - 1; _ >= 1; --_)
          if (v = d > 0 ? _ / l(-d) : _ * l(d), !(v < o)) {
            if (v > c) break;
            A.push(v);
          }
      A.length * 2 < y && (A = Jn(o, c, y));
    } else
      A = Jn(d, u, Math.min(u - d, y)).map(l);
    return h ? A.reverse() : A;
  }, n.tickFormat = (r, s) => {
    if (r == null && (r = 10), s == null && (s = i === 10 ? "s" : ","), typeof s != "function" && (!(i % 1) && (s = Ft(s)).precision == null && (s.trim = !0), s = gi(s)), r === 1 / 0) return s;
    const o = Math.max(1, i * r / n.ticks().length);
    return (c) => {
      let h = c / l(Math.round(a(c)));
      return h * i < i - 0.5 && (h *= i), h <= o ? s(c) : "";
    };
  }, n.nice = () => t(rs(t(), {
    floor: (r) => l(Math.floor(a(r))),
    ceil: (r) => l(Math.ceil(a(r)))
  })), n;
}
function Wl() {
  const e = us(Gl()).domain([1, 10]);
  return e.copy = () => Yl(e, Wl()).base(e.base()), Kl.apply(e, arguments), e;
}
function _s(e) {
  jt(e, "svelte-hl1o0t", "main.svelte-hl1o0t.svelte-hl1o0t{font-family:sans-serif;user-select:none}div.svelte-hl1o0t.svelte-hl1o0t{position:relative}div.svelte-hl1o0t svg.svelte-hl1o0t,div.svelte-hl1o0t canvas.svelte-hl1o0t{position:absolute;left:0;top:0}svg.svelte-hl1o0t text.svelte-hl1o0t{font-family:sans-serif;font-size:10px}");
}
function Aa(e, n, t) {
  const i = e.slice();
  return i[13] = n[t], i;
}
function Ma(e) {
  let n, t, i, a, l, f, r = (
    /*tickFormat*/
    e[5](
      /*x*/
      e[13]
    ) + ""
  ), s, o, c;
  return {
    c() {
      n = G("line"), f = G("text"), s = j(r), b(n, "x1", t = /*xScale*/
      e[3](
        /*x*/
        e[13]
      )), b(n, "x2", i = /*xScale*/
      e[3](
        /*x*/
        e[13]
      )), b(n, "y1", a = /*height*/
      e[1] + 1), b(n, "y2", l = /*height*/
      e[1] + 5), M(n, "stroke", "black"), b(f, "x", o = /*xScale*/
      e[3](
        /*x*/
        e[13]
      )), b(f, "y", c = /*height*/
      e[1] + 7), b(f, "class", "svelte-hl1o0t"), M(f, "fill", "black"), M(f, "text-anchor", "middle"), M(f, "dominant-baseline", "hanging");
    },
    m(h, d) {
      C(h, n, d), C(h, f, d), S(f, s);
    },
    p(h, d) {
      d & /*xScale, ticks*/
      72 && t !== (t = /*xScale*/
      h[3](
        /*x*/
        h[13]
      )) && b(n, "x1", t), d & /*xScale, ticks*/
      72 && i !== (i = /*xScale*/
      h[3](
        /*x*/
        h[13]
      )) && b(n, "x2", i), d & /*height*/
      2 && a !== (a = /*height*/
      h[1] + 1) && b(n, "y1", a), d & /*height*/
      2 && l !== (l = /*height*/
      h[1] + 5) && b(n, "y2", l), d & /*tickFormat, ticks*/
      96 && r !== (r = /*tickFormat*/
      h[5](
        /*x*/
        h[13]
      ) + "") && W(s, r), d & /*xScale, ticks*/
      72 && o !== (o = /*xScale*/
      h[3](
        /*x*/
        h[13]
      )) && b(f, "x", o), d & /*height*/
      2 && c !== (c = /*height*/
      h[1] + 7) && b(f, "y", c);
    },
    d(h) {
      h && (L(n), L(f));
    }
  };
}
function bs(e) {
  let n, t, i, a, l = `${/*width*/
  e[0]}px`, f = `${/*height*/
  e[1]}px`, r = `${/*paddingLeft*/
  e[8]}px`, s, o, c, h, d, u, _ = `${-xt}px`, v = `${/*width*/
  e[0] + /*paddingLeft*/
  e[8] + /*paddingRight*/
  e[7]}px`, y = `${/*height*/
  e[1] + 30}px`, A = me(
    /*ticks*/
    e[6]
  ), x = [];
  for (let k = 0; k < A.length; k += 1)
    x[k] = Ma(Aa(e, A, k));
  return {
    c() {
      n = D("main"), t = D("div"), i = D("canvas"), s = K(), o = G("svg"), c = G("g");
      for (let k = 0; k < x.length; k += 1)
        x[k].c();
      b(i, "width", a = /*discretizedScheme*/
      e[2].length), b(i, "height", 1), b(i, "class", "svelte-hl1o0t"), M(i, "width", l), M(i, "height", f), M(i, "left", r), b(c, "transform", h = "translate(" + /*paddingLeft*/
      (e[8] + xt) + ", 0)"), b(o, "width", d = /*width*/
      e[0] + /*paddingLeft*/
      e[8] + /*paddingRight*/
      e[7] + xt * 2), b(o, "height", u = /*height*/
      e[1] + 30), b(o, "class", "svelte-hl1o0t"), M(o, "left", _), b(t, "class", "svelte-hl1o0t"), M(t, "position", "relative"), M(t, "width", v), M(t, "height", y), b(n, "class", "svelte-hl1o0t");
    },
    m(k, g) {
      C(k, n, g), S(n, t), S(t, i), e[12](i), S(t, s), S(t, o), S(o, c);
      for (let p = 0; p < x.length; p += 1)
        x[p] && x[p].m(c, null);
    },
    p(k, [g]) {
      if (g & /*discretizedScheme*/
      4 && a !== (a = /*discretizedScheme*/
      k[2].length) && b(i, "width", a), g & /*width*/
      1 && l !== (l = `${/*width*/
      k[0]}px`) && M(i, "width", l), g & /*height*/
      2 && f !== (f = `${/*height*/
      k[1]}px`) && M(i, "height", f), g & /*paddingLeft*/
      256 && r !== (r = `${/*paddingLeft*/
      k[8]}px`) && M(i, "left", r), g & /*xScale, ticks, height, tickFormat*/
      106) {
        A = me(
          /*ticks*/
          k[6]
        );
        let p;
        for (p = 0; p < A.length; p += 1) {
          const R = Aa(k, A, p);
          x[p] ? x[p].p(R, g) : (x[p] = Ma(R), x[p].c(), x[p].m(c, null));
        }
        for (; p < x.length; p += 1)
          x[p].d(1);
        x.length = A.length;
      }
      g & /*paddingLeft*/
      256 && h !== (h = "translate(" + /*paddingLeft*/
      (k[8] + xt) + ", 0)") && b(c, "transform", h), g & /*width, paddingLeft, paddingRight*/
      385 && d !== (d = /*width*/
      k[0] + /*paddingLeft*/
      k[8] + /*paddingRight*/
      k[7] + xt * 2) && b(o, "width", d), g & /*height*/
      2 && u !== (u = /*height*/
      k[1] + 30) && b(o, "height", u), g & /*width, paddingLeft, paddingRight*/
      385 && v !== (v = `${/*width*/
      k[0] + /*paddingLeft*/
      k[8] + /*paddingRight*/
      k[7]}px`) && M(t, "width", v), g & /*height*/
      2 && y !== (y = `${/*height*/
      k[1] + 30}px`) && M(t, "height", y);
    },
    i: fe,
    o: fe,
    d(k) {
      k && L(n), e[12](null), mt(x, k);
    }
  };
}
let Sa = 5, xt = 20;
function gs(e, n, t) {
  let i, a, l, f, r, s, o, { scale: c } = n, { padding: h } = n, { width: d = 300 } = n, { height: u = 10 } = n, _;
  ci(() => {
    let y = _.getContext("2d"), A = new ImageData(l.length, 1), x = l.bytes();
    for (let k = 0; k < x.length; k++)
      A.data[k] = x[k];
    y.putImageData(A, 0, 0);
  });
  function v(y) {
    Zt[y ? "unshift" : "push"](() => {
      _ = y, t(4, _);
    });
  }
  return e.$$set = (y) => {
    "scale" in y && t(9, c = y.scale), "padding" in y && t(10, h = y.padding), "width" in y && t(0, d = y.width), "height" in y && t(1, u = y.height);
  }, e.$$.update = () => {
    e.$$.dirty & /*padding*/
    1024 && t(8, i = (h == null ? void 0 : h.left) ?? 30), e.$$.dirty & /*padding*/
    1024 && t(7, a = (h == null ? void 0 : h.right) ?? 30), e.$$.dirty & /*scale, width*/
    513 && t(2, l = new Pl(Bl(c.scheme), Math.round(d))), e.$$.dirty & /*width, discretizedScheme*/
    5 && t(11, f = d / l.length), e.$$.dirty & /*scale, pixelSize, width*/
    2561 && t(3, r = c.type == "linear" ? un(c.domain, [f / 2, d - f / 2]) : Wl(c.domain, [f / 2, d - f / 2])), e.$$.dirty & /*xScale*/
    8 && t(6, s = r.ticks(Sa)), e.$$.dirty & /*xScale*/
    8 && t(5, o = r.tickFormat(Sa));
  }, [
    d,
    u,
    l,
    r,
    _,
    o,
    s,
    a,
    i,
    c,
    h,
    f,
    v
  ];
}
class Jl extends Ve {
  constructor(n) {
    super(), Ge(
      this,
      n,
      gs,
      bs,
      Ye,
      {
        scale: 9,
        padding: 10,
        width: 0,
        height: 1
      },
      _s
    );
  }
}
function ms(e) {
  jt(e, "svelte-3d7fhm", ".container.svelte-3d7fhm.svelte-3d7fhm{white-space:nowrap}span.is-before.svelte-3d7fhm.svelte-3d7fhm,span.is-after.svelte-3d7fhm.svelte-3d7fhm{position:relative;color:#888;font-size:0.7em;width:8em;height:1em;line-height:1em;display:inline-block;white-space:nowrap;overflow:hidden}span.is-before.svelte-3d7fhm.svelte-3d7fhm{position:relative}span.is-after.svelte-3d7fhm>span.svelte-3d7fhm,span.is-before.svelte-3d7fhm>span.svelte-3d7fhm{display:inline-block;position:absolute;bottom:0;top:0}span.is-before.svelte-3d7fhm>span.svelte-3d7fhm{right:0}span.is-after.svelte-3d7fhm>span.svelte-3d7fhm{left:0}span.is-center.svelte-3d7fhm.svelte-3d7fhm{padding:2px 5px;margin-left:2px;margin-right:2px;background:#f0f0f0;color:#000;font-size:1em}");
}
function ps(e) {
  let n, t, i, a, l, f, r = (
    /*labels*/
    (e[0][
      /*index*/
      e[1]
    ] ?? /*index*/
    e[1]) + ""
  ), s, o, c, h, d;
  return {
    c() {
      n = D("span"), t = D("span"), i = D("span"), a = j(
        /*beforeText*/
        e[3]
      ), l = K(), f = D("span"), s = j(r), o = K(), c = D("span"), h = D("span"), d = j(
        /*afterText*/
        e[2]
      ), b(i, "class", "svelte-3d7fhm"), b(t, "class", "is-before svelte-3d7fhm"), b(f, "class", "is-center svelte-3d7fhm"), b(h, "class", "svelte-3d7fhm"), b(c, "class", "is-after svelte-3d7fhm"), b(n, "class", "container svelte-3d7fhm");
    },
    m(u, _) {
      C(u, n, _), S(n, t), S(t, i), S(i, a), S(n, l), S(n, f), S(f, s), S(n, o), S(n, c), S(c, h), S(h, d);
    },
    p(u, [_]) {
      _ & /*beforeText*/
      8 && W(
        a,
        /*beforeText*/
        u[3]
      ), _ & /*labels, index*/
      3 && r !== (r = /*labels*/
      (u[0][
        /*index*/
        u[1]
      ] ?? /*index*/
      u[1]) + "") && W(s, r), _ & /*afterText*/
      4 && W(
        d,
        /*afterText*/
        u[2]
      );
    },
    i: fe,
    o: fe,
    d(u) {
      u && L(n);
    }
  };
}
function ws(e, n, t) {
  let i, a, { labels: l } = n, { index: f } = n;
  return e.$$set = (r) => {
    "labels" in r && t(0, l = r.labels), "index" in r && t(1, f = r.index);
  }, e.$$.update = () => {
    e.$$.dirty & /*labels, index*/
    3 && t(3, i = l.slice(Math.max(0, f - 5), f).join(", ")), e.$$.dirty & /*labels, index*/
    3 && t(2, a = l.slice(f + 1, f + 6).join(", "));
  }, [l, f, a, i];
}
class mi extends Ve {
  constructor(n) {
    super(), Ge(this, n, ws, ps, Ye, { labels: 0, index: 1 }, ms);
  }
}
function xs(e) {
  let n, t, i, a = `${/*width*/
  e[1]}px`, l = `${/*height*/
  e[2]}px`;
  return {
    c() {
      n = D("canvas"), b(n, "width", t = /*matrix*/
      e[0].shape[1]), b(n, "height", i = /*matrix*/
      e[0].shape[0]), M(n, "width", a), M(n, "height", l), M(n, "image-rendering", "pixelated"), M(n, "background", "gray");
    },
    m(f, r) {
      C(f, n, r), e[5](n);
    },
    p(f, [r]) {
      r & /*matrix*/
      1 && t !== (t = /*matrix*/
      f[0].shape[1]) && b(n, "width", t), r & /*matrix*/
      1 && i !== (i = /*matrix*/
      f[0].shape[0]) && b(n, "height", i), r & /*width*/
      2 && a !== (a = `${/*width*/
      f[1]}px`) && M(n, "width", a), r & /*height*/
      4 && l !== (l = `${/*height*/
      f[2]}px`) && M(n, "height", l);
    },
    i: fe,
    o: fe,
    d(f) {
      f && L(n), e[5](null);
    }
  };
}
function vs(e, n, t) {
  let { matrix: i } = n, { width: a = 500 } = n, { height: l = 500 } = n, { scale: f } = n, r;
  ci(() => {
    D0(r, i, f);
  });
  function s(o) {
    Zt[o ? "unshift" : "push"](() => {
      r = o, t(3, r);
    });
  }
  return e.$$set = (o) => {
    "matrix" in o && t(0, i = o.matrix), "width" in o && t(1, a = o.width), "height" in o && t(2, l = o.height), "scale" in o && t(4, f = o.scale);
  }, [i, a, l, r, f, s];
}
class ys extends Ve {
  constructor(n) {
    super(), Ge(this, n, vs, xs, Ye, { matrix: 0, width: 1, height: 2, scale: 4 });
  }
}
let ks = document.createElement("canvas"), za = ks.getContext("2d");
function Es(e, n) {
  return za.font = n, za.measureText(e);
}
function As(e) {
  jt(e, "svelte-1nh381f", "main.svelte-1nh381f.svelte-1nh381f{font-family:system-ui, sans-serif;font-size:12px}.heatmap.svelte-1nh381f .tooltip.svelte-1nh381f{position:absolute;background:white;border:1px solid black;padding:3px;pointer-events:none;min-width:250px;max-width:400px;z-index:10;line-height:20px}svg.svelte-1nh381f text.svelte-1nh381f{font-family:system-ui, sans-serif;font-size:12px}");
}
function Un(e) {
  const n = e.slice(), t = (
    /*cursor*/
    n[16].x.toFixed(0)
  );
  n[35] = t;
  const i = (
    /*cursor*/
    n[16].y.toFixed(0)
  );
  n[36] = i;
  const a = Math.max(12, ti(
    /*xLabel*/
    n[35]
  ).width) + 8;
  n[37] = a;
  const l = Math.max(12, ti(
    /*yLabel*/
    n[36]
  ).width) + /*tickTotal*/
  n[22] + 2;
  return n[38] = l, n;
}
function Fn(e) {
  const n = e.slice(), t = (
    /*xScale*/
    n[3](
      /*cursor*/
      n[16].x
    )
  );
  n[33] = t;
  const i = (
    /*yScale*/
    n[2](
      /*cursor*/
      n[16].y
    )
  );
  return n[34] = i, n;
}
function Na(e, n, t) {
  const i = e.slice();
  i[39] = n[t];
  const a = (
    /*yScale*/
    i[2](
      /*value*/
      i[39]
    )
  );
  return i[34] = a, i;
}
function Ra(e, n, t) {
  const i = e.slice();
  i[39] = n[t];
  const a = (
    /*xScale*/
    i[3](
      /*value*/
      i[39]
    )
  );
  return i[33] = a, i;
}
function Ta(e) {
  let n, t, i = me(
    /*xTicks*/
    e[18]
  ), a = [];
  for (let f = 0; f < i.length; f += 1)
    a[f] = Da(Ra(e, i, f));
  let l = (
    /*hasXAxisTitle*/
    e[11] && Ia(e)
  );
  return {
    c() {
      for (let f = 0; f < a.length; f += 1)
        a[f].c();
      n = Ze(), l && l.c(), t = Ze();
    },
    m(f, r) {
      for (let s = 0; s < a.length; s += 1)
        a[s] && a[s].m(f, r);
      C(f, n, r), l && l.m(f, r), C(f, t, r);
    },
    p(f, r) {
      if (r[0] & /*xScale, xTicks, tickTotal*/
      4456456) {
        i = me(
          /*xTicks*/
          f[18]
        );
        let s;
        for (s = 0; s < i.length; s += 1) {
          const o = Ra(f, i, s);
          a[s] ? a[s].p(o, r) : (a[s] = Da(o), a[s].c(), a[s].m(n.parentNode, n));
        }
        for (; s < a.length; s += 1)
          a[s].d(1);
        a.length = i.length;
      }
      /*hasXAxisTitle*/
      f[11] ? l ? l.p(f, r) : (l = Ia(f), l.c(), l.m(t.parentNode, t)) : l && (l.d(1), l = null);
    },
    d(f) {
      f && (L(n), L(t)), mt(a, f), l && l.d(f);
    }
  };
}
function Da(e) {
  let n, t, i, a, l = (
    /*value*/
    e[39] + ""
  ), f, r;
  return {
    c() {
      n = G("line"), a = G("text"), f = j(l), b(n, "x1", t = /*x*/
      e[33]), b(n, "x2", i = /*x*/
      e[33]), b(n, "y1", -ke), b(n, "y2", -ke - ut), M(n, "stroke", "black"), b(a, "x", r = /*x*/
      e[33]), b(a, "y", -/*tickTotal*/
      e[22]), b(a, "class", "svelte-1nh381f"), M(a, "text-anchor", "middle"), M(a, "dominant-baseline", "bottom");
    },
    m(s, o) {
      C(s, n, o), C(s, a, o), S(a, f);
    },
    p(s, o) {
      o[0] & /*xScale, xTicks*/
      262152 && t !== (t = /*x*/
      s[33]) && b(n, "x1", t), o[0] & /*xScale, xTicks*/
      262152 && i !== (i = /*x*/
      s[33]) && b(n, "x2", i), o[0] & /*xTicks*/
      262144 && l !== (l = /*value*/
      s[39] + "") && W(f, l), o[0] & /*xScale, xTicks*/
      262152 && r !== (r = /*x*/
      s[33]) && b(a, "x", r);
    },
    d(s) {
      s && (L(n), L(a));
    }
  };
}
function Ia(e) {
  var f, r;
  let n, t = (
    /*spec*/
    (((r = (f = e[1]) == null ? void 0 : f.xAxis) == null ? void 0 : r.title) ?? "column") + ""
  ), i, a, l;
  return {
    c() {
      n = G("text"), i = j(t), b(n, "x", a = /*plotWidth*/
      e[7] / 2), b(n, "y", l = -/*tickTotal*/
      e[22] - /*labelDimensions*/
      e[10].height - 4), b(n, "class", "svelte-1nh381f"), M(n, "text-anchor", "middle");
    },
    m(s, o) {
      C(s, n, o), S(n, i);
    },
    p(s, o) {
      var c, h;
      o[0] & /*spec*/
      2 && t !== (t = /*spec*/
      (((h = (c = s[1]) == null ? void 0 : c.xAxis) == null ? void 0 : h.title) ?? "column") + "") && W(i, t), o[0] & /*plotWidth*/
      128 && a !== (a = /*plotWidth*/
      s[7] / 2) && b(n, "x", a), o[0] & /*labelDimensions*/
      1024 && l !== (l = -/*tickTotal*/
      s[22] - /*labelDimensions*/
      s[10].height - 4) && b(n, "y", l);
    },
    d(s) {
      s && L(n);
    }
  };
}
function La(e) {
  let n, t, i = me(
    /*yTicks*/
    e[17]
  ), a = [];
  for (let f = 0; f < i.length; f += 1)
    a[f] = Ca(Na(e, i, f));
  let l = (
    /*hasYAxisTitle*/
    e[13] && Za(e)
  );
  return {
    c() {
      for (let f = 0; f < a.length; f += 1)
        a[f].c();
      n = Ze(), l && l.c(), t = Ze();
    },
    m(f, r) {
      for (let s = 0; s < a.length; s += 1)
        a[s] && a[s].m(f, r);
      C(f, n, r), l && l.m(f, r), C(f, t, r);
    },
    p(f, r) {
      if (r[0] & /*yScale, yTicks*/
      131076) {
        i = me(
          /*yTicks*/
          f[17]
        );
        let s;
        for (s = 0; s < i.length; s += 1) {
          const o = Na(f, i, s);
          a[s] ? a[s].p(o, r) : (a[s] = Ca(o), a[s].c(), a[s].m(n.parentNode, n));
        }
        for (; s < a.length; s += 1)
          a[s].d(1);
        a.length = i.length;
      }
      /*hasYAxisTitle*/
      f[13] ? l ? l.p(f, r) : (l = Za(f), l.c(), l.m(t.parentNode, t)) : l && (l.d(1), l = null);
    },
    d(f) {
      f && (L(n), L(t)), mt(a, f), l && l.d(f);
    }
  };
}
function Ca(e) {
  let n, t, i, a, l = (
    /*value*/
    e[39] + ""
  ), f, r;
  return {
    c() {
      n = G("line"), a = G("text"), f = j(l), b(n, "x1", -ke), b(n, "x2", -ke - ut), b(n, "y1", t = /*y*/
      e[34]), b(n, "y2", i = /*y*/
      e[34]), M(n, "stroke", "black"), b(a, "x", -ke - ut - Ql), b(a, "y", r = /*y*/
      e[34]), b(a, "class", "svelte-1nh381f"), M(a, "text-anchor", "end"), M(a, "dominant-baseline", "middle");
    },
    m(s, o) {
      C(s, n, o), C(s, a, o), S(a, f);
    },
    p(s, o) {
      o[0] & /*yScale, yTicks*/
      131076 && t !== (t = /*y*/
      s[34]) && b(n, "y1", t), o[0] & /*yScale, yTicks*/
      131076 && i !== (i = /*y*/
      s[34]) && b(n, "y2", i), o[0] & /*yTicks*/
      131072 && l !== (l = /*value*/
      s[39] + "") && W(f, l), o[0] & /*yScale, yTicks*/
      131076 && r !== (r = /*y*/
      s[34]) && b(a, "y", r);
    },
    d(s) {
      s && (L(n), L(a));
    }
  };
}
function Za(e) {
  var f, r;
  let n, t = (
    /*spec*/
    (((r = (f = e[1]) == null ? void 0 : f.yAxis) == null ? void 0 : r.title) ?? "row") + ""
  ), i, a, l;
  return {
    c() {
      n = G("text"), i = j(t), b(n, "x", a = -/*plotHeight*/
      e[6] / 2), b(n, "y", l = -/*tickTotal*/
      e[22] - /*labelDimensions*/
      e[10].width - 4), b(n, "transform", "rotate(-90)"), b(n, "class", "svelte-1nh381f"), M(n, "text-anchor", "middle"), M(n, "dominant-baseline", "hanging");
    },
    m(s, o) {
      C(s, n, o), S(n, i);
    },
    p(s, o) {
      var c, h;
      o[0] & /*spec*/
      2 && t !== (t = /*spec*/
      (((h = (c = s[1]) == null ? void 0 : c.yAxis) == null ? void 0 : h.title) ?? "row") + "") && W(i, t), o[0] & /*plotHeight*/
      64 && a !== (a = -/*plotHeight*/
      s[6] / 2) && b(n, "x", a), o[0] & /*labelDimensions*/
      1024 && l !== (l = -/*tickTotal*/
      s[22] - /*labelDimensions*/
      s[10].width - 4) && b(n, "y", l);
    },
    d(s) {
      s && L(n);
    }
  };
}
function Oa(e) {
  let n, t, i, a, l, f, r, s, o, c, h, d, u, _ = (
    /*hasXAxis*/
    e[12] && /*hasYAxis*/
    e[14] && Ua(Un(e))
  );
  return {
    c() {
      n = G("line"), a = G("line"), r = G("line"), c = G("line"), _ && _.c(), u = Ze(), b(n, "x1", t = /*x*/
      e[33]), b(n, "x2", i = /*x*/
      e[33]), b(n, "y1", 0), b(
        n,
        "y2",
        /*plotHeight*/
        e[6]
      ), M(n, "stroke", "white"), b(a, "x1", l = /*x*/
      e[33]), b(a, "x2", f = /*x*/
      e[33]), b(a, "y1", 0), b(
        a,
        "y2",
        /*plotHeight*/
        e[6]
      ), M(a, "stroke", "black"), M(a, "stroke-dasharray", "1 1"), b(r, "x1", 0), b(
        r,
        "x2",
        /*plotWidth*/
        e[7]
      ), b(r, "y1", s = /*y*/
      e[34]), b(r, "y2", o = /*y*/
      e[34]), M(r, "stroke", "white"), b(c, "x1", 0), b(
        c,
        "x2",
        /*plotWidth*/
        e[7]
      ), b(c, "y1", h = /*y*/
      e[34]), b(c, "y2", d = /*y*/
      e[34]), M(c, "stroke", "black"), M(c, "stroke-dasharray", "1 1");
    },
    m(v, y) {
      C(v, n, y), C(v, a, y), C(v, r, y), C(v, c, y), _ && _.m(v, y), C(v, u, y);
    },
    p(v, y) {
      y[0] & /*xScale, cursor*/
      65544 && t !== (t = /*x*/
      v[33]) && b(n, "x1", t), y[0] & /*xScale, cursor*/
      65544 && i !== (i = /*x*/
      v[33]) && b(n, "x2", i), y[0] & /*plotHeight*/
      64 && b(
        n,
        "y2",
        /*plotHeight*/
        v[6]
      ), y[0] & /*xScale, cursor*/
      65544 && l !== (l = /*x*/
      v[33]) && b(a, "x1", l), y[0] & /*xScale, cursor*/
      65544 && f !== (f = /*x*/
      v[33]) && b(a, "x2", f), y[0] & /*plotHeight*/
      64 && b(
        a,
        "y2",
        /*plotHeight*/
        v[6]
      ), y[0] & /*plotWidth*/
      128 && b(
        r,
        "x2",
        /*plotWidth*/
        v[7]
      ), y[0] & /*yScale, cursor*/
      65540 && s !== (s = /*y*/
      v[34]) && b(r, "y1", s), y[0] & /*yScale, cursor*/
      65540 && o !== (o = /*y*/
      v[34]) && b(r, "y2", o), y[0] & /*plotWidth*/
      128 && b(
        c,
        "x2",
        /*plotWidth*/
        v[7]
      ), y[0] & /*yScale, cursor*/
      65540 && h !== (h = /*y*/
      v[34]) && b(c, "y1", h), y[0] & /*yScale, cursor*/
      65540 && d !== (d = /*y*/
      v[34]) && b(c, "y2", d), /*hasXAxis*/
      v[12] && /*hasYAxis*/
      v[14] ? _ ? _.p(Un(v), y) : (_ = Ua(Un(v)), _.c(), _.m(u.parentNode, u)) : _ && (_.d(1), _ = null);
    },
    d(v) {
      v && (L(n), L(a), L(r), L(c), L(u)), _ && _.d(v);
    }
  };
}
function Ua(e) {
  let n, t, i, a, l, f, r, s, o, c, h, d, u, _ = (
    /*xLabel*/
    e[35] + ""
  ), v, y, A, x, k, g, p = (
    /*yLabel*/
    e[36] + ""
  ), R, z;
  return {
    c() {
      n = G("rect"), f = G("rect"), c = G("line"), u = G("text"), v = j(_), A = G("line"), g = G("text"), R = j(p), b(n, "x", t = /*x*/
      e[33] - /*xBoxWidth*/
      e[37] / 2), b(n, "y", i = -/*labelDimensions*/
      e[10].height - /*tickTotal*/
      e[22] - 4), b(n, "width", a = /*xBoxWidth*/
      e[37]), b(n, "height", l = /*labelDimensions*/
      e[10].height + /*tickTotal*/
      e[22] + 4), M(n, "fill", "#f0f0f0"), b(f, "x", r = -/*yBoxWidth*/
      e[38] - 1), b(f, "y", s = /*y*/
      e[34] - 10), b(f, "width", o = /*yBoxWidth*/
      e[38]), b(f, "height", 20), M(f, "fill", "#f0f0f0"), b(c, "x1", h = /*x*/
      e[33]), b(c, "x2", d = /*x*/
      e[33]), b(c, "y1", -ke), b(c, "y2", -ke - ut), M(c, "stroke", "black"), b(u, "x", y = /*x*/
      e[33]), b(u, "y", -/*tickTotal*/
      e[22]), b(u, "class", "svelte-1nh381f"), M(u, "font-weight", "bold"), M(u, "text-anchor", "middle"), M(u, "dominant-baseline", "bottom"), b(A, "x1", -ke), b(A, "x2", -ke - ut), b(A, "y1", x = /*y*/
      e[34]), b(A, "y2", k = /*y*/
      e[34]), M(A, "stroke", "black"), b(g, "x", -/*tickTotal*/
      e[22]), b(g, "y", z = /*y*/
      e[34]), b(g, "class", "svelte-1nh381f"), M(g, "font-weight", "bold"), M(g, "text-anchor", "end"), M(g, "dominant-baseline", "middle");
    },
    m(E, m) {
      C(E, n, m), C(E, f, m), C(E, c, m), C(E, u, m), S(u, v), C(E, A, m), C(E, g, m), S(g, R);
    },
    p(E, m) {
      m[0] & /*xScale, cursor*/
      65544 && t !== (t = /*x*/
      E[33] - /*xBoxWidth*/
      E[37] / 2) && b(n, "x", t), m[0] & /*labelDimensions*/
      1024 && i !== (i = -/*labelDimensions*/
      E[10].height - /*tickTotal*/
      E[22] - 4) && b(n, "y", i), m[0] & /*cursor*/
      65536 && a !== (a = /*xBoxWidth*/
      E[37]) && b(n, "width", a), m[0] & /*labelDimensions*/
      1024 && l !== (l = /*labelDimensions*/
      E[10].height + /*tickTotal*/
      E[22] + 4) && b(n, "height", l), m[0] & /*cursor*/
      65536 && r !== (r = -/*yBoxWidth*/
      E[38] - 1) && b(f, "x", r), m[0] & /*yScale, cursor*/
      65540 && s !== (s = /*y*/
      E[34] - 10) && b(f, "y", s), m[0] & /*cursor*/
      65536 && o !== (o = /*yBoxWidth*/
      E[38]) && b(f, "width", o), m[0] & /*xScale, cursor*/
      65544 && h !== (h = /*x*/
      E[33]) && b(c, "x1", h), m[0] & /*xScale, cursor*/
      65544 && d !== (d = /*x*/
      E[33]) && b(c, "x2", d), m[0] & /*cursor*/
      65536 && _ !== (_ = /*xLabel*/
      E[35] + "") && W(v, _), m[0] & /*xScale, cursor*/
      65544 && y !== (y = /*x*/
      E[33]) && b(u, "x", y), m[0] & /*yScale, cursor*/
      65540 && x !== (x = /*y*/
      E[34]) && b(A, "y1", x), m[0] & /*yScale, cursor*/
      65540 && k !== (k = /*y*/
      E[34]) && b(A, "y2", k), m[0] & /*cursor*/
      65536 && p !== (p = /*yLabel*/
      E[36] + "") && W(R, p), m[0] & /*yScale, cursor*/
      65540 && z !== (z = /*y*/
      E[34]) && b(g, "y", z);
    },
    d(E) {
      E && (L(n), L(f), L(c), L(u), L(A), L(g));
    }
  };
}
function Fa(e) {
  var w, I, N, O, V, se;
  let n, t, i = (
    /*spec*/
    (((I = (w = e[1]) == null ? void 0 : w.xAxis) == null ? void 0 : I.title) ?? "column") + ""
  ), a, l, f = (
    /*cursor*/
    e[16].x + ""
  ), r, s, o, c, h = (
    /*spec*/
    (((O = (N = e[1]) == null ? void 0 : N.yAxis) == null ? void 0 : O.title) ?? "row") + ""
  ), d, u, _ = (
    /*cursor*/
    e[16].y + ""
  ), v, y, A, x, k, g = (
    /*matrix*/
    e[0].at(
      /*cursor*/
      e[16].y,
      /*cursor*/
      e[16].x
    ).toFixed(5) + ""
  ), p, R = `${/*xScale*/
  e[3](
    /*cursor*/
    e[16].x
  ) + /*paddingLeft*/
  e[5] + 5}px`, z = `${/*plotHeight*/
  e[6] - /*yScale*/
  e[2](
    /*cursor*/
    e[16].y
  ) + /*paddingBottom*/
  e[8] + 10}px`, E, m = (
    /*spec*/
    ((V = e[1]) == null ? void 0 : V.xLabels) && Ha(e)
  ), T = (
    /*spec*/
    ((se = e[1]) == null ? void 0 : se.yLabels) && $a(e)
  );
  return {
    c() {
      n = D("div"), t = D("div"), a = j(i), l = j(": "), r = j(f), s = K(), m && m.c(), o = K(), c = D("div"), d = j(h), u = j(": "), v = j(_), y = K(), T && T.c(), A = K(), x = D("div"), k = j("value: "), p = j(g), b(n, "class", "tooltip svelte-1nh381f"), M(n, "left", R), M(n, "bottom", z);
    },
    m(U, Y) {
      C(U, n, Y), S(n, t), S(t, a), S(t, l), S(t, r), S(t, s), m && m.m(t, null), S(n, o), S(n, c), S(c, d), S(c, u), S(c, v), S(c, y), T && T.m(c, null), S(n, A), S(n, x), S(x, k), S(x, p), E = !0;
    },
    p(U, Y) {
      var J, P, te, B, Re, pt;
      (!E || Y[0] & /*spec*/
      2) && i !== (i = /*spec*/
      (((P = (J = U[1]) == null ? void 0 : J.xAxis) == null ? void 0 : P.title) ?? "column") + "") && W(a, i), (!E || Y[0] & /*cursor*/
      65536) && f !== (f = /*cursor*/
      U[16].x + "") && W(r, f), /*spec*/
      (te = U[1]) != null && te.xLabels ? m ? (m.p(U, Y), Y[0] & /*spec*/
      2 && Z(m, 1)) : (m = Ha(U), m.c(), Z(m, 1), m.m(t, null)) : m && (be(), H(m, 1, 1, () => {
        m = null;
      }), ge()), (!E || Y[0] & /*spec*/
      2) && h !== (h = /*spec*/
      (((Re = (B = U[1]) == null ? void 0 : B.yAxis) == null ? void 0 : Re.title) ?? "row") + "") && W(d, h), (!E || Y[0] & /*cursor*/
      65536) && _ !== (_ = /*cursor*/
      U[16].y + "") && W(v, _), /*spec*/
      (pt = U[1]) != null && pt.yLabels ? T ? (T.p(U, Y), Y[0] & /*spec*/
      2 && Z(T, 1)) : (T = $a(U), T.c(), Z(T, 1), T.m(c, null)) : T && (be(), H(T, 1, 1, () => {
        T = null;
      }), ge()), (!E || Y[0] & /*matrix, cursor*/
      65537) && g !== (g = /*matrix*/
      U[0].at(
        /*cursor*/
        U[16].y,
        /*cursor*/
        U[16].x
      ).toFixed(5) + "") && W(p, g), Y[0] & /*xScale, cursor, paddingLeft*/
      65576 && R !== (R = `${/*xScale*/
      U[3](
        /*cursor*/
        U[16].x
      ) + /*paddingLeft*/
      U[5] + 5}px`) && M(n, "left", R), Y[0] & /*plotHeight, yScale, cursor, paddingBottom*/
      65860 && z !== (z = `${/*plotHeight*/
      U[6] - /*yScale*/
      U[2](
        /*cursor*/
        U[16].y
      ) + /*paddingBottom*/
      U[8] + 10}px`) && M(n, "bottom", z);
    },
    i(U) {
      E || (Z(m), Z(T), E = !0);
    },
    o(U) {
      H(m), H(T), E = !1;
    },
    d(U) {
      U && L(n), m && m.d(), T && T.d();
    }
  };
}
function Ha(e) {
  var i;
  let n, t;
  return n = new mi({
    props: {
      labels: (
        /*spec*/
        ((i = e[1]) == null ? void 0 : i.xLabels) ?? []
      ),
      index: (
        /*cursor*/
        e[16].x
      )
    }
  }), {
    c() {
      ue(n.$$.fragment);
    },
    m(a, l) {
      re(n, a, l), t = !0;
    },
    p(a, l) {
      var r;
      const f = {};
      l[0] & /*spec*/
      2 && (f.labels = /*spec*/
      ((r = a[1]) == null ? void 0 : r.xLabels) ?? []), l[0] & /*cursor*/
      65536 && (f.index = /*cursor*/
      a[16].x), n.$set(f);
    },
    i(a) {
      t || (Z(n.$$.fragment, a), t = !0);
    },
    o(a) {
      H(n.$$.fragment, a), t = !1;
    },
    d(a) {
      oe(n, a);
    }
  };
}
function $a(e) {
  var i;
  let n, t;
  return n = new mi({
    props: {
      labels: (
        /*spec*/
        ((i = e[1]) == null ? void 0 : i.yLabels) ?? []
      ),
      index: (
        /*cursor*/
        e[16].y
      )
    }
  }), {
    c() {
      ue(n.$$.fragment);
    },
    m(a, l) {
      re(n, a, l), t = !0;
    },
    p(a, l) {
      var r;
      const f = {};
      l[0] & /*spec*/
      2 && (f.labels = /*spec*/
      ((r = a[1]) == null ? void 0 : r.yLabels) ?? []), l[0] & /*cursor*/
      65536 && (f.index = /*cursor*/
      a[16].y), n.$set(f);
    },
    i(a) {
      t || (Z(n.$$.fragment, a), t = !0);
    },
    o(a) {
      H(n.$$.fragment, a), t = !1;
    },
    d(a) {
      oe(n, a);
    }
  };
}
function Ba(e) {
  let n, t;
  return n = new Jl({
    props: {
      scale: (
        /*heatmapScale*/
        e[19]
      ),
      padding: {
        left: (
          /*paddingLeft*/
          e[5]
        ),
        right: (
          /*paddingRight*/
          e[9]
        )
      },
      width: Math.min(
        200,
        /*plotWidth*/
        e[7]
      )
    }
  }), {
    c() {
      ue(n.$$.fragment);
    },
    m(i, a) {
      re(n, i, a), t = !0;
    },
    p(i, a) {
      const l = {};
      a[0] & /*heatmapScale*/
      524288 && (l.scale = /*heatmapScale*/
      i[19]), a[0] & /*paddingLeft, paddingRight*/
      544 && (l.padding = {
        left: (
          /*paddingLeft*/
          i[5]
        ),
        right: (
          /*paddingRight*/
          i[9]
        )
      }), a[0] & /*plotWidth*/
      128 && (l.width = Math.min(
        200,
        /*plotWidth*/
        i[7]
      )), n.$set(l);
    },
    i(i) {
      t || (Z(n.$$.fragment, i), t = !0);
    },
    o(i) {
      H(n.$$.fragment, i), t = !1;
    },
    d(i) {
      oe(n, i);
    }
  };
}
function Ms(e) {
  var T;
  let n, t, i, a, l = `${/*plotWidth*/
  e[7]}px`, f = `${/*plotHeight*/
  e[6]}px`, r = `${/*paddingTop*/
  e[4]}px ${/*paddingRight*/
  e[9]}px ${/*paddingBottom*/
  e[8]}px ${/*paddingLeft*/
  e[5]}px`, s, o, c, h, d, u, _, v = `${/*viewWidth*/
  e[21]}px`, y = `${/*viewHeight*/
  e[20]}px`, A, x, k, g;
  a = new ys({
    props: {
      matrix: (
        /*matrix*/
        e[0]
      ),
      width: (
        /*plotWidth*/
        e[7]
      ),
      height: (
        /*plotHeight*/
        e[6]
      ),
      scale: (
        /*heatmapScale*/
        e[19]
      )
    }
  });
  let p = (
    /*hasXAxis*/
    e[12] && Ta(e)
  ), R = (
    /*hasYAxis*/
    e[14] && La(e)
  ), z = (
    /*cursor*/
    e[16] != null && Oa(Fn(e))
  ), E = (
    /*cursor*/
    e[16] != null && Fa(e)
  ), m = (
    /*spec*/
    ((T = e[1]) == null ? void 0 : T.legend) !== null && Ba(e)
  );
  return {
    c() {
      n = D("main"), t = D("div"), i = D("div"), ue(a.$$.fragment), s = K(), o = G("svg"), c = G("g"), h = G("g"), p && p.c(), d = Ze(), R && R.c(), z && z.c(), _ = K(), E && E.c(), A = K(), m && m.c(), b(i, "role", "figure"), M(i, "width", l), M(i, "height", f), M(i, "padding", r), b(c, "transform", u = "translate(" + /*paddingLeft*/
      e[5] + "," + /*paddingTop*/
      e[4] + ")"), b(
        o,
        "width",
        /*viewWidth*/
        e[21]
      ), b(
        o,
        "height",
        /*viewHeight*/
        e[20]
      ), b(o, "class", "svelte-1nh381f"), M(o, "position", "absolute"), M(o, "left", "0"), M(o, "top", "0"), M(o, "pointer-events", "none"), M(o, "user-select", "none"), b(t, "class", "heatmap svelte-1nh381f"), M(t, "width", v), M(t, "height", y), M(t, "position", "relative"), b(n, "class", "svelte-1nh381f");
    },
    m(w, I) {
      C(w, n, I), S(n, t), S(t, i), re(a, i, null), e[30](i), S(t, s), S(t, o), S(o, c), S(c, h), p && p.m(h, null), S(h, d), R && R.m(h, null), z && z.m(c, null), S(t, _), E && E.m(t, null), S(n, A), m && m.m(n, null), x = !0, k || (g = [
        ye(
          i,
          "mousemove",
          /*canvasMouseMove*/
          e[23]
        ),
        ye(
          i,
          "mouseenter",
          /*canvasMouseEnter*/
          e[24]
        ),
        ye(
          i,
          "mouseleave",
          /*canvasMouseLeave*/
          e[25]
        ),
        ye(
          i,
          "mousedown",
          /*canvasMouseDown*/
          e[26]
        )
      ], k = !0);
    },
    p(w, I) {
      var O;
      const N = {};
      I[0] & /*matrix*/
      1 && (N.matrix = /*matrix*/
      w[0]), I[0] & /*plotWidth*/
      128 && (N.width = /*plotWidth*/
      w[7]), I[0] & /*plotHeight*/
      64 && (N.height = /*plotHeight*/
      w[6]), I[0] & /*heatmapScale*/
      524288 && (N.scale = /*heatmapScale*/
      w[19]), a.$set(N), I[0] & /*plotWidth*/
      128 && l !== (l = `${/*plotWidth*/
      w[7]}px`) && M(i, "width", l), I[0] & /*plotHeight*/
      64 && f !== (f = `${/*plotHeight*/
      w[6]}px`) && M(i, "height", f), I[0] & /*paddingTop, paddingRight, paddingBottom, paddingLeft*/
      816 && r !== (r = `${/*paddingTop*/
      w[4]}px ${/*paddingRight*/
      w[9]}px ${/*paddingBottom*/
      w[8]}px ${/*paddingLeft*/
      w[5]}px`) && M(i, "padding", r), /*hasXAxis*/
      w[12] ? p ? p.p(w, I) : (p = Ta(w), p.c(), p.m(h, d)) : p && (p.d(1), p = null), /*hasYAxis*/
      w[14] ? R ? R.p(w, I) : (R = La(w), R.c(), R.m(h, null)) : R && (R.d(1), R = null), /*cursor*/
      w[16] != null ? z ? z.p(Fn(w), I) : (z = Oa(Fn(w)), z.c(), z.m(c, null)) : z && (z.d(1), z = null), (!x || I[0] & /*paddingLeft, paddingTop*/
      48 && u !== (u = "translate(" + /*paddingLeft*/
      w[5] + "," + /*paddingTop*/
      w[4] + ")")) && b(c, "transform", u), (!x || I[0] & /*viewWidth*/
      2097152) && b(
        o,
        "width",
        /*viewWidth*/
        w[21]
      ), (!x || I[0] & /*viewHeight*/
      1048576) && b(
        o,
        "height",
        /*viewHeight*/
        w[20]
      ), /*cursor*/
      w[16] != null ? E ? (E.p(w, I), I[0] & /*cursor*/
      65536 && Z(E, 1)) : (E = Fa(w), E.c(), Z(E, 1), E.m(t, null)) : E && (be(), H(E, 1, 1, () => {
        E = null;
      }), ge()), I[0] & /*viewWidth*/
      2097152 && v !== (v = `${/*viewWidth*/
      w[21]}px`) && M(t, "width", v), I[0] & /*viewHeight*/
      1048576 && y !== (y = `${/*viewHeight*/
      w[20]}px`) && M(t, "height", y), /*spec*/
      ((O = w[1]) == null ? void 0 : O.legend) !== null ? m ? (m.p(w, I), I[0] & /*spec*/
      2 && Z(m, 1)) : (m = Ba(w), m.c(), Z(m, 1), m.m(n, null)) : m && (be(), H(m, 1, 1, () => {
        m = null;
      }), ge());
    },
    i(w) {
      x || (Z(a.$$.fragment, w), Z(E), Z(m), x = !0);
    },
    o(w) {
      H(a.$$.fragment, w), H(E), H(m), x = !1;
    },
    d(w) {
      w && L(n), oe(a), e[30](null), p && p.d(), R && R.d(), z && z.d(), E && E.d(), m && m.d(), k = !1, Ke(g);
    }
  };
}
function ti(e) {
  return Es(e, "12px system-ui,sans-serif");
}
function Ss(e, n, t) {
  let i = n, a = t, l = (Math.pow(10, Math.ceil(Math.log10(e - 1))) - 1).toFixed(0), f = ti(l);
  return i = Math.max(i, f.width), a = Math.max(a, f.actualBoundingBoxAscent - f.actualBoundingBoxDescent), i = Math.ceil(i), a = Math.ceil(a), { width: i, height: a };
}
function Pa(e, n) {
  let t = n.ticks(Math.round(e / 40)).filter((i) => Number.isInteger(i));
  if (t.length > 2) {
    let i = n.domain()[1] - 0.5, a = t[1] - t[0];
    i - t[t.length - 1] < a / 2 ? t[t.length - 1] = i : t.push(i);
  }
  return t;
}
const ut = 4, ke = 1, Ql = 3;
function zs(e, n, t) {
  let i, a, l, f, r, s, o, c, h, d, u, _, v, y, A, x, k, g, p, R, z, { matrix: E } = n, { spec: m = void 0 } = n;
  const T = ut + ke + Ql;
  let w, I = null, N = !1;
  function O(P) {
    let te = P.clientX - w.getBoundingClientRect().x - c, B = P.clientY - w.getBoundingClientRect().y - h;
    return te = Math.round(g.invert(te)), B = Math.round(p.invert(B)), te >= 0 && te < E.shape[1] && B >= 0 && B < E.shape[0] ? { x: te, y: B } : null;
  }
  function V(P) {
    N || t(16, I = O(P));
  }
  function se(P) {
    N || t(16, I = O(P));
  }
  function U(P) {
    N || t(16, I = null);
  }
  function Y(P) {
    N ? (t(16, I = null), N = !1) : I != null && (N = !0);
  }
  function J(P) {
    Zt[P ? "unshift" : "push"](() => {
      w = P, t(15, w);
    });
  }
  return e.$$set = (P) => {
    "matrix" in P && t(0, E = P.matrix), "spec" in P && t(1, m = P.spec);
  }, e.$$.update = () => {
    var P, te, B, Re, pt, pi;
    e.$$.dirty[0] & /*matrix*/
    1 && t(10, i = Ss(E.shape[0], 30, 0)), e.$$.dirty[0] & /*spec*/
    2 && t(12, a = (m == null ? void 0 : m.xAxis) !== null), e.$$.dirty[0] & /*spec*/
    2 && t(14, l = (m == null ? void 0 : m.yAxis) !== null), e.$$.dirty[0] & /*spec*/
    2 && t(11, f = ((P = m == null ? void 0 : m.xAxis) == null ? void 0 : P.title) !== null), e.$$.dirty[0] & /*spec*/
    2 && t(13, r = ((te = m == null ? void 0 : m.yAxis) == null ? void 0 : te.title) !== null), e.$$.dirty[0] & /*hasYAxis, labelDimensions, hasYAxisTitle*/
    25600 && t(29, s = l ? i.width + T + 4 + (r ? i.height + 4 : 0) : 0), e.$$.dirty[0] & /*hasXAxis, labelDimensions, hasXAxisTitle*/
    7168 && t(28, o = a ? i.height + T + 4 + (f ? i.height + 4 : 0) : 0), e.$$.dirty[0] & /*spec, paddingForYAxis*/
    536870914 && t(5, c = ((B = m == null ? void 0 : m.padding) == null ? void 0 : B.left) ?? s), e.$$.dirty[0] & /*spec, paddingForXAxis*/
    268435458 && t(4, h = ((Re = m == null ? void 0 : m.padding) == null ? void 0 : Re.top) ?? o), e.$$.dirty[0] & /*spec, labelDimensions*/
    1026 && t(9, d = ((pt = m == null ? void 0 : m.padding) == null ? void 0 : pt.right) ?? Math.max(4, Math.ceil(i.width / 2))), e.$$.dirty[0] & /*spec, labelDimensions*/
    1026 && t(8, u = ((pi = m == null ? void 0 : m.padding) == null ? void 0 : pi.bottom) ?? Math.max(12, Math.ceil(i.height / 2))), e.$$.dirty[0] & /*matrix*/
    1 && t(27, _ = z0(E.shape)), e.$$.dirty[0] & /*spec, defaultPlotSize*/
    134217730 && t(7, v = (m == null ? void 0 : m.width) ?? _.width), e.$$.dirty[0] & /*spec, defaultPlotSize*/
    134217730 && t(6, y = (m == null ? void 0 : m.height) ?? _.height), e.$$.dirty[0] & /*plotWidth, paddingLeft, paddingRight*/
    672 && t(21, A = v + c + d), e.$$.dirty[0] & /*plotHeight, paddingTop, paddingBottom*/
    336 && t(20, x = y + h + u), e.$$.dirty[0] & /*matrix, spec*/
    3 && t(19, k = jl(E, m == null ? void 0 : m.scale)), e.$$.dirty[0] & /*matrix, plotWidth*/
    129 && t(3, g = un([-0.5, E.shape[1] - 0.5], [0, v])), e.$$.dirty[0] & /*matrix, plotHeight*/
    65 && t(2, p = un([-0.5, E.shape[0] - 0.5], [0, y])), e.$$.dirty[0] & /*plotWidth, xScale*/
    136 && t(18, R = Pa(v, g)), e.$$.dirty[0] & /*plotHeight, yScale*/
    68 && t(17, z = Pa(y, p));
  }, [
    E,
    m,
    p,
    g,
    h,
    c,
    y,
    v,
    u,
    d,
    i,
    f,
    a,
    r,
    l,
    w,
    I,
    z,
    R,
    k,
    x,
    A,
    T,
    V,
    se,
    U,
    Y,
    _,
    o,
    s,
    J
  ];
}
class Ns extends Ve {
  constructor(n) {
    super(), Ge(this, n, zs, Ms, Ye, { matrix: 0, spec: 1 }, As, [-1, -1]);
  }
}
function Rs(e) {
  jt(e, "svelte-clglx1", "figure.svelte-clglx1.svelte-clglx1.svelte-clglx1{padding:0;margin:0}ul.svelte-clglx1.svelte-clglx1.svelte-clglx1{list-style-type:none;margin:0;padding:0;display:flex;flex-wrap:wrap}h4.svelte-clglx1.svelte-clglx1.svelte-clglx1{font-weight:normal;font-size:14px;font-family:sans-serif;margin:0;padding:0}ul.is-small-multiples.svelte-clglx1.svelte-clglx1.svelte-clglx1{display:flex;flex-direction:row;gap:10px}ul.has-nested-small-multiples.svelte-clglx1>li.svelte-clglx1>figure.svelte-clglx1{padding:4px}ul.has-nested-small-multiples.svelte-clglx1>li.svelte-clglx1>h4.svelte-clglx1{font-weight:bold;background:rgba(0, 0, 0, 0.1);padding:4px}");
}
function ja(e, n, t) {
  const i = e.slice();
  return i[3] = n[t], i[5] = t, i;
}
function Ts(e) {
  let n, t, i = me({ length: (
    /*tensor*/
    e[0].shape[0]
  ) }), a = [];
  for (let f = 0; f < i.length; f += 1)
    a[f] = Xa(ja(e, i, f));
  const l = (f) => H(a[f], 1, 1, () => {
    a[f] = null;
  });
  return {
    c() {
      n = D("ul");
      for (let f = 0; f < a.length; f += 1)
        a[f].c();
      b(n, "class", "svelte-clglx1"), Ln(n, "is-small-multiples", !0), Ln(
        n,
        "has-nested-small-multiples",
        /*dimensions*/
        e[1].slice(1).some(Ka)
      );
    },
    m(f, r) {
      C(f, n, r);
      for (let s = 0; s < a.length; s += 1)
        a[s] && a[s].m(n, null);
      t = !0;
    },
    p(f, r) {
      if (r & /*tensor, dimensions, spec*/
      7) {
        i = me({ length: (
          /*tensor*/
          f[0].shape[0]
        ) });
        let s;
        for (s = 0; s < i.length; s += 1) {
          const o = ja(f, i, s);
          a[s] ? (a[s].p(o, r), Z(a[s], 1)) : (a[s] = Xa(o), a[s].c(), Z(a[s], 1), a[s].m(n, null));
        }
        for (be(), s = i.length; s < a.length; s += 1)
          l(s);
        ge();
      }
      (!t || r & /*dimensions*/
      2) && Ln(
        n,
        "has-nested-small-multiples",
        /*dimensions*/
        f[1].slice(1).some(Ka)
      );
    },
    i(f) {
      if (!t) {
        for (let r = 0; r < i.length; r += 1)
          Z(a[r]);
        t = !0;
      }
    },
    o(f) {
      a = a.filter(Boolean);
      for (let r = 0; r < a.length; r += 1)
        H(a[r]);
      t = !1;
    },
    d(f) {
      f && L(n), mt(a, f);
    }
  };
}
function Ds(e) {
  let n, t, i;
  return t = new pn({
    props: {
      tensor: (
        /*tensor*/
        e[0].get(0)
      ),
      dimensions: (
        /*dimensions*/
        e[1].slice(1)
      ),
      spec: (
        /*spec*/
        e[2]
      )
    }
  }), {
    c() {
      n = D("figure"), ue(t.$$.fragment), b(n, "class", "svelte-clglx1");
    },
    m(a, l) {
      C(a, n, l), re(t, n, null), i = !0;
    },
    p(a, l) {
      const f = {};
      l & /*tensor*/
      1 && (f.tensor = /*tensor*/
      a[0].get(0)), l & /*dimensions*/
      2 && (f.dimensions = /*dimensions*/
      a[1].slice(1)), l & /*spec*/
      4 && (f.spec = /*spec*/
      a[2]), t.$set(f);
    },
    i(a) {
      i || (Z(t.$$.fragment, a), i = !0);
    },
    o(a) {
      H(t.$$.fragment, a), i = !1;
    },
    d(a) {
      a && L(n), oe(t);
    }
  };
}
function Is(e) {
  let n, t, i;
  return t = new pn({
    props: {
      tensor: (
        /*tensor*/
        e[0].get(
          /*dimensions*/
          e[1][0].slice
        )
      ),
      dimensions: (
        /*dimensions*/
        e[1].slice(1)
      ),
      spec: (
        /*spec*/
        e[2]
      )
    }
  }), {
    c() {
      n = D("figure"), ue(t.$$.fragment), b(n, "class", "svelte-clglx1");
    },
    m(a, l) {
      C(a, n, l), re(t, n, null), i = !0;
    },
    p(a, l) {
      const f = {};
      l & /*tensor, dimensions*/
      3 && (f.tensor = /*tensor*/
      a[0].get(
        /*dimensions*/
        a[1][0].slice
      )), l & /*dimensions*/
      2 && (f.dimensions = /*dimensions*/
      a[1].slice(1)), l & /*spec*/
      4 && (f.spec = /*spec*/
      a[2]), t.$set(f);
    },
    i(a) {
      i || (Z(t.$$.fragment, a), i = !0);
    },
    o(a) {
      H(t.$$.fragment, a), i = !1;
    },
    d(a) {
      a && L(n), oe(t);
    }
  };
}
function Ls(e) {
  let n, t;
  return n = new Ns({
    props: {
      matrix: (
        /*tensor*/
        e[0]
      ),
      spec: (
        /*spec*/
        e[2]
      )
    }
  }), {
    c() {
      ue(n.$$.fragment);
    },
    m(i, a) {
      re(n, i, a), t = !0;
    },
    p(i, a) {
      const l = {};
      a & /*tensor*/
      1 && (l.matrix = /*tensor*/
      i[0]), a & /*spec*/
      4 && (l.spec = /*spec*/
      i[2]), n.$set(l);
    },
    i(i) {
      t || (Z(n.$$.fragment, i), t = !0);
    },
    o(i) {
      H(n.$$.fragment, i), t = !1;
    },
    d(i) {
      oe(n, i);
    }
  };
}
function Xa(e) {
  let n, t, i = (
    /*dimensions*/
    e[1][0].name + ""
  ), a, l, f, r, s, o, c, h;
  return o = new pn({
    props: {
      tensor: (
        /*tensor*/
        e[0].get(
          /*index*/
          e[5]
        )
      ),
      dimensions: (
        /*dimensions*/
        e[1].slice(1)
      ),
      spec: (
        /*spec*/
        e[2]
      )
    }
  }), {
    c() {
      n = D("li"), t = D("h4"), a = j(i), l = j(": "), f = j(
        /*index*/
        e[5]
      ), r = K(), s = D("figure"), ue(o.$$.fragment), c = K(), b(t, "class", "svelte-clglx1"), b(s, "class", "svelte-clglx1"), b(n, "class", "svelte-clglx1");
    },
    m(d, u) {
      C(d, n, u), S(n, t), S(t, a), S(t, l), S(t, f), S(n, r), S(n, s), re(o, s, null), S(n, c), h = !0;
    },
    p(d, u) {
      (!h || u & /*dimensions*/
      2) && i !== (i = /*dimensions*/
      d[1][0].name + "") && W(a, i);
      const _ = {};
      u & /*tensor*/
      1 && (_.tensor = /*tensor*/
      d[0].get(
        /*index*/
        d[5]
      )), u & /*dimensions*/
      2 && (_.dimensions = /*dimensions*/
      d[1].slice(1)), u & /*spec*/
      4 && (_.spec = /*spec*/
      d[2]), o.$set(_);
    },
    i(d) {
      h || (Z(o.$$.fragment, d), h = !0);
    },
    o(d) {
      H(o.$$.fragment, d), h = !1;
    },
    d(d) {
      d && L(n), oe(o);
    }
  };
}
function Cs(e) {
  let n, t, i, a;
  const l = [Ls, Is, Ds, Ts], f = [];
  function r(s, o) {
    return (
      /*dimensions*/
      s[1].length == 0 ? 0 : (
        /*dimensions*/
        s[1][0].type == "slice" ? 1 : (
          /*dimensions*/
          s[1][0].type == "max" || /*dimensions*/
          s[1][0].type == "min" || /*dimensions*/
          s[1][0].type == "mean" ? 2 : (
            /*dimensions*/
            s[1][0].type == "small-multiples" ? 3 : -1
          )
        )
      )
    );
  }
  return ~(n = r(e)) && (t = f[n] = l[n](e)), {
    c() {
      t && t.c(), i = Ze();
    },
    m(s, o) {
      ~n && f[n].m(s, o), C(s, i, o), a = !0;
    },
    p(s, [o]) {
      let c = n;
      n = r(s), n === c ? ~n && f[n].p(s, o) : (t && (be(), H(f[c], 1, 1, () => {
        f[c] = null;
      }), ge()), ~n ? (t = f[n], t ? t.p(s, o) : (t = f[n] = l[n](s), t.c()), Z(t, 1), t.m(i.parentNode, i)) : t = null);
    },
    i(s) {
      a || (Z(t), a = !0);
    },
    o(s) {
      H(t), a = !1;
    },
    d(s) {
      s && L(i), ~n && f[n].d(s);
    }
  };
}
const Ka = (e) => e.type == "small-multiples";
function Zs(e, n, t) {
  let { tensor: i } = n, { dimensions: a } = n, { spec: l } = n;
  return e.$$set = (f) => {
    "tensor" in f && t(0, i = f.tensor), "dimensions" in f && t(1, a = f.dimensions), "spec" in f && t(2, l = f.spec);
  }, [i, a, l];
}
class pn extends Ve {
  constructor(n) {
    super(), Ge(this, n, Zs, Cs, Ye, { tensor: 0, dimensions: 1, spec: 2 }, Rs);
  }
}
function Os(e, n, t) {
  const i = e.slice();
  return i[18] = n[t], i;
}
function Ya(e, n, t) {
  const i = e.slice();
  return i[21] = n[t], i[22] = n, i[23] = t, i;
}
function Ga(e) {
  let n, t, i, a, l = (
    /*dimension*/
    e[21].slice + ""
  ), f, r, s, o, c, h;
  function d() {
    e[13].call(
      n,
      /*each_value_1*/
      e[22],
      /*index*/
      e[23]
    );
  }
  let u = (
    /*dimension*/
    e[21].labels && Va(e)
  );
  return {
    c() {
      n = D("input"), i = K(), a = D("span"), f = j(l), r = K(), u && u.c(), s = Ze(), b(n, "type", "range"), b(n, "min", 0), b(n, "max", t = /*tensor*/
      e[1].shape[
        /*index*/
        e[23]
      ] - 1), M(n, "width", "20em"), M(a, "display", "inline-block"), M(a, "width", "40px");
    },
    m(_, v) {
      C(_, n, v), de(
        n,
        /*dimension*/
        e[21].slice
      ), C(_, i, v), C(_, a, v), S(a, f), C(_, r, v), u && u.m(_, v), C(_, s, v), o = !0, c || (h = [
        ye(n, "change", d),
        ye(n, "input", d)
      ], c = !0);
    },
    p(_, v) {
      e = _, (!o || v & /*tensor*/
      2 && t !== (t = /*tensor*/
      e[1].shape[
        /*index*/
        e[23]
      ] - 1)) && b(n, "max", t), v & /*dimensionStates*/
      1 && de(
        n,
        /*dimension*/
        e[21].slice
      ), (!o || v & /*dimensionStates*/
      1) && l !== (l = /*dimension*/
      e[21].slice + "") && W(f, l), /*dimension*/
      e[21].labels ? u ? (u.p(e, v), v & /*dimensionStates*/
      1 && Z(u, 1)) : (u = Va(e), u.c(), Z(u, 1), u.m(s.parentNode, s)) : u && (be(), H(u, 1, 1, () => {
        u = null;
      }), ge());
    },
    i(_) {
      o || (Z(u), o = !0);
    },
    o(_) {
      H(u), o = !1;
    },
    d(_) {
      _ && (L(n), L(i), L(a), L(r), L(s)), u && u.d(_), c = !1, Ke(h);
    }
  };
}
function Va(e) {
  let n, t;
  return n = new mi({
    props: {
      labels: (
        /*dimension*/
        e[21].labels
      ),
      index: (
        /*dimension*/
        e[21].slice
      )
    }
  }), {
    c() {
      ue(n.$$.fragment);
    },
    m(i, a) {
      re(n, i, a), t = !0;
    },
    p(i, a) {
      const l = {};
      a & /*dimensionStates*/
      1 && (l.labels = /*dimension*/
      i[21].labels), a & /*dimensionStates*/
      1 && (l.index = /*dimension*/
      i[21].slice), n.$set(l);
    },
    i(i) {
      t || (Z(n.$$.fragment, i), t = !0);
    },
    o(i) {
      H(n.$$.fragment, i), t = !1;
    },
    d(i) {
      oe(n, i);
    }
  };
}
function qa(e) {
  let n, t, i, a = (
    /*dimension*/
    e[21].name + ""
  ), l, f, r, s, o, c, h, d, u, _, v, y;
  function A() {
    e[12].call(
      r,
      /*each_value_1*/
      e[22],
      /*index*/
      e[23]
    );
  }
  let x = (
    /*dimension*/
    e[21].type == "slice" && Ga(e)
  );
  return {
    c() {
      n = D("div"), t = D("label"), i = D("span"), l = j(a), f = K(), r = D("select"), s = D("option"), s.textContent = "Slice", o = D("option"), o.textContent = "Small Multiples", c = D("option"), c.textContent = "Mean", h = D("option"), h.textContent = "Min", d = D("option"), d.textContent = "Max", u = K(), x && x.c(), M(i, "width", "100px"), s.__value = "slice", de(s, s.__value), o.__value = "small-multiples", de(o, o.__value), c.__value = "mean", de(c, c.__value), h.__value = "min", de(h, h.__value), d.__value = "max", de(d, d.__value), /*dimension*/
      e[21].type === void 0 && ct(A), M(t, "display", "flex"), M(t, "flex-direction", "row"), M(t, "gap", "0.25em"), M(t, "align-items", "center"), M(n, "margin-bottom", "0.25em");
    },
    m(k, g) {
      C(k, n, g), S(n, t), S(t, i), S(i, l), S(t, f), S(t, r), S(r, s), S(r, o), S(r, c), S(r, h), S(r, d), st(
        r,
        /*dimension*/
        e[21].type,
        !0
      ), S(t, u), x && x.m(t, null), _ = !0, v || (y = ye(r, "change", A), v = !0);
    },
    p(k, g) {
      e = k, (!_ || g & /*dimensionStates*/
      1) && a !== (a = /*dimension*/
      e[21].name + "") && W(l, a), g & /*dimensionStates*/
      1 && st(
        r,
        /*dimension*/
        e[21].type
      ), /*dimension*/
      e[21].type == "slice" ? x ? (x.p(e, g), g & /*dimensionStates*/
      1 && Z(x, 1)) : (x = Ga(e), x.c(), Z(x, 1), x.m(t, null)) : x && (be(), H(x, 1, 1, () => {
        x = null;
      }), ge());
    },
    i(k) {
      _ || (Z(x), _ = !0);
    },
    o(k) {
      H(x), _ = !1;
    },
    d(k) {
      k && L(n), x && x.d(), v = !1, y();
    }
  };
}
function Wa(e) {
  let n, t, i, a, l, f, r, s = me(S0), o = [];
  for (let c = 0; c < s.length; c += 1)
    o[c] = Us(Os(e, s, c));
  return {
    c() {
      n = D("label"), t = D("span"), t.textContent = "Scheme:", i = K(), a = D("select"), l = D("option"), l.textContent = "Auto";
      for (let c = 0; c < o.length; c += 1)
        o[c].c();
      l.__value = null, de(l, l.__value), /*currentScheme*/
      e[5] === void 0 && ct(() => (
        /*select_change_handler_1*/
        e[14].call(a)
      )), M(n, "display", "flex"), M(n, "gap", "0.25em"), M(n, "align-items", "center");
    },
    m(c, h) {
      C(c, n, h), S(n, t), S(n, i), S(n, a), S(a, l);
      for (let d = 0; d < o.length; d += 1)
        o[d] && o[d].m(a, null);
      st(
        a,
        /*currentScheme*/
        e[5],
        !0
      ), f || (r = ye(
        a,
        "change",
        /*select_change_handler_1*/
        e[14]
      ), f = !0);
    },
    p(c, h) {
      h & /*currentScheme*/
      32 && st(
        a,
        /*currentScheme*/
        c[5]
      );
    },
    d(c) {
      c && L(n), mt(o, c), f = !1, r();
    }
  };
}
function Us(e) {
  let n;
  return {
    c() {
      n = D("option"), n.textContent = `${/*name*/
      e[18]}`, n.__value = /*name*/
      e[18].toLowerCase(), de(n, n.__value);
    },
    m(t, i) {
      C(t, n, i);
    },
    p: fe,
    d(t) {
      t && L(n);
    }
  };
}
function Ja(e) {
  let n, t, i, a, l, f, r, s, o;
  return {
    c() {
      n = D("label"), t = D("span"), t.textContent = "Scale:", i = K(), a = D("select"), l = D("option"), l.textContent = "Auto", f = D("option"), f.textContent = "Linear", r = D("option"), r.textContent = "Log", l.__value = null, de(l, l.__value), f.__value = "linear", de(f, f.__value), r.__value = "log", de(r, r.__value), /*currentScaleType*/
      e[6] === void 0 && ct(() => (
        /*select_change_handler_2*/
        e[15].call(a)
      )), M(n, "display", "flex"), M(n, "gap", "0.25em"), M(n, "align-items", "center");
    },
    m(c, h) {
      C(c, n, h), S(n, t), S(n, i), S(n, a), S(a, l), S(a, f), S(a, r), st(
        a,
        /*currentScaleType*/
        e[6],
        !0
      ), s || (o = ye(
        a,
        "change",
        /*select_change_handler_2*/
        e[15]
      ), s = !0);
    },
    p(c, h) {
      h & /*currentScaleType*/
      64 && st(
        a,
        /*currentScaleType*/
        c[6]
      );
    },
    d(c) {
      c && L(n), s = !1, o();
    }
  };
}
function Qa(e) {
  let n, t;
  return n = new Jl({
    props: {
      scale: (
        /*heatmapScale*/
        e[8]
      ),
      padding: { left: 30, right: 30 },
      width: Math.min(300, 200)
    }
  }), {
    c() {
      ue(n.$$.fragment);
    },
    m(i, a) {
      re(n, i, a), t = !0;
    },
    p(i, a) {
      const l = {};
      a & /*heatmapScale*/
      256 && (l.scale = /*heatmapScale*/
      i[8]), n.$set(l);
    },
    i(i) {
      t || (Z(n.$$.fragment, i), t = !0);
    },
    o(i) {
      H(n.$$.fragment, i), t = !1;
    },
    d(i) {
      oe(n, i);
    }
  };
}
function Fs(e) {
  var z, E, m, T, w, I;
  let n, t, i, a, l, f, r, s, o, c, h, d, u, _, v, y, A = me(
    /*dimensionStates*/
    e[0]
  ), x = [];
  for (let N = 0; N < A.length; N += 1)
    x[N] = qa(Ya(e, A, N));
  const k = (N) => H(x[N], 1, 1, () => {
    x[N] = null;
  });
  let g = (
    /*scale*/
    ((z = e[4]) == null ? void 0 : z.scheme) == null && Wa(e)
  ), p = (
    /*scale*/
    ((E = e[4]) == null ? void 0 : E.type) == null && Ja(e)
  );
  d = new pn({
    props: {
      tensor: (
        /*displayTensor*/
        e[10]
      ),
      dimensions: (
        /*dimensionStates*/
        e[0]
      ),
      spec: {
        scale: (
          /*heatmapScale*/
          e[8]
        ),
        .../*hasSmallMultiples*/
        e[9] ? { width: 200, height: 200, legend: null } : {},
        xAxis: (
          /*showAxes*/
          e[7] ? {
            title: (
              /*hasSmallMultiples*/
              e[9] ? null : (
                /*names*/
                ((m = e[2]) == null ? void 0 : m[
                  /*names*/
                  e[2].length - 1
                ]) ?? void 0
              )
            )
          } : null
        ),
        yAxis: (
          /*showAxes*/
          e[7] ? {
            title: (
              /*hasSmallMultiples*/
              e[9] ? null : (
                /*names*/
                ((T = e[2]) == null ? void 0 : T[
                  /*names*/
                  e[2].length - 2
                ]) ?? void 0
              )
            )
          } : null
        ),
        xLabels: (
          /*labels*/
          (w = e[3]) == null ? void 0 : w[
            /*tensor*/
            e[1].shape.length - 1
          ]
        ),
        yLabels: (
          /*labels*/
          (I = e[3]) == null ? void 0 : I[
            /*tensor*/
            e[1].shape.length - 2
          ]
        )
      }
    }
  });
  let R = (
    /*hasSmallMultiples*/
    e[9] && Qa(e)
  );
  return {
    c() {
      n = D("main");
      for (let N = 0; N < x.length; N += 1)
        x[N].c();
      t = K(), i = D("div"), g && g.c(), a = K(), p && p.c(), l = K(), f = D("label"), r = D("span"), r.textContent = "Axes:", s = K(), o = D("input"), c = K(), h = D("div"), ue(d.$$.fragment), u = K(), R && R.c(), b(o, "type", "checkbox"), M(f, "display", "flex"), M(f, "gap", "0.25em"), M(f, "align-items", "center"), M(i, "margin-bottom", "0.25em"), M(i, "display", "flex"), M(i, "flex-direction", "row"), M(i, "gap", "0.25em"), M(i, "align-items", "center"), M(i, "user-select", "none");
    },
    m(N, O) {
      C(N, n, O);
      for (let V = 0; V < x.length; V += 1)
        x[V] && x[V].m(n, null);
      S(n, t), S(n, i), g && g.m(i, null), S(i, a), p && p.m(i, null), S(i, l), S(i, f), S(f, r), S(f, s), S(f, o), o.checked = /*showAxes*/
      e[7], S(n, c), S(n, h), re(d, h, null), S(h, u), R && R.m(h, null), _ = !0, v || (y = ye(
        o,
        "change",
        /*input_change_handler*/
        e[16]
      ), v = !0);
    },
    p(N, [O]) {
      var se, U, Y, J, P, te;
      if (O & /*dimensionStates, tensor*/
      3) {
        A = me(
          /*dimensionStates*/
          N[0]
        );
        let B;
        for (B = 0; B < A.length; B += 1) {
          const Re = Ya(N, A, B);
          x[B] ? (x[B].p(Re, O), Z(x[B], 1)) : (x[B] = qa(Re), x[B].c(), Z(x[B], 1), x[B].m(n, t));
        }
        for (be(), B = A.length; B < x.length; B += 1)
          k(B);
        ge();
      }
      /*scale*/
      ((se = N[4]) == null ? void 0 : se.scheme) == null ? g ? g.p(N, O) : (g = Wa(N), g.c(), g.m(i, a)) : g && (g.d(1), g = null), /*scale*/
      ((U = N[4]) == null ? void 0 : U.type) == null ? p ? p.p(N, O) : (p = Ja(N), p.c(), p.m(i, l)) : p && (p.d(1), p = null), O & /*showAxes*/
      128 && (o.checked = /*showAxes*/
      N[7]);
      const V = {};
      O & /*displayTensor*/
      1024 && (V.tensor = /*displayTensor*/
      N[10]), O & /*dimensionStates*/
      1 && (V.dimensions = /*dimensionStates*/
      N[0]), O & /*heatmapScale, hasSmallMultiples, showAxes, names, labels, tensor*/
      910 && (V.spec = {
        scale: (
          /*heatmapScale*/
          N[8]
        ),
        .../*hasSmallMultiples*/
        N[9] ? { width: 200, height: 200, legend: null } : {},
        xAxis: (
          /*showAxes*/
          N[7] ? {
            title: (
              /*hasSmallMultiples*/
              N[9] ? null : (
                /*names*/
                ((Y = N[2]) == null ? void 0 : Y[
                  /*names*/
                  N[2].length - 1
                ]) ?? void 0
              )
            )
          } : null
        ),
        yAxis: (
          /*showAxes*/
          N[7] ? {
            title: (
              /*hasSmallMultiples*/
              N[9] ? null : (
                /*names*/
                ((J = N[2]) == null ? void 0 : J[
                  /*names*/
                  N[2].length - 2
                ]) ?? void 0
              )
            )
          } : null
        ),
        xLabels: (
          /*labels*/
          (P = N[3]) == null ? void 0 : P[
            /*tensor*/
            N[1].shape.length - 1
          ]
        ),
        yLabels: (
          /*labels*/
          (te = N[3]) == null ? void 0 : te[
            /*tensor*/
            N[1].shape.length - 2
          ]
        )
      }), d.$set(V), /*hasSmallMultiples*/
      N[9] ? R ? (R.p(N, O), O & /*hasSmallMultiples*/
      512 && Z(R, 1)) : (R = Qa(N), R.c(), Z(R, 1), R.m(h, null)) : R && (be(), H(R, 1, 1, () => {
        R = null;
      }), ge());
    },
    i(N) {
      if (!_) {
        for (let O = 0; O < A.length; O += 1)
          Z(x[O]);
        Z(d.$$.fragment, N), Z(R), _ = !0;
      }
    },
    o(N) {
      x = x.filter(Boolean);
      for (let O = 0; O < x.length; O += 1)
        H(x[O]);
      H(d.$$.fragment, N), H(R), _ = !1;
    },
    d(N) {
      N && L(n), mt(x, N), g && g.d(), p && p.d(), oe(d), R && R.d(), v = !1, y();
    }
  };
}
let Hn = /* @__PURE__ */ new WeakMap();
function Hs(e, n) {
  let t = e, i = n.map((a) => a.type).join(",");
  if (Hn.has(e)) {
    let a = Hn.get(e);
    if (a.key == i)
      return a.result;
  }
  for (let a = 0; a < n.length; a++)
    switch (n[a].type) {
      case "max":
        t = t.max(a);
        break;
      case "mean":
        t = t.mean(a);
        break;
      case "min":
        t = t.min(a);
        break;
    }
  return Hn.set(e, { key: i, result: t }), t;
}
function $s(e, n, t) {
  let i, a, l, { tensor: f } = n, { names: r = void 0 } = n, { labels: s = void 0 } = n, { defaultViews: o = void 0 } = n, { scale: c = void 0 } = n, h, d = "linear", u = !0, { dimensionStates: _ = [] } = n;
  if (_ == null || _.length != f.shape.length - 2) {
    _ = new Array(f.shape.length - 2);
    for (let p = 0; p < _.length; p++) {
      let R = (r == null ? void 0 : r[p]) ?? `Dimension ${p}`;
      _[p] = {
        name: R,
        labels: s == null ? void 0 : s[p],
        type: (o == null ? void 0 : o[p]) ?? "slice",
        slice: 0
      };
    }
  }
  Oo(() => {
    (c == null ? void 0 : c.type) != null && t(6, d = c == null ? void 0 : c.type), (c == null ? void 0 : c.scheme) != null && t(5, h = c == null ? void 0 : c.scheme);
  });
  const v = Ol();
  ci(() => {
    v("scale", a);
  });
  function y(p, R) {
    p[R].type = In(this), t(0, _);
  }
  function A(p, R) {
    p[R].slice = Lo(this.value), t(0, _);
  }
  function x() {
    h = In(this), t(5, h);
  }
  function k() {
    d = In(this), t(6, d);
  }
  function g() {
    u = this.checked, t(7, u);
  }
  return e.$$set = (p) => {
    "tensor" in p && t(1, f = p.tensor), "names" in p && t(2, r = p.names), "labels" in p && t(3, s = p.labels), "defaultViews" in p && t(11, o = p.defaultViews), "scale" in p && t(4, c = p.scale), "dimensionStates" in p && t(0, _ = p.dimensionStates);
  }, e.$$.update = () => {
    e.$$.dirty & /*tensor, dimensionStates*/
    3 && t(10, i = Hs(f, _)), e.$$.dirty & /*tensor, scale, currentScheme, currentScaleType*/
    114 && t(8, a = jl(f, {
      ...c,
      scheme: h,
      type: d
    })), e.$$.dirty & /*dimensionStates*/
    1 && t(9, l = _.some((p) => p.type == "small-multiples"));
  }, [
    _,
    f,
    r,
    s,
    c,
    h,
    d,
    u,
    a,
    l,
    i,
    o,
    y,
    A,
    x,
    k,
    g
  ];
}
class Bs extends Ve {
  constructor(n) {
    super(), Ge(this, n, $s, Fs, Ye, {
      tensor: 1,
      names: 2,
      labels: 3,
      defaultViews: 11,
      scale: 4,
      dimensionStates: 0
    });
  }
}
function Ps(e) {
  jt(e, "svelte-z83kmo", "main.svelte-z83kmo{font-family:system-ui, sans-serif}");
}
function js(e) {
  let n;
  return {
    c() {
      n = D("p"), n.textContent = "Loading tensor data...";
    },
    m(t, i) {
      C(t, n, i);
    },
    p: fe,
    i: fe,
    o: fe,
    d(t) {
      t && L(n);
    }
  };
}
function Xs(e) {
  let n, t;
  return n = new Bs({
    props: {
      tensor: (
        /*tensor*/
        e[0]
      ),
      names: (
        /*names*/
        e[1]
      ),
      labels: (
        /*labels*/
        e[2]
      ),
      scale: (
        /*scale*/
        e[3]
      ),
      defaultViews: (
        /*defaultViews*/
        e[4]
      )
    }
  }), n.$on(
    "scale",
    /*handleScale*/
    e[5]
  ), {
    c() {
      ue(n.$$.fragment);
    },
    m(i, a) {
      re(n, i, a), t = !0;
    },
    p(i, a) {
      const l = {};
      a & /*tensor*/
      1 && (l.tensor = /*tensor*/
      i[0]), a & /*names*/
      2 && (l.names = /*names*/
      i[1]), a & /*labels*/
      4 && (l.labels = /*labels*/
      i[2]), a & /*scale*/
      8 && (l.scale = /*scale*/
      i[3]), a & /*defaultViews*/
      16 && (l.defaultViews = /*defaultViews*/
      i[4]), n.$set(l);
    },
    i(i) {
      t || (Z(n.$$.fragment, i), t = !0);
    },
    o(i) {
      H(n.$$.fragment, i), t = !1;
    },
    d(i) {
      oe(n, i);
    }
  };
}
function Ks(e) {
  let n, t, i, a;
  const l = [Xs, js], f = [];
  function r(s, o) {
    return (
      /*tensor*/
      s[0] != null ? 0 : 1
    );
  }
  return t = r(e), i = f[t] = l[t](e), {
    c() {
      n = D("main"), i.c(), b(n, "class", "svelte-z83kmo");
    },
    m(s, o) {
      C(s, n, o), f[t].m(n, null), a = !0;
    },
    p(s, [o]) {
      let c = t;
      t = r(s), t === c ? f[t].p(s, o) : (be(), H(f[c], 1, 1, () => {
        f[c] = null;
      }), ge(), i = f[t], i ? i.p(s, o) : (i = f[t] = l[t](s), i.c()), Z(i, 1), i.m(n, null));
    },
    i(s) {
      a || (Z(i), a = !0);
    },
    o(s) {
      H(i), a = !1;
    },
    d(s) {
      s && L(n), f[t].d();
    }
  };
}
function Ys(e, n, t) {
  let i = Ol(), { tensor: a = void 0 } = n, { names: l = void 0 } = n, { labels: f = void 0 } = n, { scale: r = void 0 } = n, { defaultViews: s = void 0 } = n;
  function o(c) {
    i("scale", c.detail);
  }
  return e.$$set = (c) => {
    "tensor" in c && t(0, a = c.tensor), "names" in c && t(1, l = c.names), "labels" in c && t(2, f = c.labels), "scale" in c && t(3, r = c.scale), "defaultViews" in c && t(4, s = c.defaultViews);
  }, [a, l, f, r, s, o];
}
class Gs extends Ve {
  constructor(n) {
    super(), Ge(
      this,
      n,
      Ys,
      Ks,
      Ye,
      {
        tensor: 0,
        names: 1,
        labels: 2,
        scale: 3,
        defaultViews: 4
      },
      Ps
    );
  }
}
function Qs(e) {
  let n = e.model, t = () => ({
    names: n.get("names"),
    labels: n.get("labels"),
    defaultViews: n.get("default_views"),
    scale: {
      domain: n.get("scale_domain"),
      type: n.get("scale_type"),
      scheme: n.get("scale_scheme")
    }
  }), i = new Gs({
    target: e.el,
    props: t()
  }), a = () => {
    i.$set(t());
  };
  return n.on("change:scale_domain", a), n.on("change:scale_type", a), n.on("change:scale_scheme", a), n.on("change:names", a), n.on("change:labels", a), i.$on("scale", (l) => {
    n.send({ type: "scale", scale: l.detail });
  }), n.on("msg:custom", (l, f) => {
    if (l.type == "prop") {
      let r = l.value;
      switch (l.valueType) {
        case "Tensor":
          r = tt.fromJSON(r);
          break;
      }
      i == null || i.$set({ [l.name]: r });
    }
  }), n.send({ type: "prop", name: "tensor" }), () => {
    i == null || i.$destroy();
  };
}
export {
  Qs as renderTensorVisualizer
};
