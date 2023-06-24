<h1>Use the Tool on the Web!</h1>
Visit https://pykings.io to use this tool for free!

<h1>How it works</h1>
1. Download the sample excel, or download the template excel sheet to fill in your own DraftKings game data!
2. Upload the Excel Sheet and press the "Optimize" button.
3. The tool returns a table of the top 10 best lineups, stored in order from best lineup to 10th best lineup

The tool selects:
1. Your Captain, who earns 1.5x fantasy points at the price of 1.5x cost
2. The rest of the utility players to make a complete fantasy lineup
3. Each complete lineup will be crafted to maximize Fantasy Points per Game while exhausting the $50,000 budget constraint.

<h2>Under the Hood</h2>
The user uploads the Excel sheet and the data is read in and stored.  A custom optimization algorithm then finds the optimal lineup solution.
Each lineup solution considers:

1. Maximizing fantasy points per game
  
3. $50,000 overall budget,
  
   
5. Exactly 1 Captain (who costs 1.5x price and recieves a 1.5x boost on fantasy poinst)
  
7. Exactly 5 Utility players
   
8. Exactly 6 Players per lineup solution (1 Captain + 5 Utility).
   
10. Every player can only be used a maximum of 1 time per lineup solution.

A Solution pool of 10 is created, so that the user has 10 options to inspire them for their DraftKings lineup selection.  

<h3>Technologies Used</h3>

- Python (Flask, Gurobipy, OpenPyXL, Pandas)

- HTML
  
- CSS
  
- JavaScript

<h3>Custom Solutions</h3>
On DraftKings NBA "Captain Mode" fantasy challenges, enter a pool and download the "template Excel sheet".
Fill this template Excel sheet out with Player Name, Cost, and Projected Fantasy Points per Game.
**Make sure you are considering the correct data that is relative to a Utility player selection, not Captain.  

<h1>Future Considerations</h1>
Supporting more game modes and other fantasy sports hosted by DraftKings and potentially other Sportsbooks like Fanduel.

Visit https://pykings.io to use this tool free!





