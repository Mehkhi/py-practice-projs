# Simple & Compound Interest Calculator

A Python command-line program that calculates simple and compound interest for given principal amount, interest rate, and time period. The program provides detailed comparisons, year-by-year growth tables, and supports multiple scenarios.

## Features

### Core Features
- **Simple Interest Calculation**: Calculate interest using the formula I = P × R × T
- **Compound Interest Calculation**: Calculate interest using the formula A = P(1 + r/n)^(nt)
- **Input Validation**: Robust validation for all user inputs
- **Results Comparison**: Side-by-side comparison of simple vs compound interest
- **Formatted Output**: Clean, professional display of results

### Bonus Features
- **Year-by-Year Growth Table**: Detailed breakdown of growth over time
- **Multiple Scenario Comparison**: Compare different investment scenarios
- **CSV Export**: Export calculation results to CSV files
- **Flexible Compounding**: Support for different compounding frequencies

## Installation

No additional packages required! This program uses only Python standard library modules.

## Usage

### Basic Usage

Run the program:
```bash
python simple_interest_compound_calculator.py
```

Follow the prompts to enter:
- Principal amount (in dollars)
- Annual interest rate (as percentage)
- Time period (in years)
- Compounding frequency (optional, default: 1)

### Example Session

```
Simple & Compound Interest Calculator
========================================

Enter the following details:
Principal amount ($): 1000
Annual interest rate (%): 5
Time period (years): 10
Compounding frequency per year (default: 1): 12

============================================================
INTEREST CALCULATION RESULTS
============================================================
Principal Amount:     $1,000.00
Annual Interest Rate: 5.00%
Time Period:          10.0 years
Compounding Frequency: 12 times per year
------------------------------------------------------------
Simple Interest:      $500.00
Simple Total:         $1,500.00
Compound Interest:    $647.01
Compound Total:       $1,647.01
------------------------------------------------------------
Difference:           $147.01
Extra Earnings:       9.80%
============================================================
```

### Advanced Features

#### Year-by-Year Growth Table
When prompted, choose 'y' to see a detailed year-by-year breakdown:

```
================================================================================
YEAR-BY-YEAR GROWTH COMPARISON
================================================================================
Year   Compound Amount  Simple Amount   Year Interest  Total Interest
--------------------------------------------------------------------------------
1      $1,051.16        $1,050.00       $51.16         $51.16
2      $1,105.12        $1,100.00       $53.96         $105.12
3      $1,161.83        $1,150.00       $56.71         $161.83
...
```

#### Multiple Scenario Comparison
Compare different investment scenarios:

```
==========================================================================================
SCENARIO COMPARISON
==========================================================================================
Scenario   Principal    Rate    Time    Simple Total   Compound Total   Difference
------------------------------------------------------------------------------------
Scenario 1 $1,000       5.0%    10.0    $1,500.00      $1,647.01       $147.01
Scenario 2 $2,000       3.5%    15.0    $3,050.00      $3,351.45       $301.45
Scenario 3 $500         7.0%    5.0     $675.00        $701.28         $26.28
==========================================================================================
```

#### CSV Export
Export your calculations to a CSV file for further analysis:

```bash
Export data to CSV? (y/n): y
Enter filename (default: interest_calculation.csv): my_calculation.csv
Data exported successfully to 'my_calculation.csv'
```

## Formulas Used

### Simple Interest
```
I = P × R × T
```
Where:
- I = Interest amount
- P = Principal amount
- R = Annual interest rate (as decimal)
- T = Time in years

### Compound Interest
```
A = P(1 + r/n)^(nt)
I = A - P
```
Where:
- A = Total amount after time t
- P = Principal amount
- r = Annual interest rate (as decimal)
- n = Number of times interest is compounded per year
- t = Time in years
- I = Interest amount

## Testing

Run the unit tests to verify functionality:

```bash
python test_simple_interest_compound_calculator.py
```

The test suite includes:
- Basic calculation tests
- Edge case testing
- Input validation tests
- Year-by-year growth tests

## File Structure

```
22-simple-interest-compound-calculator/
├── simple_interest_compound_calculator.py    # Main program
├── test_simple_interest_compound_calculator.py # Unit tests
├── README.md                                 # This file
├── CHECKLIST.md                              # Feature checklist
└── SPEC.md                                   # Project specification
```

## Key Functions

- `calculate_simple_interest()`: Calculate simple interest
- `calculate_compound_interest()`: Calculate compound interest
- `get_year_by_year_growth()`: Generate year-by-year growth data
- `validate_input()`: Validate user input
- `display_results()`: Format and display results
- `compare_scenarios()`: Compare multiple scenarios
- `export_to_csv()`: Export data to CSV

## Error Handling

The program includes comprehensive error handling for:
- Invalid numeric input
- Negative values
- Empty input
- File I/O errors
- Keyboard interrupts

## Examples

### Example 1: Basic Calculation
- Principal: $1,000
- Rate: 5% annually
- Time: 10 years
- Compounding: Annually

**Results:**
- Simple Interest: $500.00
- Compound Interest: $628.89
- Difference: $128.89

### Example 2: Monthly Compounding
- Principal: $5,000
- Rate: 4% annually
- Time: 5 years
- Compounding: Monthly (12 times per year)

**Results:**
- Simple Interest: $1,000.00
- Compound Interest: $1,104.94
- Difference: $104.94

### Example 3: High Rate, Long Term
- Principal: $10,000
- Rate: 8% annually
- Time: 20 years
- Compounding: Quarterly (4 times per year)

**Results:**
- Simple Interest: $16,000.00
- Compound Interest: $48,289.47
- Difference: $32,289.47

## Contributing

This is a learning project. Feel free to:
- Add new features
- Improve the user interface
- Add more comprehensive tests
- Optimize calculations
- Add support for more investment types

## License

This project is part of a Python learning curriculum and is available for educational purposes.

## Notes

- All calculations use standard financial formulas
- Results are rounded to 2 decimal places for currency display
- The program handles edge cases like zero rates and very small amounts
- CSV export includes all year-by-year data for further analysis
