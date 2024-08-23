const {
  SvelteComponent: ri,
  assign: fi,
  create_slot: ci,
  detach: ui,
  element: _i,
  get_all_dirty_from_scope: mi,
  get_slot_changes: di,
  get_spread_update: hi,
  init: gi,
  insert: bi,
  safe_not_equal: pi,
  set_dynamic_element_data: Gn,
  set_style: J,
  toggle_class: be,
  transition_in: Dl,
  transition_out: Nl,
  update_slot_base: wi
} = window.__gradio__svelte__internal;
function Ti(l) {
  let e, t, n;
  const i = (
    /*#slots*/
    l[18].default
  ), o = ci(
    i,
    l,
    /*$$scope*/
    l[17],
    null
  );
  let a = [
    { "data-testid": (
      /*test_id*/
      l[7]
    ) },
    { id: (
      /*elem_id*/
      l[2]
    ) },
    {
      class: t = "block " + /*elem_classes*/
      l[3].join(" ") + " svelte-nl1om8"
    }
  ], f = {};
  for (let s = 0; s < a.length; s += 1)
    f = fi(f, a[s]);
  return {
    c() {
      e = _i(
        /*tag*/
        l[14]
      ), o && o.c(), Gn(
        /*tag*/
        l[14]
      )(e, f), be(
        e,
        "hidden",
        /*visible*/
        l[10] === !1
      ), be(
        e,
        "padded",
        /*padding*/
        l[6]
      ), be(
        e,
        "border_focus",
        /*border_mode*/
        l[5] === "focus"
      ), be(
        e,
        "border_contrast",
        /*border_mode*/
        l[5] === "contrast"
      ), be(e, "hide-container", !/*explicit_call*/
      l[8] && !/*container*/
      l[9]), J(
        e,
        "height",
        /*get_dimension*/
        l[15](
          /*height*/
          l[0]
        )
      ), J(e, "width", typeof /*width*/
      l[1] == "number" ? `calc(min(${/*width*/
      l[1]}px, 100%))` : (
        /*get_dimension*/
        l[15](
          /*width*/
          l[1]
        )
      )), J(
        e,
        "border-style",
        /*variant*/
        l[4]
      ), J(
        e,
        "overflow",
        /*allow_overflow*/
        l[11] ? "visible" : "hidden"
      ), J(
        e,
        "flex-grow",
        /*scale*/
        l[12]
      ), J(e, "min-width", `calc(min(${/*min_width*/
      l[13]}px, 100%))`), J(e, "border-width", "var(--block-border-width)");
    },
    m(s, r) {
      bi(s, e, r), o && o.m(e, null), n = !0;
    },
    p(s, r) {
      o && o.p && (!n || r & /*$$scope*/
      131072) && wi(
        o,
        i,
        s,
        /*$$scope*/
        s[17],
        n ? di(
          i,
          /*$$scope*/
          s[17],
          r,
          null
        ) : mi(
          /*$$scope*/
          s[17]
        ),
        null
      ), Gn(
        /*tag*/
        s[14]
      )(e, f = hi(a, [
        (!n || r & /*test_id*/
        128) && { "data-testid": (
          /*test_id*/
          s[7]
        ) },
        (!n || r & /*elem_id*/
        4) && { id: (
          /*elem_id*/
          s[2]
        ) },
        (!n || r & /*elem_classes*/
        8 && t !== (t = "block " + /*elem_classes*/
        s[3].join(" ") + " svelte-nl1om8")) && { class: t }
      ])), be(
        e,
        "hidden",
        /*visible*/
        s[10] === !1
      ), be(
        e,
        "padded",
        /*padding*/
        s[6]
      ), be(
        e,
        "border_focus",
        /*border_mode*/
        s[5] === "focus"
      ), be(
        e,
        "border_contrast",
        /*border_mode*/
        s[5] === "contrast"
      ), be(e, "hide-container", !/*explicit_call*/
      s[8] && !/*container*/
      s[9]), r & /*height*/
      1 && J(
        e,
        "height",
        /*get_dimension*/
        s[15](
          /*height*/
          s[0]
        )
      ), r & /*width*/
      2 && J(e, "width", typeof /*width*/
      s[1] == "number" ? `calc(min(${/*width*/
      s[1]}px, 100%))` : (
        /*get_dimension*/
        s[15](
          /*width*/
          s[1]
        )
      )), r & /*variant*/
      16 && J(
        e,
        "border-style",
        /*variant*/
        s[4]
      ), r & /*allow_overflow*/
      2048 && J(
        e,
        "overflow",
        /*allow_overflow*/
        s[11] ? "visible" : "hidden"
      ), r & /*scale*/
      4096 && J(
        e,
        "flex-grow",
        /*scale*/
        s[12]
      ), r & /*min_width*/
      8192 && J(e, "min-width", `calc(min(${/*min_width*/
      s[13]}px, 100%))`);
    },
    i(s) {
      n || (Dl(o, s), n = !0);
    },
    o(s) {
      Nl(o, s), n = !1;
    },
    d(s) {
      s && ui(e), o && o.d(s);
    }
  };
}
function Ei(l) {
  let e, t = (
    /*tag*/
    l[14] && Ti(l)
  );
  return {
    c() {
      t && t.c();
    },
    m(n, i) {
      t && t.m(n, i), e = !0;
    },
    p(n, [i]) {
      /*tag*/
      n[14] && t.p(n, i);
    },
    i(n) {
      e || (Dl(t, n), e = !0);
    },
    o(n) {
      Nl(t, n), e = !1;
    },
    d(n) {
      t && t.d(n);
    }
  };
}
function Ai(l, e, t) {
  let { $$slots: n = {}, $$scope: i } = e, { height: o = void 0 } = e, { width: a = void 0 } = e, { elem_id: f = "" } = e, { elem_classes: s = [] } = e, { variant: r = "solid" } = e, { border_mode: u = "base" } = e, { padding: _ = !0 } = e, { type: b = "normal" } = e, { test_id: m = void 0 } = e, { explicit_call: S = !1 } = e, { container: p = !0 } = e, { visible: A = !0 } = e, { allow_overflow: D = !0 } = e, { scale: h = null } = e, { min_width: w = 0 } = e, y = b === "fieldset" ? "fieldset" : "div";
  const O = (g) => {
    if (g !== void 0) {
      if (typeof g == "number")
        return g + "px";
      if (typeof g == "string")
        return g;
    }
  };
  return l.$$set = (g) => {
    "height" in g && t(0, o = g.height), "width" in g && t(1, a = g.width), "elem_id" in g && t(2, f = g.elem_id), "elem_classes" in g && t(3, s = g.elem_classes), "variant" in g && t(4, r = g.variant), "border_mode" in g && t(5, u = g.border_mode), "padding" in g && t(6, _ = g.padding), "type" in g && t(16, b = g.type), "test_id" in g && t(7, m = g.test_id), "explicit_call" in g && t(8, S = g.explicit_call), "container" in g && t(9, p = g.container), "visible" in g && t(10, A = g.visible), "allow_overflow" in g && t(11, D = g.allow_overflow), "scale" in g && t(12, h = g.scale), "min_width" in g && t(13, w = g.min_width), "$$scope" in g && t(17, i = g.$$scope);
  }, [
    o,
    a,
    f,
    s,
    r,
    u,
    _,
    m,
    S,
    p,
    A,
    D,
    h,
    w,
    y,
    O,
    b,
    i,
    n
  ];
}
class ki extends ri {
  constructor(e) {
    super(), gi(this, e, Ai, Ei, pi, {
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
  SvelteComponent: vi,
  append: Gt,
  attr: Ct,
  create_component: Si,
  destroy_component: yi,
  detach: Ci,
  element: Wn,
  init: Li,
  insert: Ri,
  mount_component: Di,
  safe_not_equal: Ni,
  set_data: Mi,
  space: Oi,
  text: Ii,
  toggle_class: Re,
  transition_in: Pi,
  transition_out: Fi
} = window.__gradio__svelte__internal;
function Ui(l) {
  let e, t, n, i, o, a;
  return n = new /*Icon*/
  l[1]({}), {
    c() {
      e = Wn("label"), t = Wn("span"), Si(n.$$.fragment), i = Oi(), o = Ii(
        /*label*/
        l[0]
      ), Ct(t, "class", "svelte-9gxdi0"), Ct(e, "for", ""), Ct(e, "data-testid", "block-label"), Ct(e, "class", "svelte-9gxdi0"), Re(e, "hide", !/*show_label*/
      l[2]), Re(e, "sr-only", !/*show_label*/
      l[2]), Re(
        e,
        "float",
        /*float*/
        l[4]
      ), Re(
        e,
        "hide-label",
        /*disable*/
        l[3]
      );
    },
    m(f, s) {
      Ri(f, e, s), Gt(e, t), Di(n, t, null), Gt(e, i), Gt(e, o), a = !0;
    },
    p(f, [s]) {
      (!a || s & /*label*/
      1) && Mi(
        o,
        /*label*/
        f[0]
      ), (!a || s & /*show_label*/
      4) && Re(e, "hide", !/*show_label*/
      f[2]), (!a || s & /*show_label*/
      4) && Re(e, "sr-only", !/*show_label*/
      f[2]), (!a || s & /*float*/
      16) && Re(
        e,
        "float",
        /*float*/
        f[4]
      ), (!a || s & /*disable*/
      8) && Re(
        e,
        "hide-label",
        /*disable*/
        f[3]
      );
    },
    i(f) {
      a || (Pi(n.$$.fragment, f), a = !0);
    },
    o(f) {
      Fi(n.$$.fragment, f), a = !1;
    },
    d(f) {
      f && Ci(e), yi(n);
    }
  };
}
function zi(l, e, t) {
  let { label: n = null } = e, { Icon: i } = e, { show_label: o = !0 } = e, { disable: a = !1 } = e, { float: f = !0 } = e;
  return l.$$set = (s) => {
    "label" in s && t(0, n = s.label), "Icon" in s && t(1, i = s.Icon), "show_label" in s && t(2, o = s.show_label), "disable" in s && t(3, a = s.disable), "float" in s && t(4, f = s.float);
  }, [n, i, o, a, f];
}
class Ml extends vi {
  constructor(e) {
    super(), Li(this, e, zi, Ui, Ni, {
      label: 0,
      Icon: 1,
      show_label: 2,
      disable: 3,
      float: 4
    });
  }
}
const {
  SvelteComponent: Hi,
  append: on,
  attr: ke,
  bubble: Bi,
  create_component: qi,
  destroy_component: Gi,
  detach: Ol,
  element: an,
  init: Wi,
  insert: Il,
  listen: Vi,
  mount_component: Yi,
  safe_not_equal: ji,
  set_data: Xi,
  set_style: Ze,
  space: Zi,
  text: Ki,
  toggle_class: Z,
  transition_in: Ji,
  transition_out: Qi
} = window.__gradio__svelte__internal;
function Vn(l) {
  let e, t;
  return {
    c() {
      e = an("span"), t = Ki(
        /*label*/
        l[1]
      ), ke(e, "class", "svelte-1lrphxw");
    },
    m(n, i) {
      Il(n, e, i), on(e, t);
    },
    p(n, i) {
      i & /*label*/
      2 && Xi(
        t,
        /*label*/
        n[1]
      );
    },
    d(n) {
      n && Ol(e);
    }
  };
}
function xi(l) {
  let e, t, n, i, o, a, f, s = (
    /*show_label*/
    l[2] && Vn(l)
  );
  return i = new /*Icon*/
  l[0]({}), {
    c() {
      e = an("button"), s && s.c(), t = Zi(), n = an("div"), qi(i.$$.fragment), ke(n, "class", "svelte-1lrphxw"), Z(
        n,
        "small",
        /*size*/
        l[4] === "small"
      ), Z(
        n,
        "large",
        /*size*/
        l[4] === "large"
      ), Z(
        n,
        "medium",
        /*size*/
        l[4] === "medium"
      ), e.disabled = /*disabled*/
      l[7], ke(
        e,
        "aria-label",
        /*label*/
        l[1]
      ), ke(
        e,
        "aria-haspopup",
        /*hasPopup*/
        l[8]
      ), ke(
        e,
        "title",
        /*label*/
        l[1]
      ), ke(e, "class", "svelte-1lrphxw"), Z(
        e,
        "pending",
        /*pending*/
        l[3]
      ), Z(
        e,
        "padded",
        /*padded*/
        l[5]
      ), Z(
        e,
        "highlight",
        /*highlight*/
        l[6]
      ), Z(
        e,
        "transparent",
        /*transparent*/
        l[9]
      ), Ze(e, "color", !/*disabled*/
      l[7] && /*_color*/
      l[12] ? (
        /*_color*/
        l[12]
      ) : "var(--block-label-text-color)"), Ze(e, "--bg-color", /*disabled*/
      l[7] ? "auto" : (
        /*background*/
        l[10]
      )), Ze(
        e,
        "margin-left",
        /*offset*/
        l[11] + "px"
      );
    },
    m(r, u) {
      Il(r, e, u), s && s.m(e, null), on(e, t), on(e, n), Yi(i, n, null), o = !0, a || (f = Vi(
        e,
        "click",
        /*click_handler*/
        l[14]
      ), a = !0);
    },
    p(r, [u]) {
      /*show_label*/
      r[2] ? s ? s.p(r, u) : (s = Vn(r), s.c(), s.m(e, t)) : s && (s.d(1), s = null), (!o || u & /*size*/
      16) && Z(
        n,
        "small",
        /*size*/
        r[4] === "small"
      ), (!o || u & /*size*/
      16) && Z(
        n,
        "large",
        /*size*/
        r[4] === "large"
      ), (!o || u & /*size*/
      16) && Z(
        n,
        "medium",
        /*size*/
        r[4] === "medium"
      ), (!o || u & /*disabled*/
      128) && (e.disabled = /*disabled*/
      r[7]), (!o || u & /*label*/
      2) && ke(
        e,
        "aria-label",
        /*label*/
        r[1]
      ), (!o || u & /*hasPopup*/
      256) && ke(
        e,
        "aria-haspopup",
        /*hasPopup*/
        r[8]
      ), (!o || u & /*label*/
      2) && ke(
        e,
        "title",
        /*label*/
        r[1]
      ), (!o || u & /*pending*/
      8) && Z(
        e,
        "pending",
        /*pending*/
        r[3]
      ), (!o || u & /*padded*/
      32) && Z(
        e,
        "padded",
        /*padded*/
        r[5]
      ), (!o || u & /*highlight*/
      64) && Z(
        e,
        "highlight",
        /*highlight*/
        r[6]
      ), (!o || u & /*transparent*/
      512) && Z(
        e,
        "transparent",
        /*transparent*/
        r[9]
      ), u & /*disabled, _color*/
      4224 && Ze(e, "color", !/*disabled*/
      r[7] && /*_color*/
      r[12] ? (
        /*_color*/
        r[12]
      ) : "var(--block-label-text-color)"), u & /*disabled, background*/
      1152 && Ze(e, "--bg-color", /*disabled*/
      r[7] ? "auto" : (
        /*background*/
        r[10]
      )), u & /*offset*/
      2048 && Ze(
        e,
        "margin-left",
        /*offset*/
        r[11] + "px"
      );
    },
    i(r) {
      o || (Ji(i.$$.fragment, r), o = !0);
    },
    o(r) {
      Qi(i.$$.fragment, r), o = !1;
    },
    d(r) {
      r && Ol(e), s && s.d(), Gi(i), a = !1, f();
    }
  };
}
function $i(l, e, t) {
  let n, { Icon: i } = e, { label: o = "" } = e, { show_label: a = !1 } = e, { pending: f = !1 } = e, { size: s = "small" } = e, { padded: r = !0 } = e, { highlight: u = !1 } = e, { disabled: _ = !1 } = e, { hasPopup: b = !1 } = e, { color: m = "var(--block-label-text-color)" } = e, { transparent: S = !1 } = e, { background: p = "var(--background-fill-primary)" } = e, { offset: A = 0 } = e;
  function D(h) {
    Bi.call(this, l, h);
  }
  return l.$$set = (h) => {
    "Icon" in h && t(0, i = h.Icon), "label" in h && t(1, o = h.label), "show_label" in h && t(2, a = h.show_label), "pending" in h && t(3, f = h.pending), "size" in h && t(4, s = h.size), "padded" in h && t(5, r = h.padded), "highlight" in h && t(6, u = h.highlight), "disabled" in h && t(7, _ = h.disabled), "hasPopup" in h && t(8, b = h.hasPopup), "color" in h && t(13, m = h.color), "transparent" in h && t(9, S = h.transparent), "background" in h && t(10, p = h.background), "offset" in h && t(11, A = h.offset);
  }, l.$$.update = () => {
    l.$$.dirty & /*highlight, color*/
    8256 && t(12, n = u ? "var(--color-accent)" : m);
  }, [
    i,
    o,
    a,
    f,
    s,
    r,
    u,
    _,
    b,
    S,
    p,
    A,
    n,
    m,
    D
  ];
}
class sn extends Hi {
  constructor(e) {
    super(), Wi(this, e, $i, xi, ji, {
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
  SvelteComponent: eo,
  append: to,
  attr: Wt,
  binding_callbacks: no,
  create_slot: lo,
  detach: io,
  element: Yn,
  get_all_dirty_from_scope: oo,
  get_slot_changes: ao,
  init: so,
  insert: ro,
  safe_not_equal: fo,
  toggle_class: De,
  transition_in: co,
  transition_out: uo,
  update_slot_base: _o
} = window.__gradio__svelte__internal;
function mo(l) {
  let e, t, n;
  const i = (
    /*#slots*/
    l[5].default
  ), o = lo(
    i,
    l,
    /*$$scope*/
    l[4],
    null
  );
  return {
    c() {
      e = Yn("div"), t = Yn("div"), o && o.c(), Wt(t, "class", "icon svelte-3w3rth"), Wt(e, "class", "empty svelte-3w3rth"), Wt(e, "aria-label", "Empty value"), De(
        e,
        "small",
        /*size*/
        l[0] === "small"
      ), De(
        e,
        "large",
        /*size*/
        l[0] === "large"
      ), De(
        e,
        "unpadded_box",
        /*unpadded_box*/
        l[1]
      ), De(
        e,
        "small_parent",
        /*parent_height*/
        l[3]
      );
    },
    m(a, f) {
      ro(a, e, f), to(e, t), o && o.m(t, null), l[6](e), n = !0;
    },
    p(a, [f]) {
      o && o.p && (!n || f & /*$$scope*/
      16) && _o(
        o,
        i,
        a,
        /*$$scope*/
        a[4],
        n ? ao(
          i,
          /*$$scope*/
          a[4],
          f,
          null
        ) : oo(
          /*$$scope*/
          a[4]
        ),
        null
      ), (!n || f & /*size*/
      1) && De(
        e,
        "small",
        /*size*/
        a[0] === "small"
      ), (!n || f & /*size*/
      1) && De(
        e,
        "large",
        /*size*/
        a[0] === "large"
      ), (!n || f & /*unpadded_box*/
      2) && De(
        e,
        "unpadded_box",
        /*unpadded_box*/
        a[1]
      ), (!n || f & /*parent_height*/
      8) && De(
        e,
        "small_parent",
        /*parent_height*/
        a[3]
      );
    },
    i(a) {
      n || (co(o, a), n = !0);
    },
    o(a) {
      uo(o, a), n = !1;
    },
    d(a) {
      a && io(e), o && o.d(a), l[6](null);
    }
  };
}
function ho(l, e, t) {
  let n, { $$slots: i = {}, $$scope: o } = e, { size: a = "small" } = e, { unpadded_box: f = !1 } = e, s;
  function r(_) {
    var b;
    if (!_) return !1;
    const { height: m } = _.getBoundingClientRect(), { height: S } = ((b = _.parentElement) === null || b === void 0 ? void 0 : b.getBoundingClientRect()) || { height: m };
    return m > S + 2;
  }
  function u(_) {
    no[_ ? "unshift" : "push"](() => {
      s = _, t(2, s);
    });
  }
  return l.$$set = (_) => {
    "size" in _ && t(0, a = _.size), "unpadded_box" in _ && t(1, f = _.unpadded_box), "$$scope" in _ && t(4, o = _.$$scope);
  }, l.$$.update = () => {
    l.$$.dirty & /*el*/
    4 && t(3, n = r(s));
  }, [a, f, s, n, o, i, u];
}
class go extends eo {
  constructor(e) {
    super(), so(this, e, ho, mo, fo, { size: 0, unpadded_box: 1 });
  }
}
const {
  SvelteComponent: bo,
  append: Vt,
  attr: fe,
  detach: po,
  init: wo,
  insert: To,
  noop: Yt,
  safe_not_equal: Eo,
  set_style: pe,
  svg_element: Lt
} = window.__gradio__svelte__internal;
function Ao(l) {
  let e, t, n, i;
  return {
    c() {
      e = Lt("svg"), t = Lt("g"), n = Lt("path"), i = Lt("path"), fe(n, "d", "M18,6L6.087,17.913"), pe(n, "fill", "none"), pe(n, "fill-rule", "nonzero"), pe(n, "stroke-width", "2px"), fe(t, "transform", "matrix(1.14096,-0.140958,-0.140958,1.14096,-0.0559523,0.0559523)"), fe(i, "d", "M4.364,4.364L19.636,19.636"), pe(i, "fill", "none"), pe(i, "fill-rule", "nonzero"), pe(i, "stroke-width", "2px"), fe(e, "width", "100%"), fe(e, "height", "100%"), fe(e, "viewBox", "0 0 24 24"), fe(e, "version", "1.1"), fe(e, "xmlns", "http://www.w3.org/2000/svg"), fe(e, "xmlns:xlink", "http://www.w3.org/1999/xlink"), fe(e, "xml:space", "preserve"), fe(e, "stroke", "currentColor"), pe(e, "fill-rule", "evenodd"), pe(e, "clip-rule", "evenodd"), pe(e, "stroke-linecap", "round"), pe(e, "stroke-linejoin", "round");
    },
    m(o, a) {
      To(o, e, a), Vt(e, t), Vt(t, n), Vt(e, i);
    },
    p: Yt,
    i: Yt,
    o: Yt,
    d(o) {
      o && po(e);
    }
  };
}
class ko extends bo {
  constructor(e) {
    super(), wo(this, e, null, Ao, Eo, {});
  }
}
const {
  SvelteComponent: vo,
  append: So,
  attr: Ke,
  detach: yo,
  init: Co,
  insert: Lo,
  noop: jt,
  safe_not_equal: Ro,
  svg_element: jn
} = window.__gradio__svelte__internal;
function Do(l) {
  let e, t;
  return {
    c() {
      e = jn("svg"), t = jn("path"), Ke(t, "fill", "currentColor"), Ke(t, "d", "M26 24v4H6v-4H4v4a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2v-4zm0-10l-1.41-1.41L17 20.17V2h-2v18.17l-7.59-7.58L6 14l10 10l10-10z"), Ke(e, "xmlns", "http://www.w3.org/2000/svg"), Ke(e, "width", "100%"), Ke(e, "height", "100%"), Ke(e, "viewBox", "0 0 32 32");
    },
    m(n, i) {
      Lo(n, e, i), So(e, t);
    },
    p: jt,
    i: jt,
    o: jt,
    d(n) {
      n && yo(e);
    }
  };
}
class No extends vo {
  constructor(e) {
    super(), Co(this, e, null, Do, Ro, {});
  }
}
const {
  SvelteComponent: Mo,
  append: Xn,
  attr: x,
  detach: Oo,
  init: Io,
  insert: Po,
  noop: Xt,
  safe_not_equal: Fo,
  svg_element: Zt
} = window.__gradio__svelte__internal;
function Uo(l) {
  let e, t, n;
  return {
    c() {
      e = Zt("svg"), t = Zt("path"), n = Zt("polyline"), x(t, "d", "M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"), x(n, "points", "13 2 13 9 20 9"), x(e, "xmlns", "http://www.w3.org/2000/svg"), x(e, "width", "100%"), x(e, "height", "100%"), x(e, "viewBox", "0 0 24 24"), x(e, "fill", "none"), x(e, "stroke", "currentColor"), x(e, "stroke-width", "1.5"), x(e, "stroke-linecap", "round"), x(e, "stroke-linejoin", "round"), x(e, "class", "feather feather-file");
    },
    m(i, o) {
      Po(i, e, o), Xn(e, t), Xn(e, n);
    },
    p: Xt,
    i: Xt,
    o: Xt,
    d(i) {
      i && Oo(e);
    }
  };
}
class Tn extends Mo {
  constructor(e) {
    super(), Io(this, e, null, Uo, Fo, {});
  }
}
const {
  SvelteComponent: zo,
  append: Zn,
  attr: $,
  detach: Ho,
  init: Bo,
  insert: qo,
  noop: Kt,
  safe_not_equal: Go,
  svg_element: Jt
} = window.__gradio__svelte__internal;
function Wo(l) {
  let e, t, n;
  return {
    c() {
      e = Jt("svg"), t = Jt("polyline"), n = Jt("path"), $(t, "points", "1 4 1 10 7 10"), $(n, "d", "M3.51 15a9 9 0 1 0 2.13-9.36L1 10"), $(e, "xmlns", "http://www.w3.org/2000/svg"), $(e, "width", "100%"), $(e, "height", "100%"), $(e, "viewBox", "0 0 24 24"), $(e, "fill", "none"), $(e, "stroke", "currentColor"), $(e, "stroke-width", "2"), $(e, "stroke-linecap", "round"), $(e, "stroke-linejoin", "round"), $(e, "class", "feather feather-rotate-ccw");
    },
    m(i, o) {
      qo(i, e, o), Zn(e, t), Zn(e, n);
    },
    p: Kt,
    i: Kt,
    o: Kt,
    d(i) {
      i && Ho(e);
    }
  };
}
class Vo extends zo {
  constructor(e) {
    super(), Bo(this, e, null, Wo, Go, {});
  }
}
const Yo = [
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
], Kn = {
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
Yo.reduce(
  (l, { color: e, primary: t, secondary: n }) => ({
    ...l,
    [e]: {
      primary: Kn[e][t],
      secondary: Kn[e][n]
    }
  }),
  {}
);
const {
  SvelteComponent: jo,
  add_flush_callback: Xo,
  append: Rt,
  attr: He,
  bind: Jn,
  binding_callbacks: rn,
  check_outros: Pl,
  construct_svelte_component: Qn,
  create_component: ht,
  destroy_component: gt,
  detach: fn,
  element: Qt,
  empty: Zo,
  group_outros: Fl,
  init: Ko,
  insert: cn,
  mount_component: bt,
  safe_not_equal: Jo,
  space: un,
  transition_in: Ne,
  transition_out: qe
} = window.__gradio__svelte__internal;
function xn(l) {
  let e, t, n, i, o, a, f, s, r, u, _;
  n = new sn({ props: { Icon: Vo, label: "Undo" } }), n.$on(
    "click",
    /*click_handler*/
    l[14]
  ), a = new sn({
    props: {
      Icon: No,
      label: (
        /*i18n*/
        l[3]("common.download")
      )
    }
  });
  function b(p) {
    l[16](p);
  }
  var m = (
    /*Canvas3DGSComponent*/
    l[10]
  );
  function S(p, A) {
    let D = {
      value: (
        /*value*/
        p[0]
      ),
      camera_width: (
        /*camera_width*/
        p[4]
      ),
      camera_height: (
        /*camera_height*/
        p[5]
      ),
      camera_fx: (
        /*camera_fx*/
        p[6]
      ),
      camera_fy: (
        /*camera_fy*/
        p[7]
      ),
      camera_near: (
        /*camera_near*/
        p[8]
      ),
      camera_far: (
        /*camera_far*/
        p[9]
      )
    };
    return (
      /*resolved_url*/
      p[12] !== void 0 && (D.resolved_url = /*resolved_url*/
      p[12]), { props: D }
    );
  }
  return m && (r = Qn(m, S(l)), l[15](r), rn.push(() => Jn(r, "resolved_url", b))), {
    c() {
      e = Qt("div"), t = Qt("div"), ht(n.$$.fragment), i = un(), o = Qt("a"), ht(a.$$.fragment), s = un(), r && ht(r.$$.fragment), He(
        o,
        "href",
        /*resolved_url*/
        l[12]
      ), He(o, "target", window.__is_colab__ ? "_blank" : null), He(o, "download", f = window.__is_colab__ ? null : (
        /*value*/
        l[0].file.orig_name || /*value*/
        l[0].file.path
      )), He(t, "class", "buttons svelte-10ngalm"), He(e, "class", "model3DGSCamera svelte-10ngalm");
    },
    m(p, A) {
      cn(p, e, A), Rt(e, t), bt(n, t, null), Rt(t, i), Rt(t, o), bt(a, o, null), Rt(e, s), r && bt(r, e, null), _ = !0;
    },
    p(p, A) {
      const D = {};
      if (A & /*i18n*/
      8 && (D.label = /*i18n*/
      p[3]("common.download")), a.$set(D), (!_ || A & /*resolved_url*/
      4096) && He(
        o,
        "href",
        /*resolved_url*/
        p[12]
      ), (!_ || A & /*value*/
      1 && f !== (f = window.__is_colab__ ? null : (
        /*value*/
        p[0].file.orig_name || /*value*/
        p[0].file.path
      ))) && He(o, "download", f), A & /*Canvas3DGSComponent*/
      1024 && m !== (m = /*Canvas3DGSComponent*/
      p[10])) {
        if (r) {
          Fl();
          const h = r;
          qe(h.$$.fragment, 1, 0, () => {
            gt(h, 1);
          }), Pl();
        }
        m ? (r = Qn(m, S(p)), p[15](r), rn.push(() => Jn(r, "resolved_url", b)), ht(r.$$.fragment), Ne(r.$$.fragment, 1), bt(r, e, null)) : r = null;
      } else if (m) {
        const h = {};
        A & /*value*/
        1 && (h.value = /*value*/
        p[0]), A & /*camera_width*/
        16 && (h.camera_width = /*camera_width*/
        p[4]), A & /*camera_height*/
        32 && (h.camera_height = /*camera_height*/
        p[5]), A & /*camera_fx*/
        64 && (h.camera_fx = /*camera_fx*/
        p[6]), A & /*camera_fy*/
        128 && (h.camera_fy = /*camera_fy*/
        p[7]), A & /*camera_near*/
        256 && (h.camera_near = /*camera_near*/
        p[8]), A & /*camera_far*/
        512 && (h.camera_far = /*camera_far*/
        p[9]), !u && A & /*resolved_url*/
        4096 && (u = !0, h.resolved_url = /*resolved_url*/
        p[12], Xo(() => u = !1)), r.$set(h);
      }
    },
    i(p) {
      _ || (Ne(n.$$.fragment, p), Ne(a.$$.fragment, p), r && Ne(r.$$.fragment, p), _ = !0);
    },
    o(p) {
      qe(n.$$.fragment, p), qe(a.$$.fragment, p), r && qe(r.$$.fragment, p), _ = !1;
    },
    d(p) {
      p && fn(e), gt(n), gt(a), l[15](null), r && gt(r);
    }
  };
}
function Qo(l) {
  let e, t, n, i;
  e = new Ml({
    props: {
      show_label: (
        /*show_label*/
        l[2]
      ),
      Icon: Tn,
      label: (
        /*label*/
        l[1] || /*i18n*/
        l[3]("3D_model.3d_model")
      )
    }
  });
  let o = (
    /*value*/
    l[0] && xn(l)
  );
  return {
    c() {
      ht(e.$$.fragment), t = un(), o && o.c(), n = Zo();
    },
    m(a, f) {
      bt(e, a, f), cn(a, t, f), o && o.m(a, f), cn(a, n, f), i = !0;
    },
    p(a, [f]) {
      const s = {};
      f & /*show_label*/
      4 && (s.show_label = /*show_label*/
      a[2]), f & /*label, i18n*/
      10 && (s.label = /*label*/
      a[1] || /*i18n*/
      a[3]("3D_model.3d_model")), e.$set(s), /*value*/
      a[0] ? o ? (o.p(a, f), f & /*value*/
      1 && Ne(o, 1)) : (o = xn(a), o.c(), Ne(o, 1), o.m(n.parentNode, n)) : o && (Fl(), qe(o, 1, 1, () => {
        o = null;
      }), Pl());
    },
    i(a) {
      i || (Ne(e.$$.fragment, a), Ne(o), i = !0);
    },
    o(a) {
      qe(e.$$.fragment, a), qe(o), i = !1;
    },
    d(a) {
      a && (fn(t), fn(n)), gt(e, a), o && o.d(a);
    }
  };
}
function xo(l, e, t) {
  var n = this && this.__awaiter || function(g, k, q, ie) {
    function oe(I) {
      return I instanceof q ? I : new q(function(W) {
        W(I);
      });
    }
    return new (q || (q = Promise))(function(I, W) {
      function ve(z) {
        try {
          ae(ie.next(z));
        } catch (Se) {
          W(Se);
        }
      }
      function K(z) {
        try {
          ae(ie.throw(z));
        } catch (Se) {
          W(Se);
        }
      }
      function ae(z) {
        z.done ? I(z.value) : oe(z.value).then(ve, K);
      }
      ae((ie = ie.apply(g, k || [])).next());
    });
  };
  let { value: i = null } = e, { label: o = "" } = e, { show_label: a } = e, { i18n: f } = e, { camera_width: s = null } = e, { camera_height: r = null } = e, { camera_fx: u = null } = e, { camera_fy: _ = null } = e, { camera_near: b = null } = e, { camera_far: m = null } = e, S;
  function p() {
    return n(this, void 0, void 0, function* () {
      return (yield import("./Canvas3DGSCamera-CJprx23B.js")).default;
    });
  }
  let A;
  function D() {
    A == null || A.reset_camera_pose();
  }
  let h;
  const w = () => D();
  function y(g) {
    rn[g ? "unshift" : "push"](() => {
      A = g, t(11, A);
    });
  }
  function O(g) {
    h = g, t(12, h);
  }
  return l.$$set = (g) => {
    "value" in g && t(0, i = g.value), "label" in g && t(1, o = g.label), "show_label" in g && t(2, a = g.show_label), "i18n" in g && t(3, f = g.i18n), "camera_width" in g && t(4, s = g.camera_width), "camera_height" in g && t(5, r = g.camera_height), "camera_fx" in g && t(6, u = g.camera_fx), "camera_fy" in g && t(7, _ = g.camera_fy), "camera_near" in g && t(8, b = g.camera_near), "camera_far" in g && t(9, m = g.camera_far);
  }, l.$$.update = () => {
    l.$$.dirty & /*value*/
    1 && i && p().then((g) => {
      t(10, S = g);
    });
  }, [
    i,
    o,
    a,
    f,
    s,
    r,
    u,
    _,
    b,
    m,
    S,
    A,
    h,
    D,
    w,
    y,
    O
  ];
}
class $o extends jo {
  constructor(e) {
    super(), Ko(this, e, xo, Qo, Jo, {
      value: 0,
      label: 1,
      show_label: 2,
      i18n: 3,
      camera_width: 4,
      camera_height: 5,
      camera_fx: 6,
      camera_fy: 7,
      camera_near: 8,
      camera_far: 9
    });
  }
}
function xe(l) {
  let e = ["", "k", "M", "G", "T", "P", "E", "Z"], t = 0;
  for (; l > 1e3 && t < e.length - 1; )
    l /= 1e3, t++;
  let n = e[t];
  return (Number.isInteger(l) ? l : l.toFixed(1)) + n;
}
function It() {
}
function ea(l, e) {
  return l != l ? e == e : l !== e || l && typeof l == "object" || typeof l == "function";
}
const Ul = typeof window < "u";
let $n = Ul ? () => window.performance.now() : () => Date.now(), zl = Ul ? (l) => requestAnimationFrame(l) : It;
const $e = /* @__PURE__ */ new Set();
function Hl(l) {
  $e.forEach((e) => {
    e.c(l) || ($e.delete(e), e.f());
  }), $e.size !== 0 && zl(Hl);
}
function ta(l) {
  let e;
  return $e.size === 0 && zl(Hl), {
    promise: new Promise((t) => {
      $e.add(e = { c: l, f: t });
    }),
    abort() {
      $e.delete(e);
    }
  };
}
const Je = [];
function na(l, e = It) {
  let t;
  const n = /* @__PURE__ */ new Set();
  function i(f) {
    if (ea(l, f) && (l = f, t)) {
      const s = !Je.length;
      for (const r of n)
        r[1](), Je.push(r, l);
      if (s) {
        for (let r = 0; r < Je.length; r += 2)
          Je[r][0](Je[r + 1]);
        Je.length = 0;
      }
    }
  }
  function o(f) {
    i(f(l));
  }
  function a(f, s = It) {
    const r = [f, s];
    return n.add(r), n.size === 1 && (t = e(i, o) || It), f(l), () => {
      n.delete(r), n.size === 0 && t && (t(), t = null);
    };
  }
  return { set: i, update: o, subscribe: a };
}
function el(l) {
  return Object.prototype.toString.call(l) === "[object Date]";
}
function _n(l, e, t, n) {
  if (typeof t == "number" || el(t)) {
    const i = n - t, o = (t - e) / (l.dt || 1 / 60), a = l.opts.stiffness * i, f = l.opts.damping * o, s = (a - f) * l.inv_mass, r = (o + s) * l.dt;
    return Math.abs(r) < l.opts.precision && Math.abs(i) < l.opts.precision ? n : (l.settled = !1, el(t) ? new Date(t.getTime() + r) : t + r);
  } else {
    if (Array.isArray(t))
      return t.map(
        (i, o) => _n(l, e[o], t[o], n[o])
      );
    if (typeof t == "object") {
      const i = {};
      for (const o in t)
        i[o] = _n(l, e[o], t[o], n[o]);
      return i;
    } else
      throw new Error(`Cannot spring ${typeof t} values`);
  }
}
function tl(l, e = {}) {
  const t = na(l), { stiffness: n = 0.15, damping: i = 0.8, precision: o = 0.01 } = e;
  let a, f, s, r = l, u = l, _ = 1, b = 0, m = !1;
  function S(A, D = {}) {
    u = A;
    const h = s = {};
    return l == null || D.hard || p.stiffness >= 1 && p.damping >= 1 ? (m = !0, a = $n(), r = A, t.set(l = u), Promise.resolve()) : (D.soft && (b = 1 / ((D.soft === !0 ? 0.5 : +D.soft) * 60), _ = 0), f || (a = $n(), m = !1, f = ta((w) => {
      if (m)
        return m = !1, f = null, !1;
      _ = Math.min(_ + b, 1);
      const y = {
        inv_mass: _,
        opts: p,
        settled: !0,
        dt: (w - a) * 60 / 1e3
      }, O = _n(y, r, l, u);
      return a = w, r = l, t.set(l = O), y.settled && (f = null), !y.settled;
    })), new Promise((w) => {
      f.promise.then(() => {
        h === s && w();
      });
    }));
  }
  const p = {
    set: S,
    update: (A, D) => S(A(u, l), D),
    subscribe: t.subscribe,
    stiffness: n,
    damping: i,
    precision: o
  };
  return p;
}
const {
  SvelteComponent: la,
  append: ce,
  attr: N,
  component_subscribe: nl,
  detach: ia,
  element: oa,
  init: aa,
  insert: sa,
  noop: ll,
  safe_not_equal: ra,
  set_style: Dt,
  svg_element: ue,
  toggle_class: il
} = window.__gradio__svelte__internal, { onMount: fa } = window.__gradio__svelte__internal;
function ca(l) {
  let e, t, n, i, o, a, f, s, r, u, _, b;
  return {
    c() {
      e = oa("div"), t = ue("svg"), n = ue("g"), i = ue("path"), o = ue("path"), a = ue("path"), f = ue("path"), s = ue("g"), r = ue("path"), u = ue("path"), _ = ue("path"), b = ue("path"), N(i, "d", "M255.926 0.754768L509.702 139.936V221.027L255.926 81.8465V0.754768Z"), N(i, "fill", "#FF7C00"), N(i, "fill-opacity", "0.4"), N(i, "class", "svelte-43sxxs"), N(o, "d", "M509.69 139.936L254.981 279.641V361.255L509.69 221.55V139.936Z"), N(o, "fill", "#FF7C00"), N(o, "class", "svelte-43sxxs"), N(a, "d", "M0.250138 139.937L254.981 279.641V361.255L0.250138 221.55V139.937Z"), N(a, "fill", "#FF7C00"), N(a, "fill-opacity", "0.4"), N(a, "class", "svelte-43sxxs"), N(f, "d", "M255.923 0.232622L0.236328 139.936V221.55L255.923 81.8469V0.232622Z"), N(f, "fill", "#FF7C00"), N(f, "class", "svelte-43sxxs"), Dt(n, "transform", "translate(" + /*$top*/
      l[1][0] + "px, " + /*$top*/
      l[1][1] + "px)"), N(r, "d", "M255.926 141.5L509.702 280.681V361.773L255.926 222.592V141.5Z"), N(r, "fill", "#FF7C00"), N(r, "fill-opacity", "0.4"), N(r, "class", "svelte-43sxxs"), N(u, "d", "M509.69 280.679L254.981 420.384V501.998L509.69 362.293V280.679Z"), N(u, "fill", "#FF7C00"), N(u, "class", "svelte-43sxxs"), N(_, "d", "M0.250138 280.681L254.981 420.386V502L0.250138 362.295V280.681Z"), N(_, "fill", "#FF7C00"), N(_, "fill-opacity", "0.4"), N(_, "class", "svelte-43sxxs"), N(b, "d", "M255.923 140.977L0.236328 280.68V362.294L255.923 222.591V140.977Z"), N(b, "fill", "#FF7C00"), N(b, "class", "svelte-43sxxs"), Dt(s, "transform", "translate(" + /*$bottom*/
      l[2][0] + "px, " + /*$bottom*/
      l[2][1] + "px)"), N(t, "viewBox", "-1200 -1200 3000 3000"), N(t, "fill", "none"), N(t, "xmlns", "http://www.w3.org/2000/svg"), N(t, "class", "svelte-43sxxs"), N(e, "class", "svelte-43sxxs"), il(
        e,
        "margin",
        /*margin*/
        l[0]
      );
    },
    m(m, S) {
      sa(m, e, S), ce(e, t), ce(t, n), ce(n, i), ce(n, o), ce(n, a), ce(n, f), ce(t, s), ce(s, r), ce(s, u), ce(s, _), ce(s, b);
    },
    p(m, [S]) {
      S & /*$top*/
      2 && Dt(n, "transform", "translate(" + /*$top*/
      m[1][0] + "px, " + /*$top*/
      m[1][1] + "px)"), S & /*$bottom*/
      4 && Dt(s, "transform", "translate(" + /*$bottom*/
      m[2][0] + "px, " + /*$bottom*/
      m[2][1] + "px)"), S & /*margin*/
      1 && il(
        e,
        "margin",
        /*margin*/
        m[0]
      );
    },
    i: ll,
    o: ll,
    d(m) {
      m && ia(e);
    }
  };
}
function ua(l, e, t) {
  let n, i;
  var o = this && this.__awaiter || function(m, S, p, A) {
    function D(h) {
      return h instanceof p ? h : new p(function(w) {
        w(h);
      });
    }
    return new (p || (p = Promise))(function(h, w) {
      function y(k) {
        try {
          g(A.next(k));
        } catch (q) {
          w(q);
        }
      }
      function O(k) {
        try {
          g(A.throw(k));
        } catch (q) {
          w(q);
        }
      }
      function g(k) {
        k.done ? h(k.value) : D(k.value).then(y, O);
      }
      g((A = A.apply(m, S || [])).next());
    });
  };
  let { margin: a = !0 } = e;
  const f = tl([0, 0]);
  nl(l, f, (m) => t(1, n = m));
  const s = tl([0, 0]);
  nl(l, s, (m) => t(2, i = m));
  let r;
  function u() {
    return o(this, void 0, void 0, function* () {
      yield Promise.all([f.set([125, 140]), s.set([-125, -140])]), yield Promise.all([f.set([-125, 140]), s.set([125, -140])]), yield Promise.all([f.set([-125, 0]), s.set([125, -0])]), yield Promise.all([f.set([125, 0]), s.set([-125, 0])]);
    });
  }
  function _() {
    return o(this, void 0, void 0, function* () {
      yield u(), r || _();
    });
  }
  function b() {
    return o(this, void 0, void 0, function* () {
      yield Promise.all([f.set([125, 0]), s.set([-125, 0])]), _();
    });
  }
  return fa(() => (b(), () => r = !0)), l.$$set = (m) => {
    "margin" in m && t(0, a = m.margin);
  }, [a, n, i, f, s];
}
class _a extends la {
  constructor(e) {
    super(), aa(this, e, ua, ca, ra, { margin: 0 });
  }
}
const {
  SvelteComponent: ma,
  append: Ge,
  attr: de,
  binding_callbacks: ol,
  check_outros: mn,
  create_component: Bl,
  create_slot: ql,
  destroy_component: Gl,
  destroy_each: Wl,
  detach: C,
  element: we,
  empty: lt,
  ensure_array_like: Ft,
  get_all_dirty_from_scope: Vl,
  get_slot_changes: Yl,
  group_outros: dn,
  init: da,
  insert: L,
  mount_component: jl,
  noop: hn,
  safe_not_equal: ha,
  set_data: ne,
  set_style: Me,
  space: te,
  text: F,
  toggle_class: ee,
  transition_in: me,
  transition_out: Te,
  update_slot_base: Xl
} = window.__gradio__svelte__internal, { tick: ga } = window.__gradio__svelte__internal, { onDestroy: ba } = window.__gradio__svelte__internal, { createEventDispatcher: pa } = window.__gradio__svelte__internal, wa = (l) => ({}), al = (l) => ({}), Ta = (l) => ({}), sl = (l) => ({});
function rl(l, e, t) {
  const n = l.slice();
  return n[41] = e[t], n[43] = t, n;
}
function fl(l, e, t) {
  const n = l.slice();
  return n[41] = e[t], n;
}
function Ea(l) {
  let e, t, n, i, o = (
    /*i18n*/
    l[1]("common.error") + ""
  ), a, f, s;
  t = new sn({
    props: {
      Icon: ko,
      label: (
        /*i18n*/
        l[1]("common.clear")
      ),
      disabled: !1
    }
  }), t.$on(
    "click",
    /*click_handler*/
    l[32]
  );
  const r = (
    /*#slots*/
    l[30].error
  ), u = ql(
    r,
    l,
    /*$$scope*/
    l[29],
    al
  );
  return {
    c() {
      e = we("div"), Bl(t.$$.fragment), n = te(), i = we("span"), a = F(o), f = te(), u && u.c(), de(e, "class", "clear-status svelte-v0wucf"), de(i, "class", "error svelte-v0wucf");
    },
    m(_, b) {
      L(_, e, b), jl(t, e, null), L(_, n, b), L(_, i, b), Ge(i, a), L(_, f, b), u && u.m(_, b), s = !0;
    },
    p(_, b) {
      const m = {};
      b[0] & /*i18n*/
      2 && (m.label = /*i18n*/
      _[1]("common.clear")), t.$set(m), (!s || b[0] & /*i18n*/
      2) && o !== (o = /*i18n*/
      _[1]("common.error") + "") && ne(a, o), u && u.p && (!s || b[0] & /*$$scope*/
      536870912) && Xl(
        u,
        r,
        _,
        /*$$scope*/
        _[29],
        s ? Yl(
          r,
          /*$$scope*/
          _[29],
          b,
          wa
        ) : Vl(
          /*$$scope*/
          _[29]
        ),
        al
      );
    },
    i(_) {
      s || (me(t.$$.fragment, _), me(u, _), s = !0);
    },
    o(_) {
      Te(t.$$.fragment, _), Te(u, _), s = !1;
    },
    d(_) {
      _ && (C(e), C(n), C(i), C(f)), Gl(t), u && u.d(_);
    }
  };
}
function Aa(l) {
  let e, t, n, i, o, a, f, s, r, u = (
    /*variant*/
    l[8] === "default" && /*show_eta_bar*/
    l[18] && /*show_progress*/
    l[6] === "full" && cl(l)
  );
  function _(w, y) {
    if (
      /*progress*/
      w[7]
    ) return Sa;
    if (
      /*queue_position*/
      w[2] !== null && /*queue_size*/
      w[3] !== void 0 && /*queue_position*/
      w[2] >= 0
    ) return va;
    if (
      /*queue_position*/
      w[2] === 0
    ) return ka;
  }
  let b = _(l), m = b && b(l), S = (
    /*timer*/
    l[5] && ml(l)
  );
  const p = [Ra, La], A = [];
  function D(w, y) {
    return (
      /*last_progress_level*/
      w[15] != null ? 0 : (
        /*show_progress*/
        w[6] === "full" ? 1 : -1
      )
    );
  }
  ~(o = D(l)) && (a = A[o] = p[o](l));
  let h = !/*timer*/
  l[5] && Tl(l);
  return {
    c() {
      u && u.c(), e = te(), t = we("div"), m && m.c(), n = te(), S && S.c(), i = te(), a && a.c(), f = te(), h && h.c(), s = lt(), de(t, "class", "progress-text svelte-v0wucf"), ee(
        t,
        "meta-text-center",
        /*variant*/
        l[8] === "center"
      ), ee(
        t,
        "meta-text",
        /*variant*/
        l[8] === "default"
      );
    },
    m(w, y) {
      u && u.m(w, y), L(w, e, y), L(w, t, y), m && m.m(t, null), Ge(t, n), S && S.m(t, null), L(w, i, y), ~o && A[o].m(w, y), L(w, f, y), h && h.m(w, y), L(w, s, y), r = !0;
    },
    p(w, y) {
      /*variant*/
      w[8] === "default" && /*show_eta_bar*/
      w[18] && /*show_progress*/
      w[6] === "full" ? u ? u.p(w, y) : (u = cl(w), u.c(), u.m(e.parentNode, e)) : u && (u.d(1), u = null), b === (b = _(w)) && m ? m.p(w, y) : (m && m.d(1), m = b && b(w), m && (m.c(), m.m(t, n))), /*timer*/
      w[5] ? S ? S.p(w, y) : (S = ml(w), S.c(), S.m(t, null)) : S && (S.d(1), S = null), (!r || y[0] & /*variant*/
      256) && ee(
        t,
        "meta-text-center",
        /*variant*/
        w[8] === "center"
      ), (!r || y[0] & /*variant*/
      256) && ee(
        t,
        "meta-text",
        /*variant*/
        w[8] === "default"
      );
      let O = o;
      o = D(w), o === O ? ~o && A[o].p(w, y) : (a && (dn(), Te(A[O], 1, 1, () => {
        A[O] = null;
      }), mn()), ~o ? (a = A[o], a ? a.p(w, y) : (a = A[o] = p[o](w), a.c()), me(a, 1), a.m(f.parentNode, f)) : a = null), /*timer*/
      w[5] ? h && (dn(), Te(h, 1, 1, () => {
        h = null;
      }), mn()) : h ? (h.p(w, y), y[0] & /*timer*/
      32 && me(h, 1)) : (h = Tl(w), h.c(), me(h, 1), h.m(s.parentNode, s));
    },
    i(w) {
      r || (me(a), me(h), r = !0);
    },
    o(w) {
      Te(a), Te(h), r = !1;
    },
    d(w) {
      w && (C(e), C(t), C(i), C(f), C(s)), u && u.d(w), m && m.d(), S && S.d(), ~o && A[o].d(w), h && h.d(w);
    }
  };
}
function cl(l) {
  let e, t = `translateX(${/*eta_level*/
  (l[17] || 0) * 100 - 100}%)`;
  return {
    c() {
      e = we("div"), de(e, "class", "eta-bar svelte-v0wucf"), Me(e, "transform", t);
    },
    m(n, i) {
      L(n, e, i);
    },
    p(n, i) {
      i[0] & /*eta_level*/
      131072 && t !== (t = `translateX(${/*eta_level*/
      (n[17] || 0) * 100 - 100}%)`) && Me(e, "transform", t);
    },
    d(n) {
      n && C(e);
    }
  };
}
function ka(l) {
  let e;
  return {
    c() {
      e = F("processing |");
    },
    m(t, n) {
      L(t, e, n);
    },
    p: hn,
    d(t) {
      t && C(e);
    }
  };
}
function va(l) {
  let e, t = (
    /*queue_position*/
    l[2] + 1 + ""
  ), n, i, o, a;
  return {
    c() {
      e = F("queue: "), n = F(t), i = F("/"), o = F(
        /*queue_size*/
        l[3]
      ), a = F(" |");
    },
    m(f, s) {
      L(f, e, s), L(f, n, s), L(f, i, s), L(f, o, s), L(f, a, s);
    },
    p(f, s) {
      s[0] & /*queue_position*/
      4 && t !== (t = /*queue_position*/
      f[2] + 1 + "") && ne(n, t), s[0] & /*queue_size*/
      8 && ne(
        o,
        /*queue_size*/
        f[3]
      );
    },
    d(f) {
      f && (C(e), C(n), C(i), C(o), C(a));
    }
  };
}
function Sa(l) {
  let e, t = Ft(
    /*progress*/
    l[7]
  ), n = [];
  for (let i = 0; i < t.length; i += 1)
    n[i] = _l(fl(l, t, i));
  return {
    c() {
      for (let i = 0; i < n.length; i += 1)
        n[i].c();
      e = lt();
    },
    m(i, o) {
      for (let a = 0; a < n.length; a += 1)
        n[a] && n[a].m(i, o);
      L(i, e, o);
    },
    p(i, o) {
      if (o[0] & /*progress*/
      128) {
        t = Ft(
          /*progress*/
          i[7]
        );
        let a;
        for (a = 0; a < t.length; a += 1) {
          const f = fl(i, t, a);
          n[a] ? n[a].p(f, o) : (n[a] = _l(f), n[a].c(), n[a].m(e.parentNode, e));
        }
        for (; a < n.length; a += 1)
          n[a].d(1);
        n.length = t.length;
      }
    },
    d(i) {
      i && C(e), Wl(n, i);
    }
  };
}
function ul(l) {
  let e, t = (
    /*p*/
    l[41].unit + ""
  ), n, i, o = " ", a;
  function f(u, _) {
    return (
      /*p*/
      u[41].length != null ? Ca : ya
    );
  }
  let s = f(l), r = s(l);
  return {
    c() {
      r.c(), e = te(), n = F(t), i = F(" | "), a = F(o);
    },
    m(u, _) {
      r.m(u, _), L(u, e, _), L(u, n, _), L(u, i, _), L(u, a, _);
    },
    p(u, _) {
      s === (s = f(u)) && r ? r.p(u, _) : (r.d(1), r = s(u), r && (r.c(), r.m(e.parentNode, e))), _[0] & /*progress*/
      128 && t !== (t = /*p*/
      u[41].unit + "") && ne(n, t);
    },
    d(u) {
      u && (C(e), C(n), C(i), C(a)), r.d(u);
    }
  };
}
function ya(l) {
  let e = xe(
    /*p*/
    l[41].index || 0
  ) + "", t;
  return {
    c() {
      t = F(e);
    },
    m(n, i) {
      L(n, t, i);
    },
    p(n, i) {
      i[0] & /*progress*/
      128 && e !== (e = xe(
        /*p*/
        n[41].index || 0
      ) + "") && ne(t, e);
    },
    d(n) {
      n && C(t);
    }
  };
}
function Ca(l) {
  let e = xe(
    /*p*/
    l[41].index || 0
  ) + "", t, n, i = xe(
    /*p*/
    l[41].length
  ) + "", o;
  return {
    c() {
      t = F(e), n = F("/"), o = F(i);
    },
    m(a, f) {
      L(a, t, f), L(a, n, f), L(a, o, f);
    },
    p(a, f) {
      f[0] & /*progress*/
      128 && e !== (e = xe(
        /*p*/
        a[41].index || 0
      ) + "") && ne(t, e), f[0] & /*progress*/
      128 && i !== (i = xe(
        /*p*/
        a[41].length
      ) + "") && ne(o, i);
    },
    d(a) {
      a && (C(t), C(n), C(o));
    }
  };
}
function _l(l) {
  let e, t = (
    /*p*/
    l[41].index != null && ul(l)
  );
  return {
    c() {
      t && t.c(), e = lt();
    },
    m(n, i) {
      t && t.m(n, i), L(n, e, i);
    },
    p(n, i) {
      /*p*/
      n[41].index != null ? t ? t.p(n, i) : (t = ul(n), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(n) {
      n && C(e), t && t.d(n);
    }
  };
}
function ml(l) {
  let e, t = (
    /*eta*/
    l[0] ? `/${/*formatted_eta*/
    l[19]}` : ""
  ), n, i;
  return {
    c() {
      e = F(
        /*formatted_timer*/
        l[20]
      ), n = F(t), i = F("s");
    },
    m(o, a) {
      L(o, e, a), L(o, n, a), L(o, i, a);
    },
    p(o, a) {
      a[0] & /*formatted_timer*/
      1048576 && ne(
        e,
        /*formatted_timer*/
        o[20]
      ), a[0] & /*eta, formatted_eta*/
      524289 && t !== (t = /*eta*/
      o[0] ? `/${/*formatted_eta*/
      o[19]}` : "") && ne(n, t);
    },
    d(o) {
      o && (C(e), C(n), C(i));
    }
  };
}
function La(l) {
  let e, t;
  return e = new _a({
    props: { margin: (
      /*variant*/
      l[8] === "default"
    ) }
  }), {
    c() {
      Bl(e.$$.fragment);
    },
    m(n, i) {
      jl(e, n, i), t = !0;
    },
    p(n, i) {
      const o = {};
      i[0] & /*variant*/
      256 && (o.margin = /*variant*/
      n[8] === "default"), e.$set(o);
    },
    i(n) {
      t || (me(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Te(e.$$.fragment, n), t = !1;
    },
    d(n) {
      Gl(e, n);
    }
  };
}
function Ra(l) {
  let e, t, n, i, o, a = `${/*last_progress_level*/
  l[15] * 100}%`, f = (
    /*progress*/
    l[7] != null && dl(l)
  );
  return {
    c() {
      e = we("div"), t = we("div"), f && f.c(), n = te(), i = we("div"), o = we("div"), de(t, "class", "progress-level-inner svelte-v0wucf"), de(o, "class", "progress-bar svelte-v0wucf"), Me(o, "width", a), de(i, "class", "progress-bar-wrap svelte-v0wucf"), de(e, "class", "progress-level svelte-v0wucf");
    },
    m(s, r) {
      L(s, e, r), Ge(e, t), f && f.m(t, null), Ge(e, n), Ge(e, i), Ge(i, o), l[31](o);
    },
    p(s, r) {
      /*progress*/
      s[7] != null ? f ? f.p(s, r) : (f = dl(s), f.c(), f.m(t, null)) : f && (f.d(1), f = null), r[0] & /*last_progress_level*/
      32768 && a !== (a = `${/*last_progress_level*/
      s[15] * 100}%`) && Me(o, "width", a);
    },
    i: hn,
    o: hn,
    d(s) {
      s && C(e), f && f.d(), l[31](null);
    }
  };
}
function dl(l) {
  let e, t = Ft(
    /*progress*/
    l[7]
  ), n = [];
  for (let i = 0; i < t.length; i += 1)
    n[i] = wl(rl(l, t, i));
  return {
    c() {
      for (let i = 0; i < n.length; i += 1)
        n[i].c();
      e = lt();
    },
    m(i, o) {
      for (let a = 0; a < n.length; a += 1)
        n[a] && n[a].m(i, o);
      L(i, e, o);
    },
    p(i, o) {
      if (o[0] & /*progress_level, progress*/
      16512) {
        t = Ft(
          /*progress*/
          i[7]
        );
        let a;
        for (a = 0; a < t.length; a += 1) {
          const f = rl(i, t, a);
          n[a] ? n[a].p(f, o) : (n[a] = wl(f), n[a].c(), n[a].m(e.parentNode, e));
        }
        for (; a < n.length; a += 1)
          n[a].d(1);
        n.length = t.length;
      }
    },
    d(i) {
      i && C(e), Wl(n, i);
    }
  };
}
function hl(l) {
  let e, t, n, i, o = (
    /*i*/
    l[43] !== 0 && Da()
  ), a = (
    /*p*/
    l[41].desc != null && gl(l)
  ), f = (
    /*p*/
    l[41].desc != null && /*progress_level*/
    l[14] && /*progress_level*/
    l[14][
      /*i*/
      l[43]
    ] != null && bl()
  ), s = (
    /*progress_level*/
    l[14] != null && pl(l)
  );
  return {
    c() {
      o && o.c(), e = te(), a && a.c(), t = te(), f && f.c(), n = te(), s && s.c(), i = lt();
    },
    m(r, u) {
      o && o.m(r, u), L(r, e, u), a && a.m(r, u), L(r, t, u), f && f.m(r, u), L(r, n, u), s && s.m(r, u), L(r, i, u);
    },
    p(r, u) {
      /*p*/
      r[41].desc != null ? a ? a.p(r, u) : (a = gl(r), a.c(), a.m(t.parentNode, t)) : a && (a.d(1), a = null), /*p*/
      r[41].desc != null && /*progress_level*/
      r[14] && /*progress_level*/
      r[14][
        /*i*/
        r[43]
      ] != null ? f || (f = bl(), f.c(), f.m(n.parentNode, n)) : f && (f.d(1), f = null), /*progress_level*/
      r[14] != null ? s ? s.p(r, u) : (s = pl(r), s.c(), s.m(i.parentNode, i)) : s && (s.d(1), s = null);
    },
    d(r) {
      r && (C(e), C(t), C(n), C(i)), o && o.d(r), a && a.d(r), f && f.d(r), s && s.d(r);
    }
  };
}
function Da(l) {
  let e;
  return {
    c() {
      e = F(" /");
    },
    m(t, n) {
      L(t, e, n);
    },
    d(t) {
      t && C(e);
    }
  };
}
function gl(l) {
  let e = (
    /*p*/
    l[41].desc + ""
  ), t;
  return {
    c() {
      t = F(e);
    },
    m(n, i) {
      L(n, t, i);
    },
    p(n, i) {
      i[0] & /*progress*/
      128 && e !== (e = /*p*/
      n[41].desc + "") && ne(t, e);
    },
    d(n) {
      n && C(t);
    }
  };
}
function bl(l) {
  let e;
  return {
    c() {
      e = F("-");
    },
    m(t, n) {
      L(t, e, n);
    },
    d(t) {
      t && C(e);
    }
  };
}
function pl(l) {
  let e = (100 * /*progress_level*/
  (l[14][
    /*i*/
    l[43]
  ] || 0)).toFixed(1) + "", t, n;
  return {
    c() {
      t = F(e), n = F("%");
    },
    m(i, o) {
      L(i, t, o), L(i, n, o);
    },
    p(i, o) {
      o[0] & /*progress_level*/
      16384 && e !== (e = (100 * /*progress_level*/
      (i[14][
        /*i*/
        i[43]
      ] || 0)).toFixed(1) + "") && ne(t, e);
    },
    d(i) {
      i && (C(t), C(n));
    }
  };
}
function wl(l) {
  let e, t = (
    /*p*/
    (l[41].desc != null || /*progress_level*/
    l[14] && /*progress_level*/
    l[14][
      /*i*/
      l[43]
    ] != null) && hl(l)
  );
  return {
    c() {
      t && t.c(), e = lt();
    },
    m(n, i) {
      t && t.m(n, i), L(n, e, i);
    },
    p(n, i) {
      /*p*/
      n[41].desc != null || /*progress_level*/
      n[14] && /*progress_level*/
      n[14][
        /*i*/
        n[43]
      ] != null ? t ? t.p(n, i) : (t = hl(n), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(n) {
      n && C(e), t && t.d(n);
    }
  };
}
function Tl(l) {
  let e, t, n, i;
  const o = (
    /*#slots*/
    l[30]["additional-loading-text"]
  ), a = ql(
    o,
    l,
    /*$$scope*/
    l[29],
    sl
  );
  return {
    c() {
      e = we("p"), t = F(
        /*loading_text*/
        l[9]
      ), n = te(), a && a.c(), de(e, "class", "loading svelte-v0wucf");
    },
    m(f, s) {
      L(f, e, s), Ge(e, t), L(f, n, s), a && a.m(f, s), i = !0;
    },
    p(f, s) {
      (!i || s[0] & /*loading_text*/
      512) && ne(
        t,
        /*loading_text*/
        f[9]
      ), a && a.p && (!i || s[0] & /*$$scope*/
      536870912) && Xl(
        a,
        o,
        f,
        /*$$scope*/
        f[29],
        i ? Yl(
          o,
          /*$$scope*/
          f[29],
          s,
          Ta
        ) : Vl(
          /*$$scope*/
          f[29]
        ),
        sl
      );
    },
    i(f) {
      i || (me(a, f), i = !0);
    },
    o(f) {
      Te(a, f), i = !1;
    },
    d(f) {
      f && (C(e), C(n)), a && a.d(f);
    }
  };
}
function Na(l) {
  let e, t, n, i, o;
  const a = [Aa, Ea], f = [];
  function s(r, u) {
    return (
      /*status*/
      r[4] === "pending" ? 0 : (
        /*status*/
        r[4] === "error" ? 1 : -1
      )
    );
  }
  return ~(t = s(l)) && (n = f[t] = a[t](l)), {
    c() {
      e = we("div"), n && n.c(), de(e, "class", i = "wrap " + /*variant*/
      l[8] + " " + /*show_progress*/
      l[6] + " svelte-v0wucf"), ee(e, "hide", !/*status*/
      l[4] || /*status*/
      l[4] === "complete" || /*show_progress*/
      l[6] === "hidden"), ee(
        e,
        "translucent",
        /*variant*/
        l[8] === "center" && /*status*/
        (l[4] === "pending" || /*status*/
        l[4] === "error") || /*translucent*/
        l[11] || /*show_progress*/
        l[6] === "minimal"
      ), ee(
        e,
        "generating",
        /*status*/
        l[4] === "generating" && /*show_progress*/
        l[6] === "full"
      ), ee(
        e,
        "border",
        /*border*/
        l[12]
      ), Me(
        e,
        "position",
        /*absolute*/
        l[10] ? "absolute" : "static"
      ), Me(
        e,
        "padding",
        /*absolute*/
        l[10] ? "0" : "var(--size-8) 0"
      );
    },
    m(r, u) {
      L(r, e, u), ~t && f[t].m(e, null), l[33](e), o = !0;
    },
    p(r, u) {
      let _ = t;
      t = s(r), t === _ ? ~t && f[t].p(r, u) : (n && (dn(), Te(f[_], 1, 1, () => {
        f[_] = null;
      }), mn()), ~t ? (n = f[t], n ? n.p(r, u) : (n = f[t] = a[t](r), n.c()), me(n, 1), n.m(e, null)) : n = null), (!o || u[0] & /*variant, show_progress*/
      320 && i !== (i = "wrap " + /*variant*/
      r[8] + " " + /*show_progress*/
      r[6] + " svelte-v0wucf")) && de(e, "class", i), (!o || u[0] & /*variant, show_progress, status, show_progress*/
      336) && ee(e, "hide", !/*status*/
      r[4] || /*status*/
      r[4] === "complete" || /*show_progress*/
      r[6] === "hidden"), (!o || u[0] & /*variant, show_progress, variant, status, translucent, show_progress*/
      2384) && ee(
        e,
        "translucent",
        /*variant*/
        r[8] === "center" && /*status*/
        (r[4] === "pending" || /*status*/
        r[4] === "error") || /*translucent*/
        r[11] || /*show_progress*/
        r[6] === "minimal"
      ), (!o || u[0] & /*variant, show_progress, status, show_progress*/
      336) && ee(
        e,
        "generating",
        /*status*/
        r[4] === "generating" && /*show_progress*/
        r[6] === "full"
      ), (!o || u[0] & /*variant, show_progress, border*/
      4416) && ee(
        e,
        "border",
        /*border*/
        r[12]
      ), u[0] & /*absolute*/
      1024 && Me(
        e,
        "position",
        /*absolute*/
        r[10] ? "absolute" : "static"
      ), u[0] & /*absolute*/
      1024 && Me(
        e,
        "padding",
        /*absolute*/
        r[10] ? "0" : "var(--size-8) 0"
      );
    },
    i(r) {
      o || (me(n), o = !0);
    },
    o(r) {
      Te(n), o = !1;
    },
    d(r) {
      r && C(e), ~t && f[t].d(), l[33](null);
    }
  };
}
var Ma = function(l, e, t, n) {
  function i(o) {
    return o instanceof t ? o : new t(function(a) {
      a(o);
    });
  }
  return new (t || (t = Promise))(function(o, a) {
    function f(u) {
      try {
        r(n.next(u));
      } catch (_) {
        a(_);
      }
    }
    function s(u) {
      try {
        r(n.throw(u));
      } catch (_) {
        a(_);
      }
    }
    function r(u) {
      u.done ? o(u.value) : i(u.value).then(f, s);
    }
    r((n = n.apply(l, e || [])).next());
  });
};
let Nt = [], xt = !1;
function Oa(l) {
  return Ma(this, arguments, void 0, function* (e, t = !0) {
    if (!(window.__gradio_mode__ === "website" || window.__gradio_mode__ !== "app" && t !== !0)) {
      if (Nt.push(e), !xt) xt = !0;
      else return;
      yield ga(), requestAnimationFrame(() => {
        let n = [0, 0];
        for (let i = 0; i < Nt.length; i++) {
          const a = Nt[i].getBoundingClientRect();
          (i === 0 || a.top + window.scrollY <= n[0]) && (n[0] = a.top + window.scrollY, n[1] = i);
        }
        window.scrollTo({ top: n[0] - 20, behavior: "smooth" }), xt = !1, Nt = [];
      });
    }
  });
}
function Ia(l, e, t) {
  let n, { $$slots: i = {}, $$scope: o } = e;
  this && this.__awaiter;
  const a = pa();
  let { i18n: f } = e, { eta: s = null } = e, { queue_position: r } = e, { queue_size: u } = e, { status: _ } = e, { scroll_to_output: b = !1 } = e, { timer: m = !0 } = e, { show_progress: S = "full" } = e, { message: p = null } = e, { progress: A = null } = e, { variant: D = "default" } = e, { loading_text: h = "Loading..." } = e, { absolute: w = !0 } = e, { translucent: y = !1 } = e, { border: O = !1 } = e, { autoscroll: g } = e, k, q = !1, ie = 0, oe = 0, I = null, W = null, ve = 0, K = null, ae, z = null, Se = !0;
  const pt = () => {
    t(0, s = t(27, I = t(19, P = null))), t(25, ie = performance.now()), t(26, oe = 0), q = !0, wt();
  };
  function wt() {
    requestAnimationFrame(() => {
      t(26, oe = (performance.now() - ie) / 1e3), q && wt();
    });
  }
  function it() {
    t(26, oe = 0), t(0, s = t(27, I = t(19, P = null))), q && (q = !1);
  }
  ba(() => {
    q && it();
  });
  let P = null;
  function Tt(T) {
    ol[T ? "unshift" : "push"](() => {
      z = T, t(16, z), t(7, A), t(14, K), t(15, ae);
    });
  }
  const U = () => {
    a("clear_status");
  };
  function Et(T) {
    ol[T ? "unshift" : "push"](() => {
      k = T, t(13, k);
    });
  }
  return l.$$set = (T) => {
    "i18n" in T && t(1, f = T.i18n), "eta" in T && t(0, s = T.eta), "queue_position" in T && t(2, r = T.queue_position), "queue_size" in T && t(3, u = T.queue_size), "status" in T && t(4, _ = T.status), "scroll_to_output" in T && t(22, b = T.scroll_to_output), "timer" in T && t(5, m = T.timer), "show_progress" in T && t(6, S = T.show_progress), "message" in T && t(23, p = T.message), "progress" in T && t(7, A = T.progress), "variant" in T && t(8, D = T.variant), "loading_text" in T && t(9, h = T.loading_text), "absolute" in T && t(10, w = T.absolute), "translucent" in T && t(11, y = T.translucent), "border" in T && t(12, O = T.border), "autoscroll" in T && t(24, g = T.autoscroll), "$$scope" in T && t(29, o = T.$$scope);
  }, l.$$.update = () => {
    l.$$.dirty[0] & /*eta, old_eta, timer_start, eta_from_start*/
    436207617 && (s === null && t(0, s = I), s != null && I !== s && (t(28, W = (performance.now() - ie) / 1e3 + s), t(19, P = W.toFixed(1)), t(27, I = s))), l.$$.dirty[0] & /*eta_from_start, timer_diff*/
    335544320 && t(17, ve = W === null || W <= 0 || !oe ? null : Math.min(oe / W, 1)), l.$$.dirty[0] & /*progress*/
    128 && A != null && t(18, Se = !1), l.$$.dirty[0] & /*progress, progress_level, progress_bar, last_progress_level*/
    114816 && (A != null ? t(14, K = A.map((T) => {
      if (T.index != null && T.length != null)
        return T.index / T.length;
      if (T.progress != null)
        return T.progress;
    })) : t(14, K = null), K ? (t(15, ae = K[K.length - 1]), z && (ae === 0 ? t(16, z.style.transition = "0", z) : t(16, z.style.transition = "150ms", z))) : t(15, ae = void 0)), l.$$.dirty[0] & /*status*/
    16 && (_ === "pending" ? pt() : it()), l.$$.dirty[0] & /*el, scroll_to_output, status, autoscroll*/
    20979728 && k && b && (_ === "pending" || _ === "complete") && Oa(k, g), l.$$.dirty[0] & /*status, message*/
    8388624, l.$$.dirty[0] & /*timer_diff*/
    67108864 && t(20, n = oe.toFixed(1));
  }, [
    s,
    f,
    r,
    u,
    _,
    m,
    S,
    A,
    D,
    h,
    w,
    y,
    O,
    k,
    K,
    ae,
    z,
    ve,
    Se,
    P,
    n,
    a,
    b,
    p,
    g,
    ie,
    oe,
    I,
    W,
    o,
    i,
    Tt,
    U,
    Et
  ];
}
class Pa extends ma {
  constructor(e) {
    super(), da(
      this,
      e,
      Ia,
      Na,
      ha,
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
  entries: Zl,
  setPrototypeOf: El,
  isFrozen: Fa,
  getPrototypeOf: Ua,
  getOwnPropertyDescriptor: za
} = Object;
let {
  freeze: j,
  seal: le,
  create: Kl
} = Object, {
  apply: gn,
  construct: bn
} = typeof Reflect < "u" && Reflect;
j || (j = function(e) {
  return e;
});
le || (le = function(e) {
  return e;
});
gn || (gn = function(e, t, n) {
  return e.apply(t, n);
});
bn || (bn = function(e, t) {
  return new e(...t);
});
const Mt = Q(Array.prototype.forEach), Al = Q(Array.prototype.pop), ct = Q(Array.prototype.push), Pt = Q(String.prototype.toLowerCase), $t = Q(String.prototype.toString), kl = Q(String.prototype.match), ut = Q(String.prototype.replace), Ha = Q(String.prototype.indexOf), Ba = Q(String.prototype.trim), _e = Q(Object.prototype.hasOwnProperty), Y = Q(RegExp.prototype.test), _t = qa(TypeError);
function Q(l) {
  return function(e) {
    for (var t = arguments.length, n = new Array(t > 1 ? t - 1 : 0), i = 1; i < t; i++)
      n[i - 1] = arguments[i];
    return gn(l, e, n);
  };
}
function qa(l) {
  return function() {
    for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
      t[n] = arguments[n];
    return bn(l, t);
  };
}
function R(l, e) {
  let t = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : Pt;
  El && El(l, null);
  let n = e.length;
  for (; n--; ) {
    let i = e[n];
    if (typeof i == "string") {
      const o = t(i);
      o !== i && (Fa(e) || (e[n] = o), i = o);
    }
    l[i] = !0;
  }
  return l;
}
function Ga(l) {
  for (let e = 0; e < l.length; e++)
    _e(l, e) || (l[e] = null);
  return l;
}
function Be(l) {
  const e = Kl(null);
  for (const [t, n] of Zl(l))
    _e(l, t) && (Array.isArray(n) ? e[t] = Ga(n) : n && typeof n == "object" && n.constructor === Object ? e[t] = Be(n) : e[t] = n);
  return e;
}
function mt(l, e) {
  for (; l !== null; ) {
    const n = za(l, e);
    if (n) {
      if (n.get)
        return Q(n.get);
      if (typeof n.value == "function")
        return Q(n.value);
    }
    l = Ua(l);
  }
  function t() {
    return null;
  }
  return t;
}
const vl = j(["a", "abbr", "acronym", "address", "area", "article", "aside", "audio", "b", "bdi", "bdo", "big", "blink", "blockquote", "body", "br", "button", "canvas", "caption", "center", "cite", "code", "col", "colgroup", "content", "data", "datalist", "dd", "decorator", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "element", "em", "fieldset", "figcaption", "figure", "font", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "i", "img", "input", "ins", "kbd", "label", "legend", "li", "main", "map", "mark", "marquee", "menu", "menuitem", "meter", "nav", "nobr", "ol", "optgroup", "option", "output", "p", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "section", "select", "shadow", "small", "source", "spacer", "span", "strike", "strong", "style", "sub", "summary", "sup", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "tr", "track", "tt", "u", "ul", "var", "video", "wbr"]), en = j(["svg", "a", "altglyph", "altglyphdef", "altglyphitem", "animatecolor", "animatemotion", "animatetransform", "circle", "clippath", "defs", "desc", "ellipse", "filter", "font", "g", "glyph", "glyphref", "hkern", "image", "line", "lineargradient", "marker", "mask", "metadata", "mpath", "path", "pattern", "polygon", "polyline", "radialgradient", "rect", "stop", "style", "switch", "symbol", "text", "textpath", "title", "tref", "tspan", "view", "vkern"]), tn = j(["feBlend", "feColorMatrix", "feComponentTransfer", "feComposite", "feConvolveMatrix", "feDiffuseLighting", "feDisplacementMap", "feDistantLight", "feDropShadow", "feFlood", "feFuncA", "feFuncB", "feFuncG", "feFuncR", "feGaussianBlur", "feImage", "feMerge", "feMergeNode", "feMorphology", "feOffset", "fePointLight", "feSpecularLighting", "feSpotLight", "feTile", "feTurbulence"]), Wa = j(["animate", "color-profile", "cursor", "discard", "font-face", "font-face-format", "font-face-name", "font-face-src", "font-face-uri", "foreignobject", "hatch", "hatchpath", "mesh", "meshgradient", "meshpatch", "meshrow", "missing-glyph", "script", "set", "solidcolor", "unknown", "use"]), nn = j(["math", "menclose", "merror", "mfenced", "mfrac", "mglyph", "mi", "mlabeledtr", "mmultiscripts", "mn", "mo", "mover", "mpadded", "mphantom", "mroot", "mrow", "ms", "mspace", "msqrt", "mstyle", "msub", "msup", "msubsup", "mtable", "mtd", "mtext", "mtr", "munder", "munderover", "mprescripts"]), Va = j(["maction", "maligngroup", "malignmark", "mlongdiv", "mscarries", "mscarry", "msgroup", "mstack", "msline", "msrow", "semantics", "annotation", "annotation-xml", "mprescripts", "none"]), Sl = j(["#text"]), yl = j(["accept", "action", "align", "alt", "autocapitalize", "autocomplete", "autopictureinpicture", "autoplay", "background", "bgcolor", "border", "capture", "cellpadding", "cellspacing", "checked", "cite", "class", "clear", "color", "cols", "colspan", "controls", "controlslist", "coords", "crossorigin", "datetime", "decoding", "default", "dir", "disabled", "disablepictureinpicture", "disableremoteplayback", "download", "draggable", "enctype", "enterkeyhint", "face", "for", "headers", "height", "hidden", "high", "href", "hreflang", "id", "inputmode", "integrity", "ismap", "kind", "label", "lang", "list", "loading", "loop", "low", "max", "maxlength", "media", "method", "min", "minlength", "multiple", "muted", "name", "nonce", "noshade", "novalidate", "nowrap", "open", "optimum", "pattern", "placeholder", "playsinline", "popover", "popovertarget", "popovertargetaction", "poster", "preload", "pubdate", "radiogroup", "readonly", "rel", "required", "rev", "reversed", "role", "rows", "rowspan", "spellcheck", "scope", "selected", "shape", "size", "sizes", "span", "srclang", "start", "src", "srcset", "step", "style", "summary", "tabindex", "title", "translate", "type", "usemap", "valign", "value", "width", "wrap", "xmlns", "slot"]), ln = j(["accent-height", "accumulate", "additive", "alignment-baseline", "ascent", "attributename", "attributetype", "azimuth", "basefrequency", "baseline-shift", "begin", "bias", "by", "class", "clip", "clippathunits", "clip-path", "clip-rule", "color", "color-interpolation", "color-interpolation-filters", "color-profile", "color-rendering", "cx", "cy", "d", "dx", "dy", "diffuseconstant", "direction", "display", "divisor", "dur", "edgemode", "elevation", "end", "fill", "fill-opacity", "fill-rule", "filter", "filterunits", "flood-color", "flood-opacity", "font-family", "font-size", "font-size-adjust", "font-stretch", "font-style", "font-variant", "font-weight", "fx", "fy", "g1", "g2", "glyph-name", "glyphref", "gradientunits", "gradienttransform", "height", "href", "id", "image-rendering", "in", "in2", "k", "k1", "k2", "k3", "k4", "kerning", "keypoints", "keysplines", "keytimes", "lang", "lengthadjust", "letter-spacing", "kernelmatrix", "kernelunitlength", "lighting-color", "local", "marker-end", "marker-mid", "marker-start", "markerheight", "markerunits", "markerwidth", "maskcontentunits", "maskunits", "max", "mask", "media", "method", "mode", "min", "name", "numoctaves", "offset", "operator", "opacity", "order", "orient", "orientation", "origin", "overflow", "paint-order", "path", "pathlength", "patterncontentunits", "patterntransform", "patternunits", "points", "preservealpha", "preserveaspectratio", "primitiveunits", "r", "rx", "ry", "radius", "refx", "refy", "repeatcount", "repeatdur", "restart", "result", "rotate", "scale", "seed", "shape-rendering", "specularconstant", "specularexponent", "spreadmethod", "startoffset", "stddeviation", "stitchtiles", "stop-color", "stop-opacity", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke", "stroke-width", "style", "surfacescale", "systemlanguage", "tabindex", "targetx", "targety", "transform", "transform-origin", "text-anchor", "text-decoration", "text-rendering", "textlength", "type", "u1", "u2", "unicode", "values", "viewbox", "visibility", "version", "vert-adv-y", "vert-origin-x", "vert-origin-y", "width", "word-spacing", "wrap", "writing-mode", "xchannelselector", "ychannelselector", "x", "x1", "x2", "xmlns", "y", "y1", "y2", "z", "zoomandpan"]), Cl = j(["accent", "accentunder", "align", "bevelled", "close", "columnsalign", "columnlines", "columnspan", "denomalign", "depth", "dir", "display", "displaystyle", "encoding", "fence", "frame", "height", "href", "id", "largeop", "length", "linethickness", "lspace", "lquote", "mathbackground", "mathcolor", "mathsize", "mathvariant", "maxsize", "minsize", "movablelimits", "notation", "numalign", "open", "rowalign", "rowlines", "rowspacing", "rowspan", "rspace", "rquote", "scriptlevel", "scriptminsize", "scriptsizemultiplier", "selection", "separator", "separators", "stretchy", "subscriptshift", "supscriptshift", "symmetric", "voffset", "width", "xmlns"]), Ot = j(["xlink:href", "xml:id", "xlink:title", "xml:space", "xmlns:xlink"]), Ya = le(/\{\{[\w\W]*|[\w\W]*\}\}/gm), ja = le(/<%[\w\W]*|[\w\W]*%>/gm), Xa = le(/\${[\w\W]*}/gm), Za = le(/^data-[\-\w.\u00B7-\uFFFF]/), Ka = le(/^aria-[\-\w]+$/), Jl = le(
  /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
  // eslint-disable-line no-useless-escape
), Ja = le(/^(?:\w+script|data):/i), Qa = le(
  /[\u0000-\u0020\u00A0\u1680\u180E\u2000-\u2029\u205F\u3000]/g
  // eslint-disable-line no-control-regex
), Ql = le(/^html$/i), xa = le(/^[a-z][.\w]*(-[.\w]+)+$/i);
var Ll = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  MUSTACHE_EXPR: Ya,
  ERB_EXPR: ja,
  TMPLIT_EXPR: Xa,
  DATA_ATTR: Za,
  ARIA_ATTR: Ka,
  IS_ALLOWED_URI: Jl,
  IS_SCRIPT_OR_DATA: Ja,
  ATTR_WHITESPACE: Qa,
  DOCTYPE_NAME: Ql,
  CUSTOM_ELEMENT: xa
});
const dt = {
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
}, $a = function() {
  return typeof window > "u" ? null : window;
}, es = function(e, t) {
  if (typeof e != "object" || typeof e.createPolicy != "function")
    return null;
  let n = null;
  const i = "data-tt-policy-suffix";
  t && t.hasAttribute(i) && (n = t.getAttribute(i));
  const o = "dompurify" + (n ? "#" + n : "");
  try {
    return e.createPolicy(o, {
      createHTML(a) {
        return a;
      },
      createScriptURL(a) {
        return a;
      }
    });
  } catch {
    return console.warn("TrustedTypes policy " + o + " could not be created."), null;
  }
};
function xl() {
  let l = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : $a();
  const e = (v) => xl(v);
  if (e.version = "3.1.6", e.removed = [], !l || !l.document || l.document.nodeType !== dt.document)
    return e.isSupported = !1, e;
  let {
    document: t
  } = l;
  const n = t, i = n.currentScript, {
    DocumentFragment: o,
    HTMLTemplateElement: a,
    Node: f,
    Element: s,
    NodeFilter: r,
    NamedNodeMap: u = l.NamedNodeMap || l.MozNamedAttrMap,
    HTMLFormElement: _,
    DOMParser: b,
    trustedTypes: m
  } = l, S = s.prototype, p = mt(S, "cloneNode"), A = mt(S, "remove"), D = mt(S, "nextSibling"), h = mt(S, "childNodes"), w = mt(S, "parentNode");
  if (typeof a == "function") {
    const v = t.createElement("template");
    v.content && v.content.ownerDocument && (t = v.content.ownerDocument);
  }
  let y, O = "";
  const {
    implementation: g,
    createNodeIterator: k,
    createDocumentFragment: q,
    getElementsByTagName: ie
  } = t, {
    importNode: oe
  } = n;
  let I = {};
  e.isSupported = typeof Zl == "function" && typeof w == "function" && g && g.createHTMLDocument !== void 0;
  const {
    MUSTACHE_EXPR: W,
    ERB_EXPR: ve,
    TMPLIT_EXPR: K,
    DATA_ATTR: ae,
    ARIA_ATTR: z,
    IS_SCRIPT_OR_DATA: Se,
    ATTR_WHITESPACE: pt,
    CUSTOM_ELEMENT: wt
  } = Ll;
  let {
    IS_ALLOWED_URI: it
  } = Ll, P = null;
  const Tt = R({}, [...vl, ...en, ...tn, ...nn, ...Sl]);
  let U = null;
  const Et = R({}, [...yl, ...ln, ...Cl, ...Ot]);
  let T = Object.seal(Kl(null, {
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
  })), Pe = null, ye = null, Fe = !0, ot = !0, Ce = !1, Ue = !0, Le = !1, at = !0, se = !1, re = !1, ze = !1, We = !1, At = !1, kt = !1, En = !0, An = !1;
  const ei = "user-content-";
  let Ut = !0, st = !1, Ve = {}, Ye = null;
  const kn = R({}, ["annotation-xml", "audio", "colgroup", "desc", "foreignobject", "head", "iframe", "math", "mi", "mn", "mo", "ms", "mtext", "noembed", "noframes", "noscript", "plaintext", "script", "style", "svg", "template", "thead", "title", "video", "xmp"]);
  let vn = null;
  const Sn = R({}, ["audio", "video", "img", "source", "image", "track"]);
  let zt = null;
  const yn = R({}, ["alt", "class", "for", "id", "label", "name", "pattern", "placeholder", "role", "summary", "title", "value", "style", "xmlns"]), vt = "http://www.w3.org/1998/Math/MathML", St = "http://www.w3.org/2000/svg", Ee = "http://www.w3.org/1999/xhtml";
  let je = Ee, Ht = !1, Bt = null;
  const ti = R({}, [vt, St, Ee], $t);
  let rt = null;
  const ni = ["application/xhtml+xml", "text/html"], li = "text/html";
  let H = null, Xe = null;
  const ii = t.createElement("form"), Cn = function(c) {
    return c instanceof RegExp || c instanceof Function;
  }, qt = function() {
    let c = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
    if (!(Xe && Xe === c)) {
      if ((!c || typeof c != "object") && (c = {}), c = Be(c), rt = // eslint-disable-next-line unicorn/prefer-includes
      ni.indexOf(c.PARSER_MEDIA_TYPE) === -1 ? li : c.PARSER_MEDIA_TYPE, H = rt === "application/xhtml+xml" ? $t : Pt, P = _e(c, "ALLOWED_TAGS") ? R({}, c.ALLOWED_TAGS, H) : Tt, U = _e(c, "ALLOWED_ATTR") ? R({}, c.ALLOWED_ATTR, H) : Et, Bt = _e(c, "ALLOWED_NAMESPACES") ? R({}, c.ALLOWED_NAMESPACES, $t) : ti, zt = _e(c, "ADD_URI_SAFE_ATTR") ? R(
        Be(yn),
        // eslint-disable-line indent
        c.ADD_URI_SAFE_ATTR,
        // eslint-disable-line indent
        H
        // eslint-disable-line indent
      ) : yn, vn = _e(c, "ADD_DATA_URI_TAGS") ? R(
        Be(Sn),
        // eslint-disable-line indent
        c.ADD_DATA_URI_TAGS,
        // eslint-disable-line indent
        H
        // eslint-disable-line indent
      ) : Sn, Ye = _e(c, "FORBID_CONTENTS") ? R({}, c.FORBID_CONTENTS, H) : kn, Pe = _e(c, "FORBID_TAGS") ? R({}, c.FORBID_TAGS, H) : {}, ye = _e(c, "FORBID_ATTR") ? R({}, c.FORBID_ATTR, H) : {}, Ve = _e(c, "USE_PROFILES") ? c.USE_PROFILES : !1, Fe = c.ALLOW_ARIA_ATTR !== !1, ot = c.ALLOW_DATA_ATTR !== !1, Ce = c.ALLOW_UNKNOWN_PROTOCOLS || !1, Ue = c.ALLOW_SELF_CLOSE_IN_ATTR !== !1, Le = c.SAFE_FOR_TEMPLATES || !1, at = c.SAFE_FOR_XML !== !1, se = c.WHOLE_DOCUMENT || !1, We = c.RETURN_DOM || !1, At = c.RETURN_DOM_FRAGMENT || !1, kt = c.RETURN_TRUSTED_TYPE || !1, ze = c.FORCE_BODY || !1, En = c.SANITIZE_DOM !== !1, An = c.SANITIZE_NAMED_PROPS || !1, Ut = c.KEEP_CONTENT !== !1, st = c.IN_PLACE || !1, it = c.ALLOWED_URI_REGEXP || Jl, je = c.NAMESPACE || Ee, T = c.CUSTOM_ELEMENT_HANDLING || {}, c.CUSTOM_ELEMENT_HANDLING && Cn(c.CUSTOM_ELEMENT_HANDLING.tagNameCheck) && (T.tagNameCheck = c.CUSTOM_ELEMENT_HANDLING.tagNameCheck), c.CUSTOM_ELEMENT_HANDLING && Cn(c.CUSTOM_ELEMENT_HANDLING.attributeNameCheck) && (T.attributeNameCheck = c.CUSTOM_ELEMENT_HANDLING.attributeNameCheck), c.CUSTOM_ELEMENT_HANDLING && typeof c.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements == "boolean" && (T.allowCustomizedBuiltInElements = c.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements), Le && (ot = !1), At && (We = !0), Ve && (P = R({}, Sl), U = [], Ve.html === !0 && (R(P, vl), R(U, yl)), Ve.svg === !0 && (R(P, en), R(U, ln), R(U, Ot)), Ve.svgFilters === !0 && (R(P, tn), R(U, ln), R(U, Ot)), Ve.mathMl === !0 && (R(P, nn), R(U, Cl), R(U, Ot))), c.ADD_TAGS && (P === Tt && (P = Be(P)), R(P, c.ADD_TAGS, H)), c.ADD_ATTR && (U === Et && (U = Be(U)), R(U, c.ADD_ATTR, H)), c.ADD_URI_SAFE_ATTR && R(zt, c.ADD_URI_SAFE_ATTR, H), c.FORBID_CONTENTS && (Ye === kn && (Ye = Be(Ye)), R(Ye, c.FORBID_CONTENTS, H)), Ut && (P["#text"] = !0), se && R(P, ["html", "head", "body"]), P.table && (R(P, ["tbody"]), delete Pe.tbody), c.TRUSTED_TYPES_POLICY) {
        if (typeof c.TRUSTED_TYPES_POLICY.createHTML != "function")
          throw _t('TRUSTED_TYPES_POLICY configuration option must provide a "createHTML" hook.');
        if (typeof c.TRUSTED_TYPES_POLICY.createScriptURL != "function")
          throw _t('TRUSTED_TYPES_POLICY configuration option must provide a "createScriptURL" hook.');
        y = c.TRUSTED_TYPES_POLICY, O = y.createHTML("");
      } else
        y === void 0 && (y = es(m, i)), y !== null && typeof O == "string" && (O = y.createHTML(""));
      j && j(c), Xe = c;
    }
  }, Ln = R({}, ["mi", "mo", "mn", "ms", "mtext"]), Rn = R({}, ["foreignobject", "annotation-xml"]), oi = R({}, ["title", "style", "font", "a", "script"]), Dn = R({}, [...en, ...tn, ...Wa]), Nn = R({}, [...nn, ...Va]), ai = function(c) {
    let d = w(c);
    (!d || !d.tagName) && (d = {
      namespaceURI: je,
      tagName: "template"
    });
    const E = Pt(c.tagName), M = Pt(d.tagName);
    return Bt[c.namespaceURI] ? c.namespaceURI === St ? d.namespaceURI === Ee ? E === "svg" : d.namespaceURI === vt ? E === "svg" && (M === "annotation-xml" || Ln[M]) : !!Dn[E] : c.namespaceURI === vt ? d.namespaceURI === Ee ? E === "math" : d.namespaceURI === St ? E === "math" && Rn[M] : !!Nn[E] : c.namespaceURI === Ee ? d.namespaceURI === St && !Rn[M] || d.namespaceURI === vt && !Ln[M] ? !1 : !Nn[E] && (oi[E] || !Dn[E]) : !!(rt === "application/xhtml+xml" && Bt[c.namespaceURI]) : !1;
  }, he = function(c) {
    ct(e.removed, {
      element: c
    });
    try {
      w(c).removeChild(c);
    } catch {
      A(c);
    }
  }, yt = function(c, d) {
    try {
      ct(e.removed, {
        attribute: d.getAttributeNode(c),
        from: d
      });
    } catch {
      ct(e.removed, {
        attribute: null,
        from: d
      });
    }
    if (d.removeAttribute(c), c === "is" && !U[c])
      if (We || At)
        try {
          he(d);
        } catch {
        }
      else
        try {
          d.setAttribute(c, "");
        } catch {
        }
  }, Mn = function(c) {
    let d = null, E = null;
    if (ze)
      c = "<remove></remove>" + c;
    else {
      const B = kl(c, /^[\r\n\t ]+/);
      E = B && B[0];
    }
    rt === "application/xhtml+xml" && je === Ee && (c = '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>' + c + "</body></html>");
    const M = y ? y.createHTML(c) : c;
    if (je === Ee)
      try {
        d = new b().parseFromString(M, rt);
      } catch {
      }
    if (!d || !d.documentElement) {
      d = g.createDocument(je, "template", null);
      try {
        d.documentElement.innerHTML = Ht ? O : M;
      } catch {
      }
    }
    const G = d.body || d.documentElement;
    return c && E && G.insertBefore(t.createTextNode(E), G.childNodes[0] || null), je === Ee ? ie.call(d, se ? "html" : "body")[0] : se ? d.documentElement : G;
  }, On = function(c) {
    return k.call(
      c.ownerDocument || c,
      c,
      // eslint-disable-next-line no-bitwise
      r.SHOW_ELEMENT | r.SHOW_COMMENT | r.SHOW_TEXT | r.SHOW_PROCESSING_INSTRUCTION | r.SHOW_CDATA_SECTION,
      null
    );
  }, In = function(c) {
    return c instanceof _ && (typeof c.nodeName != "string" || typeof c.textContent != "string" || typeof c.removeChild != "function" || !(c.attributes instanceof u) || typeof c.removeAttribute != "function" || typeof c.setAttribute != "function" || typeof c.namespaceURI != "string" || typeof c.insertBefore != "function" || typeof c.hasChildNodes != "function");
  }, Pn = function(c) {
    return typeof f == "function" && c instanceof f;
  }, Ae = function(c, d, E) {
    I[c] && Mt(I[c], (M) => {
      M.call(e, d, E, Xe);
    });
  }, Fn = function(c) {
    let d = null;
    if (Ae("beforeSanitizeElements", c, null), In(c))
      return he(c), !0;
    const E = H(c.nodeName);
    if (Ae("uponSanitizeElement", c, {
      tagName: E,
      allowedTags: P
    }), c.hasChildNodes() && !Pn(c.firstElementChild) && Y(/<[/\w]/g, c.innerHTML) && Y(/<[/\w]/g, c.textContent) || c.nodeType === dt.progressingInstruction || at && c.nodeType === dt.comment && Y(/<[/\w]/g, c.data))
      return he(c), !0;
    if (!P[E] || Pe[E]) {
      if (!Pe[E] && zn(E) && (T.tagNameCheck instanceof RegExp && Y(T.tagNameCheck, E) || T.tagNameCheck instanceof Function && T.tagNameCheck(E)))
        return !1;
      if (Ut && !Ye[E]) {
        const M = w(c) || c.parentNode, G = h(c) || c.childNodes;
        if (G && M) {
          const B = G.length;
          for (let X = B - 1; X >= 0; --X) {
            const ge = p(G[X], !0);
            ge.__removalCount = (c.__removalCount || 0) + 1, M.insertBefore(ge, D(c));
          }
        }
      }
      return he(c), !0;
    }
    return c instanceof s && !ai(c) || (E === "noscript" || E === "noembed" || E === "noframes") && Y(/<\/no(script|embed|frames)/i, c.innerHTML) ? (he(c), !0) : (Le && c.nodeType === dt.text && (d = c.textContent, Mt([W, ve, K], (M) => {
      d = ut(d, M, " ");
    }), c.textContent !== d && (ct(e.removed, {
      element: c.cloneNode()
    }), c.textContent = d)), Ae("afterSanitizeElements", c, null), !1);
  }, Un = function(c, d, E) {
    if (En && (d === "id" || d === "name") && (E in t || E in ii))
      return !1;
    if (!(ot && !ye[d] && Y(ae, d))) {
      if (!(Fe && Y(z, d))) {
        if (!U[d] || ye[d]) {
          if (
            // First condition does a very basic check if a) it's basically a valid custom element tagname AND
            // b) if the tagName passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
            // and c) if the attribute name passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.attributeNameCheck
            !(zn(c) && (T.tagNameCheck instanceof RegExp && Y(T.tagNameCheck, c) || T.tagNameCheck instanceof Function && T.tagNameCheck(c)) && (T.attributeNameCheck instanceof RegExp && Y(T.attributeNameCheck, d) || T.attributeNameCheck instanceof Function && T.attributeNameCheck(d)) || // Alternative, second condition checks if it's an `is`-attribute, AND
            // the value passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
            d === "is" && T.allowCustomizedBuiltInElements && (T.tagNameCheck instanceof RegExp && Y(T.tagNameCheck, E) || T.tagNameCheck instanceof Function && T.tagNameCheck(E)))
          ) return !1;
        } else if (!zt[d]) {
          if (!Y(it, ut(E, pt, ""))) {
            if (!((d === "src" || d === "xlink:href" || d === "href") && c !== "script" && Ha(E, "data:") === 0 && vn[c])) {
              if (!(Ce && !Y(Se, ut(E, pt, "")))) {
                if (E)
                  return !1;
              }
            }
          }
        }
      }
    }
    return !0;
  }, zn = function(c) {
    return c !== "annotation-xml" && kl(c, wt);
  }, Hn = function(c) {
    Ae("beforeSanitizeAttributes", c, null);
    const {
      attributes: d
    } = c;
    if (!d)
      return;
    const E = {
      attrName: "",
      attrValue: "",
      keepAttr: !0,
      allowedAttributes: U
    };
    let M = d.length;
    for (; M--; ) {
      const G = d[M], {
        name: B,
        namespaceURI: X,
        value: ge
      } = G, ft = H(B);
      let V = B === "value" ? ge : Ba(ge);
      if (E.attrName = ft, E.attrValue = V, E.keepAttr = !0, E.forceKeepAttr = void 0, Ae("uponSanitizeAttribute", c, E), V = E.attrValue, at && Y(/((--!?|])>)|<\/(style|title)/i, V)) {
        yt(B, c);
        continue;
      }
      if (E.forceKeepAttr || (yt(B, c), !E.keepAttr))
        continue;
      if (!Ue && Y(/\/>/i, V)) {
        yt(B, c);
        continue;
      }
      Le && Mt([W, ve, K], (qn) => {
        V = ut(V, qn, " ");
      });
      const Bn = H(c.nodeName);
      if (Un(Bn, ft, V)) {
        if (An && (ft === "id" || ft === "name") && (yt(B, c), V = ei + V), y && typeof m == "object" && typeof m.getAttributeType == "function" && !X)
          switch (m.getAttributeType(Bn, ft)) {
            case "TrustedHTML": {
              V = y.createHTML(V);
              break;
            }
            case "TrustedScriptURL": {
              V = y.createScriptURL(V);
              break;
            }
          }
        try {
          X ? c.setAttributeNS(X, B, V) : c.setAttribute(B, V), In(c) ? he(c) : Al(e.removed);
        } catch {
        }
      }
    }
    Ae("afterSanitizeAttributes", c, null);
  }, si = function v(c) {
    let d = null;
    const E = On(c);
    for (Ae("beforeSanitizeShadowDOM", c, null); d = E.nextNode(); )
      Ae("uponSanitizeShadowNode", d, null), !Fn(d) && (d.content instanceof o && v(d.content), Hn(d));
    Ae("afterSanitizeShadowDOM", c, null);
  };
  return e.sanitize = function(v) {
    let c = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, d = null, E = null, M = null, G = null;
    if (Ht = !v, Ht && (v = "<!-->"), typeof v != "string" && !Pn(v))
      if (typeof v.toString == "function") {
        if (v = v.toString(), typeof v != "string")
          throw _t("dirty is not a string, aborting");
      } else
        throw _t("toString is not a function");
    if (!e.isSupported)
      return v;
    if (re || qt(c), e.removed = [], typeof v == "string" && (st = !1), st) {
      if (v.nodeName) {
        const ge = H(v.nodeName);
        if (!P[ge] || Pe[ge])
          throw _t("root node is forbidden and cannot be sanitized in-place");
      }
    } else if (v instanceof f)
      d = Mn("<!---->"), E = d.ownerDocument.importNode(v, !0), E.nodeType === dt.element && E.nodeName === "BODY" || E.nodeName === "HTML" ? d = E : d.appendChild(E);
    else {
      if (!We && !Le && !se && // eslint-disable-next-line unicorn/prefer-includes
      v.indexOf("<") === -1)
        return y && kt ? y.createHTML(v) : v;
      if (d = Mn(v), !d)
        return We ? null : kt ? O : "";
    }
    d && ze && he(d.firstChild);
    const B = On(st ? v : d);
    for (; M = B.nextNode(); )
      Fn(M) || (M.content instanceof o && si(M.content), Hn(M));
    if (st)
      return v;
    if (We) {
      if (At)
        for (G = q.call(d.ownerDocument); d.firstChild; )
          G.appendChild(d.firstChild);
      else
        G = d;
      return (U.shadowroot || U.shadowrootmode) && (G = oe.call(n, G, !0)), G;
    }
    let X = se ? d.outerHTML : d.innerHTML;
    return se && P["!doctype"] && d.ownerDocument && d.ownerDocument.doctype && d.ownerDocument.doctype.name && Y(Ql, d.ownerDocument.doctype.name) && (X = "<!DOCTYPE " + d.ownerDocument.doctype.name + `>
` + X), Le && Mt([W, ve, K], (ge) => {
      X = ut(X, ge, " ");
    }), y && kt ? y.createHTML(X) : X;
  }, e.setConfig = function() {
    let v = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
    qt(v), re = !0;
  }, e.clearConfig = function() {
    Xe = null, re = !1;
  }, e.isValidAttribute = function(v, c, d) {
    Xe || qt({});
    const E = H(v), M = H(c);
    return Un(E, M, d);
  }, e.addHook = function(v, c) {
    typeof c == "function" && (I[v] = I[v] || [], ct(I[v], c));
  }, e.removeHook = function(v) {
    if (I[v])
      return Al(I[v]);
  }, e.removeHooks = function(v) {
    I[v] && (I[v] = []);
  }, e.removeAllHooks = function() {
    I = {};
  }, e;
}
xl();
const {
  SvelteComponent: ts,
  append: ns,
  attr: ls,
  detach: is,
  element: os,
  init: as,
  insert: ss,
  noop: Rl,
  safe_not_equal: rs,
  set_data: fs,
  text: cs,
  toggle_class: Qe
} = window.__gradio__svelte__internal;
function us(l) {
  let e, t = (
    /*value*/
    (l[0] ? (
      /*value*/
      l[0]
    ) : "") + ""
  ), n;
  return {
    c() {
      e = os("div"), n = cs(t), ls(e, "class", "svelte-1gecy8w"), Qe(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), Qe(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), Qe(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    m(i, o) {
      ss(i, e, o), ns(e, n);
    },
    p(i, [o]) {
      o & /*value*/
      1 && t !== (t = /*value*/
      (i[0] ? (
        /*value*/
        i[0]
      ) : "") + "") && fs(n, t), o & /*type*/
      2 && Qe(
        e,
        "table",
        /*type*/
        i[1] === "table"
      ), o & /*type*/
      2 && Qe(
        e,
        "gallery",
        /*type*/
        i[1] === "gallery"
      ), o & /*selected*/
      4 && Qe(
        e,
        "selected",
        /*selected*/
        i[2]
      );
    },
    i: Rl,
    o: Rl,
    d(i) {
      i && is(e);
    }
  };
}
function _s(l, e, t) {
  let { value: n } = e, { type: i } = e, { selected: o = !1 } = e;
  return l.$$set = (a) => {
    "value" in a && t(0, n = a.value), "type" in a && t(1, i = a.type), "selected" in a && t(2, o = a.selected);
  }, [n, i, o];
}
class Ls extends ts {
  constructor(e) {
    super(), as(this, e, _s, us, rs, { value: 0, type: 1, selected: 2 });
  }
}
const {
  SvelteComponent: ms,
  assign: ds,
  check_outros: hs,
  create_component: et,
  destroy_component: tt,
  detach: pn,
  empty: gs,
  get_spread_object: bs,
  get_spread_update: ps,
  group_outros: ws,
  init: Ts,
  insert: wn,
  mount_component: nt,
  safe_not_equal: Es,
  space: $l,
  transition_in: Oe,
  transition_out: Ie
} = window.__gradio__svelte__internal;
function As(l) {
  let e, t, n, i;
  return e = new Ml({
    props: {
      show_label: (
        /*show_label*/
        l[6]
      ),
      Icon: Tn,
      label: (
        /*label*/
        l[5] || "3D Model"
      )
    }
  }), n = new go({
    props: {
      unpadded_box: !0,
      size: "large",
      $$slots: { default: [vs] },
      $$scope: { ctx: l }
    }
  }), {
    c() {
      et(e.$$.fragment), t = $l(), et(n.$$.fragment);
    },
    m(o, a) {
      nt(e, o, a), wn(o, t, a), nt(n, o, a), i = !0;
    },
    p(o, a) {
      const f = {};
      a & /*show_label*/
      64 && (f.show_label = /*show_label*/
      o[6]), a & /*label*/
      32 && (f.label = /*label*/
      o[5] || "3D Model"), e.$set(f);
      const s = {};
      a & /*$$scope*/
      1048576 && (s.$$scope = { dirty: a, ctx: o }), n.$set(s);
    },
    i(o) {
      i || (Oe(e.$$.fragment, o), Oe(n.$$.fragment, o), i = !0);
    },
    o(o) {
      Ie(e.$$.fragment, o), Ie(n.$$.fragment, o), i = !1;
    },
    d(o) {
      o && pn(t), tt(e, o), tt(n, o);
    }
  };
}
function ks(l) {
  let e, t;
  return e = new $o({
    props: {
      value: (
        /*value*/
        l[3]
      ),
      i18n: (
        /*gradio*/
        l[10].i18n
      ),
      label: (
        /*label*/
        l[5]
      ),
      show_label: (
        /*show_label*/
        l[6]
      ),
      camera_width: (
        /*camera_width*/
        l[13]
      ),
      camera_height: (
        /*camera_height*/
        l[14]
      ),
      camera_fx: (
        /*camera_fx*/
        l[15]
      ),
      camera_fy: (
        /*camera_fy*/
        l[16]
      ),
      camera_near: (
        /*camera_near*/
        l[17]
      ),
      camera_far: (
        /*camera_far*/
        l[18]
      )
    }
  }), {
    c() {
      et(e.$$.fragment);
    },
    m(n, i) {
      nt(e, n, i), t = !0;
    },
    p(n, i) {
      const o = {};
      i & /*value*/
      8 && (o.value = /*value*/
      n[3]), i & /*gradio*/
      1024 && (o.i18n = /*gradio*/
      n[10].i18n), i & /*label*/
      32 && (o.label = /*label*/
      n[5]), i & /*show_label*/
      64 && (o.show_label = /*show_label*/
      n[6]), i & /*camera_width*/
      8192 && (o.camera_width = /*camera_width*/
      n[13]), i & /*camera_height*/
      16384 && (o.camera_height = /*camera_height*/
      n[14]), i & /*camera_fx*/
      32768 && (o.camera_fx = /*camera_fx*/
      n[15]), i & /*camera_fy*/
      65536 && (o.camera_fy = /*camera_fy*/
      n[16]), i & /*camera_near*/
      131072 && (o.camera_near = /*camera_near*/
      n[17]), i & /*camera_far*/
      262144 && (o.camera_far = /*camera_far*/
      n[18]), e.$set(o);
    },
    i(n) {
      t || (Oe(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Ie(e.$$.fragment, n), t = !1;
    },
    d(n) {
      tt(e, n);
    }
  };
}
function vs(l) {
  let e, t;
  return e = new Tn({}), {
    c() {
      et(e.$$.fragment);
    },
    m(n, i) {
      nt(e, n, i), t = !0;
    },
    i(n) {
      t || (Oe(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Ie(e.$$.fragment, n), t = !1;
    },
    d(n) {
      tt(e, n);
    }
  };
}
function Ss(l) {
  let e, t, n, i, o, a;
  const f = [
    {
      autoscroll: (
        /*gradio*/
        l[10].autoscroll
      )
    },
    { i18n: (
      /*gradio*/
      l[10].i18n
    ) },
    /*loading_status*/
    l[4]
  ];
  let s = {};
  for (let b = 0; b < f.length; b += 1)
    s = ds(s, f[b]);
  e = new Pa({ props: s }), e.$on(
    "clear_status",
    /*clear_status_handler*/
    l[19]
  );
  const r = [ks, As], u = [];
  function _(b, m) {
    return (
      /*value*/
      b[3] ? 0 : 1
    );
  }
  return n = _(l), i = u[n] = r[n](l), {
    c() {
      et(e.$$.fragment), t = $l(), i.c(), o = gs();
    },
    m(b, m) {
      nt(e, b, m), wn(b, t, m), u[n].m(b, m), wn(b, o, m), a = !0;
    },
    p(b, m) {
      const S = m & /*gradio, loading_status*/
      1040 ? ps(f, [
        m & /*gradio*/
        1024 && {
          autoscroll: (
            /*gradio*/
            b[10].autoscroll
          )
        },
        m & /*gradio*/
        1024 && { i18n: (
          /*gradio*/
          b[10].i18n
        ) },
        m & /*loading_status*/
        16 && bs(
          /*loading_status*/
          b[4]
        )
      ]) : {};
      e.$set(S);
      let p = n;
      n = _(b), n === p ? u[n].p(b, m) : (ws(), Ie(u[p], 1, 1, () => {
        u[p] = null;
      }), hs(), i = u[n], i ? i.p(b, m) : (i = u[n] = r[n](b), i.c()), Oe(i, 1), i.m(o.parentNode, o));
    },
    i(b) {
      a || (Oe(e.$$.fragment, b), Oe(i), a = !0);
    },
    o(b) {
      Ie(e.$$.fragment, b), Ie(i), a = !1;
    },
    d(b) {
      b && (pn(t), pn(o)), tt(e, b), u[n].d(b);
    }
  };
}
function ys(l) {
  let e, t;
  return e = new ki({
    props: {
      visible: (
        /*visible*/
        l[2]
      ),
      variant: (
        /*value*/
        l[3] === null ? "dashed" : "solid"
      ),
      border_mode: "base",
      padding: !1,
      elem_id: (
        /*elem_id*/
        l[0]
      ),
      elem_classes: (
        /*elem_classes*/
        l[1]
      ),
      container: (
        /*container*/
        l[7]
      ),
      scale: (
        /*scale*/
        l[8]
      ),
      min_width: (
        /*min_width*/
        l[9]
      ),
      height: (
        /*height*/
        l[11]
      ),
      width: (
        /*width*/
        l[12]
      ),
      $$slots: { default: [Ss] },
      $$scope: { ctx: l }
    }
  }), {
    c() {
      et(e.$$.fragment);
    },
    m(n, i) {
      nt(e, n, i), t = !0;
    },
    p(n, [i]) {
      const o = {};
      i & /*visible*/
      4 && (o.visible = /*visible*/
      n[2]), i & /*value*/
      8 && (o.variant = /*value*/
      n[3] === null ? "dashed" : "solid"), i & /*elem_id*/
      1 && (o.elem_id = /*elem_id*/
      n[0]), i & /*elem_classes*/
      2 && (o.elem_classes = /*elem_classes*/
      n[1]), i & /*container*/
      128 && (o.container = /*container*/
      n[7]), i & /*scale*/
      256 && (o.scale = /*scale*/
      n[8]), i & /*min_width*/
      512 && (o.min_width = /*min_width*/
      n[9]), i & /*height*/
      2048 && (o.height = /*height*/
      n[11]), i & /*width*/
      4096 && (o.width = /*width*/
      n[12]), i & /*$$scope, value, gradio, label, show_label, camera_width, camera_height, camera_fx, camera_fy, camera_near, camera_far, loading_status*/
      1565816 && (o.$$scope = { dirty: i, ctx: n }), e.$set(o);
    },
    i(n) {
      t || (Oe(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Ie(e.$$.fragment, n), t = !1;
    },
    d(n) {
      tt(e, n);
    }
  };
}
function Cs(l, e, t) {
  let { elem_id: n = "" } = e, { elem_classes: i = [] } = e, { visible: o = !0 } = e, { value: a = null } = e, { loading_status: f } = e, { label: s } = e, { show_label: r } = e, { container: u = !0 } = e, { scale: _ = null } = e, { min_width: b = void 0 } = e, { gradio: m } = e, { height: S = void 0 } = e, { width: p = void 0 } = e, { camera_width: A = null } = e, { camera_height: D = null } = e, { camera_fx: h = null } = e, { camera_fy: w = null } = e, { camera_near: y = null } = e, { camera_far: O = null } = e;
  const g = () => m.dispatch("clear_status", f);
  return l.$$set = (k) => {
    "elem_id" in k && t(0, n = k.elem_id), "elem_classes" in k && t(1, i = k.elem_classes), "visible" in k && t(2, o = k.visible), "value" in k && t(3, a = k.value), "loading_status" in k && t(4, f = k.loading_status), "label" in k && t(5, s = k.label), "show_label" in k && t(6, r = k.show_label), "container" in k && t(7, u = k.container), "scale" in k && t(8, _ = k.scale), "min_width" in k && t(9, b = k.min_width), "gradio" in k && t(10, m = k.gradio), "height" in k && t(11, S = k.height), "width" in k && t(12, p = k.width), "camera_width" in k && t(13, A = k.camera_width), "camera_height" in k && t(14, D = k.camera_height), "camera_fx" in k && t(15, h = k.camera_fx), "camera_fy" in k && t(16, w = k.camera_fy), "camera_near" in k && t(17, y = k.camera_near), "camera_far" in k && t(18, O = k.camera_far);
  }, [
    n,
    i,
    o,
    a,
    f,
    s,
    r,
    u,
    _,
    b,
    m,
    S,
    p,
    A,
    D,
    h,
    w,
    y,
    O,
    g
  ];
}
class Rs extends ms {
  constructor(e) {
    super(), Ts(this, e, Cs, ys, Es, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      value: 3,
      loading_status: 4,
      label: 5,
      show_label: 6,
      container: 7,
      scale: 8,
      min_width: 9,
      gradio: 10,
      height: 11,
      width: 12,
      camera_width: 13,
      camera_height: 14,
      camera_fx: 15,
      camera_fy: 16,
      camera_near: 17,
      camera_far: 18
    });
  }
}
export {
  Ls as BaseExample,
  $o as BaseModel3DGSCamera,
  Rs as default
};
