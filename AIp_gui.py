import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import json, os, random, math
from collections import deque
from matplotlib import animation

STORY_FILE = "story_progress.json"

# ------------------ Data Management ------------------
def load_story():
    if not os.path.exists(STORY_FILE):
        return {"current_node": "start", "visited": [], "history": [], "stats": {}}
    with open(STORY_FILE, "r") as f:
        return json.load(f)

def save_story(data):
    with open(STORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ AI Story Generator ------------------
class AdaptiveStoryGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.theme = random.choice(["mystery", "adventure", "sci-fi", "fantasy", "survival"])
        self.generate_story()

    def generate_story(self):
        """AI-style dynamic story generation each run with attribute-aware text templates"""
        start_texts = {
            "mystery": "You wake up in a foggy town with no memory of who you are.",
            "adventure": "You find a dusty map leading to a hidden island.",
            "sci-fi": "You regain consciousness in a deserted space station orbiting Earth.",
            "fantasy": "You awaken in an enchanted forest filled with glowing runes.",
            "survival": "You wake up after a plane crash in a wild jungle."
        }
        self.G.add_node("start", text=start_texts[self.theme], attributes=self.random_attributes())

        # Node generation settings
        num_branches = random.randint(3, 6)
        for i in range(1, num_branches + 1):
            n = f"choice_{i}"
            attrs = self.random_attributes()
            text = self.compose_text_for_node(n, attrs)
            self.G.add_node(n, text=text, attributes=attrs)
            self.G.add_edge("start", n)

            # Generate secondary branches
            for j in range(random.randint(1, 3)):
                m = f"{n}_path{j}"
                attrs_m = self.random_attributes()
                next_text = self.compose_text_for_node(m, attrs_m)
                self.G.add_node(m, text=next_text, attributes=attrs_m)
                self.G.add_edge(n, m)

                # Occasionally create an ending
                if random.random() < 0.35:
                    e = f"{m}_end"
                    attrs_e = self.random_attributes()
                    end_text = self.compose_text_for_node(e, attrs_e, ending=True)
                    self.G.add_node(e, text=end_text, attributes=attrs_e)
                    self.G.add_edge(m, e)

        # Add some random cross-links to make it adaptive
        nodes = list(self.G.nodes())
        for _ in range(random.randint(3, 6)):
            a, b = random.sample(nodes, 2)
            if a != "start" and b != "start" and a != b and not self.G.has_edge(a, b):
                self.G.add_edge(a, b)

    def random_attributes(self):
        # emotion: how emotionally charged the node is (1-10)
        # risk: how dangerous / uncertain the node is (0-5)
        # reward: potential reward if pursued (0-5)
        return {
            "emotion": random.randint(1, 10),
            "risk": random.randint(0, 5),
            "reward": random.randint(0, 5)
        }

    def compose_text_for_node(self, node_name, attrs, ending=False):
        """Create a short text that depends on the attributes to feel AI-generated."""
        emotion = attrs["emotion"]
        risk = attrs["risk"]
        reward = attrs["reward"]

        openings = [
            "You sense something unusual.",
            "A chill runs down your spine.",
            "The air feels charged with possibility.",
            "You spot a glimmer of something valuable.",
            "A figure appears and gestures toward you."
        ]
        ending_lines = [
            "You find peace and safety at last.",
            "You uncover the hidden truth of your journey.",
            "You vanish into the unknown, your fate sealed.",
            "You escape the danger, but the memory lingers.",
            "You realize this was only the beginning..."
        ]

        base = random.choice(openings)
        detail = f" (emotion {emotion}, risk {risk}, reward {reward})"

        # Adjust flavor by emotion and risk
        if ending:
            return f"{random.choice(ending_lines)}{detail}"
        tone = ""
        if emotion >= 8:
            tone = " Your heart races; the scene feels intense."
        elif emotion <= 3:
            tone = " A calm settles in, but something is off."
        if risk >= 4:
            tone += " Danger seems imminent."
        elif reward >= 4:
            tone += " This could be a big opportunity."

        return base + tone + detail

    def get_choices(self, node):
        return list(self.G.successors(node))

    def get_text(self, node):
        return self.G.nodes[node]["text"]

    def get_node_attributes(self, node):
        return self.G.nodes[node].get("attributes", {"emotion":5,"risk":2,"reward":2})

# ------------------ AI Recommendation Engine ------------------
class SimpleAIAdvisor:
    """
    A simple offline heuristic 'AI' that scores choices and provides recommendations + explanations.
    The scoring function uses attributes (emotion, risk, reward), novelty (visited?), and a mild randomness.
    """

    def __init__(self, graph: AdaptiveStoryGraph, story_data: dict):
        self.graph = graph
        self.story_data = story_data

    def score_choice(self, node, current_node):
        """
        Score = weighted sum:
         + reward * w_reward
         - risk * w_risk
         + emotion_bias (prefers moderate-high emotion)
         + novelty bonus if not visited
         - distance penalty if node is deeper than some threshold (we don't compute depth here; simple)
         + small random exploration noise
        """
        attrs = self.graph.get_node_attributes(node)
        reward = attrs.get("reward", 0)
        risk = attrs.get("risk", 0)
        emotion = attrs.get("emotion", 5)

        w_reward = 1.1
        w_risk = 1.2
        # emotion preference: ideal is around 6-8 (engaging but not unstable). Use gaussian.
        emotion_pref = math.exp(-((emotion - 7) ** 2) / (2 * (2.0 ** 2)))  # normalized-ish

        # novelty
        visited = set(self.story_data.get("visited", []))
        novelty = 1.0 if node not in visited else 0.0

        # basic usage stats if present (prefer nodes with higher past observed reward)
        stats = self.story_data.get("stats", {})
        node_stat = stats.get(node, {})
        observed_reward = node_stat.get("observed_reward", 0)

        # combine
        base_score = w_reward * reward - w_risk * risk
        score = base_score + 1.0 * emotion_pref + 1.3 * novelty + 0.2 * observed_reward

        # exploration noise (small)
        noise = random.uniform(-0.3, 0.3)
        return score + noise

    def rank_choices(self, choices, current_node):
        scored = [(c, self.score_choice(c, current_node)) for c in choices]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def recommend(self, choices, current_node):
        if not choices:
            return None, None
        ranked = self.rank_choices(choices, current_node)
        best_node, best_score = ranked[0]
        # create simple explanation
        explanation = self.explain_choice(best_node, best_score)
        return best_node, explanation

    def explain_choice(self, node, score):
        attrs = self.graph.get_node_attributes(node)
        parts = [
            f"Score ≈ {score:.2f}",
            f"Reward={attrs.get('reward')}",
            f"Risk={attrs.get('risk')}",
            f"Emotion={attrs.get('emotion')}"
        ]
        # novelty
        if node not in self.story_data.get("visited", []):
            parts.append("Novelty bonus: not visited")
        # observed reward
        observed = self.story_data.get("stats", {}).get(node, {}).get("observed_reward", 0)
        if observed:
            parts.append(f"Observed reward={observed}")
        return "; ".join(parts)

# ------------------ Hierarchical Layout (unchanged) ------------------
def hierarchy_layout(G, root='start', width=2.0, vert_gap=1.3, vert_loc=0):
    levels = {root: 0}
    queue = deque([root])
    while queue:
        v = queue.popleft()
        for child in G.successors(v):
            if child not in levels:
                levels[child] = levels[v] + 1
                queue.append(child)

    layer_nodes = {}
    for node, level in levels.items():
        layer_nodes.setdefault(level, []).append(node)

    pos = {}
    for depth, nodes in layer_nodes.items():
        dx = width / (len(nodes) + 1)
        for i, node in enumerate(nodes):
            pos[node] = (i * dx, -depth * vert_gap + vert_loc)
    return pos

# ------------------ GUI ------------------
class StoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🤖 AI-Driven Adaptive Story Graph Generator")
        self.geometry("920x640")
        self.config(bg="#f6f7fb")

        self.story_graph = AdaptiveStoryGraph()
        self.story_data = load_story()
        # init stats container if missing
        self.story_data.setdefault("stats", {})
        self.history_stack = self.story_data.get("history", [])

        self.create_ui()
        # ensure current_node is valid
        cur = self.story_data.get("current_node", "start")
        if cur not in self.story_graph.G.nodes():
            self.story_data["current_node"] = "start"
        self.show_story(self.story_data.get("current_node", "start"))

    def create_ui(self):
        header = tk.Frame(self, bg="#f6f7fb")
        header.pack(fill="x", pady=8)
        tk.Label(header, text="🧠 AI-Driven Adaptive Story Graph", font=("Inter", 20, "bold"), bg="#f6f7fb").pack(side="left", padx=12)

        right_header = tk.Frame(header, bg="#f6f7fb")
        right_header.pack(side="right", padx=12)
        ttk.Button(right_header, text="🎞 Visualize", command=self.show_graph_animated).pack(side="left", padx=6)
        ttk.Button(right_header, text="🔁 New Story", command=self.restart_new_story).pack(side="left", padx=6)
        ttk.Button(right_header, text="Exit", command=self.quit).pack(side="left", padx=6)

        # Story text area
        self.story_text = tk.Label(self, text="", wraplength=820, justify="center",
                                   font=("Arial", 14), bg="#ffffff", relief="solid", padx=14, pady=12)
        self.story_text.pack(pady=12, padx=20)

        # Choice frame and AI controls
        control_row = tk.Frame(self, bg="#f6f7fb")
        control_row.pack(fill="x", pady=(0,6))
        self.choice_frame = tk.Frame(self, bg="#f6f7fb")
        self.choice_frame.pack(pady=6)

        ai_controls = tk.Frame(self, bg="#f6f7fb")
        ai_controls.pack(pady=6)
        ttk.Button(ai_controls, text="⬅ Go Back", command=self.go_back).grid(row=0, column=0, padx=8)
        ttk.Button(ai_controls, text="🤖 Recommend", command=self.show_recommendation).grid(row=0, column=1, padx=8)
        ttk.Button(ai_controls, text="🟢 Auto-Choose", command=self.auto_choose).grid(row=0, column=2, padx=8)
        ttk.Button(ai_controls, text="💬 Explain", command=self.explain_recommendation).grid(row=0, column=3, padx=8)

        # Footer status
        self.status_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.status_var, bg="#f6f7fb", font=("Arial", 10, "italic")).pack(pady=6)

    def show_story(self, node):
        # set current node in data
        self.story_data["current_node"] = node
        save_story(self.story_data)

        self.story_text.config(text=self.story_graph.get_text(node))
        self.clear_choices()
        choices = self.story_graph.get_choices(node)
        if not choices:
            tk.Label(self.choice_frame, text="🌟 The End 🌟", font=("Arial", 14, "bold"),
                     bg="#f6f7fb", fg="green").pack()
            self.status_var.set("Reached an ending. Try '🔁 New Story' to explore another adventure.")
            return

        # create AI advisor
        self.advisor = SimpleAIAdvisor(self.story_graph, self.story_data)
        self.current_choices = choices  # keep for later
        self.recommendation = None
        self.recommendation_expl = None

        # show choices as colored buttons (tk.Button so we can change bg easily)
        for c in choices:
            text = self.story_graph.get_text(c)
            truncated = text if len(text) <= 80 else text[:77] + "..."
            btn = tk.Button(self.choice_frame, text=truncated, wraplength=700, justify="left",
                            anchor="w", width=80, command=lambda c=c: self.next_node(c),
                            relief="raised", padx=8, pady=6, bg="#FFF9C4")
            btn.pack(pady=4)
            # store reference attribute on button for later highlight
            btn._node_id = c

        self.status_var.set(f"{len(choices)} choices available. Click '🤖 Recommend' for AI suggestion.")

    def clear_choices(self):
        for w in self.choice_frame.winfo_children():
            w.destroy()

    def next_node(self, node, auto_record=True):
        cur = self.story_data.get("current_node", "start")
        # update history
        self.history_stack.append(cur)
        self.story_data["current_node"] = node
        if node not in self.story_data.get("visited", []):
            self.story_data.setdefault("visited", []).append(node)
        self.story_data["history"] = self.history_stack

        # update stats: accumulate "observed_reward" from visited nodes as simple RL signal
        stats = self.story_data.setdefault("stats", {})
        node_attrs = self.story_graph.get_node_attributes(node)
        # We treat 'reward' as immediate observed reward for demonstration
        observed = node_attrs.get("reward", 0)
        node_stat = stats.setdefault(node, {"visits": 0, "observed_reward": 0})
        node_stat["visits"] += 1
        node_stat["observed_reward"] += observed

        save_story(self.story_data)
        self.show_story(node)

    def go_back(self):
        if not self.history_stack:
            messagebox.showinfo("Backtracking", "You are already at the beginning!")
            return
        prev = self.history_stack.pop()
        self.story_data["current_node"] = prev
        self.story_data["history"] = self.history_stack
        save_story(self.story_data)
        self.show_story(prev)

    # ------------------ AI Actions ------------------
    def show_recommendation(self):
        if not hasattr(self, "advisor"):
            self.advisor = SimpleAIAdvisor(self.story_graph, self.story_data)
        choices = getattr(self, "current_choices", [])
        cur = self.story_data.get("current_node", "start")
        best, expl = self.advisor.recommend(choices, cur)
        self.recommendation = best
        self.recommendation_expl = expl
        if best is None:
            messagebox.showinfo("Recommend", "No available choices to recommend.")
            return
        # highlight recommended button
        for w in self.choice_frame.winfo_children():
            if getattr(w, "_node_id", None) == best:
                w.config(bg="#7EB6FF")  # highlight color for recommendation
            else:
                w.config(bg="#FFF9C4")
        self.status_var.set(f"AI recommends: {best}. Click '💬 Explain' for details or press its button to follow it.")

    def explain_recommendation(self):
        if self.recommendation is None:
            messagebox.showinfo("Explain", "No recommendation made yet. Click '🤖 Recommend' first.")
            return
        messagebox.showinfo("AI Explanation", f"Recommendation: {self.recommendation}\n\nReasoning:\n{self.recommendation_expl}")

    def auto_choose(self):
        # Use the advisor to pick one and immediately follow it
        if not hasattr(self, "advisor"):
            self.advisor = SimpleAIAdvisor(self.story_graph, self.story_data)
        choices = getattr(self, "current_choices", [])
        cur = self.story_data.get("current_node", "start")
        best, expl = self.advisor.recommend(choices, cur)
        if best is None:
            messagebox.showinfo("Auto-Choose", "No available choices to auto-choose.")
            return
        # record that AI auto-chose (optionally we could store this action)
        self.recommendation = best
        self.recommendation_expl = expl
        self.next_node(best)

    # ------------------ Animated Visualization ------------------
    def show_graph_animated(self):
        G = self.story_graph.G
        pos = hierarchy_layout(G, root='start')
        visited = set(self.story_data.get("visited", []))
        current = self.story_data.get("current_node", "start")

        fig, ax = plt.subplots(figsize=(12, 7))
        plt.title("🤖 AI Adaptive Story Graph — Animated", fontsize=14, fontweight="bold")
        plt.axis("off")

        nodes = list(G.nodes())
        edges = list(G.edges())

        def update(frame):
            ax.clear()
            plt.axis("off")
            plt.title("📘 Story Graph Progress", fontsize=14, fontweight="bold")

            step_nodes = nodes[:min(len(nodes), frame + 1)]
            step_edges = [e for e in edges if e[0] in step_nodes and e[1] in step_nodes]

            colors = []
            for n in step_nodes:
                if n == current:
                    colors.append("#7EB6FF")
                elif n in visited:
                    colors.append("#A8E6CF")
                else:
                    colors.append("#FFF9C4")

            nx.draw(G.subgraph(step_nodes), pos, with_labels=True,
                    node_color=colors, node_size=2300, font_size=8,
                    font_weight="bold", edgecolors="black",
                    arrows=True, arrowsize=12, ax=ax)

        ani = animation.FuncAnimation(fig, update, frames=len(nodes), interval=500, repeat=False)
        plt.show()

    def restart_new_story(self):
        if os.path.exists(STORY_FILE):
            os.remove(STORY_FILE)
        self.story_graph = AdaptiveStoryGraph()
        self.story_data = {"current_node": "start", "visited": [], "history": [], "stats": {}}
        self.history_stack = []
        save_story(self.story_data)
        self.show_story("start")
        messagebox.showinfo("New Story", "✨ A brand new AI-generated story has been created!")

# ------------------ Run ------------------
if __name__ == "__main__":
    app = StoryApp()
    app.mainloop()
