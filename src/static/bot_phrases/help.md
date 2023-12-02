# Help Menu

**Commands:**
- `/start` - Start the bot
- `/help` - Show this help menu
- `/report` - Generate a report of your expenses


**Examples:**
- `/report` - Generate a report of your expenses
- `/report 2020-01` - Generate a report of your expense for current month
- `/report 2020-01-01 2020-01-31` - Generate a report of your expense for the month of January 2020
- `/report 2020-01-31` - Generate a report of your expense for 31st January 2020

**Add Spending:**
Here is spending format:
- **Name** _<class 'str'>_;
- **Category** _<class 'str'>_;
- **Description** _<class 'str'>_;
- **Cost** _<class 'float'>_;
- **Currency** _typing.Literal['USD', 'RUB', 'GEL', 'EUR', 'LIR', 'DUR']_;
- **Source** _typing.Literal['Cash', 'Card', 'Bank', 'Crypto']_;
- **Date** _<class 'datetime.date'>_;

**Examples**:
```text
Lunch;10.5;Food;Nice meal;USD;Cash;2021-07-15
```
**Bulk Example**:
```text
Lunch;10.5;Food;Nice meal;USD;Cash;2021-07-15|
Lunch;10.5;Food;Nice meal;USD;Cash;2021-07-15|
Lunch;10.5;Food;Nice meal;USD;Cash;2021-07-15|
Lunch;10.5;Food;Nice meal;USD;Cash;2021-07-15
```
