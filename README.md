# AI-adaptive-story-generator
Adaptive Story is an interactive storytelling project built with Python, Tkinter, and NetworkX and AI. It lets users navigate a dynamic, branching storyline — where every decision creates a new path in the story’s graph.  The project features an animated top-down hierarchy. It also supports backtracking, data persistence via JSON, and smooth graph 
AI-Driven Adaptive Story Graph System
🎯 An intelligent storytelling system powered by AI, graph algorithms, and adaptive learning.
📘 Overview

The AI-Driven Adaptive Story Graph System is an interactive storytelling application that uses Artificial Intelligence, Graph Theory, and User Interaction to create a dynamic, personalized narrative experience.
It intelligently analyzes story paths, learns from user choices, and recommends the most engaging and meaningful story progression in real-time.

🧩 Features

✅ AI Recommendation Engine – Suggests the best next move based on risk, reward, emotion, and novelty.
✅ Adaptive Learning – Learns from user decisions to personalize future story paths.
✅ Dynamic Story Graph – Generates and visualizes story structures using graph algorithms.
✅ Interactive GUI – Clean, user-friendly interface built using Tkinter.
✅ Data Persistence – Saves progress, visited nodes, and story history in JSON.
✅ Graph Visualization – Uses Matplotlib to show the evolving story as a dynamic graph.
✅ Expandable with NLP – Can integrate models like GPT-2 for natural language story generation.

🏗️ System Architecture
+------------------------+
|     User Interface     |
|  (Tkinter GUI Window)  |
+-----------+------------+
            |
            ▼
+------------------------+
|   AI Recommendation    |
|  (Heuristic Scoring)   |
+-----------+------------+
            |
            ▼
+------------------------+
|     Story Graph        |
| (NetworkX Directed G)  |
+-----------+------------+
            |
            ▼
+------------------------+
| Data Management (JSON) |
| - Save/Load Progress   |
| - Store History        |
+------------------------+
            |
            ▼
+------------------------+
| Graph Visualization    |
| (Matplotlib Animation) |
+------------------------+

💡 Technologies Used
Component	Technology
Language	Python 3.x
GUI Framework	Tkinter & ttk
Graph Algorithms	NetworkX
Visualization	Matplotlib
Data Storage	JSON
AI Logic	Heuristic Scoring + Adaptive Learning
Optional NLP Extension	Hugging Face Transformers (GPT-2, DistilGPT2)
🧠 How It Works

The system loads or generates a story graph, where each node represents a story point.

For each decision point, the AI engine evaluates all possible choices using heuristic scores.

The system recommends the best path based on user preferences and learning data.

The story graph is visualized and animated as the player progresses.

The system saves user progress for continuation or analysis.
