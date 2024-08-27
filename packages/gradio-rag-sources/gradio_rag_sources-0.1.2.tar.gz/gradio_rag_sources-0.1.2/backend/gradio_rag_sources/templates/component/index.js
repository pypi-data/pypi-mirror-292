const {
  SvelteComponent: xl,
  assign: $l,
  create_slot: ei,
  detach: ti,
  element: ni,
  get_all_dirty_from_scope: li,
  get_slot_changes: ii,
  get_spread_update: oi,
  init: si,
  insert: ri,
  safe_not_equal: ai,
  set_dynamic_element_data: Cn,
  set_style: te,
  toggle_class: Ae,
  transition_in: yl,
  transition_out: Sl,
  update_slot_base: fi
} = window.__gradio__svelte__internal;
function ci(n) {
  let e, t, l;
  const i = (
    /*#slots*/
    n[18].default
  ), s = ei(
    i,
    n,
    /*$$scope*/
    n[17],
    null
  );
  let r = [
    { "data-testid": (
      /*test_id*/
      n[7]
    ) },
    { id: (
      /*elem_id*/
      n[2]
    ) },
    {
      class: t = "block " + /*elem_classes*/
      n[3].join(" ") + " svelte-nl1om8"
    }
  ], a = {};
  for (let o = 0; o < r.length; o += 1)
    a = $l(a, r[o]);
  return {
    c() {
      e = ni(
        /*tag*/
        n[14]
      ), s && s.c(), Cn(
        /*tag*/
        n[14]
      )(e, a), Ae(
        e,
        "hidden",
        /*visible*/
        n[10] === !1
      ), Ae(
        e,
        "padded",
        /*padding*/
        n[6]
      ), Ae(
        e,
        "border_focus",
        /*border_mode*/
        n[5] === "focus"
      ), Ae(
        e,
        "border_contrast",
        /*border_mode*/
        n[5] === "contrast"
      ), Ae(e, "hide-container", !/*explicit_call*/
      n[8] && !/*container*/
      n[9]), te(
        e,
        "height",
        /*get_dimension*/
        n[15](
          /*height*/
          n[0]
        )
      ), te(e, "width", typeof /*width*/
      n[1] == "number" ? `calc(min(${/*width*/
      n[1]}px, 100%))` : (
        /*get_dimension*/
        n[15](
          /*width*/
          n[1]
        )
      )), te(
        e,
        "border-style",
        /*variant*/
        n[4]
      ), te(
        e,
        "overflow",
        /*allow_overflow*/
        n[11] ? "visible" : "hidden"
      ), te(
        e,
        "flex-grow",
        /*scale*/
        n[12]
      ), te(e, "min-width", `calc(min(${/*min_width*/
      n[13]}px, 100%))`), te(e, "border-width", "var(--block-border-width)");
    },
    m(o, f) {
      ri(o, e, f), s && s.m(e, null), l = !0;
    },
    p(o, f) {
      s && s.p && (!l || f & /*$$scope*/
      131072) && fi(
        s,
        i,
        o,
        /*$$scope*/
        o[17],
        l ? ii(
          i,
          /*$$scope*/
          o[17],
          f,
          null
        ) : li(
          /*$$scope*/
          o[17]
        ),
        null
      ), Cn(
        /*tag*/
        o[14]
      )(e, a = oi(r, [
        (!l || f & /*test_id*/
        128) && { "data-testid": (
          /*test_id*/
          o[7]
        ) },
        (!l || f & /*elem_id*/
        4) && { id: (
          /*elem_id*/
          o[2]
        ) },
        (!l || f & /*elem_classes*/
        8 && t !== (t = "block " + /*elem_classes*/
        o[3].join(" ") + " svelte-nl1om8")) && { class: t }
      ])), Ae(
        e,
        "hidden",
        /*visible*/
        o[10] === !1
      ), Ae(
        e,
        "padded",
        /*padding*/
        o[6]
      ), Ae(
        e,
        "border_focus",
        /*border_mode*/
        o[5] === "focus"
      ), Ae(
        e,
        "border_contrast",
        /*border_mode*/
        o[5] === "contrast"
      ), Ae(e, "hide-container", !/*explicit_call*/
      o[8] && !/*container*/
      o[9]), f & /*height*/
      1 && te(
        e,
        "height",
        /*get_dimension*/
        o[15](
          /*height*/
          o[0]
        )
      ), f & /*width*/
      2 && te(e, "width", typeof /*width*/
      o[1] == "number" ? `calc(min(${/*width*/
      o[1]}px, 100%))` : (
        /*get_dimension*/
        o[15](
          /*width*/
          o[1]
        )
      )), f & /*variant*/
      16 && te(
        e,
        "border-style",
        /*variant*/
        o[4]
      ), f & /*allow_overflow*/
      2048 && te(
        e,
        "overflow",
        /*allow_overflow*/
        o[11] ? "visible" : "hidden"
      ), f & /*scale*/
      4096 && te(
        e,
        "flex-grow",
        /*scale*/
        o[12]
      ), f & /*min_width*/
      8192 && te(e, "min-width", `calc(min(${/*min_width*/
      o[13]}px, 100%))`);
    },
    i(o) {
      l || (yl(s, o), l = !0);
    },
    o(o) {
      Sl(s, o), l = !1;
    },
    d(o) {
      o && ti(e), s && s.d(o);
    }
  };
}
function ui(n) {
  let e, t = (
    /*tag*/
    n[14] && ci(n)
  );
  return {
    c() {
      t && t.c();
    },
    m(l, i) {
      t && t.m(l, i), e = !0;
    },
    p(l, [i]) {
      /*tag*/
      l[14] && t.p(l, i);
    },
    i(l) {
      e || (yl(t, l), e = !0);
    },
    o(l) {
      Sl(t, l), e = !1;
    },
    d(l) {
      t && t.d(l);
    }
  };
}
function _i(n, e, t) {
  let { $$slots: l = {}, $$scope: i } = e, { height: s = void 0 } = e, { width: r = void 0 } = e, { elem_id: a = "" } = e, { elem_classes: o = [] } = e, { variant: f = "solid" } = e, { border_mode: u = "base" } = e, { padding: m = !0 } = e, { type: E = "normal" } = e, { test_id: b = void 0 } = e, { explicit_call: k = !1 } = e, { container: R = !0 } = e, { visible: y = !0 } = e, { allow_overflow: N = !0 } = e, { scale: g = null } = e, { min_width: h = 0 } = e, w = E === "fieldset" ? "fieldset" : "div";
  const F = (_) => {
    if (_ !== void 0) {
      if (typeof _ == "number")
        return _ + "px";
      if (typeof _ == "string")
        return _;
    }
  };
  return n.$$set = (_) => {
    "height" in _ && t(0, s = _.height), "width" in _ && t(1, r = _.width), "elem_id" in _ && t(2, a = _.elem_id), "elem_classes" in _ && t(3, o = _.elem_classes), "variant" in _ && t(4, f = _.variant), "border_mode" in _ && t(5, u = _.border_mode), "padding" in _ && t(6, m = _.padding), "type" in _ && t(16, E = _.type), "test_id" in _ && t(7, b = _.test_id), "explicit_call" in _ && t(8, k = _.explicit_call), "container" in _ && t(9, R = _.container), "visible" in _ && t(10, y = _.visible), "allow_overflow" in _ && t(11, N = _.allow_overflow), "scale" in _ && t(12, g = _.scale), "min_width" in _ && t(13, h = _.min_width), "$$scope" in _ && t(17, i = _.$$scope);
  }, [
    s,
    r,
    a,
    o,
    f,
    u,
    m,
    b,
    k,
    R,
    y,
    N,
    g,
    h,
    w,
    F,
    E,
    i,
    l
  ];
}
class di extends xl {
  constructor(e) {
    super(), si(this, e, _i, ui, ai, {
      height: 0,
      width: 1,
      elem_id: 2,
      elem_classes: 3,
      variant: 4,
      border_mode: 5,
      padding: 6,
      type: 16,
      test_id: 7,
      explicit_call: 8,
      container: 9,
      visible: 10,
      allow_overflow: 11,
      scale: 12,
      min_width: 13
    });
  }
}
const {
  SvelteComponent: mi,
  attr: gi,
  create_slot: hi,
  detach: pi,
  element: bi,
  get_all_dirty_from_scope: wi,
  get_slot_changes: Ti,
  init: Ei,
  insert: Ai,
  safe_not_equal: ki,
  transition_in: yi,
  transition_out: Si,
  update_slot_base: vi
} = window.__gradio__svelte__internal;
function Li(n) {
  let e, t;
  const l = (
    /*#slots*/
    n[1].default
  ), i = hi(
    l,
    n,
    /*$$scope*/
    n[0],
    null
  );
  return {
    c() {
      e = bi("div"), i && i.c(), gi(e, "class", "svelte-1hnfib2");
    },
    m(s, r) {
      Ai(s, e, r), i && i.m(e, null), t = !0;
    },
    p(s, [r]) {
      i && i.p && (!t || r & /*$$scope*/
      1) && vi(
        i,
        l,
        s,
        /*$$scope*/
        s[0],
        t ? Ti(
          l,
          /*$$scope*/
          s[0],
          r,
          null
        ) : wi(
          /*$$scope*/
          s[0]
        ),
        null
      );
    },
    i(s) {
      t || (yi(i, s), t = !0);
    },
    o(s) {
      Si(i, s), t = !1;
    },
    d(s) {
      s && pi(e), i && i.d(s);
    }
  };
}
function Ri(n, e, t) {
  let { $$slots: l = {}, $$scope: i } = e;
  return n.$$set = (s) => {
    "$$scope" in s && t(0, i = s.$$scope);
  }, [i, l];
}
class Ci extends mi {
  constructor(e) {
    super(), Ei(this, e, Ri, Li, ki, {});
  }
}
const {
  SvelteComponent: Ni,
  attr: Nn,
  check_outros: Oi,
  create_component: Di,
  create_slot: Mi,
  destroy_component: Ii,
  detach: Mt,
  element: Pi,
  empty: Fi,
  get_all_dirty_from_scope: Ui,
  get_slot_changes: zi,
  group_outros: Hi,
  init: Bi,
  insert: It,
  mount_component: Gi,
  safe_not_equal: Wi,
  set_data: qi,
  space: Vi,
  text: Yi,
  toggle_class: Je,
  transition_in: ht,
  transition_out: Pt,
  update_slot_base: ji
} = window.__gradio__svelte__internal;
function On(n) {
  let e, t;
  return e = new Ci({
    props: {
      $$slots: { default: [Xi] },
      $$scope: { ctx: n }
    }
  }), {
    c() {
      Di(e.$$.fragment);
    },
    m(l, i) {
      Gi(e, l, i), t = !0;
    },
    p(l, i) {
      const s = {};
      i & /*$$scope, info*/
      10 && (s.$$scope = { dirty: i, ctx: l }), e.$set(s);
    },
    i(l) {
      t || (ht(e.$$.fragment, l), t = !0);
    },
    o(l) {
      Pt(e.$$.fragment, l), t = !1;
    },
    d(l) {
      Ii(e, l);
    }
  };
}
function Xi(n) {
  let e;
  return {
    c() {
      e = Yi(
        /*info*/
        n[1]
      );
    },
    m(t, l) {
      It(t, e, l);
    },
    p(t, l) {
      l & /*info*/
      2 && qi(
        e,
        /*info*/
        t[1]
      );
    },
    d(t) {
      t && Mt(e);
    }
  };
}
function Zi(n) {
  let e, t, l, i;
  const s = (
    /*#slots*/
    n[2].default
  ), r = Mi(
    s,
    n,
    /*$$scope*/
    n[3],
    null
  );
  let a = (
    /*info*/
    n[1] && On(n)
  );
  return {
    c() {
      e = Pi("span"), r && r.c(), t = Vi(), a && a.c(), l = Fi(), Nn(e, "data-testid", "block-info"), Nn(e, "class", "svelte-22c38v"), Je(e, "sr-only", !/*show_label*/
      n[0]), Je(e, "hide", !/*show_label*/
      n[0]), Je(
        e,
        "has-info",
        /*info*/
        n[1] != null
      );
    },
    m(o, f) {
      It(o, e, f), r && r.m(e, null), It(o, t, f), a && a.m(o, f), It(o, l, f), i = !0;
    },
    p(o, [f]) {
      r && r.p && (!i || f & /*$$scope*/
      8) && ji(
        r,
        s,
        o,
        /*$$scope*/
        o[3],
        i ? zi(
          s,
          /*$$scope*/
          o[3],
          f,
          null
        ) : Ui(
          /*$$scope*/
          o[3]
        ),
        null
      ), (!i || f & /*show_label*/
      1) && Je(e, "sr-only", !/*show_label*/
      o[0]), (!i || f & /*show_label*/
      1) && Je(e, "hide", !/*show_label*/
      o[0]), (!i || f & /*info*/
      2) && Je(
        e,
        "has-info",
        /*info*/
        o[1] != null
      ), /*info*/
      o[1] ? a ? (a.p(o, f), f & /*info*/
      2 && ht(a, 1)) : (a = On(o), a.c(), ht(a, 1), a.m(l.parentNode, l)) : a && (Hi(), Pt(a, 1, 1, () => {
        a = null;
      }), Oi());
    },
    i(o) {
      i || (ht(r, o), ht(a), i = !0);
    },
    o(o) {
      Pt(r, o), Pt(a), i = !1;
    },
    d(o) {
      o && (Mt(e), Mt(t), Mt(l)), r && r.d(o), a && a.d(o);
    }
  };
}
function Ki(n, e, t) {
  let { $$slots: l = {}, $$scope: i } = e, { show_label: s = !0 } = e, { info: r = void 0 } = e;
  return n.$$set = (a) => {
    "show_label" in a && t(0, s = a.show_label), "info" in a && t(1, r = a.info), "$$scope" in a && t(3, i = a.$$scope);
  }, [s, r, l, i];
}
class Ji extends Ni {
  constructor(e) {
    super(), Bi(this, e, Ki, Zi, Wi, { show_label: 0, info: 1 });
  }
}
const {
  SvelteComponent: Qi,
  append: $t,
  attr: Ce,
  bubble: xi,
  create_component: $i,
  destroy_component: eo,
  detach: vl,
  element: en,
  init: to,
  insert: Ll,
  listen: no,
  mount_component: lo,
  safe_not_equal: io,
  set_data: oo,
  set_style: Qe,
  space: so,
  text: ro,
  toggle_class: ee,
  transition_in: ao,
  transition_out: fo
} = window.__gradio__svelte__internal;
function Dn(n) {
  let e, t;
  return {
    c() {
      e = en("span"), t = ro(
        /*label*/
        n[1]
      ), Ce(e, "class", "svelte-1lrphxw");
    },
    m(l, i) {
      Ll(l, e, i), $t(e, t);
    },
    p(l, i) {
      i & /*label*/
      2 && oo(
        t,
        /*label*/
        l[1]
      );
    },
    d(l) {
      l && vl(e);
    }
  };
}
function co(n) {
  let e, t, l, i, s, r, a, o = (
    /*show_label*/
    n[2] && Dn(n)
  );
  return i = new /*Icon*/
  n[0]({}), {
    c() {
      e = en("button"), o && o.c(), t = so(), l = en("div"), $i(i.$$.fragment), Ce(l, "class", "svelte-1lrphxw"), ee(
        l,
        "small",
        /*size*/
        n[4] === "small"
      ), ee(
        l,
        "large",
        /*size*/
        n[4] === "large"
      ), ee(
        l,
        "medium",
        /*size*/
        n[4] === "medium"
      ), e.disabled = /*disabled*/
      n[7], Ce(
        e,
        "aria-label",
        /*label*/
        n[1]
      ), Ce(
        e,
        "aria-haspopup",
        /*hasPopup*/
        n[8]
      ), Ce(
        e,
        "title",
        /*label*/
        n[1]
      ), Ce(e, "class", "svelte-1lrphxw"), ee(
        e,
        "pending",
        /*pending*/
        n[3]
      ), ee(
        e,
        "padded",
        /*padded*/
        n[5]
      ), ee(
        e,
        "highlight",
        /*highlight*/
        n[6]
      ), ee(
        e,
        "transparent",
        /*transparent*/
        n[9]
      ), Qe(e, "color", !/*disabled*/
      n[7] && /*_color*/
      n[12] ? (
        /*_color*/
        n[12]
      ) : "var(--block-label-text-color)"), Qe(e, "--bg-color", /*disabled*/
      n[7] ? "auto" : (
        /*background*/
        n[10]
      )), Qe(
        e,
        "margin-left",
        /*offset*/
        n[11] + "px"
      );
    },
    m(f, u) {
      Ll(f, e, u), o && o.m(e, null), $t(e, t), $t(e, l), lo(i, l, null), s = !0, r || (a = no(
        e,
        "click",
        /*click_handler*/
        n[14]
      ), r = !0);
    },
    p(f, [u]) {
      /*show_label*/
      f[2] ? o ? o.p(f, u) : (o = Dn(f), o.c(), o.m(e, t)) : o && (o.d(1), o = null), (!s || u & /*size*/
      16) && ee(
        l,
        "small",
        /*size*/
        f[4] === "small"
      ), (!s || u & /*size*/
      16) && ee(
        l,
        "large",
        /*size*/
        f[4] === "large"
      ), (!s || u & /*size*/
      16) && ee(
        l,
        "medium",
        /*size*/
        f[4] === "medium"
      ), (!s || u & /*disabled*/
      128) && (e.disabled = /*disabled*/
      f[7]), (!s || u & /*label*/
      2) && Ce(
        e,
        "aria-label",
        /*label*/
        f[1]
      ), (!s || u & /*hasPopup*/
      256) && Ce(
        e,
        "aria-haspopup",
        /*hasPopup*/
        f[8]
      ), (!s || u & /*label*/
      2) && Ce(
        e,
        "title",
        /*label*/
        f[1]
      ), (!s || u & /*pending*/
      8) && ee(
        e,
        "pending",
        /*pending*/
        f[3]
      ), (!s || u & /*padded*/
      32) && ee(
        e,
        "padded",
        /*padded*/
        f[5]
      ), (!s || u & /*highlight*/
      64) && ee(
        e,
        "highlight",
        /*highlight*/
        f[6]
      ), (!s || u & /*transparent*/
      512) && ee(
        e,
        "transparent",
        /*transparent*/
        f[9]
      ), u & /*disabled, _color*/
      4224 && Qe(e, "color", !/*disabled*/
      f[7] && /*_color*/
      f[12] ? (
        /*_color*/
        f[12]
      ) : "var(--block-label-text-color)"), u & /*disabled, background*/
      1152 && Qe(e, "--bg-color", /*disabled*/
      f[7] ? "auto" : (
        /*background*/
        f[10]
      )), u & /*offset*/
      2048 && Qe(
        e,
        "margin-left",
        /*offset*/
        f[11] + "px"
      );
    },
    i(f) {
      s || (ao(i.$$.fragment, f), s = !0);
    },
    o(f) {
      fo(i.$$.fragment, f), s = !1;
    },
    d(f) {
      f && vl(e), o && o.d(), eo(i), r = !1, a();
    }
  };
}
function uo(n, e, t) {
  let l, { Icon: i } = e, { label: s = "" } = e, { show_label: r = !1 } = e, { pending: a = !1 } = e, { size: o = "small" } = e, { padded: f = !0 } = e, { highlight: u = !1 } = e, { disabled: m = !1 } = e, { hasPopup: E = !1 } = e, { color: b = "var(--block-label-text-color)" } = e, { transparent: k = !1 } = e, { background: R = "var(--background-fill-primary)" } = e, { offset: y = 0 } = e;
  function N(g) {
    xi.call(this, n, g);
  }
  return n.$$set = (g) => {
    "Icon" in g && t(0, i = g.Icon), "label" in g && t(1, s = g.label), "show_label" in g && t(2, r = g.show_label), "pending" in g && t(3, a = g.pending), "size" in g && t(4, o = g.size), "padded" in g && t(5, f = g.padded), "highlight" in g && t(6, u = g.highlight), "disabled" in g && t(7, m = g.disabled), "hasPopup" in g && t(8, E = g.hasPopup), "color" in g && t(13, b = g.color), "transparent" in g && t(9, k = g.transparent), "background" in g && t(10, R = g.background), "offset" in g && t(11, y = g.offset);
  }, n.$$.update = () => {
    n.$$.dirty & /*highlight, color*/
    8256 && t(12, l = u ? "var(--color-accent)" : b);
  }, [
    i,
    s,
    r,
    a,
    o,
    f,
    u,
    m,
    E,
    k,
    R,
    y,
    l,
    b,
    N
  ];
}
class _o extends Qi {
  constructor(e) {
    super(), to(this, e, uo, co, io, {
      Icon: 0,
      label: 1,
      show_label: 2,
      pending: 3,
      size: 4,
      padded: 5,
      highlight: 6,
      disabled: 7,
      hasPopup: 8,
      color: 13,
      transparent: 9,
      background: 10,
      offset: 11
    });
  }
}
const {
  SvelteComponent: mo,
  append: Yt,
  attr: ue,
  detach: go,
  init: ho,
  insert: po,
  noop: jt,
  safe_not_equal: bo,
  set_style: ke,
  svg_element: vt
} = window.__gradio__svelte__internal;
function wo(n) {
  let e, t, l, i;
  return {
    c() {
      e = vt("svg"), t = vt("g"), l = vt("path"), i = vt("path"), ue(l, "d", "M18,6L6.087,17.913"), ke(l, "fill", "none"), ke(l, "fill-rule", "nonzero"), ke(l, "stroke-width", "2px"), ue(t, "transform", "matrix(1.14096,-0.140958,-0.140958,1.14096,-0.0559523,0.0559523)"), ue(i, "d", "M4.364,4.364L19.636,19.636"), ke(i, "fill", "none"), ke(i, "fill-rule", "nonzero"), ke(i, "stroke-width", "2px"), ue(e, "width", "100%"), ue(e, "height", "100%"), ue(e, "viewBox", "0 0 24 24"), ue(e, "version", "1.1"), ue(e, "xmlns", "http://www.w3.org/2000/svg"), ue(e, "xmlns:xlink", "http://www.w3.org/1999/xlink"), ue(e, "xml:space", "preserve"), ue(e, "stroke", "currentColor"), ke(e, "fill-rule", "evenodd"), ke(e, "clip-rule", "evenodd"), ke(e, "stroke-linecap", "round"), ke(e, "stroke-linejoin", "round");
    },
    m(s, r) {
      po(s, e, r), Yt(e, t), Yt(t, l), Yt(e, i);
    },
    p: jt,
    i: jt,
    o: jt,
    d(s) {
      s && go(e);
    }
  };
}
class To extends mo {
  constructor(e) {
    super(), ho(this, e, null, wo, bo, {});
  }
}
const Eo = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], Mn = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
Eo.reduce(
  (n, { color: e, primary: t, secondary: l }) => ({
    ...n,
    [e]: {
      primary: Mn[e][t],
      secondary: Mn[e][l]
    }
  }),
  {}
);
function $e(n) {
  let e = ["", "k", "M", "G", "T", "P", "E", "Z"], t = 0;
  for (; n > 1e3 && t < e.length - 1; )
    n /= 1e3, t++;
  let l = e[t];
  return (Number.isInteger(n) ? n : n.toFixed(1)) + l;
}
function Ft() {
}
function Ao(n, e) {
  return n != n ? e == e : n !== e || n && typeof n == "object" || typeof n == "function";
}
const Rl = typeof window < "u";
let In = Rl ? () => window.performance.now() : () => Date.now(), Cl = Rl ? (n) => requestAnimationFrame(n) : Ft;
const et = /* @__PURE__ */ new Set();
function Nl(n) {
  et.forEach((e) => {
    e.c(n) || (et.delete(e), e.f());
  }), et.size !== 0 && Cl(Nl);
}
function ko(n) {
  let e;
  return et.size === 0 && Cl(Nl), {
    promise: new Promise((t) => {
      et.add(e = { c: n, f: t });
    }),
    abort() {
      et.delete(e);
    }
  };
}
const xe = [];
function yo(n, e = Ft) {
  let t;
  const l = /* @__PURE__ */ new Set();
  function i(a) {
    if (Ao(n, a) && (n = a, t)) {
      const o = !xe.length;
      for (const f of l)
        f[1](), xe.push(f, n);
      if (o) {
        for (let f = 0; f < xe.length; f += 2)
          xe[f][0](xe[f + 1]);
        xe.length = 0;
      }
    }
  }
  function s(a) {
    i(a(n));
  }
  function r(a, o = Ft) {
    const f = [a, o];
    return l.add(f), l.size === 1 && (t = e(i, s) || Ft), a(n), () => {
      l.delete(f), l.size === 0 && t && (t(), t = null);
    };
  }
  return { set: i, update: s, subscribe: r };
}
function Pn(n) {
  return Object.prototype.toString.call(n) === "[object Date]";
}
function tn(n, e, t, l) {
  if (typeof t == "number" || Pn(t)) {
    const i = l - t, s = (t - e) / (n.dt || 1 / 60), r = n.opts.stiffness * i, a = n.opts.damping * s, o = (r - a) * n.inv_mass, f = (s + o) * n.dt;
    return Math.abs(f) < n.opts.precision && Math.abs(i) < n.opts.precision ? l : (n.settled = !1, Pn(t) ? new Date(t.getTime() + f) : t + f);
  } else {
    if (Array.isArray(t))
      return t.map(
        (i, s) => tn(n, e[s], t[s], l[s])
      );
    if (typeof t == "object") {
      const i = {};
      for (const s in t)
        i[s] = tn(n, e[s], t[s], l[s]);
      return i;
    } else
      throw new Error(`Cannot spring ${typeof t} values`);
  }
}
function Fn(n, e = {}) {
  const t = yo(n), { stiffness: l = 0.15, damping: i = 0.8, precision: s = 0.01 } = e;
  let r, a, o, f = n, u = n, m = 1, E = 0, b = !1;
  function k(y, N = {}) {
    u = y;
    const g = o = {};
    return n == null || N.hard || R.stiffness >= 1 && R.damping >= 1 ? (b = !0, r = In(), f = y, t.set(n = u), Promise.resolve()) : (N.soft && (E = 1 / ((N.soft === !0 ? 0.5 : +N.soft) * 60), m = 0), a || (r = In(), b = !1, a = ko((h) => {
      if (b)
        return b = !1, a = null, !1;
      m = Math.min(m + E, 1);
      const w = {
        inv_mass: m,
        opts: R,
        settled: !0,
        dt: (h - r) * 60 / 1e3
      }, F = tn(w, f, n, u);
      return r = h, f = n, t.set(n = F), w.settled && (a = null), !w.settled;
    })), new Promise((h) => {
      a.promise.then(() => {
        g === o && h();
      });
    }));
  }
  const R = {
    set: k,
    update: (y, N) => k(y(u, n), N),
    subscribe: t.subscribe,
    stiffness: l,
    damping: i,
    precision: s
  };
  return R;
}
const {
  SvelteComponent: So,
  append: _e,
  attr: O,
  component_subscribe: Un,
  detach: vo,
  element: Lo,
  init: Ro,
  insert: Co,
  noop: zn,
  safe_not_equal: No,
  set_style: Lt,
  svg_element: de,
  toggle_class: Hn
} = window.__gradio__svelte__internal, { onMount: Oo } = window.__gradio__svelte__internal;
function Do(n) {
  let e, t, l, i, s, r, a, o, f, u, m, E;
  return {
    c() {
      e = Lo("div"), t = de("svg"), l = de("g"), i = de("path"), s = de("path"), r = de("path"), a = de("path"), o = de("g"), f = de("path"), u = de("path"), m = de("path"), E = de("path"), O(i, "d", "M255.926 0.754768L509.702 139.936V221.027L255.926 81.8465V0.754768Z"), O(i, "fill", "#FF7C00"), O(i, "fill-opacity", "0.4"), O(i, "class", "svelte-43sxxs"), O(s, "d", "M509.69 139.936L254.981 279.641V361.255L509.69 221.55V139.936Z"), O(s, "fill", "#FF7C00"), O(s, "class", "svelte-43sxxs"), O(r, "d", "M0.250138 139.937L254.981 279.641V361.255L0.250138 221.55V139.937Z"), O(r, "fill", "#FF7C00"), O(r, "fill-opacity", "0.4"), O(r, "class", "svelte-43sxxs"), O(a, "d", "M255.923 0.232622L0.236328 139.936V221.55L255.923 81.8469V0.232622Z"), O(a, "fill", "#FF7C00"), O(a, "class", "svelte-43sxxs"), Lt(l, "transform", "translate(" + /*$top*/
      n[1][0] + "px, " + /*$top*/
      n[1][1] + "px)"), O(f, "d", "M255.926 141.5L509.702 280.681V361.773L255.926 222.592V141.5Z"), O(f, "fill", "#FF7C00"), O(f, "fill-opacity", "0.4"), O(f, "class", "svelte-43sxxs"), O(u, "d", "M509.69 280.679L254.981 420.384V501.998L509.69 362.293V280.679Z"), O(u, "fill", "#FF7C00"), O(u, "class", "svelte-43sxxs"), O(m, "d", "M0.250138 280.681L254.981 420.386V502L0.250138 362.295V280.681Z"), O(m, "fill", "#FF7C00"), O(m, "fill-opacity", "0.4"), O(m, "class", "svelte-43sxxs"), O(E, "d", "M255.923 140.977L0.236328 280.68V362.294L255.923 222.591V140.977Z"), O(E, "fill", "#FF7C00"), O(E, "class", "svelte-43sxxs"), Lt(o, "transform", "translate(" + /*$bottom*/
      n[2][0] + "px, " + /*$bottom*/
      n[2][1] + "px)"), O(t, "viewBox", "-1200 -1200 3000 3000"), O(t, "fill", "none"), O(t, "xmlns", "http://www.w3.org/2000/svg"), O(t, "class", "svelte-43sxxs"), O(e, "class", "svelte-43sxxs"), Hn(
        e,
        "margin",
        /*margin*/
        n[0]
      );
    },
    m(b, k) {
      Co(b, e, k), _e(e, t), _e(t, l), _e(l, i), _e(l, s), _e(l, r), _e(l, a), _e(t, o), _e(o, f), _e(o, u), _e(o, m), _e(o, E);
    },
    p(b, [k]) {
      k & /*$top*/
      2 && Lt(l, "transform", "translate(" + /*$top*/
      b[1][0] + "px, " + /*$top*/
      b[1][1] + "px)"), k & /*$bottom*/
      4 && Lt(o, "transform", "translate(" + /*$bottom*/
      b[2][0] + "px, " + /*$bottom*/
      b[2][1] + "px)"), k & /*margin*/
      1 && Hn(
        e,
        "margin",
        /*margin*/
        b[0]
      );
    },
    i: zn,
    o: zn,
    d(b) {
      b && vo(e);
    }
  };
}
function Mo(n, e, t) {
  let l, i;
  var s = this && this.__awaiter || function(b, k, R, y) {
    function N(g) {
      return g instanceof R ? g : new R(function(h) {
        h(g);
      });
    }
    return new (R || (R = Promise))(function(g, h) {
      function w(M) {
        try {
          _(y.next(M));
        } catch (q) {
          h(q);
        }
      }
      function F(M) {
        try {
          _(y.throw(M));
        } catch (q) {
          h(q);
        }
      }
      function _(M) {
        M.done ? g(M.value) : N(M.value).then(w, F);
      }
      _((y = y.apply(b, k || [])).next());
    });
  };
  let { margin: r = !0 } = e;
  const a = Fn([0, 0]);
  Un(n, a, (b) => t(1, l = b));
  const o = Fn([0, 0]);
  Un(n, o, (b) => t(2, i = b));
  let f;
  function u() {
    return s(this, void 0, void 0, function* () {
      yield Promise.all([a.set([125, 140]), o.set([-125, -140])]), yield Promise.all([a.set([-125, 140]), o.set([125, -140])]), yield Promise.all([a.set([-125, 0]), o.set([125, -0])]), yield Promise.all([a.set([125, 0]), o.set([-125, 0])]);
    });
  }
  function m() {
    return s(this, void 0, void 0, function* () {
      yield u(), f || m();
    });
  }
  function E() {
    return s(this, void 0, void 0, function* () {
      yield Promise.all([a.set([125, 0]), o.set([-125, 0])]), m();
    });
  }
  return Oo(() => (E(), () => f = !0)), n.$$set = (b) => {
    "margin" in b && t(0, r = b.margin);
  }, [r, l, i, a, o];
}
class Io extends So {
  constructor(e) {
    super(), Ro(this, e, Mo, Do, No, { margin: 0 });
  }
}
const {
  SvelteComponent: Po,
  append: Be,
  attr: be,
  binding_callbacks: Bn,
  check_outros: nn,
  create_component: Ol,
  create_slot: Dl,
  destroy_component: Ml,
  destroy_each: Il,
  detach: S,
  element: ye,
  empty: it,
  ensure_array_like: Ht,
  get_all_dirty_from_scope: Pl,
  get_slot_changes: Fl,
  group_outros: ln,
  init: Fo,
  insert: v,
  mount_component: Ul,
  noop: on,
  safe_not_equal: Uo,
  set_data: re,
  set_style: Me,
  space: se,
  text: G,
  toggle_class: oe,
  transition_in: ge,
  transition_out: Se,
  update_slot_base: zl
} = window.__gradio__svelte__internal, { tick: zo } = window.__gradio__svelte__internal, { onDestroy: Ho } = window.__gradio__svelte__internal, { createEventDispatcher: Bo } = window.__gradio__svelte__internal, Go = (n) => ({}), Gn = (n) => ({}), Wo = (n) => ({}), Wn = (n) => ({});
function qn(n, e, t) {
  const l = n.slice();
  return l[41] = e[t], l[43] = t, l;
}
function Vn(n, e, t) {
  const l = n.slice();
  return l[41] = e[t], l;
}
function qo(n) {
  let e, t, l, i, s = (
    /*i18n*/
    n[1]("common.error") + ""
  ), r, a, o;
  t = new _o({
    props: {
      Icon: To,
      label: (
        /*i18n*/
        n[1]("common.clear")
      ),
      disabled: !1
    }
  }), t.$on(
    "click",
    /*click_handler*/
    n[32]
  );
  const f = (
    /*#slots*/
    n[30].error
  ), u = Dl(
    f,
    n,
    /*$$scope*/
    n[29],
    Gn
  );
  return {
    c() {
      e = ye("div"), Ol(t.$$.fragment), l = se(), i = ye("span"), r = G(s), a = se(), u && u.c(), be(e, "class", "clear-status svelte-v0wucf"), be(i, "class", "error svelte-v0wucf");
    },
    m(m, E) {
      v(m, e, E), Ul(t, e, null), v(m, l, E), v(m, i, E), Be(i, r), v(m, a, E), u && u.m(m, E), o = !0;
    },
    p(m, E) {
      const b = {};
      E[0] & /*i18n*/
      2 && (b.label = /*i18n*/
      m[1]("common.clear")), t.$set(b), (!o || E[0] & /*i18n*/
      2) && s !== (s = /*i18n*/
      m[1]("common.error") + "") && re(r, s), u && u.p && (!o || E[0] & /*$$scope*/
      536870912) && zl(
        u,
        f,
        m,
        /*$$scope*/
        m[29],
        o ? Fl(
          f,
          /*$$scope*/
          m[29],
          E,
          Go
        ) : Pl(
          /*$$scope*/
          m[29]
        ),
        Gn
      );
    },
    i(m) {
      o || (ge(t.$$.fragment, m), ge(u, m), o = !0);
    },
    o(m) {
      Se(t.$$.fragment, m), Se(u, m), o = !1;
    },
    d(m) {
      m && (S(e), S(l), S(i), S(a)), Ml(t), u && u.d(m);
    }
  };
}
function Vo(n) {
  let e, t, l, i, s, r, a, o, f, u = (
    /*variant*/
    n[8] === "default" && /*show_eta_bar*/
    n[18] && /*show_progress*/
    n[6] === "full" && Yn(n)
  );
  function m(h, w) {
    if (
      /*progress*/
      h[7]
    ) return Xo;
    if (
      /*queue_position*/
      h[2] !== null && /*queue_size*/
      h[3] !== void 0 && /*queue_position*/
      h[2] >= 0
    ) return jo;
    if (
      /*queue_position*/
      h[2] === 0
    ) return Yo;
  }
  let E = m(n), b = E && E(n), k = (
    /*timer*/
    n[5] && Zn(n)
  );
  const R = [Qo, Jo], y = [];
  function N(h, w) {
    return (
      /*last_progress_level*/
      h[15] != null ? 0 : (
        /*show_progress*/
        h[6] === "full" ? 1 : -1
      )
    );
  }
  ~(s = N(n)) && (r = y[s] = R[s](n));
  let g = !/*timer*/
  n[5] && tl(n);
  return {
    c() {
      u && u.c(), e = se(), t = ye("div"), b && b.c(), l = se(), k && k.c(), i = se(), r && r.c(), a = se(), g && g.c(), o = it(), be(t, "class", "progress-text svelte-v0wucf"), oe(
        t,
        "meta-text-center",
        /*variant*/
        n[8] === "center"
      ), oe(
        t,
        "meta-text",
        /*variant*/
        n[8] === "default"
      );
    },
    m(h, w) {
      u && u.m(h, w), v(h, e, w), v(h, t, w), b && b.m(t, null), Be(t, l), k && k.m(t, null), v(h, i, w), ~s && y[s].m(h, w), v(h, a, w), g && g.m(h, w), v(h, o, w), f = !0;
    },
    p(h, w) {
      /*variant*/
      h[8] === "default" && /*show_eta_bar*/
      h[18] && /*show_progress*/
      h[6] === "full" ? u ? u.p(h, w) : (u = Yn(h), u.c(), u.m(e.parentNode, e)) : u && (u.d(1), u = null), E === (E = m(h)) && b ? b.p(h, w) : (b && b.d(1), b = E && E(h), b && (b.c(), b.m(t, l))), /*timer*/
      h[5] ? k ? k.p(h, w) : (k = Zn(h), k.c(), k.m(t, null)) : k && (k.d(1), k = null), (!f || w[0] & /*variant*/
      256) && oe(
        t,
        "meta-text-center",
        /*variant*/
        h[8] === "center"
      ), (!f || w[0] & /*variant*/
      256) && oe(
        t,
        "meta-text",
        /*variant*/
        h[8] === "default"
      );
      let F = s;
      s = N(h), s === F ? ~s && y[s].p(h, w) : (r && (ln(), Se(y[F], 1, 1, () => {
        y[F] = null;
      }), nn()), ~s ? (r = y[s], r ? r.p(h, w) : (r = y[s] = R[s](h), r.c()), ge(r, 1), r.m(a.parentNode, a)) : r = null), /*timer*/
      h[5] ? g && (ln(), Se(g, 1, 1, () => {
        g = null;
      }), nn()) : g ? (g.p(h, w), w[0] & /*timer*/
      32 && ge(g, 1)) : (g = tl(h), g.c(), ge(g, 1), g.m(o.parentNode, o));
    },
    i(h) {
      f || (ge(r), ge(g), f = !0);
    },
    o(h) {
      Se(r), Se(g), f = !1;
    },
    d(h) {
      h && (S(e), S(t), S(i), S(a), S(o)), u && u.d(h), b && b.d(), k && k.d(), ~s && y[s].d(h), g && g.d(h);
    }
  };
}
function Yn(n) {
  let e, t = `translateX(${/*eta_level*/
  (n[17] || 0) * 100 - 100}%)`;
  return {
    c() {
      e = ye("div"), be(e, "class", "eta-bar svelte-v0wucf"), Me(e, "transform", t);
    },
    m(l, i) {
      v(l, e, i);
    },
    p(l, i) {
      i[0] & /*eta_level*/
      131072 && t !== (t = `translateX(${/*eta_level*/
      (l[17] || 0) * 100 - 100}%)`) && Me(e, "transform", t);
    },
    d(l) {
      l && S(e);
    }
  };
}
function Yo(n) {
  let e;
  return {
    c() {
      e = G("processing |");
    },
    m(t, l) {
      v(t, e, l);
    },
    p: on,
    d(t) {
      t && S(e);
    }
  };
}
function jo(n) {
  let e, t = (
    /*queue_position*/
    n[2] + 1 + ""
  ), l, i, s, r;
  return {
    c() {
      e = G("queue: "), l = G(t), i = G("/"), s = G(
        /*queue_size*/
        n[3]
      ), r = G(" |");
    },
    m(a, o) {
      v(a, e, o), v(a, l, o), v(a, i, o), v(a, s, o), v(a, r, o);
    },
    p(a, o) {
      o[0] & /*queue_position*/
      4 && t !== (t = /*queue_position*/
      a[2] + 1 + "") && re(l, t), o[0] & /*queue_size*/
      8 && re(
        s,
        /*queue_size*/
        a[3]
      );
    },
    d(a) {
      a && (S(e), S(l), S(i), S(s), S(r));
    }
  };
}
function Xo(n) {
  let e, t = Ht(
    /*progress*/
    n[7]
  ), l = [];
  for (let i = 0; i < t.length; i += 1)
    l[i] = Xn(Vn(n, t, i));
  return {
    c() {
      for (let i = 0; i < l.length; i += 1)
        l[i].c();
      e = it();
    },
    m(i, s) {
      for (let r = 0; r < l.length; r += 1)
        l[r] && l[r].m(i, s);
      v(i, e, s);
    },
    p(i, s) {
      if (s[0] & /*progress*/
      128) {
        t = Ht(
          /*progress*/
          i[7]
        );
        let r;
        for (r = 0; r < t.length; r += 1) {
          const a = Vn(i, t, r);
          l[r] ? l[r].p(a, s) : (l[r] = Xn(a), l[r].c(), l[r].m(e.parentNode, e));
        }
        for (; r < l.length; r += 1)
          l[r].d(1);
        l.length = t.length;
      }
    },
    d(i) {
      i && S(e), Il(l, i);
    }
  };
}
function jn(n) {
  let e, t = (
    /*p*/
    n[41].unit + ""
  ), l, i, s = " ", r;
  function a(u, m) {
    return (
      /*p*/
      u[41].length != null ? Ko : Zo
    );
  }
  let o = a(n), f = o(n);
  return {
    c() {
      f.c(), e = se(), l = G(t), i = G(" | "), r = G(s);
    },
    m(u, m) {
      f.m(u, m), v(u, e, m), v(u, l, m), v(u, i, m), v(u, r, m);
    },
    p(u, m) {
      o === (o = a(u)) && f ? f.p(u, m) : (f.d(1), f = o(u), f && (f.c(), f.m(e.parentNode, e))), m[0] & /*progress*/
      128 && t !== (t = /*p*/
      u[41].unit + "") && re(l, t);
    },
    d(u) {
      u && (S(e), S(l), S(i), S(r)), f.d(u);
    }
  };
}
function Zo(n) {
  let e = $e(
    /*p*/
    n[41].index || 0
  ) + "", t;
  return {
    c() {
      t = G(e);
    },
    m(l, i) {
      v(l, t, i);
    },
    p(l, i) {
      i[0] & /*progress*/
      128 && e !== (e = $e(
        /*p*/
        l[41].index || 0
      ) + "") && re(t, e);
    },
    d(l) {
      l && S(t);
    }
  };
}
function Ko(n) {
  let e = $e(
    /*p*/
    n[41].index || 0
  ) + "", t, l, i = $e(
    /*p*/
    n[41].length
  ) + "", s;
  return {
    c() {
      t = G(e), l = G("/"), s = G(i);
    },
    m(r, a) {
      v(r, t, a), v(r, l, a), v(r, s, a);
    },
    p(r, a) {
      a[0] & /*progress*/
      128 && e !== (e = $e(
        /*p*/
        r[41].index || 0
      ) + "") && re(t, e), a[0] & /*progress*/
      128 && i !== (i = $e(
        /*p*/
        r[41].length
      ) + "") && re(s, i);
    },
    d(r) {
      r && (S(t), S(l), S(s));
    }
  };
}
function Xn(n) {
  let e, t = (
    /*p*/
    n[41].index != null && jn(n)
  );
  return {
    c() {
      t && t.c(), e = it();
    },
    m(l, i) {
      t && t.m(l, i), v(l, e, i);
    },
    p(l, i) {
      /*p*/
      l[41].index != null ? t ? t.p(l, i) : (t = jn(l), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(l) {
      l && S(e), t && t.d(l);
    }
  };
}
function Zn(n) {
  let e, t = (
    /*eta*/
    n[0] ? `/${/*formatted_eta*/
    n[19]}` : ""
  ), l, i;
  return {
    c() {
      e = G(
        /*formatted_timer*/
        n[20]
      ), l = G(t), i = G("s");
    },
    m(s, r) {
      v(s, e, r), v(s, l, r), v(s, i, r);
    },
    p(s, r) {
      r[0] & /*formatted_timer*/
      1048576 && re(
        e,
        /*formatted_timer*/
        s[20]
      ), r[0] & /*eta, formatted_eta*/
      524289 && t !== (t = /*eta*/
      s[0] ? `/${/*formatted_eta*/
      s[19]}` : "") && re(l, t);
    },
    d(s) {
      s && (S(e), S(l), S(i));
    }
  };
}
function Jo(n) {
  let e, t;
  return e = new Io({
    props: { margin: (
      /*variant*/
      n[8] === "default"
    ) }
  }), {
    c() {
      Ol(e.$$.fragment);
    },
    m(l, i) {
      Ul(e, l, i), t = !0;
    },
    p(l, i) {
      const s = {};
      i[0] & /*variant*/
      256 && (s.margin = /*variant*/
      l[8] === "default"), e.$set(s);
    },
    i(l) {
      t || (ge(e.$$.fragment, l), t = !0);
    },
    o(l) {
      Se(e.$$.fragment, l), t = !1;
    },
    d(l) {
      Ml(e, l);
    }
  };
}
function Qo(n) {
  let e, t, l, i, s, r = `${/*last_progress_level*/
  n[15] * 100}%`, a = (
    /*progress*/
    n[7] != null && Kn(n)
  );
  return {
    c() {
      e = ye("div"), t = ye("div"), a && a.c(), l = se(), i = ye("div"), s = ye("div"), be(t, "class", "progress-level-inner svelte-v0wucf"), be(s, "class", "progress-bar svelte-v0wucf"), Me(s, "width", r), be(i, "class", "progress-bar-wrap svelte-v0wucf"), be(e, "class", "progress-level svelte-v0wucf");
    },
    m(o, f) {
      v(o, e, f), Be(e, t), a && a.m(t, null), Be(e, l), Be(e, i), Be(i, s), n[31](s);
    },
    p(o, f) {
      /*progress*/
      o[7] != null ? a ? a.p(o, f) : (a = Kn(o), a.c(), a.m(t, null)) : a && (a.d(1), a = null), f[0] & /*last_progress_level*/
      32768 && r !== (r = `${/*last_progress_level*/
      o[15] * 100}%`) && Me(s, "width", r);
    },
    i: on,
    o: on,
    d(o) {
      o && S(e), a && a.d(), n[31](null);
    }
  };
}
function Kn(n) {
  let e, t = Ht(
    /*progress*/
    n[7]
  ), l = [];
  for (let i = 0; i < t.length; i += 1)
    l[i] = el(qn(n, t, i));
  return {
    c() {
      for (let i = 0; i < l.length; i += 1)
        l[i].c();
      e = it();
    },
    m(i, s) {
      for (let r = 0; r < l.length; r += 1)
        l[r] && l[r].m(i, s);
      v(i, e, s);
    },
    p(i, s) {
      if (s[0] & /*progress_level, progress*/
      16512) {
        t = Ht(
          /*progress*/
          i[7]
        );
        let r;
        for (r = 0; r < t.length; r += 1) {
          const a = qn(i, t, r);
          l[r] ? l[r].p(a, s) : (l[r] = el(a), l[r].c(), l[r].m(e.parentNode, e));
        }
        for (; r < l.length; r += 1)
          l[r].d(1);
        l.length = t.length;
      }
    },
    d(i) {
      i && S(e), Il(l, i);
    }
  };
}
function Jn(n) {
  let e, t, l, i, s = (
    /*i*/
    n[43] !== 0 && xo()
  ), r = (
    /*p*/
    n[41].desc != null && Qn(n)
  ), a = (
    /*p*/
    n[41].desc != null && /*progress_level*/
    n[14] && /*progress_level*/
    n[14][
      /*i*/
      n[43]
    ] != null && xn()
  ), o = (
    /*progress_level*/
    n[14] != null && $n(n)
  );
  return {
    c() {
      s && s.c(), e = se(), r && r.c(), t = se(), a && a.c(), l = se(), o && o.c(), i = it();
    },
    m(f, u) {
      s && s.m(f, u), v(f, e, u), r && r.m(f, u), v(f, t, u), a && a.m(f, u), v(f, l, u), o && o.m(f, u), v(f, i, u);
    },
    p(f, u) {
      /*p*/
      f[41].desc != null ? r ? r.p(f, u) : (r = Qn(f), r.c(), r.m(t.parentNode, t)) : r && (r.d(1), r = null), /*p*/
      f[41].desc != null && /*progress_level*/
      f[14] && /*progress_level*/
      f[14][
        /*i*/
        f[43]
      ] != null ? a || (a = xn(), a.c(), a.m(l.parentNode, l)) : a && (a.d(1), a = null), /*progress_level*/
      f[14] != null ? o ? o.p(f, u) : (o = $n(f), o.c(), o.m(i.parentNode, i)) : o && (o.d(1), o = null);
    },
    d(f) {
      f && (S(e), S(t), S(l), S(i)), s && s.d(f), r && r.d(f), a && a.d(f), o && o.d(f);
    }
  };
}
function xo(n) {
  let e;
  return {
    c() {
      e = G(" /");
    },
    m(t, l) {
      v(t, e, l);
    },
    d(t) {
      t && S(e);
    }
  };
}
function Qn(n) {
  let e = (
    /*p*/
    n[41].desc + ""
  ), t;
  return {
    c() {
      t = G(e);
    },
    m(l, i) {
      v(l, t, i);
    },
    p(l, i) {
      i[0] & /*progress*/
      128 && e !== (e = /*p*/
      l[41].desc + "") && re(t, e);
    },
    d(l) {
      l && S(t);
    }
  };
}
function xn(n) {
  let e;
  return {
    c() {
      e = G("-");
    },
    m(t, l) {
      v(t, e, l);
    },
    d(t) {
      t && S(e);
    }
  };
}
function $n(n) {
  let e = (100 * /*progress_level*/
  (n[14][
    /*i*/
    n[43]
  ] || 0)).toFixed(1) + "", t, l;
  return {
    c() {
      t = G(e), l = G("%");
    },
    m(i, s) {
      v(i, t, s), v(i, l, s);
    },
    p(i, s) {
      s[0] & /*progress_level*/
      16384 && e !== (e = (100 * /*progress_level*/
      (i[14][
        /*i*/
        i[43]
      ] || 0)).toFixed(1) + "") && re(t, e);
    },
    d(i) {
      i && (S(t), S(l));
    }
  };
}
function el(n) {
  let e, t = (
    /*p*/
    (n[41].desc != null || /*progress_level*/
    n[14] && /*progress_level*/
    n[14][
      /*i*/
      n[43]
    ] != null) && Jn(n)
  );
  return {
    c() {
      t && t.c(), e = it();
    },
    m(l, i) {
      t && t.m(l, i), v(l, e, i);
    },
    p(l, i) {
      /*p*/
      l[41].desc != null || /*progress_level*/
      l[14] && /*progress_level*/
      l[14][
        /*i*/
        l[43]
      ] != null ? t ? t.p(l, i) : (t = Jn(l), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(l) {
      l && S(e), t && t.d(l);
    }
  };
}
function tl(n) {
  let e, t, l, i;
  const s = (
    /*#slots*/
    n[30]["additional-loading-text"]
  ), r = Dl(
    s,
    n,
    /*$$scope*/
    n[29],
    Wn
  );
  return {
    c() {
      e = ye("p"), t = G(
        /*loading_text*/
        n[9]
      ), l = se(), r && r.c(), be(e, "class", "loading svelte-v0wucf");
    },
    m(a, o) {
      v(a, e, o), Be(e, t), v(a, l, o), r && r.m(a, o), i = !0;
    },
    p(a, o) {
      (!i || o[0] & /*loading_text*/
      512) && re(
        t,
        /*loading_text*/
        a[9]
      ), r && r.p && (!i || o[0] & /*$$scope*/
      536870912) && zl(
        r,
        s,
        a,
        /*$$scope*/
        a[29],
        i ? Fl(
          s,
          /*$$scope*/
          a[29],
          o,
          Wo
        ) : Pl(
          /*$$scope*/
          a[29]
        ),
        Wn
      );
    },
    i(a) {
      i || (ge(r, a), i = !0);
    },
    o(a) {
      Se(r, a), i = !1;
    },
    d(a) {
      a && (S(e), S(l)), r && r.d(a);
    }
  };
}
function $o(n) {
  let e, t, l, i, s;
  const r = [Vo, qo], a = [];
  function o(f, u) {
    return (
      /*status*/
      f[4] === "pending" ? 0 : (
        /*status*/
        f[4] === "error" ? 1 : -1
      )
    );
  }
  return ~(t = o(n)) && (l = a[t] = r[t](n)), {
    c() {
      e = ye("div"), l && l.c(), be(e, "class", i = "wrap " + /*variant*/
      n[8] + " " + /*show_progress*/
      n[6] + " svelte-v0wucf"), oe(e, "hide", !/*status*/
      n[4] || /*status*/
      n[4] === "complete" || /*show_progress*/
      n[6] === "hidden"), oe(
        e,
        "translucent",
        /*variant*/
        n[8] === "center" && /*status*/
        (n[4] === "pending" || /*status*/
        n[4] === "error") || /*translucent*/
        n[11] || /*show_progress*/
        n[6] === "minimal"
      ), oe(
        e,
        "generating",
        /*status*/
        n[4] === "generating" && /*show_progress*/
        n[6] === "full"
      ), oe(
        e,
        "border",
        /*border*/
        n[12]
      ), Me(
        e,
        "position",
        /*absolute*/
        n[10] ? "absolute" : "static"
      ), Me(
        e,
        "padding",
        /*absolute*/
        n[10] ? "0" : "var(--size-8) 0"
      );
    },
    m(f, u) {
      v(f, e, u), ~t && a[t].m(e, null), n[33](e), s = !0;
    },
    p(f, u) {
      let m = t;
      t = o(f), t === m ? ~t && a[t].p(f, u) : (l && (ln(), Se(a[m], 1, 1, () => {
        a[m] = null;
      }), nn()), ~t ? (l = a[t], l ? l.p(f, u) : (l = a[t] = r[t](f), l.c()), ge(l, 1), l.m(e, null)) : l = null), (!s || u[0] & /*variant, show_progress*/
      320 && i !== (i = "wrap " + /*variant*/
      f[8] + " " + /*show_progress*/
      f[6] + " svelte-v0wucf")) && be(e, "class", i), (!s || u[0] & /*variant, show_progress, status, show_progress*/
      336) && oe(e, "hide", !/*status*/
      f[4] || /*status*/
      f[4] === "complete" || /*show_progress*/
      f[6] === "hidden"), (!s || u[0] & /*variant, show_progress, variant, status, translucent, show_progress*/
      2384) && oe(
        e,
        "translucent",
        /*variant*/
        f[8] === "center" && /*status*/
        (f[4] === "pending" || /*status*/
        f[4] === "error") || /*translucent*/
        f[11] || /*show_progress*/
        f[6] === "minimal"
      ), (!s || u[0] & /*variant, show_progress, status, show_progress*/
      336) && oe(
        e,
        "generating",
        /*status*/
        f[4] === "generating" && /*show_progress*/
        f[6] === "full"
      ), (!s || u[0] & /*variant, show_progress, border*/
      4416) && oe(
        e,
        "border",
        /*border*/
        f[12]
      ), u[0] & /*absolute*/
      1024 && Me(
        e,
        "position",
        /*absolute*/
        f[10] ? "absolute" : "static"
      ), u[0] & /*absolute*/
      1024 && Me(
        e,
        "padding",
        /*absolute*/
        f[10] ? "0" : "var(--size-8) 0"
      );
    },
    i(f) {
      s || (ge(l), s = !0);
    },
    o(f) {
      Se(l), s = !1;
    },
    d(f) {
      f && S(e), ~t && a[t].d(), n[33](null);
    }
  };
}
var es = function(n, e, t, l) {
  function i(s) {
    return s instanceof t ? s : new t(function(r) {
      r(s);
    });
  }
  return new (t || (t = Promise))(function(s, r) {
    function a(u) {
      try {
        f(l.next(u));
      } catch (m) {
        r(m);
      }
    }
    function o(u) {
      try {
        f(l.throw(u));
      } catch (m) {
        r(m);
      }
    }
    function f(u) {
      u.done ? s(u.value) : i(u.value).then(a, o);
    }
    f((l = l.apply(n, e || [])).next());
  });
};
let Rt = [], Xt = !1;
function ts(n) {
  return es(this, arguments, void 0, function* (e, t = !0) {
    if (!(window.__gradio_mode__ === "website" || window.__gradio_mode__ !== "app" && t !== !0)) {
      if (Rt.push(e), !Xt) Xt = !0;
      else return;
      yield zo(), requestAnimationFrame(() => {
        let l = [0, 0];
        for (let i = 0; i < Rt.length; i++) {
          const r = Rt[i].getBoundingClientRect();
          (i === 0 || r.top + window.scrollY <= l[0]) && (l[0] = r.top + window.scrollY, l[1] = i);
        }
        window.scrollTo({ top: l[0] - 20, behavior: "smooth" }), Xt = !1, Rt = [];
      });
    }
  });
}
function ns(n, e, t) {
  let l, { $$slots: i = {}, $$scope: s } = e;
  this && this.__awaiter;
  const r = Bo();
  let { i18n: a } = e, { eta: o = null } = e, { queue_position: f } = e, { queue_size: u } = e, { status: m } = e, { scroll_to_output: E = !1 } = e, { timer: b = !0 } = e, { show_progress: k = "full" } = e, { message: R = null } = e, { progress: y = null } = e, { variant: N = "default" } = e, { loading_text: g = "Loading..." } = e, { absolute: h = !0 } = e, { translucent: w = !1 } = e, { border: F = !1 } = e, { autoscroll: _ } = e, M, q = !1, z = 0, L = 0, I = null, W = null, ve = 0, x = null, we, H = null, Ie = !0;
  const pt = () => {
    t(0, o = t(27, I = t(19, B = null))), t(25, z = performance.now()), t(26, L = 0), q = !0, bt();
  };
  function bt() {
    requestAnimationFrame(() => {
      t(26, L = (performance.now() - z) / 1e3), q && bt();
    });
  }
  function ot() {
    t(26, L = 0), t(0, o = t(27, I = t(19, B = null))), q && (q = !1);
  }
  Ho(() => {
    q && ot();
  });
  let B = null;
  function wt(p) {
    Bn[p ? "unshift" : "push"](() => {
      H = p, t(16, H), t(7, y), t(14, x), t(15, we);
    });
  }
  const V = () => {
    r("clear_status");
  };
  function Tt(p) {
    Bn[p ? "unshift" : "push"](() => {
      M = p, t(13, M);
    });
  }
  return n.$$set = (p) => {
    "i18n" in p && t(1, a = p.i18n), "eta" in p && t(0, o = p.eta), "queue_position" in p && t(2, f = p.queue_position), "queue_size" in p && t(3, u = p.queue_size), "status" in p && t(4, m = p.status), "scroll_to_output" in p && t(22, E = p.scroll_to_output), "timer" in p && t(5, b = p.timer), "show_progress" in p && t(6, k = p.show_progress), "message" in p && t(23, R = p.message), "progress" in p && t(7, y = p.progress), "variant" in p && t(8, N = p.variant), "loading_text" in p && t(9, g = p.loading_text), "absolute" in p && t(10, h = p.absolute), "translucent" in p && t(11, w = p.translucent), "border" in p && t(12, F = p.border), "autoscroll" in p && t(24, _ = p.autoscroll), "$$scope" in p && t(29, s = p.$$scope);
  }, n.$$.update = () => {
    n.$$.dirty[0] & /*eta, old_eta, timer_start, eta_from_start*/
    436207617 && (o === null && t(0, o = I), o != null && I !== o && (t(28, W = (performance.now() - z) / 1e3 + o), t(19, B = W.toFixed(1)), t(27, I = o))), n.$$.dirty[0] & /*eta_from_start, timer_diff*/
    335544320 && t(17, ve = W === null || W <= 0 || !L ? null : Math.min(L / W, 1)), n.$$.dirty[0] & /*progress*/
    128 && y != null && t(18, Ie = !1), n.$$.dirty[0] & /*progress, progress_level, progress_bar, last_progress_level*/
    114816 && (y != null ? t(14, x = y.map((p) => {
      if (p.index != null && p.length != null)
        return p.index / p.length;
      if (p.progress != null)
        return p.progress;
    })) : t(14, x = null), x ? (t(15, we = x[x.length - 1]), H && (we === 0 ? t(16, H.style.transition = "0", H) : t(16, H.style.transition = "150ms", H))) : t(15, we = void 0)), n.$$.dirty[0] & /*status*/
    16 && (m === "pending" ? pt() : ot()), n.$$.dirty[0] & /*el, scroll_to_output, status, autoscroll*/
    20979728 && M && E && (m === "pending" || m === "complete") && ts(M, _), n.$$.dirty[0] & /*status, message*/
    8388624, n.$$.dirty[0] & /*timer_diff*/
    67108864 && t(20, l = L.toFixed(1));
  }, [
    o,
    a,
    f,
    u,
    m,
    b,
    k,
    y,
    N,
    g,
    h,
    w,
    F,
    M,
    x,
    we,
    H,
    ve,
    Ie,
    B,
    l,
    r,
    E,
    R,
    _,
    z,
    L,
    I,
    W,
    s,
    i,
    wt,
    V,
    Tt
  ];
}
class ls extends Po {
  constructor(e) {
    super(), Fo(
      this,
      e,
      ns,
      $o,
      Uo,
      {
        i18n: 1,
        eta: 0,
        queue_position: 2,
        queue_size: 3,
        status: 4,
        scroll_to_output: 22,
        timer: 5,
        show_progress: 6,
        message: 23,
        progress: 7,
        variant: 8,
        loading_text: 9,
        absolute: 10,
        translucent: 11,
        border: 12,
        autoscroll: 24
      },
      null,
      [-1, -1]
    );
  }
}
/*! @license DOMPurify 3.1.6 | (c) Cure53 and other contributors | Released under the Apache license 2.0 and Mozilla Public License 2.0 | github.com/cure53/DOMPurify/blob/3.1.6/LICENSE */
const {
  entries: Hl,
  setPrototypeOf: nl,
  isFrozen: is,
  getPrototypeOf: os,
  getOwnPropertyDescriptor: ss
} = Object;
let {
  freeze: Q,
  seal: ae,
  create: Bl
} = Object, {
  apply: sn,
  construct: rn
} = typeof Reflect < "u" && Reflect;
Q || (Q = function(e) {
  return e;
});
ae || (ae = function(e) {
  return e;
});
sn || (sn = function(e, t, l) {
  return e.apply(t, l);
});
rn || (rn = function(e, t) {
  return new e(...t);
});
const Ct = ie(Array.prototype.forEach), ll = ie(Array.prototype.pop), ut = ie(Array.prototype.push), Ut = ie(String.prototype.toLowerCase), Zt = ie(String.prototype.toString), il = ie(String.prototype.match), _t = ie(String.prototype.replace), rs = ie(String.prototype.indexOf), as = ie(String.prototype.trim), me = ie(Object.prototype.hasOwnProperty), J = ie(RegExp.prototype.test), dt = fs(TypeError);
function ie(n) {
  return function(e) {
    for (var t = arguments.length, l = new Array(t > 1 ? t - 1 : 0), i = 1; i < t; i++)
      l[i - 1] = arguments[i];
    return sn(n, e, l);
  };
}
function fs(n) {
  return function() {
    for (var e = arguments.length, t = new Array(e), l = 0; l < e; l++)
      t[l] = arguments[l];
    return rn(n, t);
  };
}
function C(n, e) {
  let t = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : Ut;
  nl && nl(n, null);
  let l = e.length;
  for (; l--; ) {
    let i = e[l];
    if (typeof i == "string") {
      const s = t(i);
      s !== i && (is(e) || (e[l] = s), i = s);
    }
    n[i] = !0;
  }
  return n;
}
function cs(n) {
  for (let e = 0; e < n.length; e++)
    me(n, e) || (n[e] = null);
  return n;
}
function He(n) {
  const e = Bl(null);
  for (const [t, l] of Hl(n))
    me(n, t) && (Array.isArray(l) ? e[t] = cs(l) : l && typeof l == "object" && l.constructor === Object ? e[t] = He(l) : e[t] = l);
  return e;
}
function mt(n, e) {
  for (; n !== null; ) {
    const l = ss(n, e);
    if (l) {
      if (l.get)
        return ie(l.get);
      if (typeof l.value == "function")
        return ie(l.value);
    }
    n = os(n);
  }
  function t() {
    return null;
  }
  return t;
}
const ol = Q(["a", "abbr", "acronym", "address", "area", "article", "aside", "audio", "b", "bdi", "bdo", "big", "blink", "blockquote", "body", "br", "button", "canvas", "caption", "center", "cite", "code", "col", "colgroup", "content", "data", "datalist", "dd", "decorator", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "element", "em", "fieldset", "figcaption", "figure", "font", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "i", "img", "input", "ins", "kbd", "label", "legend", "li", "main", "map", "mark", "marquee", "menu", "menuitem", "meter", "nav", "nobr", "ol", "optgroup", "option", "output", "p", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "section", "select", "shadow", "small", "source", "spacer", "span", "strike", "strong", "style", "sub", "summary", "sup", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "tr", "track", "tt", "u", "ul", "var", "video", "wbr"]), Kt = Q(["svg", "a", "altglyph", "altglyphdef", "altglyphitem", "animatecolor", "animatemotion", "animatetransform", "circle", "clippath", "defs", "desc", "ellipse", "filter", "font", "g", "glyph", "glyphref", "hkern", "image", "line", "lineargradient", "marker", "mask", "metadata", "mpath", "path", "pattern", "polygon", "polyline", "radialgradient", "rect", "stop", "style", "switch", "symbol", "text", "textpath", "title", "tref", "tspan", "view", "vkern"]), Jt = Q(["feBlend", "feColorMatrix", "feComponentTransfer", "feComposite", "feConvolveMatrix", "feDiffuseLighting", "feDisplacementMap", "feDistantLight", "feDropShadow", "feFlood", "feFuncA", "feFuncB", "feFuncG", "feFuncR", "feGaussianBlur", "feImage", "feMerge", "feMergeNode", "feMorphology", "feOffset", "fePointLight", "feSpecularLighting", "feSpotLight", "feTile", "feTurbulence"]), us = Q(["animate", "color-profile", "cursor", "discard", "font-face", "font-face-format", "font-face-name", "font-face-src", "font-face-uri", "foreignobject", "hatch", "hatchpath", "mesh", "meshgradient", "meshpatch", "meshrow", "missing-glyph", "script", "set", "solidcolor", "unknown", "use"]), Qt = Q(["math", "menclose", "merror", "mfenced", "mfrac", "mglyph", "mi", "mlabeledtr", "mmultiscripts", "mn", "mo", "mover", "mpadded", "mphantom", "mroot", "mrow", "ms", "mspace", "msqrt", "mstyle", "msub", "msup", "msubsup", "mtable", "mtd", "mtext", "mtr", "munder", "munderover", "mprescripts"]), _s = Q(["maction", "maligngroup", "malignmark", "mlongdiv", "mscarries", "mscarry", "msgroup", "mstack", "msline", "msrow", "semantics", "annotation", "annotation-xml", "mprescripts", "none"]), sl = Q(["#text"]), rl = Q(["accept", "action", "align", "alt", "autocapitalize", "autocomplete", "autopictureinpicture", "autoplay", "background", "bgcolor", "border", "capture", "cellpadding", "cellspacing", "checked", "cite", "class", "clear", "color", "cols", "colspan", "controls", "controlslist", "coords", "crossorigin", "datetime", "decoding", "default", "dir", "disabled", "disablepictureinpicture", "disableremoteplayback", "download", "draggable", "enctype", "enterkeyhint", "face", "for", "headers", "height", "hidden", "high", "href", "hreflang", "id", "inputmode", "integrity", "ismap", "kind", "label", "lang", "list", "loading", "loop", "low", "max", "maxlength", "media", "method", "min", "minlength", "multiple", "muted", "name", "nonce", "noshade", "novalidate", "nowrap", "open", "optimum", "pattern", "placeholder", "playsinline", "popover", "popovertarget", "popovertargetaction", "poster", "preload", "pubdate", "radiogroup", "readonly", "rel", "required", "rev", "reversed", "role", "rows", "rowspan", "spellcheck", "scope", "selected", "shape", "size", "sizes", "span", "srclang", "start", "src", "srcset", "step", "style", "summary", "tabindex", "title", "translate", "type", "usemap", "valign", "value", "width", "wrap", "xmlns", "slot"]), xt = Q(["accent-height", "accumulate", "additive", "alignment-baseline", "ascent", "attributename", "attributetype", "azimuth", "basefrequency", "baseline-shift", "begin", "bias", "by", "class", "clip", "clippathunits", "clip-path", "clip-rule", "color", "color-interpolation", "color-interpolation-filters", "color-profile", "color-rendering", "cx", "cy", "d", "dx", "dy", "diffuseconstant", "direction", "display", "divisor", "dur", "edgemode", "elevation", "end", "fill", "fill-opacity", "fill-rule", "filter", "filterunits", "flood-color", "flood-opacity", "font-family", "font-size", "font-size-adjust", "font-stretch", "font-style", "font-variant", "font-weight", "fx", "fy", "g1", "g2", "glyph-name", "glyphref", "gradientunits", "gradienttransform", "height", "href", "id", "image-rendering", "in", "in2", "k", "k1", "k2", "k3", "k4", "kerning", "keypoints", "keysplines", "keytimes", "lang", "lengthadjust", "letter-spacing", "kernelmatrix", "kernelunitlength", "lighting-color", "local", "marker-end", "marker-mid", "marker-start", "markerheight", "markerunits", "markerwidth", "maskcontentunits", "maskunits", "max", "mask", "media", "method", "mode", "min", "name", "numoctaves", "offset", "operator", "opacity", "order", "orient", "orientation", "origin", "overflow", "paint-order", "path", "pathlength", "patterncontentunits", "patterntransform", "patternunits", "points", "preservealpha", "preserveaspectratio", "primitiveunits", "r", "rx", "ry", "radius", "refx", "refy", "repeatcount", "repeatdur", "restart", "result", "rotate", "scale", "seed", "shape-rendering", "specularconstant", "specularexponent", "spreadmethod", "startoffset", "stddeviation", "stitchtiles", "stop-color", "stop-opacity", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke", "stroke-width", "style", "surfacescale", "systemlanguage", "tabindex", "targetx", "targety", "transform", "transform-origin", "text-anchor", "text-decoration", "text-rendering", "textlength", "type", "u1", "u2", "unicode", "values", "viewbox", "visibility", "version", "vert-adv-y", "vert-origin-x", "vert-origin-y", "width", "word-spacing", "wrap", "writing-mode", "xchannelselector", "ychannelselector", "x", "x1", "x2", "xmlns", "y", "y1", "y2", "z", "zoomandpan"]), al = Q(["accent", "accentunder", "align", "bevelled", "close", "columnsalign", "columnlines", "columnspan", "denomalign", "depth", "dir", "display", "displaystyle", "encoding", "fence", "frame", "height", "href", "id", "largeop", "length", "linethickness", "lspace", "lquote", "mathbackground", "mathcolor", "mathsize", "mathvariant", "maxsize", "minsize", "movablelimits", "notation", "numalign", "open", "rowalign", "rowlines", "rowspacing", "rowspan", "rspace", "rquote", "scriptlevel", "scriptminsize", "scriptsizemultiplier", "selection", "separator", "separators", "stretchy", "subscriptshift", "supscriptshift", "symmetric", "voffset", "width", "xmlns"]), Nt = Q(["xlink:href", "xml:id", "xlink:title", "xml:space", "xmlns:xlink"]), ds = ae(/\{\{[\w\W]*|[\w\W]*\}\}/gm), ms = ae(/<%[\w\W]*|[\w\W]*%>/gm), gs = ae(/\${[\w\W]*}/gm), hs = ae(/^data-[\-\w.\u00B7-\uFFFF]/), ps = ae(/^aria-[\-\w]+$/), Gl = ae(
  /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
  // eslint-disable-line no-useless-escape
), bs = ae(/^(?:\w+script|data):/i), ws = ae(
  /[\u0000-\u0020\u00A0\u1680\u180E\u2000-\u2029\u205F\u3000]/g
  // eslint-disable-line no-control-regex
), Wl = ae(/^html$/i), Ts = ae(/^[a-z][.\w]*(-[.\w]+)+$/i);
var fl = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  MUSTACHE_EXPR: ds,
  ERB_EXPR: ms,
  TMPLIT_EXPR: gs,
  DATA_ATTR: hs,
  ARIA_ATTR: ps,
  IS_ALLOWED_URI: Gl,
  IS_SCRIPT_OR_DATA: bs,
  ATTR_WHITESPACE: ws,
  DOCTYPE_NAME: Wl,
  CUSTOM_ELEMENT: Ts
});
const gt = {
  element: 1,
  attribute: 2,
  text: 3,
  cdataSection: 4,
  entityReference: 5,
  // Deprecated
  entityNode: 6,
  // Deprecated
  progressingInstruction: 7,
  comment: 8,
  document: 9,
  documentType: 10,
  documentFragment: 11,
  notation: 12
  // Deprecated
}, Es = function() {
  return typeof window > "u" ? null : window;
}, As = function(e, t) {
  if (typeof e != "object" || typeof e.createPolicy != "function")
    return null;
  let l = null;
  const i = "data-tt-policy-suffix";
  t && t.hasAttribute(i) && (l = t.getAttribute(i));
  const s = "dompurify" + (l ? "#" + l : "");
  try {
    return e.createPolicy(s, {
      createHTML(r) {
        return r;
      },
      createScriptURL(r) {
        return r;
      }
    });
  } catch {
    return console.warn("TrustedTypes policy " + s + " could not be created."), null;
  }
};
function ql() {
  let n = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : Es();
  const e = (A) => ql(A);
  if (e.version = "3.1.6", e.removed = [], !n || !n.document || n.document.nodeType !== gt.document)
    return e.isSupported = !1, e;
  let {
    document: t
  } = n;
  const l = t, i = l.currentScript, {
    DocumentFragment: s,
    HTMLTemplateElement: r,
    Node: a,
    Element: o,
    NodeFilter: f,
    NamedNodeMap: u = n.NamedNodeMap || n.MozNamedAttrMap,
    HTMLFormElement: m,
    DOMParser: E,
    trustedTypes: b
  } = n, k = o.prototype, R = mt(k, "cloneNode"), y = mt(k, "remove"), N = mt(k, "nextSibling"), g = mt(k, "childNodes"), h = mt(k, "parentNode");
  if (typeof r == "function") {
    const A = t.createElement("template");
    A.content && A.content.ownerDocument && (t = A.content.ownerDocument);
  }
  let w, F = "";
  const {
    implementation: _,
    createNodeIterator: M,
    createDocumentFragment: q,
    getElementsByTagName: z
  } = t, {
    importNode: L
  } = l;
  let I = {};
  e.isSupported = typeof Hl == "function" && typeof h == "function" && _ && _.createHTMLDocument !== void 0;
  const {
    MUSTACHE_EXPR: W,
    ERB_EXPR: ve,
    TMPLIT_EXPR: x,
    DATA_ATTR: we,
    ARIA_ATTR: H,
    IS_SCRIPT_OR_DATA: Ie,
    ATTR_WHITESPACE: pt,
    CUSTOM_ELEMENT: bt
  } = fl;
  let {
    IS_ALLOWED_URI: ot
  } = fl, B = null;
  const wt = C({}, [...ol, ...Kt, ...Jt, ...Qt, ...sl]);
  let V = null;
  const Tt = C({}, [...rl, ...xt, ...al, ...Nt]);
  let p = Object.seal(Bl(null, {
    tagNameCheck: {
      writable: !0,
      configurable: !1,
      enumerable: !0,
      value: null
    },
    attributeNameCheck: {
      writable: !0,
      configurable: !1,
      enumerable: !0,
      value: null
    },
    allowCustomizedBuiltInElements: {
      writable: !0,
      configurable: !1,
      enumerable: !0,
      value: !1
    }
  })), Pe = null, Ne = null, Fe = !0, st = !0, Oe = !1, Ue = !0, De = !1, rt = !0, fe = !1, ce = !1, ze = !1, Ye = !1, Et = !1, At = !1, an = !0, fn = !1;
  const Vl = "user-content-";
  let Bt = !0, at = !1, je = {}, Xe = null;
  const cn = C({}, ["annotation-xml", "audio", "colgroup", "desc", "foreignobject", "head", "iframe", "math", "mi", "mn", "mo", "ms", "mtext", "noembed", "noframes", "noscript", "plaintext", "script", "style", "svg", "template", "thead", "title", "video", "xmp"]);
  let un = null;
  const _n = C({}, ["audio", "video", "img", "source", "image", "track"]);
  let Gt = null;
  const dn = C({}, ["alt", "class", "for", "id", "label", "name", "pattern", "placeholder", "role", "summary", "title", "value", "style", "xmlns"]), kt = "http://www.w3.org/1998/Math/MathML", yt = "http://www.w3.org/2000/svg", Le = "http://www.w3.org/1999/xhtml";
  let Ze = Le, Wt = !1, qt = null;
  const Yl = C({}, [kt, yt, Le], Zt);
  let ft = null;
  const jl = ["application/xhtml+xml", "text/html"], Xl = "text/html";
  let Y = null, Ke = null;
  const Zl = t.createElement("form"), mn = function(c) {
    return c instanceof RegExp || c instanceof Function;
  }, Vt = function() {
    let c = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
    if (!(Ke && Ke === c)) {
      if ((!c || typeof c != "object") && (c = {}), c = He(c), ft = // eslint-disable-next-line unicorn/prefer-includes
      jl.indexOf(c.PARSER_MEDIA_TYPE) === -1 ? Xl : c.PARSER_MEDIA_TYPE, Y = ft === "application/xhtml+xml" ? Zt : Ut, B = me(c, "ALLOWED_TAGS") ? C({}, c.ALLOWED_TAGS, Y) : wt, V = me(c, "ALLOWED_ATTR") ? C({}, c.ALLOWED_ATTR, Y) : Tt, qt = me(c, "ALLOWED_NAMESPACES") ? C({}, c.ALLOWED_NAMESPACES, Zt) : Yl, Gt = me(c, "ADD_URI_SAFE_ATTR") ? C(
        He(dn),
        // eslint-disable-line indent
        c.ADD_URI_SAFE_ATTR,
        // eslint-disable-line indent
        Y
        // eslint-disable-line indent
      ) : dn, un = me(c, "ADD_DATA_URI_TAGS") ? C(
        He(_n),
        // eslint-disable-line indent
        c.ADD_DATA_URI_TAGS,
        // eslint-disable-line indent
        Y
        // eslint-disable-line indent
      ) : _n, Xe = me(c, "FORBID_CONTENTS") ? C({}, c.FORBID_CONTENTS, Y) : cn, Pe = me(c, "FORBID_TAGS") ? C({}, c.FORBID_TAGS, Y) : {}, Ne = me(c, "FORBID_ATTR") ? C({}, c.FORBID_ATTR, Y) : {}, je = me(c, "USE_PROFILES") ? c.USE_PROFILES : !1, Fe = c.ALLOW_ARIA_ATTR !== !1, st = c.ALLOW_DATA_ATTR !== !1, Oe = c.ALLOW_UNKNOWN_PROTOCOLS || !1, Ue = c.ALLOW_SELF_CLOSE_IN_ATTR !== !1, De = c.SAFE_FOR_TEMPLATES || !1, rt = c.SAFE_FOR_XML !== !1, fe = c.WHOLE_DOCUMENT || !1, Ye = c.RETURN_DOM || !1, Et = c.RETURN_DOM_FRAGMENT || !1, At = c.RETURN_TRUSTED_TYPE || !1, ze = c.FORCE_BODY || !1, an = c.SANITIZE_DOM !== !1, fn = c.SANITIZE_NAMED_PROPS || !1, Bt = c.KEEP_CONTENT !== !1, at = c.IN_PLACE || !1, ot = c.ALLOWED_URI_REGEXP || Gl, Ze = c.NAMESPACE || Le, p = c.CUSTOM_ELEMENT_HANDLING || {}, c.CUSTOM_ELEMENT_HANDLING && mn(c.CUSTOM_ELEMENT_HANDLING.tagNameCheck) && (p.tagNameCheck = c.CUSTOM_ELEMENT_HANDLING.tagNameCheck), c.CUSTOM_ELEMENT_HANDLING && mn(c.CUSTOM_ELEMENT_HANDLING.attributeNameCheck) && (p.attributeNameCheck = c.CUSTOM_ELEMENT_HANDLING.attributeNameCheck), c.CUSTOM_ELEMENT_HANDLING && typeof c.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements == "boolean" && (p.allowCustomizedBuiltInElements = c.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements), De && (st = !1), Et && (Ye = !0), je && (B = C({}, sl), V = [], je.html === !0 && (C(B, ol), C(V, rl)), je.svg === !0 && (C(B, Kt), C(V, xt), C(V, Nt)), je.svgFilters === !0 && (C(B, Jt), C(V, xt), C(V, Nt)), je.mathMl === !0 && (C(B, Qt), C(V, al), C(V, Nt))), c.ADD_TAGS && (B === wt && (B = He(B)), C(B, c.ADD_TAGS, Y)), c.ADD_ATTR && (V === Tt && (V = He(V)), C(V, c.ADD_ATTR, Y)), c.ADD_URI_SAFE_ATTR && C(Gt, c.ADD_URI_SAFE_ATTR, Y), c.FORBID_CONTENTS && (Xe === cn && (Xe = He(Xe)), C(Xe, c.FORBID_CONTENTS, Y)), Bt && (B["#text"] = !0), fe && C(B, ["html", "head", "body"]), B.table && (C(B, ["tbody"]), delete Pe.tbody), c.TRUSTED_TYPES_POLICY) {
        if (typeof c.TRUSTED_TYPES_POLICY.createHTML != "function")
          throw dt('TRUSTED_TYPES_POLICY configuration option must provide a "createHTML" hook.');
        if (typeof c.TRUSTED_TYPES_POLICY.createScriptURL != "function")
          throw dt('TRUSTED_TYPES_POLICY configuration option must provide a "createScriptURL" hook.');
        w = c.TRUSTED_TYPES_POLICY, F = w.createHTML("");
      } else
        w === void 0 && (w = As(b, i)), w !== null && typeof F == "string" && (F = w.createHTML(""));
      Q && Q(c), Ke = c;
    }
  }, gn = C({}, ["mi", "mo", "mn", "ms", "mtext"]), hn = C({}, ["foreignobject", "annotation-xml"]), Kl = C({}, ["title", "style", "font", "a", "script"]), pn = C({}, [...Kt, ...Jt, ...us]), bn = C({}, [...Qt, ..._s]), Jl = function(c) {
    let d = h(c);
    (!d || !d.tagName) && (d = {
      namespaceURI: Ze,
      tagName: "template"
    });
    const T = Ut(c.tagName), U = Ut(d.tagName);
    return qt[c.namespaceURI] ? c.namespaceURI === yt ? d.namespaceURI === Le ? T === "svg" : d.namespaceURI === kt ? T === "svg" && (U === "annotation-xml" || gn[U]) : !!pn[T] : c.namespaceURI === kt ? d.namespaceURI === Le ? T === "math" : d.namespaceURI === yt ? T === "math" && hn[U] : !!bn[T] : c.namespaceURI === Le ? d.namespaceURI === yt && !hn[U] || d.namespaceURI === kt && !gn[U] ? !1 : !bn[T] && (Kl[T] || !pn[T]) : !!(ft === "application/xhtml+xml" && qt[c.namespaceURI]) : !1;
  }, Te = function(c) {
    ut(e.removed, {
      element: c
    });
    try {
      h(c).removeChild(c);
    } catch {
      y(c);
    }
  }, St = function(c, d) {
    try {
      ut(e.removed, {
        attribute: d.getAttributeNode(c),
        from: d
      });
    } catch {
      ut(e.removed, {
        attribute: null,
        from: d
      });
    }
    if (d.removeAttribute(c), c === "is" && !V[c])
      if (Ye || Et)
        try {
          Te(d);
        } catch {
        }
      else
        try {
          d.setAttribute(c, "");
        } catch {
        }
  }, wn = function(c) {
    let d = null, T = null;
    if (ze)
      c = "<remove></remove>" + c;
    else {
      const j = il(c, /^[\r\n\t ]+/);
      T = j && j[0];
    }
    ft === "application/xhtml+xml" && Ze === Le && (c = '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>' + c + "</body></html>");
    const U = w ? w.createHTML(c) : c;
    if (Ze === Le)
      try {
        d = new E().parseFromString(U, ft);
      } catch {
      }
    if (!d || !d.documentElement) {
      d = _.createDocument(Ze, "template", null);
      try {
        d.documentElement.innerHTML = Wt ? F : U;
      } catch {
      }
    }
    const Z = d.body || d.documentElement;
    return c && T && Z.insertBefore(t.createTextNode(T), Z.childNodes[0] || null), Ze === Le ? z.call(d, fe ? "html" : "body")[0] : fe ? d.documentElement : Z;
  }, Tn = function(c) {
    return M.call(
      c.ownerDocument || c,
      c,
      // eslint-disable-next-line no-bitwise
      f.SHOW_ELEMENT | f.SHOW_COMMENT | f.SHOW_TEXT | f.SHOW_PROCESSING_INSTRUCTION | f.SHOW_CDATA_SECTION,
      null
    );
  }, En = function(c) {
    return c instanceof m && (typeof c.nodeName != "string" || typeof c.textContent != "string" || typeof c.removeChild != "function" || !(c.attributes instanceof u) || typeof c.removeAttribute != "function" || typeof c.setAttribute != "function" || typeof c.namespaceURI != "string" || typeof c.insertBefore != "function" || typeof c.hasChildNodes != "function");
  }, An = function(c) {
    return typeof a == "function" && c instanceof a;
  }, Re = function(c, d, T) {
    I[c] && Ct(I[c], (U) => {
      U.call(e, d, T, Ke);
    });
  }, kn = function(c) {
    let d = null;
    if (Re("beforeSanitizeElements", c, null), En(c))
      return Te(c), !0;
    const T = Y(c.nodeName);
    if (Re("uponSanitizeElement", c, {
      tagName: T,
      allowedTags: B
    }), c.hasChildNodes() && !An(c.firstElementChild) && J(/<[/\w]/g, c.innerHTML) && J(/<[/\w]/g, c.textContent) || c.nodeType === gt.progressingInstruction || rt && c.nodeType === gt.comment && J(/<[/\w]/g, c.data))
      return Te(c), !0;
    if (!B[T] || Pe[T]) {
      if (!Pe[T] && Sn(T) && (p.tagNameCheck instanceof RegExp && J(p.tagNameCheck, T) || p.tagNameCheck instanceof Function && p.tagNameCheck(T)))
        return !1;
      if (Bt && !Xe[T]) {
        const U = h(c) || c.parentNode, Z = g(c) || c.childNodes;
        if (Z && U) {
          const j = Z.length;
          for (let $ = j - 1; $ >= 0; --$) {
            const Ee = R(Z[$], !0);
            Ee.__removalCount = (c.__removalCount || 0) + 1, U.insertBefore(Ee, N(c));
          }
        }
      }
      return Te(c), !0;
    }
    return c instanceof o && !Jl(c) || (T === "noscript" || T === "noembed" || T === "noframes") && J(/<\/no(script|embed|frames)/i, c.innerHTML) ? (Te(c), !0) : (De && c.nodeType === gt.text && (d = c.textContent, Ct([W, ve, x], (U) => {
      d = _t(d, U, " ");
    }), c.textContent !== d && (ut(e.removed, {
      element: c.cloneNode()
    }), c.textContent = d)), Re("afterSanitizeElements", c, null), !1);
  }, yn = function(c, d, T) {
    if (an && (d === "id" || d === "name") && (T in t || T in Zl))
      return !1;
    if (!(st && !Ne[d] && J(we, d))) {
      if (!(Fe && J(H, d))) {
        if (!V[d] || Ne[d]) {
          if (
            // First condition does a very basic check if a) it's basically a valid custom element tagname AND
            // b) if the tagName passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
            // and c) if the attribute name passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.attributeNameCheck
            !(Sn(c) && (p.tagNameCheck instanceof RegExp && J(p.tagNameCheck, c) || p.tagNameCheck instanceof Function && p.tagNameCheck(c)) && (p.attributeNameCheck instanceof RegExp && J(p.attributeNameCheck, d) || p.attributeNameCheck instanceof Function && p.attributeNameCheck(d)) || // Alternative, second condition checks if it's an `is`-attribute, AND
            // the value passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
            d === "is" && p.allowCustomizedBuiltInElements && (p.tagNameCheck instanceof RegExp && J(p.tagNameCheck, T) || p.tagNameCheck instanceof Function && p.tagNameCheck(T)))
          ) return !1;
        } else if (!Gt[d]) {
          if (!J(ot, _t(T, pt, ""))) {
            if (!((d === "src" || d === "xlink:href" || d === "href") && c !== "script" && rs(T, "data:") === 0 && un[c])) {
              if (!(Oe && !J(Ie, _t(T, pt, "")))) {
                if (T)
                  return !1;
              }
            }
          }
        }
      }
    }
    return !0;
  }, Sn = function(c) {
    return c !== "annotation-xml" && il(c, bt);
  }, vn = function(c) {
    Re("beforeSanitizeAttributes", c, null);
    const {
      attributes: d
    } = c;
    if (!d)
      return;
    const T = {
      attrName: "",
      attrValue: "",
      keepAttr: !0,
      allowedAttributes: V
    };
    let U = d.length;
    for (; U--; ) {
      const Z = d[U], {
        name: j,
        namespaceURI: $,
        value: Ee
      } = Z, ct = Y(j);
      let K = j === "value" ? Ee : as(Ee);
      if (T.attrName = ct, T.attrValue = K, T.keepAttr = !0, T.forceKeepAttr = void 0, Re("uponSanitizeAttribute", c, T), K = T.attrValue, rt && J(/((--!?|])>)|<\/(style|title)/i, K)) {
        St(j, c);
        continue;
      }
      if (T.forceKeepAttr || (St(j, c), !T.keepAttr))
        continue;
      if (!Ue && J(/\/>/i, K)) {
        St(j, c);
        continue;
      }
      De && Ct([W, ve, x], (Rn) => {
        K = _t(K, Rn, " ");
      });
      const Ln = Y(c.nodeName);
      if (yn(Ln, ct, K)) {
        if (fn && (ct === "id" || ct === "name") && (St(j, c), K = Vl + K), w && typeof b == "object" && typeof b.getAttributeType == "function" && !$)
          switch (b.getAttributeType(Ln, ct)) {
            case "TrustedHTML": {
              K = w.createHTML(K);
              break;
            }
            case "TrustedScriptURL": {
              K = w.createScriptURL(K);
              break;
            }
          }
        try {
          $ ? c.setAttributeNS($, j, K) : c.setAttribute(j, K), En(c) ? Te(c) : ll(e.removed);
        } catch {
        }
      }
    }
    Re("afterSanitizeAttributes", c, null);
  }, Ql = function A(c) {
    let d = null;
    const T = Tn(c);
    for (Re("beforeSanitizeShadowDOM", c, null); d = T.nextNode(); )
      Re("uponSanitizeShadowNode", d, null), !kn(d) && (d.content instanceof s && A(d.content), vn(d));
    Re("afterSanitizeShadowDOM", c, null);
  };
  return e.sanitize = function(A) {
    let c = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, d = null, T = null, U = null, Z = null;
    if (Wt = !A, Wt && (A = "<!-->"), typeof A != "string" && !An(A))
      if (typeof A.toString == "function") {
        if (A = A.toString(), typeof A != "string")
          throw dt("dirty is not a string, aborting");
      } else
        throw dt("toString is not a function");
    if (!e.isSupported)
      return A;
    if (ce || Vt(c), e.removed = [], typeof A == "string" && (at = !1), at) {
      if (A.nodeName) {
        const Ee = Y(A.nodeName);
        if (!B[Ee] || Pe[Ee])
          throw dt("root node is forbidden and cannot be sanitized in-place");
      }
    } else if (A instanceof a)
      d = wn("<!---->"), T = d.ownerDocument.importNode(A, !0), T.nodeType === gt.element && T.nodeName === "BODY" || T.nodeName === "HTML" ? d = T : d.appendChild(T);
    else {
      if (!Ye && !De && !fe && // eslint-disable-next-line unicorn/prefer-includes
      A.indexOf("<") === -1)
        return w && At ? w.createHTML(A) : A;
      if (d = wn(A), !d)
        return Ye ? null : At ? F : "";
    }
    d && ze && Te(d.firstChild);
    const j = Tn(at ? A : d);
    for (; U = j.nextNode(); )
      kn(U) || (U.content instanceof s && Ql(U.content), vn(U));
    if (at)
      return A;
    if (Ye) {
      if (Et)
        for (Z = q.call(d.ownerDocument); d.firstChild; )
          Z.appendChild(d.firstChild);
      else
        Z = d;
      return (V.shadowroot || V.shadowrootmode) && (Z = L.call(l, Z, !0)), Z;
    }
    let $ = fe ? d.outerHTML : d.innerHTML;
    return fe && B["!doctype"] && d.ownerDocument && d.ownerDocument.doctype && d.ownerDocument.doctype.name && J(Wl, d.ownerDocument.doctype.name) && ($ = "<!DOCTYPE " + d.ownerDocument.doctype.name + `>
` + $), De && Ct([W, ve, x], (Ee) => {
      $ = _t($, Ee, " ");
    }), w && At ? w.createHTML($) : $;
  }, e.setConfig = function() {
    let A = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
    Vt(A), ce = !0;
  }, e.clearConfig = function() {
    Ke = null, ce = !1;
  }, e.isValidAttribute = function(A, c, d) {
    Ke || Vt({});
    const T = Y(A), U = Y(c);
    return yn(T, U, d);
  }, e.addHook = function(A, c) {
    typeof c == "function" && (I[A] = I[A] || [], ut(I[A], c));
  }, e.removeHook = function(A) {
    if (I[A])
      return ll(I[A]);
  }, e.removeHooks = function(A) {
    I[A] && (I[A] = []);
  }, e.removeAllHooks = function() {
    I = {};
  }, e;
}
ql();
const {
  SvelteComponent: ks,
  append: ys,
  assign: cl,
  attr: ne,
  bubble: ul,
  detach: Ss,
  exclude_internal_props: _l,
  init: vs,
  insert: Ls,
  listen: dl,
  noop: ml,
  run_all: Rs,
  safe_not_equal: Cs,
  svg_element: gl,
  toggle_class: hl
} = window.__gradio__svelte__internal;
function Ns(n) {
  let e, t, l, i, s, r;
  return {
    c() {
      e = gl("svg"), t = gl("polygon"), ne(t, "points", "50 0, 100 100, 0 100"), ne(e, "class", l = "svg-arrow " + /*$$props*/
      n[3].class + " svelte-1j9bnuy"), ne(
        e,
        "width",
        /*width*/
        n[1]
      ), ne(
        e,
        "height",
        /*height*/
        n[0]
      ), ne(e, "xmlns", "http://www.w3.org/2000/svg"), ne(e, "viewBox", "0 0 100 100"), ne(e, "aria-roledescription", i = "Sorts table in " + /*direction*/
      n[2] + "ending order"), ne(e, "role", "button"), ne(e, "tabindex", "0"), hl(
        e,
        "down",
        /*direction*/
        n[2] === "desc"
      );
    },
    m(a, o) {
      Ls(a, e, o), ys(e, t), s || (r = [
        dl(
          e,
          "click",
          /*click_handler*/
          n[4]
        ),
        dl(
          e,
          "keypress",
          /*keypress_handler*/
          n[5]
        )
      ], s = !0);
    },
    p(a, [o]) {
      o & /*$$props*/
      8 && l !== (l = "svg-arrow " + /*$$props*/
      a[3].class + " svelte-1j9bnuy") && ne(e, "class", l), o & /*width*/
      2 && ne(
        e,
        "width",
        /*width*/
        a[1]
      ), o & /*height*/
      1 && ne(
        e,
        "height",
        /*height*/
        a[0]
      ), o & /*direction*/
      4 && i !== (i = "Sorts table in " + /*direction*/
      a[2] + "ending order") && ne(e, "aria-roledescription", i), o & /*$$props, direction*/
      12 && hl(
        e,
        "down",
        /*direction*/
        a[2] === "desc"
      );
    },
    i: ml,
    o: ml,
    d(a) {
      a && Ss(e), s = !1, Rs(r);
    }
  };
}
function Os(n, e, t) {
  let { height: l = "16px" } = e, { width: i = "16px" } = e, { direction: s = "asc" } = e;
  function r(o) {
    ul.call(this, n, o);
  }
  function a(o) {
    ul.call(this, n, o);
  }
  return n.$$set = (o) => {
    t(3, e = cl(cl({}, e), _l(o))), "height" in o && t(0, l = o.height), "width" in o && t(1, i = o.width), "direction" in o && t(2, s = o.direction);
  }, e = _l(e), [l, i, s, e, r, a];
}
class Ot extends ks {
  constructor(e) {
    super(), vs(this, e, Os, Ns, Cs, { height: 0, width: 1, direction: 2 });
  }
}
const {
  SvelteComponent: Ds,
  append: D,
  assign: Ms,
  attr: P,
  check_outros: pl,
  create_component: Ge,
  destroy_component: We,
  destroy_each: Is,
  detach: tt,
  element: X,
  empty: Ps,
  ensure_array_like: bl,
  get_spread_object: Fs,
  get_spread_update: Us,
  group_outros: wl,
  init: zs,
  insert: nt,
  mount_component: qe,
  safe_not_equal: Hs,
  set_data: zt,
  set_style: Ve,
  space: he,
  svg_element: Dt,
  text: lt,
  transition_in: le,
  transition_out: pe
} = window.__gradio__svelte__internal;
function Tl(n, e, t) {
  const l = n.slice();
  return l[19] = e[t], l;
}
function El(n) {
  let e, t;
  const l = [
    {
      autoscroll: (
        /*gradio*/
        n[10].autoscroll
      )
    },
    { i18n: (
      /*gradio*/
      n[10].i18n
    ) },
    /*loading_status*/
    n[9]
  ];
  let i = {};
  for (let s = 0; s < l.length; s += 1)
    i = Ms(i, l[s]);
  return e = new ls({ props: i }), e.$on(
    "clear_status",
    /*clear_status_handler*/
    n[14]
  ), {
    c() {
      Ge(e.$$.fragment);
    },
    m(s, r) {
      qe(e, s, r), t = !0;
    },
    p(s, r) {
      const a = r & /*gradio, loading_status*/
      1536 ? Us(l, [
        r & /*gradio*/
        1024 && {
          autoscroll: (
            /*gradio*/
            s[10].autoscroll
          )
        },
        r & /*gradio*/
        1024 && { i18n: (
          /*gradio*/
          s[10].i18n
        ) },
        r & /*loading_status*/
        512 && Fs(
          /*loading_status*/
          s[9]
        )
      ]) : {};
      e.$set(a);
    },
    i(s) {
      t || (le(e.$$.fragment, s), t = !0);
    },
    o(s) {
      pe(e.$$.fragment, s), t = !1;
    },
    d(s) {
      We(e, s);
    }
  };
}
function Bs(n) {
  let e;
  return {
    c() {
      e = lt(
        /*label*/
        n[2]
      );
    },
    m(t, l) {
      nt(t, e, l);
    },
    p(t, l) {
      l & /*label*/
      4 && zt(
        e,
        /*label*/
        t[2]
      );
    },
    d(t) {
      t && tt(e);
    }
  };
}
function Al(n) {
  let e, t, l, i, s, r, a, o, f, u, m, E, b, k, R, y, N, g, h, w, F, _, M;
  u = new Ot({
    props: {
      direction: "asc",
      height: "10",
      width: "10",
      class: (
        /*sorted_by*/
        n[12] === "retrievalScoreasc" ? "active" : ""
      )
    }
  }), u.$on(
    "click",
    /*click_handler*/
    n[15]
  ), E = new Ot({
    props: {
      direction: "desc",
      height: "10",
      width: "10",
      class: (
        /*sorted_by*/
        n[12] === "retrievalScoredesc" ? "active" : ""
      )
    }
  }), E.$on(
    "click",
    /*click_handler_1*/
    n[16]
  ), g = new Ot({
    props: {
      direction: "asc",
      height: "10",
      width: "10",
      class: (
        /*sorted_by*/
        n[12] === "rerankScoreasc" ? "active" : ""
      )
    }
  }), g.$on(
    "click",
    /*click_handler_2*/
    n[17]
  ), w = new Ot({
    props: {
      direction: "desc",
      height: "10",
      width: "10",
      class: (
        /*sorted_by*/
        n[12] === "rerankScoredesc" ? "active" : ""
      )
    }
  }), w.$on(
    "click",
    /*click_handler_3*/
    n[18]
  );
  let q = bl(
    /*sorted_sources*/
    n[11]
  ), z = [];
  for (let L = 0; L < q.length; L += 1)
    z[L] = kl(Tl(n, q, L));
  return {
    c() {
      e = X("table"), t = X("thead"), l = X("tr"), i = X("th"), i.textContent = "URL", s = he(), r = X("th"), a = X("div"), o = lt(`Retrieval Score
							`), f = X("span"), Ge(u.$$.fragment), m = he(), Ge(E.$$.fragment), b = he(), k = X("th"), R = X("div"), y = lt(`Rerank Score
							`), N = X("span"), Ge(g.$$.fragment), h = he(), Ge(w.$$.fragment), F = he(), _ = X("tbody");
      for (let L = 0; L < z.length; L += 1)
        z[L].c();
      P(i, "class", "svelte-14n3y07"), P(f, "class", "arrow-grp svelte-14n3y07"), Ve(a, "display", "flex"), Ve(a, "justify-content", "right"), P(r, "class", "svelte-14n3y07"), P(N, "class", "arrow-grp svelte-14n3y07"), Ve(R, "display", "flex"), Ve(R, "justify-content", "right"), P(k, "class", "svelte-14n3y07"), P(l, "class", "svelte-14n3y07"), P(e, "class", "rag-table svelte-14n3y07");
    },
    m(L, I) {
      nt(L, e, I), D(e, t), D(t, l), D(l, i), D(l, s), D(l, r), D(r, a), D(a, o), D(a, f), qe(u, f, null), D(f, m), qe(E, f, null), D(l, b), D(l, k), D(k, R), D(R, y), D(R, N), qe(g, N, null), D(N, h), qe(w, N, null), D(e, F), D(e, _);
      for (let W = 0; W < z.length; W += 1)
        z[W] && z[W].m(_, null);
      M = !0;
    },
    p(L, I) {
      const W = {};
      I & /*sorted_by*/
      4096 && (W.class = /*sorted_by*/
      L[12] === "retrievalScoreasc" ? "active" : ""), u.$set(W);
      const ve = {};
      I & /*sorted_by*/
      4096 && (ve.class = /*sorted_by*/
      L[12] === "retrievalScoredesc" ? "active" : ""), E.$set(ve);
      const x = {};
      I & /*sorted_by*/
      4096 && (x.class = /*sorted_by*/
      L[12] === "rerankScoreasc" ? "active" : ""), g.$set(x);
      const we = {};
      if (I & /*sorted_by*/
      4096 && (we.class = /*sorted_by*/
      L[12] === "rerankScoredesc" ? "active" : ""), w.$set(we), I & /*sorted_sources*/
      2048) {
        q = bl(
          /*sorted_sources*/
          L[11]
        );
        let H;
        for (H = 0; H < q.length; H += 1) {
          const Ie = Tl(L, q, H);
          z[H] ? z[H].p(Ie, I) : (z[H] = kl(Ie), z[H].c(), z[H].m(_, null));
        }
        for (; H < z.length; H += 1)
          z[H].d(1);
        z.length = q.length;
      }
    },
    i(L) {
      M || (le(u.$$.fragment, L), le(E.$$.fragment, L), le(g.$$.fragment, L), le(w.$$.fragment, L), M = !0);
    },
    o(L) {
      pe(u.$$.fragment, L), pe(E.$$.fragment, L), pe(g.$$.fragment, L), pe(w.$$.fragment, L), M = !1;
    },
    d(L) {
      L && tt(e), We(u), We(E), We(g), We(w), Is(z, L);
    }
  };
}
function kl(n) {
  let e, t, l, i = (
    /*source*/
    n[19].url + ""
  ), s, r, a, o, f, u, m, E, b, k, R = (
    /*source*/
    n[19].retrievalScore + ""
  ), y, N, g, h = (
    /*source*/
    n[19].rerankScore + ""
  ), w, F;
  return {
    c() {
      e = X("tr"), t = X("td"), l = X("div"), s = lt(i), r = he(), a = X("a"), o = Dt("svg"), f = Dt("path"), u = Dt("polyline"), m = Dt("line"), b = he(), k = X("td"), y = lt(R), N = he(), g = X("td"), w = lt(h), F = he(), P(f, "d", "M55.4,32V53.58a1.81,1.81,0,0,1-1.82,1.82H10.42A1.81,1.81,0,0,1,8.6,53.58V10.42A1.81,1.81,0,0,1,10.42,8.6H32"), P(u, "points", "40.32 8.6 55.4 8.6 55.4 24.18"), P(m, "x1", "19.32"), P(m, "y1", "45.72"), P(m, "x2", "54.61"), P(m, "y2", "8.91"), P(o, "height", "16"), P(o, "width", "16"), P(o, "viewBox", "0 0 64 64"), P(o, "xmlns", "http://www.w3.org/2000/svg"), P(o, "class", "svelte-14n3y07"), P(a, "href", E = /*source*/
      n[19].url), P(a, "target", "_blank"), P(a, "rel", "noreferrer noopener"), P(a, "class", "rag-href svelte-14n3y07"), Ve(l, "display", "flex"), P(t, "class", "svelte-14n3y07"), Ve(k, "text-align", "right"), P(k, "class", "svelte-14n3y07"), Ve(g, "text-align", "right"), P(g, "class", "svelte-14n3y07"), P(e, "class", "svelte-14n3y07");
    },
    m(_, M) {
      nt(_, e, M), D(e, t), D(t, l), D(l, s), D(l, r), D(l, a), D(a, o), D(o, f), D(o, u), D(o, m), D(e, b), D(e, k), D(k, y), D(e, N), D(e, g), D(g, w), D(e, F);
    },
    p(_, M) {
      M & /*sorted_sources*/
      2048 && i !== (i = /*source*/
      _[19].url + "") && zt(s, i), M & /*sorted_sources*/
      2048 && E !== (E = /*source*/
      _[19].url) && P(a, "href", E), M & /*sorted_sources*/
      2048 && R !== (R = /*source*/
      _[19].retrievalScore + "") && zt(y, R), M & /*sorted_sources*/
      2048 && h !== (h = /*source*/
      _[19].rerankScore + "") && zt(w, h);
    },
    d(_) {
      _ && tt(e);
    }
  };
}
function Gs(n) {
  let e, t, l, i, s, r = (
    /*loading_status*/
    n[9] && El(n)
  );
  t = new Ji({
    props: {
      show_label: (
        /*show_label*/
        n[3]
      ),
      info: void 0,
      $$slots: { default: [Bs] },
      $$scope: { ctx: n }
    }
  });
  let a = (
    /*value*/
    n[5].length > 0 && Al(n)
  );
  return {
    c() {
      r && r.c(), e = he(), Ge(t.$$.fragment), l = he(), a && a.c(), i = Ps();
    },
    m(o, f) {
      r && r.m(o, f), nt(o, e, f), qe(t, o, f), nt(o, l, f), a && a.m(o, f), nt(o, i, f), s = !0;
    },
    p(o, f) {
      /*loading_status*/
      o[9] ? r ? (r.p(o, f), f & /*loading_status*/
      512 && le(r, 1)) : (r = El(o), r.c(), le(r, 1), r.m(e.parentNode, e)) : r && (wl(), pe(r, 1, 1, () => {
        r = null;
      }), pl());
      const u = {};
      f & /*show_label*/
      8 && (u.show_label = /*show_label*/
      o[3]), f & /*$$scope, label*/
      4194308 && (u.$$scope = { dirty: f, ctx: o }), t.$set(u), /*value*/
      o[5].length > 0 ? a ? (a.p(o, f), f & /*value*/
      32 && le(a, 1)) : (a = Al(o), a.c(), le(a, 1), a.m(i.parentNode, i)) : a && (wl(), pe(a, 1, 1, () => {
        a = null;
      }), pl());
    },
    i(o) {
      s || (le(r), le(t.$$.fragment, o), le(a), s = !0);
    },
    o(o) {
      pe(r), pe(t.$$.fragment, o), pe(a), s = !1;
    },
    d(o) {
      o && (tt(e), tt(l), tt(i)), r && r.d(o), We(t, o), a && a.d(o);
    }
  };
}
function Ws(n) {
  let e, t;
  return e = new di({
    props: {
      visible: (
        /*visible*/
        n[4]
      ),
      elem_id: (
        /*elem_id*/
        n[0]
      ),
      elem_classes: (
        /*elem_classes*/
        n[1]
      ),
      container: (
        /*container*/
        n[6]
      ),
      scale: (
        /*scale*/
        n[7]
      ),
      min_width: (
        /*min_width*/
        n[8]
      ),
      $$slots: { default: [Gs] },
      $$scope: { ctx: n }
    }
  }), {
    c() {
      Ge(e.$$.fragment);
    },
    m(l, i) {
      qe(e, l, i), t = !0;
    },
    p(l, [i]) {
      const s = {};
      i & /*visible*/
      16 && (s.visible = /*visible*/
      l[4]), i & /*elem_id*/
      1 && (s.elem_id = /*elem_id*/
      l[0]), i & /*elem_classes*/
      2 && (s.elem_classes = /*elem_classes*/
      l[1]), i & /*container*/
      64 && (s.container = /*container*/
      l[6]), i & /*scale*/
      128 && (s.scale = /*scale*/
      l[7]), i & /*min_width*/
      256 && (s.min_width = /*min_width*/
      l[8]), i & /*$$scope, sorted_sources, sorted_by, value, show_label, label, gradio, loading_status*/
      4202028 && (s.$$scope = { dirty: i, ctx: l }), e.$set(s);
    },
    i(l) {
      t || (le(e.$$.fragment, l), t = !0);
    },
    o(l) {
      pe(e.$$.fragment, l), t = !1;
    },
    d(l) {
      We(e, l);
    }
  };
}
function qs(n, e, t) {
  let { elem_id: l = "" } = e, { elem_classes: i = [] } = e, { label: s = "RAG Sources" } = e, { show_label: r = !0 } = e, { visible: a = !0 } = e, { value: o = [] } = e, { container: f = !0 } = e, { scale: u = null } = e, { min_width: m = void 0 } = e, { loading_status: E } = e, { gradio: b } = e, k, R;
  function y(_, M) {
    function q(z, L) {
      let I = z[_], W = L[_];
      return I === W ? 0 : I < W == (M === "asc") ? -1 : 1;
    }
    o.length === 0 ? t(11, k = []) : (t(11, k = o.sort(q)), t(12, R = _ + M));
  }
  const N = () => b.dispatch("clear_status", E), g = () => y("retrievalScore", "asc"), h = () => y("retrievalScore", "desc"), w = () => y("rerankScore", "asc"), F = () => y("rerankScore", "desc");
  return n.$$set = (_) => {
    "elem_id" in _ && t(0, l = _.elem_id), "elem_classes" in _ && t(1, i = _.elem_classes), "label" in _ && t(2, s = _.label), "show_label" in _ && t(3, r = _.show_label), "visible" in _ && t(4, a = _.visible), "value" in _ && t(5, o = _.value), "container" in _ && t(6, f = _.container), "scale" in _ && t(7, u = _.scale), "min_width" in _ && t(8, m = _.min_width), "loading_status" in _ && t(9, E = _.loading_status), "gradio" in _ && t(10, b = _.gradio);
  }, n.$$.update = () => {
    n.$$.dirty & /*value*/
    32 && y("rerankScore", "desc");
  }, [
    l,
    i,
    s,
    r,
    a,
    o,
    f,
    u,
    m,
    E,
    b,
    k,
    R,
    y,
    N,
    g,
    h,
    w,
    F
  ];
}
class Vs extends Ds {
  constructor(e) {
    super(), zs(this, e, qs, Ws, Hs, {
      elem_id: 0,
      elem_classes: 1,
      label: 2,
      show_label: 3,
      visible: 4,
      value: 5,
      container: 6,
      scale: 7,
      min_width: 8,
      loading_status: 9,
      gradio: 10
    });
  }
}
export {
  Vs as default
};
