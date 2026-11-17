"""Generate the light and dark SVG figures for the "Work backwards from decode" post.

Usage: python3 scripts/work-backwards-diagrams.py   (writes public/<name>-{light,dark}.svg)
"""

from pathlib import Path

PUBLIC = Path(__file__).resolve().parent.parent / "public"

# GitHub-style palette shared with the other blog diagrams.
PALETTES = {
    "dark": dict(text="#e1e4e8", sub="#8b949e", faint="#6e7681", line="#30363d", grid="#21262d",
                 node="#0d1117", muted="#21262d", blue="#58a6ff", green="#3fb950",
                 amber="#d29922", amber_text="#d29922",
                 purple="#bc8cff", cyan="#39c5cf", orange="#f0883e"),
    "light": dict(text="#1f2328", sub="#656d76", faint="#8c959f", line="#d0d7de", grid="#eaeef2",
                  node="#ffffff", muted="#eaeef2", blue="#0969da", green="#1a7f37",
                  amber="#d29922", amber_text="#9a6700",
                  purple="#8250df", cyan="#1b7c83", orange="#bc4c00"),
}
SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


class Svg:
    def __init__(self, w, h, p):
        self.w, self.h, self.p, self.out = w, h, p, []

    def rect(self, x, y, w, h, stroke=None, fill="none", rx=6, sw=1.5, dash=None, fo=1, rot=None):
        s = self.p.get(stroke, stroke) or "none"
        f = self.p.get(fill, fill)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if rot:
            extra += f' transform="rotate({rot} {x + w / 2:.1f} {y + h / 2:.1f})"'
        self.out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                        f'fill="{f}" fill-opacity="{fo}" stroke="{s}" stroke-width="{sw}"{extra}/>')

    def text(self, x, y, s, size=12, color="text", anchor="start", weight=400, mono=False, rot=None):
        fam = MONO if mono else SANS
        extra = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
                        f'font-weight="{weight}" fill="{self.p[color]}" text-anchor="{anchor}"{extra}>{s}</text>')

    def path(self, d, color="sub", sw=1.5, dash=None, arrow=False):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if arrow:
            extra += f' marker-end="url(#a-{color})"'
        self.out.append(f'<path d="{d}" fill="none" stroke="{self.p[color]}" stroke-width="{sw}" '
                        f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    def padlock(self, x, y, color="sub"):
        self.rect(x, y + 5, 10, 8, stroke=color, rx=1.5, sw=1.3)
        self.path(f"M{x + 2} {y + 5} v-2 a3 3 0 0 1 6 0 v2", color=color, sw=1.3)

    def render(self, title):
        markers = "".join(
            f'<marker id="a-{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{self.p[c]}"/></marker>'
            for c in ("sub", "text", "blue", "amber", "green"))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img">'
                f'<title>{title}</title><defs>{markers}</defs>{"".join(self.out)}</svg>\n')


def kv_cache(p):
    s = Svg(720, 296, p)
    # Prefill panel
    s.rect(1, 1, 338, 294, stroke="blue", fill="blue", fo=0.04)
    s.text(20, 30, "PREFILL", 13, "blue", weight=700, mono=True)
    s.text(90, 30, "one parallel pass over the prompt", 12, "sub")
    s.text(20, 62, "prompt tokens  t1 … t40,000", 12, "sub", mono=True)
    for i in range(17):
        cached = i < 11
        s.rect(20 + i * 17.5, 72, 14, 18, stroke="blue" if cached else "line",
               fill="blue" if cached else "node", fo=0.35 if cached else 1, rx=2.5, sw=1)
    s.path("M20 98 v4 h187 v-4", color="blue", sw=1)
    s.text(113, 116, "cached prefix: nearly free", 11, "blue", anchor="middle")
    s.path("M170 126 V160", color="sub", arrow=True)
    s.text(182, 147, "all at once", 12, "sub")
    s.rect(20, 166, 300, 44, stroke="blue", fill="blue", fo=0.12)
    s.text(170, 193, "KV cache: keys + values for t1 … t40K", 12.5, "text", anchor="middle")
    s.text(20, 270, "cost: fast per token", 12.5, "green", mono=True, weight=600)

    # Decode panel
    x0 = 370
    s.rect(x0 + 1, 1, 348, 294, stroke="amber", fill="amber", fo=0.04)
    s.text(x0 + 20, 30, "DECODE", 13, "amber_text", weight=700, mono=True)
    s.text(x0 + 82, 30, "one token per pass", 12, "sub")
    s.text(x0 + 20, 62, "the cache grows one entry per step", 12, "sub")
    s.rect(x0 + 20, 72, 196, 28, stroke="blue", fill="blue", fo=0.12, rx=4)
    s.text(x0 + 118, 91, "K,V  t1 … t40K", 12, "text", anchor="middle", mono=True)
    for i in range(3):
        s.rect(x0 + 220 + i * 32, 72, 28, 28, stroke="amber", fill="amber", fo=0.18, rx=4)
        s.text(x0 + 234 + i * 32, 91, "+1", 11, "amber_text", anchor="middle", mono=True)
    s.text(x0 + 318, 91, "…", 13, "sub", anchor="middle")
    labels = ["tok 1", "tok 2", "tok 3", "…", "tok N"]
    for i, lab in enumerate(labels):
        x = x0 + 20 + i * 64
        s.rect(x, 150, 52, 28, stroke="line" if lab == "…" else "amber", fill="node", rx=4)
        s.text(x + 26, 168, lab, 11.5, "text", anchor="middle", mono=True)
        if lab != "…":
            s.path(f"M{x + 26} 148 V106", color="sub", sw=1.2, dash="3 3", arrow=True)
        if i < len(labels) - 1:
            s.path(f"M{x + 54} 164 H{x + 62}", color="amber", sw=1.5, arrow=True)
    s.text(x0 + 20, 206, "each step reads the weights + the whole cache", 12, "sub")
    s.text(x0 + 20, 224, "inter-token latency (ITL): ~6 to 9 ms per token,", 12, "sub")
    s.text(x0 + 20, 242, "every token, in order", 12, "sub")
    s.text(x0 + 20, 270, "cost: N tokens × ITL = the wall clock", 12.5, "amber_text", mono=True, weight=600)
    return s.render("Prefill vs decode")


def app_layers(p):
    s = Svg(720, 252, p)

    def constant(x, title, items):
        s.rect(x + 1, 22, 148, 228, stroke="line", fill="muted", fo=0.6)
        s.padlock(x + 16, 46)
        s.text(x + 34, 58, title, 12, "text", weight=700, mono=True)
        s.text(x + 16, 78, "constant", 11, "sub", mono=True)
        for i, it in enumerate(items):
            s.text(x + 16, 112 + i * 24, it, 12.5, "sub")

    constant(0, "AI INFERENCE", ["model", "tokens / sec", "ITL", "KV cache"])
    s.path("M154 136 H176", color="sub", arrow=True)
    constant(180, "HARNESS", ["how agents launch", "memory limits", "process limits"])
    s.path("M334 136 H356", color="sub", arrow=True)

    x0 = 360
    s.rect(x0 + 1, 22, 358, 228, stroke="blue", fill="blue", fo=0.06, sw=2)
    s.text(x0 + 18, 58, "BUILDING BLOCKS", 12, "blue", weight=700, mono=True)
    s.text(x0 + 18, 78, "ours", 11, "sub", mono=True)
    rows = [[("prompt instructions", -2), ("step graph", 1.5)],
            [("sub-agents", -1), ("script checks", 1), ("templates", -1.5)],
            [("model per role", 2), ("reasoning effort per step", -1)]]
    for r, row in enumerate(rows):
        x, y = x0 + 18, 96 + r * 36
        for label, rot in row:
            w = len(label) * 6.6 + 22
            s.rect(x, y, w, 24, stroke="blue", fill="node", rx=5, sw=1.3, rot=rot)
            s.text(x + w / 2, y + 16, label, 12, "text", anchor="middle", rot=rot)
            x += w + 12
    s.text(x0 + 180, 228, "re-design · re-arrange · re-fit · re-write", 12, "blue", anchor="middle", mono=True)
    return s.render("The application layer we own")


# Illustrative minutes, same work in both schedules: (step, bar color, batches span, graph span)
STEPS = [("research", "blue", (0, 8), (0, 8)),
         ("main draft", "purple", (13, 23), (8, 18)),
         ("section A", "amber", (23, 27), (18, 22)),
         ("review", "green", (23, 31), (18, 26)),
         ("analysis", "cyan", (0, 13), (0, 13)),
         ("section B", "orange", (23, 29), (13, 19))]


def batches_vs_graph(p):
    s = Svg(720, 420, p)
    lx, x1, x2 = 104, 116, 692
    X = lambda m: x1 + (x2 - x1) * m / 32
    RH, GAP = 16, 6

    def chart(y0, title, note, which):
        s.text(0, y0, title, 12.5, "text", weight=700, mono=True)
        s.text(len(title) * 7.8 + 8, y0, note, 12, "sub")
        top = y0 + 26
        bottom = top + len(STEPS) * (RH + GAP) - GAP
        for m in range(0, 31, 5):
            s.path(f"M{X(m):.1f} {top - 4} V{bottom + 4}", color="grid", sw=1)
            s.text(X(m), bottom + 18, str(m), 10.5, "faint", anchor="middle", mono=True)
        rowy = {}
        for i, (name, color, bspan, gspan) in enumerate(STEPS):
            y = top + i * (RH + GAP)
            rowy[name] = y
            a, b = bspan if which == "b" else gspan
            s.text(lx, y + 12, name, 12, "sub", anchor="end")
            s.rect(X(a), y, X(b) - X(a), RH, stroke=color, fill=color, fo=0.3, rx=3, sw=1.2)
            if which == "b":
                end = {0: 13, 13: 23, 23: 31}[bspan[0]]
                if b < end:  # idle: finished early, waiting for the slowest member
                    s.rect(X(b), y + 3, X(end) - X(b), RH - 6, stroke="faint", fill="none", rx=2, sw=1, dash="3 3")
        if which == "b":
            for m, lab in ((0, "batch 1"), (13, "batch 2"), (23, "batch 3")):
                s.text(X(m) + 4, top - 8, lab, 10.5, "faint", mono=True)
            for m in (13, 23):
                s.path(f"M{X(m):.1f} {top - 18} V{bottom + 4}", color="text", sw=1.5, dash="5 4")
            done = 31
        else:
            for src, dsts, m in (("research", ["main draft"], 8), ("main draft", ["section A", "review"], 18),
                                 ("analysis", ["section B"], 13)):
                tx = X(m) - 7
                last = rowy[dsts[-1]] + RH / 2
                s.path(f"M{tx:.1f} {rowy[src] + RH} V{last}", color="text", sw=1.2)
                for d in dsts:
                    s.path(f"M{tx:.1f} {rowy[d] + RH / 2} H{X(m) - 1:.1f}", color="text", sw=1.2, arrow=True)
            done = 26
            s.path(f"M{X(31):.1f} {top - 4} V{bottom + 4}", color="faint", sw=1.2, dash="3 3")
            s.path(f"M{X(30.6):.1f} {top + 2 * (RH + GAP) + 8} H{X(26.4):.1f}", color="green", sw=1.5, arrow=True)
            s.text(X(28.3), top + 2 * (RH + GAP) + 2, "5 min sooner", 11, "green", anchor="middle", weight=600)
        s.path(f"M{X(done):.1f} {top - 4} V{bottom + 4}", color="green", sw=2)
        s.text(X(done) - 6, top - 8, f"done {done}", 11, "green", anchor="end", weight=700, mono=True)

    chart(14, "BATCHES", "each batch waits for its slowest member", "b")
    chart(222, "DEPENDENCY GRAPH", "each step starts when its inputs are ready", "g")
    s.text(x2, 416, "minutes (illustrative)", 10.5, "faint", anchor="end", mono=True)
    return s.render("Batches vs a dependency graph")


RUNS = [("Baseline", "", 31.3, 97), ("B", "lower effort", 24.7, 98), ("C", "newer model", 17.1, 97),
        ("D", "restructured", 15.2, 97), ("E", "D, run again", 18.1, 98), ("F", "D, older model", 17.4, 97)]


def knob_chart(p):
    s = Svg(720, 296, p)
    x1, x2 = 150, 600
    X = lambda m: x1 + (x2 - x1) * m / 35
    RH, GAP, top = 22, 12, 40
    s.text(0, 16, "MINUTES PER RUN", 12, "text", weight=700, mono=True)
    s.text(124, 16, "one test project · quality score at the end of each bar", 12, "sub")
    bottom = top + len(RUNS) * (RH + GAP) - GAP
    for m in range(0, 36, 5):
        s.path(f"M{X(m):.1f} {top - 6} V{bottom + 6}", color="grid", sw=1)
        s.text(X(m), bottom + 22, str(m), 10.5, "faint", anchor="middle", mono=True)
    # run-to-run noise: D and E are the same setup
    yd = top + 3 * (RH + GAP)
    mid = (15.2 + 18.1) / 2
    s.rect(X(mid - 1.5), yd - 6, X(mid + 1.5) - X(mid - 1.5), 2 * RH + GAP + 12,
           stroke="amber", fill="amber", fo=0.12, rx=3, sw=1, dash="3 3")
    for i, (run, what, mins, score) in enumerate(RUNS):
        y = top + i * (RH + GAP)
        s.text(x1 - 12, y + 15, f"{run} · {what}" if what else run, 12, "sub", anchor="end")
        color = "faint" if run == "Baseline" else "blue"
        s.rect(x1, y, X(mins) - x1, RH, stroke=color, fill=color, fo=0.35 if run == "Baseline" else 0.3, rx=3, sw=1.2)
        lx = max(X(mins), X(mid + 1.5) if run in "DE" else 0) + 8
        s.text(lx, y + 15, f"{mins}", 12.5, "text", weight=700, mono=True)
        s.text(lx + 40, y + 15, f"score {score}", 11.5, "sub", mono=True)
    s.text(X(mid + 1.5) + 134, yd + RH + 4, "± 1.5 min", 11.5, "amber_text", weight=600, mono=True)
    s.text(X(mid + 1.5) + 134, yd + RH + 20, "run-to-run noise", 11, "amber_text")
    s.text(x2, bottom + 40, "minutes", 10.5, "faint", anchor="end", mono=True)
    return s.render("Minutes per run on one test project")


if __name__ == "__main__":
    for name, fn in (("kv-cache", kv_cache), ("app-layers", app_layers),
                     ("batches-vs-graph", batches_vs_graph), ("knob-chart", knob_chart)):
        for theme, pal in PALETTES.items():
            (PUBLIC / f"{name}-{theme}.svg").write_text(fn(pal))
            print(f"wrote public/{name}-{theme}.svg")
