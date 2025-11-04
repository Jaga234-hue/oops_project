import json
import os
from datetime import datetime
from abc import ABC, abstractmethod

# 🧩 Expense Class
class Expense:
    def __init__(self, amount, category, description="", date=None):
        self._amount = float(amount)
        self._category = category
        self._description = description
        self._date = date if date else datetime.now().strftime("%Y-%m-%d")
    
    # Encapsulation - Getters and Setters
    def get_amount(self):
        return self._amount
    
    def set_amount(self, amount):
        self._amount = float(amount)
    
    def get_category(self):
        return self._category
    
    def set_category(self, category):
        self._category = category
    
    def get_description(self):
        return self._description
    
    def set_description(self, description):
        self._description = description
    
    def get_date(self):
        return self._date
    
    def set_date(self, date):
        self._date = date
    
    def to_dict(self):
        """Convert expense to dictionary for JSON storage"""
        return {
            'amount': self._amount,
            'category': self._category,
            'description': self._description,
            'date': self._date,
            'type': 'regular'
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Expense object from dictionary"""
        return cls(
            amount=data['amount'],
            category=data['category'],
            description=data['description'],
            date=data['date']
        )
    
    def __str__(self):
        return f"{self._category}: ₹{self._amount:.2f} - {self._description} ({self._date})"

# 🧩 Inheritance - RecurringExpense Class
class RecurringExpense(Expense):
    def __init__(self, amount, category, description="", date=None, frequency="monthly"):
        super().__init__(amount, category, description, date)
        self._frequency = frequency
    
    def get_frequency(self):
        return self._frequency
    
    def set_frequency(self, frequency):
        self._frequency = frequency
    
    def to_dict(self):
        data = super().to_dict()
        data['frequency'] = self._frequency
        data['type'] = 'recurring'
        return data
    
    @classmethod
    def from_dict(cls, data):
        expense = cls(
            amount=data['amount'],
            category=data['category'],
            description=data['description'],
            date=data['date'],
            frequency=data.get('frequency', 'monthly')
        )
        return expense
    
    def __str__(self):
        return f"{self._category}: ₹{self._amount:.2f} - {self._description} ({self._frequency}, {self._date})"

# 🧩 Category Class
class Category:
    def __init__(self, name, budget_limit=0):
        self._name = name
        self._budget_limit = float(budget_limit)
    
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name
    
    def get_budget_limit(self):
        return self._budget_limit
    
    def set_budget_limit(self, limit):
        self._budget_limit = float(limit)
    
    def to_dict(self):
        return {
            'name': self._name,
            'budget_limit': self._budget_limit
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            budget_limit=data['budget_limit']
        )
    
    def __str__(self):
        return f"{self._name} (Budget: ₹{self._budget_limit:.2f})"

# 🧩 Polymorphism - Report Classes
class Report(ABC):
    @abstractmethod
    def generate_report(self):
        pass

class MonthlyReport(Report):
    def __init__(self, expenses, month=None):
        self.expenses = expenses
        self.month = month if month else datetime.now().strftime("%Y-%m")
    
    def generate_report(self):
        monthly_expenses = [e for e in self.expenses if e.get_date().startswith(self.month)]
        total = sum(exp.get_amount() for exp in monthly_expenses)
        
        report = f"📊 Monthly Report for {self.month}\n"
        report += "=" * 40 + "\n"
        report += f"Total Expenses: ₹{total:.2f}\n"
        report += "Category Breakdown:\n"
        
        categories = {}
        for exp in monthly_expenses:
            cat = exp.get_category()
            categories[cat] = categories.get(cat, 0) + exp.get_amount()
        
        for cat, amount in categories.items():
            report += f"  {cat}: ₹{amount:.2f}\n"
        
        return report

class CategoryReport(Report):
    def __init__(self, expenses, categories):
        self.expenses = expenses
        self.categories = categories
    
    def generate_report(self):
        report = "📊 Category-wise Report\n"
        report += "=" * 40 + "\n"
        
        for category in self.categories:
            cat_name = category.get_name()
            cat_expenses = [e for e in self.expenses if e.get_category() == cat_name]
            total = sum(exp.get_amount() for exp in cat_expenses)
            budget_limit = category.get_budget_limit()
            
            report += f"\n{cat_name}:\n"
            report += f"  Total Spent: ₹{total:.2f}\n"
            report += f"  Budget Limit: ₹{budget_limit:.2f}\n"
            
            if budget_limit > 0:
                remaining = budget_limit - total
                if remaining >= 0:
                    report += f"  Remaining: ₹{remaining:.2f} ✅\n"
                else:
                    report += f"  Over Budget: ₹{abs(remaining):.2f} ⚠️\n"
        
        return report

# 🧩 ExpenseManager Class
class ExpenseManager:
    def __init__(self, data_file="expenses.json", categories_file="categories.json"):
        self.data_file = data_file
        self.categories_file = categories_file
        self.expenses = []
        self.categories = []
        self._initialize_files()
        self._load_data()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        # Initialize expenses file
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as file:
                json.dump([], file, indent=2)
            print(f"✅ Created new expenses file: {self.data_file}")
        
        # Initialize categories file
        if not os.path.exists(self.categories_file):
            default_categories = [
                {"name": "Food", "budget_limit": 5000},
                {"name": "Travel", "budget_limit": 3000},
                {"name": "Entertainment", "budget_limit": 2000},
                {"name": "Shopping", "budget_limit": 4000},
                {"name": "Bills", "budget_limit": 6000},
                {"name": "Healthcare", "budget_limit": 1500},
                {"name": "Education", "budget_limit": 3000},
                {"name": "Other", "budget_limit": 1000}
            ]
            with open(self.categories_file, 'w') as file:
                json.dump(default_categories, file, indent=2)
            print(f"✅ Created new categories file: {self.categories_file}")
    
    def _load_data(self):
        """Load all data from JSON files"""
        self._load_expenses()
        self._load_categories()
    
    def _load_expenses(self):
        """Load expenses from JSON file"""
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                self.expenses = []
                for item in data:
                    if item.get('type') == 'recurring':
                        self.expenses.append(RecurringExpense.from_dict(item))
                    else:
                        self.expenses.append(Expense.from_dict(item))
                print(f"✅ Loaded {len(self.expenses)} expenses from {self.data_file}")
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Error loading expenses: {e}")
            self.expenses = []
            # Reset the file if corrupted
            with open(self.data_file, 'w') as file:
                json.dump([], file, indent=2)
    
    def _load_categories(self):
        """Load categories from JSON file"""
        try:
            with open(self.categories_file, 'r') as file:
                data = json.load(file)
                self.categories = [Category.from_dict(item) for item in data]
                print(f"✅ Loaded {len(self.categories)} categories from {self.categories_file}")
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Error loading categories: {e}")
            self.categories = []
    
    def _save_expenses(self):
        """Save expenses to JSON file"""
        try:
            with open(self.data_file, 'w') as file:
                json_data = [exp.to_dict() for exp in self.expenses]
                json.dump(json_data, file, indent=2)
            print(f"💾 Saved {len(self.expenses)} expenses to {self.data_file}")
        except Exception as e:
            print(f"❌ Error saving expenses: {e}")
    
    def _save_categories(self):
        """Save categories to JSON file"""
        try:
            with open(self.categories_file, 'w') as file:
                json_data = [cat.to_dict() for cat in self.categories]
                json.dump(json_data, file, indent=2)
            print(f"💾 Saved {len(self.categories)} categories to {self.categories_file}")
        except Exception as e:
            print(f"❌ Error saving categories: {e}")
    
    def add_expense(self, expense):
        """Add a new expense"""
        self.expenses.append(expense)
        self._save_expenses()
        print("✅ Expense added successfully!")
    
    def delete_expense(self, index):
        """Delete an expense by index"""
        if 0 <= index < len(self.expenses):
            deleted = self.expenses.pop(index)
            self._save_expenses()
            print(f"✅ Expense deleted: {deleted}")
        else:
            print("❌ Invalid expense index!")
    
    def update_expense(self, index, amount=None, category=None, description=None, date=None):
        """Update an existing expense"""
        if 0 <= index < len(self.expenses):
            expense = self.expenses[index]
            if amount is not None:
                expense.set_amount(amount)
            if category is not None:
                expense.set_category(category)
            if description is not None:
                expense.set_description(description)
            if date is not None:
                expense.set_date(date)
            
            self._save_expenses()
            print("✅ Expense updated successfully!")
        else:
            print("❌ Invalid expense index!")
    
    def get_all_expenses(self):
        """Get all expenses"""
        return self.expenses
    
    def get_expenses_by_category(self, category):
        """Get expenses by category"""
        return [exp for exp in self.expenses if exp.get_category() == category]
    
    def get_total_spending(self):
        """Get total spending across all expenses"""
        return sum(exp.get_amount() for exp in self.expenses)
    
    def get_category_summary(self):
        """Get summary by category"""
        summary = {}
        for expense in self.expenses:
            category = expense.get_category()
            summary[category] = summary.get(category, 0) + expense.get_amount()
        return summary
    
    def add_category(self, name, budget_limit=0):
        """Add a new category"""
        # Check if category already exists
        for cat in self.categories:
            if cat.get_name().lower() == name.lower():
                print(f"❌ Category '{name}' already exists!")
                return
        
        new_category = Category(name, budget_limit)
        self.categories.append(new_category)
        self._save_categories()
        print(f"✅ Category '{name}' added successfully!")
    
    def update_category_budget(self, index, new_budget):
        """Update category budget"""
        if 0 <= index < len(self.categories):
            self.categories[index].set_budget_limit(new_budget)
            self._save_categories()
            print("✅ Budget updated successfully!")
        else:
            print("❌ Invalid category index!")
    
    def get_categories(self):
        """Get all categories"""
        return self.categories
    
    def get_category_names(self):
        """Get list of category names"""
        return [cat.get_name() for cat in self.categories]

# 🧭 User Interface Class
class ExpenseManagerUI:
    def __init__(self):
        self.manager = ExpenseManager()
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("🧾 PERSONAL EXPENSE MANAGER")
        print("="*50)
        print("1. ➕ Add New Expense")
        print("2. 📋 View All Expenses")
        print("3. ✏️ Edit Expense")
        print("4. 🗑️ Delete Expense")
        print("5. 📊 View Financial Summary")
        print("6. 📈 Generate Reports")
        print("7. 🏷️ Manage Categories")
        print("8. 💾 Add Recurring Expense")
        print("9. 🚪 Exit")
        print("="*50)
    
    def add_expense_ui(self):
        """UI for adding new expense"""
        print("\n➕ ADD NEW EXPENSE")
        print("-" * 30)
        
        # Display available categories
        categories = self.manager.get_categories()
        print("Available Categories:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        
        try:
            amount = float(input("Enter amount: ₹"))
            
            print("Select category (enter number): ")
            cat_input = input().strip()
            
            if cat_input.isdigit():
                cat_index = int(cat_input) - 1
                if 0 <= cat_index < len(categories):
                    category = categories[cat_index].get_name()
                else:
                    print("❌ Invalid category number. Using 'Other'.")
                    category = "Other"
            else:
                # If user enters category name directly
                category_names = self.manager.get_category_names()
                if cat_input in category_names:
                    category = cat_input
                else:
                    print("❌ Category not found. Using 'Other'.")
                    category = "Other"
            
            description = input("Enter description: ")
            
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
            date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
            
            expense = Expense(amount, category, description, date)
            self.manager.add_expense(expense)
            
        except ValueError:
            print("❌ Invalid amount! Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error adding expense: {e}")
    
    def add_recurring_expense_ui(self):
        """UI for adding recurring expense"""
        print("\n💾 ADD RECURRING EXPENSE")
        print("-" * 30)
        
        categories = self.manager.get_categories()
        print("Available Categories:")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        
        try:
            amount = float(input("Enter amount: ₹"))
            
            print("Select category (enter number): ")
            cat_input = input().strip()
            
            if cat_input.isdigit():
                cat_index = int(cat_input) - 1
                if 0 <= cat_index < len(categories):
                    category = categories[cat_index].get_name()
                else:
                    print("❌ Invalid category number. Using 'Other'.")
                    category = "Other"
            else:
                category_names = self.manager.get_category_names()
                if cat_input in category_names:
                    category = cat_input
                else:
                    print("❌ Category not found. Using 'Other'.")
                    category = "Other"
            
            description = input("Enter description: ")
            
            print("Frequency (daily/weekly/monthly/yearly): ")
            frequency = input().strip().lower()
            if frequency not in ['daily', 'weekly', 'monthly', 'yearly']:
                frequency = 'monthly'
            
            date_input = input("Enter start date (YYYY-MM-DD) or press Enter for today: ")
            date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
            
            expense = RecurringExpense(amount, category, description, date, frequency)
            self.manager.add_expense(expense)
            
        except ValueError:
            print("❌ Invalid amount! Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error adding recurring expense: {e}")
    
    def view_expenses_ui(self):
        """UI for viewing all expenses"""
        expenses = self.manager.get_all_expenses()
        
        if not expenses:
            print("\n📭 No expenses found!")
            return
        
        print(f"\n📋 ALL EXPENSES (Total: {len(expenses)})")
        print("-" * 80)
        print(f"{'No.':<4} {'Category':<15} {'Amount':<10} {'Description':<20} {'Date':<12} {'Type':<10}")
        print("-" * 80)
        
        total_amount = 0
        for i, expense in enumerate(expenses, 1):
            expense_type = "Recurring" if isinstance(expense, RecurringExpense) else "Regular"
            frequency = f"({expense.get_frequency()})" if isinstance(expense, RecurringExpense) else ""
            print(f"{i:<4} {expense.get_category():<15} ₹{expense.get_amount():<8.2f} {expense.get_description():<20} {expense.get_date():<12} {expense_type:<10} {frequency}")
            total_amount += expense.get_amount()
        
        print("-" * 80)
        print(f"GRAND TOTAL: ₹{total_amount:.2f}")
    
    def edit_expense_ui(self):
        """UI for editing expense"""
        expenses = self.manager.get_all_expenses()
        
        if not expenses:
            print("\n📭 No expenses to edit!")
            return
        
        self.view_expenses_ui()
        
        try:
            index = int(input("\nEnter expense number to edit: ")) - 1
            
            if 0 <= index < len(expenses):
                expense = expenses[index]
                print(f"\nEditing: {expense}")
                
                print("Leave field blank to keep current value:")
                
                new_amount = input(f"New amount [Current: ₹{expense.get_amount()}]: ")
                new_category = input(f"New category [Current: {expense.get_category()}]: ")
                new_description = input(f"New description [Current: {expense.get_description()}]: ")
                new_date = input(f"New date (YYYY-MM-DD) [Current: {expense.get_date()}]: ")
                
                # Convert inputs
                amount = float(new_amount) if new_amount.strip() else None
                category = new_category if new_category.strip() else None
                description = new_description if new_description.strip() else None
                date = new_date if new_date.strip() else None
                
                self.manager.update_expense(index, amount, category, description, date)
            else:
                print("❌ Invalid expense number!")
                
        except ValueError:
            print("❌ Please enter a valid number!")
        except Exception as e:
            print(f"❌ Error editing expense: {e}")
    
    def delete_expense_ui(self):
        """UI for deleting expense"""
        expenses = self.manager.get_all_expenses()
        
        if not expenses:
            print("\n📭 No expenses to delete!")
            return
        
        self.view_expenses_ui()
        
        try:
            index = int(input("\nEnter expense number to delete: ")) - 1
            self.manager.delete_expense(index)
        except ValueError:
            print("❌ Please enter a valid number!")
        except Exception as e:
            print(f"❌ Error deleting expense: {e}")
    
    def view_summary_ui(self):
        """UI for financial summary"""
        print("\n📊 FINANCIAL SUMMARY")
        print("-" * 40)
        
        total_spending = self.manager.get_total_spending()
        print(f"Total Spending: ₹{total_spending:.2f}")
        
        category_summary = self.manager.get_category_summary()
        if category_summary:
            print("\nCategory-wise Breakdown:")
            for category, amount in category_summary.items():
                print(f"  {category}: ₹{amount:.2f}")
        else:
            print("\nNo expenses recorded yet.")
    
    def generate_reports_ui(self):
        """UI for generating reports"""
        print("\n📈 GENERATE REPORTS")
        print("-" * 30)
        print("1. 📅 Monthly Report")
        print("2. 🏷️ Category Report")
        print("3. 🔙 Back")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            month = input("Enter month (YYYY-MM) or press Enter for current month: ")
            if not month:
                month = datetime.now().strftime("%Y-%m")
            
            monthly_report = MonthlyReport(self.manager.get_all_expenses(), month)
            print("\n" + monthly_report.generate_report())
        
        elif choice == '2':
            category_report = CategoryReport(
                self.manager.get_all_expenses(), 
                self.manager.get_categories()
            )
            print("\n" + category_report.generate_report())
    
    def manage_categories_ui(self):
        """UI for managing categories"""
        while True:
            print("\n🏷️ MANAGE CATEGORIES")
            print("-" * 30)
            print("1. 📋 View Categories")
            print("2. ➕ Add New Category")
            print("3. ✏️ Update Category Budget")
            print("4. 🔙 Back")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                categories = self.manager.get_categories()
                print("\nCurrent Categories:")
                print("-" * 40)
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat}")
            
            elif choice == '2':
                name = input("Enter category name: ").strip()
                if name:
                    try:
                        budget = float(input("Enter budget limit (0 for no limit): ₹"))
                        self.manager.add_category(name, budget)
                    except ValueError:
                        print("❌ Invalid budget amount!")
                else:
                    print("❌ Category name cannot be empty!")
            
            elif choice == '3':
                categories = self.manager.get_categories()
                print("\nCurrent Categories:")
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat}")
                
                try:
                    index = int(input("Enter category number to update: ")) - 1
                    if 0 <= index < len(categories):
                        new_budget = float(input("Enter new budget limit: ₹"))
                        self.manager.update_category_budget(index, new_budget)
                    else:
                        print("❌ Invalid category number!")
                except ValueError:
                    print("❌ Please enter valid numbers!")
            
            elif choice == '4':
                break
            else:
                print("❌ Invalid choice!")
    
    def run(self):
        """Main application loop"""
        print("🚀 Welcome to Personal Expense Manager!")
        print("💾 Data files initialized successfully!")
        print("📁 Using files: expenses.json, categories.json")
        
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-9): ")
            
            if choice == '1':
                self.add_expense_ui()
            elif choice == '2':
                self.view_expenses_ui()
            elif choice == '3':
                self.edit_expense_ui()
            elif choice == '4':
                self.delete_expense_ui()
            elif choice == '5':
                self.view_summary_ui()
            elif choice == '6':
                self.generate_reports_ui()
            elif choice == '7':
                self.manage_categories_ui()
            elif choice == '8':
                self.add_recurring_expense_ui()
            elif choice == '9':
                print("\n👋 Thank you for using Personal Expense Manager!")
                print("💾 Your data has been saved successfully.")
                break
            else:
                print("❌ Invalid choice! Please try again.")
            
            input("\nPress Enter to continue...")

# 🏁 Main Application
if __name__ == "__main__":
    try:
        app = ExpenseManagerUI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")