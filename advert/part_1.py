import manim as m
import numpy as np
 
 
# ── Helpers ─────────────────────────────────────────────────────────────────
 
def t(text, size=48, weight=m.BOLD, color=m.WHITE):
    return m.Text(text, font="Helvetica Neue", font_size=size,
                  color=color, weight=weight)
 
def cap(text, size=28, color="#CCCCCC"):
    return m.Text(text, font="Helvetica Neue", font_size=size, color=color)
 
def sm(text, size=20, color="#888888"):
    return m.Text(text, font="Helvetica Neue", font_size=size, color=color)
 
ACCENT      = "#0A84FF"
GLASS_FILL  = "#1C1C1E"
GLASS_EDGE  = "#3A3A3C"
GREEN       = "#32D74B"
RED         = "#FF453A"
GREY        = "#888888"
LIGHT       = "#CCCCCC"
 
 
def glass_card(width=5.5, height=2.8, corner=0.35):
    """Frosted-glass card: filled rounded rect + bright edge ring."""
    body = m.RoundedRectangle(
        width=width, height=height,
        corner_radius=corner,
        color=GLASS_EDGE, fill_color=GLASS_FILL,
        fill_opacity=0.85, stroke_width=1.5,
    )
    # Inner highlight — thin bright arc at the top edge (simulates glass sheen)
    sheen = m.RoundedRectangle(
        width=width - 0.12, height=height - 0.12,
        corner_radius=corner - 0.05,
        color="#FFFFFF", fill_opacity=0,
        stroke_width=0.6, stroke_opacity=0.25,
    ).move_to(body.get_center() + m.UP * 0.06)
    return m.VGroup(body, sheen)
 
 
class FirstScene(m.Scene):
    def construct(self):
 
        # ════════════════════════════════════════════════════════════════════
        # BEAT 1 — Three bad phrases, quick fire
        # ════════════════════════════════════════════════════════════════════
        for phrase in ["I'm busy.", "Whatever.", "Not my problem."]:
            txt = cap(phrase, color=RED).set_opacity(0)
            self.play(txt.animate.set_opacity(1), run_time=0.45)
            self.wait(0.5)
            self.play(txt.animate.set_opacity(0), run_time=0.3)
 
        # ════════════════════════════════════════════════════════════════════
        # BEAT 2 — Consequence line
        # ════════════════════════════════════════════════════════════════════
        line = cap("Words carry more weight than you think.")
        self.play(m.FadeIn(line, shift=m.UP * 0.15), run_time=0.7)
        self.wait(1.2)
        self.play(m.FadeOut(line), run_time=0.5)
 
        # ════════════════════════════════════════════════════════════════════
        # BEAT 3 — Name drop
        # ════════════════════════════════════════════════════════════════════
        name    = t("Conversation Manager.", size=50)
        tagline = sm("Say the right thing. Every time.").next_to(name, m.DOWN, buff=0.4)
        self.play(m.FadeIn(name, shift=m.UP * 0.12), run_time=0.8)
        self.play(m.FadeIn(tagline), run_time=0.6)
        self.wait(1.8)
        self.play(m.FadeOut(name, tagline), run_time=0.5)
 
        # ════════════════════════════════════════════════════════════════════
        # BEAT 4 — Before / After on glass cards
        # ════════════════════════════════════════════════════════════════════
        card_l = glass_card(5.2, 2.4).shift(m.LEFT * 3.2)
        card_r = glass_card(5.2, 2.4).shift(m.RIGHT * 3.2)
 
        lbl_b = sm("BEFORE", color=RED).next_to(card_l, m.UP, buff=0.18)
        lbl_a = sm("AFTER",  color=GREEN).next_to(card_r, m.UP, buff=0.18)
 
        txt_b = cap('"I\'m busy."', size=26, color=RED).move_to(card_l)
        txt_a = cap(
            '"My plate is full right now —\ncan we pick this up tomorrow?"',
            size=21, color=GREEN,
        ).move_to(card_r)
 
        self.play(
            m.FadeIn(card_l, shift=m.RIGHT * 0.1),
            m.FadeIn(card_r, shift=m.LEFT  * 0.1),
            m.FadeIn(lbl_b), m.FadeIn(lbl_a),
            run_time=0.8,
        )
        self.play(m.FadeIn(txt_b), run_time=0.5)
        self.wait(0.4)
 
        # Accent cursor sweeps card-to-card
        cursor = m.Dot(color=ACCENT, radius=0.09).move_to(card_l.get_right() + m.RIGHT * 0.1)
        self.play(m.FadeIn(cursor), run_time=0.2)
        self.play(cursor.animate.move_to(card_r.get_left() + m.LEFT * 0.1), run_time=0.55)
        self.play(m.FadeOut(cursor), run_time=0.15)
 
        self.play(m.FadeIn(txt_a, shift=m.LEFT * 0.08), run_time=0.6)
        self.wait(2)
 
        # ════════════════════════════════════════════════════════════════════
        # BEAT 5 — THE GLASS EXPLOSION
        # All current objects collapse into the center, then BURST out as
        # glass shards that morph into the app UI panels.
        # ════════════════════════════════════════════════════════════════════
        all_current = m.VGroup(card_l, card_r, lbl_b, lbl_a, txt_b, txt_a)
 
        # Collapse everything to a single bright point
        flash_dot = m.Dot(color=m.WHITE, radius=0.01).move_to(m.ORIGIN)
        self.play(
            all_current.animate.scale(0.05).move_to(m.ORIGIN).set_opacity(0.3),
            run_time=0.55, rate_func=m.utils.rate_functions.ease_in_cubic,
        )
        self.play(m.FadeIn(flash_dot), run_time=0.1)
 
        # FLASH — white screen burst
        flash = m.Rectangle(
            width=16, height=9, color=m.WHITE,
            fill_color=m.WHITE, fill_opacity=1, stroke_width=0,
        )
        self.add(flash)
        self.play(flash.animate.set_opacity(0), run_time=0.35)
        self.remove(flash)
        self.remove(flash_dot)
        m.Group(*[mob for mob in self.mobjects]).set_opacity(0)
        self.clear()
 
        # ── Shards burst outward ─────────────────────────────────────────
        # 8 glass shards flying from center to random directions
        rng = np.random.default_rng(42)
        shard_data = []
        for _ in range(8):
            angle  = rng.uniform(0, 2 * np.pi)
            dist   = rng.uniform(2.8, 4.5)
            dest   = dist * np.array([np.cos(angle), np.sin(angle), 0])
            width  = rng.uniform(0.5, 1.4)
            height = rng.uniform(0.3, 0.9)
            rot    = rng.uniform(-np.pi / 3, np.pi / 3)
            shard  = m.RoundedRectangle(
                width=width, height=height, corner_radius=0.1,
                color="#5E5CE6",
                fill_color="#1C1C2E", fill_opacity=0.7, stroke_width=1.2,
            ).move_to(m.ORIGIN)
            shard_data.append((shard, dest, rot))
            self.add(shard)
 
        self.play(
            *[
                m.AnimationGroup(
                    s.animate.move_to(d).rotate(r).set_opacity(0.6),
                )
                for s, d, r in shard_data
            ],
            run_time=0.7, rate_func=m.utils.rate_functions.ease_out_expo,
        )
 
        # Shards fade and drift further, lingering like glass settling
        self.play(
            *[s.animate.shift(
                np.array([np.cos(i), np.sin(i), 0]) * 0.4
            ).set_opacity(0)
              for i, (s, _, __) in enumerate(shard_data)],
            run_time=0.5,
        )
        self.clear()
 
        # ════════════════════════════════════════════════════════════════════
        # BEAT 6 — GUI panels materialise from glass shards
        # Three floating glass panels = the app UI
        # ════════════════════════════════════════════════════════════════════
        # Main window panel
        main_panel = glass_card(9.5, 5.8, corner=0.5).shift(m.ORIGIN)
 
        # Sidebar
        sidebar = glass_card(2.6, 5.0, corner=0.4).move_to(
            main_panel.get_left() + m.RIGHT * 1.5
        )
 
        # Top bar
        topbar = m.RoundedRectangle(
            width=9.5, height=0.55, corner_radius=0.27,
            color=GLASS_EDGE, fill_color="#2C2C2E",
            fill_opacity=0.95, stroke_width=1,
        ).move_to(main_panel.get_top() + m.DOWN * 0.37)
 
        # Traffic lights
        traffic = m.VGroup(*[
            m.Dot(radius=0.1, color=c).shift(m.LEFT * (0.45 - i * 0.32))
            for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"])
        ]).move_to(topbar.get_left() + m.RIGHT * 0.75)
 
        # Window title
        win_title = sm("Conversation Manager", size=16, color=LIGHT).move_to(topbar)
 
        # Fake content rows inside panel
        rows = m.VGroup(*[
            m.RoundedRectangle(
                width=5.8, height=0.38, corner_radius=0.19,
                color=GLASS_EDGE, fill_color="#2C2C2E",
                fill_opacity=0.8, stroke_width=0.8,
            ).shift(m.UP * (0.8 - i * 0.55) + m.RIGHT * 0.9)
            for i in range(5)
        ])
 
        # Sidebar profile dots
        profile_items = m.VGroup(*[
            m.VGroup(
                m.Dot(radius=0.18, color=ACCENT).shift(m.LEFT * 0.55),
                m.RoundedRectangle(
                    width=1.1, height=0.22, corner_radius=0.11,
                    color=GLASS_EDGE, fill_color="#3A3A3C",
                    fill_opacity=0.9, stroke_width=0,
                ).shift(m.RIGHT * 0.18),
            ).move_to(sidebar.get_center() + m.UP * (0.9 - i * 0.6))
            for i in range(4)
        ])
 
        ui_group = m.VGroup(main_panel, topbar, traffic, win_title,
                            rows, sidebar, profile_items)
 
        # Materialise — each piece condenses from a tiny point
        self.play(
            m.LaggedStart(
                m.GrowFromCenter(main_panel),
                m.GrowFromCenter(topbar),
                m.FadeIn(traffic),
                m.FadeIn(win_title),
                m.LaggedStart(*[m.GrowFromCenter(r) for r in rows], lag_ratio=0.08),
                m.GrowFromCenter(sidebar),
                m.LaggedStart(*[m.FadeIn(p) for p in profile_items], lag_ratio=0.1),
                lag_ratio=0.12,
            ),
            run_time=1.8,
        )
 
        # Subtle float — the whole UI breathes upward
        self.play(
            ui_group.animate.shift(m.UP * 0.08),
            run_time=1.2, rate_func=m.utils.rate_functions.ease_in_out_sine,
        )
        self.play(
            ui_group.animate.shift(m.DOWN * 0.08),
            run_time=1.2, rate_func=m.utils.rate_functions.ease_in_out_sine,
        )
 
        # Accent ring pulses around the panel (liquid glass halo)
        halo = m.RoundedRectangle(
            width=9.8, height=6.1, corner_radius=0.6,
            color=ACCENT, fill_opacity=0,
            stroke_width=1.5, stroke_opacity=0,
        )
        self.play(
            halo.animate.set_stroke(opacity=0.6).scale(1.04),
            run_time=0.5,
        )
        self.play(
            halo.animate.set_stroke(opacity=0).scale(1.03),
            run_time=0.5,
        )
        self.remove(halo)
        self.wait(1)
 
        # ════════════════════════════════════════════════════════════════════
        # BEAT 7 — Zoom out, name returns over the UI
        # ════════════════════════════════════════════════════════════════════
        self.play(
            ui_group.animate.scale(0.62).shift(m.DOWN * 0.5),
            run_time=0.9, rate_func=m.utils.rate_functions.ease_in_out_cubic,
        )
 
        final_name = t("Conversation Manager.", size=46).shift(m.UP * 2.9)
        final_sub  = sm("Know what to say.", size=22).next_to(final_name, m.DOWN, buff=0.3)
 
        self.play(m.FadeIn(final_name, shift=m.UP * 0.1), run_time=0.7)
        self.play(m.FadeIn(final_sub), run_time=0.5)
        self.wait(1.5)
 
        # Accent underline draws under the name
        ul = m.Line(
            final_name.get_left()  + m.DOWN * 0.32,
            final_name.get_right() + m.DOWN * 0.32,
            color=ACCENT, stroke_width=2,
        )
        self.play(m.Create(ul), run_time=0.7)
        self.wait(2.5)
 
        self.play(
            *[m.FadeOut(mob) for mob in self.mobjects],
            run_time=1.0,
        )