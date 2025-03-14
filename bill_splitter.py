#!/usr/bin/env python3

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Tuple, Union
import sys

class BillEntry:
    def __init__(self, item: str, people: List[str], price: Decimal):
        self.item = item.strip()
        self.people = [p.strip() for p in people]
        self.price = price
        self.price_per_person = price / len(people)

class BillSplitter:
    def __init__(self):
        self.entries: List[BillEntry] = []
        self.charge: Decimal = Decimal('0')
        self.discount: Tuple[str, Decimal] = ('value', Decimal('0'))
        self.total_before_adjustments: Decimal = Decimal('0')
        self.people_set: set = set()  # All people in current bill section

    def parse_price(self, price_str: str) -> Decimal:
        """Convert string price to Decimal, raising ValueError if invalid."""
        try:
            return Decimal(price_str.strip())
        except:
            raise ValueError(f"Invalid price format: {price_str}")

    def parse_people_list(self, people_str: str) -> List[str]:
        """Extract people list from string format [A,B,C]."""
        match = re.match(r'\[(.*?)\]', people_str.strip())
        if not match:
            raise ValueError(f"Invalid people list format: {people_str}")
        return [p.strip() for p in match.group(1).split(',')]

    def parse_line(self, line: str) -> None:
        """Parse a single line from the bill file."""
        line = line.strip()
        if not line:
            return

        lower_line = line.lower()
        if lower_line.startswith('charge:'):
            self.charge = self.parse_price(line.split(':', 1)[1])
            return

        if lower_line.startswith('discount:') or lower_line.startswith('disount:'):
            discount_value = line.split(':', 1)[1].strip()
            if discount_value.endswith('%'):
                percentage = self.parse_price(discount_value[:-1])
                self.discount = ('percentage', percentage)
            else:
                self.discount = ('value', self.parse_price(discount_value))
            return

        try:
            # Split the line into parts before and after the closing bracket
            item_and_people, price_part = line.split('],', 1)
            # Split the first part to get item and people list
            item, people_str = item_and_people.split('[', 1)
            # Add back the bracket to make it a valid format for parse_people_list
            people_str = '[' + people_str + ']'

            price = self.parse_price(price_part)
            people = self.parse_people_list(people_str)

            if not people:
                raise ValueError(f"Empty people list for item: {item}")

            # Update people set with participants in this bill section
            self.people_set.update(people)
            self.entries.append(BillEntry(item, people, price))
            self.total_before_adjustments += price

        except ValueError as e:
            raise ValueError(f"Error parsing line '{line}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid line format: {line}")

    def calculate_shares(self) -> Dict[str, Decimal]:
        """Calculate how much each person owes."""
        # Initialize shares and individual totals for people who participated
        shares = {person: Decimal('0') for person in self.people_set}
        individual_totals = {person: Decimal('0') for person in self.people_set}

        # Calculate base shares and track individual totals
        for entry in self.entries:
            share_per_person = entry.price_per_person
            for person in entry.people:
                shares[person] += share_per_person
                individual_totals[person] += share_per_person

        # Calculate total spending to determine proportions
        total_spending = sum(individual_totals.values())

        if total_spending > 0:  # Prevent division by zero
            # Apply charge proportionally based on spending
            if self.charge != 0:
                for person in shares:
                    proportion = individual_totals[person] / total_spending
                    shares[person] += self.charge * proportion

            # Apply discount proportionally
            if self.discount[1] != 0:
                if self.discount[0] == 'percentage':
                    # Calculate total after charge for discount calculation
                    total_after_charge = self.total_before_adjustments + self.charge
                    # Calculate percentage first
                    percentage = self.discount[1] / Decimal('100')
                    # Calculate total discount amount and round to 2 decimals
                    discount_amount = (total_after_charge * percentage).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    discount_amount = self.discount[1]

                for person in shares:
                    proportion = individual_totals[person] / total_spending
                    shares[person] -= discount_amount * proportion

        # Calculate total after adjustments
        total_after_adjustments = sum(shares.values())

        # Round all amounts to 2 decimal places, preserving the total
        rounded_shares = {}
        running_total = Decimal('0')

        # Sort people to ensure consistent rounding
        sorted_people = sorted(shares.keys())

        # Round all but the last person's share
        for person in sorted_people[:-1]:
            rounded_amount = shares[person].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            rounded_shares[person] = rounded_amount
            running_total += rounded_amount

        # Last person gets the remainder to ensure total adds up exactly
        last_person = sorted_people[-1]
        rounded_shares[last_person] = (total_after_adjustments - running_total).quantize(Decimal('0.01'))

        return rounded_shares

    def format_currency(self, amount: Decimal) -> str:
        """Format decimal amount as currency string."""
        return f"${amount:.2f}"

    def process_file(self, filename: str) -> None:
        """Process the bill file and print the results."""
        try:
            with open(filename, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        self.parse_line(line)
                    except ValueError as e:
                        print(f"Error on line {line_num}: {str(e)}")
                        return

            # Calculate and display results
            shares = self.calculate_shares()

            print("\n=== Bill Split Summary ===\n")

            print("Items:")
            for entry in self.entries:
                print(f"- {entry.item}: {self.format_currency(entry.price)}")
                print(f"  Split between: {', '.join(entry.people)}")
                print(f"  Per person: {self.format_currency(entry.price_per_person)}")

            print(f"\nSubtotal: {self.format_currency(self.total_before_adjustments)}")

            if self.charge != 0:
                print(f"Additional Charge: {self.format_currency(self.charge)}")

            if self.discount[1] != 0:
                if self.discount[0] == 'percentage':
                    print(f"Discount: {self.discount[1]}%")
                else:
                    print(f"Discount: {self.format_currency(self.discount[1])}")

            print("\nAmount owed per person:")
            for person in sorted(shares.keys()):
                print(f"{person}: {self.format_currency(shares[person])}")

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error processing file: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python bill_splitter.py <bill_file>")
        sys.exit(1)

    splitter = BillSplitter()
    splitter.process_file(sys.argv[1])

if __name__ == "__main__":
    main()