# BMI & Calorie Calculator

A comprehensive command-line program that calculates BMI (Body Mass Index) and estimates daily calorie needs using the Harris-Benedict equation. The program supports both metric and imperial units, provides weight goal calculations, and tracks calculation history.

## Features

### Required Features [OK]
- **BMI Calculation**: Calculate BMI from height and weight
- **Unit Support**: Support for both metric (kg, meters) and imperial (lbs, inches) units
- **BMI Categories**: Display BMI category (underweight/normal/overweight/obese)
- **Calorie Estimation**: Basic calorie estimation using Harris-Benedict formula

### Bonus Features [OK]
- **Activity Level Multiplier**: Adjust calorie needs based on activity level
- **Goal Weight Calculator**: Calculate timeline and calorie adjustments for weight goals
- **History Tracking**: Track calculation history over time with JSON storage

## What the Project Does

This program helps users:
1. **Calculate BMI**: Determine their Body Mass Index and corresponding health category
2. **Estimate Calorie Needs**: Calculate Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE)
3. **Plan Weight Goals**: Get realistic timelines and calorie targets for weight loss or gain
4. **Track Progress**: Save and view calculation history over time

## How to Run

### Prerequisites
- Python 3.7 or higher
- No additional packages required (uses only standard library)

### Running the Program

1. **Navigate to the project directory**:
   ```bash
   cd 21-bmi-calorie-calculator
   ```

2. **Run the main program**:
   ```bash
   python bmi_calorie_calculator.py
   ```

3. **Run tests** (optional):
   ```bash
   python test_bmi_calorie_calculator.py
   ```

## Example Usage

### BMI Calculation
```
--- BMI CALCULATION ---
Choose unit system:
1. Metric (kg, meters)
2. Imperial (lbs, inches)
Enter choice (1-2): 1
Enter your weight in kg: 70
Enter your height in meters: 1.75

--- RESULTS ---
Weight: 70.0 kg
Height: 1.75 meters
BMI: 22.86
Category: Normal weight
```

### Calorie Needs Calculation
```
--- CALORIE NEEDS CALCULATION ---
Choose unit system:
1. Metric (kg, meters)
2. Imperial (lbs, inches)
Enter choice (1-2): 2
Enter your weight in lbs: 154
Enter your height in inches: 69
Enter your age: 30
Enter your gender:
1. Male
2. Female
Enter choice (1-2): 1
Select your activity level:
1. Sedentary (little to no exercise)
2. Light (light exercise 1-3 days/week)
3. Moderate (moderate exercise 3-5 days/week)
4. Active (heavy exercise 6-7 days/week)
5. Very Active (very heavy exercise, physical job)
Enter choice (1-5): 3

--- RESULTS ---
Weight: 154.0 lbs
Height: 69.0 inches
Age: 30 years
Gender: Male
Activity Level: Moderate
BMR (Basal Metabolic Rate): 1740 calories/day
TDEE (Total Daily Energy Expenditure): 2697 calories/day
```

### Weight Goal Calculation
```
--- WEIGHT GOAL CALCULATION ---
Choose unit system:
1. Metric (kg, meters)
2. Imperial (lbs, inches)
Enter choice (1-2): 1
Enter your current weight in kg: 80
Enter your target weight in kg: 70
Enter your height in meters: 1.75
Enter your age: 30
Enter your gender:
1. Male
2. Female
Enter choice (1-2): 1
Select your activity level:
1. Sedentary (little to no exercise)
2. Light (light exercise 1-3 days/week)
3. Moderate (moderate exercise 3-5 days/week)
4. Active (heavy exercise 6-7 days/week)
5. Very Active (very heavy exercise, physical job)
Enter choice (1-5): 3

--- RESULTS ---
Current Weight: 80.0 kg
Target Weight: 70.0 kg
Current TDEE: 2697 calories/day

Goal: Loss
Estimated Time: 13.3 weeks
Daily Calorie Adjustment: 577 calories
Target Daily Calories: 2120 calories/day
```

## Program Structure

### Main Menu
The program provides a user-friendly menu with the following options:
1. **Calculate BMI**: Quick BMI calculation and category
2. **Calculate Calorie Needs**: Comprehensive calorie estimation
3. **Calculate Weight Goal**: Weight loss/gain planning
4. **View History**: Browse past calculations
5. **Exit**: Quit the program

### Key Components

- **BMICalculator Class**: Core calculation logic
- **Input Validation**: Robust error handling for user input
- **History Management**: JSON-based storage for calculation history
- **Unit Conversion**: Automatic conversion between metric and imperial units

## Technical Details

### BMI Calculation
- **Formula**: BMI = weight(kg) / height(m)²
- **Categories**: Underweight (<18.5), Normal (18.5-24.9), Overweight (25-29.9), Obese (≥30)

### Calorie Estimation
- **BMR Formula (Harris-Benedict)**:
  - Male: BMR = 88.362 + (13.397 × weight) + (4.799 × height) - (5.677 × age)
  - Female: BMR = 447.593 + (9.247 × weight) + (3.098 × height) - (4.330 × age)
- **Activity Multipliers**:
  - Sedentary: 1.2
  - Light: 1.375
  - Moderate: 1.55
  - Active: 1.725
  - Very Active: 1.9

### Weight Goal Calculation
- **Safe Rate**: 0.75 kg per week
- **Calorie Conversion**: 1 kg = 7700 calories
- **Timeline**: Based on weight difference and safe rate

## File Structure

```
21-bmi-calorie-calculator/
├── bmi_calorie_calculator.py    # Main program
├── test_bmi_calorie_calculator.py  # Unit tests
├── README.md                    # This file
├── CHECKLIST.md                 # Feature checklist
├── SPEC.md                      # Project specification
└── bmi_history.json            # Calculation history (created at runtime)
```

## Error Handling

The program includes comprehensive error handling:
- **Input Validation**: Prevents crashes on invalid input
- **Range Checking**: Ensures values are within reasonable bounds
- **Type Conversion**: Handles non-numeric input gracefully
- **File Operations**: Safe JSON file handling for history

## Testing

The project includes comprehensive unit tests covering:
- BMI calculations (metric and imperial)
- BMI category classification
- BMR calculations for both genders
- TDEE calculations with different activity levels
- Weight goal calculations
- History management
- Input validation

Run tests with:
```bash
python test_bmi_calorie_calculator.py
```

## Learning Objectives

This project demonstrates:
- **Python Fundamentals**: Variables, functions, classes, control flow
- **Input/Output**: User interaction and data display
- **Data Structures**: Lists, dictionaries, JSON handling
- **Error Handling**: Try/except blocks and input validation
- **File I/O**: Reading and writing JSON files
- **Mathematical Calculations**: BMI, BMR, and calorie formulas
- **Unit Testing**: Test-driven development practices

## Future Enhancements

Potential improvements:
- Graphical user interface
- Database storage for history
- More detailed nutritional information
- Integration with fitness tracking APIs
- Mobile app version
- Advanced goal tracking with progress charts

## Contributing

This is a learning project, but suggestions for improvements are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of a Python learning curriculum and is available for educational purposes.

---

**Note**: This calculator provides estimates for educational purposes. For health-related decisions, consult with healthcare professionals.
