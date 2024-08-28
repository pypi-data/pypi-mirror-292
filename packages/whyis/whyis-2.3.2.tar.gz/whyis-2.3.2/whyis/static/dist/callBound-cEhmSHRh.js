function et(n, t, e) {
  return n.fields = t || [], n.fname = e, n;
}
function jp(n) {
  return n == null ? null : n.fname;
}
function zc(n) {
  return n == null ? null : n.fields;
}
function lu(n) {
  return n.length === 1 ? Hc(n[0]) : Wc(n);
}
const Hc = (n) => function(t) {
  return t[n];
}, Wc = (n) => {
  const t = n.length;
  return function(e) {
    for (let r = 0; r < t; ++r)
      e = e[n[r]];
    return e;
  };
};
function st(n) {
  throw Error(n);
}
function su(n) {
  const t = [], e = n.length;
  let r = null, i = 0, o = "", a, u, c;
  n = n + "";
  function f() {
    t.push(o + n.substring(a, u)), o = "", a = u + 1;
  }
  for (a = u = 0; u < e; ++u)
    if (c = n[u], c === "\\")
      o += n.substring(a, u++), a = u;
    else if (c === r)
      f(), r = null, i = -1;
    else {
      if (r)
        continue;
      a === i && c === '"' || a === i && c === "'" ? (a = u + 1, r = c) : c === "." && !i ? u > a ? f() : a = u + 1 : c === "[" ? (u > a && f(), i = a = u + 1) : c === "]" && (i || st("Access path missing open bracket: " + n), i > 0 && f(), i = 0, a = u + 1);
    }
  return i && st("Access path missing closing bracket: " + n), r && st("Access path missing closing quote: " + n), u > a && (u++, f()), t;
}
function hu(n, t, e) {
  const r = su(n);
  return n = r.length === 1 ? r[0] : n, et((e && e.get || lu)(r), [n], t || n);
}
const Bp = hu("id"), gu = et((n) => n, [], "identity"), Kt = et(() => 0, [], "zero"), Gc = et(() => 1, [], "one"), zp = et(() => !0, [], "true"), Hp = et(() => !1, [], "false");
function Xc(n, t, e) {
  const r = [t].concat([].slice.call(e));
  console[n].apply(console, r);
}
const _c = 0, Vc = 1, Zc = 2, Qc = 3, Jc = 4;
function Wp(n, t) {
  let e = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : Xc, r = n || _c;
  return {
    level(i) {
      return arguments.length ? (r = +i, this) : r;
    },
    error() {
      return r >= Vc && e(t || "error", "ERROR", arguments), this;
    },
    warn() {
      return r >= Zc && e(t || "warn", "WARN", arguments), this;
    },
    info() {
      return r >= Qc && e(t || "log", "INFO", arguments), this;
    },
    debug() {
      return r >= Jc && e(t || "log", "DEBUG", arguments), this;
    }
  };
}
var Ue = Array.isArray;
function er(n) {
  return n === Object(n);
}
const qo = (n) => n !== "__proto__";
function Gp() {
  for (var n = arguments.length, t = new Array(n), e = 0; e < n; e++)
    t[e] = arguments[e];
  return t.reduce((r, i) => {
    for (const o in i)
      if (o === "signals")
        r.signals = Kc(r.signals, i.signals);
      else {
        const a = o === "legend" ? {
          layout: 1
        } : o === "style" ? !0 : null;
        pu(r, o, i[o], a);
      }
    return r;
  }, {});
}
function pu(n, t, e, r) {
  if (!qo(t)) return;
  let i, o;
  if (er(e) && !Ue(e)) {
    o = er(n[t]) ? n[t] : n[t] = {};
    for (i in e)
      r && (r === !0 || r[i]) ? pu(o, i, e[i]) : qo(i) && (o[i] = e[i]);
  } else
    n[t] = e;
}
function Kc(n, t) {
  if (n == null) return t;
  const e = {}, r = [];
  function i(o) {
    e[o.name] || (e[o.name] = 1, r.push(o));
  }
  return t.forEach(i), n.forEach(i), r;
}
function pn(n) {
  return n[n.length - 1];
}
function Qi(n) {
  return n == null || n === "" ? null : +n;
}
const du = (n) => (t) => n * Math.exp(t), mu = (n) => (t) => Math.log(n * t), yu = (n) => (t) => Math.sign(t) * Math.log1p(Math.abs(t / n)), bu = (n) => (t) => Math.sign(t) * Math.expm1(Math.abs(t)) * n, rr = (n) => (t) => t < 0 ? -Math.pow(-t, n) : Math.pow(t, n);
function Nr(n, t, e, r) {
  const i = e(n[0]), o = e(pn(n)), a = (o - i) * t;
  return [r(i - a), r(o - a)];
}
function Xp(n, t) {
  return Nr(n, t, Qi, gu);
}
function _p(n, t) {
  var e = Math.sign(n[0]);
  return Nr(n, t, mu(e), du(e));
}
function Vp(n, t, e) {
  return Nr(n, t, rr(e), rr(1 / e));
}
function Zp(n, t, e) {
  return Nr(n, t, yu(e), bu(e));
}
function Pr(n, t, e, r, i) {
  const o = r(n[0]), a = r(pn(n)), u = t != null ? r(t) : (o + a) / 2;
  return [i(u + (o - u) * e), i(u + (a - u) * e)];
}
function Qp(n, t, e) {
  return Pr(n, t, e, Qi, gu);
}
function Jp(n, t, e) {
  const r = Math.sign(n[0]);
  return Pr(n, t, e, mu(r), du(r));
}
function Kp(n, t, e, r) {
  return Pr(n, t, e, rr(r), rr(1 / r));
}
function nd(n, t, e, r) {
  return Pr(n, t, e, yu(r), bu(r));
}
function td(n) {
  return 1 + ~~(new Date(n).getMonth() / 3);
}
function ed(n) {
  return 1 + ~~(new Date(n).getUTCMonth() / 3);
}
function It(n) {
  return n != null ? Ue(n) ? n : [n] : [];
}
function rd(n, t, e) {
  let r = n[0], i = n[1], o;
  return i < r && (o = i, i = r, r = o), o = i - r, o >= e - t ? [t, e] : [r = Math.min(Math.max(r, t), e - o), r + o];
}
function Ji(n) {
  return typeof n == "function";
}
const nl = "descending";
function id(n, t, e) {
  e = e || {}, t = It(t) || [];
  const r = [], i = [], o = {}, a = e.comparator || tl;
  return It(n).forEach((u, c) => {
    u != null && (r.push(t[c] === nl ? -1 : 1), i.push(u = Ji(u) ? u : hu(u, null, e)), (zc(u) || []).forEach((f) => o[f] = 1));
  }), i.length === 0 ? null : et(a(i, r), Object.keys(o));
}
const vu = (n, t) => (n < t || n == null) && t != null ? -1 : (n > t || t == null) && n != null ? 1 : (t = t instanceof Date ? +t : t, (n = n instanceof Date ? +n : n) !== n && t === t ? -1 : t !== t && n === n ? 1 : 0), tl = (n, t) => n.length === 1 ? el(n[0], t[0]) : rl(n, t, n.length), el = (n, t) => function(e, r) {
  return vu(n(e), n(r)) * t;
}, rl = (n, t, e) => (t.push(0), function(r, i) {
  let o, a = 0, u = -1;
  for (; a === 0 && ++u < e; )
    o = n[u], a = vu(o(r), o(i));
  return a * t[u];
});
function Mu(n) {
  return Ji(n) ? n : () => n;
}
function od(n, t) {
  let e;
  return (r) => {
    e && clearTimeout(e), e = setTimeout(() => (t(r), e = null), n);
  };
}
function wu(n) {
  for (let t, e, r = 1, i = arguments.length; r < i; ++r) {
    t = arguments[r];
    for (e in t)
      n[e] = t[e];
  }
  return n;
}
function ad(n, t) {
  let e = 0, r, i, o, a;
  if (n && (r = n.length))
    if (t == null) {
      for (i = n[e]; e < r && (i == null || i !== i); i = n[++e]) ;
      for (o = a = i; e < r; ++e)
        i = n[e], i != null && (i < o && (o = i), i > a && (a = i));
    } else {
      for (i = t(n[e]); e < r && (i == null || i !== i); i = t(n[++e])) ;
      for (o = a = i; e < r; ++e)
        i = t(n[e]), i != null && (i < o && (o = i), i > a && (a = i));
    }
  return [o, a];
}
function ud(n, t) {
  const e = n.length;
  let r = -1, i, o, a, u, c;
  if (t == null) {
    for (; ++r < e; )
      if (o = n[r], o != null && o >= o) {
        i = a = o;
        break;
      }
    if (r === e) return [-1, -1];
    for (u = c = r; ++r < e; )
      o = n[r], o != null && (i > o && (i = o, u = r), a < o && (a = o, c = r));
  } else {
    for (; ++r < e; )
      if (o = t(n[r], r, n), o != null && o >= o) {
        i = a = o;
        break;
      }
    if (r === e) return [-1, -1];
    for (u = c = r; ++r < e; )
      o = t(n[r], r, n), o != null && (i > o && (i = o, u = r), a < o && (a = o, c = r));
  }
  return [u, c];
}
const il = Object.prototype.hasOwnProperty;
function ft(n, t) {
  return il.call(n, t);
}
const ze = {};
function fd(n) {
  let t = {}, e;
  function r(o) {
    return ft(t, o) && t[o] !== ze;
  }
  const i = {
    size: 0,
    empty: 0,
    object: t,
    has: r,
    get(o) {
      return r(o) ? t[o] : void 0;
    },
    set(o, a) {
      return r(o) || (++i.size, t[o] === ze && --i.empty), t[o] = a, this;
    },
    delete(o) {
      return r(o) && (--i.size, ++i.empty, t[o] = ze), this;
    },
    clear() {
      i.size = i.empty = 0, i.object = t = {};
    },
    test(o) {
      return arguments.length ? (e = o, i) : e;
    },
    clean() {
      const o = {};
      let a = 0;
      for (const u in t) {
        const c = t[u];
        c !== ze && (!e || !e(c)) && (o[u] = c, ++a);
      }
      i.size = a, i.empty = 0, i.object = t = o;
    }
  };
  return n && Object.keys(n).forEach((o) => {
    i.set(o, n[o]);
  }), i;
}
function cd(n, t, e, r, i, o) {
  if (!e && e !== 0) return o;
  const a = +e;
  let u = n[0], c = pn(n), f;
  c < u && (f = u, u = c, c = f), f = Math.abs(t - u);
  const l = Math.abs(c - t);
  return f < l && f <= a ? r : l <= a ? i : o;
}
function ld(n, t, e) {
  const r = n.prototype = Object.create(t.prototype);
  return Object.defineProperty(r, "constructor", {
    value: n,
    writable: !0,
    enumerable: !0,
    configurable: !0
  }), wu(r, e);
}
function sd(n, t, e, r) {
  let i = t[0], o = t[t.length - 1], a;
  return i > o && (a = i, i = o, o = a), e = e === void 0 || e, r = r === void 0 || r, (e ? i <= n : i < n) && (r ? n <= o : n < o);
}
function hd(n) {
  return typeof n == "boolean";
}
function ol(n) {
  return Object.prototype.toString.call(n) === "[object Date]";
}
function gd(n) {
  return n && Ji(n[Symbol.iterator]);
}
function Su(n) {
  return typeof n == "number";
}
function pd(n) {
  return Object.prototype.toString.call(n) === "[object RegExp]";
}
function Ki(n) {
  return typeof n == "string";
}
function dd(n, t, e) {
  n && (n = t ? It(n).map((u) => u.replace(/\\(.)/g, "$1")) : It(n));
  const r = n && n.length, i = e && e.get || lu, o = (u) => i(t ? [u] : su(u));
  let a;
  if (!r)
    a = function() {
      return "";
    };
  else if (r === 1) {
    const u = o(n[0]);
    a = function(c) {
      return "" + u(c);
    };
  } else {
    const u = n.map(o);
    a = function(c) {
      let f = "" + u[0](c), l = 0;
      for (; ++l < r; ) f += "|" + u[l](c);
      return f;
    };
  }
  return et(a, n, "key");
}
function md(n, t) {
  const e = n[0], r = pn(n), i = +t;
  return i ? i === 1 ? r : e + i * (r - e) : e;
}
const al = 1e4;
function yd(n) {
  n = +n || al;
  let t, e, r;
  const i = () => {
    t = {}, e = {}, r = 0;
  }, o = (a, u) => (++r > n && (e = t, t = {}, r = 1), t[a] = u);
  return i(), {
    clear: i,
    has: (a) => ft(t, a) || ft(e, a),
    get: (a) => ft(t, a) ? t[a] : ft(e, a) ? o(a, e[a]) : void 0,
    set: (a, u) => ft(t, a) ? t[a] = u : o(a, u)
  };
}
function bd(n, t, e, r) {
  const i = t.length, o = e.length;
  if (!o) return t;
  if (!i) return e;
  const a = r || new t.constructor(i + o);
  let u = 0, c = 0, f = 0;
  for (; u < i && c < o; ++f)
    a[f] = n(t[u], e[c]) > 0 ? e[c++] : t[u++];
  for (; u < i; ++u, ++f)
    a[f] = t[u];
  for (; c < o; ++c, ++f)
    a[f] = e[c];
  return a;
}
function He(n, t) {
  let e = "";
  for (; --t >= 0; ) e += n;
  return e;
}
function vd(n, t, e, r) {
  const i = e || " ", o = n + "", a = t - o.length;
  return a <= 0 ? o : r === "left" ? He(i, a) + o : r === "center" ? He(i, ~~(a / 2)) + o + He(i, Math.ceil(a / 2)) : o + He(i, a);
}
function xu(n) {
  return n && pn(n) - n[0] || 0;
}
function ul(n) {
  return Ue(n) ? "[" + n.map(ul) + "]" : er(n) || Ki(n) ? (
    // Output valid JSON and JS source strings.
    // See http://timelessrepo.com/json-isnt-a-javascript-subset
    JSON.stringify(n).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
  ) : n;
}
function Md(n) {
  return n == null || n === "" ? null : !n || n === "false" || n === "0" ? !1 : !!n;
}
const fl = (n) => Su(n) || ol(n) ? n : Date.parse(n);
function wd(n, t) {
  return t = t || fl, n == null || n === "" ? null : t(n);
}
function Sd(n) {
  return n == null || n === "" ? null : n + "";
}
function $u(n) {
  const t = {}, e = n.length;
  for (let r = 0; r < e; ++r) t[n[r]] = !0;
  return t;
}
function xd(n, t, e, r) {
  const i = r ?? "…", o = n + "", a = o.length, u = Math.max(0, t - i.length);
  return a <= t ? o : e === "left" ? i + o.slice(a - u) : e === "center" ? o.slice(0, Math.ceil(u / 2)) + i + o.slice(a - ~~(u / 2)) : o.slice(0, u) + i;
}
function $d(n, t, e) {
  if (n)
    if (t) {
      const r = n.length;
      for (let i = 0; i < r; ++i) {
        const o = t(n[i]);
        o && e(o, i, n);
      }
    } else
      n.forEach(e);
}
function cl(n) {
  return n;
}
function ll(n) {
  if (n == null) return cl;
  var t, e, r = n.scale[0], i = n.scale[1], o = n.translate[0], a = n.translate[1];
  return function(u, c) {
    c || (t = e = 0);
    var f = 2, l = u.length, s = new Array(l);
    for (s[0] = (t += u[0]) * r + o, s[1] = (e += u[1]) * i + a; f < l; ) s[f] = u[f], ++f;
    return s;
  };
}
function sl(n, t) {
  for (var e, r = n.length, i = r - t; i < --r; ) e = n[i], n[i++] = n[r], n[r] = e;
}
function Ed(n, t) {
  return typeof t == "string" && (t = n.objects[t]), t.type === "GeometryCollection" ? { type: "FeatureCollection", features: t.geometries.map(function(e) {
    return Yo(n, e);
  }) } : Yo(n, t);
}
function Yo(n, t) {
  var e = t.id, r = t.bbox, i = t.properties == null ? {} : t.properties, o = Eu(n, t);
  return e == null && r == null ? { type: "Feature", properties: i, geometry: o } : r == null ? { type: "Feature", id: e, properties: i, geometry: o } : { type: "Feature", id: e, bbox: r, properties: i, geometry: o };
}
function Eu(n, t) {
  var e = ll(n.transform), r = n.arcs;
  function i(l, s) {
    s.length && s.pop();
    for (var h = r[l < 0 ? ~l : l], g = 0, p = h.length; g < p; ++g)
      s.push(e(h[g], g));
    l < 0 && sl(s, p);
  }
  function o(l) {
    return e(l);
  }
  function a(l) {
    for (var s = [], h = 0, g = l.length; h < g; ++h) i(l[h], s);
    return s.length < 2 && s.push(s[0]), s;
  }
  function u(l) {
    for (var s = a(l); s.length < 4; ) s.push(s[0]);
    return s;
  }
  function c(l) {
    return l.map(u);
  }
  function f(l) {
    var s = l.type, h;
    switch (s) {
      case "GeometryCollection":
        return { type: s, geometries: l.geometries.map(f) };
      case "Point":
        h = o(l.coordinates);
        break;
      case "MultiPoint":
        h = l.coordinates.map(o);
        break;
      case "LineString":
        h = a(l.arcs);
        break;
      case "MultiLineString":
        h = l.arcs.map(a);
        break;
      case "Polygon":
        h = c(l.arcs);
        break;
      case "MultiPolygon":
        h = l.arcs.map(c);
        break;
      default:
        return null;
    }
    return { type: s, coordinates: h };
  }
  return f(t);
}
function hl(n, t) {
  var e = {}, r = {}, i = {}, o = [], a = -1;
  t.forEach(function(f, l) {
    var s = n.arcs[f < 0 ? ~f : f], h;
    s.length < 3 && !s[1][0] && !s[1][1] && (h = t[++a], t[a] = f, t[l] = h);
  }), t.forEach(function(f) {
    var l = u(f), s = l[0], h = l[1], g, p;
    if (g = i[s])
      if (delete i[g.end], g.push(f), g.end = h, p = r[h]) {
        delete r[p.start];
        var d = p === g ? g : g.concat(p);
        r[d.start = g.start] = i[d.end = p.end] = d;
      } else
        r[g.start] = i[g.end] = g;
    else if (g = r[h])
      if (delete r[g.start], g.unshift(f), g.start = s, p = i[s]) {
        delete i[p.end];
        var m = p === g ? g : p.concat(g);
        r[m.start = p.start] = i[m.end = g.end] = m;
      } else
        r[g.start] = i[g.end] = g;
    else
      g = [f], r[g.start = s] = i[g.end = h] = g;
  });
  function u(f) {
    var l = n.arcs[f < 0 ? ~f : f], s = l[0], h;
    return n.transform ? (h = [0, 0], l.forEach(function(g) {
      h[0] += g[0], h[1] += g[1];
    })) : h = l[l.length - 1], f < 0 ? [h, s] : [s, h];
  }
  function c(f, l) {
    for (var s in f) {
      var h = f[s];
      delete l[h.start], delete h.start, delete h.end, h.forEach(function(g) {
        e[g < 0 ? ~g : g] = 1;
      }), o.push(h);
    }
  }
  return c(i, r), c(r, i), t.forEach(function(f) {
    e[f < 0 ? ~f : f] || o.push([f]);
  }), o;
}
function Ad(n) {
  return Eu(n, gl.apply(this, arguments));
}
function gl(n, t, e) {
  var r, i, o;
  if (arguments.length > 1) r = pl(n, t, e);
  else for (i = 0, r = new Array(o = n.arcs.length); i < o; ++i) r[i] = i;
  return { type: "MultiLineString", arcs: hl(n, r) };
}
function pl(n, t, e) {
  var r = [], i = [], o;
  function a(s) {
    var h = s < 0 ? ~s : s;
    (i[h] || (i[h] = [])).push({ i: s, g: o });
  }
  function u(s) {
    s.forEach(a);
  }
  function c(s) {
    s.forEach(u);
  }
  function f(s) {
    s.forEach(c);
  }
  function l(s) {
    switch (o = s, s.type) {
      case "GeometryCollection":
        s.geometries.forEach(l);
        break;
      case "LineString":
        u(s.arcs);
        break;
      case "MultiLineString":
      case "Polygon":
        c(s.arcs);
        break;
      case "MultiPolygon":
        f(s.arcs);
        break;
    }
  }
  return l(t), i.forEach(e == null ? function(s) {
    r.push(s[0].i);
  } : function(s) {
    e(s[0].g, s[s.length - 1].g) && r.push(s[0].i);
  }), r;
}
function Wn(n, t) {
  return n == null || t == null ? NaN : n < t ? -1 : n > t ? 1 : n >= t ? 0 : NaN;
}
function dl(n, t) {
  return n == null || t == null ? NaN : t < n ? -1 : t > n ? 1 : t >= n ? 0 : NaN;
}
function Cr(n) {
  let t, e, r;
  n.length !== 2 ? (t = Wn, e = (u, c) => Wn(n(u), c), r = (u, c) => n(u) - c) : (t = n === Wn || n === dl ? n : ml, e = n, r = n);
  function i(u, c, f = 0, l = u.length) {
    if (f < l) {
      if (t(c, c) !== 0) return l;
      do {
        const s = f + l >>> 1;
        e(u[s], c) < 0 ? f = s + 1 : l = s;
      } while (f < l);
    }
    return f;
  }
  function o(u, c, f = 0, l = u.length) {
    if (f < l) {
      if (t(c, c) !== 0) return l;
      do {
        const s = f + l >>> 1;
        e(u[s], c) <= 0 ? f = s + 1 : l = s;
      } while (f < l);
    }
    return f;
  }
  function a(u, c, f = 0, l = u.length) {
    const s = i(u, c, f, l - 1);
    return s > f && r(u[s - 1], c) > -r(u[s], c) ? s - 1 : s;
  }
  return { left: i, center: a, right: o };
}
function ml() {
  return 0;
}
function Au(n) {
  return n === null ? NaN : +n;
}
function* yl(n, t) {
  if (t === void 0)
    for (let e of n)
      e != null && (e = +e) >= e && (yield e);
  else {
    let e = -1;
    for (let r of n)
      (r = t(r, ++e, n)) != null && (r = +r) >= r && (yield r);
  }
}
const Tu = Cr(Wn), mt = Tu.right, Td = Tu.left;
Cr(Au).center;
function bl(n, t) {
  let e = 0, r, i = 0, o = 0;
  if (t === void 0)
    for (let a of n)
      a != null && (a = +a) >= a && (r = a - i, i += r / ++e, o += r * (a - i));
  else {
    let a = -1;
    for (let u of n)
      (u = t(u, ++a, n)) != null && (u = +u) >= u && (r = u - i, i += r / ++e, o += r * (u - i));
  }
  if (e > 1) return o / (e - 1);
}
function vl(n, t) {
  const e = bl(n, t);
  return e && Math.sqrt(e);
}
class yt {
  constructor() {
    this._partials = new Float64Array(32), this._n = 0;
  }
  add(t) {
    const e = this._partials;
    let r = 0;
    for (let i = 0; i < this._n && i < 32; i++) {
      const o = e[i], a = t + o, u = Math.abs(t) < Math.abs(o) ? t - (a - o) : o - (a - t);
      u && (e[r++] = u), t = a;
    }
    return e[r] = t, this._n = r + 1, this;
  }
  valueOf() {
    const t = this._partials;
    let e = this._n, r, i, o, a = 0;
    if (e > 0) {
      for (a = t[--e]; e > 0 && (r = a, i = t[--e], a = r + i, o = i - (a - r), !o); )
        ;
      e > 0 && (o < 0 && t[e - 1] < 0 || o > 0 && t[e - 1] > 0) && (i = o * 2, r = a + i, i == r - a && (a = r));
    }
    return a;
  }
}
class Lo extends Map {
  constructor(t, e = Cu) {
    if (super(), Object.defineProperties(this, { _intern: { value: /* @__PURE__ */ new Map() }, _key: { value: e } }), t != null) for (const [r, i] of t) this.set(r, i);
  }
  get(t) {
    return super.get(di(this, t));
  }
  has(t) {
    return super.has(di(this, t));
  }
  set(t, e) {
    return super.set(Nu(this, t), e);
  }
  delete(t) {
    return super.delete(Pu(this, t));
  }
}
class Nd extends Set {
  constructor(t, e = Cu) {
    if (super(), Object.defineProperties(this, { _intern: { value: /* @__PURE__ */ new Map() }, _key: { value: e } }), t != null) for (const r of t) this.add(r);
  }
  has(t) {
    return super.has(di(this, t));
  }
  add(t) {
    return super.add(Nu(this, t));
  }
  delete(t) {
    return super.delete(Pu(this, t));
  }
}
function di({ _intern: n, _key: t }, e) {
  const r = t(e);
  return n.has(r) ? n.get(r) : e;
}
function Nu({ _intern: n, _key: t }, e) {
  const r = t(e);
  return n.has(r) ? n.get(r) : (n.set(r, e), e);
}
function Pu({ _intern: n, _key: t }, e) {
  const r = t(e);
  return n.has(r) && (e = n.get(r), n.delete(r)), e;
}
function Cu(n) {
  return n !== null && typeof n == "object" ? n.valueOf() : n;
}
function Ml(n = Wn) {
  if (n === Wn) return Du;
  if (typeof n != "function") throw new TypeError("compare is not a function");
  return (t, e) => {
    const r = n(t, e);
    return r || r === 0 ? r : (n(e, e) === 0) - (n(t, t) === 0);
  };
}
function Du(n, t) {
  return (n == null || !(n >= n)) - (t == null || !(t >= t)) || (n < t ? -1 : n > t ? 1 : 0);
}
const wl = Math.sqrt(50), Sl = Math.sqrt(10), xl = Math.sqrt(2);
function ir(n, t, e) {
  const r = (t - n) / Math.max(0, e), i = Math.floor(Math.log10(r)), o = r / Math.pow(10, i), a = o >= wl ? 10 : o >= Sl ? 5 : o >= xl ? 2 : 1;
  let u, c, f;
  return i < 0 ? (f = Math.pow(10, -i) / a, u = Math.round(n * f), c = Math.round(t * f), u / f < n && ++u, c / f > t && --c, f = -f) : (f = Math.pow(10, i) * a, u = Math.round(n / f), c = Math.round(t / f), u * f < n && ++u, c * f > t && --c), c < u && 0.5 <= e && e < 2 ? ir(n, t, e * 2) : [u, c, f];
}
function mi(n, t, e) {
  if (t = +t, n = +n, e = +e, !(e > 0)) return [];
  if (n === t) return [n];
  const r = t < n, [i, o, a] = r ? ir(t, n, e) : ir(n, t, e);
  if (!(o >= i)) return [];
  const u = o - i + 1, c = new Array(u);
  if (r)
    if (a < 0) for (let f = 0; f < u; ++f) c[f] = (o - f) / -a;
    else for (let f = 0; f < u; ++f) c[f] = (o - f) * a;
  else if (a < 0) for (let f = 0; f < u; ++f) c[f] = (i + f) / -a;
  else for (let f = 0; f < u; ++f) c[f] = (i + f) * a;
  return c;
}
function yi(n, t, e) {
  return t = +t, n = +n, e = +e, ir(n, t, e)[2];
}
function we(n, t, e) {
  t = +t, n = +n, e = +e;
  const r = t < n, i = r ? yi(t, n, e) : yi(n, t, e);
  return (r ? -1 : 1) * (i < 0 ? 1 / -i : i);
}
function jo(n, t) {
  let e;
  if (t === void 0)
    for (const r of n)
      r != null && (e < r || e === void 0 && r >= r) && (e = r);
  else {
    let r = -1;
    for (let i of n)
      (i = t(i, ++r, n)) != null && (e < i || e === void 0 && i >= i) && (e = i);
  }
  return e;
}
function Bo(n, t) {
  let e;
  if (t === void 0)
    for (const r of n)
      r != null && (e > r || e === void 0 && r >= r) && (e = r);
  else {
    let r = -1;
    for (let i of n)
      (i = t(i, ++r, n)) != null && (e > i || e === void 0 && i >= i) && (e = i);
  }
  return e;
}
function Uu(n, t, e = 0, r = 1 / 0, i) {
  if (t = Math.floor(t), e = Math.floor(Math.max(0, e)), r = Math.floor(Math.min(n.length - 1, r)), !(e <= t && t <= r)) return n;
  for (i = i === void 0 ? Du : Ml(i); r > e; ) {
    if (r - e > 600) {
      const c = r - e + 1, f = t - e + 1, l = Math.log(c), s = 0.5 * Math.exp(2 * l / 3), h = 0.5 * Math.sqrt(l * s * (c - s) / c) * (f - c / 2 < 0 ? -1 : 1), g = Math.max(e, Math.floor(t - f * s / c + h)), p = Math.min(r, Math.floor(t + (c - f) * s / c + h));
      Uu(n, t, g, p, i);
    }
    const o = n[t];
    let a = e, u = r;
    for (ne(n, e, t), i(n[r], o) > 0 && ne(n, e, r); a < u; ) {
      for (ne(n, a, u), ++a, --u; i(n[a], o) < 0; ) ++a;
      for (; i(n[u], o) > 0; ) --u;
    }
    i(n[e], o) === 0 ? ne(n, e, u) : (++u, ne(n, u, r)), u <= t && (e = u + 1), t <= u && (r = u - 1);
  }
  return n;
}
function ne(n, t, e) {
  const r = n[t];
  n[t] = n[e], n[e] = r;
}
function bi(n, t, e) {
  if (n = Float64Array.from(yl(n, e)), !(!(r = n.length) || isNaN(t = +t))) {
    if (t <= 0 || r < 2) return Bo(n);
    if (t >= 1) return jo(n);
    var r, i = (r - 1) * t, o = Math.floor(i), a = jo(Uu(n, o).subarray(0, o + 1)), u = Bo(n.subarray(o + 1));
    return a + (u - a) * (i - o);
  }
}
function Fu(n, t, e = Au) {
  if (!(!(r = n.length) || isNaN(t = +t))) {
    if (t <= 0 || r < 2) return +e(n[0], 0, n);
    if (t >= 1) return +e(n[r - 1], r - 1, n);
    var r, i = (r - 1) * t, o = Math.floor(i), a = +e(n[o], o, n), u = +e(n[o + 1], o + 1, n);
    return a + (u - a) * (i - o);
  }
}
function $l(n, t) {
  return bi(n, 0.5, t);
}
function* El(n) {
  for (const t of n)
    yield* t;
}
function Ru(n) {
  return Array.from(El(n));
}
function Al(n, t, e) {
  n = +n, t = +t, e = (i = arguments.length) < 2 ? (t = n, n = 0, 1) : i < 3 ? 1 : +e;
  for (var r = -1, i = Math.max(0, Math.ceil((t - n) / e)) | 0, o = new Array(i); ++r < i; )
    o[r] = n + r * e;
  return o;
}
function* Iu(n, t) {
  if (t == null)
    for (let e of n)
      e != null && e !== "" && (e = +e) >= e && (yield e);
  else {
    let e = -1;
    for (let r of n)
      r = t(r, ++e, n), r != null && r !== "" && (r = +r) >= r && (yield r);
  }
}
function Tl(n, t, e) {
  const r = Float64Array.from(Iu(n, e));
  return r.sort(Wn), t.map((i) => Fu(r, i));
}
function Nl(n, t) {
  return Tl(n, [0.25, 0.5, 0.75], t);
}
function Pl(n, t) {
  const e = n.length, r = vl(n, t), i = Nl(n, t), o = (i[2] - i[0]) / 1.34;
  return 1.06 * (Math.min(r, o) || r || Math.abs(i[0]) || 1) * Math.pow(e, -0.2);
}
function Pd(n) {
  const t = n.maxbins || 20, e = n.base || 10, r = Math.log(e), i = n.divide || [5, 2];
  let o = n.extent[0], a = n.extent[1], u, c, f, l, s, h;
  const g = n.span || a - o || Math.abs(o) || 1;
  if (n.step)
    u = n.step;
  else if (n.steps) {
    for (l = g / t, s = 0, h = n.steps.length; s < h && n.steps[s] < l; ++s) ;
    u = n.steps[Math.max(0, s - 1)];
  } else {
    for (c = Math.ceil(Math.log(t) / r), f = n.minstep || 0, u = Math.max(f, Math.pow(e, Math.round(Math.log(g) / r) - c)); Math.ceil(g / u) > t; )
      u *= e;
    for (s = 0, h = i.length; s < h; ++s)
      l = u / i[s], l >= f && g / l <= t && (u = l);
  }
  l = Math.log(u);
  const p = l >= 0 ? 0 : ~~(-l / r) + 1, d = Math.pow(e, -p - 1);
  return (n.nice || n.nice === void 0) && (l = Math.floor(o / u + d) * u, o = o < l ? l - u : l, a = Math.ceil(a / u) * u), {
    start: o,
    stop: a === o ? o + u : a,
    step: u
  };
}
var nt = Math.random;
function Cd(n) {
  nt = n;
}
function Dd(n, t, e, r) {
  if (!n.length) return [void 0, void 0];
  const i = Float64Array.from(Iu(n, r)), o = i.length, a = t;
  let u, c, f, l;
  for (f = 0, l = Array(a); f < a; ++f) {
    for (u = 0, c = 0; c < o; ++c)
      u += i[~~(nt() * o)];
    l[f] = u / o;
  }
  return l.sort(Wn), [bi(l, e / 2), bi(l, 1 - e / 2)];
}
function Ud(n, t, e, r) {
  r = r || ((h) => h);
  const i = n.length, o = new Float64Array(i);
  let a = 0, u = 1, c = r(n[0]), f = c, l = c + t, s;
  for (; u < i; ++u) {
    if (s = r(n[u]), s >= l) {
      for (f = (c + f) / 2; a < u; ++a) o[a] = f;
      l = s + t, c = s;
    }
    f = s;
  }
  for (f = (c + f) / 2; a < u; ++a) o[a] = f;
  return e ? Cl(o, t + t / 4) : o;
}
function Cl(n, t) {
  const e = n.length;
  let r = 0, i = 1, o, a;
  for (; n[r] === n[i]; ) ++i;
  for (; i < e; ) {
    for (o = i + 1; n[i] === n[o]; ) ++o;
    if (n[i] - n[i - 1] < t) {
      for (a = i + (r + o - i - i >> 1); a < i; ) n[a++] = n[i];
      for (; a > i; ) n[a--] = n[r];
    }
    r = i, i = o;
  }
  return n;
}
function Fd(n) {
  return function() {
    return n = (1103515245 * n + 12345) % 2147483647, n / 2147483647;
  };
}
function Rd(n, t) {
  t == null && (t = n, n = 0);
  let e, r, i;
  const o = {
    min(a) {
      return arguments.length ? (e = a || 0, i = r - e, o) : e;
    },
    max(a) {
      return arguments.length ? (r = a || 0, i = r - e, o) : r;
    },
    sample() {
      return e + Math.floor(i * nt());
    },
    pdf(a) {
      return a === Math.floor(a) && a >= e && a < r ? 1 / i : 0;
    },
    cdf(a) {
      const u = Math.floor(a);
      return u < e ? 0 : u >= r ? 1 : (u - e + 1) / i;
    },
    icdf(a) {
      return a >= 0 && a <= 1 ? e - 1 + Math.floor(a * i) : NaN;
    }
  };
  return o.min(n).max(t);
}
const ku = Math.sqrt(2 * Math.PI), Dl = Math.SQRT2;
let te = NaN;
function Ou(n, t) {
  n = n || 0, t = t ?? 1;
  let e = 0, r = 0, i, o;
  if (te === te)
    e = te, te = NaN;
  else {
    do
      e = nt() * 2 - 1, r = nt() * 2 - 1, i = e * e + r * r;
    while (i === 0 || i > 1);
    o = Math.sqrt(-2 * Math.log(i) / i), e *= o, te = r * o;
  }
  return n + e * t;
}
function Ul(n, t, e) {
  e = e ?? 1;
  const r = (n - (t || 0)) / e;
  return Math.exp(-0.5 * r * r) / (e * ku);
}
function qu(n, t, e) {
  t = t || 0, e = e ?? 1;
  const r = (n - t) / e, i = Math.abs(r);
  let o;
  if (i > 37)
    o = 0;
  else {
    const a = Math.exp(-i * i / 2);
    let u;
    i < 7.07106781186547 ? (u = 0.0352624965998911 * i + 0.700383064443688, u = u * i + 6.37396220353165, u = u * i + 33.912866078383, u = u * i + 112.079291497871, u = u * i + 221.213596169931, u = u * i + 220.206867912376, o = a * u, u = 0.0883883476483184 * i + 1.75566716318264, u = u * i + 16.064177579207, u = u * i + 86.7807322029461, u = u * i + 296.564248779674, u = u * i + 637.333633378831, u = u * i + 793.826512519948, u = u * i + 440.413735824752, o = o / u) : (u = i + 0.65, u = i + 4 / u, u = i + 3 / u, u = i + 2 / u, u = i + 1 / u, o = a / u / 2.506628274631);
  }
  return r > 0 ? 1 - o : o;
}
function Yu(n, t, e) {
  return n < 0 || n > 1 ? NaN : (t || 0) + (e ?? 1) * Dl * Fl(2 * n - 1);
}
function Fl(n) {
  let t = -Math.log((1 - n) * (1 + n)), e;
  return t < 6.25 ? (t -= 3.125, e = -364441206401782e-35, e = -16850591381820166e-35 + e * t, e = 128584807152564e-32 + e * t, e = 11157877678025181e-33 + e * t, e = -1333171662854621e-31 + e * t, e = 20972767875968562e-33 + e * t, e = 6637638134358324e-30 + e * t, e = -4054566272975207e-29 + e * t, e = -8151934197605472e-29 + e * t, e = 26335093153082323e-28 + e * t, e = -12975133253453532e-27 + e * t, e = -5415412054294628e-26 + e * t, e = 10512122733215323e-25 + e * t, e = -4112633980346984e-24 + e * t, e = -29070369957882005e-24 + e * t, e = 42347877827932404e-23 + e * t, e = -13654692000834679e-22 + e * t, e = -13882523362786469e-21 + e * t, e = 18673420803405714e-20 + e * t, e = -740702534166267e-18 + e * t, e = -0.006033670871430149 + e * t, e = 0.24015818242558962 + e * t, e = 1.6536545626831027 + e * t) : t < 16 ? (t = Math.sqrt(t) - 3.25, e = 22137376921775787e-25, e = 9075656193888539e-23 + e * t, e = -27517406297064545e-23 + e * t, e = 18239629214389228e-24 + e * t, e = 15027403968909828e-22 + e * t, e = -4013867526981546e-21 + e * t, e = 29234449089955446e-22 + e * t, e = 12475304481671779e-21 + e * t, e = -47318229009055734e-21 + e * t, e = 6828485145957318e-20 + e * t, e = 24031110387097894e-21 + e * t, e = -3550375203628475e-19 + e * t, e = 9532893797373805e-19 + e * t, e = -0.0016882755560235047 + e * t, e = 0.002491442096107851 + e * t, e = -0.003751208507569241 + e * t, e = 0.005370914553590064 + e * t, e = 1.0052589676941592 + e * t, e = 3.0838856104922208 + e * t) : Number.isFinite(t) ? (t = Math.sqrt(t) - 5, e = -27109920616438573e-27, e = -2555641816996525e-25 + e * t, e = 15076572693500548e-25 + e * t, e = -3789465440126737e-24 + e * t, e = 761570120807834e-23 + e * t, e = -1496002662714924e-23 + e * t, e = 2914795345090108e-23 + e * t, e = -6771199775845234e-23 + e * t, e = 22900482228026655e-23 + e * t, e = -99298272942317e-20 + e * t, e = 4526062597223154e-21 + e * t, e = -1968177810553167e-20 + e * t, e = 7599527703001776e-20 + e * t, e = -21503011930044477e-20 + e * t, e = -13871931833623122e-20 + e * t, e = 1.0103004648645344 + e * t, e = 4.849906401408584 + e * t) : e = 1 / 0, e * n;
}
function Rl(n, t) {
  let e, r;
  const i = {
    mean(o) {
      return arguments.length ? (e = o || 0, i) : e;
    },
    stdev(o) {
      return arguments.length ? (r = o ?? 1, i) : r;
    },
    sample: () => Ou(e, r),
    pdf: (o) => Ul(o, e, r),
    cdf: (o) => qu(o, e, r),
    icdf: (o) => Yu(o, e, r)
  };
  return i.mean(n).stdev(t);
}
function Id(n, t) {
  const e = Rl();
  let r = 0;
  const i = {
    data(o) {
      return arguments.length ? (n = o, r = o ? o.length : 0, i.bandwidth(t)) : n;
    },
    bandwidth(o) {
      return arguments.length ? (t = o, !t && n && (t = Pl(n)), i) : t;
    },
    sample() {
      return n[~~(nt() * r)] + t * e.sample();
    },
    pdf(o) {
      let a = 0, u = 0;
      for (; u < r; ++u)
        a += e.pdf((o - n[u]) / t);
      return a / t / r;
    },
    cdf(o) {
      let a = 0, u = 0;
      for (; u < r; ++u)
        a += e.cdf((o - n[u]) / t);
      return a / r;
    },
    icdf() {
      throw Error("KDE icdf not supported.");
    }
  };
  return i.data(n);
}
function Il(n, t) {
  return n = n || 0, t = t ?? 1, Math.exp(n + Ou() * t);
}
function kl(n, t, e) {
  if (n <= 0) return 0;
  t = t || 0, e = e ?? 1;
  const r = (Math.log(n) - t) / e;
  return Math.exp(-0.5 * r * r) / (e * ku * n);
}
function Ol(n, t, e) {
  return qu(Math.log(n), t, e);
}
function ql(n, t, e) {
  return Math.exp(Yu(n, t, e));
}
function kd(n, t) {
  let e, r;
  const i = {
    mean(o) {
      return arguments.length ? (e = o || 0, i) : e;
    },
    stdev(o) {
      return arguments.length ? (r = o ?? 1, i) : r;
    },
    sample: () => Il(e, r),
    pdf: (o) => kl(o, e, r),
    cdf: (o) => Ol(o, e, r),
    icdf: (o) => ql(o, e, r)
  };
  return i.mean(n).stdev(t);
}
function Od(n, t) {
  let e = 0, r;
  function i(a) {
    const u = [];
    let c = 0, f;
    for (f = 0; f < e; ++f)
      c += u[f] = a[f] == null ? 1 : +a[f];
    for (f = 0; f < e; ++f)
      u[f] /= c;
    return u;
  }
  const o = {
    weights(a) {
      return arguments.length ? (r = i(t = a || []), o) : t;
    },
    distributions(a) {
      return arguments.length ? (a ? (e = a.length, n = a) : (e = 0, n = []), o.weights(t)) : n;
    },
    sample() {
      const a = nt();
      let u = n[e - 1], c = r[0], f = 0;
      for (; f < e - 1; c += r[++f])
        if (a < c) {
          u = n[f];
          break;
        }
      return u.sample();
    },
    pdf(a) {
      let u = 0, c = 0;
      for (; c < e; ++c)
        u += r[c] * n[c].pdf(a);
      return u;
    },
    cdf(a) {
      let u = 0, c = 0;
      for (; c < e; ++c)
        u += r[c] * n[c].cdf(a);
      return u;
    },
    icdf() {
      throw Error("Mixture icdf not supported.");
    }
  };
  return o.distributions(n).weights(t);
}
function Yl(n, t) {
  return t == null && (t = n ?? 1, n = 0), n + (t - n) * nt();
}
function Ll(n, t, e) {
  return e == null && (e = t ?? 1, t = 0), n >= t && n <= e ? 1 / (e - t) : 0;
}
function jl(n, t, e) {
  return e == null && (e = t ?? 1, t = 0), n < t ? 0 : n > e ? 1 : (n - t) / (e - t);
}
function Bl(n, t, e) {
  return e == null && (e = t ?? 1, t = 0), n >= 0 && n <= 1 ? t + n * (e - t) : NaN;
}
function qd(n, t) {
  let e, r;
  const i = {
    min(o) {
      return arguments.length ? (e = o || 0, i) : e;
    },
    max(o) {
      return arguments.length ? (r = o ?? 1, i) : r;
    },
    sample: () => Yl(e, r),
    pdf: (o) => Ll(o, e, r),
    cdf: (o) => jl(o, e, r),
    icdf: (o) => Bl(o, e, r)
  };
  return t == null && (t = n ?? 1, n = 0), i.min(n).max(t);
}
function zl(n, t, e) {
  let r = 0, i = 0;
  for (const o of n) {
    const a = e(o);
    t(o) == null || a == null || isNaN(a) || (r += (a - r) / ++i);
  }
  return {
    coef: [r],
    predict: () => r,
    rSquared: 0
  };
}
function Fe(n, t, e, r) {
  const i = r - n * n, o = Math.abs(i) < 1e-24 ? 0 : (e - n * t) / i;
  return [t - o * n, o];
}
function Dr(n, t, e, r) {
  n = n.filter((g) => {
    let p = t(g), d = e(g);
    return p != null && (p = +p) >= p && d != null && (d = +d) >= d;
  }), r && n.sort((g, p) => t(g) - t(p));
  const i = n.length, o = new Float64Array(i), a = new Float64Array(i);
  let u = 0, c = 0, f = 0, l, s, h;
  for (h of n)
    o[u] = l = +t(h), a[u] = s = +e(h), ++u, c += (l - c) / u, f += (s - f) / u;
  for (u = 0; u < i; ++u)
    o[u] -= c, a[u] -= f;
  return [o, a, c, f];
}
function Re(n, t, e, r) {
  let i = -1, o, a;
  for (const u of n)
    o = t(u), a = e(u), o != null && (o = +o) >= o && a != null && (a = +a) >= a && r(o, a, ++i);
}
function Xt(n, t, e, r, i) {
  let o = 0, a = 0;
  return Re(n, t, e, (u, c) => {
    const f = c - i(u), l = c - r;
    o += f * f, a += l * l;
  }), 1 - o / a;
}
function Hl(n, t, e) {
  let r = 0, i = 0, o = 0, a = 0, u = 0;
  Re(n, t, e, (l, s) => {
    ++u, r += (l - r) / u, i += (s - i) / u, o += (l * s - o) / u, a += (l * l - a) / u;
  });
  const c = Fe(r, i, o, a), f = (l) => c[0] + c[1] * l;
  return {
    coef: c,
    predict: f,
    rSquared: Xt(n, t, e, i, f)
  };
}
function Yd(n, t, e) {
  let r = 0, i = 0, o = 0, a = 0, u = 0;
  Re(n, t, e, (l, s) => {
    ++u, l = Math.log(l), r += (l - r) / u, i += (s - i) / u, o += (l * s - o) / u, a += (l * l - a) / u;
  });
  const c = Fe(r, i, o, a), f = (l) => c[0] + c[1] * Math.log(l);
  return {
    coef: c,
    predict: f,
    rSquared: Xt(n, t, e, i, f)
  };
}
function Ld(n, t, e) {
  const [r, i, o, a] = Dr(n, t, e);
  let u = 0, c = 0, f = 0, l = 0, s = 0, h, g, p;
  Re(n, t, e, (S, y) => {
    h = r[s++], g = Math.log(y), p = h * y, u += (y * g - u) / s, c += (p - c) / s, f += (p * g - f) / s, l += (h * p - l) / s;
  });
  const [d, m] = Fe(c / a, u / a, f / a, l / a), v = (S) => Math.exp(d + m * (S - o));
  return {
    coef: [Math.exp(d - m * o), m],
    predict: v,
    rSquared: Xt(n, t, e, a, v)
  };
}
function jd(n, t, e) {
  let r = 0, i = 0, o = 0, a = 0, u = 0, c = 0;
  Re(n, t, e, (s, h) => {
    const g = Math.log(s), p = Math.log(h);
    ++c, r += (g - r) / c, i += (p - i) / c, o += (g * p - o) / c, a += (g * g - a) / c, u += (h - u) / c;
  });
  const f = Fe(r, i, o, a), l = (s) => f[0] * Math.pow(s, f[1]);
  return f[0] = Math.exp(f[0]), {
    coef: f,
    predict: l,
    rSquared: Xt(n, t, e, u, l)
  };
}
function Wl(n, t, e) {
  const [r, i, o, a] = Dr(n, t, e), u = r.length;
  let c = 0, f = 0, l = 0, s = 0, h = 0, g, p, d, m;
  for (g = 0; g < u; )
    p = r[g], d = i[g++], m = p * p, c += (m - c) / g, f += (m * p - f) / g, l += (m * m - l) / g, s += (p * d - s) / g, h += (m * d - h) / g;
  const v = l - c * c, S = c * v - f * f, y = (h * c - s * f) / S, b = (s * v - h * f) / S, x = -y * c, M = (A) => (A = A - o, y * A * A + b * A + x + a);
  return {
    coef: [x - b * o + y * o * o + a, b - 2 * y * o, y],
    predict: M,
    rSquared: Xt(n, t, e, a, M)
  };
}
function Bd(n, t, e, r) {
  if (r === 0) return zl(n, t, e);
  if (r === 1) return Hl(n, t, e);
  if (r === 2) return Wl(n, t, e);
  const [i, o, a, u] = Dr(n, t, e), c = i.length, f = [], l = [], s = r + 1;
  let h, g, p, d, m;
  for (h = 0; h < s; ++h) {
    for (p = 0, d = 0; p < c; ++p)
      d += Math.pow(i[p], h) * o[p];
    for (f.push(d), m = new Float64Array(s), g = 0; g < s; ++g) {
      for (p = 0, d = 0; p < c; ++p)
        d += Math.pow(i[p], h + g);
      m[g] = d;
    }
    l.push(m);
  }
  l.push(f);
  const v = Xl(l), S = (y) => {
    y -= a;
    let b = u + v[0] + v[1] * y + v[2] * y * y;
    for (h = 3; h < s; ++h) b += v[h] * Math.pow(y, h);
    return b;
  };
  return {
    coef: Gl(s, v, -a, u),
    predict: S,
    rSquared: Xt(n, t, e, u, S)
  };
}
function Gl(n, t, e, r) {
  const i = Array(n);
  let o, a, u, c;
  for (o = 0; o < n; ++o) i[o] = 0;
  for (o = n - 1; o >= 0; --o)
    for (u = t[o], c = 1, i[o] += u, a = 1; a <= o; ++a)
      c *= (o + 1 - a) / a, i[o - a] += u * Math.pow(e, a) * c;
  return i[0] += r, i;
}
function Xl(n) {
  const t = n.length - 1, e = [];
  let r, i, o, a, u;
  for (r = 0; r < t; ++r) {
    for (a = r, i = r + 1; i < t; ++i)
      Math.abs(n[r][i]) > Math.abs(n[r][a]) && (a = i);
    for (o = r; o < t + 1; ++o)
      u = n[o][r], n[o][r] = n[o][a], n[o][a] = u;
    for (i = r + 1; i < t; ++i)
      for (o = t; o >= r; o--)
        n[o][i] -= n[o][r] * n[r][i] / n[r][r];
  }
  for (i = t - 1; i >= 0; --i) {
    for (u = 0, o = i + 1; o < t; ++o)
      u += n[o][i] * e[o];
    e[i] = (n[t][i] - u) / n[i][i];
  }
  return e;
}
const zo = 2, Ho = 1e-12;
function zd(n, t, e, r) {
  const [i, o, a, u] = Dr(n, t, e, !0), c = i.length, f = Math.max(2, ~~(r * c)), l = new Float64Array(c), s = new Float64Array(c), h = new Float64Array(c).fill(1);
  for (let g = -1; ++g <= zo; ) {
    const p = [0, f - 1];
    for (let m = 0; m < c; ++m) {
      const v = i[m], S = p[0], y = p[1], b = v - i[S] > i[y] - v ? S : y;
      let x = 0, M = 0, A = 0, P = 0, F = 0;
      const Y = 1 / Math.abs(i[b] - v || 1);
      for (let D = S; D <= y; ++D) {
        const R = i[D], w = o[D], N = _l(Math.abs(v - R) * Y) * h[D], z = R * N;
        x += N, M += z, A += w * N, P += w * z, F += R * z;
      }
      const [E, W] = Fe(M / x, A / x, P / x, F / x);
      l[m] = E + W * v, s[m] = Math.abs(o[m] - l[m]), Vl(i, m + 1, p);
    }
    if (g === zo)
      break;
    const d = $l(s);
    if (Math.abs(d) < Ho) break;
    for (let m = 0, v, S; m < c; ++m)
      v = s[m] / (6 * d), h[m] = v >= 1 ? Ho : (S = 1 - v * v) * S;
  }
  return Zl(i, l, a, u);
}
function _l(n) {
  return (n = 1 - n * n * n) * n * n;
}
function Vl(n, t, e) {
  const r = n[t];
  let i = e[0], o = e[1] + 1;
  if (!(o >= n.length))
    for (; t > i && n[o] - r <= r - n[i]; )
      e[0] = ++i, e[1] = o, ++o;
}
function Zl(n, t, e, r) {
  const i = n.length, o = [];
  let a = 0, u = 0, c = [], f;
  for (; a < i; ++a)
    f = n[a] + e, c[0] === f ? c[1] += (t[a] - c[1]) / ++u : (u = 0, c[1] += r, c = [f, t[a]], o.push(c));
  return c[1] += r, o;
}
const Ql = 0.5 * Math.PI / 180;
function Hd(n, t, e, r) {
  e = e || 25, r = Math.max(e, r || 200);
  const i = (d) => [d, n(d)], o = t[0], a = t[1], u = a - o, c = u / r, f = [i(o)], l = [];
  if (e === r) {
    for (let d = 1; d < r; ++d)
      f.push(i(o + d / e * u));
    return f.push(i(a)), f;
  } else {
    l.push(i(a));
    for (let d = e; --d > 0; )
      l.push(i(o + d / e * u));
  }
  let s = f[0], h = l[l.length - 1];
  const g = 1 / u, p = Jl(s[1], l);
  for (; h; ) {
    const d = i((s[0] + h[0]) / 2);
    d[0] - s[0] >= c && Kl(s, d, h, g, p) > Ql ? l.push(d) : (s = h, f.push(h), l.pop()), h = l[l.length - 1];
  }
  return f;
}
function Jl(n, t) {
  let e = n, r = n;
  const i = t.length;
  for (let o = 0; o < i; ++o) {
    const a = t[o][1];
    a < e && (e = a), a > r && (r = a);
  }
  return 1 / (r - e);
}
function Kl(n, t, e, r, i) {
  const o = Math.atan2(i * (e[1] - n[1]), r * (e[0] - n[0])), a = Math.atan2(i * (t[1] - n[1]), r * (t[0] - n[0]));
  return Math.abs(o - a);
}
function Wd(n, t) {
  if (typeof document < "u" && document.createElement) {
    const e = document.createElement("canvas");
    if (e && e.getContext)
      return e.width = n, e.height = t, e;
  }
  return null;
}
const Gd = () => typeof Image < "u" ? Image : null;
var U = 1e-6, Lu = 1e-12, k = Math.PI, V = k / 2, Wo = k / 4, dn = k * 2, rn = 180 / k, _ = k / 180, B = Math.abs, _t = Math.atan, Xn = Math.atan2, I = Math.cos, Xd = Math.ceil, ju = Math.exp, _d = Math.hypot, or = Math.log, _r = Math.pow, C = Math.sin, yn = Math.sign || function(n) {
  return n > 0 ? 1 : n < 0 ? -1 : 0;
}, ln = Math.sqrt, no = Math.tan;
function Bu(n) {
  return n > 1 ? 0 : n < -1 ? k : Math.acos(n);
}
function Mn(n) {
  return n > 1 ? V : n < -1 ? -V : Math.asin(n);
}
function bn() {
}
function ar(n, t) {
  n && Xo.hasOwnProperty(n.type) && Xo[n.type](n, t);
}
var Go = {
  Feature: function(n, t) {
    ar(n.geometry, t);
  },
  FeatureCollection: function(n, t) {
    for (var e = n.features, r = -1, i = e.length; ++r < i; ) ar(e[r].geometry, t);
  }
}, Xo = {
  Sphere: function(n, t) {
    t.sphere();
  },
  Point: function(n, t) {
    n = n.coordinates, t.point(n[0], n[1], n[2]);
  },
  MultiPoint: function(n, t) {
    for (var e = n.coordinates, r = -1, i = e.length; ++r < i; ) n = e[r], t.point(n[0], n[1], n[2]);
  },
  LineString: function(n, t) {
    vi(n.coordinates, t, 0);
  },
  MultiLineString: function(n, t) {
    for (var e = n.coordinates, r = -1, i = e.length; ++r < i; ) vi(e[r], t, 0);
  },
  Polygon: function(n, t) {
    _o(n.coordinates, t);
  },
  MultiPolygon: function(n, t) {
    for (var e = n.coordinates, r = -1, i = e.length; ++r < i; ) _o(e[r], t);
  },
  GeometryCollection: function(n, t) {
    for (var e = n.geometries, r = -1, i = e.length; ++r < i; ) ar(e[r], t);
  }
};
function vi(n, t, e) {
  var r = -1, i = n.length - e, o;
  for (t.lineStart(); ++r < i; ) o = n[r], t.point(o[0], o[1], o[2]);
  t.lineEnd();
}
function _o(n, t) {
  var e = -1, r = n.length;
  for (t.polygonStart(); ++e < r; ) vi(n[e], t, 1);
  t.polygonEnd();
}
function Pt(n, t) {
  n && Go.hasOwnProperty(n.type) ? Go[n.type](n, t) : ar(n, t);
}
function Mi(n) {
  return [Xn(n[1], n[0]), Mn(n[2])];
}
function kt(n) {
  var t = n[0], e = n[1], r = I(e);
  return [r * I(t), r * C(t), C(e)];
}
function We(n, t) {
  return n[0] * t[0] + n[1] * t[1] + n[2] * t[2];
}
function ur(n, t) {
  return [n[1] * t[2] - n[2] * t[1], n[2] * t[0] - n[0] * t[2], n[0] * t[1] - n[1] * t[0]];
}
function Vr(n, t) {
  n[0] += t[0], n[1] += t[1], n[2] += t[2];
}
function Ge(n, t) {
  return [n[0] * t, n[1] * t, n[2] * t];
}
function wi(n) {
  var t = ln(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]);
  n[0] /= t, n[1] /= t, n[2] /= t;
}
function Si(n, t) {
  function e(r, i) {
    return r = n(r, i), t(r[0], r[1]);
  }
  return n.invert && t.invert && (e.invert = function(r, i) {
    return r = t.invert(r, i), r && n.invert(r[0], r[1]);
  }), e;
}
function xi(n, t) {
  return B(n) > k && (n -= Math.round(n / dn) * dn), [n, t];
}
xi.invert = xi;
function zu(n, t, e) {
  return (n %= dn) ? t || e ? Si(Zo(n), Qo(t, e)) : Zo(n) : t || e ? Qo(t, e) : xi;
}
function Vo(n) {
  return function(t, e) {
    return t += n, B(t) > k && (t -= Math.round(t / dn) * dn), [t, e];
  };
}
function Zo(n) {
  var t = Vo(n);
  return t.invert = Vo(-n), t;
}
function Qo(n, t) {
  var e = I(n), r = C(n), i = I(t), o = C(t);
  function a(u, c) {
    var f = I(c), l = I(u) * f, s = C(u) * f, h = C(c), g = h * e + l * r;
    return [
      Xn(s * i - g * o, l * e - h * r),
      Mn(g * i + s * o)
    ];
  }
  return a.invert = function(u, c) {
    var f = I(c), l = I(u) * f, s = C(u) * f, h = C(c), g = h * i - s * o;
    return [
      Xn(s * i + h * o, l * e + g * r),
      Mn(g * e - l * r)
    ];
  }, a;
}
function ns(n) {
  n = zu(n[0] * _, n[1] * _, n.length > 2 ? n[2] * _ : 0);
  function t(e) {
    return e = n(e[0] * _, e[1] * _), e[0] *= rn, e[1] *= rn, e;
  }
  return t.invert = function(e) {
    return e = n.invert(e[0] * _, e[1] * _), e[0] *= rn, e[1] *= rn, e;
  }, t;
}
function ts(n, t, e, r, i, o) {
  if (e) {
    var a = I(t), u = C(t), c = r * e;
    i == null ? (i = t + r * dn, o = t - c / 2) : (i = Jo(a, i), o = Jo(a, o), (r > 0 ? i < o : i > o) && (i += r * dn));
    for (var f, l = i; r > 0 ? l > o : l < o; l -= c)
      f = Mi([a, -u * I(l), -u * C(l)]), n.point(f[0], f[1]);
  }
}
function Jo(n, t) {
  t = kt(t), t[0] -= n, wi(t);
  var e = Bu(-t[1]);
  return ((-t[2] < 0 ? -e : e) + dn - U) % dn;
}
function Hu() {
  var n = [], t;
  return {
    point: function(e, r, i) {
      t.push([e, r, i]);
    },
    lineStart: function() {
      n.push(t = []);
    },
    lineEnd: bn,
    rejoin: function() {
      n.length > 1 && n.push(n.pop().concat(n.shift()));
    },
    result: function() {
      var e = n;
      return n = [], t = null, e;
    }
  };
}
function nr(n, t) {
  return B(n[0] - t[0]) < U && B(n[1] - t[1]) < U;
}
function Xe(n, t, e, r) {
  this.x = n, this.z = t, this.o = e, this.e = r, this.v = !1, this.n = this.p = null;
}
function Wu(n, t, e, r, i) {
  var o = [], a = [], u, c;
  if (n.forEach(function(p) {
    if (!((d = p.length - 1) <= 0)) {
      var d, m = p[0], v = p[d], S;
      if (nr(m, v)) {
        if (!m[2] && !v[2]) {
          for (i.lineStart(), u = 0; u < d; ++u) i.point((m = p[u])[0], m[1]);
          i.lineEnd();
          return;
        }
        v[0] += 2 * U;
      }
      o.push(S = new Xe(m, p, null, !0)), a.push(S.o = new Xe(m, null, S, !1)), o.push(S = new Xe(v, p, null, !1)), a.push(S.o = new Xe(v, null, S, !0));
    }
  }), !!o.length) {
    for (a.sort(t), Ko(o), Ko(a), u = 0, c = a.length; u < c; ++u)
      a[u].e = e = !e;
    for (var f = o[0], l, s; ; ) {
      for (var h = f, g = !0; h.v; ) if ((h = h.n) === f) return;
      l = h.z, i.lineStart();
      do {
        if (h.v = h.o.v = !0, h.e) {
          if (g)
            for (u = 0, c = l.length; u < c; ++u) i.point((s = l[u])[0], s[1]);
          else
            r(h.x, h.n.x, 1, i);
          h = h.n;
        } else {
          if (g)
            for (l = h.p.z, u = l.length - 1; u >= 0; --u) i.point((s = l[u])[0], s[1]);
          else
            r(h.x, h.p.x, -1, i);
          h = h.p;
        }
        h = h.o, l = h.z, g = !g;
      } while (!h.v);
      i.lineEnd();
    }
  }
}
function Ko(n) {
  if (t = n.length) {
    for (var t, e = 0, r = n[0], i; ++e < t; )
      r.n = i = n[e], i.p = r, r = i;
    r.n = i = n[0], i.p = r;
  }
}
function Zr(n) {
  return B(n[0]) <= k ? n[0] : yn(n[0]) * ((B(n[0]) + k) % dn - k);
}
function es(n, t) {
  var e = Zr(t), r = t[1], i = C(r), o = [C(e), -I(e), 0], a = 0, u = 0, c = new yt();
  i === 1 ? r = V + U : i === -1 && (r = -V - U);
  for (var f = 0, l = n.length; f < l; ++f)
    if (h = (s = n[f]).length)
      for (var s, h, g = s[h - 1], p = Zr(g), d = g[1] / 2 + Wo, m = C(d), v = I(d), S = 0; S < h; ++S, p = b, m = M, v = A, g = y) {
        var y = s[S], b = Zr(y), x = y[1] / 2 + Wo, M = C(x), A = I(x), P = b - p, F = P >= 0 ? 1 : -1, Y = F * P, E = Y > k, W = m * M;
        if (c.add(Xn(W * F * C(Y), v * A + W * I(Y))), a += E ? P + F * dn : P, E ^ p >= e ^ b >= e) {
          var D = ur(kt(g), kt(y));
          wi(D);
          var R = ur(o, D);
          wi(R);
          var w = (E ^ P >= 0 ? -1 : 1) * Mn(R[2]);
          (r > w || r === w && (D[0] || D[1])) && (u += E ^ P >= 0 ? 1 : -1);
        }
      }
  return (a < -U || a < U && c < -Lu) ^ u & 1;
}
function Gu(n, t, e, r) {
  return function(i) {
    var o = t(i), a = Hu(), u = t(a), c = !1, f, l, s, h = {
      point: g,
      lineStart: d,
      lineEnd: m,
      polygonStart: function() {
        h.point = v, h.lineStart = S, h.lineEnd = y, l = [], f = [];
      },
      polygonEnd: function() {
        h.point = g, h.lineStart = d, h.lineEnd = m, l = Ru(l);
        var b = es(f, r);
        l.length ? (c || (i.polygonStart(), c = !0), Wu(l, is, b, e, i)) : b && (c || (i.polygonStart(), c = !0), i.lineStart(), e(null, null, 1, i), i.lineEnd()), c && (i.polygonEnd(), c = !1), l = f = null;
      },
      sphere: function() {
        i.polygonStart(), i.lineStart(), e(null, null, 1, i), i.lineEnd(), i.polygonEnd();
      }
    };
    function g(b, x) {
      n(b, x) && i.point(b, x);
    }
    function p(b, x) {
      o.point(b, x);
    }
    function d() {
      h.point = p, o.lineStart();
    }
    function m() {
      h.point = g, o.lineEnd();
    }
    function v(b, x) {
      s.push([b, x]), u.point(b, x);
    }
    function S() {
      u.lineStart(), s = [];
    }
    function y() {
      v(s[0][0], s[0][1]), u.lineEnd();
      var b = u.clean(), x = a.result(), M, A = x.length, P, F, Y;
      if (s.pop(), f.push(s), s = null, !!A) {
        if (b & 1) {
          if (F = x[0], (P = F.length - 1) > 0) {
            for (c || (i.polygonStart(), c = !0), i.lineStart(), M = 0; M < P; ++M) i.point((Y = F[M])[0], Y[1]);
            i.lineEnd();
          }
          return;
        }
        A > 1 && b & 2 && x.push(x.pop().concat(x.shift())), l.push(x.filter(rs));
      }
    }
    return h;
  };
}
function rs(n) {
  return n.length > 1;
}
function is(n, t) {
  return ((n = n.x)[0] < 0 ? n[1] - V - U : V - n[1]) - ((t = t.x)[0] < 0 ? t[1] - V - U : V - t[1]);
}
const na = Gu(
  function() {
    return !0;
  },
  os,
  us,
  [-k, -V]
);
function os(n) {
  var t = NaN, e = NaN, r = NaN, i;
  return {
    lineStart: function() {
      n.lineStart(), i = 1;
    },
    point: function(o, a) {
      var u = o > 0 ? k : -k, c = B(o - t);
      B(c - k) < U ? (n.point(t, e = (e + a) / 2 > 0 ? V : -V), n.point(r, e), n.lineEnd(), n.lineStart(), n.point(u, e), n.point(o, e), i = 0) : r !== u && c >= k && (B(t - r) < U && (t -= r * U), B(o - u) < U && (o -= u * U), e = as(t, e, o, a), n.point(r, e), n.lineEnd(), n.lineStart(), n.point(u, e), i = 0), n.point(t = o, e = a), r = u;
    },
    lineEnd: function() {
      n.lineEnd(), t = e = NaN;
    },
    clean: function() {
      return 2 - i;
    }
  };
}
function as(n, t, e, r) {
  var i, o, a = C(n - e);
  return B(a) > U ? _t((C(t) * (o = I(r)) * C(e) - C(r) * (i = I(t)) * C(n)) / (i * o * a)) : (t + r) / 2;
}
function us(n, t, e, r) {
  var i;
  if (n == null)
    i = e * V, r.point(-k, i), r.point(0, i), r.point(k, i), r.point(k, 0), r.point(k, -i), r.point(0, -i), r.point(-k, -i), r.point(-k, 0), r.point(-k, i);
  else if (B(n[0] - t[0]) > U) {
    var o = n[0] < t[0] ? k : -k;
    i = e * o / 2, r.point(-o, i), r.point(0, i), r.point(o, i);
  } else
    r.point(t[0], t[1]);
}
function fs(n) {
  var t = I(n), e = 2 * _, r = t > 0, i = B(t) > U;
  function o(l, s, h, g) {
    ts(g, n, e, h, l, s);
  }
  function a(l, s) {
    return I(l) * I(s) > t;
  }
  function u(l) {
    var s, h, g, p, d;
    return {
      lineStart: function() {
        p = g = !1, d = 1;
      },
      point: function(m, v) {
        var S = [m, v], y, b = a(m, v), x = r ? b ? 0 : f(m, v) : b ? f(m + (m < 0 ? k : -k), v) : 0;
        if (!s && (p = g = b) && l.lineStart(), b !== g && (y = c(s, S), (!y || nr(s, y) || nr(S, y)) && (S[2] = 1)), b !== g)
          d = 0, b ? (l.lineStart(), y = c(S, s), l.point(y[0], y[1])) : (y = c(s, S), l.point(y[0], y[1], 2), l.lineEnd()), s = y;
        else if (i && s && r ^ b) {
          var M;
          !(x & h) && (M = c(S, s, !0)) && (d = 0, r ? (l.lineStart(), l.point(M[0][0], M[0][1]), l.point(M[1][0], M[1][1]), l.lineEnd()) : (l.point(M[1][0], M[1][1]), l.lineEnd(), l.lineStart(), l.point(M[0][0], M[0][1], 3)));
        }
        b && (!s || !nr(s, S)) && l.point(S[0], S[1]), s = S, g = b, h = x;
      },
      lineEnd: function() {
        g && l.lineEnd(), s = null;
      },
      // Rejoin first and last segments if there were intersections and the first
      // and last points were visible.
      clean: function() {
        return d | (p && g) << 1;
      }
    };
  }
  function c(l, s, h) {
    var g = kt(l), p = kt(s), d = [1, 0, 0], m = ur(g, p), v = We(m, m), S = m[0], y = v - S * S;
    if (!y) return !h && l;
    var b = t * v / y, x = -t * S / y, M = ur(d, m), A = Ge(d, b), P = Ge(m, x);
    Vr(A, P);
    var F = M, Y = We(A, F), E = We(F, F), W = Y * Y - E * (We(A, A) - 1);
    if (!(W < 0)) {
      var D = ln(W), R = Ge(F, (-Y - D) / E);
      if (Vr(R, A), R = Mi(R), !h) return R;
      var w = l[0], N = s[0], z = l[1], Z = s[1], X;
      N < w && (X = w, w = N, N = X);
      var at = N - w, Sn = B(at - k) < U, Yn = Sn || at < U;
      if (!Sn && Z < z && (X = z, z = Z, Z = X), Yn ? Sn ? z + Z > 0 ^ R[1] < (B(R[0] - w) < U ? z : Z) : z <= R[1] && R[1] <= Z : at > k ^ (w <= R[0] && R[0] <= N)) {
        var xn = Ge(F, (-Y + D) / E);
        return Vr(xn, A), [R, Mi(xn)];
      }
    }
  }
  function f(l, s) {
    var h = r ? n : k - n, g = 0;
    return l < -h ? g |= 1 : l > h && (g |= 2), s < -h ? g |= 4 : s > h && (g |= 8), g;
  }
  return Gu(a, u, o, r ? [0, -n] : [-k, n - k]);
}
function cs(n, t, e, r, i, o) {
  var a = n[0], u = n[1], c = t[0], f = t[1], l = 0, s = 1, h = c - a, g = f - u, p;
  if (p = e - a, !(!h && p > 0)) {
    if (p /= h, h < 0) {
      if (p < l) return;
      p < s && (s = p);
    } else if (h > 0) {
      if (p > s) return;
      p > l && (l = p);
    }
    if (p = i - a, !(!h && p < 0)) {
      if (p /= h, h < 0) {
        if (p > s) return;
        p > l && (l = p);
      } else if (h > 0) {
        if (p < l) return;
        p < s && (s = p);
      }
      if (p = r - u, !(!g && p > 0)) {
        if (p /= g, g < 0) {
          if (p < l) return;
          p < s && (s = p);
        } else if (g > 0) {
          if (p > s) return;
          p > l && (l = p);
        }
        if (p = o - u, !(!g && p < 0)) {
          if (p /= g, g < 0) {
            if (p > s) return;
            p > l && (l = p);
          } else if (g > 0) {
            if (p < l) return;
            p < s && (s = p);
          }
          return l > 0 && (n[0] = a + l * h, n[1] = u + l * g), s < 1 && (t[0] = a + s * h, t[1] = u + s * g), !0;
        }
      }
    }
  }
}
var ae = 1e9, _e = -ae;
function Xu(n, t, e, r) {
  function i(f, l) {
    return n <= f && f <= e && t <= l && l <= r;
  }
  function o(f, l, s, h) {
    var g = 0, p = 0;
    if (f == null || (g = a(f, s)) !== (p = a(l, s)) || c(f, l) < 0 ^ s > 0)
      do
        h.point(g === 0 || g === 3 ? n : e, g > 1 ? r : t);
      while ((g = (g + s + 4) % 4) !== p);
    else
      h.point(l[0], l[1]);
  }
  function a(f, l) {
    return B(f[0] - n) < U ? l > 0 ? 0 : 3 : B(f[0] - e) < U ? l > 0 ? 2 : 1 : B(f[1] - t) < U ? l > 0 ? 1 : 0 : l > 0 ? 3 : 2;
  }
  function u(f, l) {
    return c(f.x, l.x);
  }
  function c(f, l) {
    var s = a(f, 1), h = a(l, 1);
    return s !== h ? s - h : s === 0 ? l[1] - f[1] : s === 1 ? f[0] - l[0] : s === 2 ? f[1] - l[1] : l[0] - f[0];
  }
  return function(f) {
    var l = f, s = Hu(), h, g, p, d, m, v, S, y, b, x, M, A = {
      point: P,
      lineStart: W,
      lineEnd: D,
      polygonStart: Y,
      polygonEnd: E
    };
    function P(w, N) {
      i(w, N) && l.point(w, N);
    }
    function F() {
      for (var w = 0, N = 0, z = g.length; N < z; ++N)
        for (var Z = g[N], X = 1, at = Z.length, Sn = Z[0], Yn, xn, Et = Sn[0], Jn = Sn[1]; X < at; ++X)
          Yn = Et, xn = Jn, Sn = Z[X], Et = Sn[0], Jn = Sn[1], xn <= r ? Jn > r && (Et - Yn) * (r - xn) > (Jn - xn) * (n - Yn) && ++w : Jn <= r && (Et - Yn) * (r - xn) < (Jn - xn) * (n - Yn) && --w;
      return w;
    }
    function Y() {
      l = s, h = [], g = [], M = !0;
    }
    function E() {
      var w = F(), N = M && w, z = (h = Ru(h)).length;
      (N || z) && (f.polygonStart(), N && (f.lineStart(), o(null, null, 1, f), f.lineEnd()), z && Wu(h, u, w, o, f), f.polygonEnd()), l = f, h = g = p = null;
    }
    function W() {
      A.point = R, g && g.push(p = []), x = !0, b = !1, S = y = NaN;
    }
    function D() {
      h && (R(d, m), v && b && s.rejoin(), h.push(s.result())), A.point = P, b && l.lineEnd();
    }
    function R(w, N) {
      var z = i(w, N);
      if (g && p.push([w, N]), x)
        d = w, m = N, v = z, x = !1, z && (l.lineStart(), l.point(w, N));
      else if (z && b) l.point(w, N);
      else {
        var Z = [S = Math.max(_e, Math.min(ae, S)), y = Math.max(_e, Math.min(ae, y))], X = [w = Math.max(_e, Math.min(ae, w)), N = Math.max(_e, Math.min(ae, N))];
        cs(Z, X, n, t, e, r) ? (b || (l.lineStart(), l.point(Z[0], Z[1])), l.point(X[0], X[1]), z || l.lineEnd(), M = !1) : z && (l.lineStart(), l.point(w, N), M = !1);
      }
      S = w, y = N, b = z;
    }
    return A;
  };
}
const Se = (n) => n;
var Qr = new yt(), $i = new yt(), _u, Vu, Ei, Ai, Ln = {
  point: bn,
  lineStart: bn,
  lineEnd: bn,
  polygonStart: function() {
    Ln.lineStart = ls, Ln.lineEnd = hs;
  },
  polygonEnd: function() {
    Ln.lineStart = Ln.lineEnd = Ln.point = bn, Qr.add(B($i)), $i = new yt();
  },
  result: function() {
    var n = Qr / 2;
    return Qr = new yt(), n;
  }
};
function ls() {
  Ln.point = ss;
}
function ss(n, t) {
  Ln.point = Zu, _u = Ei = n, Vu = Ai = t;
}
function Zu(n, t) {
  $i.add(Ai * n - Ei * t), Ei = n, Ai = t;
}
function hs() {
  Zu(_u, Vu);
}
var Ot = 1 / 0, fr = Ot, xe = -Ot, cr = xe, lr = {
  point: gs,
  lineStart: bn,
  lineEnd: bn,
  polygonStart: bn,
  polygonEnd: bn,
  result: function() {
    var n = [[Ot, fr], [xe, cr]];
    return xe = cr = -(fr = Ot = 1 / 0), n;
  }
};
function gs(n, t) {
  n < Ot && (Ot = n), n > xe && (xe = n), t < fr && (fr = t), t > cr && (cr = t);
}
var Ti = 0, Ni = 0, ue = 0, sr = 0, hr = 0, Dt = 0, Pi = 0, Ci = 0, fe = 0, Qu, Ju, Nn, Pn, mn = {
  point: bt,
  lineStart: ta,
  lineEnd: ea,
  polygonStart: function() {
    mn.lineStart = ms, mn.lineEnd = ys;
  },
  polygonEnd: function() {
    mn.point = bt, mn.lineStart = ta, mn.lineEnd = ea;
  },
  result: function() {
    var n = fe ? [Pi / fe, Ci / fe] : Dt ? [sr / Dt, hr / Dt] : ue ? [Ti / ue, Ni / ue] : [NaN, NaN];
    return Ti = Ni = ue = sr = hr = Dt = Pi = Ci = fe = 0, n;
  }
};
function bt(n, t) {
  Ti += n, Ni += t, ++ue;
}
function ta() {
  mn.point = ps;
}
function ps(n, t) {
  mn.point = ds, bt(Nn = n, Pn = t);
}
function ds(n, t) {
  var e = n - Nn, r = t - Pn, i = ln(e * e + r * r);
  sr += i * (Nn + n) / 2, hr += i * (Pn + t) / 2, Dt += i, bt(Nn = n, Pn = t);
}
function ea() {
  mn.point = bt;
}
function ms() {
  mn.point = bs;
}
function ys() {
  Ku(Qu, Ju);
}
function bs(n, t) {
  mn.point = Ku, bt(Qu = Nn = n, Ju = Pn = t);
}
function Ku(n, t) {
  var e = n - Nn, r = t - Pn, i = ln(e * e + r * r);
  sr += i * (Nn + n) / 2, hr += i * (Pn + t) / 2, Dt += i, i = Pn * n - Nn * t, Pi += i * (Nn + n), Ci += i * (Pn + t), fe += i * 3, bt(Nn = n, Pn = t);
}
function nf(n) {
  this._context = n;
}
nf.prototype = {
  _radius: 4.5,
  pointRadius: function(n) {
    return this._radius = n, this;
  },
  polygonStart: function() {
    this._line = 0;
  },
  polygonEnd: function() {
    this._line = NaN;
  },
  lineStart: function() {
    this._point = 0;
  },
  lineEnd: function() {
    this._line === 0 && this._context.closePath(), this._point = NaN;
  },
  point: function(n, t) {
    switch (this._point) {
      case 0: {
        this._context.moveTo(n, t), this._point = 1;
        break;
      }
      case 1: {
        this._context.lineTo(n, t);
        break;
      }
      default: {
        this._context.moveTo(n + this._radius, t), this._context.arc(n, t, this._radius, 0, dn);
        break;
      }
    }
  },
  result: bn
};
var Di = new yt(), Jr, tf, ef, ce, le, $e = {
  point: bn,
  lineStart: function() {
    $e.point = vs;
  },
  lineEnd: function() {
    Jr && rf(tf, ef), $e.point = bn;
  },
  polygonStart: function() {
    Jr = !0;
  },
  polygonEnd: function() {
    Jr = null;
  },
  result: function() {
    var n = +Di;
    return Di = new yt(), n;
  }
};
function vs(n, t) {
  $e.point = rf, tf = ce = n, ef = le = t;
}
function rf(n, t) {
  ce -= n, le -= t, Di.add(ln(ce * ce + le * le)), ce = n, le = t;
}
let ra, gr, ia, oa;
class aa {
  constructor(t) {
    this._append = t == null ? of : Ms(t), this._radius = 4.5, this._ = "";
  }
  pointRadius(t) {
    return this._radius = +t, this;
  }
  polygonStart() {
    this._line = 0;
  }
  polygonEnd() {
    this._line = NaN;
  }
  lineStart() {
    this._point = 0;
  }
  lineEnd() {
    this._line === 0 && (this._ += "Z"), this._point = NaN;
  }
  point(t, e) {
    switch (this._point) {
      case 0: {
        this._append`M${t},${e}`, this._point = 1;
        break;
      }
      case 1: {
        this._append`L${t},${e}`;
        break;
      }
      default: {
        if (this._append`M${t},${e}`, this._radius !== ia || this._append !== gr) {
          const r = this._radius, i = this._;
          this._ = "", this._append`m0,${r}a${r},${r} 0 1,1 0,${-2 * r}a${r},${r} 0 1,1 0,${2 * r}z`, ia = r, gr = this._append, oa = this._, this._ = i;
        }
        this._ += oa;
        break;
      }
    }
  }
  result() {
    const t = this._;
    return this._ = "", t.length ? t : null;
  }
}
function of(n) {
  let t = 1;
  this._ += n[0];
  for (const e = n.length; t < e; ++t)
    this._ += arguments[t] + n[t];
}
function Ms(n) {
  const t = Math.floor(n);
  if (!(t >= 0)) throw new RangeError(`invalid digits: ${n}`);
  if (t > 15) return of;
  if (t !== ra) {
    const e = 10 ** t;
    ra = t, gr = function(i) {
      let o = 1;
      this._ += i[0];
      for (const a = i.length; o < a; ++o)
        this._ += Math.round(arguments[o] * e) / e + i[o];
    };
  }
  return gr;
}
function af(n, t) {
  let e = 3, r = 4.5, i, o;
  function a(u) {
    return u && (typeof r == "function" && o.pointRadius(+r.apply(this, arguments)), Pt(u, i(o))), o.result();
  }
  return a.area = function(u) {
    return Pt(u, i(Ln)), Ln.result();
  }, a.measure = function(u) {
    return Pt(u, i($e)), $e.result();
  }, a.bounds = function(u) {
    return Pt(u, i(lr)), lr.result();
  }, a.centroid = function(u) {
    return Pt(u, i(mn)), mn.result();
  }, a.projection = function(u) {
    return arguments.length ? (i = u == null ? (n = null, Se) : (n = u).stream, a) : n;
  }, a.context = function(u) {
    return arguments.length ? (o = u == null ? (t = null, new aa(e)) : new nf(t = u), typeof r != "function" && o.pointRadius(r), a) : t;
  }, a.pointRadius = function(u) {
    return arguments.length ? (r = typeof u == "function" ? u : (o.pointRadius(+u), +u), a) : r;
  }, a.digits = function(u) {
    if (!arguments.length) return e;
    if (u == null) e = null;
    else {
      const c = Math.floor(u);
      if (!(c >= 0)) throw new RangeError(`invalid digits: ${u}`);
      e = c;
    }
    return t === null && (o = new aa(e)), a;
  }, a.projection(n).digits(e).context(t);
}
function Ur(n) {
  return function(t) {
    var e = new Ui();
    for (var r in n) e[r] = n[r];
    return e.stream = t, e;
  };
}
function Ui() {
}
Ui.prototype = {
  constructor: Ui,
  point: function(n, t) {
    this.stream.point(n, t);
  },
  sphere: function() {
    this.stream.sphere();
  },
  lineStart: function() {
    this.stream.lineStart();
  },
  lineEnd: function() {
    this.stream.lineEnd();
  },
  polygonStart: function() {
    this.stream.polygonStart();
  },
  polygonEnd: function() {
    this.stream.polygonEnd();
  }
};
function to(n, t, e) {
  var r = n.clipExtent && n.clipExtent();
  return n.scale(150).translate([0, 0]), r != null && n.clipExtent(null), Pt(e, n.stream(lr)), t(lr.result()), r != null && n.clipExtent(r), n;
}
function Fr(n, t, e) {
  return to(n, function(r) {
    var i = t[1][0] - t[0][0], o = t[1][1] - t[0][1], a = Math.min(i / (r[1][0] - r[0][0]), o / (r[1][1] - r[0][1])), u = +t[0][0] + (i - a * (r[1][0] + r[0][0])) / 2, c = +t[0][1] + (o - a * (r[1][1] + r[0][1])) / 2;
    n.scale(150 * a).translate([u, c]);
  }, e);
}
function eo(n, t, e) {
  return Fr(n, [[0, 0], t], e);
}
function ro(n, t, e) {
  return to(n, function(r) {
    var i = +t, o = i / (r[1][0] - r[0][0]), a = (i - o * (r[1][0] + r[0][0])) / 2, u = -o * r[0][1];
    n.scale(150 * o).translate([a, u]);
  }, e);
}
function io(n, t, e) {
  return to(n, function(r) {
    var i = +t, o = i / (r[1][1] - r[0][1]), a = -o * r[0][0], u = (i - o * (r[1][1] + r[0][1])) / 2;
    n.scale(150 * o).translate([a, u]);
  }, e);
}
var ua = 16, ws = I(30 * _);
function fa(n, t) {
  return +t ? xs(n, t) : Ss(n);
}
function Ss(n) {
  return Ur({
    point: function(t, e) {
      t = n(t, e), this.stream.point(t[0], t[1]);
    }
  });
}
function xs(n, t) {
  function e(r, i, o, a, u, c, f, l, s, h, g, p, d, m) {
    var v = f - r, S = l - i, y = v * v + S * S;
    if (y > 4 * t && d--) {
      var b = a + h, x = u + g, M = c + p, A = ln(b * b + x * x + M * M), P = Mn(M /= A), F = B(B(M) - 1) < U || B(o - s) < U ? (o + s) / 2 : Xn(x, b), Y = n(F, P), E = Y[0], W = Y[1], D = E - r, R = W - i, w = S * D - v * R;
      (w * w / y > t || B((v * D + S * R) / y - 0.5) > 0.3 || a * h + u * g + c * p < ws) && (e(r, i, o, a, u, c, E, W, F, b /= A, x /= A, M, d, m), m.point(E, W), e(E, W, F, b, x, M, f, l, s, h, g, p, d, m));
    }
  }
  return function(r) {
    var i, o, a, u, c, f, l, s, h, g, p, d, m = {
      point: v,
      lineStart: S,
      lineEnd: b,
      polygonStart: function() {
        r.polygonStart(), m.lineStart = x;
      },
      polygonEnd: function() {
        r.polygonEnd(), m.lineStart = S;
      }
    };
    function v(P, F) {
      P = n(P, F), r.point(P[0], P[1]);
    }
    function S() {
      s = NaN, m.point = y, r.lineStart();
    }
    function y(P, F) {
      var Y = kt([P, F]), E = n(P, F);
      e(s, h, l, g, p, d, s = E[0], h = E[1], l = P, g = Y[0], p = Y[1], d = Y[2], ua, r), r.point(s, h);
    }
    function b() {
      m.point = v, r.lineEnd();
    }
    function x() {
      S(), m.point = M, m.lineEnd = A;
    }
    function M(P, F) {
      y(i = P, F), o = s, a = h, u = g, c = p, f = d, m.point = y;
    }
    function A() {
      e(s, h, l, g, p, d, o, a, i, u, c, f, ua, r), m.lineEnd = b, b();
    }
    return m;
  };
}
var $s = Ur({
  point: function(n, t) {
    this.stream.point(n * _, t * _);
  }
});
function Es(n) {
  return Ur({
    point: function(t, e) {
      var r = n(t, e);
      return this.stream.point(r[0], r[1]);
    }
  });
}
function As(n, t, e, r, i) {
  function o(a, u) {
    return a *= r, u *= i, [t + n * a, e - n * u];
  }
  return o.invert = function(a, u) {
    return [(a - t) / n * r, (e - u) / n * i];
  }, o;
}
function ca(n, t, e, r, i, o) {
  if (!o) return As(n, t, e, r, i);
  var a = I(o), u = C(o), c = a * n, f = u * n, l = a / n, s = u / n, h = (u * e - a * t) / n, g = (u * t + a * e) / n;
  function p(d, m) {
    return d *= r, m *= i, [c * d - f * m + t, e - f * d - c * m];
  }
  return p.invert = function(d, m) {
    return [r * (l * d - s * m + h), i * (g - s * d - l * m)];
  }, p;
}
function kn(n) {
  return uf(function() {
    return n;
  })();
}
function uf(n) {
  var t, e = 150, r = 480, i = 250, o = 0, a = 0, u = 0, c = 0, f = 0, l, s = 0, h = 1, g = 1, p = null, d = na, m = null, v, S, y, b = Se, x = 0.5, M, A, P, F, Y;
  function E(w) {
    return P(w[0] * _, w[1] * _);
  }
  function W(w) {
    return w = P.invert(w[0], w[1]), w && [w[0] * rn, w[1] * rn];
  }
  E.stream = function(w) {
    return F && Y === w ? F : F = $s(Es(l)(d(M(b(Y = w)))));
  }, E.preclip = function(w) {
    return arguments.length ? (d = w, p = void 0, R()) : d;
  }, E.postclip = function(w) {
    return arguments.length ? (b = w, m = v = S = y = null, R()) : b;
  }, E.clipAngle = function(w) {
    return arguments.length ? (d = +w ? fs(p = w * _) : (p = null, na), R()) : p * rn;
  }, E.clipExtent = function(w) {
    return arguments.length ? (b = w == null ? (m = v = S = y = null, Se) : Xu(m = +w[0][0], v = +w[0][1], S = +w[1][0], y = +w[1][1]), R()) : m == null ? null : [[m, v], [S, y]];
  }, E.scale = function(w) {
    return arguments.length ? (e = +w, D()) : e;
  }, E.translate = function(w) {
    return arguments.length ? (r = +w[0], i = +w[1], D()) : [r, i];
  }, E.center = function(w) {
    return arguments.length ? (o = w[0] % 360 * _, a = w[1] % 360 * _, D()) : [o * rn, a * rn];
  }, E.rotate = function(w) {
    return arguments.length ? (u = w[0] % 360 * _, c = w[1] % 360 * _, f = w.length > 2 ? w[2] % 360 * _ : 0, D()) : [u * rn, c * rn, f * rn];
  }, E.angle = function(w) {
    return arguments.length ? (s = w % 360 * _, D()) : s * rn;
  }, E.reflectX = function(w) {
    return arguments.length ? (h = w ? -1 : 1, D()) : h < 0;
  }, E.reflectY = function(w) {
    return arguments.length ? (g = w ? -1 : 1, D()) : g < 0;
  }, E.precision = function(w) {
    return arguments.length ? (M = fa(A, x = w * w), R()) : ln(x);
  }, E.fitExtent = function(w, N) {
    return Fr(E, w, N);
  }, E.fitSize = function(w, N) {
    return eo(E, w, N);
  }, E.fitWidth = function(w, N) {
    return ro(E, w, N);
  }, E.fitHeight = function(w, N) {
    return io(E, w, N);
  };
  function D() {
    var w = ca(e, 0, 0, h, g, s).apply(null, t(o, a)), N = ca(e, r - w[0], i - w[1], h, g, s);
    return l = zu(u, c, f), A = Si(t, N), P = Si(l, A), M = fa(A, x), R();
  }
  function R() {
    return F = Y = null, E;
  }
  return function() {
    return t = n.apply(this, arguments), E.invert = t.invert && W, D();
  };
}
function oo(n) {
  var t = 0, e = k / 3, r = uf(n), i = r(t, e);
  return i.parallels = function(o) {
    return arguments.length ? r(t = o[0] * _, e = o[1] * _) : [t * rn, e * rn];
  }, i;
}
function Ts(n) {
  var t = I(n);
  function e(r, i) {
    return [r * t, C(i) / t];
  }
  return e.invert = function(r, i) {
    return [r / t, Mn(i * t)];
  }, e;
}
function Ns(n, t) {
  var e = C(n), r = (e + C(t)) / 2;
  if (B(r) < U) return Ts(n);
  var i = 1 + e * (2 * r - e), o = ln(i) / r;
  function a(u, c) {
    var f = ln(i - 2 * r * C(c)) / r;
    return [f * C(u *= r), o - f * I(u)];
  }
  return a.invert = function(u, c) {
    var f = o - c, l = Xn(u, B(f)) * yn(f);
    return f * r < 0 && (l -= k * yn(u) * yn(f)), [l / r, Mn((i - (u * u + f * f) * r * r) / (2 * r))];
  }, a;
}
function pr() {
  return oo(Ns).scale(155.424).center([0, 33.6442]);
}
function ff() {
  return pr().parallels([29.5, 45.5]).scale(1070).translate([480, 250]).rotate([96, 0]).center([-0.6, 38.7]);
}
function Ps(n) {
  var t = n.length;
  return {
    point: function(e, r) {
      for (var i = -1; ++i < t; ) n[i].point(e, r);
    },
    sphere: function() {
      for (var e = -1; ++e < t; ) n[e].sphere();
    },
    lineStart: function() {
      for (var e = -1; ++e < t; ) n[e].lineStart();
    },
    lineEnd: function() {
      for (var e = -1; ++e < t; ) n[e].lineEnd();
    },
    polygonStart: function() {
      for (var e = -1; ++e < t; ) n[e].polygonStart();
    },
    polygonEnd: function() {
      for (var e = -1; ++e < t; ) n[e].polygonEnd();
    }
  };
}
function Cs() {
  var n, t, e = ff(), r, i = pr().rotate([154, 0]).center([-2, 58.5]).parallels([55, 65]), o, a = pr().rotate([157, 0]).center([-3, 19.9]).parallels([8, 18]), u, c, f = { point: function(h, g) {
    c = [h, g];
  } };
  function l(h) {
    var g = h[0], p = h[1];
    return c = null, r.point(g, p), c || (o.point(g, p), c) || (u.point(g, p), c);
  }
  l.invert = function(h) {
    var g = e.scale(), p = e.translate(), d = (h[0] - p[0]) / g, m = (h[1] - p[1]) / g;
    return (m >= 0.12 && m < 0.234 && d >= -0.425 && d < -0.214 ? i : m >= 0.166 && m < 0.234 && d >= -0.214 && d < -0.115 ? a : e).invert(h);
  }, l.stream = function(h) {
    return n && t === h ? n : n = Ps([e.stream(t = h), i.stream(h), a.stream(h)]);
  }, l.precision = function(h) {
    return arguments.length ? (e.precision(h), i.precision(h), a.precision(h), s()) : e.precision();
  }, l.scale = function(h) {
    return arguments.length ? (e.scale(h), i.scale(h * 0.35), a.scale(h), l.translate(e.translate())) : e.scale();
  }, l.translate = function(h) {
    if (!arguments.length) return e.translate();
    var g = e.scale(), p = +h[0], d = +h[1];
    return r = e.translate(h).clipExtent([[p - 0.455 * g, d - 0.238 * g], [p + 0.455 * g, d + 0.238 * g]]).stream(f), o = i.translate([p - 0.307 * g, d + 0.201 * g]).clipExtent([[p - 0.425 * g + U, d + 0.12 * g + U], [p - 0.214 * g - U, d + 0.234 * g - U]]).stream(f), u = a.translate([p - 0.205 * g, d + 0.212 * g]).clipExtent([[p - 0.214 * g + U, d + 0.166 * g + U], [p - 0.115 * g - U, d + 0.234 * g - U]]).stream(f), s();
  }, l.fitExtent = function(h, g) {
    return Fr(l, h, g);
  }, l.fitSize = function(h, g) {
    return eo(l, h, g);
  }, l.fitWidth = function(h, g) {
    return ro(l, h, g);
  }, l.fitHeight = function(h, g) {
    return io(l, h, g);
  };
  function s() {
    return n = t = null, l;
  }
  return l.scale(1070);
}
function cf(n) {
  return function(t, e) {
    var r = I(t), i = I(e), o = n(r * i);
    return o === 1 / 0 ? [2, 0] : [
      o * i * C(t),
      o * C(e)
    ];
  };
}
function Ie(n) {
  return function(t, e) {
    var r = ln(t * t + e * e), i = n(r), o = C(i), a = I(i);
    return [
      Xn(t * o, r * a),
      Mn(r && e * o / r)
    ];
  };
}
var lf = cf(function(n) {
  return ln(2 / (1 + n));
});
lf.invert = Ie(function(n) {
  return 2 * Mn(n / 2);
});
function Ds() {
  return kn(lf).scale(124.75).clipAngle(180 - 1e-3);
}
var sf = cf(function(n) {
  return (n = Bu(n)) && n / C(n);
});
sf.invert = Ie(function(n) {
  return n;
});
function Us() {
  return kn(sf).scale(79.4188).clipAngle(180 - 1e-3);
}
function Rr(n, t) {
  return [n, or(no((V + t) / 2))];
}
Rr.invert = function(n, t) {
  return [n, 2 * _t(ju(t)) - V];
};
function Fs() {
  return hf(Rr).scale(961 / dn);
}
function hf(n) {
  var t = kn(n), e = t.center, r = t.scale, i = t.translate, o = t.clipExtent, a = null, u, c, f;
  t.scale = function(s) {
    return arguments.length ? (r(s), l()) : r();
  }, t.translate = function(s) {
    return arguments.length ? (i(s), l()) : i();
  }, t.center = function(s) {
    return arguments.length ? (e(s), l()) : e();
  }, t.clipExtent = function(s) {
    return arguments.length ? (s == null ? a = u = c = f = null : (a = +s[0][0], u = +s[0][1], c = +s[1][0], f = +s[1][1]), l()) : a == null ? null : [[a, u], [c, f]];
  };
  function l() {
    var s = k * r(), h = t(ns(t.rotate()).invert([0, 0]));
    return o(a == null ? [[h[0] - s, h[1] - s], [h[0] + s, h[1] + s]] : n === Rr ? [[Math.max(h[0] - s, a), u], [Math.min(h[0] + s, c), f]] : [[a, Math.max(h[1] - s, u)], [c, Math.min(h[1] + s, f)]]);
  }
  return l();
}
function Ve(n) {
  return no((V + n) / 2);
}
function Rs(n, t) {
  var e = I(n), r = n === t ? C(n) : or(e / I(t)) / or(Ve(t) / Ve(n)), i = e * _r(Ve(n), r) / r;
  if (!r) return Rr;
  function o(a, u) {
    i > 0 ? u < -V + U && (u = -V + U) : u > V - U && (u = V - U);
    var c = i / _r(Ve(u), r);
    return [c * C(r * a), i - c * I(r * a)];
  }
  return o.invert = function(a, u) {
    var c = i - u, f = yn(r) * ln(a * a + c * c), l = Xn(a, B(c)) * yn(c);
    return c * r < 0 && (l -= k * yn(a) * yn(c)), [l / r, 2 * _t(_r(i / f, 1 / r)) - V];
  }, o;
}
function Is() {
  return oo(Rs).scale(109.5).parallels([30, 30]);
}
function dr(n, t) {
  return [n, t];
}
dr.invert = dr;
function ks() {
  return kn(dr).scale(152.63);
}
function Os(n, t) {
  var e = I(n), r = n === t ? C(n) : (e - I(t)) / (t - n), i = e / r + n;
  if (B(r) < U) return dr;
  function o(a, u) {
    var c = i - u, f = r * a;
    return [c * C(f), i - c * I(f)];
  }
  return o.invert = function(a, u) {
    var c = i - u, f = Xn(a, B(c)) * yn(c);
    return c * r < 0 && (f -= k * yn(a) * yn(c)), [f / r, i - yn(r) * ln(a * a + c * c)];
  }, o;
}
function qs() {
  return oo(Os).scale(131.154).center([0, 13.9389]);
}
var ye = 1.340264, be = -0.081106, ve = 893e-6, Me = 3796e-6, mr = ln(3) / 2, Ys = 12;
function gf(n, t) {
  var e = Mn(mr * C(t)), r = e * e, i = r * r * r;
  return [
    n * I(e) / (mr * (ye + 3 * be * r + i * (7 * ve + 9 * Me * r))),
    e * (ye + be * r + i * (ve + Me * r))
  ];
}
gf.invert = function(n, t) {
  for (var e = t, r = e * e, i = r * r * r, o = 0, a, u, c; o < Ys && (u = e * (ye + be * r + i * (ve + Me * r)) - t, c = ye + 3 * be * r + i * (7 * ve + 9 * Me * r), e -= a = u / c, r = e * e, i = r * r * r, !(B(a) < Lu)); ++o)
    ;
  return [
    mr * n * (ye + 3 * be * r + i * (7 * ve + 9 * Me * r)) / I(e),
    Mn(C(e) / mr)
  ];
};
function Ls() {
  return kn(gf).scale(177.158);
}
function pf(n, t) {
  var e = I(t), r = I(n) * e;
  return [e * C(n) / r, C(t) / r];
}
pf.invert = Ie(_t);
function js() {
  return kn(pf).scale(144.049).clipAngle(60);
}
function Bs() {
  var n = 1, t = 0, e = 0, r = 1, i = 1, o = 0, a, u, c = null, f, l, s, h = 1, g = 1, p = Ur({
    point: function(b, x) {
      var M = y([b, x]);
      this.stream.point(M[0], M[1]);
    }
  }), d = Se, m, v;
  function S() {
    return h = n * r, g = n * i, m = v = null, y;
  }
  function y(b) {
    var x = b[0] * h, M = b[1] * g;
    if (o) {
      var A = M * a - x * u;
      x = x * a + M * u, M = A;
    }
    return [x + t, M + e];
  }
  return y.invert = function(b) {
    var x = b[0] - t, M = b[1] - e;
    if (o) {
      var A = M * a + x * u;
      x = x * a - M * u, M = A;
    }
    return [x / h, M / g];
  }, y.stream = function(b) {
    return m && v === b ? m : m = p(d(v = b));
  }, y.postclip = function(b) {
    return arguments.length ? (d = b, c = f = l = s = null, S()) : d;
  }, y.clipExtent = function(b) {
    return arguments.length ? (d = b == null ? (c = f = l = s = null, Se) : Xu(c = +b[0][0], f = +b[0][1], l = +b[1][0], s = +b[1][1]), S()) : c == null ? null : [[c, f], [l, s]];
  }, y.scale = function(b) {
    return arguments.length ? (n = +b, S()) : n;
  }, y.translate = function(b) {
    return arguments.length ? (t = +b[0], e = +b[1], S()) : [t, e];
  }, y.angle = function(b) {
    return arguments.length ? (o = b % 360 * _, u = C(o), a = I(o), S()) : o * rn;
  }, y.reflectX = function(b) {
    return arguments.length ? (r = b ? -1 : 1, S()) : r < 0;
  }, y.reflectY = function(b) {
    return arguments.length ? (i = b ? -1 : 1, S()) : i < 0;
  }, y.fitExtent = function(b, x) {
    return Fr(y, b, x);
  }, y.fitSize = function(b, x) {
    return eo(y, b, x);
  }, y.fitWidth = function(b, x) {
    return ro(y, b, x);
  }, y.fitHeight = function(b, x) {
    return io(y, b, x);
  }, y;
}
function df(n, t) {
  var e = t * t, r = e * e;
  return [
    n * (0.8707 - 0.131979 * e + r * (-0.013791 + r * (3971e-6 * e - 1529e-6 * r))),
    t * (1.007226 + e * (0.015085 + r * (-0.044475 + 0.028874 * e - 5916e-6 * r)))
  ];
}
df.invert = function(n, t) {
  var e = t, r = 25, i;
  do {
    var o = e * e, a = o * o;
    e -= i = (e * (1.007226 + o * (0.015085 + a * (-0.044475 + 0.028874 * o - 5916e-6 * a))) - t) / (1.007226 + o * (0.015085 * 3 + a * (-0.044475 * 7 + 0.028874 * 9 * o - 5916e-6 * 11 * a)));
  } while (B(i) > U && --r > 0);
  return [
    n / (0.8707 + (o = e * e) * (-0.131979 + o * (-0.013791 + o * o * o * (3971e-6 - 1529e-6 * o)))),
    e
  ];
};
function zs() {
  return kn(df).scale(175.295);
}
function mf(n, t) {
  return [I(t) * C(n), C(t)];
}
mf.invert = Ie(Mn);
function Hs() {
  return kn(mf).scale(249.5).clipAngle(90 + U);
}
function yf(n, t) {
  var e = I(t), r = 1 + I(n) * e;
  return [e * C(n) / r, C(t) / r];
}
yf.invert = Ie(function(n) {
  return 2 * _t(n);
});
function Ws() {
  return kn(yf).scale(250).clipAngle(142);
}
function bf(n, t) {
  return [or(no((V + t) / 2)), -n];
}
bf.invert = function(n, t) {
  return [-t, 2 * _t(ju(n)) - V];
};
function Gs() {
  var n = hf(bf), t = n.center, e = n.rotate;
  return n.center = function(r) {
    return arguments.length ? t([-r[1], r[0]]) : (r = t(), [r[1], -r[0]]);
  }, n.rotate = function(r) {
    return arguments.length ? e([r[0], r[1], r.length > 2 ? r[2] + 90 : 90]) : (r = e(), [r[0], r[1], r[2] - 90]);
  }, e([0, 0, 90]).scale(159.155);
}
var Xs = Math.abs, Fi = Math.cos, yr = Math.sin, _s = 1e-6, vf = Math.PI, Ri = vf / 2, la = Vs(2);
function sa(n) {
  return n > 1 ? Ri : n < -1 ? -Ri : Math.asin(n);
}
function Vs(n) {
  return n > 0 ? Math.sqrt(n) : 0;
}
function Zs(n, t) {
  var e = n * yr(t), r = 30, i;
  do
    t -= i = (t + yr(t) - e) / (1 + Fi(t));
  while (Xs(i) > _s && --r > 0);
  return t / 2;
}
function Qs(n, t, e) {
  function r(i, o) {
    return [n * i * Fi(o = Zs(e, o)), t * yr(o)];
  }
  return r.invert = function(i, o) {
    return o = sa(o / t), [i / (n * Fi(o)), sa((2 * o + yr(2 * o)) / e)];
  }, r;
}
var Js = Qs(la / Ri, la, vf);
function Ks() {
  return kn(Js).scale(169.529);
}
function On(n, t) {
  switch (arguments.length) {
    case 0:
      break;
    case 1:
      this.range(n);
      break;
    default:
      this.range(t).domain(n);
      break;
  }
  return this;
}
function rt(n, t) {
  switch (arguments.length) {
    case 0:
      break;
    case 1: {
      typeof n == "function" ? this.interpolator(n) : this.range(n);
      break;
    }
    default: {
      this.domain(n), typeof t == "function" ? this.interpolator(t) : this.range(t);
      break;
    }
  }
  return this;
}
const ha = Symbol("implicit");
function ao() {
  var n = new Lo(), t = [], e = [], r = ha;
  function i(o) {
    let a = n.get(o);
    if (a === void 0) {
      if (r !== ha) return r;
      n.set(o, a = t.push(o) - 1);
    }
    return e[a % e.length];
  }
  return i.domain = function(o) {
    if (!arguments.length) return t.slice();
    t = [], n = new Lo();
    for (const a of o)
      n.has(a) || n.set(a, t.push(a) - 1);
    return i;
  }, i.range = function(o) {
    return arguments.length ? (e = Array.from(o), i) : e.slice();
  }, i.unknown = function(o) {
    return arguments.length ? (r = o, i) : r;
  }, i.copy = function() {
    return ao(t, e).unknown(r);
  }, On.apply(i, arguments), i;
}
function Vt(n, t, e) {
  n.prototype = t.prototype = e, e.constructor = n;
}
function ke(n, t) {
  var e = Object.create(n.prototype);
  for (var r in t) e[r] = t[r];
  return e;
}
function it() {
}
var vt = 0.7, qt = 1 / vt, Ut = "\\s*([+-]?\\d+)\\s*", Ee = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*", Cn = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*", n0 = /^#([0-9a-f]{3,8})$/, t0 = new RegExp(`^rgb\\(${Ut},${Ut},${Ut}\\)$`), e0 = new RegExp(`^rgb\\(${Cn},${Cn},${Cn}\\)$`), r0 = new RegExp(`^rgba\\(${Ut},${Ut},${Ut},${Ee}\\)$`), i0 = new RegExp(`^rgba\\(${Cn},${Cn},${Cn},${Ee}\\)$`), o0 = new RegExp(`^hsl\\(${Ee},${Cn},${Cn}\\)$`), a0 = new RegExp(`^hsla\\(${Ee},${Cn},${Cn},${Ee}\\)$`), ga = {
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
Vt(it, Ae, {
  copy(n) {
    return Object.assign(new this.constructor(), this, n);
  },
  displayable() {
    return this.rgb().displayable();
  },
  hex: pa,
  // Deprecated! Use color.formatHex.
  formatHex: pa,
  formatHex8: u0,
  formatHsl: f0,
  formatRgb: da,
  toString: da
});
function pa() {
  return this.rgb().formatHex();
}
function u0() {
  return this.rgb().formatHex8();
}
function f0() {
  return Mf(this).formatHsl();
}
function da() {
  return this.rgb().formatRgb();
}
function Ae(n) {
  var t, e;
  return n = (n + "").trim().toLowerCase(), (t = n0.exec(n)) ? (e = t[1].length, t = parseInt(t[1], 16), e === 6 ? ma(t) : e === 3 ? new nn(t >> 8 & 15 | t >> 4 & 240, t >> 4 & 15 | t & 240, (t & 15) << 4 | t & 15, 1) : e === 8 ? Ze(t >> 24 & 255, t >> 16 & 255, t >> 8 & 255, (t & 255) / 255) : e === 4 ? Ze(t >> 12 & 15 | t >> 8 & 240, t >> 8 & 15 | t >> 4 & 240, t >> 4 & 15 | t & 240, ((t & 15) << 4 | t & 15) / 255) : null) : (t = t0.exec(n)) ? new nn(t[1], t[2], t[3], 1) : (t = e0.exec(n)) ? new nn(t[1] * 255 / 100, t[2] * 255 / 100, t[3] * 255 / 100, 1) : (t = r0.exec(n)) ? Ze(t[1], t[2], t[3], t[4]) : (t = i0.exec(n)) ? Ze(t[1] * 255 / 100, t[2] * 255 / 100, t[3] * 255 / 100, t[4]) : (t = o0.exec(n)) ? va(t[1], t[2] / 100, t[3] / 100, 1) : (t = a0.exec(n)) ? va(t[1], t[2] / 100, t[3] / 100, t[4]) : ga.hasOwnProperty(n) ? ma(ga[n]) : n === "transparent" ? new nn(NaN, NaN, NaN, 0) : null;
}
function ma(n) {
  return new nn(n >> 16 & 255, n >> 8 & 255, n & 255, 1);
}
function Ze(n, t, e, r) {
  return r <= 0 && (n = t = e = NaN), new nn(n, t, e, r);
}
function uo(n) {
  return n instanceof it || (n = Ae(n)), n ? (n = n.rgb(), new nn(n.r, n.g, n.b, n.opacity)) : new nn();
}
function br(n, t, e, r) {
  return arguments.length === 1 ? uo(n) : new nn(n, t, e, r ?? 1);
}
function nn(n, t, e, r) {
  this.r = +n, this.g = +t, this.b = +e, this.opacity = +r;
}
Vt(nn, br, ke(it, {
  brighter(n) {
    return n = n == null ? qt : Math.pow(qt, n), new nn(this.r * n, this.g * n, this.b * n, this.opacity);
  },
  darker(n) {
    return n = n == null ? vt : Math.pow(vt, n), new nn(this.r * n, this.g * n, this.b * n, this.opacity);
  },
  rgb() {
    return this;
  },
  clamp() {
    return new nn(ht(this.r), ht(this.g), ht(this.b), vr(this.opacity));
  },
  displayable() {
    return -0.5 <= this.r && this.r < 255.5 && -0.5 <= this.g && this.g < 255.5 && -0.5 <= this.b && this.b < 255.5 && 0 <= this.opacity && this.opacity <= 1;
  },
  hex: ya,
  // Deprecated! Use color.formatHex.
  formatHex: ya,
  formatHex8: c0,
  formatRgb: ba,
  toString: ba
}));
function ya() {
  return `#${lt(this.r)}${lt(this.g)}${lt(this.b)}`;
}
function c0() {
  return `#${lt(this.r)}${lt(this.g)}${lt(this.b)}${lt((isNaN(this.opacity) ? 1 : this.opacity) * 255)}`;
}
function ba() {
  const n = vr(this.opacity);
  return `${n === 1 ? "rgb(" : "rgba("}${ht(this.r)}, ${ht(this.g)}, ${ht(this.b)}${n === 1 ? ")" : `, ${n})`}`;
}
function vr(n) {
  return isNaN(n) ? 1 : Math.max(0, Math.min(1, n));
}
function ht(n) {
  return Math.max(0, Math.min(255, Math.round(n) || 0));
}
function lt(n) {
  return n = ht(n), (n < 16 ? "0" : "") + n.toString(16);
}
function va(n, t, e, r) {
  return r <= 0 ? n = t = e = NaN : e <= 0 || e >= 1 ? n = t = NaN : t <= 0 && (n = NaN), new En(n, t, e, r);
}
function Mf(n) {
  if (n instanceof En) return new En(n.h, n.s, n.l, n.opacity);
  if (n instanceof it || (n = Ae(n)), !n) return new En();
  if (n instanceof En) return n;
  n = n.rgb();
  var t = n.r / 255, e = n.g / 255, r = n.b / 255, i = Math.min(t, e, r), o = Math.max(t, e, r), a = NaN, u = o - i, c = (o + i) / 2;
  return u ? (t === o ? a = (e - r) / u + (e < r) * 6 : e === o ? a = (r - t) / u + 2 : a = (t - e) / u + 4, u /= c < 0.5 ? o + i : 2 - o - i, a *= 60) : u = c > 0 && c < 1 ? 0 : a, new En(a, u, c, n.opacity);
}
function Ii(n, t, e, r) {
  return arguments.length === 1 ? Mf(n) : new En(n, t, e, r ?? 1);
}
function En(n, t, e, r) {
  this.h = +n, this.s = +t, this.l = +e, this.opacity = +r;
}
Vt(En, Ii, ke(it, {
  brighter(n) {
    return n = n == null ? qt : Math.pow(qt, n), new En(this.h, this.s, this.l * n, this.opacity);
  },
  darker(n) {
    return n = n == null ? vt : Math.pow(vt, n), new En(this.h, this.s, this.l * n, this.opacity);
  },
  rgb() {
    var n = this.h % 360 + (this.h < 0) * 360, t = isNaN(n) || isNaN(this.s) ? 0 : this.s, e = this.l, r = e + (e < 0.5 ? e : 1 - e) * t, i = 2 * e - r;
    return new nn(
      Kr(n >= 240 ? n - 240 : n + 120, i, r),
      Kr(n, i, r),
      Kr(n < 120 ? n + 240 : n - 120, i, r),
      this.opacity
    );
  },
  clamp() {
    return new En(Ma(this.h), Qe(this.s), Qe(this.l), vr(this.opacity));
  },
  displayable() {
    return (0 <= this.s && this.s <= 1 || isNaN(this.s)) && 0 <= this.l && this.l <= 1 && 0 <= this.opacity && this.opacity <= 1;
  },
  formatHsl() {
    const n = vr(this.opacity);
    return `${n === 1 ? "hsl(" : "hsla("}${Ma(this.h)}, ${Qe(this.s) * 100}%, ${Qe(this.l) * 100}%${n === 1 ? ")" : `, ${n})`}`;
  }
}));
function Ma(n) {
  return n = (n || 0) % 360, n < 0 ? n + 360 : n;
}
function Qe(n) {
  return Math.max(0, Math.min(1, n || 0));
}
function Kr(n, t, e) {
  return (n < 60 ? t + (e - t) * n / 60 : n < 180 ? e : n < 240 ? t + (e - t) * (240 - n) / 60 : t) * 255;
}
const wf = Math.PI / 180, Sf = 180 / Math.PI, Mr = 18, xf = 0.96422, $f = 1, Ef = 0.82521, Af = 4 / 29, Ft = 6 / 29, Tf = 3 * Ft * Ft, l0 = Ft * Ft * Ft;
function Nf(n) {
  if (n instanceof Dn) return new Dn(n.l, n.a, n.b, n.opacity);
  if (n instanceof jn) return Pf(n);
  n instanceof nn || (n = uo(n));
  var t = ri(n.r), e = ri(n.g), r = ri(n.b), i = ni((0.2225045 * t + 0.7168786 * e + 0.0606169 * r) / $f), o, a;
  return t === e && e === r ? o = a = i : (o = ni((0.4360747 * t + 0.3850649 * e + 0.1430804 * r) / xf), a = ni((0.0139322 * t + 0.0971045 * e + 0.7141733 * r) / Ef)), new Dn(116 * i - 16, 500 * (o - i), 200 * (i - a), n.opacity);
}
function ki(n, t, e, r) {
  return arguments.length === 1 ? Nf(n) : new Dn(n, t, e, r ?? 1);
}
function Dn(n, t, e, r) {
  this.l = +n, this.a = +t, this.b = +e, this.opacity = +r;
}
Vt(Dn, ki, ke(it, {
  brighter(n) {
    return new Dn(this.l + Mr * (n ?? 1), this.a, this.b, this.opacity);
  },
  darker(n) {
    return new Dn(this.l - Mr * (n ?? 1), this.a, this.b, this.opacity);
  },
  rgb() {
    var n = (this.l + 16) / 116, t = isNaN(this.a) ? n : n + this.a / 500, e = isNaN(this.b) ? n : n - this.b / 200;
    return t = xf * ti(t), n = $f * ti(n), e = Ef * ti(e), new nn(
      ei(3.1338561 * t - 1.6168667 * n - 0.4906146 * e),
      ei(-0.9787684 * t + 1.9161415 * n + 0.033454 * e),
      ei(0.0719453 * t - 0.2289914 * n + 1.4052427 * e),
      this.opacity
    );
  }
}));
function ni(n) {
  return n > l0 ? Math.pow(n, 1 / 3) : n / Tf + Af;
}
function ti(n) {
  return n > Ft ? n * n * n : Tf * (n - Af);
}
function ei(n) {
  return 255 * (n <= 31308e-7 ? 12.92 * n : 1.055 * Math.pow(n, 1 / 2.4) - 0.055);
}
function ri(n) {
  return (n /= 255) <= 0.04045 ? n / 12.92 : Math.pow((n + 0.055) / 1.055, 2.4);
}
function s0(n) {
  if (n instanceof jn) return new jn(n.h, n.c, n.l, n.opacity);
  if (n instanceof Dn || (n = Nf(n)), n.a === 0 && n.b === 0) return new jn(NaN, 0 < n.l && n.l < 100 ? 0 : NaN, n.l, n.opacity);
  var t = Math.atan2(n.b, n.a) * Sf;
  return new jn(t < 0 ? t + 360 : t, Math.sqrt(n.a * n.a + n.b * n.b), n.l, n.opacity);
}
function Oi(n, t, e, r) {
  return arguments.length === 1 ? s0(n) : new jn(n, t, e, r ?? 1);
}
function jn(n, t, e, r) {
  this.h = +n, this.c = +t, this.l = +e, this.opacity = +r;
}
function Pf(n) {
  if (isNaN(n.h)) return new Dn(n.l, 0, 0, n.opacity);
  var t = n.h * wf;
  return new Dn(n.l, Math.cos(t) * n.c, Math.sin(t) * n.c, n.opacity);
}
Vt(jn, Oi, ke(it, {
  brighter(n) {
    return new jn(this.h, this.c, this.l + Mr * (n ?? 1), this.opacity);
  },
  darker(n) {
    return new jn(this.h, this.c, this.l - Mr * (n ?? 1), this.opacity);
  },
  rgb() {
    return Pf(this).rgb();
  }
}));
var Cf = -0.14861, fo = 1.78277, co = -0.29227, Ir = -0.90649, Te = 1.97294, wa = Te * Ir, Sa = Te * fo, xa = fo * co - Ir * Cf;
function h0(n) {
  if (n instanceof gt) return new gt(n.h, n.s, n.l, n.opacity);
  n instanceof nn || (n = uo(n));
  var t = n.r / 255, e = n.g / 255, r = n.b / 255, i = (xa * r + wa * t - Sa * e) / (xa + wa - Sa), o = r - i, a = (Te * (e - i) - co * o) / Ir, u = Math.sqrt(a * a + o * o) / (Te * i * (1 - i)), c = u ? Math.atan2(a, o) * Sf - 120 : NaN;
  return new gt(c < 0 ? c + 360 : c, u, i, n.opacity);
}
function qi(n, t, e, r) {
  return arguments.length === 1 ? h0(n) : new gt(n, t, e, r ?? 1);
}
function gt(n, t, e, r) {
  this.h = +n, this.s = +t, this.l = +e, this.opacity = +r;
}
Vt(gt, qi, ke(it, {
  brighter(n) {
    return n = n == null ? qt : Math.pow(qt, n), new gt(this.h, this.s, this.l * n, this.opacity);
  },
  darker(n) {
    return n = n == null ? vt : Math.pow(vt, n), new gt(this.h, this.s, this.l * n, this.opacity);
  },
  rgb() {
    var n = isNaN(this.h) ? 0 : (this.h + 120) * wf, t = +this.l, e = isNaN(this.s) ? 0 : this.s * t * (1 - t), r = Math.cos(n), i = Math.sin(n);
    return new nn(
      255 * (t + e * (Cf * r + fo * i)),
      255 * (t + e * (co * r + Ir * i)),
      255 * (t + e * (Te * r)),
      this.opacity
    );
  }
}));
function Df(n, t, e, r, i) {
  var o = n * n, a = o * n;
  return ((1 - 3 * n + 3 * o - a) * t + (4 - 6 * o + 3 * a) * e + (1 + 3 * n + 3 * o - 3 * a) * r + a * i) / 6;
}
function Uf(n) {
  var t = n.length - 1;
  return function(e) {
    var r = e <= 0 ? e = 0 : e >= 1 ? (e = 1, t - 1) : Math.floor(e * t), i = n[r], o = n[r + 1], a = r > 0 ? n[r - 1] : 2 * i - o, u = r < t - 1 ? n[r + 2] : 2 * o - i;
    return Df((e - r / t) * t, a, i, o, u);
  };
}
function Ff(n) {
  var t = n.length;
  return function(e) {
    var r = Math.floor(((e %= 1) < 0 ? ++e : e) * t), i = n[(r + t - 1) % t], o = n[r % t], a = n[(r + 1) % t], u = n[(r + 2) % t];
    return Df((e - r / t) * t, i, o, a, u);
  };
}
const kr = (n) => () => n;
function Rf(n, t) {
  return function(e) {
    return n + e * t;
  };
}
function g0(n, t, e) {
  return n = Math.pow(n, e), t = Math.pow(t, e) - n, e = 1 / e, function(r) {
    return Math.pow(n + r * t, e);
  };
}
function Or(n, t) {
  var e = t - n;
  return e ? Rf(n, e > 180 || e < -180 ? e - 360 * Math.round(e / 360) : e) : kr(isNaN(n) ? t : n);
}
function p0(n) {
  return (n = +n) == 1 ? tn : function(t, e) {
    return e - t ? g0(t, e, n) : kr(isNaN(t) ? e : t);
  };
}
function tn(n, t) {
  var e = t - n;
  return e ? Rf(n, e) : kr(isNaN(n) ? t : n);
}
const Yi = function n(t) {
  var e = p0(t);
  function r(i, o) {
    var a = e((i = br(i)).r, (o = br(o)).r), u = e(i.g, o.g), c = e(i.b, o.b), f = tn(i.opacity, o.opacity);
    return function(l) {
      return i.r = a(l), i.g = u(l), i.b = c(l), i.opacity = f(l), i + "";
    };
  }
  return r.gamma = n, r;
}(1);
function If(n) {
  return function(t) {
    var e = t.length, r = new Array(e), i = new Array(e), o = new Array(e), a, u;
    for (a = 0; a < e; ++a)
      u = br(t[a]), r[a] = u.r || 0, i[a] = u.g || 0, o[a] = u.b || 0;
    return r = n(r), i = n(i), o = n(o), u.opacity = 1, function(c) {
      return u.r = r(c), u.g = i(c), u.b = o(c), u + "";
    };
  };
}
var d0 = If(Uf), m0 = If(Ff);
function lo(n, t) {
  t || (t = []);
  var e = n ? Math.min(t.length, n.length) : 0, r = t.slice(), i;
  return function(o) {
    for (i = 0; i < e; ++i) r[i] = n[i] * (1 - o) + t[i] * o;
    return r;
  };
}
function kf(n) {
  return ArrayBuffer.isView(n) && !(n instanceof DataView);
}
function y0(n, t) {
  return (kf(t) ? lo : Of)(n, t);
}
function Of(n, t) {
  var e = t ? t.length : 0, r = n ? Math.min(e, n.length) : 0, i = new Array(r), o = new Array(e), a;
  for (a = 0; a < r; ++a) i[a] = Mt(n[a], t[a]);
  for (; a < e; ++a) o[a] = t[a];
  return function(u) {
    for (a = 0; a < r; ++a) o[a] = i[a](u);
    return o;
  };
}
function qf(n, t) {
  var e = /* @__PURE__ */ new Date();
  return n = +n, t = +t, function(r) {
    return e.setTime(n * (1 - r) + t * r), e;
  };
}
function $n(n, t) {
  return n = +n, t = +t, function(e) {
    return n * (1 - e) + t * e;
  };
}
function Yf(n, t) {
  var e = {}, r = {}, i;
  (n === null || typeof n != "object") && (n = {}), (t === null || typeof t != "object") && (t = {});
  for (i in t)
    i in n ? e[i] = Mt(n[i], t[i]) : r[i] = t[i];
  return function(o) {
    for (i in e) r[i] = e[i](o);
    return r;
  };
}
var Li = /[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g, ii = new RegExp(Li.source, "g");
function b0(n) {
  return function() {
    return n;
  };
}
function v0(n) {
  return function(t) {
    return n(t) + "";
  };
}
function Lf(n, t) {
  var e = Li.lastIndex = ii.lastIndex = 0, r, i, o, a = -1, u = [], c = [];
  for (n = n + "", t = t + ""; (r = Li.exec(n)) && (i = ii.exec(t)); )
    (o = i.index) > e && (o = t.slice(e, o), u[a] ? u[a] += o : u[++a] = o), (r = r[0]) === (i = i[0]) ? u[a] ? u[a] += i : u[++a] = i : (u[++a] = null, c.push({ i: a, x: $n(r, i) })), e = ii.lastIndex;
  return e < t.length && (o = t.slice(e), u[a] ? u[a] += o : u[++a] = o), u.length < 2 ? c[0] ? v0(c[0].x) : b0(t) : (t = c.length, function(f) {
    for (var l = 0, s; l < t; ++l) u[(s = c[l]).i] = s.x(f);
    return u.join("");
  });
}
function Mt(n, t) {
  var e = typeof t, r;
  return t == null || e === "boolean" ? kr(t) : (e === "number" ? $n : e === "string" ? (r = Ae(t)) ? (t = r, Yi) : Lf : t instanceof Ae ? Yi : t instanceof Date ? qf : kf(t) ? lo : Array.isArray(t) ? Of : typeof t.valueOf != "function" && typeof t.toString != "function" || isNaN(t) ? Yf : $n)(n, t);
}
function M0(n) {
  var t = n.length;
  return function(e) {
    return n[Math.max(0, Math.min(t - 1, Math.floor(e * t)))];
  };
}
function w0(n, t) {
  var e = Or(+n, +t);
  return function(r) {
    var i = e(r);
    return i - 360 * Math.floor(i / 360);
  };
}
function qr(n, t) {
  return n = +n, t = +t, function(e) {
    return Math.round(n * (1 - e) + t * e);
  };
}
var $a = 180 / Math.PI, ji = {
  translateX: 0,
  translateY: 0,
  rotate: 0,
  skewX: 0,
  scaleX: 1,
  scaleY: 1
};
function jf(n, t, e, r, i, o) {
  var a, u, c;
  return (a = Math.sqrt(n * n + t * t)) && (n /= a, t /= a), (c = n * e + t * r) && (e -= n * c, r -= t * c), (u = Math.sqrt(e * e + r * r)) && (e /= u, r /= u, c /= u), n * r < t * e && (n = -n, t = -t, c = -c, a = -a), {
    translateX: i,
    translateY: o,
    rotate: Math.atan2(t, n) * $a,
    skewX: Math.atan(c) * $a,
    scaleX: a,
    scaleY: u
  };
}
var Je;
function S0(n) {
  const t = new (typeof DOMMatrix == "function" ? DOMMatrix : WebKitCSSMatrix)(n + "");
  return t.isIdentity ? ji : jf(t.a, t.b, t.c, t.d, t.e, t.f);
}
function x0(n) {
  return n == null || (Je || (Je = document.createElementNS("http://www.w3.org/2000/svg", "g")), Je.setAttribute("transform", n), !(n = Je.transform.baseVal.consolidate())) ? ji : (n = n.matrix, jf(n.a, n.b, n.c, n.d, n.e, n.f));
}
function Bf(n, t, e, r) {
  function i(f) {
    return f.length ? f.pop() + " " : "";
  }
  function o(f, l, s, h, g, p) {
    if (f !== s || l !== h) {
      var d = g.push("translate(", null, t, null, e);
      p.push({ i: d - 4, x: $n(f, s) }, { i: d - 2, x: $n(l, h) });
    } else (s || h) && g.push("translate(" + s + t + h + e);
  }
  function a(f, l, s, h) {
    f !== l ? (f - l > 180 ? l += 360 : l - f > 180 && (f += 360), h.push({ i: s.push(i(s) + "rotate(", null, r) - 2, x: $n(f, l) })) : l && s.push(i(s) + "rotate(" + l + r);
  }
  function u(f, l, s, h) {
    f !== l ? h.push({ i: s.push(i(s) + "skewX(", null, r) - 2, x: $n(f, l) }) : l && s.push(i(s) + "skewX(" + l + r);
  }
  function c(f, l, s, h, g, p) {
    if (f !== s || l !== h) {
      var d = g.push(i(g) + "scale(", null, ",", null, ")");
      p.push({ i: d - 4, x: $n(f, s) }, { i: d - 2, x: $n(l, h) });
    } else (s !== 1 || h !== 1) && g.push(i(g) + "scale(" + s + "," + h + ")");
  }
  return function(f, l) {
    var s = [], h = [];
    return f = n(f), l = n(l), o(f.translateX, f.translateY, l.translateX, l.translateY, s, h), a(f.rotate, l.rotate, s, h), u(f.skewX, l.skewX, s, h), c(f.scaleX, f.scaleY, l.scaleX, l.scaleY, s, h), f = l = null, function(g) {
      for (var p = -1, d = h.length, m; ++p < d; ) s[(m = h[p]).i] = m.x(g);
      return s.join("");
    };
  };
}
var $0 = Bf(S0, "px, ", "px)", "deg)"), E0 = Bf(x0, ", ", ")", ")"), A0 = 1e-12;
function Ea(n) {
  return ((n = Math.exp(n)) + 1 / n) / 2;
}
function T0(n) {
  return ((n = Math.exp(n)) - 1 / n) / 2;
}
function N0(n) {
  return ((n = Math.exp(2 * n)) - 1) / (n + 1);
}
const P0 = function n(t, e, r) {
  function i(o, a) {
    var u = o[0], c = o[1], f = o[2], l = a[0], s = a[1], h = a[2], g = l - u, p = s - c, d = g * g + p * p, m, v;
    if (d < A0)
      v = Math.log(h / f) / t, m = function(A) {
        return [
          u + A * g,
          c + A * p,
          f * Math.exp(t * A * v)
        ];
      };
    else {
      var S = Math.sqrt(d), y = (h * h - f * f + r * d) / (2 * f * e * S), b = (h * h - f * f - r * d) / (2 * h * e * S), x = Math.log(Math.sqrt(y * y + 1) - y), M = Math.log(Math.sqrt(b * b + 1) - b);
      v = (M - x) / t, m = function(A) {
        var P = A * v, F = Ea(x), Y = f / (e * S) * (F * N0(t * P + x) - T0(x));
        return [
          u + Y * g,
          c + Y * p,
          f * F / Ea(t * P + x)
        ];
      };
    }
    return m.duration = v * 1e3 * t / Math.SQRT2, m;
  }
  return i.rho = function(o) {
    var a = Math.max(1e-3, +o), u = a * a, c = u * u;
    return n(a, u, c);
  }, i;
}(Math.SQRT2, 2, 4);
function zf(n) {
  return function(t, e) {
    var r = n((t = Ii(t)).h, (e = Ii(e)).h), i = tn(t.s, e.s), o = tn(t.l, e.l), a = tn(t.opacity, e.opacity);
    return function(u) {
      return t.h = r(u), t.s = i(u), t.l = o(u), t.opacity = a(u), t + "";
    };
  };
}
const C0 = zf(Or);
var D0 = zf(tn);
function U0(n, t) {
  var e = tn((n = ki(n)).l, (t = ki(t)).l), r = tn(n.a, t.a), i = tn(n.b, t.b), o = tn(n.opacity, t.opacity);
  return function(a) {
    return n.l = e(a), n.a = r(a), n.b = i(a), n.opacity = o(a), n + "";
  };
}
function Hf(n) {
  return function(t, e) {
    var r = n((t = Oi(t)).h, (e = Oi(e)).h), i = tn(t.c, e.c), o = tn(t.l, e.l), a = tn(t.opacity, e.opacity);
    return function(u) {
      return t.h = r(u), t.c = i(u), t.l = o(u), t.opacity = a(u), t + "";
    };
  };
}
const F0 = Hf(Or);
var R0 = Hf(tn);
function Wf(n) {
  return function t(e) {
    e = +e;
    function r(i, o) {
      var a = n((i = qi(i)).h, (o = qi(o)).h), u = tn(i.s, o.s), c = tn(i.l, o.l), f = tn(i.opacity, o.opacity);
      return function(l) {
        return i.h = a(l), i.s = u(l), i.l = c(Math.pow(l, e)), i.opacity = f(l), i + "";
      };
    }
    return r.gamma = t, r;
  }(1);
}
const I0 = Wf(Or);
var k0 = Wf(tn);
function so(n, t) {
  t === void 0 && (t = n, n = Mt);
  for (var e = 0, r = t.length - 1, i = t[0], o = new Array(r < 0 ? 0 : r); e < r; ) o[e] = n(i, i = t[++e]);
  return function(a) {
    var u = Math.max(0, Math.min(r - 1, Math.floor(a *= r)));
    return o[u](a - u);
  };
}
function O0(n, t) {
  for (var e = new Array(t), r = 0; r < t; ++r) e[r] = n(r / (t - 1));
  return e;
}
const q0 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  interpolate: Mt,
  interpolateArray: y0,
  interpolateBasis: Uf,
  interpolateBasisClosed: Ff,
  interpolateCubehelix: I0,
  interpolateCubehelixLong: k0,
  interpolateDate: qf,
  interpolateDiscrete: M0,
  interpolateHcl: F0,
  interpolateHclLong: R0,
  interpolateHsl: C0,
  interpolateHslLong: D0,
  interpolateHue: w0,
  interpolateLab: U0,
  interpolateNumber: $n,
  interpolateNumberArray: lo,
  interpolateObject: Yf,
  interpolateRgb: Yi,
  interpolateRgbBasis: d0,
  interpolateRgbBasisClosed: m0,
  interpolateRound: qr,
  interpolateString: Lf,
  interpolateTransformCss: $0,
  interpolateTransformSvg: E0,
  interpolateZoom: P0,
  piecewise: so,
  quantize: O0
}, Symbol.toStringTag, { value: "Module" }));
function Y0(n) {
  return function() {
    return n;
  };
}
function Bi(n) {
  return +n;
}
var Aa = [0, 1];
function fn(n) {
  return n;
}
function zi(n, t) {
  return (t -= n = +n) ? function(e) {
    return (e - n) / t;
  } : Y0(isNaN(t) ? NaN : 0.5);
}
function L0(n, t) {
  var e;
  return n > t && (e = n, n = t, t = e), function(r) {
    return Math.max(n, Math.min(t, r));
  };
}
function j0(n, t, e) {
  var r = n[0], i = n[1], o = t[0], a = t[1];
  return i < r ? (r = zi(i, r), o = e(a, o)) : (r = zi(r, i), o = e(o, a)), function(u) {
    return o(r(u));
  };
}
function B0(n, t, e) {
  var r = Math.min(n.length, t.length) - 1, i = new Array(r), o = new Array(r), a = -1;
  for (n[r] < n[0] && (n = n.slice().reverse(), t = t.slice().reverse()); ++a < r; )
    i[a] = zi(n[a], n[a + 1]), o[a] = e(t[a], t[a + 1]);
  return function(u) {
    var c = mt(n, u, 1, r) - 1;
    return o[c](i[c](u));
  };
}
function Oe(n, t) {
  return t.domain(n.domain()).range(n.range()).interpolate(n.interpolate()).clamp(n.clamp()).unknown(n.unknown());
}
function Yr() {
  var n = Aa, t = Aa, e = Mt, r, i, o, a = fn, u, c, f;
  function l() {
    var h = Math.min(n.length, t.length);
    return a !== fn && (a = L0(n[0], n[h - 1])), u = h > 2 ? B0 : j0, c = f = null, s;
  }
  function s(h) {
    return h == null || isNaN(h = +h) ? o : (c || (c = u(n.map(r), t, e)))(r(a(h)));
  }
  return s.invert = function(h) {
    return a(i((f || (f = u(t, n.map(r), $n)))(h)));
  }, s.domain = function(h) {
    return arguments.length ? (n = Array.from(h, Bi), l()) : n.slice();
  }, s.range = function(h) {
    return arguments.length ? (t = Array.from(h), l()) : t.slice();
  }, s.rangeRound = function(h) {
    return t = Array.from(h), e = qr, l();
  }, s.clamp = function(h) {
    return arguments.length ? (a = h ? !0 : fn, l()) : a !== fn;
  }, s.interpolate = function(h) {
    return arguments.length ? (e = h, l()) : e;
  }, s.unknown = function(h) {
    return arguments.length ? (o = h, s) : o;
  }, function(h, g) {
    return r = h, i = g, l();
  };
}
function Gf() {
  return Yr()(fn, fn);
}
function z0(n) {
  return Math.abs(n = Math.round(n)) >= 1e21 ? n.toLocaleString("en").replace(/,/g, "") : n.toString(10);
}
function wr(n, t) {
  if ((e = (n = t ? n.toExponential(t - 1) : n.toExponential()).indexOf("e")) < 0) return null;
  var e, r = n.slice(0, e);
  return [
    r.length > 1 ? r[0] + r.slice(2) : r,
    +n.slice(e + 1)
  ];
}
function Yt(n) {
  return n = wr(Math.abs(n)), n ? n[1] : NaN;
}
function H0(n, t) {
  return function(e, r) {
    for (var i = e.length, o = [], a = 0, u = n[0], c = 0; i > 0 && u > 0 && (c + u + 1 > r && (u = Math.max(1, r - c)), o.push(e.substring(i -= u, i + u)), !((c += u + 1) > r)); )
      u = n[a = (a + 1) % n.length];
    return o.reverse().join(t);
  };
}
function W0(n) {
  return function(t) {
    return t.replace(/[0-9]/g, function(e) {
      return n[+e];
    });
  };
}
var G0 = /^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;
function Ne(n) {
  if (!(t = G0.exec(n))) throw new Error("invalid format: " + n);
  var t;
  return new ho({
    fill: t[1],
    align: t[2],
    sign: t[3],
    symbol: t[4],
    zero: t[5],
    width: t[6],
    comma: t[7],
    precision: t[8] && t[8].slice(1),
    trim: t[9],
    type: t[10]
  });
}
Ne.prototype = ho.prototype;
function ho(n) {
  this.fill = n.fill === void 0 ? " " : n.fill + "", this.align = n.align === void 0 ? ">" : n.align + "", this.sign = n.sign === void 0 ? "-" : n.sign + "", this.symbol = n.symbol === void 0 ? "" : n.symbol + "", this.zero = !!n.zero, this.width = n.width === void 0 ? void 0 : +n.width, this.comma = !!n.comma, this.precision = n.precision === void 0 ? void 0 : +n.precision, this.trim = !!n.trim, this.type = n.type === void 0 ? "" : n.type + "";
}
ho.prototype.toString = function() {
  return this.fill + this.align + this.sign + this.symbol + (this.zero ? "0" : "") + (this.width === void 0 ? "" : Math.max(1, this.width | 0)) + (this.comma ? "," : "") + (this.precision === void 0 ? "" : "." + Math.max(0, this.precision | 0)) + (this.trim ? "~" : "") + this.type;
};
function X0(n) {
  n: for (var t = n.length, e = 1, r = -1, i; e < t; ++e)
    switch (n[e]) {
      case ".":
        r = i = e;
        break;
      case "0":
        r === 0 && (r = e), i = e;
        break;
      default:
        if (!+n[e]) break n;
        r > 0 && (r = 0);
        break;
    }
  return r > 0 ? n.slice(0, r) + n.slice(i + 1) : n;
}
var Xf;
function _0(n, t) {
  var e = wr(n, t);
  if (!e) return n + "";
  var r = e[0], i = e[1], o = i - (Xf = Math.max(-8, Math.min(8, Math.floor(i / 3))) * 3) + 1, a = r.length;
  return o === a ? r : o > a ? r + new Array(o - a + 1).join("0") : o > 0 ? r.slice(0, o) + "." + r.slice(o) : "0." + new Array(1 - o).join("0") + wr(n, Math.max(0, t + o - 1))[0];
}
function Ta(n, t) {
  var e = wr(n, t);
  if (!e) return n + "";
  var r = e[0], i = e[1];
  return i < 0 ? "0." + new Array(-i).join("0") + r : r.length > i + 1 ? r.slice(0, i + 1) + "." + r.slice(i + 1) : r + new Array(i - r.length + 2).join("0");
}
const Na = {
  "%": (n, t) => (n * 100).toFixed(t),
  b: (n) => Math.round(n).toString(2),
  c: (n) => n + "",
  d: z0,
  e: (n, t) => n.toExponential(t),
  f: (n, t) => n.toFixed(t),
  g: (n, t) => n.toPrecision(t),
  o: (n) => Math.round(n).toString(8),
  p: (n, t) => Ta(n * 100, t),
  r: Ta,
  s: _0,
  X: (n) => Math.round(n).toString(16).toUpperCase(),
  x: (n) => Math.round(n).toString(16)
};
function Pa(n) {
  return n;
}
var Ca = Array.prototype.map, Da = ["y", "z", "a", "f", "p", "n", "µ", "m", "", "k", "M", "G", "T", "P", "E", "Z", "Y"];
function V0(n) {
  var t = n.grouping === void 0 || n.thousands === void 0 ? Pa : H0(Ca.call(n.grouping, Number), n.thousands + ""), e = n.currency === void 0 ? "" : n.currency[0] + "", r = n.currency === void 0 ? "" : n.currency[1] + "", i = n.decimal === void 0 ? "." : n.decimal + "", o = n.numerals === void 0 ? Pa : W0(Ca.call(n.numerals, String)), a = n.percent === void 0 ? "%" : n.percent + "", u = n.minus === void 0 ? "−" : n.minus + "", c = n.nan === void 0 ? "NaN" : n.nan + "";
  function f(s) {
    s = Ne(s);
    var h = s.fill, g = s.align, p = s.sign, d = s.symbol, m = s.zero, v = s.width, S = s.comma, y = s.precision, b = s.trim, x = s.type;
    x === "n" ? (S = !0, x = "g") : Na[x] || (y === void 0 && (y = 12), b = !0, x = "g"), (m || h === "0" && g === "=") && (m = !0, h = "0", g = "=");
    var M = d === "$" ? e : d === "#" && /[boxX]/.test(x) ? "0" + x.toLowerCase() : "", A = d === "$" ? r : /[%p]/.test(x) ? a : "", P = Na[x], F = /[defgprs%]/.test(x);
    y = y === void 0 ? 6 : /[gprs]/.test(x) ? Math.max(1, Math.min(21, y)) : Math.max(0, Math.min(20, y));
    function Y(E) {
      var W = M, D = A, R, w, N;
      if (x === "c")
        D = P(E) + D, E = "";
      else {
        E = +E;
        var z = E < 0 || 1 / E < 0;
        if (E = isNaN(E) ? c : P(Math.abs(E), y), b && (E = X0(E)), z && +E == 0 && p !== "+" && (z = !1), W = (z ? p === "(" ? p : u : p === "-" || p === "(" ? "" : p) + W, D = (x === "s" ? Da[8 + Xf / 3] : "") + D + (z && p === "(" ? ")" : ""), F) {
          for (R = -1, w = E.length; ++R < w; )
            if (N = E.charCodeAt(R), 48 > N || N > 57) {
              D = (N === 46 ? i + E.slice(R + 1) : E.slice(R)) + D, E = E.slice(0, R);
              break;
            }
        }
      }
      S && !m && (E = t(E, 1 / 0));
      var Z = W.length + E.length + D.length, X = Z < v ? new Array(v - Z + 1).join(h) : "";
      switch (S && m && (E = t(X + E, X.length ? v - D.length : 1 / 0), X = ""), g) {
        case "<":
          E = W + E + D + X;
          break;
        case "=":
          E = W + X + E + D;
          break;
        case "^":
          E = X.slice(0, Z = X.length >> 1) + W + E + D + X.slice(Z);
          break;
        default:
          E = X + W + E + D;
          break;
      }
      return o(E);
    }
    return Y.toString = function() {
      return s + "";
    }, Y;
  }
  function l(s, h) {
    var g = f((s = Ne(s), s.type = "f", s)), p = Math.max(-8, Math.min(8, Math.floor(Yt(h) / 3))) * 3, d = Math.pow(10, -p), m = Da[8 + p / 3];
    return function(v) {
      return g(d * v) + m;
    };
  }
  return {
    format: f,
    formatPrefix: l
  };
}
var Ke, go, _f;
Z0({
  thousands: ",",
  grouping: [3],
  currency: ["$", ""]
});
function Z0(n) {
  return Ke = V0(n), go = Ke.format, _f = Ke.formatPrefix, Ke;
}
function Q0(n) {
  return Math.max(0, -Yt(Math.abs(n)));
}
function J0(n, t) {
  return Math.max(0, Math.max(-8, Math.min(8, Math.floor(Yt(t) / 3))) * 3 - Yt(Math.abs(n)));
}
function K0(n, t) {
  return n = Math.abs(n), t = Math.abs(t) - n, Math.max(0, Yt(t) - Yt(n)) + 1;
}
function Vf(n, t, e, r) {
  var i = we(n, t, e), o;
  switch (r = Ne(r ?? ",f"), r.type) {
    case "s": {
      var a = Math.max(Math.abs(n), Math.abs(t));
      return r.precision == null && !isNaN(o = J0(i, a)) && (r.precision = o), _f(r, a);
    }
    case "":
    case "e":
    case "g":
    case "p":
    case "r": {
      r.precision == null && !isNaN(o = K0(i, Math.max(Math.abs(n), Math.abs(t)))) && (r.precision = o - (r.type === "e"));
      break;
    }
    case "f":
    case "%": {
      r.precision == null && !isNaN(o = Q0(i)) && (r.precision = o - (r.type === "%") * 2);
      break;
    }
  }
  return go(r);
}
function wt(n) {
  var t = n.domain;
  return n.ticks = function(e) {
    var r = t();
    return mi(r[0], r[r.length - 1], e ?? 10);
  }, n.tickFormat = function(e, r) {
    var i = t();
    return Vf(i[0], i[i.length - 1], e ?? 10, r);
  }, n.nice = function(e) {
    e == null && (e = 10);
    var r = t(), i = 0, o = r.length - 1, a = r[i], u = r[o], c, f, l = 10;
    for (u < a && (f = a, a = u, u = f, f = i, i = o, o = f); l-- > 0; ) {
      if (f = yi(a, u, e), f === c)
        return r[i] = a, r[o] = u, t(r);
      if (f > 0)
        a = Math.floor(a / f) * f, u = Math.ceil(u / f) * f;
      else if (f < 0)
        a = Math.ceil(a * f) / f, u = Math.floor(u * f) / f;
      else
        break;
      c = f;
    }
    return n;
  }, n;
}
function Zf() {
  var n = Gf();
  return n.copy = function() {
    return Oe(n, Zf());
  }, On.apply(n, arguments), wt(n);
}
function Qf(n) {
  var t;
  function e(r) {
    return r == null || isNaN(r = +r) ? t : r;
  }
  return e.invert = e, e.domain = e.range = function(r) {
    return arguments.length ? (n = Array.from(r, Bi), e) : n.slice();
  }, e.unknown = function(r) {
    return arguments.length ? (t = r, e) : t;
  }, e.copy = function() {
    return Qf(n).unknown(t);
  }, n = arguments.length ? Array.from(n, Bi) : [0, 1], wt(e);
}
function Jf(n, t) {
  n = n.slice();
  var e = 0, r = n.length - 1, i = n[e], o = n[r], a;
  return o < i && (a = e, e = r, r = a, a = i, i = o, o = a), n[e] = t.floor(i), n[r] = t.ceil(o), n;
}
function Ua(n) {
  return Math.log(n);
}
function Fa(n) {
  return Math.exp(n);
}
function n1(n) {
  return -Math.log(-n);
}
function t1(n) {
  return -Math.exp(-n);
}
function e1(n) {
  return isFinite(n) ? +("1e" + n) : n < 0 ? 0 : n;
}
function r1(n) {
  return n === 10 ? e1 : n === Math.E ? Math.exp : (t) => Math.pow(n, t);
}
function i1(n) {
  return n === Math.E ? Math.log : n === 10 && Math.log10 || n === 2 && Math.log2 || (n = Math.log(n), (t) => Math.log(t) / n);
}
function Ra(n) {
  return (t, e) => -n(-t, e);
}
function po(n) {
  const t = n(Ua, Fa), e = t.domain;
  let r = 10, i, o;
  function a() {
    return i = i1(r), o = r1(r), e()[0] < 0 ? (i = Ra(i), o = Ra(o), n(n1, t1)) : n(Ua, Fa), t;
  }
  return t.base = function(u) {
    return arguments.length ? (r = +u, a()) : r;
  }, t.domain = function(u) {
    return arguments.length ? (e(u), a()) : e();
  }, t.ticks = (u) => {
    const c = e();
    let f = c[0], l = c[c.length - 1];
    const s = l < f;
    s && ([f, l] = [l, f]);
    let h = i(f), g = i(l), p, d;
    const m = u == null ? 10 : +u;
    let v = [];
    if (!(r % 1) && g - h < m) {
      if (h = Math.floor(h), g = Math.ceil(g), f > 0) {
        for (; h <= g; ++h)
          for (p = 1; p < r; ++p)
            if (d = h < 0 ? p / o(-h) : p * o(h), !(d < f)) {
              if (d > l) break;
              v.push(d);
            }
      } else for (; h <= g; ++h)
        for (p = r - 1; p >= 1; --p)
          if (d = h > 0 ? p / o(-h) : p * o(h), !(d < f)) {
            if (d > l) break;
            v.push(d);
          }
      v.length * 2 < m && (v = mi(f, l, m));
    } else
      v = mi(h, g, Math.min(g - h, m)).map(o);
    return s ? v.reverse() : v;
  }, t.tickFormat = (u, c) => {
    if (u == null && (u = 10), c == null && (c = r === 10 ? "s" : ","), typeof c != "function" && (!(r % 1) && (c = Ne(c)).precision == null && (c.trim = !0), c = go(c)), u === 1 / 0) return c;
    const f = Math.max(1, r * u / t.ticks().length);
    return (l) => {
      let s = l / o(Math.round(i(l)));
      return s * r < r - 0.5 && (s *= r), s <= f ? c(l) : "";
    };
  }, t.nice = () => e(Jf(e(), {
    floor: (u) => o(Math.floor(i(u))),
    ceil: (u) => o(Math.ceil(i(u)))
  })), t;
}
function Kf() {
  const n = po(Yr()).domain([1, 10]);
  return n.copy = () => Oe(n, Kf()).base(n.base()), On.apply(n, arguments), n;
}
function Ia(n) {
  return function(t) {
    return Math.sign(t) * Math.log1p(Math.abs(t / n));
  };
}
function ka(n) {
  return function(t) {
    return Math.sign(t) * Math.expm1(Math.abs(t)) * n;
  };
}
function mo(n) {
  var t = 1, e = n(Ia(t), ka(t));
  return e.constant = function(r) {
    return arguments.length ? n(Ia(t = +r), ka(t)) : t;
  }, wt(e);
}
function nc() {
  var n = mo(Yr());
  return n.copy = function() {
    return Oe(n, nc()).constant(n.constant());
  }, On.apply(n, arguments);
}
function Oa(n) {
  return function(t) {
    return t < 0 ? -Math.pow(-t, n) : Math.pow(t, n);
  };
}
function o1(n) {
  return n < 0 ? -Math.sqrt(-n) : Math.sqrt(n);
}
function a1(n) {
  return n < 0 ? -n * n : n * n;
}
function yo(n) {
  var t = n(fn, fn), e = 1;
  function r() {
    return e === 1 ? n(fn, fn) : e === 0.5 ? n(o1, a1) : n(Oa(e), Oa(1 / e));
  }
  return t.exponent = function(i) {
    return arguments.length ? (e = +i, r()) : e;
  }, wt(t);
}
function bo() {
  var n = yo(Yr());
  return n.copy = function() {
    return Oe(n, bo()).exponent(n.exponent());
  }, On.apply(n, arguments), n;
}
function u1() {
  return bo.apply(null, arguments).exponent(0.5);
}
function tc() {
  var n = [], t = [], e = [], r;
  function i() {
    var a = 0, u = Math.max(1, t.length);
    for (e = new Array(u - 1); ++a < u; ) e[a - 1] = Fu(n, a / u);
    return o;
  }
  function o(a) {
    return a == null || isNaN(a = +a) ? r : t[mt(e, a)];
  }
  return o.invertExtent = function(a) {
    var u = t.indexOf(a);
    return u < 0 ? [NaN, NaN] : [
      u > 0 ? e[u - 1] : n[0],
      u < e.length ? e[u] : n[n.length - 1]
    ];
  }, o.domain = function(a) {
    if (!arguments.length) return n.slice();
    n = [];
    for (let u of a) u != null && !isNaN(u = +u) && n.push(u);
    return n.sort(Wn), i();
  }, o.range = function(a) {
    return arguments.length ? (t = Array.from(a), i()) : t.slice();
  }, o.unknown = function(a) {
    return arguments.length ? (r = a, o) : r;
  }, o.quantiles = function() {
    return e.slice();
  }, o.copy = function() {
    return tc().domain(n).range(t).unknown(r);
  }, On.apply(o, arguments);
}
function ec() {
  var n = 0, t = 1, e = 1, r = [0.5], i = [0, 1], o;
  function a(c) {
    return c != null && c <= c ? i[mt(r, c, 0, e)] : o;
  }
  function u() {
    var c = -1;
    for (r = new Array(e); ++c < e; ) r[c] = ((c + 1) * t - (c - e) * n) / (e + 1);
    return a;
  }
  return a.domain = function(c) {
    return arguments.length ? ([n, t] = c, n = +n, t = +t, u()) : [n, t];
  }, a.range = function(c) {
    return arguments.length ? (e = (i = Array.from(c)).length - 1, u()) : i.slice();
  }, a.invertExtent = function(c) {
    var f = i.indexOf(c);
    return f < 0 ? [NaN, NaN] : f < 1 ? [n, r[0]] : f >= e ? [r[e - 1], t] : [r[f - 1], r[f]];
  }, a.unknown = function(c) {
    return arguments.length && (o = c), a;
  }, a.thresholds = function() {
    return r.slice();
  }, a.copy = function() {
    return ec().domain([n, t]).range(i).unknown(o);
  }, On.apply(wt(a), arguments);
}
function rc() {
  var n = [0.5], t = [0, 1], e, r = 1;
  function i(o) {
    return o != null && o <= o ? t[mt(n, o, 0, r)] : e;
  }
  return i.domain = function(o) {
    return arguments.length ? (n = Array.from(o), r = Math.min(n.length, t.length - 1), i) : n.slice();
  }, i.range = function(o) {
    return arguments.length ? (t = Array.from(o), r = Math.min(n.length, t.length - 1), i) : t.slice();
  }, i.invertExtent = function(o) {
    var a = t.indexOf(o);
    return [n[a - 1], n[a]];
  }, i.unknown = function(o) {
    return arguments.length ? (e = o, i) : e;
  }, i.copy = function() {
    return rc().domain(n).range(t).unknown(e);
  }, On.apply(i, arguments);
}
const oi = /* @__PURE__ */ new Date(), ai = /* @__PURE__ */ new Date();
function Q(n, t, e, r) {
  function i(o) {
    return n(o = arguments.length === 0 ? /* @__PURE__ */ new Date() : /* @__PURE__ */ new Date(+o)), o;
  }
  return i.floor = (o) => (n(o = /* @__PURE__ */ new Date(+o)), o), i.ceil = (o) => (n(o = new Date(o - 1)), t(o, 1), n(o), o), i.round = (o) => {
    const a = i(o), u = i.ceil(o);
    return o - a < u - o ? a : u;
  }, i.offset = (o, a) => (t(o = /* @__PURE__ */ new Date(+o), a == null ? 1 : Math.floor(a)), o), i.range = (o, a, u) => {
    const c = [];
    if (o = i.ceil(o), u = u == null ? 1 : Math.floor(u), !(o < a) || !(u > 0)) return c;
    let f;
    do
      c.push(f = /* @__PURE__ */ new Date(+o)), t(o, u), n(o);
    while (f < o && o < a);
    return c;
  }, i.filter = (o) => Q((a) => {
    if (a >= a) for (; n(a), !o(a); ) a.setTime(a - 1);
  }, (a, u) => {
    if (a >= a)
      if (u < 0) for (; ++u <= 0; )
        for (; t(a, -1), !o(a); )
          ;
      else for (; --u >= 0; )
        for (; t(a, 1), !o(a); )
          ;
  }), e && (i.count = (o, a) => (oi.setTime(+o), ai.setTime(+a), n(oi), n(ai), Math.floor(e(oi, ai))), i.every = (o) => (o = Math.floor(o), !isFinite(o) || !(o > 0) ? null : o > 1 ? i.filter(r ? (a) => r(a) % o === 0 : (a) => i.count(0, a) % o === 0) : i)), i;
}
const Lt = Q(() => {
}, (n, t) => {
  n.setTime(+n + t);
}, (n, t) => t - n);
Lt.every = (n) => (n = Math.floor(n), !isFinite(n) || !(n > 0) ? null : n > 1 ? Q((t) => {
  t.setTime(Math.floor(t / n) * n);
}, (t, e) => {
  t.setTime(+t + e * n);
}, (t, e) => (e - t) / n) : Lt);
Lt.range;
const Bn = 1e3, vn = Bn * 60, zn = vn * 60, _n = zn * 24, vo = _n * 7, qa = _n * 30, ui = _n * 365, Hn = Q((n) => {
  n.setTime(n - n.getMilliseconds());
}, (n, t) => {
  n.setTime(+n + t * Bn);
}, (n, t) => (t - n) / Bn, (n) => n.getUTCSeconds());
Hn.range;
const Lr = Q((n) => {
  n.setTime(n - n.getMilliseconds() - n.getSeconds() * Bn);
}, (n, t) => {
  n.setTime(+n + t * vn);
}, (n, t) => (t - n) / vn, (n) => n.getMinutes());
Lr.range;
const jr = Q((n) => {
  n.setUTCSeconds(0, 0);
}, (n, t) => {
  n.setTime(+n + t * vn);
}, (n, t) => (t - n) / vn, (n) => n.getUTCMinutes());
jr.range;
const Br = Q((n) => {
  n.setTime(n - n.getMilliseconds() - n.getSeconds() * Bn - n.getMinutes() * vn);
}, (n, t) => {
  n.setTime(+n + t * zn);
}, (n, t) => (t - n) / zn, (n) => n.getHours());
Br.range;
const zr = Q((n) => {
  n.setUTCMinutes(0, 0, 0);
}, (n, t) => {
  n.setTime(+n + t * zn);
}, (n, t) => (t - n) / zn, (n) => n.getUTCHours());
zr.range;
const Gn = Q(
  (n) => n.setHours(0, 0, 0, 0),
  (n, t) => n.setDate(n.getDate() + t),
  (n, t) => (t - n - (t.getTimezoneOffset() - n.getTimezoneOffset()) * vn) / _n,
  (n) => n.getDate() - 1
);
Gn.range;
const Kn = Q((n) => {
  n.setUTCHours(0, 0, 0, 0);
}, (n, t) => {
  n.setUTCDate(n.getUTCDate() + t);
}, (n, t) => (t - n) / _n, (n) => n.getUTCDate() - 1);
Kn.range;
const ic = Q((n) => {
  n.setUTCHours(0, 0, 0, 0);
}, (n, t) => {
  n.setUTCDate(n.getUTCDate() + t);
}, (n, t) => (t - n) / _n, (n) => Math.floor(n / _n));
ic.range;
function St(n) {
  return Q((t) => {
    t.setDate(t.getDate() - (t.getDay() + 7 - n) % 7), t.setHours(0, 0, 0, 0);
  }, (t, e) => {
    t.setDate(t.getDate() + e * 7);
  }, (t, e) => (e - t - (e.getTimezoneOffset() - t.getTimezoneOffset()) * vn) / vo);
}
const Zt = St(0), Sr = St(1), f1 = St(2), c1 = St(3), jt = St(4), l1 = St(5), s1 = St(6);
Zt.range;
Sr.range;
f1.range;
c1.range;
jt.range;
l1.range;
s1.range;
function xt(n) {
  return Q((t) => {
    t.setUTCDate(t.getUTCDate() - (t.getUTCDay() + 7 - n) % 7), t.setUTCHours(0, 0, 0, 0);
  }, (t, e) => {
    t.setUTCDate(t.getUTCDate() + e * 7);
  }, (t, e) => (e - t) / vo);
}
const Qt = xt(0), xr = xt(1), h1 = xt(2), g1 = xt(3), Bt = xt(4), p1 = xt(5), d1 = xt(6);
Qt.range;
xr.range;
h1.range;
g1.range;
Bt.range;
p1.range;
d1.range;
const Pe = Q((n) => {
  n.setDate(1), n.setHours(0, 0, 0, 0);
}, (n, t) => {
  n.setMonth(n.getMonth() + t);
}, (n, t) => t.getMonth() - n.getMonth() + (t.getFullYear() - n.getFullYear()) * 12, (n) => n.getMonth());
Pe.range;
const Ce = Q((n) => {
  n.setUTCDate(1), n.setUTCHours(0, 0, 0, 0);
}, (n, t) => {
  n.setUTCMonth(n.getUTCMonth() + t);
}, (n, t) => t.getUTCMonth() - n.getUTCMonth() + (t.getUTCFullYear() - n.getUTCFullYear()) * 12, (n) => n.getUTCMonth());
Ce.range;
const Un = Q((n) => {
  n.setMonth(0, 1), n.setHours(0, 0, 0, 0);
}, (n, t) => {
  n.setFullYear(n.getFullYear() + t);
}, (n, t) => t.getFullYear() - n.getFullYear(), (n) => n.getFullYear());
Un.every = (n) => !isFinite(n = Math.floor(n)) || !(n > 0) ? null : Q((t) => {
  t.setFullYear(Math.floor(t.getFullYear() / n) * n), t.setMonth(0, 1), t.setHours(0, 0, 0, 0);
}, (t, e) => {
  t.setFullYear(t.getFullYear() + e * n);
});
Un.range;
const Fn = Q((n) => {
  n.setUTCMonth(0, 1), n.setUTCHours(0, 0, 0, 0);
}, (n, t) => {
  n.setUTCFullYear(n.getUTCFullYear() + t);
}, (n, t) => t.getUTCFullYear() - n.getUTCFullYear(), (n) => n.getUTCFullYear());
Fn.every = (n) => !isFinite(n = Math.floor(n)) || !(n > 0) ? null : Q((t) => {
  t.setUTCFullYear(Math.floor(t.getUTCFullYear() / n) * n), t.setUTCMonth(0, 1), t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCFullYear(t.getUTCFullYear() + e * n);
});
Fn.range;
function oc(n, t, e, r, i, o) {
  const a = [
    [Hn, 1, Bn],
    [Hn, 5, 5 * Bn],
    [Hn, 15, 15 * Bn],
    [Hn, 30, 30 * Bn],
    [o, 1, vn],
    [o, 5, 5 * vn],
    [o, 15, 15 * vn],
    [o, 30, 30 * vn],
    [i, 1, zn],
    [i, 3, 3 * zn],
    [i, 6, 6 * zn],
    [i, 12, 12 * zn],
    [r, 1, _n],
    [r, 2, 2 * _n],
    [e, 1, vo],
    [t, 1, qa],
    [t, 3, 3 * qa],
    [n, 1, ui]
  ];
  function u(f, l, s) {
    const h = l < f;
    h && ([f, l] = [l, f]);
    const g = s && typeof s.range == "function" ? s : c(f, l, s), p = g ? g.range(f, +l + 1) : [];
    return h ? p.reverse() : p;
  }
  function c(f, l, s) {
    const h = Math.abs(l - f) / s, g = Cr(([, , m]) => m).right(a, h);
    if (g === a.length) return n.every(we(f / ui, l / ui, s));
    if (g === 0) return Lt.every(Math.max(we(f, l, s), 1));
    const [p, d] = a[h / a[g - 1][2] < a[g][2] / h ? g - 1 : g];
    return p.every(d);
  }
  return [u, c];
}
const [m1, y1] = oc(Fn, Ce, Qt, ic, zr, jr), [b1, v1] = oc(Un, Pe, Zt, Gn, Br, Lr);
function fi(n) {
  if (0 <= n.y && n.y < 100) {
    var t = new Date(-1, n.m, n.d, n.H, n.M, n.S, n.L);
    return t.setFullYear(n.y), t;
  }
  return new Date(n.y, n.m, n.d, n.H, n.M, n.S, n.L);
}
function ci(n) {
  if (0 <= n.y && n.y < 100) {
    var t = new Date(Date.UTC(-1, n.m, n.d, n.H, n.M, n.S, n.L));
    return t.setUTCFullYear(n.y), t;
  }
  return new Date(Date.UTC(n.y, n.m, n.d, n.H, n.M, n.S, n.L));
}
function ee(n, t, e) {
  return { y: n, m: t, d: e, H: 0, M: 0, S: 0, L: 0 };
}
function M1(n) {
  var t = n.dateTime, e = n.date, r = n.time, i = n.periods, o = n.days, a = n.shortDays, u = n.months, c = n.shortMonths, f = re(i), l = ie(i), s = re(o), h = ie(o), g = re(a), p = ie(a), d = re(u), m = ie(u), v = re(c), S = ie(c), y = {
    a: z,
    A: Z,
    b: X,
    B: at,
    c: null,
    d: Ha,
    e: Ha,
    f: z1,
    g: K1,
    G: th,
    H: L1,
    I: j1,
    j: B1,
    L: ac,
    m: H1,
    M: W1,
    p: Sn,
    q: Yn,
    Q: Xa,
    s: _a,
    S: G1,
    u: X1,
    U: _1,
    V: V1,
    w: Z1,
    W: Q1,
    x: null,
    X: null,
    y: J1,
    Y: nh,
    Z: eh,
    "%": Ga
  }, b = {
    a: xn,
    A: Et,
    b: Jn,
    B: Lc,
    c: null,
    d: Wa,
    e: Wa,
    f: ah,
    g: mh,
    G: bh,
    H: rh,
    I: ih,
    j: oh,
    L: fc,
    m: uh,
    M: fh,
    p: jc,
    q: Bc,
    Q: Xa,
    s: _a,
    S: ch,
    u: lh,
    U: sh,
    V: hh,
    w: gh,
    W: ph,
    x: null,
    X: null,
    y: dh,
    Y: yh,
    Z: vh,
    "%": Ga
  }, x = {
    a: Y,
    A: E,
    b: W,
    B: D,
    c: R,
    d: Ba,
    e: Ba,
    f: k1,
    g: ja,
    G: La,
    H: za,
    I: za,
    j: U1,
    L: I1,
    m: D1,
    M: F1,
    p: F,
    q: C1,
    Q: q1,
    s: Y1,
    S: R1,
    u: E1,
    U: A1,
    V: T1,
    w: $1,
    W: N1,
    x: w,
    X: N,
    y: ja,
    Y: La,
    Z: P1,
    "%": O1
  };
  y.x = M(e, y), y.X = M(r, y), y.c = M(t, y), b.x = M(e, b), b.X = M(r, b), b.c = M(t, b);
  function M(T, O) {
    return function(L) {
      var $ = [], an = -1, G = 0, sn = T.length, hn, ut, Oo;
      for (L instanceof Date || (L = /* @__PURE__ */ new Date(+L)); ++an < sn; )
        T.charCodeAt(an) === 37 && ($.push(T.slice(G, an)), (ut = Ya[hn = T.charAt(++an)]) != null ? hn = T.charAt(++an) : ut = hn === "e" ? " " : "0", (Oo = O[hn]) && (hn = Oo(L, ut)), $.push(hn), G = an + 1);
      return $.push(T.slice(G, an)), $.join("");
    };
  }
  function A(T, O) {
    return function(L) {
      var $ = ee(1900, void 0, 1), an = P($, T, L += "", 0), G, sn;
      if (an != L.length) return null;
      if ("Q" in $) return new Date($.Q);
      if ("s" in $) return new Date($.s * 1e3 + ("L" in $ ? $.L : 0));
      if (O && !("Z" in $) && ($.Z = 0), "p" in $ && ($.H = $.H % 12 + $.p * 12), $.m === void 0 && ($.m = "q" in $ ? $.q : 0), "V" in $) {
        if ($.V < 1 || $.V > 53) return null;
        "w" in $ || ($.w = 1), "Z" in $ ? (G = ci(ee($.y, 0, 1)), sn = G.getUTCDay(), G = sn > 4 || sn === 0 ? xr.ceil(G) : xr(G), G = Kn.offset(G, ($.V - 1) * 7), $.y = G.getUTCFullYear(), $.m = G.getUTCMonth(), $.d = G.getUTCDate() + ($.w + 6) % 7) : (G = fi(ee($.y, 0, 1)), sn = G.getDay(), G = sn > 4 || sn === 0 ? Sr.ceil(G) : Sr(G), G = Gn.offset(G, ($.V - 1) * 7), $.y = G.getFullYear(), $.m = G.getMonth(), $.d = G.getDate() + ($.w + 6) % 7);
      } else ("W" in $ || "U" in $) && ("w" in $ || ($.w = "u" in $ ? $.u % 7 : "W" in $ ? 1 : 0), sn = "Z" in $ ? ci(ee($.y, 0, 1)).getUTCDay() : fi(ee($.y, 0, 1)).getDay(), $.m = 0, $.d = "W" in $ ? ($.w + 6) % 7 + $.W * 7 - (sn + 5) % 7 : $.w + $.U * 7 - (sn + 6) % 7);
      return "Z" in $ ? ($.H += $.Z / 100 | 0, $.M += $.Z % 100, ci($)) : fi($);
    };
  }
  function P(T, O, L, $) {
    for (var an = 0, G = O.length, sn = L.length, hn, ut; an < G; ) {
      if ($ >= sn) return -1;
      if (hn = O.charCodeAt(an++), hn === 37) {
        if (hn = O.charAt(an++), ut = x[hn in Ya ? O.charAt(an++) : hn], !ut || ($ = ut(T, L, $)) < 0) return -1;
      } else if (hn != L.charCodeAt($++))
        return -1;
    }
    return $;
  }
  function F(T, O, L) {
    var $ = f.exec(O.slice(L));
    return $ ? (T.p = l.get($[0].toLowerCase()), L + $[0].length) : -1;
  }
  function Y(T, O, L) {
    var $ = g.exec(O.slice(L));
    return $ ? (T.w = p.get($[0].toLowerCase()), L + $[0].length) : -1;
  }
  function E(T, O, L) {
    var $ = s.exec(O.slice(L));
    return $ ? (T.w = h.get($[0].toLowerCase()), L + $[0].length) : -1;
  }
  function W(T, O, L) {
    var $ = v.exec(O.slice(L));
    return $ ? (T.m = S.get($[0].toLowerCase()), L + $[0].length) : -1;
  }
  function D(T, O, L) {
    var $ = d.exec(O.slice(L));
    return $ ? (T.m = m.get($[0].toLowerCase()), L + $[0].length) : -1;
  }
  function R(T, O, L) {
    return P(T, t, O, L);
  }
  function w(T, O, L) {
    return P(T, e, O, L);
  }
  function N(T, O, L) {
    return P(T, r, O, L);
  }
  function z(T) {
    return a[T.getDay()];
  }
  function Z(T) {
    return o[T.getDay()];
  }
  function X(T) {
    return c[T.getMonth()];
  }
  function at(T) {
    return u[T.getMonth()];
  }
  function Sn(T) {
    return i[+(T.getHours() >= 12)];
  }
  function Yn(T) {
    return 1 + ~~(T.getMonth() / 3);
  }
  function xn(T) {
    return a[T.getUTCDay()];
  }
  function Et(T) {
    return o[T.getUTCDay()];
  }
  function Jn(T) {
    return c[T.getUTCMonth()];
  }
  function Lc(T) {
    return u[T.getUTCMonth()];
  }
  function jc(T) {
    return i[+(T.getUTCHours() >= 12)];
  }
  function Bc(T) {
    return 1 + ~~(T.getUTCMonth() / 3);
  }
  return {
    format: function(T) {
      var O = M(T += "", y);
      return O.toString = function() {
        return T;
      }, O;
    },
    parse: function(T) {
      var O = A(T += "", !1);
      return O.toString = function() {
        return T;
      }, O;
    },
    utcFormat: function(T) {
      var O = M(T += "", b);
      return O.toString = function() {
        return T;
      }, O;
    },
    utcParse: function(T) {
      var O = A(T += "", !0);
      return O.toString = function() {
        return T;
      }, O;
    }
  };
}
var Ya = { "-": "", _: " ", 0: "0" }, en = /^\s*\d+/, w1 = /^%/, S1 = /[\\^$*+?|[\]().{}]/g;
function j(n, t, e) {
  var r = n < 0 ? "-" : "", i = (r ? -n : n) + "", o = i.length;
  return r + (o < e ? new Array(e - o + 1).join(t) + i : i);
}
function x1(n) {
  return n.replace(S1, "\\$&");
}
function re(n) {
  return new RegExp("^(?:" + n.map(x1).join("|") + ")", "i");
}
function ie(n) {
  return new Map(n.map((t, e) => [t.toLowerCase(), e]));
}
function $1(n, t, e) {
  var r = en.exec(t.slice(e, e + 1));
  return r ? (n.w = +r[0], e + r[0].length) : -1;
}
function E1(n, t, e) {
  var r = en.exec(t.slice(e, e + 1));
  return r ? (n.u = +r[0], e + r[0].length) : -1;
}
function A1(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.U = +r[0], e + r[0].length) : -1;
}
function T1(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.V = +r[0], e + r[0].length) : -1;
}
function N1(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.W = +r[0], e + r[0].length) : -1;
}
function La(n, t, e) {
  var r = en.exec(t.slice(e, e + 4));
  return r ? (n.y = +r[0], e + r[0].length) : -1;
}
function ja(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.y = +r[0] + (+r[0] > 68 ? 1900 : 2e3), e + r[0].length) : -1;
}
function P1(n, t, e) {
  var r = /^(Z)|([+-]\d\d)(?::?(\d\d))?/.exec(t.slice(e, e + 6));
  return r ? (n.Z = r[1] ? 0 : -(r[2] + (r[3] || "00")), e + r[0].length) : -1;
}
function C1(n, t, e) {
  var r = en.exec(t.slice(e, e + 1));
  return r ? (n.q = r[0] * 3 - 3, e + r[0].length) : -1;
}
function D1(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.m = r[0] - 1, e + r[0].length) : -1;
}
function Ba(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.d = +r[0], e + r[0].length) : -1;
}
function U1(n, t, e) {
  var r = en.exec(t.slice(e, e + 3));
  return r ? (n.m = 0, n.d = +r[0], e + r[0].length) : -1;
}
function za(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.H = +r[0], e + r[0].length) : -1;
}
function F1(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.M = +r[0], e + r[0].length) : -1;
}
function R1(n, t, e) {
  var r = en.exec(t.slice(e, e + 2));
  return r ? (n.S = +r[0], e + r[0].length) : -1;
}
function I1(n, t, e) {
  var r = en.exec(t.slice(e, e + 3));
  return r ? (n.L = +r[0], e + r[0].length) : -1;
}
function k1(n, t, e) {
  var r = en.exec(t.slice(e, e + 6));
  return r ? (n.L = Math.floor(r[0] / 1e3), e + r[0].length) : -1;
}
function O1(n, t, e) {
  var r = w1.exec(t.slice(e, e + 1));
  return r ? e + r[0].length : -1;
}
function q1(n, t, e) {
  var r = en.exec(t.slice(e));
  return r ? (n.Q = +r[0], e + r[0].length) : -1;
}
function Y1(n, t, e) {
  var r = en.exec(t.slice(e));
  return r ? (n.s = +r[0], e + r[0].length) : -1;
}
function Ha(n, t) {
  return j(n.getDate(), t, 2);
}
function L1(n, t) {
  return j(n.getHours(), t, 2);
}
function j1(n, t) {
  return j(n.getHours() % 12 || 12, t, 2);
}
function B1(n, t) {
  return j(1 + Gn.count(Un(n), n), t, 3);
}
function ac(n, t) {
  return j(n.getMilliseconds(), t, 3);
}
function z1(n, t) {
  return ac(n, t) + "000";
}
function H1(n, t) {
  return j(n.getMonth() + 1, t, 2);
}
function W1(n, t) {
  return j(n.getMinutes(), t, 2);
}
function G1(n, t) {
  return j(n.getSeconds(), t, 2);
}
function X1(n) {
  var t = n.getDay();
  return t === 0 ? 7 : t;
}
function _1(n, t) {
  return j(Zt.count(Un(n) - 1, n), t, 2);
}
function uc(n) {
  var t = n.getDay();
  return t >= 4 || t === 0 ? jt(n) : jt.ceil(n);
}
function V1(n, t) {
  return n = uc(n), j(jt.count(Un(n), n) + (Un(n).getDay() === 4), t, 2);
}
function Z1(n) {
  return n.getDay();
}
function Q1(n, t) {
  return j(Sr.count(Un(n) - 1, n), t, 2);
}
function J1(n, t) {
  return j(n.getFullYear() % 100, t, 2);
}
function K1(n, t) {
  return n = uc(n), j(n.getFullYear() % 100, t, 2);
}
function nh(n, t) {
  return j(n.getFullYear() % 1e4, t, 4);
}
function th(n, t) {
  var e = n.getDay();
  return n = e >= 4 || e === 0 ? jt(n) : jt.ceil(n), j(n.getFullYear() % 1e4, t, 4);
}
function eh(n) {
  var t = n.getTimezoneOffset();
  return (t > 0 ? "-" : (t *= -1, "+")) + j(t / 60 | 0, "0", 2) + j(t % 60, "0", 2);
}
function Wa(n, t) {
  return j(n.getUTCDate(), t, 2);
}
function rh(n, t) {
  return j(n.getUTCHours(), t, 2);
}
function ih(n, t) {
  return j(n.getUTCHours() % 12 || 12, t, 2);
}
function oh(n, t) {
  return j(1 + Kn.count(Fn(n), n), t, 3);
}
function fc(n, t) {
  return j(n.getUTCMilliseconds(), t, 3);
}
function ah(n, t) {
  return fc(n, t) + "000";
}
function uh(n, t) {
  return j(n.getUTCMonth() + 1, t, 2);
}
function fh(n, t) {
  return j(n.getUTCMinutes(), t, 2);
}
function ch(n, t) {
  return j(n.getUTCSeconds(), t, 2);
}
function lh(n) {
  var t = n.getUTCDay();
  return t === 0 ? 7 : t;
}
function sh(n, t) {
  return j(Qt.count(Fn(n) - 1, n), t, 2);
}
function cc(n) {
  var t = n.getUTCDay();
  return t >= 4 || t === 0 ? Bt(n) : Bt.ceil(n);
}
function hh(n, t) {
  return n = cc(n), j(Bt.count(Fn(n), n) + (Fn(n).getUTCDay() === 4), t, 2);
}
function gh(n) {
  return n.getUTCDay();
}
function ph(n, t) {
  return j(xr.count(Fn(n) - 1, n), t, 2);
}
function dh(n, t) {
  return j(n.getUTCFullYear() % 100, t, 2);
}
function mh(n, t) {
  return n = cc(n), j(n.getUTCFullYear() % 100, t, 2);
}
function yh(n, t) {
  return j(n.getUTCFullYear() % 1e4, t, 4);
}
function bh(n, t) {
  var e = n.getUTCDay();
  return n = e >= 4 || e === 0 ? Bt(n) : Bt.ceil(n), j(n.getUTCFullYear() % 1e4, t, 4);
}
function vh() {
  return "+0000";
}
function Ga() {
  return "%";
}
function Xa(n) {
  return +n;
}
function _a(n) {
  return Math.floor(+n / 1e3);
}
var At, lc, Mh, sc, wh;
Sh({
  dateTime: "%x, %X",
  date: "%-m/%-d/%Y",
  time: "%-I:%M:%S %p",
  periods: ["AM", "PM"],
  days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  shortDays: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  shortMonths: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
});
function Sh(n) {
  return At = M1(n), lc = At.format, Mh = At.parse, sc = At.utcFormat, wh = At.utcParse, At;
}
function xh(n) {
  return new Date(n);
}
function $h(n) {
  return n instanceof Date ? +n : +/* @__PURE__ */ new Date(+n);
}
function Mo(n, t, e, r, i, o, a, u, c, f) {
  var l = Gf(), s = l.invert, h = l.domain, g = f(".%L"), p = f(":%S"), d = f("%I:%M"), m = f("%I %p"), v = f("%a %d"), S = f("%b %d"), y = f("%B"), b = f("%Y");
  function x(M) {
    return (c(M) < M ? g : u(M) < M ? p : a(M) < M ? d : o(M) < M ? m : r(M) < M ? i(M) < M ? v : S : e(M) < M ? y : b)(M);
  }
  return l.invert = function(M) {
    return new Date(s(M));
  }, l.domain = function(M) {
    return arguments.length ? h(Array.from(M, $h)) : h().map(xh);
  }, l.ticks = function(M) {
    var A = h();
    return n(A[0], A[A.length - 1], M ?? 10);
  }, l.tickFormat = function(M, A) {
    return A == null ? x : f(A);
  }, l.nice = function(M) {
    var A = h();
    return (!M || typeof M.range != "function") && (M = t(A[0], A[A.length - 1], M ?? 10)), M ? h(Jf(A, M)) : l;
  }, l.copy = function() {
    return Oe(l, Mo(n, t, e, r, i, o, a, u, c, f));
  }, l;
}
function Eh() {
  return On.apply(Mo(b1, v1, Un, Pe, Zt, Gn, Br, Lr, Hn, lc).domain([new Date(2e3, 0, 1), new Date(2e3, 0, 2)]), arguments);
}
function Ah() {
  return On.apply(Mo(m1, y1, Fn, Ce, Qt, Kn, zr, jr, Hn, sc).domain([Date.UTC(2e3, 0, 1), Date.UTC(2e3, 0, 2)]), arguments);
}
function Hr() {
  var n = 0, t = 1, e, r, i, o, a = fn, u = !1, c;
  function f(s) {
    return s == null || isNaN(s = +s) ? c : a(i === 0 ? 0.5 : (s = (o(s) - e) * i, u ? Math.max(0, Math.min(1, s)) : s));
  }
  f.domain = function(s) {
    return arguments.length ? ([n, t] = s, e = o(n = +n), r = o(t = +t), i = e === r ? 0 : 1 / (r - e), f) : [n, t];
  }, f.clamp = function(s) {
    return arguments.length ? (u = !!s, f) : u;
  }, f.interpolator = function(s) {
    return arguments.length ? (a = s, f) : a;
  };
  function l(s) {
    return function(h) {
      var g, p;
      return arguments.length ? ([g, p] = h, a = s(g, p), f) : [a(0), a(1)];
    };
  }
  return f.range = l(Mt), f.rangeRound = l(qr), f.unknown = function(s) {
    return arguments.length ? (c = s, f) : c;
  }, function(s) {
    return o = s, e = s(n), r = s(t), i = e === r ? 0 : 1 / (r - e), f;
  };
}
function ot(n, t) {
  return t.domain(n.domain()).interpolator(n.interpolator()).clamp(n.clamp()).unknown(n.unknown());
}
function wo() {
  var n = wt(Hr()(fn));
  return n.copy = function() {
    return ot(n, wo());
  }, rt.apply(n, arguments);
}
function hc() {
  var n = po(Hr()).domain([1, 10]);
  return n.copy = function() {
    return ot(n, hc()).base(n.base());
  }, rt.apply(n, arguments);
}
function gc() {
  var n = mo(Hr());
  return n.copy = function() {
    return ot(n, gc()).constant(n.constant());
  }, rt.apply(n, arguments);
}
function So() {
  var n = yo(Hr());
  return n.copy = function() {
    return ot(n, So()).exponent(n.exponent());
  }, rt.apply(n, arguments);
}
function Th() {
  return So.apply(null, arguments).exponent(0.5);
}
function Wr() {
  var n = 0, t = 0.5, e = 1, r = 1, i, o, a, u, c, f = fn, l, s = !1, h;
  function g(d) {
    return isNaN(d = +d) ? h : (d = 0.5 + ((d = +l(d)) - o) * (r * d < r * o ? u : c), f(s ? Math.max(0, Math.min(1, d)) : d));
  }
  g.domain = function(d) {
    return arguments.length ? ([n, t, e] = d, i = l(n = +n), o = l(t = +t), a = l(e = +e), u = i === o ? 0 : 0.5 / (o - i), c = o === a ? 0 : 0.5 / (a - o), r = o < i ? -1 : 1, g) : [n, t, e];
  }, g.clamp = function(d) {
    return arguments.length ? (s = !!d, g) : s;
  }, g.interpolator = function(d) {
    return arguments.length ? (f = d, g) : f;
  };
  function p(d) {
    return function(m) {
      var v, S, y;
      return arguments.length ? ([v, S, y] = m, f = so(d, [v, S, y]), g) : [f(0), f(0.5), f(1)];
    };
  }
  return g.range = p(Mt), g.rangeRound = p(qr), g.unknown = function(d) {
    return arguments.length ? (h = d, g) : h;
  }, function(d) {
    return l = d, i = d(n), o = d(t), a = d(e), u = i === o ? 0 : 0.5 / (o - i), c = o === a ? 0 : 0.5 / (a - o), r = o < i ? -1 : 1, g;
  };
}
function pc() {
  var n = wt(Wr()(fn));
  return n.copy = function() {
    return ot(n, pc());
  }, rt.apply(n, arguments);
}
function dc() {
  var n = po(Wr()).domain([0.1, 1, 10]);
  return n.copy = function() {
    return ot(n, dc()).base(n.base());
  }, rt.apply(n, arguments);
}
function mc() {
  var n = mo(Wr());
  return n.copy = function() {
    return ot(n, mc()).constant(n.constant());
  }, rt.apply(n, arguments);
}
function xo() {
  var n = yo(Wr());
  return n.copy = function() {
    return ot(n, xo()).exponent(n.exponent());
  }, rt.apply(n, arguments);
}
function Nh() {
  return xo.apply(null, arguments).exponent(0.5);
}
function qn(n) {
  for (var t = n.length / 6 | 0, e = new Array(t), r = 0; r < t; ) e[r] = "#" + n.slice(r * 6, ++r * 6);
  return e;
}
const Ph = qn("1f77b4ff7f0e2ca02cd627289467bd8c564be377c27f7f7fbcbd2217becf"), Ch = qn("7fc97fbeaed4fdc086ffff99386cb0f0027fbf5b17666666"), Dh = qn("1b9e77d95f027570b3e7298a66a61ee6ab02a6761d666666"), Uh = qn("4269d0efb118ff725c6cc5b03ca951ff8ab7a463f297bbf59c6b4e9498a0"), Fh = qn("a6cee31f78b4b2df8a33a02cfb9a99e31a1cfdbf6fff7f00cab2d66a3d9affff99b15928"), Rh = qn("fbb4aeb3cde3ccebc5decbe4fed9a6ffffcce5d8bdfddaecf2f2f2"), Ih = qn("b3e2cdfdcdaccbd5e8f4cae4e6f5c9fff2aef1e2cccccccc"), kh = qn("e41a1c377eb84daf4a984ea3ff7f00ffff33a65628f781bf999999"), Oh = qn("66c2a5fc8d628da0cbe78ac3a6d854ffd92fe5c494b3b3b3"), qh = qn("8dd3c7ffffb3bebadafb807280b1d3fdb462b3de69fccde5d9d9d9bc80bdccebc5ffed6f"), cn = "year", An = "quarter", gn = "month", on = "week", Tn = "date", un = "day", Vn = "dayofyear", Rn = "hours", In = "minutes", Zn = "seconds", Qn = "milliseconds", Yh = [cn, An, gn, on, Tn, un, Vn, Rn, In, Zn, Qn], li = Yh.reduce((n, t, e) => (n[t] = 1 + e, n), {});
function Lh(n) {
  const t = It(n).slice(), e = {};
  return t.length || st("Missing time unit."), t.forEach((i) => {
    ft(li, i) ? e[i] = 1 : st(`Invalid time unit: ${i}.`);
  }), (e[on] || e[un] ? 1 : 0) + (e[An] || e[gn] || e[Tn] ? 1 : 0) + (e[Vn] ? 1 : 0) > 1 && st(`Incompatible time units: ${n}`), t.sort((i, o) => li[i] - li[o]), t;
}
const jh = {
  [cn]: "%Y ",
  [An]: "Q%q ",
  [gn]: "%b ",
  [Tn]: "%d ",
  [on]: "W%U ",
  [un]: "%a ",
  [Vn]: "%j ",
  [Rn]: "%H:00",
  [In]: "00:%M",
  [Zn]: ":%S",
  [Qn]: ".%L",
  [`${cn}-${gn}`]: "%Y-%m ",
  [`${cn}-${gn}-${Tn}`]: "%Y-%m-%d ",
  [`${Rn}-${In}`]: "%H:%M"
};
function Vd(n, t) {
  const e = wu({}, jh, t), r = Lh(n), i = r.length;
  let o = "", a = 0, u, c;
  for (a = 0; a < i; )
    for (u = r.length; u > a; --u)
      if (c = r.slice(a, u).join("-"), e[c] != null) {
        o += e[c], a = u;
        break;
      }
  return o.trim();
}
const ct = /* @__PURE__ */ new Date();
function $o(n) {
  return ct.setFullYear(n), ct.setMonth(0), ct.setDate(1), ct.setHours(0, 0, 0, 0), ct;
}
function Zd(n) {
  return yc(new Date(n));
}
function Qd(n) {
  return Hi(new Date(n));
}
function yc(n) {
  return Gn.count($o(n.getFullYear()) - 1, n);
}
function Hi(n) {
  return Zt.count($o(n.getFullYear()) - 1, n);
}
function Wi(n) {
  return $o(n).getDay();
}
function Bh(n, t, e, r, i, o, a) {
  if (0 <= n && n < 100) {
    const u = new Date(-1, t, e, r, i, o, a);
    return u.setFullYear(n), u;
  }
  return new Date(n, t, e, r, i, o, a);
}
function Jd(n) {
  return bc(new Date(n));
}
function Kd(n) {
  return Gi(new Date(n));
}
function bc(n) {
  const t = Date.UTC(n.getUTCFullYear(), 0, 1);
  return Kn.count(t - 1, n);
}
function Gi(n) {
  const t = Date.UTC(n.getUTCFullYear(), 0, 1);
  return Qt.count(t - 1, n);
}
function Xi(n) {
  return ct.setTime(Date.UTC(n, 0, 1)), ct.getUTCDay();
}
function zh(n, t, e, r, i, o, a) {
  if (0 <= n && n < 100) {
    const u = new Date(Date.UTC(-1, t, e, r, i, o, a));
    return u.setUTCFullYear(e.y), u;
  }
  return new Date(Date.UTC(n, t, e, r, i, o, a));
}
function vc(n, t, e, r, i) {
  const o = t || 1, a = pn(n), u = (v, S, y) => (y = y || v, Hh(e[y], r[y], v === a && o, S)), c = /* @__PURE__ */ new Date(), f = $u(n), l = f[cn] ? u(cn) : Mu(2012), s = f[gn] ? u(gn) : f[An] ? u(An) : Kt, h = f[on] && f[un] ? u(un, 1, on + un) : f[on] ? u(on, 1) : f[un] ? u(un, 1) : f[Tn] ? u(Tn, 1) : f[Vn] ? u(Vn, 1) : Gc, g = f[Rn] ? u(Rn) : Kt, p = f[In] ? u(In) : Kt, d = f[Zn] ? u(Zn) : Kt, m = f[Qn] ? u(Qn) : Kt;
  return function(v) {
    c.setTime(+v);
    const S = l(c);
    return i(S, s(c), h(c, S), g(c), p(c), d(c), m(c));
  };
}
function Hh(n, t, e, r) {
  const i = e <= 1 ? n : r ? (o, a) => r + e * Math.floor((n(o, a) - r) / e) : (o, a) => e * Math.floor(n(o, a) / e);
  return t ? (o, a) => t(i(o, a), a) : i;
}
function zt(n, t, e) {
  return t + n * 7 - (e + 6) % 7;
}
const Wh = {
  [cn]: (n) => n.getFullYear(),
  [An]: (n) => Math.floor(n.getMonth() / 3),
  [gn]: (n) => n.getMonth(),
  [Tn]: (n) => n.getDate(),
  [Rn]: (n) => n.getHours(),
  [In]: (n) => n.getMinutes(),
  [Zn]: (n) => n.getSeconds(),
  [Qn]: (n) => n.getMilliseconds(),
  [Vn]: (n) => yc(n),
  [on]: (n) => Hi(n),
  [on + un]: (n, t) => zt(Hi(n), n.getDay(), Wi(t)),
  [un]: (n, t) => zt(1, n.getDay(), Wi(t))
}, Gh = {
  [An]: (n) => 3 * n,
  [on]: (n, t) => zt(n, 0, Wi(t))
};
function n2(n, t) {
  return vc(n, t || 1, Wh, Gh, Bh);
}
const Xh = {
  [cn]: (n) => n.getUTCFullYear(),
  [An]: (n) => Math.floor(n.getUTCMonth() / 3),
  [gn]: (n) => n.getUTCMonth(),
  [Tn]: (n) => n.getUTCDate(),
  [Rn]: (n) => n.getUTCHours(),
  [In]: (n) => n.getUTCMinutes(),
  [Zn]: (n) => n.getUTCSeconds(),
  [Qn]: (n) => n.getUTCMilliseconds(),
  [Vn]: (n) => bc(n),
  [on]: (n) => Gi(n),
  [un]: (n, t) => zt(1, n.getUTCDay(), Xi(t)),
  [on + un]: (n, t) => zt(Gi(n), n.getUTCDay(), Xi(t))
}, _h = {
  [An]: (n) => 3 * n,
  [on]: (n, t) => zt(n, 0, Xi(t))
};
function t2(n, t) {
  return vc(n, t || 1, Xh, _h, zh);
}
const Vh = {
  [cn]: Un,
  [An]: Pe.every(3),
  [gn]: Pe,
  [on]: Zt,
  [Tn]: Gn,
  [un]: Gn,
  [Vn]: Gn,
  [Rn]: Br,
  [In]: Lr,
  [Zn]: Hn,
  [Qn]: Lt
}, Zh = {
  [cn]: Fn,
  [An]: Ce.every(3),
  [gn]: Ce,
  [on]: Qt,
  [Tn]: Kn,
  [un]: Kn,
  [Vn]: Kn,
  [Rn]: zr,
  [In]: jr,
  [Zn]: Hn,
  [Qn]: Lt
};
function Eo(n) {
  return Vh[n];
}
function Ao(n) {
  return Zh[n];
}
function Mc(n, t, e) {
  return n ? n.offset(t, e) : void 0;
}
function e2(n, t, e) {
  return Mc(Eo(n), t, e);
}
function r2(n, t, e) {
  return Mc(Ao(n), t, e);
}
function wc(n, t, e, r) {
  return n ? n.range(t, e, r) : void 0;
}
function i2(n, t, e, r) {
  return wc(Eo(n), t, e, r);
}
function o2(n, t, e, r) {
  return wc(Ao(n), t, e, r);
}
const se = 1e3, he = se * 60, ge = he * 60, Gr = ge * 24, Qh = Gr * 7, Va = Gr * 30, _i = Gr * 365, Sc = [cn, gn, Tn, Rn, In, Zn, Qn], pe = Sc.slice(0, -1), de = pe.slice(0, -1), me = de.slice(0, -1), Jh = me.slice(0, -1), Kh = [cn, on], Za = [cn, gn], xc = [cn], oe = [[pe, 1, se], [pe, 5, 5 * se], [pe, 15, 15 * se], [pe, 30, 30 * se], [de, 1, he], [de, 5, 5 * he], [de, 15, 15 * he], [de, 30, 30 * he], [me, 1, ge], [me, 3, 3 * ge], [me, 6, 6 * ge], [me, 12, 12 * ge], [Jh, 1, Gr], [Kh, 1, Qh], [Za, 1, Va], [Za, 3, 3 * Va], [xc, 1, _i]];
function a2(n) {
  const t = n.extent, e = n.maxbins || 40, r = Math.abs(xu(t)) / e;
  let i = Cr((u) => u[2]).right(oe, r), o, a;
  return i === oe.length ? (o = xc, a = we(t[0] / _i, t[1] / _i, e)) : i ? (i = oe[r / oe[i - 1][2] < oe[i][2] / r ? i - 1 : i], o = i[0], a = i[1]) : (o = Sc, a = Math.max(we(t[0], t[1], e), 1)), {
    units: o,
    step: a
  };
}
function ng(n, t, e) {
  const r = n - t + e * 2;
  return n ? r > 0 ? r : 1 : 0;
}
const tg = "identity", To = "linear", tt = "log", No = "pow", Po = "sqrt", Co = "symlog", Ht = "time", Wt = "utc", Jt = "sequential", qe = "diverging", De = "quantile", Do = "quantize", Uo = "threshold", eg = "ordinal", rg = "point", ig = "band", og = "bin-ordinal", J = "continuous", Ye = "discrete", Le = "discretizing", wn = "interpolating", Fo = "temporal";
function ag(n) {
  return function(t) {
    let e = t[0], r = t[1], i;
    return r < e && (i = e, e = r, r = i), [n.invert(e), n.invert(r)];
  };
}
function ug(n) {
  return function(t) {
    const e = n.range();
    let r = t[0], i = t[1], o = -1, a, u, c, f;
    for (i < r && (u = r, r = i, i = u), c = 0, f = e.length; c < f; ++c)
      e[c] >= r && e[c] <= i && (o < 0 && (o = c), a = c);
    if (!(o < 0))
      return r = n.invertExtent(e[o]), i = n.invertExtent(e[a]), [r[0] === void 0 ? r[1] : r[0], i[1] === void 0 ? i[0] : i[1]];
  };
}
function Ro() {
  const n = ao().unknown(void 0), t = n.domain, e = n.range;
  let r = [0, 1], i, o, a = !1, u = 0, c = 0, f = 0.5;
  delete n.unknown;
  function l() {
    const s = t().length, h = r[1] < r[0], g = r[1 - h], p = ng(s, u, c);
    let d = r[h - 0];
    i = (g - d) / (p || 1), a && (i = Math.floor(i)), d += (g - d - i * (s - u)) * f, o = i * (1 - u), a && (d = Math.round(d), o = Math.round(o));
    const m = Al(s).map((v) => d + i * v);
    return e(h ? m.reverse() : m);
  }
  return n.domain = function(s) {
    return arguments.length ? (t(s), l()) : t();
  }, n.range = function(s) {
    return arguments.length ? (r = [+s[0], +s[1]], l()) : r.slice();
  }, n.rangeRound = function(s) {
    return r = [+s[0], +s[1]], a = !0, l();
  }, n.bandwidth = function() {
    return o;
  }, n.step = function() {
    return i;
  }, n.round = function(s) {
    return arguments.length ? (a = !!s, l()) : a;
  }, n.padding = function(s) {
    return arguments.length ? (c = Math.max(0, Math.min(1, s)), u = c, l()) : u;
  }, n.paddingInner = function(s) {
    return arguments.length ? (u = Math.max(0, Math.min(1, s)), l()) : u;
  }, n.paddingOuter = function(s) {
    return arguments.length ? (c = Math.max(0, Math.min(1, s)), l()) : c;
  }, n.align = function(s) {
    return arguments.length ? (f = Math.max(0, Math.min(1, s)), l()) : f;
  }, n.invertRange = function(s) {
    if (s[0] == null || s[1] == null) return;
    const h = r[1] < r[0], g = h ? e().reverse() : e(), p = g.length - 1;
    let d = +s[0], m = +s[1], v, S, y;
    if (!(d !== d || m !== m) && (m < d && (y = d, d = m, m = y), !(m < g[0] || d > r[1 - h])))
      return v = Math.max(0, mt(g, d) - 1), S = d === m ? v : mt(g, m) - 1, d - g[v] > o + 1e-10 && ++v, h && (y = v, v = p - S, S = p - y), v > S ? void 0 : t().slice(v, S + 1);
  }, n.invert = function(s) {
    const h = n.invertRange([s, s]);
    return h && h[0];
  }, n.copy = function() {
    return Ro().domain(t()).range(r).round(a).paddingInner(u).paddingOuter(c).align(f);
  }, l();
}
function $c(n) {
  const t = n.copy;
  return n.padding = n.paddingOuter, delete n.paddingInner, n.copy = function() {
    return $c(t());
  }, n;
}
function fg() {
  return $c(Ro().paddingInner(1));
}
var cg = Array.prototype.map;
function lg(n) {
  return cg.call(n, Qi);
}
const sg = Array.prototype.slice;
function Ec() {
  let n = [], t = [];
  function e(r) {
    return r == null || r !== r ? void 0 : t[(mt(n, r) - 1) % t.length];
  }
  return e.domain = function(r) {
    return arguments.length ? (n = lg(r), e) : n.slice();
  }, e.range = function(r) {
    return arguments.length ? (t = sg.call(r), e) : t.slice();
  }, e.tickFormat = function(r, i) {
    return Vf(n[0], pn(n), r ?? 10, i);
  }, e.copy = function() {
    return Ec().domain(e.domain()).range(e.range());
  }, e;
}
const $r = /* @__PURE__ */ new Map(), Ac = Symbol("vega_scale");
function Tc(n) {
  return n[Ac] = !0, n;
}
function u2(n) {
  return n && n[Ac] === !0;
}
function hg(n, t, e) {
  const r = function() {
    const o = t();
    return o.invertRange || (o.invertRange = o.invert ? ag(o) : o.invertExtent ? ug(o) : void 0), o.type = n, Tc(o);
  };
  return r.metadata = $u(It(e)), r;
}
function H(n, t, e) {
  return arguments.length > 1 ? ($r.set(n, hg(n, t, e)), this) : gg(n) ? $r.get(n) : void 0;
}
H(tg, Qf);
H(To, Zf, J);
H(tt, Kf, [J, tt]);
H(No, bo, J);
H(Po, u1, J);
H(Co, nc, J);
H(Ht, Eh, [J, Fo]);
H(Wt, Ah, [J, Fo]);
H(Jt, wo, [J, wn]);
H(`${Jt}-${To}`, wo, [J, wn]);
H(`${Jt}-${tt}`, hc, [J, wn, tt]);
H(`${Jt}-${No}`, So, [J, wn]);
H(`${Jt}-${Po}`, Th, [J, wn]);
H(`${Jt}-${Co}`, gc, [J, wn]);
H(`${qe}-${To}`, pc, [J, wn]);
H(`${qe}-${tt}`, dc, [J, wn, tt]);
H(`${qe}-${No}`, xo, [J, wn]);
H(`${qe}-${Po}`, Nh, [J, wn]);
H(`${qe}-${Co}`, mc, [J, wn]);
H(De, tc, [Le, De]);
H(Do, ec, Le);
H(Uo, rc, Le);
H(og, Ec, [Ye, Le]);
H(eg, ao, Ye);
H(ig, Ro, Ye);
H(rg, fg, Ye);
function gg(n) {
  return $r.has(n);
}
function $t(n, t) {
  const e = $r.get(n);
  return e && e.metadata[t];
}
function f2(n) {
  return $t(n, J);
}
function pg(n) {
  return $t(n, Ye);
}
function dg(n) {
  return $t(n, Le);
}
function mg(n) {
  return $t(n, tt);
}
function yg(n) {
  return $t(n, Fo);
}
function c2(n) {
  return $t(n, wn);
}
function l2(n) {
  return $t(n, De);
}
const bg = ["clamp", "base", "constant", "exponent"];
function s2(n, t) {
  const e = t[0], r = pn(t) - e;
  return function(i) {
    return n(e + i * r);
  };
}
function vg(n, t, e) {
  return so(Mg(t || "rgb", e), n);
}
function h2(n, t) {
  const e = new Array(t), r = t + 1;
  for (let i = 0; i < t; ) e[i] = n(++i / r);
  return e;
}
function g2(n, t, e) {
  const r = e - t;
  let i, o, a;
  return !r || !Number.isFinite(r) ? Mu(0.5) : (i = (o = n.type).indexOf("-"), o = i < 0 ? o : o.slice(i + 1), a = H(o)().domain([t, e]).range([0, 1]), bg.forEach((u) => n[u] ? a[u](n[u]()) : 0), a);
}
function Mg(n, t) {
  const e = q0[wg(n)];
  return t != null && e && e.gamma ? e.gamma(t) : e;
}
function wg(n) {
  return "interpolate" + n.toLowerCase().split("-").map((t) => t[0].toUpperCase() + t.slice(1)).join("");
}
const Sg = {
  blues: "cfe1f2bed8eca8cee58fc1de74b2d75ba3cf4592c63181bd206fb2125ca40a4a90",
  greens: "d3eecdc0e6baabdda594d3917bc77d60ba6c46ab5e329a512089430e7735036429",
  greys: "e2e2e2d4d4d4c4c4c4b1b1b19d9d9d8888887575756262624d4d4d3535351e1e1e",
  oranges: "fdd8b3fdc998fdb87bfda55efc9244f87f2cf06b18e4580bd14904b93d029f3303",
  purples: "e2e1efd4d4e8c4c5e0b4b3d6a3a0cc928ec3827cb97566ae684ea25c3696501f8c",
  reds: "fdc9b4fcb49afc9e80fc8767fa7051f6573fec3f2fdc2a25c81b1db21218970b13",
  blueGreen: "d5efedc1e8e0a7ddd18bd2be70c6a958ba9144ad77319c5d2089460e7736036429",
  bluePurple: "ccddecbad0e4a8c2dd9ab0d4919cc98d85be8b6db28a55a6873c99822287730f71",
  greenBlue: "d3eecec5e8c3b1e1bb9bd8bb82cec269c2ca51b2cd3c9fc7288abd1675b10b60a1",
  orangeRed: "fddcaffdcf9bfdc18afdad77fb9562f67d53ee6545e24932d32d1ebf130da70403",
  purpleBlue: "dbdaebc8cee4b1c3de97b7d87bacd15b9fc93a90c01e7fb70b70ab056199045281",
  purpleBlueGreen: "dbd8eac8cee4b0c3de93b7d872acd1549fc83892bb1c88a3097f8702736b016353",
  purpleRed: "dcc9e2d3b3d7ce9eccd186c0da6bb2e14da0e23189d91e6fc61159ab07498f023a",
  redPurple: "fccfccfcbec0faa9b8f98faff571a5ec539ddb3695c41b8aa908808d0179700174",
  yellowGreen: "e4f4acd1eca0b9e2949ed68880c97c62bb6e47aa5e3297502083440e723b036034",
  yellowOrangeBrown: "feeaa1fedd84fecc63feb746fca031f68921eb7215db5e0bc54c05ab3d038f3204",
  yellowOrangeRed: "fee087fed16ffebd59fea849fd903efc7335f9522bee3423de1b20ca0b22af0225",
  blueOrange: "134b852f78b35da2cb9dcae1d2e5eff2f0ebfce0bafbbf74e8932fc5690d994a07",
  brownBlueGreen: "704108a0651ac79548e3c78af3e6c6eef1eac9e9e48ed1c74da79e187a72025147",
  purpleGreen: "5b1667834792a67fb6c9aed3e6d6e8eff0efd9efd5aedda971bb75368e490e5e29",
  purpleOrange: "4114696647968f83b7b9b4d6dadbebf3eeeafce0bafbbf74e8932fc5690d994a07",
  redBlue: "8c0d25bf363adf745ef4ae91fbdbc9f2efeed2e5ef9dcae15da2cb2f78b3134b85",
  redGrey: "8c0d25bf363adf745ef4ae91fcdccbfaf4f1e2e2e2c0c0c0969696646464343434",
  yellowGreenBlue: "eff9bddbf1b4bde5b594d5b969c5be45b4c22c9ec02182b82163aa23479c1c3185",
  redYellowBlue: "a50026d4322cf16e43fcac64fedd90faf8c1dcf1ecabd6e875abd04a74b4313695",
  redYellowGreen: "a50026d4322cf16e43fcac63fedd8df9f7aed7ee8ea4d86e64bc6122964f006837",
  pinkYellowGreen: "8e0152c0267edd72adf0b3d6faddedf5f3efe1f2cab6de8780bb474f9125276419",
  spectral: "9e0142d13c4bf0704afcac63fedd8dfbf8b0e0f3a1a9dda269bda94288b55e4fa2",
  viridis: "440154470e61481a6c482575472f7d443a834144873d4e8a39568c35608d31688e2d708e2a788e27818e23888e21918d1f988b1fa08822a8842ab07f35b77943bf7154c56866cc5d7ad1518fd744a5db36bcdf27d2e21be9e51afde725",
  magma: "0000040404130b0924150e3720114b2c11603b0f704a107957157e651a80721f817f24828c29819a2e80a8327db6377ac43c75d1426fde4968e95462f1605df76f5cfa7f5efc8f65fe9f6dfeaf78febf84fece91fddea0fcedaffcfdbf",
  inferno: "0000040403130c0826170c3b240c4f330a5f420a68500d6c5d126e6b176e781c6d86216b932667a12b62ae305cbb3755c73e4cd24644dd513ae65c30ed6925f3771af8850ffb9506fca50afcb519fac62df6d645f2e661f3f484fcffa4",
  plasma: "0d088723069033059742039d5002a25d01a66a00a87801a88405a7900da49c179ea72198b12a90ba3488c33d80cb4779d35171da5a69e16462e76e5bed7953f2834cf68f44fa9a3dfca636fdb32ffec029fcce25f9dc24f5ea27f0f921",
  cividis: "00205100235800265d002961012b65042e670831690d346b11366c16396d1c3c6e213f6e26426e2c456e31476e374a6e3c4d6e42506e47536d4c566d51586e555b6e5a5e6e5e616e62646f66676f6a6a706e6d717270717573727976737c79747f7c75827f758682768985778c8877908b78938e789691789a94789e9778a19b78a59e77a9a177aea575b2a874b6ab73bbaf71c0b26fc5b66dc9b96acebd68d3c065d8c462ddc85fe2cb5ce7cf58ebd355f0d652f3da4ff7de4cfae249fce647",
  rainbow: "6e40aa883eb1a43db3bf3cafd83fa4ee4395fe4b83ff576eff6659ff7847ff8c38f3a130e2b72fcfcc36bee044aff05b8ff4576ff65b52f6673af27828ea8d1ddfa319d0b81cbecb23abd82f96e03d82e14c6edb5a5dd0664dbf6e40aa",
  sinebow: "ff4040fc582af47218e78d0bd5a703bfbf00a7d5038de70b72f41858fc2a40ff402afc5818f4720be78d03d5a700bfbf03a7d50b8de71872f42a58fc4040ff582afc7218f48d0be7a703d5bf00bfd503a7e70b8df41872fc2a58ff4040",
  turbo: "23171b32204a3e2a71453493493eae4b49c54a53d7485ee44569ee4074f53c7ff8378af93295f72e9ff42ba9ef28b3e926bce125c5d925cdcf27d5c629dcbc2de3b232e9a738ee9d3ff39347f68950f9805afc7765fd6e70fe667cfd5e88fc5795fb51a1f84badf545b9f140c5ec3cd0e637dae034e4d931ecd12ef4c92bfac029ffb626ffad24ffa223ff9821ff8d1fff821dff771cfd6c1af76118f05616e84b14df4111d5380fcb2f0dc0260ab61f07ac1805a313029b0f00950c00910b00",
  browns: "eedbbdecca96e9b97ae4a865dc9856d18954c7784cc0673fb85536ad44339f3632",
  tealBlues: "bce4d89dd3d181c3cb65b3c245a2b9368fae347da0306a932c5985",
  teals: "bbdfdfa2d4d58ac9c975bcbb61b0af4da5a43799982b8b8c1e7f7f127273006667",
  warmGreys: "dcd4d0cec5c1c0b8b4b3aaa7a59c9998908c8b827f7e7673726866665c5a59504e",
  goldGreen: "f4d166d5ca60b6c35c98bb597cb25760a6564b9c533f8f4f33834a257740146c36",
  goldOrange: "f4d166f8be5cf8aa4cf5983bf3852aef701be2621fd65322c54923b142239e3a26",
  goldRed: "f4d166f6be59f9aa51fc964ef6834bee734ae56249db5247cf4244c43141b71d3e",
  lightGreyRed: "efe9e6e1dad7d5cbc8c8bdb9bbaea9cd967ddc7b43e15f19df4011dc000b",
  lightGreyTeal: "e4eaead6dcddc8ced2b7c2c7a6b4bc64b0bf22a6c32295c11f85be1876bc",
  lightMulti: "e0f1f2c4e9d0b0de9fd0e181f6e072f6c053f3993ef77440ef4a3c",
  lightOrange: "f2e7daf7d5baf9c499fab184fa9c73f68967ef7860e8645bde515bd43d5b",
  lightTealBlue: "e3e9e0c0dccf9aceca7abfc859afc0389fb9328dad2f7ca0276b95255988",
  darkBlue: "3232322d46681a5c930074af008cbf05a7ce25c0dd38daed50f3faffffff",
  darkGold: "3c3c3c584b37725e348c7631ae8b2bcfa424ecc31ef9de30fff184ffffff",
  darkGreen: "3a3a3a215748006f4d048942489e4276b340a6c63dd2d836ffeb2cffffaa",
  darkMulti: "3737371f5287197d8c29a86995ce3fffe800ffffff",
  darkRed: "3434347036339e3c38cc4037e75d1eec8620eeab29f0ce32ffeb2c"
}, xg = {
  accent: Ch,
  category10: Ph,
  category20: "1f77b4aec7e8ff7f0effbb782ca02c98df8ad62728ff98969467bdc5b0d58c564bc49c94e377c2f7b6d27f7f7fc7c7c7bcbd22dbdb8d17becf9edae5",
  category20b: "393b795254a36b6ecf9c9ede6379398ca252b5cf6bcedb9c8c6d31bd9e39e7ba52e7cb94843c39ad494ad6616be7969c7b4173a55194ce6dbdde9ed6",
  category20c: "3182bd6baed69ecae1c6dbefe6550dfd8d3cfdae6bfdd0a231a35474c476a1d99bc7e9c0756bb19e9ac8bcbddcdadaeb636363969696bdbdbdd9d9d9",
  dark2: Dh,
  observable10: Uh,
  paired: Fh,
  pastel1: Rh,
  pastel2: Ih,
  set1: kh,
  set2: Oh,
  set3: qh,
  tableau10: "4c78a8f58518e4575672b7b254a24beeca3bb279a2ff9da69d755dbab0ac",
  tableau20: "4c78a89ecae9f58518ffbf7954a24b88d27ab79a20f2cf5b43989483bcb6e45756ff9d9879706ebab0acd67195fcbfd2b279a2d6a5c99e765fd8b5a5"
};
function Nc(n) {
  if (Ue(n)) return n;
  const t = n.length / 6 | 0, e = new Array(t);
  for (let r = 0; r < t; )
    e[r] = "#" + n.slice(r * 6, ++r * 6);
  return e;
}
function Pc(n, t) {
  for (const e in n) $g(e, t(n[e]));
}
const Qa = {};
Pc(xg, Nc);
Pc(Sg, (n) => vg(Nc(n)));
function $g(n, t) {
  return n = n && n.toLowerCase(), arguments.length > 1 ? (Qa[n] = t, this) : Qa[n];
}
const Eg = "symbol", Ag = "discrete", p2 = "gradient", Tg = (n) => Ue(n) ? n.map((t) => String(t)) : String(n), Ng = (n, t) => n[1] - t[1], Pg = (n, t) => t[1] - n[1];
function d2(n, t, e) {
  let r;
  return Su(t) && (n.bins && (t = Math.max(t, n.bins.length)), e != null && (t = Math.min(t, Math.floor(xu(n.domain()) / e || 1) + 1))), er(t) && (r = t.step, t = t.interval), Ki(t) && (t = n.type === Ht ? Eo(t) : n.type == Wt ? Ao(t) : st("Only time and utc scales accept interval strings."), r && (t = t.every(r))), t;
}
function Cg(n, t, e) {
  let r = n.range(), i = r[0], o = pn(r), a = Ng;
  if (i > o && (r = o, o = i, i = r, a = Pg), i = Math.floor(i), o = Math.ceil(o), t = t.map((u) => [u, n(u)]).filter((u) => i <= u[1] && u[1] <= o).sort(a).map((u) => u[0]), e > 0 && t.length > 1) {
    const u = [t[0], pn(t)];
    for (; t.length > e && t.length >= 3; )
      t = t.filter((c, f) => !(f % 2));
    t.length < 3 && (t = u);
  }
  return t;
}
function Cc(n, t) {
  return n.bins ? Cg(n, n.bins, t) : n.ticks ? n.ticks(t) : n.domain();
}
function Dg(n, t, e, r, i, o) {
  const a = t.type;
  let u = Tg;
  if (a === Ht || i === Ht)
    u = n.timeFormat(r);
  else if (a === Wt || i === Wt)
    u = n.utcFormat(r);
  else if (mg(a)) {
    const c = n.formatFloat(r);
    if (o || t.bins)
      u = c;
    else {
      const f = Dc(t, e, !1);
      u = (l) => f(l) ? c(l) : "";
    }
  } else if (t.tickFormat) {
    const c = t.domain();
    u = n.formatSpan(c[0], c[c.length - 1], e, r);
  } else r && (u = n.format(r));
  return u;
}
function Dc(n, t, e) {
  const r = Cc(n, t), i = n.base(), o = Math.log(i), a = Math.max(1, i * t / r.length), u = (c) => {
    let f = c / Math.pow(i, Math.round(Math.log(c) / o));
    return f * i < i - 0.5 && (f *= i), f <= a;
  };
  return e ? r.filter(u) : u;
}
const Vi = {
  [De]: "quantiles",
  [Do]: "thresholds",
  [Uo]: "domain"
}, Uc = {
  [De]: "quantiles",
  [Do]: "domain"
};
function Ug(n, t) {
  return n.bins ? Ig(n.bins) : n.type === tt ? Dc(n, t, !0) : Vi[n.type] ? Rg(n[Vi[n.type]]()) : Cc(n, t);
}
function Fg(n, t, e) {
  const r = t[Uc[t.type]](), i = r.length;
  let o = i > 1 ? r[1] - r[0] : r[0], a;
  for (a = 1; a < i; ++a)
    o = Math.min(o, r[a] - r[a - 1]);
  return n.formatSpan(0, o, 3 * 10, e);
}
function Rg(n) {
  const t = [-1 / 0].concat(n);
  return t.max = 1 / 0, t;
}
function Ig(n) {
  const t = n.slice(0, -1);
  return t.max = pn(n), t;
}
const kg = (n) => Vi[n.type] || n.bins;
function Og(n, t, e, r, i, o, a) {
  const u = Uc[t.type] && o !== Ht && o !== Wt ? Fg(n, t, i) : Dg(n, t, e, i, o, a);
  return r === Eg && kg(t) ? qg(u) : r === Ag ? Yg(u) : Lg(u);
}
const qg = (n) => (t, e, r) => {
  const i = Ja(r[e + 1], Ja(r.max, 1 / 0)), o = Ka(t, n), a = Ka(i, n);
  return o && a ? o + " – " + a : a ? "< " + a : "≥ " + o;
}, Ja = (n, t) => n ?? t, Yg = (n) => (t, e) => e ? n(t) : null, Lg = (n) => (t) => n(t), Ka = (n, t) => Number.isFinite(n) ? t(n) : null;
function m2(n) {
  const t = n.domain(), e = t.length - 1;
  let r = +t[0], i = +pn(t), o = i - r;
  if (n.type === Uo) {
    const a = e ? o / e : 0.1;
    r -= a, i += a, o = i - r;
  }
  return (a) => (a - r) / o;
}
function jg(n, t, e, r) {
  const i = r || t.type;
  return Ki(e) && yg(i) && (e = e.replace(/%a/g, "%A").replace(/%b/g, "%B")), !e && i === Ht ? n.timeFormat("%A, %d %B %Y, %X") : !e && i === Wt ? n.utcFormat("%A, %d %B %Y, %X UTC") : Og(n, t, 5, null, e, r, !0);
}
function y2(n, t, e) {
  e = e || {};
  const r = Math.max(3, e.maxlen || 7), i = jg(n, t, e.format, e.formatType);
  if (dg(t.type)) {
    const o = Ug(t).slice(1).map(i), a = o.length;
    return `${a} boundar${a === 1 ? "y" : "ies"}: ${o.join(", ")}`;
  } else if (pg(t.type)) {
    const o = t.domain(), a = o.length, u = a > r ? o.slice(0, r - 2).map(i).join(", ") + ", ending with " + o.slice(-1).map(i) : o.map(i).join(", ");
    return `${a} value${a === 1 ? "" : "s"}: ${u}`;
  } else {
    const o = t.domain();
    return `values from ${i(o[0])} to ${i(pn(o))}`;
  }
}
const Bg = af(), zg = [
  // standard properties in d3-geo
  "clipAngle",
  "clipExtent",
  "scale",
  "translate",
  "center",
  "rotate",
  "parallels",
  "precision",
  "reflectX",
  "reflectY",
  // extended properties in d3-geo-projections
  "coefficient",
  "distance",
  "fraction",
  "lobes",
  "parallel",
  "radius",
  "ratio",
  "spacing",
  "tilt"
];
function Hg(n, t) {
  return function e() {
    const r = t();
    return r.type = n, r.path = af().projection(r), r.copy = r.copy || function() {
      const i = e();
      return zg.forEach((o) => {
        r[o] && i[o](r[o]());
      }), i.path.pointRadius(r.path.pointRadius()), i;
    }, Tc(r);
  };
}
function Wg(n, t) {
  if (!n || typeof n != "string")
    throw new Error("Projection type must be a name string.");
  return n = n.toLowerCase(), arguments.length > 1 ? (Er[n] = Hg(n, t), this) : Er[n] || null;
}
function b2(n) {
  return n && n.path || Bg;
}
const Er = {
  // base d3-geo projection types
  albers: ff,
  albersusa: Cs,
  azimuthalequalarea: Ds,
  azimuthalequidistant: Us,
  conicconformal: Is,
  conicequalarea: pr,
  conicequidistant: qs,
  equalEarth: Ls,
  equirectangular: ks,
  gnomonic: js,
  identity: Bs,
  mercator: Fs,
  mollweide: Ks,
  naturalEarth1: zs,
  orthographic: Hs,
  stereographic: Ws,
  transversemercator: Gs
};
for (const n in Er)
  Wg(n, Er[n]);
var Fc = { exports: {} }, Gg = "Function.prototype.bind called on incompatible ", Xg = Object.prototype.toString, _g = Math.max, Vg = "[object Function]", nu = function(t, e) {
  for (var r = [], i = 0; i < t.length; i += 1)
    r[i] = t[i];
  for (var o = 0; o < e.length; o += 1)
    r[o + t.length] = e[o];
  return r;
}, Zg = function(t, e) {
  for (var r = [], i = e, o = 0; i < t.length; i += 1, o += 1)
    r[o] = t[i];
  return r;
}, Qg = function(n, t) {
  for (var e = "", r = 0; r < n.length; r += 1)
    e += n[r], r + 1 < n.length && (e += t);
  return e;
}, Jg = function(t) {
  var e = this;
  if (typeof e != "function" || Xg.apply(e) !== Vg)
    throw new TypeError(Gg + e);
  for (var r = Zg(arguments, 1), i, o = function() {
    if (this instanceof i) {
      var l = e.apply(
        this,
        nu(r, arguments)
      );
      return Object(l) === l ? l : this;
    }
    return e.apply(
      t,
      nu(r, arguments)
    );
  }, a = _g(0, e.length - r.length), u = [], c = 0; c < a; c++)
    u[c] = "$" + c;
  if (i = Function("binder", "return function (" + Qg(u, ",") + "){ return binder.apply(this,arguments); }")(o), e.prototype) {
    var f = function() {
    };
    f.prototype = e.prototype, i.prototype = new f(), f.prototype = null;
  }
  return i;
}, Kg = Jg, Io = Function.prototype.bind || Kg, np = Error, tp = EvalError, ep = RangeError, rp = ReferenceError, Rc = SyntaxError, Xr = TypeError, ip = URIError, op = function() {
  if (typeof Symbol != "function" || typeof Object.getOwnPropertySymbols != "function")
    return !1;
  if (typeof Symbol.iterator == "symbol")
    return !0;
  var t = {}, e = Symbol("test"), r = Object(e);
  if (typeof e == "string" || Object.prototype.toString.call(e) !== "[object Symbol]" || Object.prototype.toString.call(r) !== "[object Symbol]")
    return !1;
  var i = 42;
  t[e] = i;
  for (e in t)
    return !1;
  if (typeof Object.keys == "function" && Object.keys(t).length !== 0 || typeof Object.getOwnPropertyNames == "function" && Object.getOwnPropertyNames(t).length !== 0)
    return !1;
  var o = Object.getOwnPropertySymbols(t);
  if (o.length !== 1 || o[0] !== e || !Object.prototype.propertyIsEnumerable.call(t, e))
    return !1;
  if (typeof Object.getOwnPropertyDescriptor == "function") {
    var a = Object.getOwnPropertyDescriptor(t, e);
    if (a.value !== i || a.enumerable !== !0)
      return !1;
  }
  return !0;
}, tu = typeof Symbol < "u" && Symbol, ap = op, up = function() {
  return typeof tu != "function" || typeof Symbol != "function" || typeof tu("foo") != "symbol" || typeof Symbol("bar") != "symbol" ? !1 : ap();
}, si = {
  __proto__: null,
  foo: {}
}, fp = Object, cp = function() {
  return { __proto__: si }.foo === si.foo && !(si instanceof fp);
}, lp = Function.prototype.call, sp = Object.prototype.hasOwnProperty, hp = Io, gp = hp.call(lp, sp), q, pp = np, dp = tp, mp = ep, yp = rp, Gt = Rc, Rt = Xr, bp = ip, Ic = Function, hi = function(n) {
  try {
    return Ic('"use strict"; return (' + n + ").constructor;")();
  } catch {
  }
}, pt = Object.getOwnPropertyDescriptor;
if (pt)
  try {
    pt({}, "");
  } catch {
    pt = null;
  }
var gi = function() {
  throw new Rt();
}, vp = pt ? function() {
  try {
    return arguments.callee, gi;
  } catch {
    try {
      return pt(arguments, "callee").get;
    } catch {
      return gi;
    }
  }
}() : gi, Tt = up(), Mp = cp(), K = Object.getPrototypeOf || (Mp ? function(n) {
  return n.__proto__;
} : null), Ct = {}, wp = typeof Uint8Array > "u" || !K ? q : K(Uint8Array), dt = {
  __proto__: null,
  "%AggregateError%": typeof AggregateError > "u" ? q : AggregateError,
  "%Array%": Array,
  "%ArrayBuffer%": typeof ArrayBuffer > "u" ? q : ArrayBuffer,
  "%ArrayIteratorPrototype%": Tt && K ? K([][Symbol.iterator]()) : q,
  "%AsyncFromSyncIteratorPrototype%": q,
  "%AsyncFunction%": Ct,
  "%AsyncGenerator%": Ct,
  "%AsyncGeneratorFunction%": Ct,
  "%AsyncIteratorPrototype%": Ct,
  "%Atomics%": typeof Atomics > "u" ? q : Atomics,
  "%BigInt%": typeof BigInt > "u" ? q : BigInt,
  "%BigInt64Array%": typeof BigInt64Array > "u" ? q : BigInt64Array,
  "%BigUint64Array%": typeof BigUint64Array > "u" ? q : BigUint64Array,
  "%Boolean%": Boolean,
  "%DataView%": typeof DataView > "u" ? q : DataView,
  "%Date%": Date,
  "%decodeURI%": decodeURI,
  "%decodeURIComponent%": decodeURIComponent,
  "%encodeURI%": encodeURI,
  "%encodeURIComponent%": encodeURIComponent,
  "%Error%": pp,
  "%eval%": eval,
  // eslint-disable-line no-eval
  "%EvalError%": dp,
  "%Float32Array%": typeof Float32Array > "u" ? q : Float32Array,
  "%Float64Array%": typeof Float64Array > "u" ? q : Float64Array,
  "%FinalizationRegistry%": typeof FinalizationRegistry > "u" ? q : FinalizationRegistry,
  "%Function%": Ic,
  "%GeneratorFunction%": Ct,
  "%Int8Array%": typeof Int8Array > "u" ? q : Int8Array,
  "%Int16Array%": typeof Int16Array > "u" ? q : Int16Array,
  "%Int32Array%": typeof Int32Array > "u" ? q : Int32Array,
  "%isFinite%": isFinite,
  "%isNaN%": isNaN,
  "%IteratorPrototype%": Tt && K ? K(K([][Symbol.iterator]())) : q,
  "%JSON%": typeof JSON == "object" ? JSON : q,
  "%Map%": typeof Map > "u" ? q : Map,
  "%MapIteratorPrototype%": typeof Map > "u" || !Tt || !K ? q : K((/* @__PURE__ */ new Map())[Symbol.iterator]()),
  "%Math%": Math,
  "%Number%": Number,
  "%Object%": Object,
  "%parseFloat%": parseFloat,
  "%parseInt%": parseInt,
  "%Promise%": typeof Promise > "u" ? q : Promise,
  "%Proxy%": typeof Proxy > "u" ? q : Proxy,
  "%RangeError%": mp,
  "%ReferenceError%": yp,
  "%Reflect%": typeof Reflect > "u" ? q : Reflect,
  "%RegExp%": RegExp,
  "%Set%": typeof Set > "u" ? q : Set,
  "%SetIteratorPrototype%": typeof Set > "u" || !Tt || !K ? q : K((/* @__PURE__ */ new Set())[Symbol.iterator]()),
  "%SharedArrayBuffer%": typeof SharedArrayBuffer > "u" ? q : SharedArrayBuffer,
  "%String%": String,
  "%StringIteratorPrototype%": Tt && K ? K(""[Symbol.iterator]()) : q,
  "%Symbol%": Tt ? Symbol : q,
  "%SyntaxError%": Gt,
  "%ThrowTypeError%": vp,
  "%TypedArray%": wp,
  "%TypeError%": Rt,
  "%Uint8Array%": typeof Uint8Array > "u" ? q : Uint8Array,
  "%Uint8ClampedArray%": typeof Uint8ClampedArray > "u" ? q : Uint8ClampedArray,
  "%Uint16Array%": typeof Uint16Array > "u" ? q : Uint16Array,
  "%Uint32Array%": typeof Uint32Array > "u" ? q : Uint32Array,
  "%URIError%": bp,
  "%WeakMap%": typeof WeakMap > "u" ? q : WeakMap,
  "%WeakRef%": typeof WeakRef > "u" ? q : WeakRef,
  "%WeakSet%": typeof WeakSet > "u" ? q : WeakSet
};
if (K)
  try {
    null.error;
  } catch (n) {
    var Sp = K(K(n));
    dt["%Error.prototype%"] = Sp;
  }
var xp = function n(t) {
  var e;
  if (t === "%AsyncFunction%")
    e = hi("async function () {}");
  else if (t === "%GeneratorFunction%")
    e = hi("function* () {}");
  else if (t === "%AsyncGeneratorFunction%")
    e = hi("async function* () {}");
  else if (t === "%AsyncGenerator%") {
    var r = n("%AsyncGeneratorFunction%");
    r && (e = r.prototype);
  } else if (t === "%AsyncIteratorPrototype%") {
    var i = n("%AsyncGenerator%");
    i && K && (e = K(i.prototype));
  }
  return dt[t] = e, e;
}, eu = {
  __proto__: null,
  "%ArrayBufferPrototype%": ["ArrayBuffer", "prototype"],
  "%ArrayPrototype%": ["Array", "prototype"],
  "%ArrayProto_entries%": ["Array", "prototype", "entries"],
  "%ArrayProto_forEach%": ["Array", "prototype", "forEach"],
  "%ArrayProto_keys%": ["Array", "prototype", "keys"],
  "%ArrayProto_values%": ["Array", "prototype", "values"],
  "%AsyncFunctionPrototype%": ["AsyncFunction", "prototype"],
  "%AsyncGenerator%": ["AsyncGeneratorFunction", "prototype"],
  "%AsyncGeneratorPrototype%": ["AsyncGeneratorFunction", "prototype", "prototype"],
  "%BooleanPrototype%": ["Boolean", "prototype"],
  "%DataViewPrototype%": ["DataView", "prototype"],
  "%DatePrototype%": ["Date", "prototype"],
  "%ErrorPrototype%": ["Error", "prototype"],
  "%EvalErrorPrototype%": ["EvalError", "prototype"],
  "%Float32ArrayPrototype%": ["Float32Array", "prototype"],
  "%Float64ArrayPrototype%": ["Float64Array", "prototype"],
  "%FunctionPrototype%": ["Function", "prototype"],
  "%Generator%": ["GeneratorFunction", "prototype"],
  "%GeneratorPrototype%": ["GeneratorFunction", "prototype", "prototype"],
  "%Int8ArrayPrototype%": ["Int8Array", "prototype"],
  "%Int16ArrayPrototype%": ["Int16Array", "prototype"],
  "%Int32ArrayPrototype%": ["Int32Array", "prototype"],
  "%JSONParse%": ["JSON", "parse"],
  "%JSONStringify%": ["JSON", "stringify"],
  "%MapPrototype%": ["Map", "prototype"],
  "%NumberPrototype%": ["Number", "prototype"],
  "%ObjectPrototype%": ["Object", "prototype"],
  "%ObjProto_toString%": ["Object", "prototype", "toString"],
  "%ObjProto_valueOf%": ["Object", "prototype", "valueOf"],
  "%PromisePrototype%": ["Promise", "prototype"],
  "%PromiseProto_then%": ["Promise", "prototype", "then"],
  "%Promise_all%": ["Promise", "all"],
  "%Promise_reject%": ["Promise", "reject"],
  "%Promise_resolve%": ["Promise", "resolve"],
  "%RangeErrorPrototype%": ["RangeError", "prototype"],
  "%ReferenceErrorPrototype%": ["ReferenceError", "prototype"],
  "%RegExpPrototype%": ["RegExp", "prototype"],
  "%SetPrototype%": ["Set", "prototype"],
  "%SharedArrayBufferPrototype%": ["SharedArrayBuffer", "prototype"],
  "%StringPrototype%": ["String", "prototype"],
  "%SymbolPrototype%": ["Symbol", "prototype"],
  "%SyntaxErrorPrototype%": ["SyntaxError", "prototype"],
  "%TypedArrayPrototype%": ["TypedArray", "prototype"],
  "%TypeErrorPrototype%": ["TypeError", "prototype"],
  "%Uint8ArrayPrototype%": ["Uint8Array", "prototype"],
  "%Uint8ClampedArrayPrototype%": ["Uint8ClampedArray", "prototype"],
  "%Uint16ArrayPrototype%": ["Uint16Array", "prototype"],
  "%Uint32ArrayPrototype%": ["Uint32Array", "prototype"],
  "%URIErrorPrototype%": ["URIError", "prototype"],
  "%WeakMapPrototype%": ["WeakMap", "prototype"],
  "%WeakSetPrototype%": ["WeakSet", "prototype"]
}, je = Io, Ar = gp, $p = je.call(Function.call, Array.prototype.concat), Ep = je.call(Function.apply, Array.prototype.splice), ru = je.call(Function.call, String.prototype.replace), Tr = je.call(Function.call, String.prototype.slice), Ap = je.call(Function.call, RegExp.prototype.exec), Tp = /[^%.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|%$))/g, Np = /\\(\\)?/g, Pp = function(t) {
  var e = Tr(t, 0, 1), r = Tr(t, -1);
  if (e === "%" && r !== "%")
    throw new Gt("invalid intrinsic syntax, expected closing `%`");
  if (r === "%" && e !== "%")
    throw new Gt("invalid intrinsic syntax, expected opening `%`");
  var i = [];
  return ru(t, Tp, function(o, a, u, c) {
    i[i.length] = u ? ru(c, Np, "$1") : a || o;
  }), i;
}, Cp = function(t, e) {
  var r = t, i;
  if (Ar(eu, r) && (i = eu[r], r = "%" + i[0] + "%"), Ar(dt, r)) {
    var o = dt[r];
    if (o === Ct && (o = xp(r)), typeof o > "u" && !e)
      throw new Rt("intrinsic " + t + " exists, but is not available. Please file an issue!");
    return {
      alias: i,
      name: r,
      value: o
    };
  }
  throw new Gt("intrinsic " + t + " does not exist!");
}, Be = function(t, e) {
  if (typeof t != "string" || t.length === 0)
    throw new Rt("intrinsic name must be a non-empty string");
  if (arguments.length > 1 && typeof e != "boolean")
    throw new Rt('"allowMissing" argument must be a boolean');
  if (Ap(/^%?[^%]*%?$/, t) === null)
    throw new Gt("`%` may not be present anywhere but at the beginning and end of the intrinsic name");
  var r = Pp(t), i = r.length > 0 ? r[0] : "", o = Cp("%" + i + "%", e), a = o.name, u = o.value, c = !1, f = o.alias;
  f && (i = f[0], Ep(r, $p([0, 1], f)));
  for (var l = 1, s = !0; l < r.length; l += 1) {
    var h = r[l], g = Tr(h, 0, 1), p = Tr(h, -1);
    if ((g === '"' || g === "'" || g === "`" || p === '"' || p === "'" || p === "`") && g !== p)
      throw new Gt("property names with quotes must have matching quotes");
    if ((h === "constructor" || !s) && (c = !0), i += "." + h, a = "%" + i + "%", Ar(dt, a))
      u = dt[a];
    else if (u != null) {
      if (!(h in u)) {
        if (!e)
          throw new Rt("base intrinsic for " + t + " exists, but the property is not available.");
        return;
      }
      if (pt && l + 1 >= r.length) {
        var d = pt(u, h);
        s = !!d, s && "get" in d && !("originalValue" in d.get) ? u = d.get : u = u[h];
      } else
        s = Ar(u, h), u = u[h];
      s && !c && (dt[a] = u);
    }
  }
  return u;
}, pi, iu;
function ko() {
  if (iu) return pi;
  iu = 1;
  var n = Be, t = n("%Object.defineProperty%", !0) || !1;
  if (t)
    try {
      t({}, "a", { value: 1 });
    } catch {
      t = !1;
    }
  return pi = t, pi;
}
var Dp = Be, tr = Dp("%Object.getOwnPropertyDescriptor%", !0);
if (tr)
  try {
    tr([], "length");
  } catch {
    tr = null;
  }
var kc = tr, ou = ko(), Up = Rc, Nt = Xr, au = kc, Fp = function(t, e, r) {
  if (!t || typeof t != "object" && typeof t != "function")
    throw new Nt("`obj` must be an object or a function`");
  if (typeof e != "string" && typeof e != "symbol")
    throw new Nt("`property` must be a string or a symbol`");
  if (arguments.length > 3 && typeof arguments[3] != "boolean" && arguments[3] !== null)
    throw new Nt("`nonEnumerable`, if provided, must be a boolean or null");
  if (arguments.length > 4 && typeof arguments[4] != "boolean" && arguments[4] !== null)
    throw new Nt("`nonWritable`, if provided, must be a boolean or null");
  if (arguments.length > 5 && typeof arguments[5] != "boolean" && arguments[5] !== null)
    throw new Nt("`nonConfigurable`, if provided, must be a boolean or null");
  if (arguments.length > 6 && typeof arguments[6] != "boolean")
    throw new Nt("`loose`, if provided, must be a boolean");
  var i = arguments.length > 3 ? arguments[3] : null, o = arguments.length > 4 ? arguments[4] : null, a = arguments.length > 5 ? arguments[5] : null, u = arguments.length > 6 ? arguments[6] : !1, c = !!au && au(t, e);
  if (ou)
    ou(t, e, {
      configurable: a === null && c ? c.configurable : !a,
      enumerable: i === null && c ? c.enumerable : !i,
      value: r,
      writable: o === null && c ? c.writable : !o
    });
  else if (u || !i && !o && !a)
    t[e] = r;
  else
    throw new Up("This environment does not support defining a property as non-configurable, non-writable, or non-enumerable.");
}, Zi = ko(), Oc = function() {
  return !!Zi;
};
Oc.hasArrayLengthDefineBug = function() {
  if (!Zi)
    return null;
  try {
    return Zi([], "length", { value: 1 }).length !== 1;
  } catch {
    return !0;
  }
};
var Rp = Oc, Ip = Be, uu = Fp, kp = Rp(), fu = kc, cu = Xr, Op = Ip("%Math.floor%"), qp = function(t, e) {
  if (typeof t != "function")
    throw new cu("`fn` is not a function");
  if (typeof e != "number" || e < 0 || e > 4294967295 || Op(e) !== e)
    throw new cu("`length` must be a positive 32-bit integer");
  var r = arguments.length > 2 && !!arguments[2], i = !0, o = !0;
  if ("length" in t && fu) {
    var a = fu(t, "length");
    a && !a.configurable && (i = !1), a && !a.writable && (o = !1);
  }
  return (i || o || !r) && (kp ? uu(
    /** @type {Parameters<define>[0]} */
    t,
    "length",
    e,
    !0,
    !0
  ) : uu(
    /** @type {Parameters<define>[0]} */
    t,
    "length",
    e
  )), t;
};
(function(n) {
  var t = Io, e = Be, r = qp, i = Xr, o = e("%Function.prototype.apply%"), a = e("%Function.prototype.call%"), u = e("%Reflect.apply%", !0) || t.call(a, o), c = ko(), f = e("%Math.max%");
  n.exports = function(h) {
    if (typeof h != "function")
      throw new i("a function is required");
    var g = u(t, a, arguments);
    return r(
      g,
      1 + f(0, h.length - (arguments.length - 1)),
      !0
    );
  };
  var l = function() {
    return u(t, o, arguments);
  };
  c ? c(n.exports, "apply", { value: l }) : n.exports.apply = l;
})(Fc);
var Yp = Fc.exports, qc = Be, Yc = Yp, Lp = Yc(qc("String.prototype.indexOf")), v2 = function(t, e) {
  var r = qc(t, !!e);
  return typeof r == "function" && Lp(t, ".prototype.") > -1 ? Yc(r) : r;
};
export {
  Qi as $,
  yt as A,
  we as B,
  Q0 as C,
  K0 as D,
  J0 as E,
  go as F,
  _f as G,
  Ki as H,
  Nd as I,
  lc as J,
  Mh as K,
  sc as L,
  wh as M,
  er as N,
  In as O,
  Rn as P,
  Tn as Q,
  gn as R,
  Zn as S,
  An as T,
  Qn as U,
  un as V,
  on as W,
  Eo as X,
  cn as Y,
  Ao as Z,
  Md as _,
  Xn as a,
  Cg as a$,
  wd as a0,
  Sd as a1,
  gu as a2,
  ft as a3,
  ul as a4,
  Ji as a5,
  hu as a6,
  Ue as a7,
  gd as a8,
  Ed as a9,
  Cr as aA,
  ud as aB,
  Nl as aC,
  Dd as aD,
  bd as aE,
  id as aF,
  xu as aG,
  fd as aH,
  dd as aI,
  nt as aJ,
  Od as aK,
  Rl as aL,
  kd as aM,
  qd as aN,
  $l as aO,
  Bo as aP,
  jo as aQ,
  Kt as aR,
  Wd as aS,
  $u as aT,
  yd as aU,
  Su as aV,
  Gd as aW,
  pg as aX,
  y2 as aY,
  d2 as aZ,
  Dg as a_,
  Ad as aa,
  $d as ab,
  ld as ac,
  It as ad,
  zp as ae,
  Wp as af,
  Vc as ag,
  Mu as ah,
  Bp as ai,
  od as aj,
  zc as ak,
  et as al,
  vu as am,
  jp as an,
  Pd as ao,
  ad as ap,
  Hd as aq,
  Ud as ar,
  Id as as,
  Tl as at,
  Yh as au,
  a2 as av,
  Lh as aw,
  t2 as ax,
  n2 as ay,
  pn as az,
  B as b,
  kl as b$,
  Cc as b0,
  Hp as b1,
  Eg as b2,
  Og as b3,
  Ug as b4,
  p2 as b5,
  g2 as b6,
  m2 as b7,
  Gc as b8,
  H as b9,
  Uo as bA,
  De as bB,
  Do as bC,
  h2 as bD,
  s2 as bE,
  qe as bF,
  b2 as bG,
  br as bH,
  zg as bI,
  Wg as bJ,
  Pl as bK,
  zd as bL,
  zl as bM,
  Hl as bN,
  Yd as bO,
  Ld as bP,
  jd as bQ,
  Wl as bR,
  Bd as bS,
  Td as bT,
  mt as bU,
  ol as bV,
  sd as bW,
  qu as bX,
  Ol as bY,
  jl as bZ,
  Ul as b_,
  Jt as ba,
  To as bb,
  f2 as bc,
  Ht as bd,
  Wt as be,
  eg as bf,
  ha as bg,
  tt as bh,
  Jp as bi,
  Po as bj,
  Kp as bk,
  No as bl,
  Co as bm,
  nd as bn,
  Qp as bo,
  mg as bp,
  og as bq,
  c2 as br,
  vg as bs,
  Mg as bt,
  qr as bu,
  Mt as bv,
  ig as bw,
  rg as bx,
  ng as by,
  $g as bz,
  I as c,
  Ll as c0,
  Yu as c1,
  ql as c2,
  Bl as c3,
  Ou as c4,
  Il as c5,
  Yl as c6,
  hd as c7,
  pd as c8,
  cd as c9,
  l2 as cA,
  dg as cB,
  Vn as cC,
  Jc as cD,
  Qc as cE,
  _c as cF,
  Zc as cG,
  Rd as cH,
  Fd as cI,
  He as cJ,
  Cd as cK,
  pu as cL,
  Be as cM,
  v2 as cN,
  Xr as cO,
  Yp as cP,
  md as ca,
  vd as cb,
  xd as cc,
  ki as cd,
  Oi as ce,
  Ii as cf,
  r2 as cg,
  o2 as ch,
  e2 as ci,
  i2 as cj,
  Vd as ck,
  td as cl,
  ed as cm,
  Qd as cn,
  Kd as co,
  Zd as cp,
  Jd as cq,
  rd as cr,
  Xp as cs,
  _p as ct,
  Vp as cu,
  Zp as cv,
  u2 as cw,
  Gp as cx,
  su as cy,
  gg as cz,
  kt as d,
  U as e,
  ur as f,
  Pt as g,
  wi as h,
  Mi as i,
  rn as j,
  Lu as k,
  _d as l,
  Mn as m,
  bn as n,
  ln as o,
  Al as p,
  Wo as q,
  _ as r,
  C as s,
  dn as t,
  Xd as u,
  st as v,
  V0 as w,
  M1 as x,
  wu as y,
  Ne as z
};
