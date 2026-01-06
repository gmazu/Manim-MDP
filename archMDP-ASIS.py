from pathlib import Path

import yaml
from manim import *


def load_timeline_config(path: Path = Path("cronos.yaml")) -> dict:
    if not path.exists():
        return {
            "labels": ["Ene 2024", "Mar 2024", "Nov 2025", "Dic 2025", "Ene 2026"],
            "titles": [
                "Creando Escenario",
                "Timeout F5",
                "Bypass Apache",
                "Falla Apache L1",
                "RollBack F5",
            ],
            "details": ["", "", "", "", ""],
        }
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    timeline = data.get("timeline") or {}
    milestones = timeline.get("milestones") or []
    if len(milestones) < 2:
        raise ValueError("cronos.yaml: se requieren minimo 2 hitos en timeline.milestones")
    if len(milestones) > 6:
        print("cronos.yaml: se paso el maximo de 6 hitos, se usaran solo los primeros 6.")
        milestones = milestones[:6]
    labels = [str(item.get("label") or "") for item in milestones]
    titles = [str(item.get("title") or "") for item in milestones]
    details = [str(item.get("detail") or "") for item in milestones]
    duration_seconds = timeline.get("duration_seconds") or 77
    return {
        "labels": labels,
        "titles": titles,
        "details": details,
        "duration_seconds": duration_seconds,
    }

def load_visual_config(path: Path = Path("archMDP-ASIS.yaml")) -> dict:
    defaults = {
        "base_line": {
            "width": 1.0,
            "opacity": 0.07,
        },
        "trail": {
            "width": 2.0,
            "opacity": 0.75,
            "fade_time": 3.2,
            "linger_time": 0.6,
        },
        "trail_stuck": {
            "fade_time": 0.4,
            "linger_time": 0.2,
        },
    }
    if not path.exists():
        return defaults
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    config = defaults | data
    config["base_line"] = defaults["base_line"] | (data.get("base_line") or {})
    config["trail"] = defaults["trail"] | (data.get("trail") or {})
    config["trail_stuck"] = defaults["trail_stuck"] | (data.get("trail_stuck") or {})
    return config


def label_to_month_index(label: str) -> int | None:
    parts = label.strip().split()
    if len(parts) < 2:
        return None
    month_key = parts[0][:3].lower()
    try:
        year = int(parts[1])
    except ValueError:
        return None
    months = {
        "ene": 1,
        "feb": 2,
        "mar": 3,
        "abr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "ago": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dic": 12,
    }
    month = months.get(month_key)
    if not month:
        return None
    return year * 12 + month

class ArquitecturaMDPLBTR(Scene):
    def construct(self):
        timeline_config = load_timeline_config()
        titles = timeline_config.get("titles") or []
        details = timeline_config.get("details") or []
        duration_seconds = float(timeline_config.get("duration_seconds") or 77)
        def title_text(idx: int, fallback: str) -> str:
            return titles[idx] if idx < len(titles) and titles[idx] else fallback
        def detail_text(idx: int) -> str:
            return details[idx] if idx < len(details) else ""

        visual_config = load_visual_config()
        base_line_cfg = visual_config.get("base_line") or {}
        trail_cfg = visual_config.get("trail") or {}
        trail_stuck_cfg = visual_config.get("trail_stuck") or {}

        title = Text("Arquitectura Motor de Pagos LBTR - ASIS - 2025", font_size=40).to_edge(UP)
        default_subtitle = "Arquitectura sin HA\ndesde marzo 2024\n hasta enero 2025\naproximadamente."
        signature = Text("by eCORE - PNLöP v³ & Manim v0.19.1", font_size=9)
        version_document = Text("versión v2.2.13", font_size=9)
        footer = VGroup(signature, version_document).arrange(RIGHT, buff=0.3)
        footer.next_to(title, DOWN, aligned_edge=RIGHT, buff=0.1)
        self.play(Write(title), FadeIn(footer))

        # Timeline de hitos (alineada con la firma)
        timeline_line = Line(LEFT, RIGHT).set_width(footer.width)
        timeline_line.set_stroke(color=WHITE, width=2, opacity=0.25)
        label_indexes = [label_to_month_index(label) for label in timeline_config["labels"]]
        if all(idx is not None for idx in label_indexes):
            min_idx = min(label_indexes)
            max_idx = max(label_indexes)
            denom = max(1, max_idx - min_idx)
            timeline_positions = [(idx - min_idx) / denom for idx in label_indexes]
        else:
            timeline_positions = [i / max(1, len(timeline_config["labels"]) - 1) for i in range(len(timeline_config["labels"]))]
        timeline_labels = [Text(label, font_size=7) for label in timeline_config["labels"]]
        timeline_dots = [Dot(radius=0.04, color=WHITE) for _ in timeline_positions]
        for idx, (dot, label, pos) in enumerate(zip(timeline_dots, timeline_labels, timeline_positions)):
            dot.move_to(timeline_line.point_from_proportion(pos))
            direction = UP if idx % 2 == 0 else DOWN
            angle = PI / 4 if idx % 2 == 0 else -PI / 4
            label.next_to(dot, direction, buff=0.3)
            label.rotate(angle, about_point=dot.get_center())
            label.shift(RIGHT * (dot.get_center()[0] - label.get_left()[0]))
        start_index = 1 if len(timeline_positions) > 1 else 0
        marker_progress = ValueTracker(
            timeline_positions[start_index] if timeline_positions else 0.0
        )
        def progress_line(length: float, color, width: float, opacity: float):
            line = Line(timeline_line.get_start(), timeline_line.get_end())
            line.set_stroke(color=color, width=width, opacity=opacity)
            line.set_length(length)
            line.align_to(timeline_line, LEFT)
            return line

        progress_track = always_redraw(
            lambda: VGroup(
                progress_line(
                    timeline_line.get_length() * marker_progress.get_value(),
                    GREEN,
                    6,
                    0.08,
                ),
                progress_line(
                    timeline_line.get_length() * marker_progress.get_value(),
                    GREEN,
                    4,
                    0.18,
                ),
                progress_line(
                    timeline_line.get_length() * marker_progress.get_value(),
                    GREEN,
                    2.4,
                    0.8,
                ),
            )
        )

        timeline_group = VGroup(timeline_line, progress_track, *timeline_dots, *timeline_labels)
        timeline_group.to_corner(DR).shift(DOWN * 0.2 + LEFT * 0.1)
        current_index_value = [start_index]
        def current_index() -> int:
            return current_index_value[0]
        timeline_marker = always_redraw(
            lambda: Dot(radius=0.05, color=GREEN).move_to(
                timeline_line.point_from_proportion(marker_progress.get_value())
            )
        )
        subtitle = always_redraw(
            lambda: Text(
                detail_text(current_index()) or default_subtitle,
                font_size=9,
            ).next_to(title, DOWN, aligned_edge=LEFT, buff=0.1)
        )
        timeline_event = always_redraw(
            lambda: Text(
                title_text(current_index(), "Creando Escenario"),
                font_size=14,
            ).next_to(timeline_group, UP, buff=0.14)
        )
        def move_timeline_to(index: int, run_time: float = 2.0):
            if not timeline_positions:
                return
            target = max(0, min(index, len(timeline_positions) - 1))
            current_index_value[0] = target
            self.play(
                marker_progress.animate.set_value(timeline_positions[target]),
                run_time=run_time,
            )
        self.play(FadeIn(timeline_group), FadeIn(timeline_marker), FadeIn(subtitle))
        self.play(FadeIn(timeline_event), run_time=0.6)

        def base_line(start, end):
            return Line(start, end).set_stroke(
                color=WHITE,
                width=base_line_cfg.get("width", 1.0),
                opacity=base_line_cfg.get("opacity", 0.07),
            )

        def move_with_trail(
            route,
            dot,
            move_time: float,
            fade_time: float | None = None,
            linger_time: float | None = None,
        ):
            fade_time = trail_cfg.get("fade_time", 3.2) if fade_time is None else fade_time
            linger_time = trail_cfg.get("linger_time", 0.6) if linger_time is None else linger_time
            path = VMobject()
            path.set_points_as_corners(route)
            trail = VMobject()
            trail.set_points_as_corners(route)
            trail.set_stroke(
                color=WHITE,
                width=trail_cfg.get("width", 2.0),
                opacity=trail_cfg.get("opacity", 0.75),
            )
            return Succession(
                AnimationGroup(
                    MoveAlongPath(dot, path, rate_func=linear, run_time=move_time),
                    Create(trail, rate_func=linear, run_time=move_time),
                ),
                Wait(linger_time),
                FadeOut(trail, run_time=fade_time, rate_func=linear),
            )

        # Columnas: MDP → F5 → OSBs → Tuxedos → Tandem

        # MDP
        mdp = Circle(radius=0.5, color=BLUE).move_to(LEFT * 6)
        mdp_label = Text("MDP", font_size=24).next_to(mdp, DOWN)

        # F5
        f5 = Circle(radius=0.5, color=GREEN).move_to(LEFT * 3)
        f5_label = Text("F5", font_size=24).next_to(f5, DOWN)

        # OSBs (4 Morandé + 4 Longovilo)
        osb_nodes = []
        osb_labels = []
        for i in range(4):
            node = Circle(radius=0.2, color=YELLOW).move_to(RIGHT * 0 + UP * (2.5 - i * 0.8))
            label = Text(f"OSB M{i+1}", font_size=12).next_to(node, DOWN, buff=0.1)
            osb_nodes.append(node)
            osb_labels.append(label)
        for i in range(4):
            node = Circle(radius=0.2, color=ORANGE).move_to(RIGHT * 0 + DOWN * (i * 0.8 + 1))
            label = Text(f"OSB L{i+1}", font_size=12).next_to(node, DOWN, buff=0.1)
            osb_nodes.append(node)
            osb_labels.append(label)

        # Tuxedos
        tux1 = Circle(radius=0.5, color=PURPLE).move_to(RIGHT * 3 + UP * 0.8)
        tux2 = Circle(radius=0.5, color=ORANGE).move_to(RIGHT * 3 + DOWN * 0.8)
        tux_labels = [Text("Tux A", font_size=20).next_to(tux1, DOWN),
                      Text("Tux L", font_size=20).next_to(tux2, DOWN)]

        # Tandem
        tan1 = Circle(radius=0.5, color=PURPLE).move_to(RIGHT * 6 + UP * 0.8)
        tan2 = Circle(radius=0.5, color=GRAY).move_to(RIGHT * 6 + DOWN * 0.8)
        tan_labels = [Text("Tandem A", font_size=20).next_to(tan1, DOWN),
                      Text("Tandem L", font_size=20).next_to(tan2, DOWN)]

        # Animar aparición
        self.play(FadeIn(mdp), Write(mdp_label))
        self.wait(0.3)
        self.play(FadeIn(f5), Write(f5_label))
        self.wait(0.3)
        self.play(*[FadeIn(node) for node in osb_nodes], *[Write(label) for label in osb_labels])
        self.wait(0.2)
        self.play(FadeIn(tux1), FadeIn(tux2), Write(tux_labels[0]), Write(tux_labels[1]))
        self.wait(0.3)
        self.play(FadeIn(tan1), FadeIn(tan2), Write(tan_labels[0]), Write(tan_labels[1]))

        # Leyenda de datacenter por color (esquina inferior izquierda)
        legend_items = [
            VGroup(Dot(color=YELLOW, radius=0.06), Text("Morande", font_size=10)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=ORANGE, radius=0.06), Text("Longovilo", font_size=10)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=PURPLE, radius=0.06), Text("Aconcagua", font_size=10)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=GRAY, radius=0.06), Text("Inactivo", font_size=10)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=WHITE, radius=0.06), Text("Intento de Pago", font_size=10)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=RED, radius=0.06), Text("Pago Timeout", font_size=10)).arrange(RIGHT, buff=0.15),
            VGroup(Dot(color=GREEN, radius=0.06), Text("Pago Exitoso", font_size=10)).arrange(RIGHT, buff=0.15),



        ]
        legend = VGroup(*legend_items).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(DL).shift(RIGHT * 0.2 + UP * 0.2)
        self.play(FadeIn(legend))

        # Conexiones
        line_mdp_f5 = base_line(mdp.get_right(), f5.get_left())
        self.play(Create(line_mdp_f5))
        lines_f5_osb = []
        lines_osb_tux1 = []
        lines_osb_tux2 = []
        for osb in osb_nodes:
            lfo = base_line(f5.get_right(), osb.get_left())
            lines_f5_osb.append(lfo)
            self.play(Create(lfo), run_time=0.2)
        for osb in osb_nodes:
            l1 = base_line(osb.get_right(), tux1.get_left())
            l2 = base_line(osb.get_right(), tux2.get_left())
            lines_osb_tux1.append(l1)
            lines_osb_tux2.append(l2)
            self.play(Create(l1), run_time=0.2)
            self.play(Create(l2), run_time=0.2)
        lines_tux_tan = [
            base_line(tux1.get_right(), tan1.get_left()),
            base_line(tux2.get_right(), tan1.get_left()),
        ]
        self.play(Create(lines_tux_tan[0]), Create(lines_tux_tan[1]))

        # Simulación de transacciones: 16 bolitas, la 4ª, 8ª, 12ª y última quedan atascadas en F5
        travel_routes = []
        for osb in osb_nodes:
            travel_routes.append([
                mdp.get_right(),
                f5.get_left(), f5.get_right(),
                osb.get_left(), osb.get_right(),
                tux1.get_left(), tux1.get_right(),
                tan1.get_left(),
            ])
            travel_routes.append([
                mdp.get_right(),
                f5.get_left(), f5.get_right(),
                osb.get_left(), osb.get_right(),
                tux2.get_left(), tux2.get_right(),
                tan1.get_left(),
            ])

        stuck_indices = [3, 7, 11, 15]  # 4ª, 8ª, 12ª y última (0-based)
        stuck_offsets = [
            UP * 0.12 + LEFT * 0.05,
            DOWN * 0.12 + RIGHT * 0.05,
            UP * 0.05 + RIGHT * 0.12,
            DOWN * 0.18 + LEFT * 0.12,
        ]

        travel_dots = []
        stuck_dots = []
        delivered_dots = []
        animations = []
        for i, route in enumerate(travel_routes):
            dot = Dot(color=WHITE, radius=0.06)
            self.add(dot)
            if i in stuck_indices:
                offset = stuck_offsets[len(stuck_dots) % len(stuck_offsets)]
                stuck_route = [mdp.get_right(), f5.get_center() + offset]
                animations.append(move_with_trail(
                    stuck_route,
                    dot,
                    move_time=0.6,
                    fade_time=trail_stuck_cfg.get("fade_time", 0.4),
                    linger_time=trail_stuck_cfg.get("linger_time", 0.2),
                ))
                stuck_dots.append(dot)
            else:
                animations.append(move_with_trail(route, dot, move_time=2.0))
                delivered_dots.append(dot)
            travel_dots.append(dot)

        # Lag suave para que se perciban secuenciales sin saturar
        self.play(LaggedStart(*animations, lag_ratio=0.08))

        # Las que llegan a Tandem se quedan verdes y se posicionan sobre Tandem A
        self.play(*[dot.animate.set_color(GREEN) for dot in delivered_dots], run_time=1.0)
        tandem_offsets = [
            UP * 0.1 + LEFT * 0.05,
            DOWN * 0.1 + RIGHT * 0.05,
            UP * 0.05 + RIGHT * 0.1,
            DOWN * 0.15 + LEFT * 0.1,
            ORIGIN,
        ]
        self.play(*[
            dot.animate.move_to(tan1.get_center() + tandem_offsets[i % len(tandem_offsets)])
            for i, dot in enumerate(delivered_dots)
        ], run_time=0.6)

        # Cambio de color de las atascadas: espera 1s, luego rojo y gris
        self.wait(1.0)
        self.play(*[dot.animate.set_color(RED) for dot in stuck_dots], run_time=1.0)

        # Línea desde la leyenda "Pago Timeout" al centro de F5 (más delgada)
        timeout_source = legend[5]  # VGroup(Dot rojo + texto Pago Timeout)
        timeout_line = Line(timeout_source.get_right(), f5.get_center(), color=RED, stroke_width=1.5)
        self.play(Create(timeout_line))
        self.wait(3)
        self.play(FadeOut(timeout_line))

        success_source = legend[6]  # VGroup(Dot verde + texto Pago Existoso)
        success_line = Line(success_source.get_right(), tan1.get_center(), color=GREEN, stroke_width=1.5)
        self.play(Create(success_line))
        self.wait(3)
        self.play(FadeOut(success_line))


        self.play(*[dot.animate.set_color(GRAY) for dot in stuck_dots], run_time=1.0)
        tandem_offsets = [
            UP*0.1+LEFT*0.05, DOWN*0.1+RIGHT*0.05,
            UP*0.05+RIGHT*0.1, DOWN*0.15+LEFT*0.1,
            ORIGIN
        ]
        self.play(*[
            dot.animate.move_to(tan1.get_center() + tandem_offsets[i % len(tandem_offsets)])
            for i, dot in enumerate(delivered_dots)
        ], run_time=0.6)

        move_timeline_to(2, run_time=2.0)
        next_event = Text(title_text(2, "Bypass Apache"), font_size=14).next_to(timeline_group, UP, buff=0.14)
        next_subtitle = Text(detail_text(2) or default_subtitle, font_size=9).next_to(title, DOWN, aligned_edge=LEFT, buff=0.1)
        self.play(FadeOut(timeline_event), FadeIn(next_event), run_time=0.8)
        self.play(Transform(subtitle, next_subtitle), run_time=0.4)
        timeline_event = next_event

        # Al ocurrir los timeouts, desconectar todas las líneas previas
        self.play(
            FadeOut(line_mdp_f5),
            *[FadeOut(l) for l in lines_f5_osb],
            *[FadeOut(l) for l in lines_osb_tux1],
            *[FadeOut(l) for l in lines_osb_tux2],
            *[FadeOut(l) for l in lines_tux_tan],
        )

        # Apache proxies en la columna de F5 (se muestran al final, tras las bolitas)
        apache_m1 = Circle(radius=0.3, color=YELLOW).move_to(LEFT * 3 + UP * 1.4)
        apache_m1_label = Text("Apache Proxy M1", font_size=14).next_to(apache_m1, UP, buff=0.1)
        apache_l1 = Circle(radius=0.3, color=ORANGE).move_to(LEFT * 3 + DOWN * 1.8)
        apache_l1_label = Text("Apache Proxy L1", font_size=14).next_to(apache_l1, DOWN, buff=0.1)
        self.play(FadeIn(apache_m1), Write(apache_m1_label),
                  FadeIn(apache_l1), Write(apache_l1_label))

        # Nuevas líneas: MDP → Apache L1 → OSB L1 → Tux A/L → Tandem A
        line_mdp_apache_l1 = base_line(mdp.get_right(), apache_l1.get_left())
        line_apache_l1_osb_l1 = base_line(apache_l1.get_right(), osb_nodes[4].get_left())
        line_osb_l1_tux1 = base_line(osb_nodes[4].get_right(), tux1.get_left())
        line_osb_l1_tux2 = base_line(osb_nodes[4].get_right(), tux2.get_left())
        line_tux1_tan1_new = base_line(tux1.get_right(), tan1.get_left())
        line_tux2_tan1_new = base_line(tux2.get_right(), tan1.get_left())

        # Crear de izquierda a derecha (secuencial) como la primera fase
        self.play(Create(line_mdp_apache_l1), run_time=0.3)
        self.play(Create(line_apache_l1_osb_l1), run_time=0.3)
        self.play(Create(line_osb_l1_tux1), run_time=0.25)
        self.play(Create(line_osb_l1_tux2), run_time=0.25)
        self.play(Create(line_tux1_tan1_new), Create(line_tux2_tan1_new), run_time=0.3)

        # Nuevas transacciones (16) todas pasando por Apache L1 → OSB L1 → Tux A/L → Tandem A
        apache_routes = []
        for i in range(16):
            next_tux = tux1 if i % 2 == 0 else tux2
            apache_routes.append([
                mdp.get_right(),
                apache_l1.get_left(),
                apache_l1.get_right(),
                osb_nodes[4].get_left(),
                osb_nodes[4].get_right(),
                next_tux.get_left(),
                next_tux.get_right(),
                tan1.get_left(),
            ])

        apache_dots = [Dot(color=WHITE, radius=0.06) for _ in apache_routes]
        for dot in apache_dots:
            self.add(dot)

        apache_anims = []
        for dot, route in zip(apache_dots, apache_routes):
            apache_anims.append(move_with_trail(route, dot, move_time=2.0))

        self.play(LaggedStart(*apache_anims, lag_ratio=0.08))

        move_timeline_to(3, run_time=2.0)
        next_event = Text(title_text(3, "Falla Apache L1"), font_size=14).next_to(timeline_group, UP, buff=0.14)
        next_subtitle = Text(detail_text(3) or default_subtitle, font_size=9).next_to(title, DOWN, aligned_edge=LEFT, buff=0.1)
        self.play(FadeOut(timeline_event), FadeIn(next_event), run_time=0.4)
        self.play(Transform(subtitle, next_subtitle), run_time=0.4)
        timeline_event = next_event

        # Falla en Apache L1: se reinicia y se switchea la carga a M1
        self.play(
            FadeOut(line_mdp_apache_l1),
            FadeOut(line_apache_l1_osb_l1),
            FadeOut(line_osb_l1_tux1),
            FadeOut(line_osb_l1_tux2),
        )
        self.play(
            apache_l1.animate.set_color(RED),
            run_time=0.3,
        )
        self.play(
            apache_l1.animate.set_color(ORANGE),
            run_time=0.4,
        )
        line_mdp_apache_m1 = base_line(mdp.get_right(), apache_m1.get_left())
        line_apache_m1_osb_m1 = base_line(apache_m1.get_right(), osb_nodes[0].get_left())
        line_osb_m1_tux1 = base_line(osb_nodes[0].get_right(), tux1.get_left())
        line_osb_m1_tux2 = base_line(osb_nodes[0].get_right(), tux2.get_left())
        self.play(Create(line_mdp_apache_m1), run_time=0.3)
        self.play(Create(line_apache_m1_osb_m1), run_time=0.3)
        self.play(Create(line_osb_m1_tux1), run_time=0.25)
        self.play(Create(line_osb_m1_tux2), run_time=0.25)

        apache_m1_routes = []
        for i in range(16):
            next_tux = tux1 if i % 2 == 0 else tux2
            apache_m1_routes.append([
                mdp.get_right(),
                apache_m1.get_left(),
                apache_m1.get_right(),
                osb_nodes[0].get_left(),
                osb_nodes[0].get_right(),
                next_tux.get_left(),
                next_tux.get_right(),
                tan1.get_left(),
            ])
        apache_m1_dots = [Dot(color=WHITE, radius=0.06) for _ in apache_m1_routes]
        for dot in apache_m1_dots:
            self.add(dot)
        apache_m1_anims = []
        for dot, route in zip(apache_m1_dots, apache_m1_routes):
            apache_m1_anims.append(move_with_trail(route, dot, move_time=2.0))
        self.play(LaggedStart(*apache_m1_anims, lag_ratio=0.08))

        move_timeline_to(4, run_time=2.0)
        next_event = Text(title_text(4, "RollBack F5"), font_size=14).next_to(timeline_group, UP, buff=0.14)
        next_subtitle = Text(detail_text(4) or default_subtitle, font_size=9).next_to(title, DOWN, aligned_edge=LEFT, buff=0.1)
        self.play(FadeOut(timeline_event), FadeIn(next_event), run_time=0.8)
        self.play(Transform(subtitle, next_subtitle), run_time=0.4)
        timeline_event = next_event
        new_title = Text("Arquitectura Motor de Pagos LBTR - TOBE - 2026", font_size=40).to_edge(UP)
        self.play(Transform(title, new_title), run_time=0.6)

        # Switch back to F5 and run all transactions with no timeouts
        self.play(
            FadeOut(line_mdp_apache_m1),
            FadeOut(line_apache_m1_osb_m1),
            FadeOut(line_osb_m1_tux1),
            FadeOut(line_osb_m1_tux2),
        )
        line_mdp_f5_final = base_line(mdp.get_right(), f5.get_left())
        self.play(Create(line_mdp_f5_final))
        lines_f5_osb_final = []
        lines_osb_tux1_final = []
        lines_osb_tux2_final = []
        for osb in osb_nodes:
            lfo = base_line(f5.get_right(), osb.get_left())
            lines_f5_osb_final.append(lfo)
            self.play(Create(lfo), run_time=0.2)
        for osb in osb_nodes:
            l1 = base_line(osb.get_right(), tux1.get_left())
            l2 = base_line(osb.get_right(), tux2.get_left())
            lines_osb_tux1_final.append(l1)
            lines_osb_tux2_final.append(l2)
            self.play(Create(l1), run_time=0.2)
            self.play(Create(l2), run_time=0.2)

        f5_routes_final = []
        for osb in osb_nodes:
            f5_routes_final.append([
                mdp.get_right(),
                f5.get_left(), f5.get_right(),
                osb.get_left(), osb.get_right(),
                tux1.get_left(), tux1.get_right(),
                tan1.get_left(),
            ])
            f5_routes_final.append([
                mdp.get_right(),
                f5.get_left(), f5.get_right(),
                osb.get_left(), osb.get_right(),
                tux2.get_left(), tux2.get_right(),
                tan1.get_left(),
            ])

        f5_dots_final = [Dot(color=WHITE, radius=0.06) for _ in f5_routes_final]
        for dot in f5_dots_final:
            self.add(dot)
        f5_anims_final = []
        for dot, route in zip(f5_dots_final, f5_routes_final):
            f5_anims_final.append(move_with_trail(route, dot, move_time=2.0))
        self.play(LaggedStart(*f5_anims_final, lag_ratio=0.08))
        self.play(*[dot.animate.set_color(GREEN) for dot in f5_dots_final], run_time=1.0)
        tandem_offsets = [
            UP * 0.1 + LEFT * 0.05,
            DOWN * 0.1 + RIGHT * 0.05,
            UP * 0.05 + RIGHT * 0.1,
            DOWN * 0.15 + LEFT * 0.1,
            ORIGIN,
        ]
        self.play(*[
            dot.animate.move_to(tan1.get_center() + tandem_offsets[i % len(tandem_offsets)])
            for i, dot in enumerate(f5_dots_final)
        ], run_time=0.6)

        self.wait(2)
