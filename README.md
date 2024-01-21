# Budget Planner Backend

Welcome to the Budget Planner backend, a robust solution for managing financial data.

## Getting Started

This backend is designed to work seamlessly with the Budget Planner frontend. Follow the steps below to set up and run the backend server.

### Prerequisites

Ensure you have Python installed on your machine.

### Installation

1. Clone the repository to your local machine:

 
    git clone https://github.com/bjugoy/budgetPlannerBE.git


### Database Initialization
To set up the database and tables, execute the following command in your terminal:

    python main.py

### Starting the Backend Server

To launch the backend server, use the following command:

    uvicorn main:app --reload

The server will be accessible at http://127.0.0.1:8000

### MoSCow
2.1. Must-Requirements
1. The application must include user authentication through E-mail address and password.

2. The application must provide the user with the ability to create entries for incomes and expenses.

3. The application’s entries must consist of the amount, the category, and an optional comment.

4. The application must provide the user with the ability to set incomes to monthly or singular incomes.

5. The application must provide the user with the ability to set expenses to monthly or singular expenses.

6. The application must provide the user with the ability to separate income and expenses into categories.

7. The application’s fixed income categories must consist of: “salary”, “investment dividends”, “capital gain”, “additional income”.

8. The application’s fixed expense categories must consist of: “food”, “bills”, “subscriptions”, “groceries”, “medicine”, “investments”, “clothing”, “rent”, “insurance”, “car”.

9. The application must calculate the total income, total expenses and provide the remaining balance.

10. The application must use minimal graphics to provide a simple and attractive user interface.

2.2. Should-Requirements
1. The application should allow the user to set saving goals.

2. The application should remind the user of upcoming bill payments or other expenses through notifications.

3. The application should remind the user of upcoming bill payments or other expenses through pop-ups upon opening the application.

2.3. Could-Requirements
1. The application could allow the user to create customizable income and expense categories.

2. The application could provide the user with the ability to create budget plans consisting of expense entries.

3. The application could provide the user with saving plans that calculate and set aside an amount from the user’s expenses.

4. The application could provide the user with yearly financial statistics.

2.4. Won’t-Requirements
1. The application won’t have collaboration features that allow shared budgeting among family members.

2. The application won’t have advanced tax optimization or tax filling features.

3. The application won’t be able to synchronize the user’s bank account.

4. The application won’t allow the user to change the expense and income time interval from monthly to a custom interval.
