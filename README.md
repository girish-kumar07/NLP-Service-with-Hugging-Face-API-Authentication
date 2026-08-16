# Bank Account Management System (Python OOP)

A simple Object-Oriented Banking System built in Python demonstrating core OOP principles, abstract base classes, custom exceptions, and modular project structure.

## Features
- **Savings Account**: Supports deposit, withdrawal validation, and automated interest calculation.
- **Checking Account**: Includes overdraft protection logic.
- **Transaction History**: Logs timestamps and transaction types per account.
- **Custom Exceptions**: Gracefully handles edge cases like invalid amounts and insufficient funds.

## Project Structure
- `models.py`: Contains `BankAccount` (ABC), `SavingsAccount`, `CheckingAccount`, and `Transaction` classes.
- `exceptions.py`: Custom error definitions.
- `main.py`: Test driver script.

## Run Locally
```bash
python main.py