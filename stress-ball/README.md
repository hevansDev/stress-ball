# stress-ball stress-gauge

Put a stress-gauge in a stress-ball

![](stress-ball.gif)

## Requirements

- Python 3.13+
- Raspberry Pi Pico with force sensor connected via USB
- macOS, Windows, or Linux

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/stress-ball.git
cd stress-ball/stress-ball
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install briefcase
```
## Running the App

### Development Mode

```bash
briefcase dev
```
Build and Run

```bash
briefcase build
briefcase run
```