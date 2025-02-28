# PyKings.io

A linear programming tool for optimizing DraftKings NBA Showdown lineups. Built as a portfolio project to demonstrate optimization algorithms.

## Features

- Upload player data with projected points and salaries
- Generate optimal lineups using PuLP linear programming
- View multiple lineup variations with detailed breakdowns
- Responsive design for desktop and mobile devices

## Technology Stack

- **Backend**: Python, Flask, PuLP (linear programming)
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas

## How It Works

The optimizer uses linear programming to find the best possible lineup combinations:

1. **Upload Data**: Provide player data including names, projected points, and salaries
2. **Optimization**: The algorithm maximizes projected points while respecting the salary cap
3. **Results**: View multiple optimized lineups with detailed statistics

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python api/app.py
   ```
4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Download the template or example file
2. Fill in your player data
3. Upload the file and generate lineups
4. Review the optimized lineups

## License

MIT

## Created By

Hunter Lebow