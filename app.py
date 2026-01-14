from shiny import App, ui, render, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import os

# ---------- Font setup ----------
font_path = os.path.join(os.getcwd(), "Clarendon Bold.otf")
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    clarendon = fm.FontProperties(fname=font_path)
else:
    clarendon = None

# ---------- UI ----------
app_ui = ui.page_navbar(

    # ===== TAB 0: OVERVIEW / ABSTRACT =====
    ui.nav_panel(
        "Overview",
        ui.div(
            ui.img(
                src="header.png",
                style="""
                width: 100%;
                max-height: 320px;
                object-fit: cover;
                border-radius: 6px;
                margin-bottom: 24px;
                display: block;
                """
            ),
            ui.h1(
                "College Fight Song Analysis",
                style="font-family: 'Clarendon Bold', serif; margin-bottom: 12px;"
            ),
            ui.HTML(
                """
                <p style="font-family: 'Clarendon Bold', serif; font-size: 1.05rem; max-width: 1800px;">
                College fight songs are a unique intersection of music, athletics, and institutional identity.
                This project examines how common lyrical tropes, such as references to victory, opponents,
                school colors, and collective identity, have evolved across decades, by athletic conference, and by authorship.</p>

                <p style="font-family: 'Clarendon Bold', serif; font-size: 1.05rem; max-width: 1800px;">
                Using a dataset of <a href="https://github.com/fivethirtyeight/data/tree/master/fight-songs" target="_blank">Power Five fight songs</a> spanning the late 19th century through the modern era,
                the visualizations explore historical trends and stylistic differences, highlighting how
                musical traditions reflect broader cultural and institutional shifts in college sports.
                </p>

                <p style="font-family: 'Clarendon Bold', serif; font-size: 1.05rem; max-width: 1800px;">
                This dashboard was created for <a href="https://www.northwestern.edu/provost/about/ir/love-data/nu-data-viz-champ.html" target="_blank">Northwestern's Data Viz Championship</a>. Using the <a href="https://github.com/fivethirtyeight/data/tree/master/fight-songs" target="_blank">Fight Songs Dataset</a>,
                we chose to display how the usage of tropes in fight songs vary across decade and conference. The dashboard was created 
                using <a href="https://shiny.posit.co/" target="_blank">Shiny</a> and <a href="https://www.shinyapps.io/" target="_blank">shinyapps.io</a> in Python. The header for the 'Overview' tab was designed by the students using Procreate
                and Canva.
                </p>

                <p style="font-family: 'Clarendon Bold', serif; font-size: 1.05rem; max-width: 1800px;">
                If you are interested in our code, <a href="https://github.com/your-repo" target="_blank">click here</a>!
                </p>

                <p style="font-family: 'Clarendon Bold', serif; font-size: 1.05rem; max-width: 1800px;">
                - Sophia Perez and Andre Bianchi
                </p>
                """
            ),  # Keep your abstract HTML
            style="padding: 24px;"
        ),
    ),

    # ===== TAB 1: BY DECADE (WITH SIDEBAR) =====
    ui.nav_panel(
        "By decade",
        ui.page_sidebar(
            ui.sidebar(
                ui.input_slider("min_decade", "Minimum decade", 1890, 1960, value=1890, step=10),
                ui.input_checkbox_group(
                    "series", "Show series",
                    choices={
                        "men": "Men",
                        "victory": "Victory / Win / Won",
                        "fight": "Fight",
                        "rah": "Rah",
                        "colors": "Colors",
                        "nonsense": "Nonsense",
                        "opponents": "Opponents"
                    },
                    selected=[
                        "men", "victory", "fight", "rah", "colors", "nonsense", "opponents"
                    ]
                ),
                ui.hr(),
                ui.h4("Select a decade"),
                ui.output_ui("decade_buttons"),
                width=320,
            ),
            ui.h2("Fight Song Trope Mentions by Decade",
                  style="font-family: 'Clarendon Bold', serif;"),
            ui.h6(
                "This visualization showcases trends in fight song tropes across decades, "
                "using a football field–inspired layout to reflect the sport’s culture, "
                "while drawing on historical context to explore why certain tropes rise "
                "and fall over time.",
                style="font-family: 'Clarendon Bold', serif;"
            ),
            ui.output_ui("decade_info"),
            ui.hr(),
            ui.output_plot("plot2", height="420px"),
        ),
    ),

    # ===== TAB 2: BY CONFERENCE (NO SIDEBAR) =====
    ui.nav_panel(
        "By conference",
        ui.h2("Fight Song Trope Profiles by Conference",
              style="font-family: 'Clarendon Bold', serif;"),
        ui.p("Top 5 conferences by sample size."),
        ui.output_plot("plot_conf", height="420px"),
    ),

    # ===== TAB 3: STUDENT / CONTEST ANALYSIS =====
    ui.nav_panel(
        "By authorship",
        ui.h2("Fight Song Trope Usage by Authorship",
              style="font-family: 'Clarendon Bold', serif;"),
        ui.p("Click a button below to toggle between plots."),
        ui.input_radio_buttons(
            "student_contest_plot",
            "Select plot:",
            {"student": "Student vs Non-student", "contest": "Contest vs Non-contest"},
            inline=True
        ),
        ui.output_plot("student_contest_plot_output", height="500px"),
    ),

    title="College Fight Song Analysis",
    navbar_options=ui.navbar_options(class_="bg-primary", theme="dark", bg="#005e9e")
)

# ---------- Server ----------
def server(input, output, session):

    # ---------- Load data ----------
    @reactive.Calc
    def fight_songs_data():
        path = Path("fight-songs.csv")
        if not path.exists():
            return None

        d = pd.read_csv(path)
        d["year"] = d["year"].astype(str).str.extract(r"(\d{4})")[0].astype(float)
        d = d.dropna(subset=["year"])
        d["year"] = d["year"].astype(int)
        d["decade"] = (d["year"] // 10) * 10

        def yn_to_bool(s):
            return s.astype(str).str.strip().str.lower().map({"yes": True, "no": False})

        d["men_bool"] = yn_to_bool(d["men"])
        d["victory_bool"] = yn_to_bool(d["victory_win_won"])
        d["fight_bool"] = yn_to_bool(d["fight"])
        d["rah_bool"] = yn_to_bool(d["rah"])
        d["nonsense_bool"] = yn_to_bool(d["nonsense"])
        d["colors_bool"] = yn_to_bool(d["colors"])
        d["opponents_bool"] = yn_to_bool(d["opponents"])

        return d

    # ---------- Student / Contest Proportions ----------
    @reactive.Calc
    def student_contest_props():
        data = fight_songs_data()
        if data is None:
            return None

        tropes = ["fight", "victory_win_won", "rah", "nonsense",
                  "colors", "men", "opponents", "spelling"]
        cols = ["student_writer", "contest"] + tropes
        data = data[cols]
        data = data[data["student_writer"].isin(["Yes", "No"])]
        data = data[data["contest"].isin(["Yes", "No"])]

        for trope in tropes:
            data = data[data[trope].isin(["Yes", "No"])]
            data[trope] = data[trope].map({"Yes": 1, "No": 0})

        def trope_props(df_group, group_col, group_val):
            subset = df_group[df_group[group_col] == group_val]
            return subset[tropes].mean()

        return {
            "student": trope_props(data, "student_writer", "Yes"),
            "nonstudent": trope_props(data, "student_writer", "No"),
            "contest": trope_props(data, "contest", "Yes"),
            "noncontest": trope_props(data, "contest", "No"),
            "tropes": tropes
        }

    # ---------- Student / Contest Plot ----------
    @output
    @render.plot
    def student_contest_plot_output():
        plot_type = input.student_contest_plot()
        props = student_contest_props()
        if props is None:
            fig, ax = plt.subplots()
            ax.set_axis_off()
            return fig

        x = np.arange(len(props["tropes"]))
        width = 0.35
        palette = ["#228B22", "#8FBC8B", "#ef6351", "#fbc3bc"]

        fig, ax = plt.subplots(figsize=(10, 6))

        if plot_type == "student":
            ax.bar(x - width / 2, props["student"], width, label="Student-written", color=palette[0])
            ax.bar(x + width / 2, props["nonstudent"], width, label="Non-student-written", color=palette[1])
            ax.set_title("Trope Usage by Student Authorship")
        else:  # contest
            ax.bar(x - width / 2, props["contest"], width, label="Contest-selected", color=palette[2])
            ax.bar(x + width / 2, props["noncontest"], width, label="Non-contest", color=palette[3])
            ax.set_title("Trope Usage by Contest Selection")

        ax.set_xticks(x)
        ax.set_xticklabels(props["tropes"], rotation=30, ha="right")
        ax.set_ylabel("Proportion of Songs")
        ax.legend()
        fig.tight_layout()
        return fig

    # ---------- DECADE CONTEXT ----------
    DECADE_CONTEXT = {
        1890: "Late 19th century: Universities were formalizing traditions, including fight songs, mascots, and sporting events. College culture emphasized classical education, discipline, and the beginnings of organized football programs.",
        1900: "Progressive Era in the United States: Reform movements sought to address social issues like labor conditions, women's suffrage, and education. College life grew more structured, and intercollegiate sports became increasingly popular. The 'Men' trope reaches a global maximum in this decade and quickly declines in following years, which is indicative of changes in gender norms.",
        1910: "World War I period: Global tensions and the outbreak of war influenced American society. Colleges contributed to military training, and patriotic themes became common in student life and song lyrics, which illustrates how the 'Fight' trope is on the rise.",
        1920: "Roaring Twenties: Economic prosperity and cultural dynamism characterized the decade. Jazz, flappers, and new forms of entertainment emerged, and college campuses embraced spirited events, football, and lively social traditions.",
        1930: "Great Depression: Economic hardship shaped everyday life. Despite financial challenges, colleges maintained traditions, with fight songs often reflecting resilience and community pride in difficult times. All songs use the 'Fight' trope here.",
        1940: "World War II: American involvement affected campus populations as many students joined the military. College events, songs, and sports often incorporated patriotic themes, morale-building, and support for the war effort.",
        1950: "Post-war boom and Cold War beginnings: Returning veterans fueled campus growth through the GI Bill. Colleges expanded, football and other sports flourished, and societal optimism mixed with the tension of emerging Cold War politics. The 'Fight' and 'Victory' tropes fall while the use of opponents in fight songs starts to ri",
        1960: "Civil Rights Movement and social change: Activism and social justice influenced campuses nationwide. Music, including fight songs and student performances, reflected changing attitudes, while traditional college traditions coexisted with broader societal transformation.",

    }

    # ---------- Decade Proportions ----------
    @reactive.Calc
    def decade_props():
        d = fight_songs_data()
        if d is None:
            return None

        d = d[d["decade"] >= input.min_decade()]

        prop_men = d.groupby("decade")["men_bool"].mean()
        prop_victory = d.groupby("decade")["victory_bool"].mean()
        prop_fight = d.groupby("decade")["fight_bool"].mean()
        prop_rah = d.groupby("decade")["rah_bool"].mean()
        prop_nonsense = d.groupby("decade")["nonsense_bool"].mean()
        prop_colors = d.groupby("decade")["colors_bool"].mean()
        prop_opponents = d.groupby("decade")["opponents_bool"].mean()

        return prop_men, prop_victory, prop_fight, prop_rah, prop_nonsense, prop_colors, prop_opponents

    # ---------- Available Decades ----------
    @reactive.Calc
    def available_decades():
        p = decade_props()
        if p is None:
            return []
        return p[0].index.to_list()

    last_clicked_decade = reactive.Value(None)

    # ---------- Buttons UI ----------
    @output
    @render.ui
    def decade_buttons():
        buttons = []
        for d in available_decades():
            btn = ui.input_action_button(
                f"decade_{d}",
                label=f"{d}s",
                class_="btn btn-outline-success btn-sm"
            )

            @reactive.Effect
            def _update(d=d):
                if input[f"decade_{d}"]() > 0:
                    last_clicked_decade.set(d)

            buttons.append(btn)

        return ui.div(*buttons, style="display: flex; flex-wrap: wrap; gap: 6px;")

    @reactive.Calc
    def selected_decade():
        return last_clicked_decade.get()

    @output
    @render.ui
    def decade_info():
        decade = selected_decade()
        if decade is None:
            return ui.p("Click a decade button to see historical context.",
                        style="font-family: 'Clarendon Bold', serif;")
        text = DECADE_CONTEXT.get(decade, "No context added yet for this decade.")
        return ui.div(
            ui.h4(f"{decade}s"),
            ui.p(text),
            style="padding: 12px; border-left: 4px solid #35654d;"
        )

    # ---------- Plot by Decade ----------
    @output
    @render.plot
    def plot2():
        p = decade_props()
        if p is None:
            fig, ax = plt.subplots()
            ax.set_axis_off()
            return fig

        prop_men, prop_victory, prop_fight, prop_rah, prop_nonsense, prop_colors, prop_opponents = p
        selected = set(input.series())
        decades_list = prop_men.index.to_list()
        x = np.arange(len(decades_list))

        fig, ax = plt.subplots(figsize=(12, 4.8))
        fig.patch.set_facecolor("#376f32")
        ax.set_facecolor("#376f32")

        # Yard lines
        for i in x:
            ax.axvline(i, color="white", alpha=0.3, linewidth=1)

        BOLD_INTERVAL = 7
        for i in x[::BOLD_INTERVAL]:
            ax.axvline(i, color="white", alpha=0.7, linewidth=2)

        # Lines
        if "men" in selected:
            ax.plot(x, prop_men.values, marker="$\u266A$", label="Men",
                    color="lightcoral", markersize=12)
        if "victory" in selected:
            ax.plot(x, prop_victory.values, marker="$\u266A$", label="Victory / Win / Won",
                    color="orange", markersize=12)
        if "fight" in selected:
            ax.plot(x, prop_fight.values, marker="$\u266A$", label="Fight",
                    color="lightskyblue", markersize=12)
        if "rah" in selected:
            ax.plot(x, prop_rah.values, marker="$\u266A$", label="Rah",
                    color="gold", markersize=12)
        if "nonsense" in selected:
            ax.plot(x, prop_nonsense.values, marker="$\u266A$", label="Nonsense",
                    color="turquoise", markersize=12)
        if "colors" in selected:
            ax.plot(x, prop_colors.values, marker="$\u266A$", label="Colors",
                    color="mediumpurple", markersize=12)
        if "opponents" in selected:
            ax.plot(x, prop_opponents.values, marker="$\u266A$", label="Opponents",
                    color="orchid", markersize=12)

        ax.set_xticks(x)
        ax.set_xticklabels([str(d) for d in decades_list],
                           fontproperties=clarendon, fontsize=18, color="white")
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlim(-0.5, len(x) - 0.5)
        ax.set_xlabel("Decade", color="white")
        ax.set_ylabel("Proportion of songs using each trope", color="white")
        ax.tick_params(colors="white")
        ax.legend(loc='lower left', bbox_to_anchor=(1, 0.5))
        fig.tight_layout()
        return fig

    # ---------- Plot by Conference ----------
    @output
    @render.plot
    def plot_conf():
        d = fight_songs_data()
        if d is None:
            fig, ax = plt.subplots()
            ax.set_axis_off()
            return fig

        trope_cols = ["victory_bool", "fight_bool", "rah_bool", "nonsense_bool",
                     "men_bool", "colors_bool", "opponents_bool"]

        if "conference" not in d.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Missing 'conference' column in fight-songs.csv",
                    ha="center", va="center")
            ax.set_axis_off()
            return fig

        dd = d.dropna(subset=["conference"] + trope_cols).copy()
        if dd.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No rows with conference + trope data", ha="center", va="center")
            ax.set_axis_off()
            return fig

        conf_trope = dd.groupby("conference")[trope_cols].mean().rename(columns={
            "victory_bool": "Victory/Win/Won",
            "fight_bool": "Fight",
            "rah_bool": "Rah",
            "nonsense_bool": "Nonsense",
            "men_bool": "Men",
            "colors_bool": "Colors",
            "opponents_bool": "Opponents",
        })

        conf_counts = dd.groupby("conference").size().sort_values(ascending=False)
        top5 = conf_counts.head(5).index.tolist()

        conf_colors = {"ACC": "#013CA6", "Big Ten": "#0B1F41",
                       "Big 12": "#0033A0", "Pac-12": "#004B91", "SEC": "#1C2E4A"}
        default_color = "#333333"

        labels = conf_trope.columns.tolist()
        n_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, n_vars, endpoint=False)
        angles_closed = np.concatenate([angles, [angles[0]]])

        fig, axes = plt.subplots(1, max(1, len(top5)), figsize=(3.6 * len(top5), 4),
                                 subplot_kw=dict(polar=True), constrained_layout=True)
        if len(top5) == 1:
            axes = [axes]

        for ax, conf in zip(axes, top5):
            vals = conf_trope.loc[conf].values
            vals_closed = np.concatenate([vals, [vals[0]]])
            color = conf_colors.get(conf, default_color)

            ax.plot(angles_closed, vals_closed, linewidth=2, color=color)
            ax.fill(angles_closed, vals_closed, color=color, alpha=0.25)
            ax.set_title(f"{conf}\n(n={int(conf_counts[conf])})", pad=14, fontsize=11)
            ax.set_ylim(0, 1)
            ax.set_thetagrids(np.degrees(angles), labels, fontsize=8)
            ax.set_rgrids([0.25, 0.5, 0.75, 1.0], angle=0, fontsize=7)
            ax.grid(alpha=0.35)

        fig.suptitle("Fight Song Trope Profiles by Conference", fontsize=14)
        return fig

# ---------- App ----------
app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
