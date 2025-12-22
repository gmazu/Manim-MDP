from manim import *

class ArquitecturaMDPLBTR(Scene):
    def construct(self):
        title = Text("Arquitectura Motor de Pagos LBTR - ASIS - 2025", font_size=40).to_edge(UP)
        subtitle = Text(
            "Arquitectura sin HA\ndesde marzo 2024\n hasta enero 2025\naproximadamente.",
            font_size=12,
        ).to_corner(UL).shift(DOWN * 1.0 + RIGHT * 0.2)
        version_document = Text("versión v2.2.1", font_size=9).next_to(title, DOWN, aligned_edge=RIGHT, buff=0.1)
        self.play(Write(title), FadeIn(subtitle), FadeIn(version_document))

        
        # Mostrar versión en esquina inferior derecha (evita solaparse con la leyenda)
        version_general = Text("by eCORE - PNLöP v³ & Manim v0.19.1", font_size=9).to_corner(DR).shift(UP * 0.1 + LEFT * 0.1)
        self.play(FadeIn(version_general))

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
        line_mdp_f5 = Line(mdp.get_right(), f5.get_left())
        self.play(Create(line_mdp_f5))
        lines_f5_osb = []
        lines_osb_tux1 = []
        lines_osb_tux2 = []
        lines_tux_tan = [
            Line(tux1.get_right(), tan1.get_left()),
            Line(tux2.get_right(), tan1.get_left()),
        ]
        for osb in osb_nodes:
            lfo = Line(f5.get_right(), osb.get_left())
            lines_f5_osb.append(lfo)
            self.play(Create(lfo), run_time=0.2)
        for osb in osb_nodes:
            l1 = Line(osb.get_right(), tux1.get_left())
            l2 = Line(osb.get_right(), tux2.get_left())
            lines_osb_tux1.append(l1)
            lines_osb_tux2.append(l2)
            self.play(Create(l1), run_time=0.2)
            self.play(Create(l2), run_time=0.2)
        self.play(Create(lines_tux_tan[0]), Create(lines_tux_tan[1]))

        # Simulación de transacciones: 16 bolitas, la 4ª, 8ª, 12ª y última quedan atascadas en F5
        travel_routes = []
        for osb in osb_nodes:
            travel_routes.append([mdp.get_right(), f5.get_left(), osb.get_left(), tux1.get_left(), tan1.get_left()])
            travel_routes.append([mdp.get_right(), f5.get_left(), osb.get_left(), tux2.get_left(), tan1.get_left()])

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
                path = VMobject()
                path.set_points_as_corners([mdp.get_right(), f5.get_center() + offset])
                animations.append(MoveAlongPath(dot, path, rate_func=linear, run_time=0.6))
                stuck_dots.append(dot)
            else:
                path = VMobject()
                path.set_points_as_corners(route)
                animations.append(MoveAlongPath(dot, path, rate_func=linear, run_time=2.0))
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
        line_mdp_apache_l1 = Line(mdp.get_right(), apache_l1.get_left())
        line_apache_l1_osb_l1 = Line(apache_l1.get_right(), osb_nodes[4].get_left())
        line_osb_l1_tux1 = Line(osb_nodes[4].get_right(), tux1.get_left())
        line_osb_l1_tux2 = Line(osb_nodes[4].get_right(), tux2.get_left())
        line_tux1_tan1_new = Line(tux1.get_right(), tan1.get_left())
        line_tux2_tan1_new = Line(tux2.get_right(), tan1.get_left())

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
                tan1.get_left(),
            ])

        apache_dots = [Dot(color=WHITE, radius=0.06) for _ in apache_routes]
        for dot in apache_dots:
            self.add(dot)

        apache_anims = []
        for dot, route in zip(apache_dots, apache_routes):
            path = VMobject()
            path.set_points_as_corners(route)
            apache_anims.append(MoveAlongPath(dot, path, rate_func=linear, run_time=2.0))

        self.play(LaggedStart(*apache_anims, lag_ratio=0.08))

        # Switch to Apache M1 and run all transactions
        self.play(
            FadeOut(line_mdp_apache_l1),
            FadeOut(line_apache_l1_osb_l1),
            FadeOut(line_osb_l1_tux1),
            FadeOut(line_osb_l1_tux2),
        )
        line_mdp_apache_m1 = Line(mdp.get_right(), apache_m1.get_left())
        line_apache_m1_osb_m1 = Line(apache_m1.get_right(), osb_nodes[0].get_left())
        line_osb_m1_tux1 = Line(osb_nodes[0].get_right(), tux1.get_left())
        line_osb_m1_tux2 = Line(osb_nodes[0].get_right(), tux2.get_left())
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
                tan1.get_left(),
            ])
        apache_m1_dots = [Dot(color=WHITE, radius=0.06) for _ in apache_m1_routes]
        for dot in apache_m1_dots:
            self.add(dot)
        apache_m1_anims = []
        for dot, route in zip(apache_m1_dots, apache_m1_routes):
            path = VMobject()
            path.set_points_as_corners(route)
            apache_m1_anims.append(MoveAlongPath(dot, path, rate_func=linear, run_time=2.0))
        self.play(LaggedStart(*apache_m1_anims, lag_ratio=0.08))

        # Switch back to Apache L1 and run all transactions
        self.play(
            FadeOut(line_mdp_apache_m1),
            FadeOut(line_apache_m1_osb_m1),
            FadeOut(line_osb_m1_tux1),
            FadeOut(line_osb_m1_tux2),
        )
        line_mdp_apache_l1_round2 = Line(mdp.get_right(), apache_l1.get_left())
        line_apache_l1_osb_l1_round2 = Line(apache_l1.get_right(), osb_nodes[4].get_left())
        line_osb_l1_tux1_round2 = Line(osb_nodes[4].get_right(), tux1.get_left())
        line_osb_l1_tux2_round2 = Line(osb_nodes[4].get_right(), tux2.get_left())
        self.play(Create(line_mdp_apache_l1_round2), run_time=0.3)
        self.play(Create(line_apache_l1_osb_l1_round2), run_time=0.3)
        self.play(Create(line_osb_l1_tux1_round2), run_time=0.25)
        self.play(Create(line_osb_l1_tux2_round2), run_time=0.25)

        apache_l1_routes_round2 = []
        for i in range(16):
            next_tux = tux1 if i % 2 == 0 else tux2
            apache_l1_routes_round2.append([
                mdp.get_right(),
                apache_l1.get_left(),
                apache_l1.get_right(),
                osb_nodes[4].get_left(),
                osb_nodes[4].get_right(),
                next_tux.get_left(),
                tan1.get_left(),
            ])
        apache_l1_dots_round2 = [Dot(color=WHITE, radius=0.06) for _ in apache_l1_routes_round2]
        for dot in apache_l1_dots_round2:
            self.add(dot)
        apache_l1_anims_round2 = []
        for dot, route in zip(apache_l1_dots_round2, apache_l1_routes_round2):
            path = VMobject()
            path.set_points_as_corners(route)
            apache_l1_anims_round2.append(MoveAlongPath(dot, path, rate_func=linear, run_time=2.0))
        self.play(LaggedStart(*apache_l1_anims_round2, lag_ratio=0.08))

        # Switch back to F5 and run all transactions with no timeouts
        self.play(
            FadeOut(line_mdp_apache_l1_round2),
            FadeOut(line_apache_l1_osb_l1_round2),
            FadeOut(line_osb_l1_tux1_round2),
            FadeOut(line_osb_l1_tux2_round2),
        )
        line_mdp_f5_final = Line(mdp.get_right(), f5.get_left())
        self.play(Create(line_mdp_f5_final))
        lines_f5_osb_final = []
        lines_osb_tux1_final = []
        lines_osb_tux2_final = []
        for osb in osb_nodes:
            lfo = Line(f5.get_right(), osb.get_left())
            lines_f5_osb_final.append(lfo)
            self.play(Create(lfo), run_time=0.2)
        for osb in osb_nodes:
            l1 = Line(osb.get_right(), tux1.get_left())
            l2 = Line(osb.get_right(), tux2.get_left())
            lines_osb_tux1_final.append(l1)
            lines_osb_tux2_final.append(l2)
            self.play(Create(l1), run_time=0.2)
            self.play(Create(l2), run_time=0.2)

        f5_routes_final = []
        for osb in osb_nodes:
            f5_routes_final.append([mdp.get_right(), f5.get_left(), osb.get_left(), tux1.get_left(), tan1.get_left()])
            f5_routes_final.append([mdp.get_right(), f5.get_left(), osb.get_left(), tux2.get_left(), tan1.get_left()])

        f5_dots_final = [Dot(color=WHITE, radius=0.06) for _ in f5_routes_final]
        for dot in f5_dots_final:
            self.add(dot)
        f5_anims_final = []
        for dot, route in zip(f5_dots_final, f5_routes_final):
            path = VMobject()
            path.set_points_as_corners(route)
            f5_anims_final.append(MoveAlongPath(dot, path, rate_func=linear, run_time=2.0))
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

        # Mostrar subtítulo al final
        self.play(FadeIn(subtitle, run_time=1.3))

        self.wait(2)
