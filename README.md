# SnappySplit
A Split App that makes adding splits in Splitwise easy. If you are a student, living in a shared house, feel like adding splits is hard; this app is for you!

## Overview

The SnappySplit App simplifies the process of adding expense splits to the Splitwise app. Instead of manually entering each item, this tool takes a structured text file as input and processes it to generate a formatted expense breakdown for easy addition to Splitwise.

## Features

- Parses a structured text file containing expense details.
- Supports multiple participants for each item.
- Handles additional charges and discounts.
- Automatically calculates final amounts after adjustments.

## Using the Application

Clone the Git Repo

```
git clone https://github.com/tantalum-73/SnappySplit.git
```

```
cd SnappySplit
```

Use the test-bill to generate the split.
```
python bill_splitter.py test-bill.txt
```

## Input File Format

The input text file should follow this format:
```
Item,[participants],price
Additional Charge: value
Discount: percentage or value
```

Example:
```
Pizza,[Keerthana],18.65
Milk,[Yakgna,Rohan,Keerthana],6.94
Salt,[Yakgna,Rohan,Keerthana],1.85
charge:2.50
discount:20%
```

Output:

```
=== Bill Split Summary ===

Items:
- Pizza,: $18.65
  Split between: Keerthana
  Per person: $18.65
- Milk,: $6.94
  Split between: Yakgna, Rohan, Keerthana
  Per person: $2.31
- Salt,: $1.85
  Split between: Yakgna, Rohan, Keerthana
  Per person: $0.62

Subtotal: $27.44
Additional Charge: $2.50
Discount: 20%

Amount owed per person:
Keerthana: $18.84
Rohan: $2.56
Yakgna: $2.55
```

## Explanation:

- Dahi,[r,y,k],8.07 → "Dahi" costs $8.07 and is shared among r, y, and k.
- Bananas,[r],1.85 → "Bananas" costs $1.85 and is assigned to r.
- charge:-0.51 → Additional charge of -0.51 (negative values can represent deductions).
- discount:20% → A 20% discount is applied to the total.

## How It Works

- Read the input file.
- Parse each item and participant.
- Calculate the total amount, considering additional charges and discounts.
- Generate an output formatted for easy entry into Splitwise.

## Usage

- Prepare a structured input file as shown above.
- Run the Bill Split App with the input file.
- Copy the generated output and paste it into Splitwise.

## Future Enhancements

- Direct integration with the Splitwise API.
- Support for different currencies.
- Customizable splitting rules.
