# Tip & Bill Splitter

A command-line application for calculating tips, adding tax, and splitting bills among multiple people with support for uneven splits and receipt export.

## Features

### Core Features
- **Tip Calculation**: Calculate tips based on customizable percentages
- **Tax Addition**: Add tax to subtotal with configurable rates
- **Even Splitting**: Split total evenly among any number of people
- **Detailed Breakdown**: Display subtotal, tax, tip, total, and per-person amounts

### Bonus Features
- **Uneven Splitting**: Split bills by custom percentages for each person
- **Multiple Rounding Strategies**: Choose from different rounding methods
- **Receipt Export**: Save receipts to JSON and text file formats
- **Receipt History**: View and manage saved receipt history
- **Input Validation**: Comprehensive validation for all user inputs

## How to Run

```bash
python tip_bill_splitter.py
```

## How to Use

### 1. Main Menu
When you start the app, you'll see the main menu:

```
[MONEY BAG] TIP & BILL SPLITTER MENU
===================================
1. Even split calculation
2. Uneven split calculation
3. View receipt history
4. Exit
```

### 2. Even Split Calculation

1. Select option 1 from the main menu
2. Enter the required information:
   - Subtotal amount
   - Tax rate (percentage)
   - Tip percentage
   - Number of people
3. Choose a rounding strategy
4. View the detailed breakdown
5. Save or export the receipt

### 3. Uneven Split Calculation

1. Select option 2 from the main menu
2. Enter bill information (subtotal, tax, tip)
3. Enter number of people
4. Specify percentage for each person
5. Choose rounding strategy
6. View both even and uneven breakdowns
7. Save or export the receipt

### 4. Rounding Strategies

Choose from four rounding options:

1. **None**: No rounding applied (full precision)
2. **Normal**: Standard rounding (0.005 rounds up)
3. **Always round up**: Always round up to next cent
4. **Always round down**: Always round down to previous cent

## Example Usage Session

### Even Split Example

```
[MONEY BAG] TIP & BILL SPLITTER MENU
===================================
1. Even split calculation
2. Uneven split calculation
3. View receipt history
4. Exit

Enter your choice (1-4): 1

[ABACUS] EVEN SPLIT CALCULATION
========================================
Enter subtotal amount: $100.00
Enter tax rate (%): 8.5
Enter tip percentage (%): 18
Enter number of people: 4

[REFRESH] ROUNDING STRATEGIES:
1. None (no rounding)
2. Normal (standard rounding)
3. Always round up
4. Always round down
Select rounding strategy (1-4): 2

============================================================
[MONEY BAG] BILL BREAKDOWN
============================================================

[CLIPBOARD] SUBTOTAL:           $100.00
[CHART UP] TAX RATE:           8.5%
[DOLLAR BILL] TAX AMOUNT:         $8.50
[TARGET] TIP PERCENTAGE:     18.0%
[GIFT HEART] TIP AMOUNT:         $18.00
----------------------------------------
[MONEY BAG] TOTAL:              $126.50
[PROFILES] SPLIT BETWEEN:      4 people
[RECEIPT] PER PERSON:         $31.63
[REFRESH] ROUNDING:           NORMAL

============================================================

Save receipt? (y/n): y
[PAGE] Receipt saved to 'receipts.json'

Export receipt to text file? (y/n): y
Enter filename (press Enter for default):
[PAGE] Receipt exported to 'receipt_20231207_153045.txt'
```

### Uneven Split Example

```
[MONEY BAG] TIP & BILL SPLITTER MENU
===================================
1. Even split calculation
2. Uneven split calculation
3. View receipt history
4. Exit

Enter your choice (1-4): 2

[BAR CHART] UNEVEN SPLIT CALCULATION
========================================
Enter subtotal amount: $150.00
Enter tax rate (%): 10
Enter tip percentage (%): 20
Enter number of people: 3

[BAR CHART] Enter percentage split for 3 people:
Person 1 percentage: 50
Person 2 percentage: 30
Person 3 percentage: 20

Total percentage entered: 100.0%
Continue with these percentages? (y/n): y

[REFRESH] ROUNDING STRATEGIES:
1. None (no rounding)
2. Normal (standard rounding)
3. Always round up
4. Always round down
Select rounding strategy (1-4): 2

============================================================
[MONEY BAG] BILL BREAKDOWN
============================================================

[CLIPBOARD] SUBTOTAL:           $150.00
[CHART UP] TAX RATE:           10.0%
[DOLLAR BILL] TAX AMOUNT:         $15.00
[TARGET] TIP PERCENTAGE:     20.0%
[GIFT HEART] TIP AMOUNT:         $30.00
----------------------------------------
[MONEY BAG] TOTAL:              $195.00
[PROFILES] SPLIT BETWEEN:      3 people
[RECEIPT] PER PERSON:         $65.00
[REFRESH] ROUNDING:           NORMAL

============================================================

============================================================
[BAR CHART] UNEVEN SPLIT BREAKDOWN
============================================================

[PROFILE] Person 1:
   Percentage: 50.0%
   Amount: $97.50

[PROFILE] Person 2:
   Percentage: 30.0%
   Amount: $58.50

[PROFILE] Person 3:
   Percentage: 20.0%
   Amount: $39.00

[MONEY BAG] Total: $195.00
============================================================
```

## Receipt Features

### JSON Receipt Storage
All receipts are automatically saved to `receipts.json`:

```json
[
  {
    "timestamp": "2023-12-07T15:30:45.123456",
    "date": "2023-12-07",
    "time": "15:30:45",
    "bill_data": {
      "subtotal": 100.0,
      "tax_rate": 8.5,
      "tax_amount": 8.5,
      "tip_percentage": 18.0,
      "tip_amount": 18.0,
      "total": 126.5,
      "num_people": 4,
      "per_person": 31.63,
      "rounding_strategy": "normal"
    }
  }
]
```

### Text Receipt Export
Export formatted text receipts for sharing or printing:

```
============================================================
[MONEY BAG] RECEIPT
============================================================
Date: 2023-12-07 15:30:45
Rounding Strategy: NORMAL

BILL BREAKDOWN:
----------------------------------------
Subtotal:           $100.00
Tax Rate:           8.5%
Tax Amount:         $8.50
Tip Percentage:     18.0%
Tip Amount:         $18.00
----------------------------------------
Total:              $126.50
Split Between:      4 people
Per Person:         $31.63
============================================================
```

### Receipt History
View your last 10 receipts with summary information:
- Date and time
- Total amount
- Number of people
- Per-person amount
- Split type (even/uneven)

## Rounding Strategies

### Strategy Comparison

For a total of $126.50 split among 4 people:

| Strategy | Per Person | Total |
|----------|------------|-------|
| None | $31.625 | $126.50 |
| Normal | $31.63 | $126.52 |
| Always Up | $31.63 | $126.52 |
| Always Down | $31.62 | $126.48 |

### When to Use Each Strategy

- **None**: Maximum precision, good for accounting
- **Normal**: Standard everyday use
- **Always Up**: Ensures you never underpay
- **Always Down**: Conservative rounding, good for budgeting

## Input Validation

The app includes comprehensive input validation:

### Numeric Inputs
- **Subtotal**: Must be positive number
- **Tax Rate**: 0-100%
- **Tip Percentage**: 0-100%
- **Number of People**: Positive integer
- **Percentages**: Non-negative numbers

### Error Handling
- Invalid number formats
- Out-of-range values
- Empty inputs
- Non-numeric characters

## Advanced Features

### Uneven Split Normalization
When percentages don't sum to 100%, the app automatically normalizes them:

```
Input: [30%, 20%] (sum = 50%)
Normalized: [60%, 40%] (sum = 100%)
```

### Rounding Error Correction
For uneven splits, the app adjusts for rounding errors to ensure the total matches exactly.

### Multiple Session Support
Receipt history persists across multiple application sessions.

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_tip_bill_splitter.py -v
```

The test suite includes:
- **30 test methods** covering all calculator functionality
- **Calculation tests** for tip, tax, and splitting
- **Rounding strategy tests** for all rounding options
- **Input validation tests** for error handling
- **File I/O tests** for receipt operations
- **Integration tests** for complete workflows

## Code Structure

### Main Classes
- `TipBillSplitter`: Core calculator class with all functionality
- `RoundingStrategy`: Enum for rounding strategy options

### Key Methods
- `calculate_bill()`: Complete bill calculation with all components
- `calculate_even_split()`: Even split among people
- `calculate_uneven_split()`: Uneven split by percentages
- `save_receipt()`: Save receipt to JSON file
- `export_receipt_to_text()`: Export formatted text receipt
- `view_receipt_history()`: Display saved receipts

### Helper Functions
- `calculate_tax()`: Tax amount calculation
- `calculate_tip()`: Tip amount calculation
- `apply_rounding()`: Apply rounding strategies
- `get_valid_float_input()`: Validated float input
- `get_valid_int_input()`: Validated integer input

## Use Cases

### Restaurant Bills
Split restaurant checks with tax and tip among friends.

### Group Expenses
Divide shared expenses like rent, utilities, or group purchases.

### Event Planning
Calculate costs for events with different contribution levels.

### Business Expenses
Split business expenses among departments or projects.

### Budget Planning
Plan expenses with different rounding strategies for accuracy.

## File Management

### Auto-generated Files
- `receipts.json`: All receipt history
- `receipt_YYYYMMDD_HHMMSS.txt`: Exported text receipts

### File Locations
- Files are saved in the same directory as the application
- JSON files use UTF-8 encoding for international characters
- Text files use plain text format for maximum compatibility

## Requirements

- Python 3.7 or higher
- No external dependencies required
- Cross-platform compatibility (Windows, macOS, Linux)

## File Structure

```
20-tip-bill-splitter/
├── tip_bill_splitter.py           # Main application
├── test_tip_bill_splitter.py      # Unit tests
├── README.md                      # This file
├── SPEC.md                        # Project specifications
├── CHECKLIST.md                   # Project checklist
├── receipts.json                  # Receipt history (auto-generated)
└── receipt_*.txt                  # Exported receipts (auto-generated)
```

## Troubleshooting

### Common Issues

**Invalid Input Errors:**
- Ensure numbers are entered correctly (e.g., 25.50 not 25,50)
- Check that percentages are within 0-100 range
- Verify number of people is a positive integer

**File Permission Errors:**
- Ensure the application has write permissions in its directory
- Check that the disk isn't full
- Verify the directory isn't read-only

**Rounding Discrepancies:**
- Different rounding strategies produce different results
- Uneven splits may have small rounding adjustments
- Total may not exactly equal sum of parts due to rounding

**Receipt History Issues:**
- JSON files may become corrupted if the application crashes
- Delete the receipts.json file to start fresh
- Back up important receipts regularly

## Performance

### Large Numbers
The app handles large values efficiently:
- Supports amounts up to 999,999.99
- Handles up to 999 people in a split
- Processes calculations instantly

### Memory Usage
- Minimal memory footprint
- Receipt history grows linearly with usage
- Text exports are temporary and cleaned up automatically

## Extension Ideas

### Future Enhancements
- Currency support for different countries
- Discount and coupon calculations
- Split by item (who ordered what)
- Integration with payment apps
- GUI interface
- Mobile app version

### Data Analysis
- Spending trends over time
- Average tip percentages
- Popular split patterns
- Tax rate statistics

Enjoy splitting bills easily with the Tip & Bill Splitter! [MONEY BAG]
