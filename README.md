# MotionSim-Overlay

### An iOS-inspired anti-motion sickness overlay for PC gaming.

**MotionSim-Overlay** is a lightweight Windows utility designed to reduce simulation sickness (motion sickness) during gameplay. Inspired by the "Vehicle Motion Cues" feature in iOS, this tool creates a subtle, reactive grid of particles that move in sync with your mouse and keyboard inputs, providing your brain with a stable visual reference point.

---

## 🚀 Features

* **iOS-Style Motion Cues**: Real-time particle system that reacts to physical movement (Mouse & WASD).
* **Intelligent Input Handling**: Supports complex keyboard inputs without key conflicts; accurately tracks simultaneous WASD presses.
* **Dual-Column Layout**: Generates two columns of particles on both the left and right sides of the screen for maximum visual stability.
* **Highly Customizable**:
* **Sensitivity**: Fine-tune mouse and keyboard reaction force.
* **Physics**: Adjust friction and particle life for a smoother or snappier feel.
* **Visuals**: Customize particle radius, generation density, and line spacing.


* **Modern Discord-Inspired UI**: A clean, dark-themed control panel with bilingual (English/Chinese) support.
* **Low Performance Impact**: Built with PyQt6 and optimized threading to ensure zero impact on your game's FPS.

---

## 🛠️ Installation

### Prerequisites

* Python 3.8+
* Pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Chicagohucise/Simulation-Sickness.git
cd Simulation-Sickness

```


2. Install dependencies:
```bash
pip install PyQt6 pynput

```


3. Run the application:
```bash
python antimotion.py

```



---

## 🎮 How It Works

When you play 1st or 3rd person games, your eyes see motion on the screen that your inner ear doesn't feel, causing **Sensory Conflict**.

This overlay bridges that gap by:

1. **Mouse Tracking**: Moving particles in the opposite direction of your mouse look to simulate "inertia."
2. **Keyboard Sync**: Generating vertical streams of particles when pressing WASD to provide a sense of directional acceleration.
3. **Peripheral Vision**: By placing cues in your peripheral vision (the edges of the screen), it grounds your vestibular system without distracting you from the center-screen action.

---

## ⌨️ Controls

* **WASD**: Controls movement cues.
* **Mouse Move**: Controls rotational cues.
* **End Key**: Instantly exits the overlay program.

---

## 📝 Configuration

The **Control Panel** allows you to adjust:

* **Friction**: How "sluggish" or "slippery" the particles feel.
* **Max Particles**: Controls the visual density (higher = more dots).
* **Line Spacing**: The vertical gap between the dots in the WASD columns.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new motion patterns or performance optimizations, feel free to fork the repo and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

---
