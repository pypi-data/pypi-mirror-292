const {
  SvelteComponent: Zl,
  assign: Xl,
  create_slot: Kl,
  detach: Jl,
  element: Ql,
  get_all_dirty_from_scope: xl,
  get_slot_changes: $l,
  get_spread_update: ei,
  init: ti,
  insert: ni,
  safe_not_equal: li,
  set_dynamic_element_data: Mn,
  set_style: le,
  toggle_class: Ee,
  transition_in: wl,
  transition_out: Tl,
  update_slot_base: ii
} = window.__gradio__svelte__internal;
function oi(n) {
  let e, t, l;
  const i = (
    /*#slots*/
    n[18].default
  ), o = Kl(
    i,
    n,
    /*$$scope*/
    n[17],
    null
  );
  let s = [
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
  ], c = {};
  for (let a = 0; a < s.length; a += 1)
    c = Xl(c, s[a]);
  return {
    c() {
      e = Ql(
        /*tag*/
        n[14]
      ), o && o.c(), Mn(
        /*tag*/
        n[14]
      )(e, c), Ee(
        e,
        "hidden",
        /*visible*/
        n[10] === !1
      ), Ee(
        e,
        "padded",
        /*padding*/
        n[6]
      ), Ee(
        e,
        "border_focus",
        /*border_mode*/
        n[5] === "focus"
      ), Ee(
        e,
        "border_contrast",
        /*border_mode*/
        n[5] === "contrast"
      ), Ee(e, "hide-container", !/*explicit_call*/
      n[8] && !/*container*/
      n[9]), le(
        e,
        "height",
        /*get_dimension*/
        n[15](
          /*height*/
          n[0]
        )
      ), le(e, "width", typeof /*width*/
      n[1] == "number" ? `calc(min(${/*width*/
      n[1]}px, 100%))` : (
        /*get_dimension*/
        n[15](
          /*width*/
          n[1]
        )
      )), le(
        e,
        "border-style",
        /*variant*/
        n[4]
      ), le(
        e,
        "overflow",
        /*allow_overflow*/
        n[11] ? "visible" : "hidden"
      ), le(
        e,
        "flex-grow",
        /*scale*/
        n[12]
      ), le(e, "min-width", `calc(min(${/*min_width*/
      n[13]}px, 100%))`), le(e, "border-width", "var(--block-border-width)");
    },
    m(a, r) {
      ni(a, e, r), o && o.m(e, null), l = !0;
    },
    p(a, r) {
      o && o.p && (!l || r & /*$$scope*/
      131072) && ii(
        o,
        i,
        a,
        /*$$scope*/
        a[17],
        l ? $l(
          i,
          /*$$scope*/
          a[17],
          r,
          null
        ) : xl(
          /*$$scope*/
          a[17]
        ),
        null
      ), Mn(
        /*tag*/
        a[14]
      )(e, c = ei(s, [
        (!l || r & /*test_id*/
        128) && { "data-testid": (
          /*test_id*/
          a[7]
        ) },
        (!l || r & /*elem_id*/
        4) && { id: (
          /*elem_id*/
          a[2]
        ) },
        (!l || r & /*elem_classes*/
        8 && t !== (t = "block " + /*elem_classes*/
        a[3].join(" ") + " svelte-nl1om8")) && { class: t }
      ])), Ee(
        e,
        "hidden",
        /*visible*/
        a[10] === !1
      ), Ee(
        e,
        "padded",
        /*padding*/
        a[6]
      ), Ee(
        e,
        "border_focus",
        /*border_mode*/
        a[5] === "focus"
      ), Ee(
        e,
        "border_contrast",
        /*border_mode*/
        a[5] === "contrast"
      ), Ee(e, "hide-container", !/*explicit_call*/
      a[8] && !/*container*/
      a[9]), r & /*height*/
      1 && le(
        e,
        "height",
        /*get_dimension*/
        a[15](
          /*height*/
          a[0]
        )
      ), r & /*width*/
      2 && le(e, "width", typeof /*width*/
      a[1] == "number" ? `calc(min(${/*width*/
      a[1]}px, 100%))` : (
        /*get_dimension*/
        a[15](
          /*width*/
          a[1]
        )
      )), r & /*variant*/
      16 && le(
        e,
        "border-style",
        /*variant*/
        a[4]
      ), r & /*allow_overflow*/
      2048 && le(
        e,
        "overflow",
        /*allow_overflow*/
        a[11] ? "visible" : "hidden"
      ), r & /*scale*/
      4096 && le(
        e,
        "flex-grow",
        /*scale*/
        a[12]
      ), r & /*min_width*/
      8192 && le(e, "min-width", `calc(min(${/*min_width*/
      a[13]}px, 100%))`);
    },
    i(a) {
      l || (wl(o, a), l = !0);
    },
    o(a) {
      Tl(o, a), l = !1;
    },
    d(a) {
      a && Jl(e), o && o.d(a);
    }
  };
}
function si(n) {
  let e, t = (
    /*tag*/
    n[14] && oi(n)
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
      e || (wl(t, l), e = !0);
    },
    o(l) {
      Tl(t, l), e = !1;
    },
    d(l) {
      t && t.d(l);
    }
  };
}
function ai(n, e, t) {
  let { $$slots: l = {}, $$scope: i } = e, { height: o = void 0 } = e, { width: s = void 0 } = e, { elem_id: c = "" } = e, { elem_classes: a = [] } = e, { variant: r = "solid" } = e, { border_mode: u = "base" } = e, { padding: d = !0 } = e, { type: w = "normal" } = e, { test_id: b = void 0 } = e, { explicit_call: y = !1 } = e, { container: N = !0 } = e, { visible: C = !0 } = e, { allow_overflow: z = !0 } = e, { scale: h = null } = e, { min_width: p = 0 } = e, E = w === "fieldset" ? "fieldset" : "div";
  const P = (A) => {
    if (A !== void 0) {
      if (typeof A == "number")
        return A + "px";
      if (typeof A == "string")
        return A;
    }
  };
  return n.$$set = (A) => {
    "height" in A && t(0, o = A.height), "width" in A && t(1, s = A.width), "elem_id" in A && t(2, c = A.elem_id), "elem_classes" in A && t(3, a = A.elem_classes), "variant" in A && t(4, r = A.variant), "border_mode" in A && t(5, u = A.border_mode), "padding" in A && t(6, d = A.padding), "type" in A && t(16, w = A.type), "test_id" in A && t(7, b = A.test_id), "explicit_call" in A && t(8, y = A.explicit_call), "container" in A && t(9, N = A.container), "visible" in A && t(10, C = A.visible), "allow_overflow" in A && t(11, z = A.allow_overflow), "scale" in A && t(12, h = A.scale), "min_width" in A && t(13, p = A.min_width), "$$scope" in A && t(17, i = A.$$scope);
  }, [
    o,
    s,
    c,
    a,
    r,
    u,
    d,
    b,
    y,
    N,
    C,
    z,
    h,
    p,
    E,
    P,
    w,
    i,
    l
  ];
}
class ri extends Zl {
  constructor(e) {
    super(), ti(this, e, ai, si, li, {
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
  SvelteComponent: fi,
  attr: ci,
  create_slot: ui,
  detach: _i,
  element: di,
  get_all_dirty_from_scope: mi,
  get_slot_changes: pi,
  init: hi,
  insert: gi,
  safe_not_equal: bi,
  transition_in: wi,
  transition_out: Ti,
  update_slot_base: Ei
} = window.__gradio__svelte__internal;
function yi(n) {
  let e, t;
  const l = (
    /*#slots*/
    n[1].default
  ), i = ui(
    l,
    n,
    /*$$scope*/
    n[0],
    null
  );
  return {
    c() {
      e = di("div"), i && i.c(), ci(e, "class", "svelte-1hnfib2");
    },
    m(o, s) {
      gi(o, e, s), i && i.m(e, null), t = !0;
    },
    p(o, [s]) {
      i && i.p && (!t || s & /*$$scope*/
      1) && Ei(
        i,
        l,
        o,
        /*$$scope*/
        o[0],
        t ? pi(
          l,
          /*$$scope*/
          o[0],
          s,
          null
        ) : mi(
          /*$$scope*/
          o[0]
        ),
        null
      );
    },
    i(o) {
      t || (wi(i, o), t = !0);
    },
    o(o) {
      Ti(i, o), t = !1;
    },
    d(o) {
      o && _i(e), i && i.d(o);
    }
  };
}
function Ai(n, e, t) {
  let { $$slots: l = {}, $$scope: i } = e;
  return n.$$set = (o) => {
    "$$scope" in o && t(0, i = o.$$scope);
  }, [i, l];
}
class ki extends fi {
  constructor(e) {
    super(), hi(this, e, Ai, yi, bi, {});
  }
}
const {
  SvelteComponent: vi,
  attr: Dn,
  check_outros: Si,
  create_component: Li,
  create_slot: Ci,
  destroy_component: Ri,
  detach: Mt,
  element: Ni,
  empty: Oi,
  get_all_dirty_from_scope: Mi,
  get_slot_changes: Di,
  group_outros: Ii,
  init: Pi,
  insert: Dt,
  mount_component: Fi,
  safe_not_equal: Ui,
  set_data: zi,
  space: Hi,
  text: Bi,
  toggle_class: Qe,
  transition_in: ht,
  transition_out: It,
  update_slot_base: Gi
} = window.__gradio__svelte__internal;
function In(n) {
  let e, t;
  return e = new ki({
    props: {
      $$slots: { default: [Wi] },
      $$scope: { ctx: n }
    }
  }), {
    c() {
      Li(e.$$.fragment);
    },
    m(l, i) {
      Fi(e, l, i), t = !0;
    },
    p(l, i) {
      const o = {};
      i & /*$$scope, info*/
      10 && (o.$$scope = { dirty: i, ctx: l }), e.$set(o);
    },
    i(l) {
      t || (ht(e.$$.fragment, l), t = !0);
    },
    o(l) {
      It(e.$$.fragment, l), t = !1;
    },
    d(l) {
      Ri(e, l);
    }
  };
}
function Wi(n) {
  let e;
  return {
    c() {
      e = Bi(
        /*info*/
        n[1]
      );
    },
    m(t, l) {
      Dt(t, e, l);
    },
    p(t, l) {
      l & /*info*/
      2 && zi(
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
function qi(n) {
  let e, t, l, i;
  const o = (
    /*#slots*/
    n[2].default
  ), s = Ci(
    o,
    n,
    /*$$scope*/
    n[3],
    null
  );
  let c = (
    /*info*/
    n[1] && In(n)
  );
  return {
    c() {
      e = Ni("span"), s && s.c(), t = Hi(), c && c.c(), l = Oi(), Dn(e, "data-testid", "block-info"), Dn(e, "class", "svelte-22c38v"), Qe(e, "sr-only", !/*show_label*/
      n[0]), Qe(e, "hide", !/*show_label*/
      n[0]), Qe(
        e,
        "has-info",
        /*info*/
        n[1] != null
      );
    },
    m(a, r) {
      Dt(a, e, r), s && s.m(e, null), Dt(a, t, r), c && c.m(a, r), Dt(a, l, r), i = !0;
    },
    p(a, [r]) {
      s && s.p && (!i || r & /*$$scope*/
      8) && Gi(
        s,
        o,
        a,
        /*$$scope*/
        a[3],
        i ? Di(
          o,
          /*$$scope*/
          a[3],
          r,
          null
        ) : Mi(
          /*$$scope*/
          a[3]
        ),
        null
      ), (!i || r & /*show_label*/
      1) && Qe(e, "sr-only", !/*show_label*/
      a[0]), (!i || r & /*show_label*/
      1) && Qe(e, "hide", !/*show_label*/
      a[0]), (!i || r & /*info*/
      2) && Qe(
        e,
        "has-info",
        /*info*/
        a[1] != null
      ), /*info*/
      a[1] ? c ? (c.p(a, r), r & /*info*/
      2 && ht(c, 1)) : (c = In(a), c.c(), ht(c, 1), c.m(l.parentNode, l)) : c && (Ii(), It(c, 1, 1, () => {
        c = null;
      }), Si());
    },
    i(a) {
      i || (ht(s, a), ht(c), i = !0);
    },
    o(a) {
      It(s, a), It(c), i = !1;
    },
    d(a) {
      a && (Mt(e), Mt(t), Mt(l)), s && s.d(a), c && c.d(a);
    }
  };
}
function Vi(n, e, t) {
  let { $$slots: l = {}, $$scope: i } = e, { show_label: o = !0 } = e, { info: s = void 0 } = e;
  return n.$$set = (c) => {
    "show_label" in c && t(0, o = c.show_label), "info" in c && t(1, s = c.info), "$$scope" in c && t(3, i = c.$$scope);
  }, [o, s, l, i];
}
class Yi extends vi {
  constructor(e) {
    super(), Pi(this, e, Vi, qi, Ui, { show_label: 0, info: 1 });
  }
}
const {
  SvelteComponent: ji,
  append: xt,
  attr: Oe,
  bubble: Zi,
  create_component: Xi,
  destroy_component: Ki,
  detach: El,
  element: $t,
  init: Ji,
  insert: yl,
  listen: Qi,
  mount_component: xi,
  safe_not_equal: $i,
  set_data: eo,
  set_style: xe,
  space: to,
  text: no,
  toggle_class: ne,
  transition_in: lo,
  transition_out: io
} = window.__gradio__svelte__internal;
function Pn(n) {
  let e, t;
  return {
    c() {
      e = $t("span"), t = no(
        /*label*/
        n[1]
      ), Oe(e, "class", "svelte-1lrphxw");
    },
    m(l, i) {
      yl(l, e, i), xt(e, t);
    },
    p(l, i) {
      i & /*label*/
      2 && eo(
        t,
        /*label*/
        l[1]
      );
    },
    d(l) {
      l && El(e);
    }
  };
}
function oo(n) {
  let e, t, l, i, o, s, c, a = (
    /*show_label*/
    n[2] && Pn(n)
  );
  return i = new /*Icon*/
  n[0]({}), {
    c() {
      e = $t("button"), a && a.c(), t = to(), l = $t("div"), Xi(i.$$.fragment), Oe(l, "class", "svelte-1lrphxw"), ne(
        l,
        "small",
        /*size*/
        n[4] === "small"
      ), ne(
        l,
        "large",
        /*size*/
        n[4] === "large"
      ), ne(
        l,
        "medium",
        /*size*/
        n[4] === "medium"
      ), e.disabled = /*disabled*/
      n[7], Oe(
        e,
        "aria-label",
        /*label*/
        n[1]
      ), Oe(
        e,
        "aria-haspopup",
        /*hasPopup*/
        n[8]
      ), Oe(
        e,
        "title",
        /*label*/
        n[1]
      ), Oe(e, "class", "svelte-1lrphxw"), ne(
        e,
        "pending",
        /*pending*/
        n[3]
      ), ne(
        e,
        "padded",
        /*padded*/
        n[5]
      ), ne(
        e,
        "highlight",
        /*highlight*/
        n[6]
      ), ne(
        e,
        "transparent",
        /*transparent*/
        n[9]
      ), xe(e, "color", !/*disabled*/
      n[7] && /*_color*/
      n[12] ? (
        /*_color*/
        n[12]
      ) : "var(--block-label-text-color)"), xe(e, "--bg-color", /*disabled*/
      n[7] ? "auto" : (
        /*background*/
        n[10]
      )), xe(
        e,
        "margin-left",
        /*offset*/
        n[11] + "px"
      );
    },
    m(r, u) {
      yl(r, e, u), a && a.m(e, null), xt(e, t), xt(e, l), xi(i, l, null), o = !0, s || (c = Qi(
        e,
        "click",
        /*click_handler*/
        n[14]
      ), s = !0);
    },
    p(r, [u]) {
      /*show_label*/
      r[2] ? a ? a.p(r, u) : (a = Pn(r), a.c(), a.m(e, t)) : a && (a.d(1), a = null), (!o || u & /*size*/
      16) && ne(
        l,
        "small",
        /*size*/
        r[4] === "small"
      ), (!o || u & /*size*/
      16) && ne(
        l,
        "large",
        /*size*/
        r[4] === "large"
      ), (!o || u & /*size*/
      16) && ne(
        l,
        "medium",
        /*size*/
        r[4] === "medium"
      ), (!o || u & /*disabled*/
      128) && (e.disabled = /*disabled*/
      r[7]), (!o || u & /*label*/
      2) && Oe(
        e,
        "aria-label",
        /*label*/
        r[1]
      ), (!o || u & /*hasPopup*/
      256) && Oe(
        e,
        "aria-haspopup",
        /*hasPopup*/
        r[8]
      ), (!o || u & /*label*/
      2) && Oe(
        e,
        "title",
        /*label*/
        r[1]
      ), (!o || u & /*pending*/
      8) && ne(
        e,
        "pending",
        /*pending*/
        r[3]
      ), (!o || u & /*padded*/
      32) && ne(
        e,
        "padded",
        /*padded*/
        r[5]
      ), (!o || u & /*highlight*/
      64) && ne(
        e,
        "highlight",
        /*highlight*/
        r[6]
      ), (!o || u & /*transparent*/
      512) && ne(
        e,
        "transparent",
        /*transparent*/
        r[9]
      ), u & /*disabled, _color*/
      4224 && xe(e, "color", !/*disabled*/
      r[7] && /*_color*/
      r[12] ? (
        /*_color*/
        r[12]
      ) : "var(--block-label-text-color)"), u & /*disabled, background*/
      1152 && xe(e, "--bg-color", /*disabled*/
      r[7] ? "auto" : (
        /*background*/
        r[10]
      )), u & /*offset*/
      2048 && xe(
        e,
        "margin-left",
        /*offset*/
        r[11] + "px"
      );
    },
    i(r) {
      o || (lo(i.$$.fragment, r), o = !0);
    },
    o(r) {
      io(i.$$.fragment, r), o = !1;
    },
    d(r) {
      r && El(e), a && a.d(), Ki(i), s = !1, c();
    }
  };
}
function so(n, e, t) {
  let l, { Icon: i } = e, { label: o = "" } = e, { show_label: s = !1 } = e, { pending: c = !1 } = e, { size: a = "small" } = e, { padded: r = !0 } = e, { highlight: u = !1 } = e, { disabled: d = !1 } = e, { hasPopup: w = !1 } = e, { color: b = "var(--block-label-text-color)" } = e, { transparent: y = !1 } = e, { background: N = "var(--background-fill-primary)" } = e, { offset: C = 0 } = e;
  function z(h) {
    Zi.call(this, n, h);
  }
  return n.$$set = (h) => {
    "Icon" in h && t(0, i = h.Icon), "label" in h && t(1, o = h.label), "show_label" in h && t(2, s = h.show_label), "pending" in h && t(3, c = h.pending), "size" in h && t(4, a = h.size), "padded" in h && t(5, r = h.padded), "highlight" in h && t(6, u = h.highlight), "disabled" in h && t(7, d = h.disabled), "hasPopup" in h && t(8, w = h.hasPopup), "color" in h && t(13, b = h.color), "transparent" in h && t(9, y = h.transparent), "background" in h && t(10, N = h.background), "offset" in h && t(11, C = h.offset);
  }, n.$$.update = () => {
    n.$$.dirty & /*highlight, color*/
    8256 && t(12, l = u ? "var(--color-accent)" : b);
  }, [
    i,
    o,
    s,
    c,
    a,
    r,
    u,
    d,
    w,
    y,
    N,
    C,
    l,
    b,
    z
  ];
}
class ao extends ji {
  constructor(e) {
    super(), Ji(this, e, so, oo, $i, {
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
  SvelteComponent: ro,
  append: Vt,
  attr: _e,
  detach: fo,
  init: co,
  insert: uo,
  noop: Yt,
  safe_not_equal: _o,
  set_style: ye,
  svg_element: St
} = window.__gradio__svelte__internal;
function mo(n) {
  let e, t, l, i;
  return {
    c() {
      e = St("svg"), t = St("g"), l = St("path"), i = St("path"), _e(l, "d", "M18,6L6.087,17.913"), ye(l, "fill", "none"), ye(l, "fill-rule", "nonzero"), ye(l, "stroke-width", "2px"), _e(t, "transform", "matrix(1.14096,-0.140958,-0.140958,1.14096,-0.0559523,0.0559523)"), _e(i, "d", "M4.364,4.364L19.636,19.636"), ye(i, "fill", "none"), ye(i, "fill-rule", "nonzero"), ye(i, "stroke-width", "2px"), _e(e, "width", "100%"), _e(e, "height", "100%"), _e(e, "viewBox", "0 0 24 24"), _e(e, "version", "1.1"), _e(e, "xmlns", "http://www.w3.org/2000/svg"), _e(e, "xmlns:xlink", "http://www.w3.org/1999/xlink"), _e(e, "xml:space", "preserve"), _e(e, "stroke", "currentColor"), ye(e, "fill-rule", "evenodd"), ye(e, "clip-rule", "evenodd"), ye(e, "stroke-linecap", "round"), ye(e, "stroke-linejoin", "round");
    },
    m(o, s) {
      uo(o, e, s), Vt(e, t), Vt(t, l), Vt(e, i);
    },
    p: Yt,
    i: Yt,
    o: Yt,
    d(o) {
      o && fo(e);
    }
  };
}
class po extends ro {
  constructor(e) {
    super(), co(this, e, null, mo, _o, {});
  }
}
const ho = [
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
], Fn = {
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
ho.reduce(
  (n, { color: e, primary: t, secondary: l }) => ({
    ...n,
    [e]: {
      primary: Fn[e][t],
      secondary: Fn[e][l]
    }
  }),
  {}
);
function et(n) {
  let e = ["", "k", "M", "G", "T", "P", "E", "Z"], t = 0;
  for (; n > 1e3 && t < e.length - 1; )
    n /= 1e3, t++;
  let l = e[t];
  return (Number.isInteger(n) ? n : n.toFixed(1)) + l;
}
function Pt() {
}
function go(n, e) {
  return n != n ? e == e : n !== e || n && typeof n == "object" || typeof n == "function";
}
const Al = typeof window < "u";
let Un = Al ? () => window.performance.now() : () => Date.now(), kl = Al ? (n) => requestAnimationFrame(n) : Pt;
const lt = /* @__PURE__ */ new Set();
function vl(n) {
  lt.forEach((e) => {
    e.c(n) || (lt.delete(e), e.f());
  }), lt.size !== 0 && kl(vl);
}
function bo(n) {
  let e;
  return lt.size === 0 && kl(vl), {
    promise: new Promise((t) => {
      lt.add(e = { c: n, f: t });
    }),
    abort() {
      lt.delete(e);
    }
  };
}
const $e = [];
function wo(n, e = Pt) {
  let t;
  const l = /* @__PURE__ */ new Set();
  function i(c) {
    if (go(n, c) && (n = c, t)) {
      const a = !$e.length;
      for (const r of l)
        r[1](), $e.push(r, n);
      if (a) {
        for (let r = 0; r < $e.length; r += 2)
          $e[r][0]($e[r + 1]);
        $e.length = 0;
      }
    }
  }
  function o(c) {
    i(c(n));
  }
  function s(c, a = Pt) {
    const r = [c, a];
    return l.add(r), l.size === 1 && (t = e(i, o) || Pt), c(n), () => {
      l.delete(r), l.size === 0 && t && (t(), t = null);
    };
  }
  return { set: i, update: o, subscribe: s };
}
function zn(n) {
  return Object.prototype.toString.call(n) === "[object Date]";
}
function en(n, e, t, l) {
  if (typeof t == "number" || zn(t)) {
    const i = l - t, o = (t - e) / (n.dt || 1 / 60), s = n.opts.stiffness * i, c = n.opts.damping * o, a = (s - c) * n.inv_mass, r = (o + a) * n.dt;
    return Math.abs(r) < n.opts.precision && Math.abs(i) < n.opts.precision ? l : (n.settled = !1, zn(t) ? new Date(t.getTime() + r) : t + r);
  } else {
    if (Array.isArray(t))
      return t.map(
        (i, o) => en(n, e[o], t[o], l[o])
      );
    if (typeof t == "object") {
      const i = {};
      for (const o in t)
        i[o] = en(n, e[o], t[o], l[o]);
      return i;
    } else
      throw new Error(`Cannot spring ${typeof t} values`);
  }
}
function Hn(n, e = {}) {
  const t = wo(n), { stiffness: l = 0.15, damping: i = 0.8, precision: o = 0.01 } = e;
  let s, c, a, r = n, u = n, d = 1, w = 0, b = !1;
  function y(C, z = {}) {
    u = C;
    const h = a = {};
    return n == null || z.hard || N.stiffness >= 1 && N.damping >= 1 ? (b = !0, s = Un(), r = C, t.set(n = u), Promise.resolve()) : (z.soft && (w = 1 / ((z.soft === !0 ? 0.5 : +z.soft) * 60), d = 0), c || (s = Un(), b = !1, c = bo((p) => {
      if (b)
        return b = !1, c = null, !1;
      d = Math.min(d + w, 1);
      const E = {
        inv_mass: d,
        opts: N,
        settled: !0,
        dt: (p - s) * 60 / 1e3
      }, P = en(E, r, n, u);
      return s = p, r = n, t.set(n = P), E.settled && (c = null), !E.settled;
    })), new Promise((p) => {
      c.promise.then(() => {
        h === a && p();
      });
    }));
  }
  const N = {
    set: y,
    update: (C, z) => y(C(u, n), z),
    subscribe: t.subscribe,
    stiffness: l,
    damping: i,
    precision: o
  };
  return N;
}
const {
  SvelteComponent: To,
  append: de,
  attr: M,
  component_subscribe: Bn,
  detach: Eo,
  element: yo,
  init: Ao,
  insert: ko,
  noop: Gn,
  safe_not_equal: vo,
  set_style: Lt,
  svg_element: me,
  toggle_class: Wn
} = window.__gradio__svelte__internal, { onMount: So } = window.__gradio__svelte__internal;
function Lo(n) {
  let e, t, l, i, o, s, c, a, r, u, d, w;
  return {
    c() {
      e = yo("div"), t = me("svg"), l = me("g"), i = me("path"), o = me("path"), s = me("path"), c = me("path"), a = me("g"), r = me("path"), u = me("path"), d = me("path"), w = me("path"), M(i, "d", "M255.926 0.754768L509.702 139.936V221.027L255.926 81.8465V0.754768Z"), M(i, "fill", "#FF7C00"), M(i, "fill-opacity", "0.4"), M(i, "class", "svelte-43sxxs"), M(o, "d", "M509.69 139.936L254.981 279.641V361.255L509.69 221.55V139.936Z"), M(o, "fill", "#FF7C00"), M(o, "class", "svelte-43sxxs"), M(s, "d", "M0.250138 139.937L254.981 279.641V361.255L0.250138 221.55V139.937Z"), M(s, "fill", "#FF7C00"), M(s, "fill-opacity", "0.4"), M(s, "class", "svelte-43sxxs"), M(c, "d", "M255.923 0.232622L0.236328 139.936V221.55L255.923 81.8469V0.232622Z"), M(c, "fill", "#FF7C00"), M(c, "class", "svelte-43sxxs"), Lt(l, "transform", "translate(" + /*$top*/
      n[1][0] + "px, " + /*$top*/
      n[1][1] + "px)"), M(r, "d", "M255.926 141.5L509.702 280.681V361.773L255.926 222.592V141.5Z"), M(r, "fill", "#FF7C00"), M(r, "fill-opacity", "0.4"), M(r, "class", "svelte-43sxxs"), M(u, "d", "M509.69 280.679L254.981 420.384V501.998L509.69 362.293V280.679Z"), M(u, "fill", "#FF7C00"), M(u, "class", "svelte-43sxxs"), M(d, "d", "M0.250138 280.681L254.981 420.386V502L0.250138 362.295V280.681Z"), M(d, "fill", "#FF7C00"), M(d, "fill-opacity", "0.4"), M(d, "class", "svelte-43sxxs"), M(w, "d", "M255.923 140.977L0.236328 280.68V362.294L255.923 222.591V140.977Z"), M(w, "fill", "#FF7C00"), M(w, "class", "svelte-43sxxs"), Lt(a, "transform", "translate(" + /*$bottom*/
      n[2][0] + "px, " + /*$bottom*/
      n[2][1] + "px)"), M(t, "viewBox", "-1200 -1200 3000 3000"), M(t, "fill", "none"), M(t, "xmlns", "http://www.w3.org/2000/svg"), M(t, "class", "svelte-43sxxs"), M(e, "class", "svelte-43sxxs"), Wn(
        e,
        "margin",
        /*margin*/
        n[0]
      );
    },
    m(b, y) {
      ko(b, e, y), de(e, t), de(t, l), de(l, i), de(l, o), de(l, s), de(l, c), de(t, a), de(a, r), de(a, u), de(a, d), de(a, w);
    },
    p(b, [y]) {
      y & /*$top*/
      2 && Lt(l, "transform", "translate(" + /*$top*/
      b[1][0] + "px, " + /*$top*/
      b[1][1] + "px)"), y & /*$bottom*/
      4 && Lt(a, "transform", "translate(" + /*$bottom*/
      b[2][0] + "px, " + /*$bottom*/
      b[2][1] + "px)"), y & /*margin*/
      1 && Wn(
        e,
        "margin",
        /*margin*/
        b[0]
      );
    },
    i: Gn,
    o: Gn,
    d(b) {
      b && Eo(e);
    }
  };
}
function Co(n, e, t) {
  let l, i;
  var o = this && this.__awaiter || function(b, y, N, C) {
    function z(h) {
      return h instanceof N ? h : new N(function(p) {
        p(h);
      });
    }
    return new (N || (N = Promise))(function(h, p) {
      function E(H) {
        try {
          A(C.next(H));
        } catch (X) {
          p(X);
        }
      }
      function P(H) {
        try {
          A(C.throw(H));
        } catch (X) {
          p(X);
        }
      }
      function A(H) {
        H.done ? h(H.value) : z(H.value).then(E, P);
      }
      A((C = C.apply(b, y || [])).next());
    });
  };
  let { margin: s = !0 } = e;
  const c = Hn([0, 0]);
  Bn(n, c, (b) => t(1, l = b));
  const a = Hn([0, 0]);
  Bn(n, a, (b) => t(2, i = b));
  let r;
  function u() {
    return o(this, void 0, void 0, function* () {
      yield Promise.all([c.set([125, 140]), a.set([-125, -140])]), yield Promise.all([c.set([-125, 140]), a.set([125, -140])]), yield Promise.all([c.set([-125, 0]), a.set([125, -0])]), yield Promise.all([c.set([125, 0]), a.set([-125, 0])]);
    });
  }
  function d() {
    return o(this, void 0, void 0, function* () {
      yield u(), r || d();
    });
  }
  function w() {
    return o(this, void 0, void 0, function* () {
      yield Promise.all([c.set([125, 0]), a.set([-125, 0])]), d();
    });
  }
  return So(() => (w(), () => r = !0)), n.$$set = (b) => {
    "margin" in b && t(0, s = b.margin);
  }, [s, l, i, c, a];
}
class Ro extends To {
  constructor(e) {
    super(), Ao(this, e, Co, Lo, vo, { margin: 0 });
  }
}
const {
  SvelteComponent: No,
  append: Ve,
  attr: ge,
  binding_callbacks: qn,
  check_outros: tn,
  create_component: Sl,
  create_slot: Ll,
  destroy_component: Cl,
  destroy_each: Rl,
  detach: S,
  element: Se,
  empty: it,
  ensure_array_like: Ut,
  get_all_dirty_from_scope: Nl,
  get_slot_changes: Ol,
  group_outros: nn,
  init: Oo,
  insert: L,
  mount_component: Ml,
  noop: ln,
  safe_not_equal: Mo,
  set_data: ae,
  set_style: ze,
  space: se,
  text: V,
  toggle_class: oe,
  transition_in: he,
  transition_out: Le,
  update_slot_base: Dl
} = window.__gradio__svelte__internal, { tick: Do } = window.__gradio__svelte__internal, { onDestroy: Io } = window.__gradio__svelte__internal, { createEventDispatcher: Po } = window.__gradio__svelte__internal, Fo = (n) => ({}), Vn = (n) => ({}), Uo = (n) => ({}), Yn = (n) => ({});
function jn(n, e, t) {
  const l = n.slice();
  return l[41] = e[t], l[43] = t, l;
}
function Zn(n, e, t) {
  const l = n.slice();
  return l[41] = e[t], l;
}
function zo(n) {
  let e, t, l, i, o = (
    /*i18n*/
    n[1]("common.error") + ""
  ), s, c, a;
  t = new ao({
    props: {
      Icon: po,
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
  const r = (
    /*#slots*/
    n[30].error
  ), u = Ll(
    r,
    n,
    /*$$scope*/
    n[29],
    Vn
  );
  return {
    c() {
      e = Se("div"), Sl(t.$$.fragment), l = se(), i = Se("span"), s = V(o), c = se(), u && u.c(), ge(e, "class", "clear-status svelte-v0wucf"), ge(i, "class", "error svelte-v0wucf");
    },
    m(d, w) {
      L(d, e, w), Ml(t, e, null), L(d, l, w), L(d, i, w), Ve(i, s), L(d, c, w), u && u.m(d, w), a = !0;
    },
    p(d, w) {
      const b = {};
      w[0] & /*i18n*/
      2 && (b.label = /*i18n*/
      d[1]("common.clear")), t.$set(b), (!a || w[0] & /*i18n*/
      2) && o !== (o = /*i18n*/
      d[1]("common.error") + "") && ae(s, o), u && u.p && (!a || w[0] & /*$$scope*/
      536870912) && Dl(
        u,
        r,
        d,
        /*$$scope*/
        d[29],
        a ? Ol(
          r,
          /*$$scope*/
          d[29],
          w,
          Fo
        ) : Nl(
          /*$$scope*/
          d[29]
        ),
        Vn
      );
    },
    i(d) {
      a || (he(t.$$.fragment, d), he(u, d), a = !0);
    },
    o(d) {
      Le(t.$$.fragment, d), Le(u, d), a = !1;
    },
    d(d) {
      d && (S(e), S(l), S(i), S(c)), Cl(t), u && u.d(d);
    }
  };
}
function Ho(n) {
  let e, t, l, i, o, s, c, a, r, u = (
    /*variant*/
    n[8] === "default" && /*show_eta_bar*/
    n[18] && /*show_progress*/
    n[6] === "full" && Xn(n)
  );
  function d(p, E) {
    if (
      /*progress*/
      p[7]
    ) return Wo;
    if (
      /*queue_position*/
      p[2] !== null && /*queue_size*/
      p[3] !== void 0 && /*queue_position*/
      p[2] >= 0
    ) return Go;
    if (
      /*queue_position*/
      p[2] === 0
    ) return Bo;
  }
  let w = d(n), b = w && w(n), y = (
    /*timer*/
    n[5] && Qn(n)
  );
  const N = [jo, Yo], C = [];
  function z(p, E) {
    return (
      /*last_progress_level*/
      p[15] != null ? 0 : (
        /*show_progress*/
        p[6] === "full" ? 1 : -1
      )
    );
  }
  ~(o = z(n)) && (s = C[o] = N[o](n));
  let h = !/*timer*/
  n[5] && il(n);
  return {
    c() {
      u && u.c(), e = se(), t = Se("div"), b && b.c(), l = se(), y && y.c(), i = se(), s && s.c(), c = se(), h && h.c(), a = it(), ge(t, "class", "progress-text svelte-v0wucf"), oe(
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
    m(p, E) {
      u && u.m(p, E), L(p, e, E), L(p, t, E), b && b.m(t, null), Ve(t, l), y && y.m(t, null), L(p, i, E), ~o && C[o].m(p, E), L(p, c, E), h && h.m(p, E), L(p, a, E), r = !0;
    },
    p(p, E) {
      /*variant*/
      p[8] === "default" && /*show_eta_bar*/
      p[18] && /*show_progress*/
      p[6] === "full" ? u ? u.p(p, E) : (u = Xn(p), u.c(), u.m(e.parentNode, e)) : u && (u.d(1), u = null), w === (w = d(p)) && b ? b.p(p, E) : (b && b.d(1), b = w && w(p), b && (b.c(), b.m(t, l))), /*timer*/
      p[5] ? y ? y.p(p, E) : (y = Qn(p), y.c(), y.m(t, null)) : y && (y.d(1), y = null), (!r || E[0] & /*variant*/
      256) && oe(
        t,
        "meta-text-center",
        /*variant*/
        p[8] === "center"
      ), (!r || E[0] & /*variant*/
      256) && oe(
        t,
        "meta-text",
        /*variant*/
        p[8] === "default"
      );
      let P = o;
      o = z(p), o === P ? ~o && C[o].p(p, E) : (s && (nn(), Le(C[P], 1, 1, () => {
        C[P] = null;
      }), tn()), ~o ? (s = C[o], s ? s.p(p, E) : (s = C[o] = N[o](p), s.c()), he(s, 1), s.m(c.parentNode, c)) : s = null), /*timer*/
      p[5] ? h && (nn(), Le(h, 1, 1, () => {
        h = null;
      }), tn()) : h ? (h.p(p, E), E[0] & /*timer*/
      32 && he(h, 1)) : (h = il(p), h.c(), he(h, 1), h.m(a.parentNode, a));
    },
    i(p) {
      r || (he(s), he(h), r = !0);
    },
    o(p) {
      Le(s), Le(h), r = !1;
    },
    d(p) {
      p && (S(e), S(t), S(i), S(c), S(a)), u && u.d(p), b && b.d(), y && y.d(), ~o && C[o].d(p), h && h.d(p);
    }
  };
}
function Xn(n) {
  let e, t = `translateX(${/*eta_level*/
  (n[17] || 0) * 100 - 100}%)`;
  return {
    c() {
      e = Se("div"), ge(e, "class", "eta-bar svelte-v0wucf"), ze(e, "transform", t);
    },
    m(l, i) {
      L(l, e, i);
    },
    p(l, i) {
      i[0] & /*eta_level*/
      131072 && t !== (t = `translateX(${/*eta_level*/
      (l[17] || 0) * 100 - 100}%)`) && ze(e, "transform", t);
    },
    d(l) {
      l && S(e);
    }
  };
}
function Bo(n) {
  let e;
  return {
    c() {
      e = V("processing |");
    },
    m(t, l) {
      L(t, e, l);
    },
    p: ln,
    d(t) {
      t && S(e);
    }
  };
}
function Go(n) {
  let e, t = (
    /*queue_position*/
    n[2] + 1 + ""
  ), l, i, o, s;
  return {
    c() {
      e = V("queue: "), l = V(t), i = V("/"), o = V(
        /*queue_size*/
        n[3]
      ), s = V(" |");
    },
    m(c, a) {
      L(c, e, a), L(c, l, a), L(c, i, a), L(c, o, a), L(c, s, a);
    },
    p(c, a) {
      a[0] & /*queue_position*/
      4 && t !== (t = /*queue_position*/
      c[2] + 1 + "") && ae(l, t), a[0] & /*queue_size*/
      8 && ae(
        o,
        /*queue_size*/
        c[3]
      );
    },
    d(c) {
      c && (S(e), S(l), S(i), S(o), S(s));
    }
  };
}
function Wo(n) {
  let e, t = Ut(
    /*progress*/
    n[7]
  ), l = [];
  for (let i = 0; i < t.length; i += 1)
    l[i] = Jn(Zn(n, t, i));
  return {
    c() {
      for (let i = 0; i < l.length; i += 1)
        l[i].c();
      e = it();
    },
    m(i, o) {
      for (let s = 0; s < l.length; s += 1)
        l[s] && l[s].m(i, o);
      L(i, e, o);
    },
    p(i, o) {
      if (o[0] & /*progress*/
      128) {
        t = Ut(
          /*progress*/
          i[7]
        );
        let s;
        for (s = 0; s < t.length; s += 1) {
          const c = Zn(i, t, s);
          l[s] ? l[s].p(c, o) : (l[s] = Jn(c), l[s].c(), l[s].m(e.parentNode, e));
        }
        for (; s < l.length; s += 1)
          l[s].d(1);
        l.length = t.length;
      }
    },
    d(i) {
      i && S(e), Rl(l, i);
    }
  };
}
function Kn(n) {
  let e, t = (
    /*p*/
    n[41].unit + ""
  ), l, i, o = " ", s;
  function c(u, d) {
    return (
      /*p*/
      u[41].length != null ? Vo : qo
    );
  }
  let a = c(n), r = a(n);
  return {
    c() {
      r.c(), e = se(), l = V(t), i = V(" | "), s = V(o);
    },
    m(u, d) {
      r.m(u, d), L(u, e, d), L(u, l, d), L(u, i, d), L(u, s, d);
    },
    p(u, d) {
      a === (a = c(u)) && r ? r.p(u, d) : (r.d(1), r = a(u), r && (r.c(), r.m(e.parentNode, e))), d[0] & /*progress*/
      128 && t !== (t = /*p*/
      u[41].unit + "") && ae(l, t);
    },
    d(u) {
      u && (S(e), S(l), S(i), S(s)), r.d(u);
    }
  };
}
function qo(n) {
  let e = et(
    /*p*/
    n[41].index || 0
  ) + "", t;
  return {
    c() {
      t = V(e);
    },
    m(l, i) {
      L(l, t, i);
    },
    p(l, i) {
      i[0] & /*progress*/
      128 && e !== (e = et(
        /*p*/
        l[41].index || 0
      ) + "") && ae(t, e);
    },
    d(l) {
      l && S(t);
    }
  };
}
function Vo(n) {
  let e = et(
    /*p*/
    n[41].index || 0
  ) + "", t, l, i = et(
    /*p*/
    n[41].length
  ) + "", o;
  return {
    c() {
      t = V(e), l = V("/"), o = V(i);
    },
    m(s, c) {
      L(s, t, c), L(s, l, c), L(s, o, c);
    },
    p(s, c) {
      c[0] & /*progress*/
      128 && e !== (e = et(
        /*p*/
        s[41].index || 0
      ) + "") && ae(t, e), c[0] & /*progress*/
      128 && i !== (i = et(
        /*p*/
        s[41].length
      ) + "") && ae(o, i);
    },
    d(s) {
      s && (S(t), S(l), S(o));
    }
  };
}
function Jn(n) {
  let e, t = (
    /*p*/
    n[41].index != null && Kn(n)
  );
  return {
    c() {
      t && t.c(), e = it();
    },
    m(l, i) {
      t && t.m(l, i), L(l, e, i);
    },
    p(l, i) {
      /*p*/
      l[41].index != null ? t ? t.p(l, i) : (t = Kn(l), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(l) {
      l && S(e), t && t.d(l);
    }
  };
}
function Qn(n) {
  let e, t = (
    /*eta*/
    n[0] ? `/${/*formatted_eta*/
    n[19]}` : ""
  ), l, i;
  return {
    c() {
      e = V(
        /*formatted_timer*/
        n[20]
      ), l = V(t), i = V("s");
    },
    m(o, s) {
      L(o, e, s), L(o, l, s), L(o, i, s);
    },
    p(o, s) {
      s[0] & /*formatted_timer*/
      1048576 && ae(
        e,
        /*formatted_timer*/
        o[20]
      ), s[0] & /*eta, formatted_eta*/
      524289 && t !== (t = /*eta*/
      o[0] ? `/${/*formatted_eta*/
      o[19]}` : "") && ae(l, t);
    },
    d(o) {
      o && (S(e), S(l), S(i));
    }
  };
}
function Yo(n) {
  let e, t;
  return e = new Ro({
    props: { margin: (
      /*variant*/
      n[8] === "default"
    ) }
  }), {
    c() {
      Sl(e.$$.fragment);
    },
    m(l, i) {
      Ml(e, l, i), t = !0;
    },
    p(l, i) {
      const o = {};
      i[0] & /*variant*/
      256 && (o.margin = /*variant*/
      l[8] === "default"), e.$set(o);
    },
    i(l) {
      t || (he(e.$$.fragment, l), t = !0);
    },
    o(l) {
      Le(e.$$.fragment, l), t = !1;
    },
    d(l) {
      Cl(e, l);
    }
  };
}
function jo(n) {
  let e, t, l, i, o, s = `${/*last_progress_level*/
  n[15] * 100}%`, c = (
    /*progress*/
    n[7] != null && xn(n)
  );
  return {
    c() {
      e = Se("div"), t = Se("div"), c && c.c(), l = se(), i = Se("div"), o = Se("div"), ge(t, "class", "progress-level-inner svelte-v0wucf"), ge(o, "class", "progress-bar svelte-v0wucf"), ze(o, "width", s), ge(i, "class", "progress-bar-wrap svelte-v0wucf"), ge(e, "class", "progress-level svelte-v0wucf");
    },
    m(a, r) {
      L(a, e, r), Ve(e, t), c && c.m(t, null), Ve(e, l), Ve(e, i), Ve(i, o), n[31](o);
    },
    p(a, r) {
      /*progress*/
      a[7] != null ? c ? c.p(a, r) : (c = xn(a), c.c(), c.m(t, null)) : c && (c.d(1), c = null), r[0] & /*last_progress_level*/
      32768 && s !== (s = `${/*last_progress_level*/
      a[15] * 100}%`) && ze(o, "width", s);
    },
    i: ln,
    o: ln,
    d(a) {
      a && S(e), c && c.d(), n[31](null);
    }
  };
}
function xn(n) {
  let e, t = Ut(
    /*progress*/
    n[7]
  ), l = [];
  for (let i = 0; i < t.length; i += 1)
    l[i] = ll(jn(n, t, i));
  return {
    c() {
      for (let i = 0; i < l.length; i += 1)
        l[i].c();
      e = it();
    },
    m(i, o) {
      for (let s = 0; s < l.length; s += 1)
        l[s] && l[s].m(i, o);
      L(i, e, o);
    },
    p(i, o) {
      if (o[0] & /*progress_level, progress*/
      16512) {
        t = Ut(
          /*progress*/
          i[7]
        );
        let s;
        for (s = 0; s < t.length; s += 1) {
          const c = jn(i, t, s);
          l[s] ? l[s].p(c, o) : (l[s] = ll(c), l[s].c(), l[s].m(e.parentNode, e));
        }
        for (; s < l.length; s += 1)
          l[s].d(1);
        l.length = t.length;
      }
    },
    d(i) {
      i && S(e), Rl(l, i);
    }
  };
}
function $n(n) {
  let e, t, l, i, o = (
    /*i*/
    n[43] !== 0 && Zo()
  ), s = (
    /*p*/
    n[41].desc != null && el(n)
  ), c = (
    /*p*/
    n[41].desc != null && /*progress_level*/
    n[14] && /*progress_level*/
    n[14][
      /*i*/
      n[43]
    ] != null && tl()
  ), a = (
    /*progress_level*/
    n[14] != null && nl(n)
  );
  return {
    c() {
      o && o.c(), e = se(), s && s.c(), t = se(), c && c.c(), l = se(), a && a.c(), i = it();
    },
    m(r, u) {
      o && o.m(r, u), L(r, e, u), s && s.m(r, u), L(r, t, u), c && c.m(r, u), L(r, l, u), a && a.m(r, u), L(r, i, u);
    },
    p(r, u) {
      /*p*/
      r[41].desc != null ? s ? s.p(r, u) : (s = el(r), s.c(), s.m(t.parentNode, t)) : s && (s.d(1), s = null), /*p*/
      r[41].desc != null && /*progress_level*/
      r[14] && /*progress_level*/
      r[14][
        /*i*/
        r[43]
      ] != null ? c || (c = tl(), c.c(), c.m(l.parentNode, l)) : c && (c.d(1), c = null), /*progress_level*/
      r[14] != null ? a ? a.p(r, u) : (a = nl(r), a.c(), a.m(i.parentNode, i)) : a && (a.d(1), a = null);
    },
    d(r) {
      r && (S(e), S(t), S(l), S(i)), o && o.d(r), s && s.d(r), c && c.d(r), a && a.d(r);
    }
  };
}
function Zo(n) {
  let e;
  return {
    c() {
      e = V(" /");
    },
    m(t, l) {
      L(t, e, l);
    },
    d(t) {
      t && S(e);
    }
  };
}
function el(n) {
  let e = (
    /*p*/
    n[41].desc + ""
  ), t;
  return {
    c() {
      t = V(e);
    },
    m(l, i) {
      L(l, t, i);
    },
    p(l, i) {
      i[0] & /*progress*/
      128 && e !== (e = /*p*/
      l[41].desc + "") && ae(t, e);
    },
    d(l) {
      l && S(t);
    }
  };
}
function tl(n) {
  let e;
  return {
    c() {
      e = V("-");
    },
    m(t, l) {
      L(t, e, l);
    },
    d(t) {
      t && S(e);
    }
  };
}
function nl(n) {
  let e = (100 * /*progress_level*/
  (n[14][
    /*i*/
    n[43]
  ] || 0)).toFixed(1) + "", t, l;
  return {
    c() {
      t = V(e), l = V("%");
    },
    m(i, o) {
      L(i, t, o), L(i, l, o);
    },
    p(i, o) {
      o[0] & /*progress_level*/
      16384 && e !== (e = (100 * /*progress_level*/
      (i[14][
        /*i*/
        i[43]
      ] || 0)).toFixed(1) + "") && ae(t, e);
    },
    d(i) {
      i && (S(t), S(l));
    }
  };
}
function ll(n) {
  let e, t = (
    /*p*/
    (n[41].desc != null || /*progress_level*/
    n[14] && /*progress_level*/
    n[14][
      /*i*/
      n[43]
    ] != null) && $n(n)
  );
  return {
    c() {
      t && t.c(), e = it();
    },
    m(l, i) {
      t && t.m(l, i), L(l, e, i);
    },
    p(l, i) {
      /*p*/
      l[41].desc != null || /*progress_level*/
      l[14] && /*progress_level*/
      l[14][
        /*i*/
        l[43]
      ] != null ? t ? t.p(l, i) : (t = $n(l), t.c(), t.m(e.parentNode, e)) : t && (t.d(1), t = null);
    },
    d(l) {
      l && S(e), t && t.d(l);
    }
  };
}
function il(n) {
  let e, t, l, i;
  const o = (
    /*#slots*/
    n[30]["additional-loading-text"]
  ), s = Ll(
    o,
    n,
    /*$$scope*/
    n[29],
    Yn
  );
  return {
    c() {
      e = Se("p"), t = V(
        /*loading_text*/
        n[9]
      ), l = se(), s && s.c(), ge(e, "class", "loading svelte-v0wucf");
    },
    m(c, a) {
      L(c, e, a), Ve(e, t), L(c, l, a), s && s.m(c, a), i = !0;
    },
    p(c, a) {
      (!i || a[0] & /*loading_text*/
      512) && ae(
        t,
        /*loading_text*/
        c[9]
      ), s && s.p && (!i || a[0] & /*$$scope*/
      536870912) && Dl(
        s,
        o,
        c,
        /*$$scope*/
        c[29],
        i ? Ol(
          o,
          /*$$scope*/
          c[29],
          a,
          Uo
        ) : Nl(
          /*$$scope*/
          c[29]
        ),
        Yn
      );
    },
    i(c) {
      i || (he(s, c), i = !0);
    },
    o(c) {
      Le(s, c), i = !1;
    },
    d(c) {
      c && (S(e), S(l)), s && s.d(c);
    }
  };
}
function Xo(n) {
  let e, t, l, i, o;
  const s = [Ho, zo], c = [];
  function a(r, u) {
    return (
      /*status*/
      r[4] === "pending" ? 0 : (
        /*status*/
        r[4] === "error" ? 1 : -1
      )
    );
  }
  return ~(t = a(n)) && (l = c[t] = s[t](n)), {
    c() {
      e = Se("div"), l && l.c(), ge(e, "class", i = "wrap " + /*variant*/
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
      ), ze(
        e,
        "position",
        /*absolute*/
        n[10] ? "absolute" : "static"
      ), ze(
        e,
        "padding",
        /*absolute*/
        n[10] ? "0" : "var(--size-8) 0"
      );
    },
    m(r, u) {
      L(r, e, u), ~t && c[t].m(e, null), n[33](e), o = !0;
    },
    p(r, u) {
      let d = t;
      t = a(r), t === d ? ~t && c[t].p(r, u) : (l && (nn(), Le(c[d], 1, 1, () => {
        c[d] = null;
      }), tn()), ~t ? (l = c[t], l ? l.p(r, u) : (l = c[t] = s[t](r), l.c()), he(l, 1), l.m(e, null)) : l = null), (!o || u[0] & /*variant, show_progress*/
      320 && i !== (i = "wrap " + /*variant*/
      r[8] + " " + /*show_progress*/
      r[6] + " svelte-v0wucf")) && ge(e, "class", i), (!o || u[0] & /*variant, show_progress, status, show_progress*/
      336) && oe(e, "hide", !/*status*/
      r[4] || /*status*/
      r[4] === "complete" || /*show_progress*/
      r[6] === "hidden"), (!o || u[0] & /*variant, show_progress, variant, status, translucent, show_progress*/
      2384) && oe(
        e,
        "translucent",
        /*variant*/
        r[8] === "center" && /*status*/
        (r[4] === "pending" || /*status*/
        r[4] === "error") || /*translucent*/
        r[11] || /*show_progress*/
        r[6] === "minimal"
      ), (!o || u[0] & /*variant, show_progress, status, show_progress*/
      336) && oe(
        e,
        "generating",
        /*status*/
        r[4] === "generating" && /*show_progress*/
        r[6] === "full"
      ), (!o || u[0] & /*variant, show_progress, border*/
      4416) && oe(
        e,
        "border",
        /*border*/
        r[12]
      ), u[0] & /*absolute*/
      1024 && ze(
        e,
        "position",
        /*absolute*/
        r[10] ? "absolute" : "static"
      ), u[0] & /*absolute*/
      1024 && ze(
        e,
        "padding",
        /*absolute*/
        r[10] ? "0" : "var(--size-8) 0"
      );
    },
    i(r) {
      o || (he(l), o = !0);
    },
    o(r) {
      Le(l), o = !1;
    },
    d(r) {
      r && S(e), ~t && c[t].d(), n[33](null);
    }
  };
}
var Ko = function(n, e, t, l) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function c(u) {
      try {
        r(l.next(u));
      } catch (d) {
        s(d);
      }
    }
    function a(u) {
      try {
        r(l.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function r(u) {
      u.done ? o(u.value) : i(u.value).then(c, a);
    }
    r((l = l.apply(n, e || [])).next());
  });
};
let Ct = [], jt = !1;
function Jo(n) {
  return Ko(this, arguments, void 0, function* (e, t = !0) {
    if (!(window.__gradio_mode__ === "website" || window.__gradio_mode__ !== "app" && t !== !0)) {
      if (Ct.push(e), !jt) jt = !0;
      else return;
      yield Do(), requestAnimationFrame(() => {
        let l = [0, 0];
        for (let i = 0; i < Ct.length; i++) {
          const s = Ct[i].getBoundingClientRect();
          (i === 0 || s.top + window.scrollY <= l[0]) && (l[0] = s.top + window.scrollY, l[1] = i);
        }
        window.scrollTo({ top: l[0] - 20, behavior: "smooth" }), jt = !1, Ct = [];
      });
    }
  });
}
function Qo(n, e, t) {
  let l, { $$slots: i = {}, $$scope: o } = e;
  this && this.__awaiter;
  const s = Po();
  let { i18n: c } = e, { eta: a = null } = e, { queue_position: r } = e, { queue_size: u } = e, { status: d } = e, { scroll_to_output: w = !1 } = e, { timer: b = !0 } = e, { show_progress: y = "full" } = e, { message: N = null } = e, { progress: C = null } = e, { variant: z = "default" } = e, { loading_text: h = "Loading..." } = e, { absolute: p = !0 } = e, { translucent: E = !1 } = e, { border: P = !1 } = e, { autoscroll: A } = e, H, X = !1, fe = 0, D = 0, B = null, U = null, Q = 0, F = null, _, O = null, Y = !0;
  const I = () => {
    t(0, a = t(27, B = t(19, q = null))), t(25, fe = performance.now()), t(26, D = 0), X = !0, be();
  };
  function be() {
    requestAnimationFrame(() => {
      t(26, D = (performance.now() - fe) / 1e3), X && be();
    });
  }
  function ot() {
    t(26, D = 0), t(0, a = t(27, B = t(19, q = null))), X && (X = !1);
  }
  Io(() => {
    X && ot();
  });
  let q = null;
  function wt(g) {
    qn[g ? "unshift" : "push"](() => {
      O = g, t(16, O), t(7, C), t(14, F), t(15, _);
    });
  }
  const j = () => {
    s("clear_status");
  };
  function Tt(g) {
    qn[g ? "unshift" : "push"](() => {
      H = g, t(13, H);
    });
  }
  return n.$$set = (g) => {
    "i18n" in g && t(1, c = g.i18n), "eta" in g && t(0, a = g.eta), "queue_position" in g && t(2, r = g.queue_position), "queue_size" in g && t(3, u = g.queue_size), "status" in g && t(4, d = g.status), "scroll_to_output" in g && t(22, w = g.scroll_to_output), "timer" in g && t(5, b = g.timer), "show_progress" in g && t(6, y = g.show_progress), "message" in g && t(23, N = g.message), "progress" in g && t(7, C = g.progress), "variant" in g && t(8, z = g.variant), "loading_text" in g && t(9, h = g.loading_text), "absolute" in g && t(10, p = g.absolute), "translucent" in g && t(11, E = g.translucent), "border" in g && t(12, P = g.border), "autoscroll" in g && t(24, A = g.autoscroll), "$$scope" in g && t(29, o = g.$$scope);
  }, n.$$.update = () => {
    n.$$.dirty[0] & /*eta, old_eta, timer_start, eta_from_start*/
    436207617 && (a === null && t(0, a = B), a != null && B !== a && (t(28, U = (performance.now() - fe) / 1e3 + a), t(19, q = U.toFixed(1)), t(27, B = a))), n.$$.dirty[0] & /*eta_from_start, timer_diff*/
    335544320 && t(17, Q = U === null || U <= 0 || !D ? null : Math.min(D / U, 1)), n.$$.dirty[0] & /*progress*/
    128 && C != null && t(18, Y = !1), n.$$.dirty[0] & /*progress, progress_level, progress_bar, last_progress_level*/
    114816 && (C != null ? t(14, F = C.map((g) => {
      if (g.index != null && g.length != null)
        return g.index / g.length;
      if (g.progress != null)
        return g.progress;
    })) : t(14, F = null), F ? (t(15, _ = F[F.length - 1]), O && (_ === 0 ? t(16, O.style.transition = "0", O) : t(16, O.style.transition = "150ms", O))) : t(15, _ = void 0)), n.$$.dirty[0] & /*status*/
    16 && (d === "pending" ? I() : ot()), n.$$.dirty[0] & /*el, scroll_to_output, status, autoscroll*/
    20979728 && H && w && (d === "pending" || d === "complete") && Jo(H, A), n.$$.dirty[0] & /*status, message*/
    8388624, n.$$.dirty[0] & /*timer_diff*/
    67108864 && t(20, l = D.toFixed(1));
  }, [
    a,
    c,
    r,
    u,
    d,
    b,
    y,
    C,
    z,
    h,
    p,
    E,
    P,
    H,
    F,
    _,
    O,
    Q,
    Y,
    q,
    l,
    s,
    w,
    N,
    A,
    fe,
    D,
    B,
    U,
    o,
    i,
    wt,
    j,
    Tt
  ];
}
class xo extends No {
  constructor(e) {
    super(), Oo(
      this,
      e,
      Qo,
      Xo,
      Mo,
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
  entries: Il,
  setPrototypeOf: ol,
  isFrozen: $o,
  getPrototypeOf: es,
  getOwnPropertyDescriptor: ts
} = Object;
let {
  freeze: ee,
  seal: re,
  create: Pl
} = Object, {
  apply: on,
  construct: sn
} = typeof Reflect < "u" && Reflect;
ee || (ee = function(e) {
  return e;
});
re || (re = function(e) {
  return e;
});
on || (on = function(e, t, l) {
  return e.apply(t, l);
});
sn || (sn = function(e, t) {
  return new e(...t);
});
const Rt = ie(Array.prototype.forEach), sl = ie(Array.prototype.pop), ut = ie(Array.prototype.push), Ft = ie(String.prototype.toLowerCase), Zt = ie(String.prototype.toString), al = ie(String.prototype.match), _t = ie(String.prototype.replace), ns = ie(String.prototype.indexOf), ls = ie(String.prototype.trim), pe = ie(Object.prototype.hasOwnProperty), $ = ie(RegExp.prototype.test), dt = is(TypeError);
function ie(n) {
  return function(e) {
    for (var t = arguments.length, l = new Array(t > 1 ? t - 1 : 0), i = 1; i < t; i++)
      l[i - 1] = arguments[i];
    return on(n, e, l);
  };
}
function is(n) {
  return function() {
    for (var e = arguments.length, t = new Array(e), l = 0; l < e; l++)
      t[l] = arguments[l];
    return sn(n, t);
  };
}
function R(n, e) {
  let t = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : Ft;
  ol && ol(n, null);
  let l = e.length;
  for (; l--; ) {
    let i = e[l];
    if (typeof i == "string") {
      const o = t(i);
      o !== i && ($o(e) || (e[l] = o), i = o);
    }
    n[i] = !0;
  }
  return n;
}
function os(n) {
  for (let e = 0; e < n.length; e++)
    pe(n, e) || (n[e] = null);
  return n;
}
function qe(n) {
  const e = Pl(null);
  for (const [t, l] of Il(n))
    pe(n, t) && (Array.isArray(l) ? e[t] = os(l) : l && typeof l == "object" && l.constructor === Object ? e[t] = qe(l) : e[t] = l);
  return e;
}
function mt(n, e) {
  for (; n !== null; ) {
    const l = ts(n, e);
    if (l) {
      if (l.get)
        return ie(l.get);
      if (typeof l.value == "function")
        return ie(l.value);
    }
    n = es(n);
  }
  function t() {
    return null;
  }
  return t;
}
const rl = ee(["a", "abbr", "acronym", "address", "area", "article", "aside", "audio", "b", "bdi", "bdo", "big", "blink", "blockquote", "body", "br", "button", "canvas", "caption", "center", "cite", "code", "col", "colgroup", "content", "data", "datalist", "dd", "decorator", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "element", "em", "fieldset", "figcaption", "figure", "font", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "i", "img", "input", "ins", "kbd", "label", "legend", "li", "main", "map", "mark", "marquee", "menu", "menuitem", "meter", "nav", "nobr", "ol", "optgroup", "option", "output", "p", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "section", "select", "shadow", "small", "source", "spacer", "span", "strike", "strong", "style", "sub", "summary", "sup", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "tr", "track", "tt", "u", "ul", "var", "video", "wbr"]), Xt = ee(["svg", "a", "altglyph", "altglyphdef", "altglyphitem", "animatecolor", "animatemotion", "animatetransform", "circle", "clippath", "defs", "desc", "ellipse", "filter", "font", "g", "glyph", "glyphref", "hkern", "image", "line", "lineargradient", "marker", "mask", "metadata", "mpath", "path", "pattern", "polygon", "polyline", "radialgradient", "rect", "stop", "style", "switch", "symbol", "text", "textpath", "title", "tref", "tspan", "view", "vkern"]), Kt = ee(["feBlend", "feColorMatrix", "feComponentTransfer", "feComposite", "feConvolveMatrix", "feDiffuseLighting", "feDisplacementMap", "feDistantLight", "feDropShadow", "feFlood", "feFuncA", "feFuncB", "feFuncG", "feFuncR", "feGaussianBlur", "feImage", "feMerge", "feMergeNode", "feMorphology", "feOffset", "fePointLight", "feSpecularLighting", "feSpotLight", "feTile", "feTurbulence"]), ss = ee(["animate", "color-profile", "cursor", "discard", "font-face", "font-face-format", "font-face-name", "font-face-src", "font-face-uri", "foreignobject", "hatch", "hatchpath", "mesh", "meshgradient", "meshpatch", "meshrow", "missing-glyph", "script", "set", "solidcolor", "unknown", "use"]), Jt = ee(["math", "menclose", "merror", "mfenced", "mfrac", "mglyph", "mi", "mlabeledtr", "mmultiscripts", "mn", "mo", "mover", "mpadded", "mphantom", "mroot", "mrow", "ms", "mspace", "msqrt", "mstyle", "msub", "msup", "msubsup", "mtable", "mtd", "mtext", "mtr", "munder", "munderover", "mprescripts"]), as = ee(["maction", "maligngroup", "malignmark", "mlongdiv", "mscarries", "mscarry", "msgroup", "mstack", "msline", "msrow", "semantics", "annotation", "annotation-xml", "mprescripts", "none"]), fl = ee(["#text"]), cl = ee(["accept", "action", "align", "alt", "autocapitalize", "autocomplete", "autopictureinpicture", "autoplay", "background", "bgcolor", "border", "capture", "cellpadding", "cellspacing", "checked", "cite", "class", "clear", "color", "cols", "colspan", "controls", "controlslist", "coords", "crossorigin", "datetime", "decoding", "default", "dir", "disabled", "disablepictureinpicture", "disableremoteplayback", "download", "draggable", "enctype", "enterkeyhint", "face", "for", "headers", "height", "hidden", "high", "href", "hreflang", "id", "inputmode", "integrity", "ismap", "kind", "label", "lang", "list", "loading", "loop", "low", "max", "maxlength", "media", "method", "min", "minlength", "multiple", "muted", "name", "nonce", "noshade", "novalidate", "nowrap", "open", "optimum", "pattern", "placeholder", "playsinline", "popover", "popovertarget", "popovertargetaction", "poster", "preload", "pubdate", "radiogroup", "readonly", "rel", "required", "rev", "reversed", "role", "rows", "rowspan", "spellcheck", "scope", "selected", "shape", "size", "sizes", "span", "srclang", "start", "src", "srcset", "step", "style", "summary", "tabindex", "title", "translate", "type", "usemap", "valign", "value", "width", "wrap", "xmlns", "slot"]), Qt = ee(["accent-height", "accumulate", "additive", "alignment-baseline", "ascent", "attributename", "attributetype", "azimuth", "basefrequency", "baseline-shift", "begin", "bias", "by", "class", "clip", "clippathunits", "clip-path", "clip-rule", "color", "color-interpolation", "color-interpolation-filters", "color-profile", "color-rendering", "cx", "cy", "d", "dx", "dy", "diffuseconstant", "direction", "display", "divisor", "dur", "edgemode", "elevation", "end", "fill", "fill-opacity", "fill-rule", "filter", "filterunits", "flood-color", "flood-opacity", "font-family", "font-size", "font-size-adjust", "font-stretch", "font-style", "font-variant", "font-weight", "fx", "fy", "g1", "g2", "glyph-name", "glyphref", "gradientunits", "gradienttransform", "height", "href", "id", "image-rendering", "in", "in2", "k", "k1", "k2", "k3", "k4", "kerning", "keypoints", "keysplines", "keytimes", "lang", "lengthadjust", "letter-spacing", "kernelmatrix", "kernelunitlength", "lighting-color", "local", "marker-end", "marker-mid", "marker-start", "markerheight", "markerunits", "markerwidth", "maskcontentunits", "maskunits", "max", "mask", "media", "method", "mode", "min", "name", "numoctaves", "offset", "operator", "opacity", "order", "orient", "orientation", "origin", "overflow", "paint-order", "path", "pathlength", "patterncontentunits", "patterntransform", "patternunits", "points", "preservealpha", "preserveaspectratio", "primitiveunits", "r", "rx", "ry", "radius", "refx", "refy", "repeatcount", "repeatdur", "restart", "result", "rotate", "scale", "seed", "shape-rendering", "specularconstant", "specularexponent", "spreadmethod", "startoffset", "stddeviation", "stitchtiles", "stop-color", "stop-opacity", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke", "stroke-width", "style", "surfacescale", "systemlanguage", "tabindex", "targetx", "targety", "transform", "transform-origin", "text-anchor", "text-decoration", "text-rendering", "textlength", "type", "u1", "u2", "unicode", "values", "viewbox", "visibility", "version", "vert-adv-y", "vert-origin-x", "vert-origin-y", "width", "word-spacing", "wrap", "writing-mode", "xchannelselector", "ychannelselector", "x", "x1", "x2", "xmlns", "y", "y1", "y2", "z", "zoomandpan"]), ul = ee(["accent", "accentunder", "align", "bevelled", "close", "columnsalign", "columnlines", "columnspan", "denomalign", "depth", "dir", "display", "displaystyle", "encoding", "fence", "frame", "height", "href", "id", "largeop", "length", "linethickness", "lspace", "lquote", "mathbackground", "mathcolor", "mathsize", "mathvariant", "maxsize", "minsize", "movablelimits", "notation", "numalign", "open", "rowalign", "rowlines", "rowspacing", "rowspan", "rspace", "rquote", "scriptlevel", "scriptminsize", "scriptsizemultiplier", "selection", "separator", "separators", "stretchy", "subscriptshift", "supscriptshift", "symmetric", "voffset", "width", "xmlns"]), Nt = ee(["xlink:href", "xml:id", "xlink:title", "xml:space", "xmlns:xlink"]), rs = re(/\{\{[\w\W]*|[\w\W]*\}\}/gm), fs = re(/<%[\w\W]*|[\w\W]*%>/gm), cs = re(/\${[\w\W]*}/gm), us = re(/^data-[\-\w.\u00B7-\uFFFF]/), _s = re(/^aria-[\-\w]+$/), Fl = re(
  /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
  // eslint-disable-line no-useless-escape
), ds = re(/^(?:\w+script|data):/i), ms = re(
  /[\u0000-\u0020\u00A0\u1680\u180E\u2000-\u2029\u205F\u3000]/g
  // eslint-disable-line no-control-regex
), Ul = re(/^html$/i), ps = re(/^[a-z][.\w]*(-[.\w]+)+$/i);
var _l = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  MUSTACHE_EXPR: rs,
  ERB_EXPR: fs,
  TMPLIT_EXPR: cs,
  DATA_ATTR: us,
  ARIA_ATTR: _s,
  IS_ALLOWED_URI: Fl,
  IS_SCRIPT_OR_DATA: ds,
  ATTR_WHITESPACE: ms,
  DOCTYPE_NAME: Ul,
  CUSTOM_ELEMENT: ps
});
const pt = {
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
}, hs = function() {
  return typeof window > "u" ? null : window;
}, gs = function(e, t) {
  if (typeof e != "object" || typeof e.createPolicy != "function")
    return null;
  let l = null;
  const i = "data-tt-policy-suffix";
  t && t.hasAttribute(i) && (l = t.getAttribute(i));
  const o = "dompurify" + (l ? "#" + l : "");
  try {
    return e.createPolicy(o, {
      createHTML(s) {
        return s;
      },
      createScriptURL(s) {
        return s;
      }
    });
  } catch {
    return console.warn("TrustedTypes policy " + o + " could not be created."), null;
  }
};
function zl() {
  let n = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : hs();
  const e = (k) => zl(k);
  if (e.version = "3.1.6", e.removed = [], !n || !n.document || n.document.nodeType !== pt.document)
    return e.isSupported = !1, e;
  let {
    document: t
  } = n;
  const l = t, i = l.currentScript, {
    DocumentFragment: o,
    HTMLTemplateElement: s,
    Node: c,
    Element: a,
    NodeFilter: r,
    NamedNodeMap: u = n.NamedNodeMap || n.MozNamedAttrMap,
    HTMLFormElement: d,
    DOMParser: w,
    trustedTypes: b
  } = n, y = a.prototype, N = mt(y, "cloneNode"), C = mt(y, "remove"), z = mt(y, "nextSibling"), h = mt(y, "childNodes"), p = mt(y, "parentNode");
  if (typeof s == "function") {
    const k = t.createElement("template");
    k.content && k.content.ownerDocument && (t = k.content.ownerDocument);
  }
  let E, P = "";
  const {
    implementation: A,
    createNodeIterator: H,
    createDocumentFragment: X,
    getElementsByTagName: fe
  } = t, {
    importNode: D
  } = l;
  let B = {};
  e.isSupported = typeof Il == "function" && typeof p == "function" && A && A.createHTMLDocument !== void 0;
  const {
    MUSTACHE_EXPR: U,
    ERB_EXPR: Q,
    TMPLIT_EXPR: F,
    DATA_ATTR: _,
    ARIA_ATTR: O,
    IS_SCRIPT_OR_DATA: Y,
    ATTR_WHITESPACE: I,
    CUSTOM_ELEMENT: be
  } = _l;
  let {
    IS_ALLOWED_URI: ot
  } = _l, q = null;
  const wt = R({}, [...rl, ...Xt, ...Kt, ...Jt, ...fl]);
  let j = null;
  const Tt = R({}, [...cl, ...Qt, ...ul, ...Nt]);
  let g = Object.seal(Pl(null, {
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
  })), He = null, Me = null, Be = !0, st = !0, De = !1, Ge = !0, Ie = !1, at = !0, ce = !1, ue = !1, We = !1, je = !1, Et = !1, yt = !1, un = !0, _n = !1;
  const Hl = "user-content-";
  let Ht = !0, rt = !1, Ze = {}, Xe = null;
  const dn = R({}, ["annotation-xml", "audio", "colgroup", "desc", "foreignobject", "head", "iframe", "math", "mi", "mn", "mo", "ms", "mtext", "noembed", "noframes", "noscript", "plaintext", "script", "style", "svg", "template", "thead", "title", "video", "xmp"]);
  let mn = null;
  const pn = R({}, ["audio", "video", "img", "source", "image", "track"]);
  let Bt = null;
  const hn = R({}, ["alt", "class", "for", "id", "label", "name", "pattern", "placeholder", "role", "summary", "title", "value", "style", "xmlns"]), At = "http://www.w3.org/1998/Math/MathML", kt = "http://www.w3.org/2000/svg", Re = "http://www.w3.org/1999/xhtml";
  let Ke = Re, Gt = !1, Wt = null;
  const Bl = R({}, [At, kt, Re], Zt);
  let ft = null;
  const Gl = ["application/xhtml+xml", "text/html"], Wl = "text/html";
  let Z = null, Je = null;
  const ql = t.createElement("form"), gn = function(f) {
    return f instanceof RegExp || f instanceof Function;
  }, qt = function() {
    let f = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
    if (!(Je && Je === f)) {
      if ((!f || typeof f != "object") && (f = {}), f = qe(f), ft = // eslint-disable-next-line unicorn/prefer-includes
      Gl.indexOf(f.PARSER_MEDIA_TYPE) === -1 ? Wl : f.PARSER_MEDIA_TYPE, Z = ft === "application/xhtml+xml" ? Zt : Ft, q = pe(f, "ALLOWED_TAGS") ? R({}, f.ALLOWED_TAGS, Z) : wt, j = pe(f, "ALLOWED_ATTR") ? R({}, f.ALLOWED_ATTR, Z) : Tt, Wt = pe(f, "ALLOWED_NAMESPACES") ? R({}, f.ALLOWED_NAMESPACES, Zt) : Bl, Bt = pe(f, "ADD_URI_SAFE_ATTR") ? R(
        qe(hn),
        // eslint-disable-line indent
        f.ADD_URI_SAFE_ATTR,
        // eslint-disable-line indent
        Z
        // eslint-disable-line indent
      ) : hn, mn = pe(f, "ADD_DATA_URI_TAGS") ? R(
        qe(pn),
        // eslint-disable-line indent
        f.ADD_DATA_URI_TAGS,
        // eslint-disable-line indent
        Z
        // eslint-disable-line indent
      ) : pn, Xe = pe(f, "FORBID_CONTENTS") ? R({}, f.FORBID_CONTENTS, Z) : dn, He = pe(f, "FORBID_TAGS") ? R({}, f.FORBID_TAGS, Z) : {}, Me = pe(f, "FORBID_ATTR") ? R({}, f.FORBID_ATTR, Z) : {}, Ze = pe(f, "USE_PROFILES") ? f.USE_PROFILES : !1, Be = f.ALLOW_ARIA_ATTR !== !1, st = f.ALLOW_DATA_ATTR !== !1, De = f.ALLOW_UNKNOWN_PROTOCOLS || !1, Ge = f.ALLOW_SELF_CLOSE_IN_ATTR !== !1, Ie = f.SAFE_FOR_TEMPLATES || !1, at = f.SAFE_FOR_XML !== !1, ce = f.WHOLE_DOCUMENT || !1, je = f.RETURN_DOM || !1, Et = f.RETURN_DOM_FRAGMENT || !1, yt = f.RETURN_TRUSTED_TYPE || !1, We = f.FORCE_BODY || !1, un = f.SANITIZE_DOM !== !1, _n = f.SANITIZE_NAMED_PROPS || !1, Ht = f.KEEP_CONTENT !== !1, rt = f.IN_PLACE || !1, ot = f.ALLOWED_URI_REGEXP || Fl, Ke = f.NAMESPACE || Re, g = f.CUSTOM_ELEMENT_HANDLING || {}, f.CUSTOM_ELEMENT_HANDLING && gn(f.CUSTOM_ELEMENT_HANDLING.tagNameCheck) && (g.tagNameCheck = f.CUSTOM_ELEMENT_HANDLING.tagNameCheck), f.CUSTOM_ELEMENT_HANDLING && gn(f.CUSTOM_ELEMENT_HANDLING.attributeNameCheck) && (g.attributeNameCheck = f.CUSTOM_ELEMENT_HANDLING.attributeNameCheck), f.CUSTOM_ELEMENT_HANDLING && typeof f.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements == "boolean" && (g.allowCustomizedBuiltInElements = f.CUSTOM_ELEMENT_HANDLING.allowCustomizedBuiltInElements), Ie && (st = !1), Et && (je = !0), Ze && (q = R({}, fl), j = [], Ze.html === !0 && (R(q, rl), R(j, cl)), Ze.svg === !0 && (R(q, Xt), R(j, Qt), R(j, Nt)), Ze.svgFilters === !0 && (R(q, Kt), R(j, Qt), R(j, Nt)), Ze.mathMl === !0 && (R(q, Jt), R(j, ul), R(j, Nt))), f.ADD_TAGS && (q === wt && (q = qe(q)), R(q, f.ADD_TAGS, Z)), f.ADD_ATTR && (j === Tt && (j = qe(j)), R(j, f.ADD_ATTR, Z)), f.ADD_URI_SAFE_ATTR && R(Bt, f.ADD_URI_SAFE_ATTR, Z), f.FORBID_CONTENTS && (Xe === dn && (Xe = qe(Xe)), R(Xe, f.FORBID_CONTENTS, Z)), Ht && (q["#text"] = !0), ce && R(q, ["html", "head", "body"]), q.table && (R(q, ["tbody"]), delete He.tbody), f.TRUSTED_TYPES_POLICY) {
        if (typeof f.TRUSTED_TYPES_POLICY.createHTML != "function")
          throw dt('TRUSTED_TYPES_POLICY configuration option must provide a "createHTML" hook.');
        if (typeof f.TRUSTED_TYPES_POLICY.createScriptURL != "function")
          throw dt('TRUSTED_TYPES_POLICY configuration option must provide a "createScriptURL" hook.');
        E = f.TRUSTED_TYPES_POLICY, P = E.createHTML("");
      } else
        E === void 0 && (E = gs(b, i)), E !== null && typeof P == "string" && (P = E.createHTML(""));
      ee && ee(f), Je = f;
    }
  }, bn = R({}, ["mi", "mo", "mn", "ms", "mtext"]), wn = R({}, ["foreignobject", "annotation-xml"]), Vl = R({}, ["title", "style", "font", "a", "script"]), Tn = R({}, [...Xt, ...Kt, ...ss]), En = R({}, [...Jt, ...as]), Yl = function(f) {
    let m = p(f);
    (!m || !m.tagName) && (m = {
      namespaceURI: Ke,
      tagName: "template"
    });
    const T = Ft(f.tagName), G = Ft(m.tagName);
    return Wt[f.namespaceURI] ? f.namespaceURI === kt ? m.namespaceURI === Re ? T === "svg" : m.namespaceURI === At ? T === "svg" && (G === "annotation-xml" || bn[G]) : !!Tn[T] : f.namespaceURI === At ? m.namespaceURI === Re ? T === "math" : m.namespaceURI === kt ? T === "math" && wn[G] : !!En[T] : f.namespaceURI === Re ? m.namespaceURI === kt && !wn[G] || m.namespaceURI === At && !bn[G] ? !1 : !En[T] && (Vl[T] || !Tn[T]) : !!(ft === "application/xhtml+xml" && Wt[f.namespaceURI]) : !1;
  }, we = function(f) {
    ut(e.removed, {
      element: f
    });
    try {
      p(f).removeChild(f);
    } catch {
      C(f);
    }
  }, vt = function(f, m) {
    try {
      ut(e.removed, {
        attribute: m.getAttributeNode(f),
        from: m
      });
    } catch {
      ut(e.removed, {
        attribute: null,
        from: m
      });
    }
    if (m.removeAttribute(f), f === "is" && !j[f])
      if (je || Et)
        try {
          we(m);
        } catch {
        }
      else
        try {
          m.setAttribute(f, "");
        } catch {
        }
  }, yn = function(f) {
    let m = null, T = null;
    if (We)
      f = "<remove></remove>" + f;
    else {
      const K = al(f, /^[\r\n\t ]+/);
      T = K && K[0];
    }
    ft === "application/xhtml+xml" && Ke === Re && (f = '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body>' + f + "</body></html>");
    const G = E ? E.createHTML(f) : f;
    if (Ke === Re)
      try {
        m = new w().parseFromString(G, ft);
      } catch {
      }
    if (!m || !m.documentElement) {
      m = A.createDocument(Ke, "template", null);
      try {
        m.documentElement.innerHTML = Gt ? P : G;
      } catch {
      }
    }
    const J = m.body || m.documentElement;
    return f && T && J.insertBefore(t.createTextNode(T), J.childNodes[0] || null), Ke === Re ? fe.call(m, ce ? "html" : "body")[0] : ce ? m.documentElement : J;
  }, An = function(f) {
    return H.call(
      f.ownerDocument || f,
      f,
      // eslint-disable-next-line no-bitwise
      r.SHOW_ELEMENT | r.SHOW_COMMENT | r.SHOW_TEXT | r.SHOW_PROCESSING_INSTRUCTION | r.SHOW_CDATA_SECTION,
      null
    );
  }, kn = function(f) {
    return f instanceof d && (typeof f.nodeName != "string" || typeof f.textContent != "string" || typeof f.removeChild != "function" || !(f.attributes instanceof u) || typeof f.removeAttribute != "function" || typeof f.setAttribute != "function" || typeof f.namespaceURI != "string" || typeof f.insertBefore != "function" || typeof f.hasChildNodes != "function");
  }, vn = function(f) {
    return typeof c == "function" && f instanceof c;
  }, Ne = function(f, m, T) {
    B[f] && Rt(B[f], (G) => {
      G.call(e, m, T, Je);
    });
  }, Sn = function(f) {
    let m = null;
    if (Ne("beforeSanitizeElements", f, null), kn(f))
      return we(f), !0;
    const T = Z(f.nodeName);
    if (Ne("uponSanitizeElement", f, {
      tagName: T,
      allowedTags: q
    }), f.hasChildNodes() && !vn(f.firstElementChild) && $(/<[/\w]/g, f.innerHTML) && $(/<[/\w]/g, f.textContent) || f.nodeType === pt.progressingInstruction || at && f.nodeType === pt.comment && $(/<[/\w]/g, f.data))
      return we(f), !0;
    if (!q[T] || He[T]) {
      if (!He[T] && Cn(T) && (g.tagNameCheck instanceof RegExp && $(g.tagNameCheck, T) || g.tagNameCheck instanceof Function && g.tagNameCheck(T)))
        return !1;
      if (Ht && !Xe[T]) {
        const G = p(f) || f.parentNode, J = h(f) || f.childNodes;
        if (J && G) {
          const K = J.length;
          for (let te = K - 1; te >= 0; --te) {
            const Te = N(J[te], !0);
            Te.__removalCount = (f.__removalCount || 0) + 1, G.insertBefore(Te, z(f));
          }
        }
      }
      return we(f), !0;
    }
    return f instanceof a && !Yl(f) || (T === "noscript" || T === "noembed" || T === "noframes") && $(/<\/no(script|embed|frames)/i, f.innerHTML) ? (we(f), !0) : (Ie && f.nodeType === pt.text && (m = f.textContent, Rt([U, Q, F], (G) => {
      m = _t(m, G, " ");
    }), f.textContent !== m && (ut(e.removed, {
      element: f.cloneNode()
    }), f.textContent = m)), Ne("afterSanitizeElements", f, null), !1);
  }, Ln = function(f, m, T) {
    if (un && (m === "id" || m === "name") && (T in t || T in ql))
      return !1;
    if (!(st && !Me[m] && $(_, m))) {
      if (!(Be && $(O, m))) {
        if (!j[m] || Me[m]) {
          if (
            // First condition does a very basic check if a) it's basically a valid custom element tagname AND
            // b) if the tagName passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
            // and c) if the attribute name passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.attributeNameCheck
            !(Cn(f) && (g.tagNameCheck instanceof RegExp && $(g.tagNameCheck, f) || g.tagNameCheck instanceof Function && g.tagNameCheck(f)) && (g.attributeNameCheck instanceof RegExp && $(g.attributeNameCheck, m) || g.attributeNameCheck instanceof Function && g.attributeNameCheck(m)) || // Alternative, second condition checks if it's an `is`-attribute, AND
            // the value passes whatever the user has configured for CUSTOM_ELEMENT_HANDLING.tagNameCheck
            m === "is" && g.allowCustomizedBuiltInElements && (g.tagNameCheck instanceof RegExp && $(g.tagNameCheck, T) || g.tagNameCheck instanceof Function && g.tagNameCheck(T)))
          ) return !1;
        } else if (!Bt[m]) {
          if (!$(ot, _t(T, I, ""))) {
            if (!((m === "src" || m === "xlink:href" || m === "href") && f !== "script" && ns(T, "data:") === 0 && mn[f])) {
              if (!(De && !$(Y, _t(T, I, "")))) {
                if (T)
                  return !1;
              }
            }
          }
        }
      }
    }
    return !0;
  }, Cn = function(f) {
    return f !== "annotation-xml" && al(f, be);
  }, Rn = function(f) {
    Ne("beforeSanitizeAttributes", f, null);
    const {
      attributes: m
    } = f;
    if (!m)
      return;
    const T = {
      attrName: "",
      attrValue: "",
      keepAttr: !0,
      allowedAttributes: j
    };
    let G = m.length;
    for (; G--; ) {
      const J = m[G], {
        name: K,
        namespaceURI: te,
        value: Te
      } = J, ct = Z(K);
      let x = K === "value" ? Te : ls(Te);
      if (T.attrName = ct, T.attrValue = x, T.keepAttr = !0, T.forceKeepAttr = void 0, Ne("uponSanitizeAttribute", f, T), x = T.attrValue, at && $(/((--!?|])>)|<\/(style|title)/i, x)) {
        vt(K, f);
        continue;
      }
      if (T.forceKeepAttr || (vt(K, f), !T.keepAttr))
        continue;
      if (!Ge && $(/\/>/i, x)) {
        vt(K, f);
        continue;
      }
      Ie && Rt([U, Q, F], (On) => {
        x = _t(x, On, " ");
      });
      const Nn = Z(f.nodeName);
      if (Ln(Nn, ct, x)) {
        if (_n && (ct === "id" || ct === "name") && (vt(K, f), x = Hl + x), E && typeof b == "object" && typeof b.getAttributeType == "function" && !te)
          switch (b.getAttributeType(Nn, ct)) {
            case "TrustedHTML": {
              x = E.createHTML(x);
              break;
            }
            case "TrustedScriptURL": {
              x = E.createScriptURL(x);
              break;
            }
          }
        try {
          te ? f.setAttributeNS(te, K, x) : f.setAttribute(K, x), kn(f) ? we(f) : sl(e.removed);
        } catch {
        }
      }
    }
    Ne("afterSanitizeAttributes", f, null);
  }, jl = function k(f) {
    let m = null;
    const T = An(f);
    for (Ne("beforeSanitizeShadowDOM", f, null); m = T.nextNode(); )
      Ne("uponSanitizeShadowNode", m, null), !Sn(m) && (m.content instanceof o && k(m.content), Rn(m));
    Ne("afterSanitizeShadowDOM", f, null);
  };
  return e.sanitize = function(k) {
    let f = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {}, m = null, T = null, G = null, J = null;
    if (Gt = !k, Gt && (k = "<!-->"), typeof k != "string" && !vn(k))
      if (typeof k.toString == "function") {
        if (k = k.toString(), typeof k != "string")
          throw dt("dirty is not a string, aborting");
      } else
        throw dt("toString is not a function");
    if (!e.isSupported)
      return k;
    if (ue || qt(f), e.removed = [], typeof k == "string" && (rt = !1), rt) {
      if (k.nodeName) {
        const Te = Z(k.nodeName);
        if (!q[Te] || He[Te])
          throw dt("root node is forbidden and cannot be sanitized in-place");
      }
    } else if (k instanceof c)
      m = yn("<!---->"), T = m.ownerDocument.importNode(k, !0), T.nodeType === pt.element && T.nodeName === "BODY" || T.nodeName === "HTML" ? m = T : m.appendChild(T);
    else {
      if (!je && !Ie && !ce && // eslint-disable-next-line unicorn/prefer-includes
      k.indexOf("<") === -1)
        return E && yt ? E.createHTML(k) : k;
      if (m = yn(k), !m)
        return je ? null : yt ? P : "";
    }
    m && We && we(m.firstChild);
    const K = An(rt ? k : m);
    for (; G = K.nextNode(); )
      Sn(G) || (G.content instanceof o && jl(G.content), Rn(G));
    if (rt)
      return k;
    if (je) {
      if (Et)
        for (J = X.call(m.ownerDocument); m.firstChild; )
          J.appendChild(m.firstChild);
      else
        J = m;
      return (j.shadowroot || j.shadowrootmode) && (J = D.call(l, J, !0)), J;
    }
    let te = ce ? m.outerHTML : m.innerHTML;
    return ce && q["!doctype"] && m.ownerDocument && m.ownerDocument.doctype && m.ownerDocument.doctype.name && $(Ul, m.ownerDocument.doctype.name) && (te = "<!DOCTYPE " + m.ownerDocument.doctype.name + `>
` + te), Ie && Rt([U, Q, F], (Te) => {
      te = _t(te, Te, " ");
    }), E && yt ? E.createHTML(te) : te;
  }, e.setConfig = function() {
    let k = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
    qt(k), ue = !0;
  }, e.clearConfig = function() {
    Je = null, ue = !1;
  }, e.isValidAttribute = function(k, f, m) {
    Je || qt({});
    const T = Z(k), G = Z(f);
    return Ln(T, G, m);
  }, e.addHook = function(k, f) {
    typeof f == "function" && (B[k] = B[k] || [], ut(B[k], f));
  }, e.removeHook = function(k) {
    if (B[k])
      return sl(B[k]);
  }, e.removeHooks = function(k) {
    B[k] && (B[k] = []);
  }, e.removeAllHooks = function() {
    B = {};
  }, e;
}
zl();
const {
  SvelteComponent: bs,
  append: W,
  assign: ws,
  attr: v,
  check_outros: Ts,
  create_component: an,
  destroy_component: rn,
  destroy_each: dl,
  detach: Fe,
  element: Pe,
  ensure_array_like: Ot,
  flush: Ae,
  get_spread_object: Es,
  get_spread_update: ys,
  group_outros: As,
  init: ks,
  insert: Ue,
  listen: Ye,
  mount_component: fn,
  run_all: cn,
  safe_not_equal: vs,
  set_data: zt,
  set_style: Ce,
  space: ke,
  svg_element: ve,
  text: bt,
  toggle_class: tt,
  transition_in: nt,
  transition_out: gt
} = window.__gradio__svelte__internal;
function ml(n, e, t) {
  const l = n.slice();
  return l[28] = e[t], l[30] = t, l;
}
function pl(n, e, t) {
  const l = n.slice();
  return l[31] = e[t], l[30] = t, l;
}
function hl(n) {
  let e, t;
  const l = [
    { autoscroll: (
      /*gradio*/
      n[0].autoscroll
    ) },
    { i18n: (
      /*gradio*/
      n[0].i18n
    ) },
    /*loading_status*/
    n[8]
  ];
  let i = {};
  for (let o = 0; o < l.length; o += 1)
    i = ws(i, l[o]);
  return e = new xo({ props: i }), e.$on(
    "clear_status",
    /*clear_status_handler*/
    n[17]
  ), {
    c() {
      an(e.$$.fragment);
    },
    m(o, s) {
      fn(e, o, s), t = !0;
    },
    p(o, s) {
      const c = s[0] & /*gradio, loading_status*/
      257 ? ys(l, [
        s[0] & /*gradio*/
        1 && { autoscroll: (
          /*gradio*/
          o[0].autoscroll
        ) },
        s[0] & /*gradio*/
        1 && { i18n: (
          /*gradio*/
          o[0].i18n
        ) },
        s[0] & /*loading_status*/
        256 && Es(
          /*loading_status*/
          o[8]
        )
      ]) : {};
      e.$set(c);
    },
    i(o) {
      t || (nt(e.$$.fragment, o), t = !0);
    },
    o(o) {
      gt(e.$$.fragment, o), t = !1;
    },
    d(o) {
      rn(e, o);
    }
  };
}
function Ss(n) {
  let e;
  return {
    c() {
      e = bt(
        /*label*/
        n[1]
      );
    },
    m(t, l) {
      Ue(t, e, l);
    },
    p(t, l) {
      l[0] & /*label*/
      2 && zt(
        e,
        /*label*/
        t[1]
      );
    },
    d(t) {
      t && Fe(e);
    }
  };
}
function gl(n) {
  let e, t, l, i, o = (
    /*directory*/
    n[31] + ""
  ), s, c, a;
  function r() {
    return (
      /*click_handler_1*/
      n[20](
        /*i*/
        n[30]
      )
    );
  }
  function u() {
    return (
      /*keypress_handler_1*/
      n[21](
        /*i*/
        n[30]
      )
    );
  }
  return {
    c() {
      e = Pe("div"), t = ve("svg"), l = ve("path"), i = ke(), s = bt(o), v(l, "d", "M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z"), v(l, "class", "svelte-179ly2y"), v(t, "aria-hidden", "true"), v(t, "focusable", "false"), v(t, "role", "img"), v(t, "class", "Octicon-sc-9kayk9-0 fczqEI svelte-179ly2y"), v(t, "viewBox", "0 0 16 16"), v(t, "width", "16"), v(t, "height", "16"), v(t, "fill", "currentColor"), Ce(t, "display", "inline-block"), Ce(t, "user-select", "none"), Ce(t, "vertical-align", "text-bottom"), Ce(t, "overflow", "visible"), v(e, "class", "inode_option svelte-179ly2y"), v(e, "role", "button"), v(e, "tabindex", "0");
    },
    m(d, w) {
      Ue(d, e, w), W(e, t), W(t, l), W(e, i), W(e, s), c || (a = [
        Ye(e, "click", r),
        Ye(e, "keypress", u)
      ], c = !0);
    },
    p(d, w) {
      n = d, w[0] & /*directories*/
      1024 && o !== (o = /*directory*/
      n[31] + "") && zt(s, o);
    },
    d(d) {
      d && Fe(e), c = !1, cn(a);
    }
  };
}
function bl(n) {
  let e, t, l, i, o = (
    /*filename*/
    n[28] + ""
  ), s, c, a, r;
  function u() {
    return (
      /*click_handler_2*/
      n[22](
        /*i*/
        n[30]
      )
    );
  }
  function d() {
    return (
      /*keypress_handler_2*/
      n[23](
        /*i*/
        n[30]
      )
    );
  }
  return {
    c() {
      e = Pe("div"), t = ve("svg"), l = ve("path"), i = ke(), s = bt(o), c = ke(), v(l, "d", "M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16h-9.5A1.75 1.75 0 0 1 2 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h9.5a.25.25 0 0 0 .25-.25V6h-2.75A1.75 1.75 0 0 1 9 4.25V1.5Zm6.75.062V4.25c0 .138.112.25.25.25h2.688l-.011-.013-2.914-2.914-.013-.011Z"), v(l, "class", "svelte-179ly2y"), v(t, "aria-hidden", "true"), v(t, "focusable", "false"), v(t, "role", "img"), v(t, "class", "color-fg-muted svelte-179ly2y"), v(t, "viewBox", "0 0 16 16"), v(t, "width", "16"), v(t, "height", "16"), v(t, "fill", "currentColor"), Ce(t, "display", "inline-block"), Ce(t, "user-select", "none"), Ce(t, "vertical-align", "text-bottom"), Ce(t, "overflow", "visible"), v(e, "class", "inode_option svelte-179ly2y"), v(e, "role", "button"), v(e, "tabindex", "0"), tt(
        e,
        "selected",
        /*selected_file_idx*/
        n[12] === /*i*/
        n[30]
      );
    },
    m(w, b) {
      Ue(w, e, b), W(e, t), W(t, l), W(e, i), W(e, s), W(e, c), a || (r = [
        Ye(e, "click", u),
        Ye(e, "keypress", d)
      ], a = !0);
    },
    p(w, b) {
      n = w, b[0] & /*files*/
      2048 && o !== (o = /*filename*/
      n[28] + "") && zt(s, o), b[0] & /*selected_file_idx*/
      4096 && tt(
        e,
        "selected",
        /*selected_file_idx*/
        n[12] === /*i*/
        n[30]
      );
    },
    d(w) {
      w && Fe(e), a = !1, cn(r);
    }
  };
}
function Ls(n) {
  let e, t, l, i, o, s, c, a, r, u, d, w, b, y, N, C, z, h, p, E, P, A, H, X, fe, D = (
    /*loading_status*/
    n[8] && hl(n)
  );
  t = new Yi({
    props: {
      show_label: (
        /*show_label*/
        n[5]
      ),
      info: void 0,
      $$slots: { default: [Ss] },
      $$scope: { ctx: n }
    }
  });
  let B = Ot(
    /*directories*/
    n[10]
  ), U = [];
  for (let _ = 0; _ < B.length; _ += 1)
    U[_] = gl(pl(n, B, _));
  let Q = Ot(
    /*files*/
    n[11]
  ), F = [];
  for (let _ = 0; _ < Q.length; _ += 1)
    F[_] = bl(ml(n, Q, _));
  return {
    c() {
      D && D.c(), e = ke(), an(t.$$.fragment), l = ke(), i = Pe("div"), o = Pe("div"), s = bt(
        /*full_path*/
        n[13]
      ), c = ke(), a = Pe("button"), r = Pe("div"), u = ve("svg"), d = ve("path"), w = ve("path"), b = ke(), y = ve("svg"), N = ve("circle"), C = ve("path"), z = bt(`
		Copy path`), h = ke(), p = Pe("div"), E = Pe("div"), E.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="16" height="16" style="display: inline; fill: white;" class="svelte-179ly2y"><polygon points="0 45, 45 10, 45 80" class="svelte-179ly2y"></polygon><polygon points="40 45, 85 10, 85 80" class="svelte-179ly2y"></polygon></svg>
				Up`, P = ke();
      for (let _ = 0; _ < U.length; _ += 1)
        U[_].c();
      A = ke();
      for (let _ = 0; _ < F.length; _ += 1)
        F[_].c();
      v(o, "class", "scroll-hide path_box svelte-179ly2y"), v(d, "class", "path1 svelte-179ly2y"), v(d, "d", "M5.75 4.75H10.25V1.75H5.75V4.75Z"), v(w, "class", "path2 svelte-179ly2y"), v(w, "d", "M3.25 2.88379C2.9511 3.05669 2.75 3.37987 2.75 3.75001V13.25C2.75 13.8023 3.19772 14.25 3.75 14.25H12.25C12.8023 14.25 13.25 13.8023 13.25 13.25V3.75001C13.25 3.37987 13.0489 3.05669 12.75 2.88379"), v(u, "class", "clippy_icon svelte-179ly2y"), v(u, "width", "16"), v(u, "height", "16"), v(u, "viewBox", "0 0 16 16"), tt(
        u,
        "copying",
        /*copying*/
        n[9]
      ), v(N, "cx", "8"), v(N, "cy", "8"), v(N, "r", "8"), Ce(N, "fill", "green"), Ce(N, "stroke-width", "0"), v(N, "class", "svelte-179ly2y"), v(C, "d", "M13.25 4.75L6 12L2.75 8.75"), v(C, "class", "svelte-179ly2y"), v(y, "class", "check_icon svelte-179ly2y"), v(y, "width", "16"), v(y, "height", "16"), v(y, "viewBox", "0 0 16 16"), tt(
        y,
        "copying",
        /*copying*/
        n[9]
      ), v(r, "class", "svelte-179ly2y"), v(a, "class", "submit_btn lg secondary svelte-cmf5ev svelte-179ly2y"), v(i, "class", "parent svelte-179ly2y"), v(E, "class", "inode_option svelte-179ly2y"), v(E, "role", "button"), v(E, "tabindex", "0"), v(p, "class", "inodes svelte-179ly2y");
    },
    m(_, O) {
      D && D.m(_, O), Ue(_, e, O), fn(t, _, O), Ue(_, l, O), Ue(_, i, O), W(i, o), W(o, s), W(i, c), W(i, a), W(a, r), W(r, u), W(u, d), W(u, w), W(r, b), W(r, y), W(y, N), W(y, C), W(a, z), Ue(_, h, O), Ue(_, p, O), W(p, E), W(p, P);
      for (let Y = 0; Y < U.length; Y += 1)
        U[Y] && U[Y].m(p, null);
      W(p, A);
      for (let Y = 0; Y < F.length; Y += 1)
        F[Y] && F[Y].m(p, null);
      H = !0, X || (fe = [
        Ye(
          a,
          "click",
          /*copy*/
          n[15]
        ),
        Ye(
          E,
          "click",
          /*click_handler*/
          n[18]
        ),
        Ye(
          E,
          "keypress",
          /*keypress_handler*/
          n[19]
        )
      ], X = !0);
    },
    p(_, O) {
      /*loading_status*/
      _[8] ? D ? (D.p(_, O), O[0] & /*loading_status*/
      256 && nt(D, 1)) : (D = hl(_), D.c(), nt(D, 1), D.m(e.parentNode, e)) : D && (As(), gt(D, 1, 1, () => {
        D = null;
      }), Ts());
      const Y = {};
      if (O[0] & /*show_label*/
      32 && (Y.show_label = /*show_label*/
      _[5]), O[0] & /*label*/
      2 | O[1] & /*$$scope*/
      4 && (Y.$$scope = { dirty: O, ctx: _ }), t.$set(Y), (!H || O[0] & /*full_path*/
      8192) && zt(
        s,
        /*full_path*/
        _[13]
      ), (!H || O[0] & /*copying*/
      512) && tt(
        u,
        "copying",
        /*copying*/
        _[9]
      ), (!H || O[0] & /*copying*/
      512) && tt(
        y,
        "copying",
        /*copying*/
        _[9]
      ), O[0] & /*click, directories*/
      17408) {
        B = Ot(
          /*directories*/
          _[10]
        );
        let I;
        for (I = 0; I < B.length; I += 1) {
          const be = pl(_, B, I);
          U[I] ? U[I].p(be, O) : (U[I] = gl(be), U[I].c(), U[I].m(p, A));
        }
        for (; I < U.length; I += 1)
          U[I].d(1);
        U.length = B.length;
      }
      if (O[0] & /*selected_file_idx, click, files*/
      22528) {
        Q = Ot(
          /*files*/
          _[11]
        );
        let I;
        for (I = 0; I < Q.length; I += 1) {
          const be = ml(_, Q, I);
          F[I] ? F[I].p(be, O) : (F[I] = bl(be), F[I].c(), F[I].m(p, null));
        }
        for (; I < F.length; I += 1)
          F[I].d(1);
        F.length = Q.length;
      }
    },
    i(_) {
      H || (nt(D), nt(t.$$.fragment, _), H = !0);
    },
    o(_) {
      gt(D), gt(t.$$.fragment, _), H = !1;
    },
    d(_) {
      _ && (Fe(e), Fe(l), Fe(i), Fe(h), Fe(p)), D && D.d(_), rn(t, _), dl(U, _), dl(F, _), X = !1, cn(fe);
    }
  };
}
function Cs(n) {
  let e, t;
  return e = new ri({
    props: {
      visible: (
        /*visible*/
        n[4]
      ),
      elem_id: (
        /*elem_id*/
        n[2]
      ),
      elem_classes: (
        /*elem_classes*/
        n[3]
      ),
      scale: (
        /*scale*/
        n[6]
      ),
      min_width: (
        /*min_width*/
        n[7]
      ),
      allow_overflow: !1,
      padding: !0,
      $$slots: { default: [Ls] },
      $$scope: { ctx: n }
    }
  }), {
    c() {
      an(e.$$.fragment);
    },
    m(l, i) {
      fn(e, l, i), t = !0;
    },
    p(l, i) {
      const o = {};
      i[0] & /*visible*/
      16 && (o.visible = /*visible*/
      l[4]), i[0] & /*elem_id*/
      4 && (o.elem_id = /*elem_id*/
      l[2]), i[0] & /*elem_classes*/
      8 && (o.elem_classes = /*elem_classes*/
      l[3]), i[0] & /*scale*/
      64 && (o.scale = /*scale*/
      l[6]), i[0] & /*min_width*/
      128 && (o.min_width = /*min_width*/
      l[7]), i[0] & /*files, selected_file_idx, directories, copying, full_path, show_label, label, gradio, loading_status*/
      16163 | i[1] & /*$$scope*/
      4 && (o.$$scope = { dirty: i, ctx: l }), e.$set(o);
    },
    i(l) {
      t || (nt(e.$$.fragment, l), t = !0);
    },
    o(l) {
      gt(e.$$.fragment, l), t = !1;
    },
    d(l) {
      rn(e, l);
    }
  };
}
function Rs(n, e, t) {
  let { gradio: l } = e, { label: i = "Path Selector" } = e, { elem_id: o = "" } = e, { elem_classes: s = [] } = e, { visible: c = !0 } = e, { value: a = "" } = e, { show_label: r } = e, { scale: u = null } = e, { min_width: d = void 0 } = e, { loading_status: w = void 0 } = e, b = !1, y = "", N = [], C = [], z = "/", h = -1, p = y;
  function E() {
    let _ = JSON.parse(a);
    _.status == "download" && (y = _.current_path, t(10, N = _.directories), t(11, C = _.files), z = _.separator, H());
  }
  function P(_, O) {
    if (O === "dict") {
      let Y = {
        selected_inode: _ === -1 ? -1 : N[_],
        current_path: y,
        status: "upload"
      };
      t(16, a = JSON.stringify(Y)), t(12, h = -1), l.dispatch("change");
    } else O === "file" && (h === _ ? t(12, h = -1) : t(12, h = _), H());
  }
  function A() {
    navigator.clipboard.writeText(p), b || (t(9, b = !0), setTimeout(
      () => {
        b && t(9, b = !1);
      },
      1e3
    ));
  }
  function H() {
    let _ = y;
    h != -1 && (_ = _ + z + C[h]), t(13, p = _);
  }
  const X = () => l.dispatch("clear_status", w), fe = () => P(-1, "dict"), D = () => P(-1, "dict"), B = (_) => P(_, "dict"), U = (_) => P(_, "dict"), Q = (_) => P(_, "file"), F = (_) => P(_, "file");
  return n.$$set = (_) => {
    "gradio" in _ && t(0, l = _.gradio), "label" in _ && t(1, i = _.label), "elem_id" in _ && t(2, o = _.elem_id), "elem_classes" in _ && t(3, s = _.elem_classes), "visible" in _ && t(4, c = _.visible), "value" in _ && t(16, a = _.value), "show_label" in _ && t(5, r = _.show_label), "scale" in _ && t(6, u = _.scale), "min_width" in _ && t(7, d = _.min_width), "loading_status" in _ && t(8, w = _.loading_status);
  }, n.$$.update = () => {
    n.$$.dirty[0] & /*value*/
    65536 && a === null && t(16, a = ""), n.$$.dirty[0] & /*value*/
    65536 && E();
  }, [
    l,
    i,
    o,
    s,
    c,
    r,
    u,
    d,
    w,
    b,
    N,
    C,
    h,
    p,
    P,
    A,
    a,
    X,
    fe,
    D,
    B,
    U,
    Q,
    F
  ];
}
class Ns extends bs {
  constructor(e) {
    super(), ks(
      this,
      e,
      Rs,
      Cs,
      vs,
      {
        gradio: 0,
        label: 1,
        elem_id: 2,
        elem_classes: 3,
        visible: 4,
        value: 16,
        show_label: 5,
        scale: 6,
        min_width: 7,
        loading_status: 8
      },
      null,
      [-1, -1]
    );
  }
  get gradio() {
    return this.$$.ctx[0];
  }
  set gradio(e) {
    this.$$set({ gradio: e }), Ae();
  }
  get label() {
    return this.$$.ctx[1];
  }
  set label(e) {
    this.$$set({ label: e }), Ae();
  }
  get elem_id() {
    return this.$$.ctx[2];
  }
  set elem_id(e) {
    this.$$set({ elem_id: e }), Ae();
  }
  get elem_classes() {
    return this.$$.ctx[3];
  }
  set elem_classes(e) {
    this.$$set({ elem_classes: e }), Ae();
  }
  get visible() {
    return this.$$.ctx[4];
  }
  set visible(e) {
    this.$$set({ visible: e }), Ae();
  }
  get value() {
    return this.$$.ctx[16];
  }
  set value(e) {
    this.$$set({ value: e }), Ae();
  }
  get show_label() {
    return this.$$.ctx[5];
  }
  set show_label(e) {
    this.$$set({ show_label: e }), Ae();
  }
  get scale() {
    return this.$$.ctx[6];
  }
  set scale(e) {
    this.$$set({ scale: e }), Ae();
  }
  get min_width() {
    return this.$$.ctx[7];
  }
  set min_width(e) {
    this.$$set({ min_width: e }), Ae();
  }
  get loading_status() {
    return this.$$.ctx[8];
  }
  set loading_status(e) {
    this.$$set({ loading_status: e }), Ae();
  }
}
export {
  Ns as default
};
