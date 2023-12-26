from main import session
from database_models.financials import Income, Expenses

# Testdaten für Income
income_data = [
    Income(source_of_income="Gehalt", amount_of_income=3000.00),
    Income(source_of_income="Nebenjob", amount_of_income=500.00)
]

# Testdaten für Expenses
expenses_data = [
    Expenses(source_of_expenses="Miete", amount_of_expense=1200.00),
    Expenses(source_of_expenses="Lebensmittel", amount_of_expense=400.00)
]

# Hinzufügen von Income und Expese- daten zur Session
for income in income_data:
    session.add(income)

for expense in expenses_data:
    session.add(expense)

#normaler commit zur db
session.commit()
